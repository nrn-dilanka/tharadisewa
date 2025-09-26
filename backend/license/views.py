from django.shortcuts import render
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.utils import timezone
from django.db.models import Q, Count, Avg
from datetime import datetime, timedelta
from django.http import HttpResponse
import csv
import json

from .models import License
from .serializers import (
    LicenseCreateSerializer, LicenseUpdateSerializer, LicenseDetailSerializer,
    LicenseListSerializer, LicenseActivationSerializer, LicenseRenewalSerializer,
    LicenseUsageSerializer, LicenseSummarySerializer, LicenseStatsSerializer,
    LicenseExportSerializer
)

try:
    from django_filters import rest_framework as filters_framework
    FilterSet = filters_framework.FilterSet
    CharFilter = filters_framework.CharFilter
    BooleanFilter = filters_framework.BooleanFilter
    DateTimeFilter = filters_framework.DateTimeFilter
    ChoiceFilter = filters_framework.ChoiceFilter
    NumberFilter = filters_framework.NumberFilter
except ImportError:
    # Fallback if django_filters is not available
    FilterSet = None
    CharFilter = None
    BooleanFilter = None
    DateTimeFilter = None
    ChoiceFilter = None
    NumberFilter = None

class LicenseFilter(FilterSet if FilterSet else object):
    """
    Filter set for License model
    """
    if FilterSet:
        license_number = CharFilter(field_name='license_number', lookup_expr='icontains')
        license_key = CharFilter(field_name='license_key', lookup_expr='exact')
        software_name = CharFilter(field_name='software_name', lookup_expr='icontains')
        license_type = ChoiceFilter(field_name='license_type', choices=License._meta.get_field('license_type').choices)
        status = ChoiceFilter(field_name='status', choices=License._meta.get_field('status').choices)
        licensed_to = CharFilter(field_name='licensed_to', lookup_expr='icontains')
        organization = CharFilter(field_name='organization', lookup_expr='icontains')
        
        # Date filters
        issue_date_from = DateTimeFilter(field_name='in_date', lookup_expr='gte')
        issue_date_to = DateTimeFilter(field_name='in_date', lookup_expr='lte')
        expiry_date_from = DateTimeFilter(field_name='ex_date', lookup_expr='gte')
        expiry_date_to = DateTimeFilter(field_name='ex_date', lookup_expr='lte')
        
        # Boolean filters
        is_expired = BooleanFilter(method='filter_expired')
        is_active = BooleanFilter(method='filter_active')
        is_expiring_soon = BooleanFilter(method='filter_expiring_soon')
        auto_renewal = BooleanFilter(field_name='auto_renewal')
        terms_accepted = BooleanFilter(field_name='terms_accepted')
        
        # Related model filters
        customer_id = NumberFilter(field_name='purchase__customer__id')
        customer_name = CharFilter(field_name='purchase__customer__first_name', lookup_expr='icontains')
        product_id = NumberFilter(field_name='purchase__product__id')
        product_name = CharFilter(field_name='purchase__product__name', lookup_expr='icontains')
        shop_id = NumberFilter(field_name='purchase__product__shop__id')
        shop_name = CharFilter(field_name='purchase__product__shop__name', lookup_expr='icontains')
        
        class Meta:
            model = License
            fields = []
        
        def filter_expired(self, queryset, name, value):
            """Filter expired licenses"""
            if value is True:
                return queryset.filter(Q(status='expired') | Q(ex_date__lt=timezone.now()))
            elif value is False:
                return queryset.exclude(Q(status='expired') | Q(ex_date__lt=timezone.now()))
            return queryset
        
        def filter_active(self, queryset, name, value):
            """Filter active licenses"""
            if value is True:
                return queryset.filter(status='active', ex_date__gt=timezone.now())
            elif value is False:
                return queryset.exclude(status='active', ex_date__gt=timezone.now())
            return queryset
        
        def filter_expiring_soon(self, queryset, name, value):
            """Filter licenses expiring within 30 days"""
            cutoff_date = timezone.now() + timedelta(days=30)
            if value is True:
                return queryset.filter(
                    status='active',
                    ex_date__lte=cutoff_date,
                    ex_date__gt=timezone.now()
                )
            elif value is False:
                return queryset.exclude(
                    status='active',
                    ex_date__lte=cutoff_date,
                    ex_date__gt=timezone.now()
                )
            return queryset

