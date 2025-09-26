from django.shortcuts import render
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django_filters.rest_framework import DjangoFilterBackend
from django.contrib.auth import login, logout
from django.utils import timezone
from django.db.models import Q, Count
from datetime import datetime, timedelta
from django.http import HttpResponse
import csv

from .models import User
from .serializers import (
    UserCreateSerializer, UserUpdateSerializer, UserDetailSerializer,
    UserListSerializer, UserProfileSerializer, ChangePasswordSerializer,
    UserLoginSerializer, UserRoleUpdateSerializer, UserStatsSerializer,
    UserExportSerializer
)

try:
    from django_filters import rest_framework as filters_framework
    FilterSet = filters_framework.FilterSet
    CharFilter = filters_framework.CharFilter
    BooleanFilter = filters_framework.BooleanFilter
    DateTimeFilter = filters_framework.DateTimeFilter
    ChoiceFilter = filters_framework.ChoiceFilter
except ImportError:
    FilterSet = None
    CharFilter = None
    BooleanFilter = None
    DateTimeFilter = None
    ChoiceFilter = None


class UserFilter(FilterSet if FilterSet else object):
    """
    Filter set for User model
    """
    if FilterSet:
        username = CharFilter(field_name='username', lookup_expr='icontains')
        email = CharFilter(field_name='email', lookup_expr='icontains')
        full_name = CharFilter(method='filter_full_name')
        role = ChoiceFilter(field_name='role', choices=User._meta.get_field('role').choices)
        phone_number = CharFilter(field_name='phone_number', lookup_expr='icontains')
        
        # Boolean filters
        is_active = BooleanFilter(field_name='is_active')
        is_verified = BooleanFilter(field_name='is_verified')
        is_staff = BooleanFilter(field_name='is_staff')
        
        # Date filters
        date_joined_from = DateTimeFilter(field_name='date_joined', lookup_expr='gte')
        date_joined_to = DateTimeFilter(field_name='date_joined', lookup_expr='lte')
        
        class Meta:
            model = User
            fields = []
        
        def filter_full_name(self, queryset, name, value):
            """Filter by full name"""
            return queryset.filter(
                Q(first_name__icontains=value) | Q(last_name__icontains=value)
            )


