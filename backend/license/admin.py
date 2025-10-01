from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils import timezone
from django.db.models import Q
from .models import License

@admin.register(License)
class LicenseAdmin(admin.ModelAdmin):
    """
    Admin configuration for License model
    """
    list_display = [
        'license_number', 'software_name', 'license_type', 'status_badge',
        'licensed_to', 'customer_link', 'product_link', 'issue_date_short',
        'expiry_date_short', 'expiry_status', 'activation_count', 'auto_renewal'
    ]
    
    list_filter = [
        'license_type', 'status', 'auto_renewal', 'terms_accepted',
        ('in_date', admin.DateFieldListFilter),
        ('ex_date', admin.DateFieldListFilter),
        ('activated_date', admin.DateFieldListFilter),
        'purchase__customer'
    ]
    
    search_fields = [
        'license_number', 'license_key', 'software_name', 'licensed_to',
        'organization', 'contact_email', 'purchase__customer__first_name',
        'purchase__customer__last_name', 'purchase__product__name'
    ]
    
    readonly_fields = [
        'id', 'license_number', 'license_key', 'created_at', 'updated_at',
        'customer_info', 'product_info', 'license_summary',
        'usage_summary', 'expiry_info'
    ]
    
    fieldsets = (
        ('Basic Information', {
            'fields': (
                'id', 'license_number', 'license_key', 'purchase',
                'software_name', 'version', 'license_type', 'status'
            )
        }),
        ('Dates', {
            'fields': (
                'in_date', 'ex_date', 'activated_date', 'last_used_date',
                'support_expires', 'maintenance_expires'
            )
        }),
        ('License Holder', {
            'fields': (
                'licensed_to', 'organization', 'contact_email'
            )
        }),
        ('Licensing Details', {
            'fields': (
                'max_users', 'max_installations', 'features_enabled',
                'restrictions', 'auto_renewal', 'renewal_price'
            )
        }),
        ('Activation & Usage', {
            'fields': (
                'activation_count', 'usage_data', 'terms_accepted',
                'terms_accepted_date'
            )
        }),
        ('Notes', {
            'fields': ('notes',)
        }),
        ('Related Information', {
            'fields': (
                'customer_info', 'product_info'
            ),
            'classes': ('collapse',)
        }),
        ('Summary Information', {
            'fields': (
                'license_summary', 'usage_summary', 'expiry_info'
            ),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    actions = [
        'activate_licenses', 'suspend_licenses', 'check_expiry_status',
        'export_licenses', 'send_renewal_reminders'
    ]
    
    ordering = ['-in_date', '-created_at']
    date_hierarchy = 'in_date'
    list_per_page = 25
    
    def get_queryset(self, request):
        """
        Optimize queryset with select_related
        """
        return super().get_queryset(request).select_related(
            'purchase', 'purchase__customer', 'purchase__product'
        )
    
    def status_badge(self, obj):
        """
        Display status with color coding
        """
        colors = {
            'active': 'green',
            'expired': 'red',
            'suspended': 'orange',
            'revoked': 'darkred',
            'pending': 'blue'
        }
        color = colors.get(obj.status, 'gray')
        
        # Add warning for expiring licenses
        badge_text = obj.get_status_display()
        if obj.status == 'active' and obj.is_expiring_soon:
            badge_text += ' (Expiring Soon)'
            color = 'orange'
        
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color, badge_text
        )
    status_badge.short_description = 'Status'
    status_badge.admin_order_field = 'status'
    
    def customer_link(self, obj):
        """
        Link to customer admin page
        """
        if obj.customer:
            url = reverse('admin:customer_customer_change', args=[obj.customer.id])
            return format_html(
                '<a href="{}">{}</a>',
                url, obj.customer.get_full_name()
            )
        return '-'
    customer_link.short_description = 'Customer'
    
    def product_link(self, obj):
        """
        Link to product admin page
        """
        if obj.product:
            url = reverse('admin:product_product_change', args=[obj.product.id])
            return format_html(
                '<a href="{}">{}</a>',
                url, obj.product.name
            )
        return '-'
    product_link.short_description = 'Product'
    
    def issue_date_short(self, obj):
        """
        Short format issue date
        """
        return obj.in_date.strftime('%Y-%m-%d') if obj.in_date else '-'
    issue_date_short.short_description = 'Issue Date'
    issue_date_short.admin_order_field = 'in_date'
    
    def expiry_date_short(self, obj):
        """
        Short format expiry date
        """
        return obj.ex_date.strftime('%Y-%m-%d') if obj.ex_date else '-'
    expiry_date_short.short_description = 'Expiry Date'
    expiry_date_short.admin_order_field = 'ex_date'
    
    def expiry_status(self, obj):
        """
        Display expiry status with warning colors
        """
        if obj.is_expired:
            return format_html('<span style="color: red; font-weight: bold;">EXPIRED</span>')
        elif obj.is_expiring_soon:
            days = obj.days_until_expiry
            return format_html(
                '<span style="color: orange; font-weight: bold;">Expires in {} days</span>',
                days
            )
        else:
            days = obj.days_until_expiry
            return format_html(
                '<span style="color: green;">{} days left</span>',
                days if days else 'N/A'
            )
    expiry_status.short_description = 'Expiry Status'
    
    def customer_info(self, obj):
        """
        Display customer information
        """
        if obj.customer:
            return format_html(
                '<strong>Name:</strong> {}<br>'
                '<strong>Email:</strong> {}<br>'
                '<strong>Phone:</strong> {}<br>'
                '<strong>NIC:</strong> {}',
                obj.customer.get_full_name(),
                obj.customer.email or 'N/A',
                obj.customer.phone or 'N/A',
                obj.customer.nic or 'N/A'
            )
        return 'No customer information'
    customer_info.short_description = 'Customer Information'
    
    def product_info(self, obj):
        """
        Display product information
        """
        if obj.product:
            return format_html(
                '<strong>Name:</strong> {}<br>'
                '<strong>SKU:</strong> {}<br>'
                '<strong>Brand:</strong> {}<br>'
                '<strong>Model:</strong> {}<br>'
                '<strong>Price:</strong> {}',
                obj.product.name,
                obj.product.sku or 'N/A',
                obj.product.brand or 'N/A',
                obj.product.model or 'N/A',
                obj.product.price or 'N/A'
            )
        return 'No product information'
    product_info.short_description = 'Product Information'
    
    def license_summary(self, obj):
        """
        Display license summary
        """
        return format_html(
            '<strong>Duration:</strong> {} days<br>'
            '<strong>Age:</strong> {} days<br>'
            '<strong>Active:</strong> {}<br>'
            '<strong>Expired:</strong> {}<br>'
            '<strong>Max Users:</strong> {}<br>'
            '<strong>Max Installations:</strong> {}',
            obj.license_duration or 'N/A',
            obj.days_since_issue or 'N/A',
            'Yes' if obj.is_active else 'No',
            'Yes' if obj.is_expired else 'No',
            obj.max_users,
            obj.max_installations
        )
    license_summary.short_description = 'License Summary'
    
    def usage_summary(self, obj):
        """
        Display usage summary
        """
        last_used = obj.last_used_date.strftime('%Y-%m-%d %H:%M') if obj.last_used_date else 'Never'
        activated = obj.activated_date.strftime('%Y-%m-%d %H:%M') if obj.activated_date else 'Not activated'
        
        return format_html(
            '<strong>Activation Count:</strong> {}<br>'
            '<strong>Activated:</strong> {}<br>'
            '<strong>Last Used:</strong> {}<br>'
            '<strong>Features:</strong> {}',
            obj.activation_count,
            activated,
            last_used,
            ', '.join(obj.features_enabled) if obj.features_enabled else 'None'
        )
    usage_summary.short_description = 'Usage Summary'
    
    def expiry_info(self, obj):
        """
        Display detailed expiry information
        """
        support_expires = obj.support_expires.strftime('%Y-%m-%d') if obj.support_expires else 'N/A'
        maintenance_expires = obj.maintenance_expires.strftime('%Y-%m-%d') if obj.maintenance_expires else 'N/A'
        
        return format_html(
            '<strong>Days Until Expiry:</strong> {}<br>'
            '<strong>Expiring Soon:</strong> {}<br>'
            '<strong>Auto Renewal:</strong> {}<br>'
            '<strong>Renewal Price:</strong> {}<br>'
            '<strong>Support Expires:</strong> {}<br>'
            '<strong>Maintenance Expires:</strong> {}',
            obj.days_until_expiry if obj.days_until_expiry is not None else 'N/A',
            'Yes' if obj.is_expiring_soon else 'No',
            'Yes' if obj.auto_renewal else 'No',
            obj.renewal_price or 'N/A',
            support_expires,
            maintenance_expires
        )
    expiry_info.short_description = 'Expiry Information'
    
    # Admin Actions
    def activate_licenses(self, request, queryset):
        """
        Activate selected licenses
        """
        count = 0
        for license_obj in queryset:
            if license_obj.status not in ['revoked'] and not license_obj.is_expired:
                license_obj.activate()
                count += 1
        
        self.message_user(request, f'Activated {count} licenses.')
    activate_licenses.short_description = 'Activate selected licenses'
    
    def suspend_licenses(self, request, queryset):
        """
        Suspend selected licenses
        """
        count = queryset.update(status='suspended')
        self.message_user(request, f'Suspended {count} licenses.')
    suspend_licenses.short_description = 'Suspend selected licenses'
    
    def check_expiry_status(self, request, queryset):
        """
        Check and update expiry status for selected licenses
        """
        count = 0
        for license_obj in queryset:
            if license_obj.check_and_update_status():
                count += 1
        
        self.message_user(request, f'Updated expiry status for {count} licenses.')
    check_expiry_status.short_description = 'Check expiry status'
    
    def export_licenses(self, request, queryset):
        """
        Export selected licenses (placeholder - would need implementation)
        """
        count = queryset.count()
        self.message_user(request, f'Export functionality for {count} licenses (implement CSV export).')
    export_licenses.short_description = 'Export selected licenses'
    
    def send_renewal_reminders(self, request, queryset):
        """
        Send renewal reminders (placeholder - would need email implementation)
        """
        expiring_licenses = queryset.filter(
            status='active',
            ex_date__lte=timezone.now() + timezone.timedelta(days=30),
            ex_date__gt=timezone.now()
        )
        count = expiring_licenses.count()
        self.message_user(
            request, 
            f'Renewal reminders would be sent for {count} expiring licenses (implement email functionality).'
        )
    send_renewal_reminders.short_description = 'Send renewal reminders'
    
    def get_list_filter(self, request):
        """
        Dynamic list filters
        """
        filters = list(self.list_filter)
        
        # Add customer filter if there are customers
        if License.objects.exclude(purchase__customer__isnull=True).exists():
            filters.append('purchase__customer')
        
        # Add product filter if there are products
        if License.objects.exclude(purchase__product__isnull=True).exists():
            filters.append('purchase__product')
        
        return filters
    
    def changelist_view(self, request, extra_context=None):
        """
        Add custom context to changelist view
        """
        extra_context = extra_context or {}
        
        # Add summary statistics
        total_licenses = License.objects.count()
        active_licenses = License.objects.filter(status='active').count()
        expiring_soon = License.objects.filter(
            status='active',
            ex_date__lte=timezone.now() + timezone.timedelta(days=30),
            ex_date__gt=timezone.now()
        ).count()
        expired_licenses = License.objects.filter(
            Q(status='expired') | Q(ex_date__lt=timezone.now())
        ).count()
        
        extra_context['license_stats'] = {
            'total': total_licenses,
            'active': active_licenses,
            'expiring_soon': expiring_soon,
            'expired': expired_licenses,
        }
        
        return super().changelist_view(request, extra_context)