class LicenseViewSet(viewsets.ModelViewSet):
    """
    ViewSet for License model with full CRUD operations and additional actions
    """
    queryset = License.objects.all()
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = [
        'license_number', 'license_key', 'software_name', 'licensed_to',
        'organization', 'contact_email', 'purchase__customer__first_name',
        'purchase__customer__last_name', 'purchase__product__name'
    ]
    ordering_fields = [
        'in_date', 'ex_date', 'created_at', 'updated_at', 'license_number',
        'status', 'license_type', 'activation_count', 'last_used_date'
    ]
    ordering = ['-in_date', '-created_at']
    
    # Add filter class if available
    if FilterSet:
        filterset_class = LicenseFilter
    
    def get_serializer_class(self):
        """
        Return appropriate serializer based on action
        """
        if self.action == 'create':
            return LicenseCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return LicenseUpdateSerializer
        elif self.action == 'retrieve':
            return LicenseDetailSerializer
        elif self.action == 'list':
            return LicenseListSerializer
        else:
            return LicenseDetailSerializer
    
    def perform_create(self, serializer):
        """
        Custom create logic
        """
        license_obj = serializer.save()
        
        # Auto-activate if terms are accepted and license is for immediate use
        if serializer.validated_data.get('terms_accepted', False):
            if serializer.validated_data.get('status', 'pending') == 'active':
                license_obj.activate()
    
    def perform_update(self, serializer):
        """
        Custom update logic
        """
        license_obj = serializer.save()
        
        # Check and update status if license has expired
        license_obj.check_and_update_status()
    
    @action(detail=False, methods=['get'])
    def active(self, request):
        """
        Get all active licenses
        """
        active_licenses = License.get_active_licenses()
        page = self.paginate_queryset(active_licenses)
        if page is not None:
            serializer = LicenseListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = LicenseListSerializer(active_licenses, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def expired(self, request):
        """
        Get all expired licenses
        """
        expired_licenses = License.get_expired_licenses()
        page = self.paginate_queryset(expired_licenses)
        if page is not None:
            serializer = LicenseListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = LicenseListSerializer(expired_licenses, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def expiring_soon(self, request):
        """
        Get licenses expiring within specified days (default 30)
        """
        days = int(request.query_params.get('days', 30))
        expiring_licenses = License.get_expiring_soon(days)
        page = self.paginate_queryset(expiring_licenses)
        if page is not None:
            serializer = LicenseListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = LicenseListSerializer(expiring_licenses, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def activate(self, request, pk=None):
        """
        Activate a license
        """
        license_obj = self.get_object()
        
        if license_obj.status == 'revoked':
            return Response(
                {'error': 'Cannot activate revoked license'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if license_obj.is_expired:
            return Response(
                {'error': 'Cannot activate expired license'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        license_obj.activate()
        serializer = LicenseDetailSerializer(license_obj)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def suspend(self, request, pk=None):
        """
        Suspend a license
        """
        license_obj = self.get_object()
        license_obj.suspend()
        serializer = LicenseDetailSerializer(license_obj)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def revoke(self, request, pk=None):
        """
        Revoke a license
        """
        license_obj = self.get_object()
        license_obj.revoke()
        serializer = LicenseDetailSerializer(license_obj)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def renew(self, request, pk=None):
        """
        Renew a license
        """
        license_obj = self.get_object()
        serializer = LicenseRenewalSerializer(data=request.data)
        
        if serializer.is_valid():
            renewal_type = serializer.validated_data.get('renewal_type', 'extend')
            
            if renewal_type == 'extend':
                days = serializer.validated_data['renewal_period_days']
                license_obj.extend_license(days)
            elif renewal_type == 'new_period':
                days = serializer.validated_data['renewal_period_days']
                new_expiry = timezone.now() + timedelta(days=days)
                license_obj.renew(new_expiry)
            elif renewal_type == 'custom_date':
                new_expiry = serializer.validated_data['new_expiry_date']
                license_obj.renew(new_expiry)
            
            response_serializer = LicenseDetailSerializer(license_obj)
            return Response(response_serializer.data)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def update_usage(self, request, pk=None):
        """
        Update license usage information
        """
        license_obj = self.get_object()
        serializer = LicenseUsageSerializer(data=request.data)
        
        if serializer.is_valid():
            usage_info = serializer.validated_data['usage_info']
            
            # Add additional usage data
            if 'session_duration' in serializer.validated_data:
                usage_info['session_duration'] = serializer.validated_data['session_duration']
            
            if 'features_used' in serializer.validated_data:
                usage_info['features_used'] = serializer.validated_data['features_used']
            
            if 'user_count' in serializer.validated_data:
                usage_info['user_count'] = serializer.validated_data['user_count']
            
            if 'installation_info' in serializer.validated_data:
                usage_info['installation_info'] = serializer.validated_data['installation_info']
            
            license_obj.update_usage(usage_info)
            
            response_serializer = LicenseDetailSerializer(license_obj)
            return Response(response_serializer.data)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'])
    def activate_by_key(self, request):
        """
        Activate license by license key
        """
        serializer = LicenseActivationSerializer(data=request.data)
        
        if serializer.is_valid():
            license_key = serializer.validated_data['license_key']
            terms_accepted = serializer.validated_data['terms_accepted']
            activation_info = serializer.validated_data.get('activation_info', {})
            
            try:
                license_obj = License.objects.get(license_key=license_key)
                
                if license_obj.status == 'revoked':
                    return Response(
                        {'error': 'This license has been revoked'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                
                if license_obj.is_expired:
                    return Response(
                        {'error': 'This license has expired'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                
                # Update license with activation info
                if activation_info:
                    license_obj.update_usage(activation_info)
                
                if terms_accepted:
                    license_obj.activate()
                
                response_serializer = LicenseDetailSerializer(license_obj)
                return Response(response_serializer.data)
                
            except License.DoesNotExist:
                return Response(
                    {'error': 'Invalid license key'},
                    status=status.HTTP_404_NOT_FOUND
                )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['get'])
    def summary(self, request, pk=None):
        """
        Get detailed license summary
        """
        license_obj = self.get_object()
        summary = license_obj.get_license_summary()
        return Response(summary)
    
    @action(detail=False, methods=['get'])
    def dashboard(self, request):
        """
        Get license dashboard data
        """
        licenses = self.get_queryset()
        page = self.paginate_queryset(licenses)
        if page is not None:
            serializer = LicenseSummarySerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = LicenseSummarySerializer(licenses, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """
        Get comprehensive license statistics
        """
        # Basic counts
        total_licenses = License.objects.count()
        active_licenses = License.objects.filter(status='active', ex_date__gt=timezone.now()).count()
        expired_licenses = License.objects.filter(
            Q(status='expired') | Q(ex_date__lt=timezone.now())
        ).count()
        expiring_soon = License.get_expiring_soon().count()
        suspended_licenses = License.objects.filter(status='suspended').count()
        revoked_licenses = License.objects.filter(status='revoked').count()
        pending_licenses = License.objects.filter(status='pending').count()
        
        # License type breakdown
        type_counts = License.objects.values('license_type').annotate(count=Count('id'))
        trial_licenses = next((item['count'] for item in type_counts if item['license_type'] == 'trial'), 0)
        standard_licenses = next((item['count'] for item in type_counts if item['license_type'] == 'standard'), 0)
        premium_licenses = next((item['count'] for item in type_counts if item['license_type'] == 'premium'), 0)
        enterprise_licenses = next((item['count'] for item in type_counts if item['license_type'] == 'enterprise'), 0)
        
        # Usage statistics
        total_activations = License.objects.aggregate(
            total=Count('activation_count')
        )['total'] or 0
        
        avg_duration = License.objects.aggregate(
            avg_duration=Avg('ex_date') - Avg('in_date')
        )
        avg_license_duration = 0
        if avg_duration['avg_duration']:
            avg_license_duration = avg_duration['avg_duration'].days
        
        # Calculate renewal rate (simplified)
        total_renewed = License.objects.filter(activation_count__gt=1).count()
        renewal_rate = (total_renewed / total_licenses * 100) if total_licenses > 0 else 0
        
        # Time-based stats
        current_month_start = timezone.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        current_year_start = timezone.now().replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
        
        licenses_this_month = License.objects.filter(created_at__gte=current_month_start).count()
        licenses_this_year = License.objects.filter(created_at__gte=current_year_start).count()
        
        next_month_start = (current_month_start + timedelta(days=32)).replace(day=1)
        expiring_this_month = License.objects.filter(
            ex_date__gte=current_month_start,
            ex_date__lt=next_month_start,
            status='active'
        ).count()
        
        stats = {
            'total_licenses': total_licenses,
            'active_licenses': active_licenses,
            'expired_licenses': expired_licenses,
            'expiring_soon': expiring_soon,
            'suspended_licenses': suspended_licenses,
            'revoked_licenses': revoked_licenses,
            'pending_licenses': pending_licenses,
            'trial_licenses': trial_licenses,
            'standard_licenses': standard_licenses,
            'premium_licenses': premium_licenses,
            'enterprise_licenses': enterprise_licenses,
            'total_activations': total_activations,
            'avg_license_duration': avg_license_duration,
            'renewal_rate': renewal_rate,
            'licenses_this_month': licenses_this_month,
            'licenses_this_year': licenses_this_year,
            'expiring_this_month': expiring_this_month,
        }
        
        serializer = LicenseStatsSerializer(data=stats)
        if serializer.is_valid():
            return Response(serializer.data)
        return Response(stats)
    
    @action(detail=False, methods=['get'])
    def export(self, request):
        """
        Export licenses to CSV
        """
        # Get filtered queryset
        queryset = self.filter_queryset(self.get_queryset())
        
        # Create HTTP response with CSV content type
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="licenses_{timezone.now().strftime("%Y%m%d_%H%M%S")}.csv"'
        
        # Create CSV writer
        writer = csv.writer(response)
        
        # Write header row
        header = [
            'License Number', 'License Key', 'Software Name', 'Version',
            'License Type', 'Status', 'Issue Date', 'Expiry Date',
            'Licensed To', 'Organization', 'Contact Email', 'Max Users',
            'Max Installations', 'Activated Date', 'Activation Count',
            'Last Used', 'Auto Renewal', 'Support Expires', 'Maintenance Expires',
            'Customer Name', 'Customer Email', 'Customer Phone', 'Product Name',
            'Product SKU', 'Shop Name', 'Purchase Date', 'Purchase Amount',
            'Days Until Expiry', 'License Age (Days)', 'Created At', 'Updated At'
        ]
        writer.writerow(header)
        
        # Serialize and write data rows
        serializer = LicenseExportSerializer(queryset, many=True)
        for license_data in serializer.data:
            row = [
                license_data.get('license_number', ''),
                license_data.get('license_key', ''),
                license_data.get('software_name', ''),
                license_data.get('version', ''),
                license_data.get('license_type', ''),
                license_data.get('status', ''),
                license_data.get('in_date', ''),
                license_data.get('ex_date', ''),
                license_data.get('licensed_to', ''),
                license_data.get('organization', ''),
                license_data.get('contact_email', ''),
                license_data.get('max_users', ''),
                license_data.get('max_installations', ''),
                license_data.get('activated_date', ''),
                license_data.get('activation_count', ''),
                license_data.get('last_used_date', ''),
                license_data.get('auto_renewal', ''),
                license_data.get('support_expires', ''),
                license_data.get('maintenance_expires', ''),
                license_data.get('customer_name', ''),
                license_data.get('customer_email', ''),
                license_data.get('customer_phone', ''),
                license_data.get('product_name', ''),
                license_data.get('product_sku', ''),
                license_data.get('shop_name', ''),
                license_data.get('purchase_date', ''),
                license_data.get('purchase_amount', ''),
                license_data.get('days_until_expiry', ''),
                license_data.get('license_age_days', ''),
                license_data.get('created_at', ''),
                license_data.get('updated_at', ''),
            ]
            writer.writerow(row)
        
        return response
    
    @action(detail=False, methods=['post'])
    def bulk_operations(self, request):
        """
        Perform bulk operations on licenses
        """
        operation = request.data.get('operation')
        license_ids = request.data.get('license_ids', [])
        
        if not operation or not license_ids:
            return Response(
                {'error': 'Operation and license_ids are required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        licenses = License.objects.filter(id__in=license_ids)
        
        if operation == 'activate':
            for license_obj in licenses:
                if license_obj.status not in ['revoked'] and not license_obj.is_expired:
                    license_obj.activate()
        elif operation == 'suspend':
            licenses.update(status='suspended')
        elif operation == 'delete':
            count = licenses.count()
            licenses.delete()
            return Response({'message': f'Deleted {count} licenses'})
        else:
            return Response(
                {'error': 'Invalid operation'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        return Response({'message': f'Operation {operation} completed on {licenses.count()} licenses'})
    
    @action(detail=True, methods=['post'])
    def add_feature(self, request, pk=None):
        """
        Add a feature to license
        """
        license_obj = self.get_object()
        feature_name = request.data.get('feature_name')
        
        if not feature_name:
            return Response(
                {'error': 'Feature name is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        license_obj.add_feature(feature_name)
        serializer = LicenseDetailSerializer(license_obj)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def remove_feature(self, request, pk=None):
        """
        Remove a feature from license
        """
        license_obj = self.get_object()
        feature_name = request.data.get('feature_name')
        
        if not feature_name:
            return Response(
                {'error': 'Feature name is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        license_obj.remove_feature(feature_name)
        serializer = LicenseDetailSerializer(license_obj)
        return Response(serializer.data)
