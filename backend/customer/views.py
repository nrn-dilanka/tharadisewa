from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q, Count
from django.http import HttpResponse
import csv

from .models import Customer
from .serializers import (
    CustomerCreateSerializer, CustomerUpdateSerializer, CustomerSerializer,
    CustomerListSerializer, CustomerDetailSerializer, CreateUserAccountSerializer
)


try:
    from django_filters import rest_framework as filters_framework
    FilterSet = filters_framework.FilterSet
    CharFilter = filters_framework.CharFilter
    BooleanFilter = filters_framework.BooleanFilter
    DateTimeFilter = filters_framework.DateTimeFilter
except ImportError:
    FilterSet = None
    CharFilter = None
    BooleanFilter = None
    DateTimeFilter = None


class CustomerFilter(FilterSet if FilterSet else object):
    """
    Filter set for Customer model
    """
    if FilterSet:
        customer_id = CharFilter(field_name='customer_id', lookup_expr='icontains')
        first_name = CharFilter(field_name='first_name', lookup_expr='icontains')
        last_name = CharFilter(field_name='last_name', lookup_expr='icontains')
        email = CharFilter(field_name='email', lookup_expr='icontains')
        phone_number = CharFilter(field_name='phone_number', lookup_expr='icontains')
        nic = CharFilter(field_name='nic', lookup_expr='icontains')
        
        # Boolean filters
        is_verified = BooleanFilter(field_name='is_verified')
        is_active = BooleanFilter(field_name='is_active')
        has_user_account = BooleanFilter(method='filter_has_user_account')
        
        # Date filters
        created_from = DateTimeFilter(field_name='created_at', lookup_expr='gte')
        created_to = DateTimeFilter(field_name='created_at', lookup_expr='lte')
        
        class Meta:
            model = Customer
            fields = []
        
        def filter_has_user_account(self, queryset, name, value):
            """Filter customers with/without user accounts"""
            if value is True:
                return queryset.exclude(user__isnull=True)
            elif value is False:
                return queryset.filter(user__isnull=True)
            return queryset


class CustomerViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Customer model with full CRUD operations
    """
    queryset = Customer.objects.all()
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = [
        'customer_id', 'first_name', 'last_name', 'email', 'phone_number', 'nic'
    ]
    ordering_fields = [
        'customer_id', 'first_name', 'last_name', 'email', 'created_at', 'updated_at'
    ]
    ordering = ['-created_at']
    
    # Add filter class if available
    if FilterSet:
        filterset_class = CustomerFilter
    
    def get_serializer_class(self):
        """
        Return appropriate serializer based on action
        """
        if self.action == 'create':
            return CustomerCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return CustomerUpdateSerializer
        elif self.action == 'retrieve':
            return CustomerDetailSerializer
        elif self.action == 'list':
            return CustomerListSerializer
        else:
            return CustomerSerializer
    
    def get_permissions(self):
        """
        Set different permissions for different actions
        """
        if self.action == 'create':
            # Allow customer creation by anyone (registration)
            permission_classes = [AllowAny]
        else:
            # Require authentication for other actions
            permission_classes = [IsAuthenticated]
        
        return [permission() for permission in permission_classes]
    
    @action(detail=True, methods=['post'])
    def create_user_account(self, request, pk=None):
        """
        Create user account for existing customer
        """
        customer = self.get_object()
        
        if customer.has_user_account:
            return Response(
                {'error': 'Customer already has a user account'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer = CreateUserAccountSerializer(data=request.data)
        if serializer.is_valid():
            username = serializer.validated_data['username']
            password = serializer.validated_data['password']
            role = serializer.validated_data.get('role', 'customer')
            
            user = customer.create_user_account(username, password, role)
            
            return Response({
                'message': 'User account created successfully',
                'customer': CustomerDetailSerializer(customer).data,
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'role': user.role
                }
            })
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def verify(self, request, pk=None):
        """
        Verify/unverify a customer
        """
        customer = self.get_object()
        customer.is_verified = not customer.is_verified
        customer.save()
        
        status_text = "verified" if customer.is_verified else "unverified"
        
        return Response({
            'message': f'Customer {status_text} successfully',
            'customer': CustomerDetailSerializer(customer).data
        })
    
    @action(detail=True, methods=['post'])
    def activate(self, request, pk=None):
        """
        Activate/deactivate a customer
        """
        customer = self.get_object()
        customer.is_active = not customer.is_active
        customer.save()
        
        status_text = "activated" if customer.is_active else "deactivated"
        
        return Response({
            'message': f'Customer {status_text} successfully',
            'customer': CustomerDetailSerializer(customer).data
        })
    
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """
        Get customer statistics
        """
        total_customers = Customer.objects.count()
        verified_customers = Customer.objects.filter(is_verified=True).count()
        active_customers = Customer.objects.filter(is_active=True).count()
        customers_with_accounts = Customer.objects.exclude(user__isnull=True).count()
        
        # Recent customers (last 30 days)
        from datetime import datetime, timedelta
        thirty_days_ago = datetime.now() - timedelta(days=30)
        recent_customers = Customer.objects.filter(created_at__gte=thirty_days_ago).count()
        
        return Response({
            'total_customers': total_customers,
            'verified_customers': verified_customers,
            'active_customers': active_customers,
            'unverified_customers': total_customers - verified_customers,
            'inactive_customers': total_customers - active_customers,
            'customers_with_accounts': customers_with_accounts,
            'customers_without_accounts': total_customers - customers_with_accounts,
            'recent_customers': recent_customers,
        })
    
    @action(detail=False, methods=['get'])
    def verified(self, request):
        """
        Get all verified customers
        """
        verified_customers = Customer.objects.filter(is_verified=True)
        page = self.paginate_queryset(verified_customers)
        if page is not None:
            serializer = CustomerListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = CustomerListSerializer(verified_customers, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def unverified(self, request):
        """
        Get all unverified customers
        """
        unverified_customers = Customer.objects.filter(is_verified=False)
        page = self.paginate_queryset(unverified_customers)
        if page is not None:
            serializer = CustomerListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = CustomerListSerializer(unverified_customers, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def with_accounts(self, request):
        """
        Get customers who have user accounts
        """
        customers_with_accounts = Customer.objects.exclude(user__isnull=True)
        page = self.paginate_queryset(customers_with_accounts)
        if page is not None:
            serializer = CustomerListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = CustomerListSerializer(customers_with_accounts, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def without_accounts(self, request):
        """
        Get customers who don't have user accounts
        """
        customers_without_accounts = Customer.objects.filter(user__isnull=True)
        page = self.paginate_queryset(customers_without_accounts)
        if page is not None:
            serializer = CustomerListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = CustomerListSerializer(customers_without_accounts, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def export(self, request):
        """
        Export customers to CSV
        """
        # Get filtered queryset
        queryset = self.filter_queryset(self.get_queryset())
        
        # Create HTTP response with CSV content type
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="customers.csv"'
        
        # Create CSV writer
        writer = csv.writer(response)
        
        # Write header row
        header = [
            'Customer ID', 'First Name', 'Last Name', 'Email', 'Phone Number',
            'NIC', 'Date of Birth', 'Address', 'Is Verified', 'Is Active',
            'Has User Account', 'Created At', 'Updated At'
        ]
        writer.writerow(header)
        
        # Write data rows
        for customer in queryset:
            row = [
                customer.customer_id,
                customer.first_name,
                customer.last_name,
                customer.email,
                customer.phone_number or '',
                customer.nic,
                customer.date_of_birth or '',
                customer.address or '',
                customer.is_verified,
                customer.is_active,
                customer.has_user_account,
                customer.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                customer.updated_at.strftime('%Y-%m-%d %H:%M:%S'),
            ]
            writer.writerow(row)
        
        return response
    
    @action(detail=False, methods=['post'])
    def bulk_operations(self, request):
        """
        Perform bulk operations on customers
        """
        operation = request.data.get('operation')
        customer_ids = request.data.get('customer_ids', [])
        
        if not operation or not customer_ids:
            return Response(
                {'error': 'Operation and customer_ids are required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        customers = Customer.objects.filter(id__in=customer_ids)
        
        if operation == 'verify':
            customers.update(is_verified=True)
        elif operation == 'unverify':
            customers.update(is_verified=False)
        elif operation == 'activate':
            customers.update(is_active=True)
        elif operation == 'deactivate':
            customers.update(is_active=False)
        elif operation == 'delete':
            count = customers.count()
            customers.delete()
            return Response({'message': f'Deleted {count} customers'})
        else:
            return Response(
                {'error': 'Invalid operation'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        return Response({'message': f'Operation {operation} completed on {customers.count()} customers'})