class UserViewSet(viewsets.ModelViewSet):
    """
    ViewSet for User model with full CRUD operations
    """
    queryset = User.objects.all()
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['username', 'email', 'first_name', 'last_name', 'phone_number']
    ordering_fields = ['username', 'email', 'date_joined', 'last_login', 'role']
    ordering = ['-date_joined']
    
    # Add filter class if available
    if FilterSet:
        filterset_class = UserFilter
    
    def get_serializer_class(self):
        """
        Return appropriate serializer based on action
        """
        if self.action == 'create':
            return UserCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return UserUpdateSerializer
        elif self.action == 'retrieve':
            return UserDetailSerializer
        elif self.action == 'list':
            return UserListSerializer
        elif self.action == 'profile':
            return UserProfileSerializer
        elif self.action == 'change_password':
            return ChangePasswordSerializer
        elif self.action == 'update_role':
            return UserRoleUpdateSerializer
        else:
            return UserDetailSerializer
    
    def get_permissions(self):
        """
        Set different permissions for different actions
        """
        if self.action == 'create':
            # Allow user creation (registration)
            permission_classes = [AllowAny]
        elif self.action in ['profile', 'change_password']:
            # Allow authenticated users to view/edit their own profile
            permission_classes = [IsAuthenticated]
        elif self.action in ['update_role', 'statistics', 'export']:
            # Admin-only actions
            permission_classes = [IsAuthenticated]
        else:
            permission_classes = [IsAuthenticated]
        
        return [permission() for permission in permission_classes]
    
    def perform_create(self, serializer):
        """
        Custom create logic
        """
        user = serializer.save()
        
        # Auto-verify admin and manager roles
        if user.role in ['admin', 'manager']:
            user.is_verified = True
            user.save()
    
    def create(self, request, *args, **kwargs):
        """
        Custom create method with role validation
        """
        # Check if user has permission to create users with specified role
        role = request.data.get('role', 'customer')
        
        if hasattr(request, 'user') and request.user.is_authenticated:
            if role in ['admin', 'manager'] and not request.user.is_admin():
                return Response(
                    {'error': 'Insufficient permissions to create admin/manager users'},
                    status=status.HTTP_403_FORBIDDEN
                )
        
        return super().create(request, *args, **kwargs)
    
    @action(detail=False, methods=['get', 'put', 'patch'])
    def profile(self, request):
        """
        Get or update current user's profile
        """
        user = request.user
        
        if request.method == 'GET':
            serializer = UserProfileSerializer(user)
            return Response(serializer.data)
        
        elif request.method in ['PUT', 'PATCH']:
            serializer = UserProfileSerializer(
                user, 
                data=request.data, 
                partial=(request.method == 'PATCH')
            )
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'])
    def change_password(self, request):
        """
        Change current user's password
        """
        serializer = ChangePasswordSerializer(data=request.data, context={'request': request})
        
        if serializer.is_valid():
            user = request.user
            user.set_password(serializer.validated_data['new_password'])
            user.save()
            
            return Response({'message': 'Password changed successfully'})
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['patch'])
    def update_role(self, request, pk=None):
        """
        Update user role (admin/manager only)
        """
        user = self.get_object()
        
        # Check permissions
        if not (request.user.is_admin() or request.user.is_manager()):
            return Response(
                {'error': 'Insufficient permissions'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Prevent users from changing their own role
        if user == request.user:
            return Response(
                {'error': 'Cannot change your own role'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer = UserRoleUpdateSerializer(
            user, 
            data=request.data, 
            partial=True,
            context={'request': request}
        )
        
        if serializer.is_valid():
            serializer.save()
            return Response(UserDetailSerializer(user).data)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def activate(self, request, pk=None):
        """
        Activate a user account
        """
        user = self.get_object()
        
        if not request.user.is_staff_member():
            return Response(
                {'error': 'Insufficient permissions'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        user.is_active = True
        user.save()
        
        serializer = UserDetailSerializer(user)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def deactivate(self, request, pk=None):
        """
        Deactivate a user account
        """
        user = self.get_object()
        
        if not request.user.is_staff_member():
            return Response(
                {'error': 'Insufficient permissions'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Prevent deactivating yourself
        if user == request.user:
            return Response(
                {'error': 'Cannot deactivate your own account'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        user.is_active = False
        user.save()
        
        serializer = UserDetailSerializer(user)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def verify(self, request, pk=None):
        """
        Verify a user account
        """
        user = self.get_object()
        
        if not request.user.is_staff_member():
            return Response(
                {'error': 'Insufficient permissions'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        user.is_verified = True
        user.save()
        
        serializer = UserDetailSerializer(user)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def staff(self, request):
        """
        Get all staff users
        """
        if not request.user.is_staff_member():
            return Response(
                {'error': 'Insufficient permissions'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        staff_users = User.objects.filter(
            role__in=['admin', 'manager', 'staff', 'technician', 'sales', 'support']
        )
        
        page = self.paginate_queryset(staff_users)
        if page is not None:
            serializer = UserListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = UserListSerializer(staff_users, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def customers(self, request):
        """
        Get all customer users
        """
        if not request.user.is_staff_member():
            return Response(
                {'error': 'Insufficient permissions'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        customer_users = User.objects.filter(role='customer')
        
        page = self.paginate_queryset(customer_users)
        if page is not None:
            serializer = UserListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = UserListSerializer(customer_users, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """
        Get user statistics (admin only)
        """
        if not request.user.is_admin():
            return Response(
                {'error': 'Admin access required'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Basic counts
        total_users = User.objects.count()
        active_users = User.objects.filter(is_active=True).count()
        verified_users = User.objects.filter(is_verified=True).count()
        staff_users = User.objects.filter(is_staff=True).count()
        
        # Role counts
        role_counts = User.objects.values('role').annotate(count=Count('id'))
        role_dict = {item['role']: item['count'] for item in role_counts}
        
        admin_count = role_dict.get('admin', 0)
        manager_count = role_dict.get('manager', 0)
        staff_count = role_dict.get('staff', 0)
        customer_count = role_dict.get('customer', 0)
        technician_count = role_dict.get('technician', 0)
        sales_count = role_dict.get('sales', 0)
        support_count = role_dict.get('support', 0)
        
        # Time-based stats
        today = timezone.now().date()
        week_ago = today - timedelta(days=7)
        month_ago = today - timedelta(days=30)
        
        new_users_today = User.objects.filter(date_joined__date=today).count()
        new_users_this_week = User.objects.filter(date_joined__date__gte=week_ago).count()
        new_users_this_month = User.objects.filter(date_joined__date__gte=month_ago).count()
        
        stats = {
            'total_users': total_users,
            'active_users': active_users,
            'verified_users': verified_users,
            'staff_users': staff_users,
            'admin_count': admin_count,
            'manager_count': manager_count,
            'staff_count': staff_count,
            'customer_count': customer_count,
            'technician_count': technician_count,
            'sales_count': sales_count,
            'support_count': support_count,
            'new_users_today': new_users_today,
            'new_users_this_week': new_users_this_week,
            'new_users_this_month': new_users_this_month,
        }
        
        serializer = UserStatsSerializer(data=stats)
        if serializer.is_valid():
            return Response(serializer.data)
        return Response(stats)
    
    @action(detail=False, methods=['get'])
    def export(self, request):
        """
        Export users to CSV (admin only)
        """
        if not request.user.is_admin():
            return Response(
                {'error': 'Admin access required'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Get filtered queryset
        queryset = self.filter_queryset(self.get_queryset())
        
        # Create HTTP response with CSV content type
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="users_{timezone.now().strftime("%Y%m%d_%H%M%S")}.csv"'
        
        # Create CSV writer
        writer = csv.writer(response)
        
        # Write header row
        header = [
            'ID', 'Username', 'Email', 'First Name', 'Last Name', 'Full Name',
            'Phone Number', 'Role', 'Date of Birth', 'Address', 'Is Verified',
            'Is Active', 'Is Staff', 'Is Superuser', 'Date Joined', 'Last Login',
            'Created At', 'Updated At'
        ]
        writer.writerow(header)
        
        # Serialize and write data rows
        serializer = UserExportSerializer(queryset, many=True)
        for user_data in serializer.data:
            row = [
                user_data.get('id', ''),
                user_data.get('username', ''),
                user_data.get('email', ''),
                user_data.get('first_name', ''),
                user_data.get('last_name', ''),
                user_data.get('full_name', ''),
                user_data.get('phone_number', ''),
                user_data.get('role_display', ''),
                user_data.get('date_of_birth', ''),
                user_data.get('address', ''),
                user_data.get('is_verified', ''),
                user_data.get('is_active', ''),
                user_data.get('is_staff', ''),
                user_data.get('is_superuser', ''),
                user_data.get('date_joined', ''),
                user_data.get('last_login', ''),
                user_data.get('created_at', ''),
                user_data.get('updated_at', ''),
            ]
            writer.writerow(row)
        
        return response
    
    @action(detail=False, methods=['post'])
    def bulk_operations(self, request):
        """
        Perform bulk operations on users (admin only)
        """
        if not request.user.is_admin():
            return Response(
                {'error': 'Admin access required'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        operation = request.data.get('operation')
        user_ids = request.data.get('user_ids', [])
        
        if not operation or not user_ids:
            return Response(
                {'error': 'Operation and user_ids are required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        users = User.objects.filter(id__in=user_ids)
        
        # Prevent operations on self
        if request.user.id in user_ids:
            return Response(
                {'error': 'Cannot perform bulk operations on your own account'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if operation == 'activate':
            users.update(is_active=True)
        elif operation == 'deactivate':
            users.update(is_active=False)
        elif operation == 'verify':
            users.update(is_verified=True)
        elif operation == 'delete':
            count = users.count()
            users.delete()
            return Response({'message': f'Deleted {count} users'})
        else:
            return Response(
                {'error': 'Invalid operation'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        return Response({'message': f'Operation {operation} completed on {users.count()} users'})
