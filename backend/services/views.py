from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404
from django.db.models import Q, Count, Sum, Avg
from django.utils import timezone
from datetime import datetime, timedelta
from .models import Service
from purchase.models import Purchase
from product.models import Product
from customer.models import Customer
from .serializers import (
    ServiceSerializer,
    ServiceCreateSerializer,
    ServiceListSerializer,
    ServiceUpdateSerializer,
    ServiceStatsSerializer,
    PurchaseServicesSerializer,
    ProductServicesSerializer,
    BulkServiceCreateSerializer
)

class ServiceViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing services with full CRUD operations
    """
    
    queryset = Service.objects.select_related('purchase__customer', 'product__shop__customer').all()
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['purchase', 'product', 'product__shop', 'service_type', 'status', 'priority', 'is_under_warranty', 'is_active']
    search_fields = ['description', 'technician_notes', 'customer_feedback', 'purchase__customer__username', 'product__name']
    ordering_fields = ['date', 'service_cost', 'rating', 'created_at']
    ordering = ['-date']
    
    def get_serializer_class(self):
        """
        Return appropriate serializer based on action
        """
        if self.action == 'create':
            return ServiceCreateSerializer
        elif self.action == 'update' or self.action == 'partial_update':
            return ServiceUpdateSerializer
        elif self.action == 'list':
            return ServiceListSerializer
        else:
            return ServiceSerializer
    
    def get_queryset(self):
        """
        Filter queryset based on query parameters
        """
        queryset = super().get_queryset()
        
        # Filter by customer
        customer_id = self.request.query_params.get('customer_id')
        if customer_id:
            queryset = queryset.filter(purchase__customer_id=customer_id)
        
        # Filter by purchase
        purchase_id = self.request.query_params.get('purchase_id')
        if purchase_id:
            queryset = queryset.filter(purchase_id=purchase_id)
        
        # Filter by product
        product_id = self.request.query_params.get('product_id')
        if product_id:
            queryset = queryset.filter(product_id=product_id)
        
        # Filter by shop
        shop_id = self.request.query_params.get('shop_id')
        if shop_id:
            queryset = queryset.filter(product__shop_id=shop_id)
        
        # Filter by date range
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')
        
        if start_date:
            try:
                start_date = datetime.fromisoformat(start_date)
                queryset = queryset.filter(date__gte=start_date)
            except ValueError:
                pass
        
        if end_date:
            try:
                end_date = datetime.fromisoformat(end_date)
                queryset = queryset.filter(date__lte=end_date)
            except ValueError:
                pass
        
        # Filter by status
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        # Filter by service type
        service_type = self.request.query_params.get('service_type')
        if service_type:
            queryset = queryset.filter(service_type=service_type)
        
        # Filter by overdue services
        overdue = self.request.query_params.get('overdue')
        if overdue == 'true':
            current_time = timezone.now()
            queryset = queryset.filter(
                scheduled_date__lt=current_time,
                status__in=['requested', 'in_progress', 'on_hold']
            )
        
        # Filter by warranty status
        warranty = self.request.query_params.get('warranty')
        if warranty is not None:
            queryset = queryset.filter(is_under_warranty=warranty.lower() == 'true')
        
        return queryset
    
    def list(self, request, *args, **kwargs):
        """
        List all services with filtering and pagination
        """
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response({
                'success': True,
                'message': 'Services retrieved successfully',
                'data': serializer.data
            })
        
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            'success': True,
            'message': 'Services retrieved successfully',
            'data': serializer.data
        })
    
    def create(self, request, *args, **kwargs):
        """
        Create a new service
        """
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            service = serializer.save()
            response_serializer = ServiceSerializer(service)
            return Response({
                'success': True,
                'message': 'Service created successfully',
                'data': response_serializer.data
            }, status=status.HTTP_201_CREATED)
        
        return Response({
            'success': False,
            'message': 'Failed to create service',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
    
    def retrieve(self, request, *args, **kwargs):
        """
        Retrieve a specific service
        """
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response({
            'success': True,
            'message': 'Service retrieved successfully',
            'data': serializer.data
        })
    
    def update(self, request, *args, **kwargs):
        """
        Update a service
        """
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        
        if serializer.is_valid():
            service = serializer.save()
            response_serializer = ServiceSerializer(service)
            return Response({
                'success': True,
                'message': 'Service updated successfully',
                'data': response_serializer.data
            })
        
        return Response({
            'success': False,
            'message': 'Failed to update service',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
    
    def destroy(self, request, *args, **kwargs):
        """
        Delete a service
        """
        instance = self.get_object()
        instance.delete()
        return Response({
            'success': True,
            'message': 'Service deleted successfully'
        }, status=status.HTTP_204_NO_CONTENT)
    
    @action(detail=True, methods=['post'])
    def update_status(self, request, pk=None):
        """
        Update status of a service
        """
        service = self.get_object()
        new_status = request.data.get('status')
        
        if not new_status:
            return Response({
                'success': False,
                'message': 'status is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        valid_statuses = ['requested', 'in_progress', 'completed', 'cancelled', 'on_hold']
        if new_status not in valid_statuses:
            return Response({
                'success': False,
                'message': f'Invalid status. Valid options: {valid_statuses}'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        service.status = new_status
        service.save(update_fields=['status'])
        
        serializer = ServiceSerializer(service)
        return Response({
            'success': True,
            'message': f'Service status updated to {new_status}',
            'data': serializer.data
        })
    
    @action(detail=True, methods=['post'])
    def add_feedback(self, request, pk=None):
        """
        Add customer feedback and rating to a service
        """
        service = self.get_object()
        feedback = request.data.get('customer_feedback')
        rating = request.data.get('rating')
        
        if feedback:
            service.customer_feedback = feedback
        
        if rating:
            try:
                rating = int(rating)
                if 1 <= rating <= 5:
                    service.rating = rating
                else:
                    return Response({
                        'success': False,
                        'message': 'Rating must be between 1 and 5'
                    }, status=status.HTTP_400_BAD_REQUEST)
            except ValueError:
                return Response({
                    'success': False,
                    'message': 'Rating must be a number'
                }, status=status.HTTP_400_BAD_REQUEST)
        
        service.save(update_fields=['customer_feedback', 'rating'])
        
        serializer = ServiceSerializer(service)
        return Response({
            'success': True,
            'message': 'Feedback added successfully',
            'data': serializer.data
        })
    
    @action(detail=True, methods=['post'])
    def toggle_status(self, request, pk=None):
        """
        Toggle active/inactive status of a service
        """
        service = self.get_object()
        service.is_active = not service.is_active
        service.save(update_fields=['is_active'])
        
        serializer = ServiceSerializer(service)
        return Response({
            'success': True,
            'message': f'Service {"activated" if service.is_active else "deactivated"} successfully',
            'data': serializer.data
        })
    
    @action(detail=False, methods=['get'])
    def by_purchase(self, request):
        """
        Get all services for a specific purchase
        """
        purchase_id = request.query_params.get('purchase_id')
        if not purchase_id:
            return Response({
                'success': False,
                'message': 'purchase_id parameter is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            purchase = Purchase.objects.get(id=purchase_id)
        except Purchase.DoesNotExist:
            return Response({
                'success': False,
                'message': 'Purchase not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Calculate service count
        purchase.service_count = purchase.services.count()
        
        serializer = PurchaseServicesSerializer(purchase)
        
        return Response({
            'success': True,
            'message': f'Services for purchase "{purchase.purchase_code}" retrieved successfully',
            'data': serializer.data
        })
    
    @action(detail=False, methods=['get'])
    def by_product(self, request):
        """
        Get all services for a specific product
        """
        product_id = request.query_params.get('product_id')
        if not product_id:
            return Response({
                'success': False,
                'message': 'product_id parameter is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return Response({
                'success': False,
                'message': 'Product not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Calculate service count
        product.service_count = product.services.count()
        
        serializer = ProductServicesSerializer(product)
        
        return Response({
            'success': True,
            'message': f'Services for product "{product.name}" retrieved successfully',
            'data': serializer.data
        })
    
    @action(detail=False, methods=['get'])
    def by_customer(self, request):
        """
        Get all services for a specific customer
        """
        customer_id = request.query_params.get('customer_id')
        if not customer_id:
            return Response({
                'success': False,
                'message': 'customer_id parameter is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        services = Service.objects.filter(purchase__customer_id=customer_id)
        
        # Apply additional filters
        is_active = request.query_params.get('is_active')
        if is_active is not None:
            services = services.filter(is_active=is_active.lower() == 'true')
        
        serializer = ServiceListSerializer(services, many=True)
        
        return Response({
            'success': True,
            'message': f'Services for customer retrieved successfully',
            'data': {
                'customer_id': customer_id,
                'services': serializer.data,
                'service_count': len(serializer.data)
            }
        })
    
    @action(detail=False, methods=['post'])
    def bulk_create(self, request):
        """
        Create multiple services at once
        """
        serializer = BulkServiceCreateSerializer(data=request.data)
        if serializer.is_valid():
            result = serializer.save()
            services = result['services']
            
            response_serializer = ServiceListSerializer(services, many=True)
            return Response({
                'success': True,
                'message': f'{len(services)} services created successfully',
                'data': response_serializer.data
            }, status=status.HTTP_201_CREATED)
        
        return Response({
            'success': False,
            'message': 'Failed to create services',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """
        Get comprehensive service statistics
        """
        # Get all services
        all_services = Service.objects.all()
        
        # Basic counts
        total_services = all_services.count()
        requested_services = all_services.filter(status='requested').count()
        in_progress_services = all_services.filter(status='in_progress').count()
        completed_services = all_services.filter(status='completed').count()
        cancelled_services = all_services.filter(status='cancelled').count()
        on_hold_services = all_services.filter(status='on_hold').count()
        
        # Overdue services
        current_time = timezone.now()
        overdue_services = all_services.filter(
            scheduled_date__lt=current_time,
            status__in=['requested', 'in_progress', 'on_hold']
        ).count()
        
        # Warranty services
        warranty_services = all_services.filter(is_under_warranty=True).count()
        
        # Financial stats
        paid_services = all_services.filter(service_cost__gt=0).count()
        total_service_revenue = all_services.aggregate(total=Sum('service_cost'))['total'] or 0
        average_service_cost = all_services.aggregate(avg=Avg('service_cost'))['avg']
        
        # Rating stats
        average_rating = all_services.filter(rating__isnull=False).aggregate(avg=Avg('rating'))['avg']
        
        # Today's stats
        today = timezone.now().date()
        services_today = all_services.filter(date__date=today).count()
        
        # Unique counts
        unique_customers = all_services.values('purchase__customer').distinct().count()
        unique_products = all_services.values('product').distinct().count()
        
        stats_data = {
            'total_services': total_services,
            'requested_services': requested_services,
            'in_progress_services': in_progress_services,
            'completed_services': completed_services,
            'cancelled_services': cancelled_services,
            'on_hold_services': on_hold_services,
            'overdue_services': overdue_services,
            'warranty_services': warranty_services,
            'paid_services': paid_services,
            'total_service_revenue': total_service_revenue,
            'average_service_cost': average_service_cost,
            'average_rating': average_rating,
            'services_today': services_today,
            'unique_customers': unique_customers,
            'unique_products': unique_products
        }
        
        serializer = ServiceStatsSerializer(stats_data)
        return Response({
            'success': True,
            'message': 'Service statistics retrieved successfully',
            'data': serializer.data
        })
    
    @action(detail=False, methods=['get'])
    def overdue(self, request):
        """
        Get overdue services
        """
        current_time = timezone.now()
        overdue_services = Service.objects.filter(
            scheduled_date__lt=current_time,
            status__in=['requested', 'in_progress', 'on_hold']
        )
        
        serializer = ServiceListSerializer(overdue_services, many=True)
        return Response({
            'success': True,
            'message': f'Found {overdue_services.count()} overdue services',
            'data': {
                'current_time': current_time,
                'overdue_services': serializer.data,
                'count': overdue_services.count()
            }
        })
    
    @action(detail=False, methods=['get'])
    def warranty(self, request):
        """
        Get warranty services
        """
        warranty_services = Service.objects.filter(is_under_warranty=True)
        
        serializer = ServiceListSerializer(warranty_services, many=True)
        return Response({
            'success': True,
            'message': f'Found {warranty_services.count()} warranty services',
            'data': {
                'warranty_services': serializer.data,
                'count': warranty_services.count()
            }
        })
    
    @action(detail=False, methods=['get'])
    def today(self, request):
        """
        Get today's services
        """
        today = timezone.now().date()
        services = Service.objects.filter(date__date=today)
        
        serializer = ServiceListSerializer(services, many=True)
        return Response({
            'success': True,
            'message': f'Today\'s services retrieved successfully',
            'data': {
                'date': today,
                'services': serializer.data,
                'count': len(serializer.data)
            }
        })
