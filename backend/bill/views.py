from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q, Sum, Avg, Count
from django.utils import timezone
from datetime import datetime, timedelta
from decimal import Decimal
try:
    from django_filters.rest_framework import DjangoFilterBackend
except ImportError:
    DjangoFilterBackend = None
from rest_framework.filters import SearchFilter, OrderingFilter

from .models import Bill
from .serializers import (
    BillSerializer,
    BillCreateSerializer,
    BillListSerializer,
    BillUpdateSerializer,
    BillStatsSerializer,
    BillSummarySerializer
)


class BillViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing bills
    Provides CRUD operations and additional bill management endpoints
    """
    
    queryset = Bill.objects.select_related('service', 'purchase__customer', 'service__product__shop')
    permission_classes = [IsAuthenticated]
    
    # Add filters if django-filter is available
    filter_backends = [SearchFilter, OrderingFilter]
    if DjangoFilterBackend:
        filter_backends.insert(0, DjangoFilterBackend)
        filterset_fields = {
            'status': ['exact', 'in'],
            'date': ['exact', 'gte', 'lte', 'year', 'month'],
            'amount': ['exact', 'gte', 'lte'],
            'service__service_type': ['exact'],
            'purchase__customer': ['exact'],
            'service__product__shop': ['exact'],
            'due_date': ['exact', 'gte', 'lte'],
            'created_at': ['exact', 'gte', 'lte']
        }
    
    search_fields = [
        'bill_number',
        'notes',
        'purchase__customer__first_name',
        'purchase__customer__last_name',
        'purchase__customer__username',
        'service__description',
        'service__product__name',
        'service__product__shop__name'
    ]
    
    ordering_fields = [
        'date', 'amount', 'bill_number', 'status',
        'due_date', 'created_at'
    ]
    
    ordering = ['-date', '-created_at']
    
    def get_serializer_class(self):
        """
        Return appropriate serializer based on action
        """
        if self.action == 'list':
            return BillListSerializer
        elif self.action == 'create':
            return BillCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return BillUpdateSerializer
        elif self.action == 'statistics':
            return BillStatsSerializer
        elif self.action == 'summary':
            return BillSummarySerializer
        return BillSerializer
    
    def get_queryset(self):
        """
        Filter queryset based on user permissions and query parameters
        """
        queryset = self.queryset
        
        # Filter by customer if specified
        customer_id = self.request.query_params.get('customer', None)
        if customer_id:
            queryset = queryset.filter(purchase__customer_id=customer_id)
        
        # Filter by service if specified  
        service_id = self.request.query_params.get('service', None)
        if service_id:
            queryset = queryset.filter(service_id=service_id)
        
        # Filter by purchase if specified
        purchase_id = self.request.query_params.get('purchase', None)
        if purchase_id:
            queryset = queryset.filter(purchase_id=purchase_id)
        
        # Filter by shop if specified
        shop_id = self.request.query_params.get('shop', None)
        if shop_id:
            queryset = queryset.filter(service__product__shop_id=shop_id)
        
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
        
        # Filter by amount range
        amount_min = self.request.query_params.get('amount_min', None)
        amount_max = self.request.query_params.get('amount_max', None)
        
        if amount_min:
            try:
                queryset = queryset.filter(amount__gte=Decimal(amount_min))
            except (ValueError, TypeError):
                pass
        
        if amount_max:
            try:
                queryset = queryset.filter(amount__lte=Decimal(amount_max))
            except (ValueError, TypeError):
                pass
        
        return queryset
    
    @action(detail=False, methods=['get'])
    def by_customer(self, request, customer_id=None):
        """
        Get bills for a specific customer
        """
        if not customer_id:
            customer_id = request.query_params.get('customer_id')
        
        if not customer_id:
            return Response(
                {'error': 'Customer ID is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        bills = self.get_queryset().filter(purchase__customer_id=customer_id)
        serializer = BillListSerializer(bills, many=True)
        
        return Response({
            'count': bills.count(),
            'bills': serializer.data
        })
    
    @action(detail=False, methods=['get'])
    def by_service(self, request, service_id=None):
        """
        Get bills for a specific service
        """
        if not service_id:
            service_id = request.query_params.get('service_id')
        
        if not service_id:
            return Response(
                {'error': 'Service ID is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        bills = self.get_queryset().filter(service_id=service_id)
        serializer = BillListSerializer(bills, many=True)
        
        return Response({
            'count': bills.count(),
            'bills': serializer.data
        })
    
    @action(detail=False, methods=['get'])
    def by_purchase(self, request, purchase_id=None):
        """
        Get bills for a specific purchase
        """
        if not purchase_id:
            purchase_id = request.query_params.get('purchase_id')
        
        if not purchase_id:
            return Response(
                {'error': 'Purchase ID is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        bills = self.get_queryset().filter(purchase_id=purchase_id)
        serializer = BillListSerializer(bills, many=True)
        
        return Response({
            'count': bills.count(),
            'bills': serializer.data
        })
    
    @action(detail=False, methods=['get'])
    def by_shop(self, request, shop_id=None):
        """
        Get bills for a specific shop
        """
        if not shop_id:
            shop_id = request.query_params.get('shop_id')
        
        if not shop_id:
            return Response(
                {'error': 'Shop ID is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        bills = self.get_queryset().filter(service__product__shop_id=shop_id)
        serializer = BillListSerializer(bills, many=True)
        
        return Response({
            'count': bills.count(),
            'bills': serializer.data
        })
    
    @action(detail=False, methods=['get'])
    def pending(self, request):
        """
        Get all pending bills
        """
        bills = self.get_queryset().filter(status='pending')
        serializer = BillListSerializer(bills, many=True)
        
        return Response({
            'count': bills.count(),
            'total_amount': bills.aggregate(total=Sum('amount'))['total'] or 0,
            'bills': serializer.data
        })
    
    @action(detail=False, methods=['get'])
    def paid(self, request):
        """
        Get all paid bills
        """
        bills = self.get_queryset().filter(status='paid')
        serializer = BillListSerializer(bills, many=True)
        
        return Response({
            'count': bills.count(),
            'total_amount': bills.aggregate(total=Sum('amount'))['total'] or 0,
            'bills': serializer.data
        })
    
    @action(detail=False, methods=['get'])
    def overdue(self, request):
        """
        Get all overdue bills
        """
        now = timezone.now()
        bills = self.get_queryset().filter(
            status='pending',
            due_date__lt=now
        )
        
        # Update status to overdue
        bills.update(status='overdue')
        
        # Re-fetch with updated status
        overdue_bills = self.get_queryset().filter(status='overdue')
        serializer = BillListSerializer(overdue_bills, many=True)
        
        return Response({
            'count': overdue_bills.count(),
            'total_amount': overdue_bills.aggregate(total=Sum('amount'))['total'] or 0,
            'bills': serializer.data
        })
    
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """
        Get comprehensive bill statistics
        """
        queryset = self.get_queryset()
        
        # Basic statistics
        total_bills = queryset.count()
        total_amount = queryset.aggregate(total=Sum('amount'))['total'] or 0
        
        # Status-wise statistics
        paid_bills = queryset.filter(status='paid')
        paid_count = paid_bills.count()
        paid_amount = paid_bills.aggregate(total=Sum('amount'))['total'] or 0
        
        pending_bills = queryset.filter(status='pending')
        pending_count = pending_bills.count()
        pending_amount = pending_bills.aggregate(total=Sum('amount'))['total'] or 0
        
        overdue_bills = queryset.filter(status='overdue')
        overdue_count = overdue_bills.count()
        overdue_amount = overdue_bills.aggregate(total=Sum('amount'))['total'] or 0
        
        # Additional statistics
        avg_amount = queryset.aggregate(avg=Avg('amount'))['avg'] or 0
        total_tax = queryset.aggregate(total=Sum('tax_amount'))['total'] or 0
        total_discount = queryset.aggregate(total=Sum('discount_amount'))['total'] or 0
        
        stats_data = {
            'total_bills': total_bills,
            'total_amount': total_amount,
            'paid_bills': paid_count,
            'paid_amount': paid_amount,
            'pending_bills': pending_count,
            'pending_amount': pending_amount,
            'overdue_bills': overdue_count,
            'overdue_amount': overdue_amount,
            'average_bill_amount': avg_amount,
            'total_tax_collected': total_tax,
            'total_discounts_given': total_discount
        }
        
        serializer = BillStatsSerializer(stats_data)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def mark_paid(self, request, pk=None):
        """
        Mark a bill as paid
        """
        bill = self.get_object()
        
        if bill.status == 'paid':
            return Response(
                {'message': 'Bill is already marked as paid'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        bill.mark_as_paid()
        
        serializer = self.get_serializer(bill)
        return Response({
            'message': 'Bill marked as paid successfully',
            'bill': serializer.data
        })
    
    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """
        Cancel a bill
        """
        bill = self.get_object()
        
        if bill.status == 'paid':
            return Response(
                {'error': 'Cannot cancel a paid bill'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        bill.status = 'cancelled'
        bill.save()
        
        serializer = self.get_serializer(bill)
        return Response({
            'message': 'Bill cancelled successfully',
            'bill': serializer.data
        })
    
    @action(detail=True, methods=['get'])
    def summary(self, request, pk=None):
        """
        Get formatted bill summary
        """
        bill = self.get_object()
        summary_data = bill.get_bill_summary()
        
        serializer = BillSummarySerializer(summary_data)
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'])
    def bulk_mark_paid(self, request):
        """
        Mark multiple bills as paid
        """
        bill_ids = request.data.get('bill_ids', [])
        
        if not bill_ids:
            return Response(
                {'error': 'Bill IDs are required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        bills = Bill.objects.filter(id__in=bill_ids, status__in=['pending', 'overdue'])
        updated_count = 0
        
        for bill in bills:
            bill.mark_as_paid()
            updated_count += 1
        
        return Response({
            'message': f'{updated_count} bills marked as paid',
            'updated_count': updated_count
        })
    
    @action(detail=False, methods=['get'])
    def monthly_report(self, request):
        """
        Get monthly bill report
        """
        # Get month and year from query params
        year = request.query_params.get('year', timezone.now().year)
        month = request.query_params.get('month', timezone.now().month)
        
        try:
            year = int(year)
            month = int(month)
        except (ValueError, TypeError):
            return Response(
                {'error': 'Invalid year or month'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Filter bills for the specified month
        bills = self.get_queryset().filter(
            date__year=year,
            date__month=month
        )
        
        # Calculate statistics
        total_bills = bills.count()
        total_amount = bills.aggregate(total=Sum('amount'))['total'] or 0
        paid_amount = bills.filter(status='paid').aggregate(total=Sum('amount'))['total'] or 0
        pending_amount = bills.filter(status='pending').aggregate(total=Sum('amount'))['total'] or 0
        
        # Group by day
        daily_stats = {}
        for bill in bills:
            day = bill.date.day
            if day not in daily_stats:
                daily_stats[day] = {'count': 0, 'amount': 0}
            daily_stats[day]['count'] += 1
            daily_stats[day]['amount'] += float(bill.amount)
        
        return Response({
            'year': year,
            'month': month,
            'total_bills': total_bills,
            'total_amount': total_amount,
            'paid_amount': paid_amount,
            'pending_amount': pending_amount,
            'daily_stats': daily_stats
        })
    
    @action(detail=False, methods=['get'])
    def recent(self, request):
        """
        Get recent bills (last 30 days)
        """
        thirty_days_ago = timezone.now() - timedelta(days=30)
        bills = self.get_queryset().filter(created_at__gte=thirty_days_ago)
        
        serializer = BillListSerializer(bills, many=True)
        return Response({
            'count': bills.count(),
            'total_amount': bills.aggregate(total=Sum('amount'))['total'] or 0,
            'bills': serializer.data
        })
