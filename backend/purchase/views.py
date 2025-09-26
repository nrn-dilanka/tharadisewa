from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404
from django.db.models import Q, Count, Sum, Avg
from django.utils import timezone
from datetime import datetime, timedelta
from .models import Purchase
from product.models import Product
from customer.models import Customer
from .serializers import (
    PurchaseSerializer,
    PurchaseCreateSerializer,
    PurchaseListSerializer,
    PurchaseUpdateSerializer,
    PurchaseStatsSerializer,
    CustomerPurchasesSerializer,
    ProductPurchasesSerializer,
    BulkPurchaseCreateSerializer
)

class PurchaseViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing purchases with full CRUD operations
    """
    
    queryset = Purchase.objects.select_related('customer', 'product__shop__customer').all()
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['customer', 'product', 'product__shop', 'payment_status', 'purchase_method', 'is_active']
    search_fields = ['customer__username', 'customer__first_name', 'customer__last_name', 'product__name', 'product__shop__name', 'notes']
    ordering_fields = ['date', 'total_amount', 'created_at']
    ordering = ['-date']
    
    def get_serializer_class(self):
        """
        Return appropriate serializer based on action
        """
        if self.action == 'create':
            return PurchaseCreateSerializer
        elif self.action == 'update' or self.action == 'partial_update':
            return PurchaseUpdateSerializer
        elif self.action == 'list':
            return PurchaseListSerializer
        else:
            return PurchaseSerializer
    
    def get_queryset(self):
        """
        Filter queryset based on query parameters
        """
        queryset = super().get_queryset()
        
        # Filter by customer
        customer_id = self.request.query_params.get('customer_id')
        if customer_id:
            queryset = queryset.filter(customer_id=customer_id)
        
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
        
        # Filter by payment status
        payment_status = self.request.query_params.get('payment_status')
        if payment_status:
            queryset = queryset.filter(payment_status=payment_status)
        
        # Filter by active status
        is_active = self.request.query_params.get('is_active')
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')
        
        return queryset
    
    def list(self, request, *args, **kwargs):
        """
        List all purchases with filtering and pagination
        """
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response({
                'success': True,
                'message': 'Purchases retrieved successfully',
                'data': serializer.data
            })
        
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            'success': True,
            'message': 'Purchases retrieved successfully',
            'data': serializer.data
        })
    
    def create(self, request, *args, **kwargs):
        """
        Create a new purchase
        """
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            purchase = serializer.save()
            
            # Update product stock
            if purchase.product:
                purchase.product.stock_quantity -= purchase.quantity
                purchase.product.save(update_fields=['stock_quantity'])
            
            response_serializer = PurchaseSerializer(purchase)
            return Response({
                'success': True,
                'message': 'Purchase created successfully',
                'data': response_serializer.data
            }, status=status.HTTP_201_CREATED)
        
        return Response({
            'success': False,
            'message': 'Failed to create purchase',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
    
    def retrieve(self, request, *args, **kwargs):
        """
        Retrieve a specific purchase
        """
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response({
            'success': True,
            'message': 'Purchase retrieved successfully',
            'data': serializer.data
        })
    
    def update(self, request, *args, **kwargs):
        """
        Update a purchase
        """
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        old_quantity = instance.quantity
        
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        
        if serializer.is_valid():
            purchase = serializer.save()
            
            # Update product stock if quantity changed
            if 'quantity' in serializer.validated_data:
                new_quantity = serializer.validated_data['quantity']
                quantity_diff = new_quantity - old_quantity
                purchase.product.stock_quantity -= quantity_diff
                purchase.product.save(update_fields=['stock_quantity'])
            
            response_serializer = PurchaseSerializer(purchase)
            return Response({
                'success': True,
                'message': 'Purchase updated successfully',
                'data': response_serializer.data
            })
        
        return Response({
            'success': False,
            'message': 'Failed to update purchase',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
    
    def destroy(self, request, *args, **kwargs):
        """
        Delete a purchase (restore stock)
        """
        instance = self.get_object()
        
        # Restore product stock
        if instance.product:
            instance.product.stock_quantity += instance.quantity
            instance.product.save(update_fields=['stock_quantity'])
        
        instance.delete()
        return Response({
            'success': True,
            'message': 'Purchase deleted successfully'
        }, status=status.HTTP_204_NO_CONTENT)
    
    @action(detail=True, methods=['post'])
    def update_payment_status(self, request, pk=None):
        """
        Update payment status of a purchase
        """
        purchase = self.get_object()
        new_status = request.data.get('payment_status')
        
        if not new_status:
            return Response({
                'success': False,
                'message': 'payment_status is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        valid_statuses = ['pending', 'completed', 'failed', 'refunded']
        if new_status not in valid_statuses:
            return Response({
                'success': False,
                'message': f'Invalid payment status. Valid options: {valid_statuses}'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        purchase.payment_status = new_status
        purchase.save(update_fields=['payment_status'])
        
        serializer = PurchaseSerializer(purchase)
        return Response({
            'success': True,
            'message': f'Payment status updated to {new_status}',
            'data': serializer.data
        })
    
    @action(detail=True, methods=['post'])
    def toggle_status(self, request, pk=None):
        """
        Toggle active/inactive status of a purchase
        """
        purchase = self.get_object()
        purchase.is_active = not purchase.is_active
        purchase.save(update_fields=['is_active'])
        
        serializer = PurchaseSerializer(purchase)
        return Response({
            'success': True,
            'message': f'Purchase {"activated" if purchase.is_active else "deactivated"} successfully',
            'data': serializer.data
        })
    
    @action(detail=False, methods=['get'])
    def by_customer(self, request):
        """
        Get all purchases for a specific customer
        """
        customer_id = request.query_params.get('customer_id')
        if not customer_id:
            return Response({
                'success': False,
                'message': 'customer_id parameter is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            customer = Customer.objects.get(id=customer_id)
        except Customer.DoesNotExist:
            return Response({
                'success': False,
                'message': 'Customer not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        purchases = Purchase.objects.filter(customer=customer)
        
        # Apply additional filters
        is_active = request.query_params.get('is_active')
        if is_active is not None:
            purchases = purchases.filter(is_active=is_active.lower() == 'true')
        
        # Calculate totals
        customer.purchase_count = purchases.count()
        customer.total_spent = purchases.filter(payment_status='completed').aggregate(
            total=Sum('total_amount')
        )['total'] or 0
        
        serializer = CustomerPurchasesSerializer(customer)
        
        return Response({
            'success': True,
            'message': f'Purchases for customer "{customer.get_full_name()}" retrieved successfully',
            'data': serializer.data
        })
    
    @action(detail=False, methods=['get'])
    def by_product(self, request):
        """
        Get all purchases for a specific product
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
        
        purchases = Purchase.objects.filter(product=product)
        
        # Calculate totals
        product.purchase_count = purchases.count()
        product.total_sold_quantity = purchases.aggregate(
            total=Sum('quantity')
        )['total'] or 0
        product.total_revenue = purchases.filter(payment_status='completed').aggregate(
            total=Sum('total_amount')
        )['total'] or 0
        
        serializer = ProductPurchasesSerializer(product)
        
        return Response({
            'success': True,
            'message': f'Purchases for product "{product.name}" retrieved successfully',
            'data': serializer.data
        })
    
    @action(detail=False, methods=['post'])
    def bulk_create(self, request):
        """
        Create multiple purchases at once
        """
        serializer = BulkPurchaseCreateSerializer(data=request.data)
        if serializer.is_valid():
            result = serializer.save()
            purchases = result['purchases']
            
            # Update stock for all products
            for purchase in purchases:
                if purchase.product:
                    purchase.product.stock_quantity -= purchase.quantity
                    purchase.product.save(update_fields=['stock_quantity'])
            
            response_serializer = PurchaseListSerializer(purchases, many=True)
            return Response({
                'success': True,
                'message': f'{len(purchases)} purchases created successfully',
                'data': response_serializer.data
            }, status=status.HTTP_201_CREATED)
        
        return Response({
            'success': False,
            'message': 'Failed to create purchases',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """
        Get comprehensive purchase statistics
        """
        # Get all purchases
        all_purchases = Purchase.objects.all()
        
        # Basic counts
        total_purchases = all_purchases.count()
        completed_purchases = all_purchases.filter(payment_status='completed').count()
        pending_purchases = all_purchases.filter(payment_status='pending').count()
        failed_purchases = all_purchases.filter(payment_status='failed').count()
        refunded_purchases = all_purchases.filter(payment_status='refunded').count()
        
        # Revenue calculations
        completed_only = all_purchases.filter(payment_status='completed')
        total_revenue = completed_only.aggregate(total=Sum('total_amount'))['total'] or 0
        average_purchase_amount = completed_only.aggregate(avg=Avg('total_amount'))['avg']
        
        # Unique counts
        unique_customers = all_purchases.values('customer').distinct().count()
        unique_products = all_purchases.values('product').distinct().count()
        
        # Today's stats
        today = timezone.now().date()
        today_purchases = all_purchases.filter(date__date=today)
        purchases_today = today_purchases.count()
        revenue_today = today_purchases.filter(payment_status='completed').aggregate(
            total=Sum('total_amount')
        )['total'] or 0
        
        stats_data = {
            'total_purchases': total_purchases,
            'completed_purchases': completed_purchases,
            'pending_purchases': pending_purchases,
            'failed_purchases': failed_purchases,
            'refunded_purchases': refunded_purchases,
            'total_revenue': total_revenue,
            'average_purchase_amount': average_purchase_amount,
            'unique_customers': unique_customers,
            'unique_products': unique_products,
            'purchases_today': purchases_today,
            'revenue_today': revenue_today
        }
        
        serializer = PurchaseStatsSerializer(stats_data)
        return Response({
            'success': True,
            'message': 'Purchase statistics retrieved successfully',
            'data': serializer.data
        })
    
    @action(detail=False, methods=['get'])
    def today(self, request):
        """
        Get today's purchases
        """
        today = timezone.now().date()
        purchases = Purchase.objects.filter(date__date=today)
        
        serializer = PurchaseListSerializer(purchases, many=True)
        return Response({
            'success': True,
            'message': f'Today\'s purchases retrieved successfully',
            'data': {
                'date': today,
                'purchases': serializer.data,
                'count': len(serializer.data)
            }
        })
    
    @action(detail=False, methods=['get'])
    def recent(self, request):
        """
        Get recent purchases (last 7 days)
        """
        days = int(request.query_params.get('days', 7))
        start_date = timezone.now() - timedelta(days=days)
        
        purchases = Purchase.objects.filter(date__gte=start_date)
        
        serializer = PurchaseListSerializer(purchases, many=True)
        return Response({
            'success': True,
            'message': f'Recent purchases (last {days} days) retrieved successfully',
            'data': {
                'period': f'Last {days} days',
                'start_date': start_date,
                'purchases': serializer.data,
                'count': len(serializer.data)
            }
        })
