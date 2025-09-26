from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q, Count, Avg, Sum
from django.utils import timezone
from datetime import datetime, timedelta
from decimal import Decimal
try:
    from django_filters.rest_framework import DjangoFilterBackend
except ImportError:
    DjangoFilterBackend = None
from rest_framework.filters import SearchFilter, OrderingFilter

from .models import Repair
from .serializers import (
    RepairSerializer,
    RepairCreateSerializer,
    RepairListSerializer,
    RepairUpdateSerializer,
    RepairStatsSerializer,
    RepairSummarySerializer,
    PartsUsedSerializer
)


class RepairViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing repairs
    Provides CRUD operations and additional repair management endpoints
    """
    
    queryset = Repair.objects.select_related('purchase__customer', 'purchase__product__shop')
    permission_classes = [IsAuthenticated]
    
    # Add filters if django-filter is available
    filter_backends = [SearchFilter, OrderingFilter]
    if DjangoFilterBackend:
        filter_backends.insert(0, DjangoFilterBackend)
        filterset_fields = {
            'repair_type': ['exact', 'in'],
            'status': ['exact', 'in'],
            'priority': ['exact', 'in'],
            'date': ['exact', 'gte', 'lte', 'year', 'month'],
            'purchase': ['exact'],
            'purchase__customer': ['exact'],
            'purchase__product': ['exact'],
            'purchase__product__shop': ['exact'],
            'technician_name': ['exact', 'icontains'],
            'is_under_warranty': ['exact'],
            'quality_check_passed': ['exact'],
            'ready_for_pickup': ['exact'],
            'created_at': ['exact', 'gte', 'lte']
        }
    
    search_fields = [
        'repair_code',
        'problem_description',
        'diagnosis',
        'repair_notes',
        'technician_name',
        'purchase__customer__first_name',
        'purchase__customer__last_name',
        'purchase__customer__username',
        'purchase__product__name',
        'purchase__product__shop__name'
    ]
    
    ordering_fields = [
        'date', 'repair_code', 'status', 'priority',
        'estimated_completion', 'created_at', 'completed_date'
    ]
    
    ordering = ['-date', '-created_at']
    
    def get_serializer_class(self):
        """
        Return appropriate serializer based on action
        """
        if self.action == 'list':
            return RepairListSerializer
        elif self.action == 'create':
            return RepairCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return RepairUpdateSerializer
        elif self.action == 'statistics':
            return RepairStatsSerializer
        elif self.action == 'summary':
            return RepairSummarySerializer
        elif self.action in ['add_part', 'update_parts']:
            return PartsUsedSerializer
        return RepairSerializer
    
    def get_queryset(self):
        """
        Filter queryset based on query parameters
        """
        queryset = self.queryset
        
        # Filter by customer if specified
        customer_id = self.request.query_params.get('customer', None)
        if customer_id:
            queryset = queryset.filter(purchase__customer_id=customer_id)
        
        # Filter by product if specified
        product_id = self.request.query_params.get('product', None)
        if product_id:
            queryset = queryset.filter(purchase__product_id=product_id)
        
        # Filter by purchase if specified
        purchase_id = self.request.query_params.get('purchase', None)
        if purchase_id:
            queryset = queryset.filter(purchase_id=purchase_id)
        
        # Filter by shop if specified
        shop_id = self.request.query_params.get('shop', None)
        if shop_id:
            queryset = queryset.filter(purchase__product__shop_id=shop_id)
        
        # Filter by technician if specified
        technician = self.request.query_params.get('technician', None)
        if technician:
            queryset = queryset.filter(technician_name__icontains=technician)
        
        # Filter by date range
        date_from = self.request.query_params.get('date_from', None)
        date_to = self.request.query_params.get('date_to', None)
        
        if date_from:
            try:
                date_from = datetime.fromisoformat(date_from.replace('Z', '+00:00'))
                queryset = queryset.filter(date__gte=date_from)
            except ValueError:
                pass
        
        if date_to:
            try:
                date_to = datetime.fromisoformat(date_to.replace('Z', '+00:00'))
                queryset = queryset.filter(date__lte=date_to)
            except ValueError:
                pass
        
        return queryset
    
    @action(detail=False, methods=['get'])
    def by_customer(self, request, customer_id=None):
        """
        Get repairs for a specific customer
        """
        if not customer_id:
            customer_id = request.query_params.get('customer_id')
        
        if not customer_id:
            return Response(
                {'error': 'Customer ID is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        repairs = self.get_queryset().filter(purchase__customer_id=customer_id)
        serializer = RepairListSerializer(repairs, many=True)
        
        return Response({
            'count': repairs.count(),
            'repairs': serializer.data
        })
    
    @action(detail=False, methods=['get'])
    def by_product(self, request, product_id=None):
        """
        Get repairs for a specific product
        """
        if not product_id:
            product_id = request.query_params.get('product_id')
        
        if not product_id:
            return Response(
                {'error': 'Product ID is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        repairs = self.get_queryset().filter(purchase__product_id=product_id)
        serializer = RepairListSerializer(repairs, many=True)
        
        return Response({
            'count': repairs.count(),
            'repairs': serializer.data
        })
    
    @action(detail=False, methods=['get'])
    def by_purchase(self, request, purchase_id=None):
        """
        Get repairs for a specific purchase
        """
        if not purchase_id:
            purchase_id = request.query_params.get('purchase_id')
        
        if not purchase_id:
            return Response(
                {'error': 'Purchase ID is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        repairs = self.get_queryset().filter(purchase_id=purchase_id)
        serializer = RepairListSerializer(repairs, many=True)
        
        return Response({
            'count': repairs.count(),
            'repairs': serializer.data
        })
    
    @action(detail=False, methods=['get'])
    def by_shop(self, request, shop_id=None):
        """
        Get repairs for a specific shop
        """
        if not shop_id:
            shop_id = request.query_params.get('shop_id')
        
        if not shop_id:
            return Response(
                {'error': 'Shop ID is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        repairs = self.get_queryset().filter(purchase__product__shop_id=shop_id)
        serializer = RepairListSerializer(repairs, many=True)
        
        return Response({
            'count': repairs.count(),
            'repairs': serializer.data
        })
    
    @action(detail=False, methods=['get'])
    def active(self, request):
        """
        Get all active repairs
        """
        repairs = Repair.get_active_repairs()
        serializer = RepairListSerializer(repairs, many=True)
        
        return Response({
            'count': repairs.count(),
            'repairs': serializer.data
        })
    
    @action(detail=False, methods=['get'])
    def completed(self, request):
        """
        Get all completed repairs
        """
        repairs = self.get_queryset().filter(status='completed')
        serializer = RepairListSerializer(repairs, many=True)
        
        return Response({
            'count': repairs.count(),
            'repairs': serializer.data
        })
    
    @action(detail=False, methods=['get'])
    def overdue(self, request):
        """
        Get all overdue repairs
        """
        repairs = Repair.get_overdue_repairs()
        serializer = RepairListSerializer(repairs, many=True)
        
        return Response({
            'count': repairs.count(),
            'repairs': serializer.data
        })
    
    @action(detail=False, methods=['get'])
    def ready_for_pickup(self, request):
        """
        Get all repairs ready for pickup
        """
        repairs = self.get_queryset().filter(ready_for_pickup=True, delivered_date__isnull=True)
        serializer = RepairListSerializer(repairs, many=True)
        
        return Response({
            'count': repairs.count(),
            'repairs': serializer.data
        })
    
    @action(detail=False, methods=['get'])
    def warranty_repairs(self, request):
        """
        Get all warranty repairs
        """
        repairs = self.get_queryset().filter(is_under_warranty=True)
        serializer = RepairListSerializer(repairs, many=True)
        
        return Response({
            'count': repairs.count(),
            'repairs': serializer.data
        })
    
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """
        Get comprehensive repair statistics
        """
        queryset = self.get_queryset()
        
        # Basic statistics
        total_repairs = queryset.count()
        active_repairs = queryset.filter(
            status__in=['requested', 'diagnosed', 'in_progress', 'waiting_parts']
        ).count()
        completed_repairs = queryset.filter(status='completed').count()
        cancelled_repairs = queryset.filter(status='cancelled').count()
        overdue_repairs = Repair.get_overdue_repairs().count()
        
        # Type statistics
        repair_types = [
            'warranty', 'paid', 'emergency', 'maintenance',
            'replacement', 'diagnostic', 'software', 'hardware'
        ]
        repairs_by_type = {}
        for repair_type in repair_types:
            count = queryset.filter(repair_type=repair_type).count()
            repairs_by_type[repair_type] = count
        
        # Status statistics
        statuses = [
            'requested', 'diagnosed', 'in_progress', 'waiting_parts',
            'completed', 'cancelled', 'failed'
        ]
        repairs_by_status = {}
        for repair_status in statuses:
            count = queryset.filter(status=repair_status).count()
            repairs_by_status[repair_status] = count
        
        # Priority statistics
        priorities = ['low', 'normal', 'high', 'urgent']
        repairs_by_priority = {}
        for priority in priorities:
            count = queryset.filter(priority=priority).count()
            repairs_by_priority[priority] = count
        
        # Time and cost statistics
        completed_repairs_with_times = queryset.filter(
            status='completed',
            started_date__isnull=False,
            completed_date__isnull=False
        )
        
        avg_repair_time = "Not available"
        if completed_repairs_with_times.exists():
            total_seconds = 0
            count = 0
            for repair in completed_repairs_with_times:
                duration = repair.completed_date - repair.started_date
                total_seconds += duration.total_seconds()
                count += 1
            
            if count > 0:
                avg_seconds = total_seconds / count
                avg_days = int(avg_seconds // 86400)
                avg_hours = int((avg_seconds % 86400) // 3600)
                avg_repair_time = f"{avg_days} days, {avg_hours} hours"
        
        # Cost statistics
        total_cost = queryset.filter(actual_cost__isnull=False).aggregate(
            total=Sum('actual_cost')
        )['total'] or 0
        
        avg_cost = queryset.filter(actual_cost__isnull=False).aggregate(
            avg=Avg('actual_cost')
        )['avg'] or 0
        
        stats_data = {
            'total_repairs': total_repairs,
            'active_repairs': active_repairs,
            'completed_repairs': completed_repairs,
            'cancelled_repairs': cancelled_repairs,
            'overdue_repairs': overdue_repairs,
            'repairs_by_type': repairs_by_type,
            'repairs_by_status': repairs_by_status,
            'repairs_by_priority': repairs_by_priority,
            'average_repair_time': avg_repair_time,
            'total_repair_cost': total_cost,
            'average_repair_cost': avg_cost
        }
        
        serializer = RepairStatsSerializer(stats_data)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def summary(self, request, pk=None):
        """
        Get formatted repair summary
        """
        repair = self.get_object()
        summary_data = repair.get_repair_summary()
        
        serializer = RepairSummarySerializer(summary_data)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def start_repair(self, request, pk=None):
        """
        Start a repair
        """
        repair = self.get_object()
        
        if repair.status not in ['requested', 'diagnosed']:
            return Response(
                {'error': 'Repair cannot be started from current status'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        repair.mark_as_started()
        
        serializer = self.get_serializer(repair)
        return Response({
            'message': 'Repair started successfully',
            'repair': serializer.data
        })
    
    @action(detail=True, methods=['post'])
    def complete_repair(self, request, pk=None):
        """
        Complete a repair
        """
        repair = self.get_object()
        
        if repair.status != 'in_progress':
            return Response(
                {'error': 'Only repairs in progress can be completed'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        repair.mark_as_completed()
        
        serializer = self.get_serializer(repair)
        return Response({
            'message': 'Repair completed successfully',
            'repair': serializer.data
        })
    
    @action(detail=True, methods=['post'])
    def deliver(self, request, pk=None):
        """
        Mark repair as delivered to customer
        """
        repair = self.get_object()
        
        if repair.status != 'completed':
            return Response(
                {'error': 'Only completed repairs can be delivered'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        repair.mark_as_delivered()
        
        serializer = self.get_serializer(repair)
        return Response({
            'message': 'Repair marked as delivered successfully',
            'repair': serializer.data
        })
    
    @action(detail=True, methods=['post'])
    def add_part(self, request, pk=None):
        """
        Add a part used in the repair
        """
        repair = self.get_object()
        
        part_name = request.data.get('name')
        quantity = request.data.get('quantity', 1)
        cost = request.data.get('cost')
        
        if not part_name:
            return Response(
                {'error': 'Part name is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            quantity = int(quantity)
            if quantity <= 0:
                raise ValueError()
        except (ValueError, TypeError):
            return Response(
                {'error': 'Quantity must be a positive integer'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if cost is not None:
            try:
                cost = Decimal(str(cost))
                if cost < 0:
                    raise ValueError()
            except (ValueError, TypeError):
                return Response(
                    {'error': 'Cost must be a non-negative number'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        repair.add_part_used(part_name, quantity, cost)
        
        serializer = self.get_serializer(repair)
        return Response({
            'message': 'Part added successfully',
            'repair': serializer.data
        })
    
    @action(detail=False, methods=['get'])
    def recent(self, request):
        """
        Get recent repairs (last 30 days)
        """
        thirty_days_ago = timezone.now() - timedelta(days=30)
        repairs = self.get_queryset().filter(created_at__gte=thirty_days_ago)
        
        serializer = RepairListSerializer(repairs, many=True)
        return Response({
            'count': repairs.count(),
            'repairs': serializer.data
        })
    
    @action(detail=False, methods=['post'])
    def bulk_update_status(self, request):
        """
        Update status for multiple repairs
        """
        repair_ids = request.data.get('repair_ids', [])
        new_status = request.data.get('status')
        
        if not repair_ids:
            return Response(
                {'error': 'Repair IDs are required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if not new_status:
            return Response(
                {'error': 'New status is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        repairs = Repair.objects.filter(id__in=repair_ids)
        updated_count = 0
        
        for repair in repairs:
            try:
                if new_status == 'in_progress' and repair.status in ['requested', 'diagnosed']:
                    repair.mark_as_started()
                    updated_count += 1
                elif new_status == 'completed' and repair.status == 'in_progress':
                    repair.mark_as_completed()
                    updated_count += 1
                elif repair.status not in ['completed', 'cancelled']:
                    repair.status = new_status
                    repair.save()
                    updated_count += 1
            except Exception:
                continue
        
        return Response({
            'message': f'{updated_count} repairs updated',
            'updated_count': updated_count
        })
    
    @action(detail=False, methods=['get'])
    def technician_workload(self, request):
        """
        Get workload by technician
        """
        technician_stats = (
            self.get_queryset()
            .exclude(technician_name='')
            .values('technician_name')
            .annotate(
                total_repairs=Count('id'),
                active_repairs=Count('id', filter=Q(
                    status__in=['requested', 'diagnosed', 'in_progress', 'waiting_parts']
                )),
                completed_repairs=Count('id', filter=Q(status='completed'))
            )
            .order_by('-active_repairs')
        )
        
        return Response({
            'technician_workload': list(technician_stats)
        })
