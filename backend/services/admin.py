from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.db.models import Count, Avg
from django.utils import timezone
from .models import Service

@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    """
    Admin interface for Service model
    """
    
    list_display = [
        'service_code',
        'date_formatted',
        'service_type_colored',
        'customer_link',
        'product_link',
        'purchase_link',
        'shop_name',
        'status_colored',
        'priority_colored',
        'service_cost',
        'rating_stars',
        'is_under_warranty',
        'is_overdue_check',
        'created_at'
    ]
    
    list_filter = [
        'service_type',
        'status',
        'priority',
        'is_under_warranty',
        'is_active',
        'date',
        'created_at',
        'product__shop',
        'rating'
    ]
    
    search_fields = [
        'description',
        'technician_notes',
        'customer_feedback',
        'purchase__customer__username',
        'purchase__customer__first_name',
        'purchase__customer__last_name',
        'product__name',
        'product__shop__name',
        'id'
    ]
    
    readonly_fields = [
        'id',
        'service_code',
        'customer_display',
        'purchase_info_display',
        'product_info_display',
        'shop_info_display',
        'service_summary_display',
        'duration_since_purchase',
        'is_overdue',
        'created_at',
        'updated_at'
    ]
    
    fieldsets = (
        ('Basic Information', {
            'fields': (
                'id',
                'service_code',
                'date',
                'service_type',
                'description'
            )
        }),
        ('References', {
            'fields': (
                'purchase',
                'purchase_info_display',
                'product',
                'product_info_display',
                'customer_display',
                'shop_info_display'
            )
        }),
        ('Service Details', {
            'fields': (
                'status',
                'priority',
                'service_cost',
                'is_under_warranty',
                'scheduled_date',
                'completed_date',
                'warranty_expires',
                'is_active'
            )
        }),
        ('Notes & Feedback', {
            'fields': (
                'technician_notes',
                'customer_feedback',
                'rating'
            )
        }),
        ('Computed Fields', {
            'fields': (
                'duration_since_purchase',
                'is_overdue',
                'service_summary_display'
            ),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': (
                'created_at',
                'updated_at'
            ),
            'classes': ('collapse',)
        })
    )
    
    ordering = ['-date', '-created_at']
    list_per_page = 25
    date_hierarchy = 'date'
    
    def customer_link(self, obj):
        """
        Display customer name as a link to customer admin
        """
        if obj.customer:
            url = reverse('admin:customer_customer_change', args=[obj.customer.id])
            return format_html('<a href="{}">{}</a>', url, obj.customer.get_full_name())
        return '-'
    customer_link.short_description = 'Customer'
    customer_link.admin_order_field = 'purchase__customer__first_name'
    
    def product_link(self, obj):
        """
        Display product name as a link to product admin
        """
        if obj.product:
            url = reverse('admin:product_product_change', args=[obj.product.id])
            return format_html('<a href="{}">{}</a>', url, obj.product.name)
        return '-'
    product_link.short_description = 'Product'
    product_link.admin_order_field = 'product__name'
    
    def purchase_link(self, obj):
        """
        Display purchase code as a link to purchase admin
        """
        if obj.purchase:
            url = reverse('admin:purchase_purchase_change', args=[obj.purchase.id])
            return format_html('<a href="{}">{}</a>', url, obj.purchase.purchase_code)
        return '-'
    purchase_link.short_description = 'Purchase'
    purchase_link.admin_order_field = 'purchase__date'
    
    def shop_name(self, obj):
        """
        Display shop name
        """
        if obj.shop:
            return obj.shop.name
        return '-'
    shop_name.short_description = 'Shop'
    shop_name.admin_order_field = 'product__shop__name'
    
    def date_formatted(self, obj):
        """
        Display formatted date
        """
        return obj.date.strftime('%Y-%m-%d %H:%M')
    date_formatted.short_description = 'Service Date'
    date_formatted.admin_order_field = 'date'
    
    def service_type_colored(self, obj):
        """
        Display service type with colors
        """
        colors = {
            'warranty': '#28a745',
            'repair': '#dc3545',
            'maintenance': '#ffc107',
            'replacement': '#6f42c1',
            'installation': '#17a2b8',
            'support': '#fd7e14',
            'consultation': '#6c757d',
            'training': '#20c997'
        }
        color = colors.get(obj.service_type, '#6c757d')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color,
            obj.get_service_type_display()
        )
    service_type_colored.short_description = 'Service Type'
    service_type_colored.admin_order_field = 'service_type'
    
    def status_colored(self, obj):
        """
        Display status with colors
        """
        colors = {
            'requested': '#6c757d',
            'in_progress': '#ffc107',
            'completed': '#28a745',
            'cancelled': '#dc3545',
            'on_hold': '#fd7e14'
        }
        color = colors.get(obj.status, '#6c757d')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color,
            obj.get_status_display()
        )
    status_colored.short_description = 'Status'
    status_colored.admin_order_field = 'status'
    
    def priority_colored(self, obj):
        """
        Display priority with colors
        """
        colors = {
            'low': '#28a745',
            'medium': '#ffc107',
            'high': '#fd7e14',
            'urgent': '#dc3545'
        }
        color = colors.get(obj.priority, '#6c757d')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color,
            obj.get_priority_display()
        )
    priority_colored.short_description = 'Priority'
    priority_colored.admin_order_field = 'priority'
    
    def rating_stars(self, obj):
        """
        Display rating as stars
        """
        if obj.rating:
            stars = '★' * obj.rating + '☆' * (5 - obj.rating)
            return format_html('<span style="color: #ffc107;">{}</span> ({})', stars, obj.rating)
        return 'No rating'
    rating_stars.short_description = 'Rating'
    rating_stars.admin_order_field = 'rating'
    
    def is_overdue_check(self, obj):
        """
        Display overdue status
        """
        if obj.is_overdue:
            return format_html('<span style="color: #dc3545; font-weight: bold;">⚠ OVERDUE</span>')
        return format_html('<span style="color: #28a745;">✓ On Time</span>')
    is_overdue_check.short_description = 'Schedule'
    
    def customer_display(self, obj):
        """
        Display formatted customer information
        """
        if obj.customer:
            return format_html(
                '<strong>Name:</strong> {}<br>'
                '<strong>Username:</strong> {}<br>'
                '<strong>Email:</strong> {}',
                obj.customer.get_full_name(),
                obj.customer.username,
                obj.customer.email or 'Not provided'
            )
        return 'No customer information'
    customer_display.short_description = 'Customer Information'
    
    def purchase_info_display(self, obj):
        """
        Display formatted purchase information
        """
        if obj.purchase:
            return format_html(
                '<strong>Code:</strong> {}<br>'
                '<strong>Date:</strong> {}<br>'
                '<strong>Amount:</strong> ${}<br>'
                '<strong>Status:</strong> {}',
                obj.purchase.purchase_code,
                obj.purchase.date.strftime('%Y-%m-%d'),
                obj.purchase.total_amount,
                obj.purchase.get_payment_status_display()
            )
        return 'No purchase information'
    purchase_info_display.short_description = 'Purchase Information'
    
    def product_info_display(self, obj):
        """
        Display formatted product information
        """
        if obj.product:
            return format_html(
                '<strong>Name:</strong> {}<br>'
                '<strong>Code:</strong> {}<br>'
                '<strong>Price:</strong> ${}<br>'
                '<strong>Stock:</strong> {}',
                obj.product.name,
                obj.product.product_code,
                obj.product.price or 'Not set',
                obj.product.stock_quantity
            )
        return 'No product information'
    product_info_display.short_description = 'Product Information'
    
    def shop_info_display(self, obj):
        """
        Display formatted shop information
        """
        if obj.shop:
            return format_html(
                '<strong>Shop:</strong> {}<br>'
                '<strong>Address:</strong> {}<br>'
                '<strong>Owner:</strong> {}',
                obj.shop.name,
                obj.shop.full_address,
                obj.shop.customer.get_full_name()
            )
        return 'No shop information'
    shop_info_display.short_description = 'Shop Information'
    
    def service_summary_display(self, obj):
        """
        Display formatted service summary
        """
        return format_html(
            '<strong>Service Code:</strong> {}<br>'
            '<strong>Type:</strong> {}<br>'
            '<strong>Status:</strong> {}<br>'
            '<strong>Priority:</strong> {}<br>'
            '<strong>Cost:</strong> ${}<br>'
            '<strong>Under Warranty:</strong> {}<br>'
            '<strong>Rating:</strong> {}',
            obj.service_code,
            obj.get_service_type_display(),
            obj.get_status_display(),
            obj.get_priority_display(),
            obj.service_cost,
            'Yes' if obj.is_under_warranty else 'No',
            f'{obj.rating}/5' if obj.rating else 'Not rated'
        )
    service_summary_display.short_description = 'Service Summary'
    
    actions = [
        'mark_as_requested',
        'mark_as_in_progress',
        'mark_as_completed',
        'mark_as_cancelled',
        'activate_services',
        'deactivate_services'
    ]
    
    def mark_as_requested(self, request, queryset):
        """
        Mark selected services as requested
        """
        updated = queryset.update(status='requested')
        self.message_user(request, f'{updated} services marked as requested.')
    mark_as_requested.short_description = 'Mark as requested'
    
    def mark_as_in_progress(self, request, queryset):
        """
        Mark selected services as in progress
        """
        updated = queryset.update(status='in_progress')
        self.message_user(request, f'{updated} services marked as in progress.')
    mark_as_in_progress.short_description = 'Mark as in progress'
    
    def mark_as_completed(self, request, queryset):
        """
        Mark selected services as completed
        """
        from django.utils import timezone
        updated = 0
        for service in queryset:
            service.status = 'completed'
            if not service.completed_date:
                service.completed_date = timezone.now()
            service.save()
            updated += 1
        self.message_user(request, f'{updated} services marked as completed.')
    mark_as_completed.short_description = 'Mark as completed'
    
    def mark_as_cancelled(self, request, queryset):
        """
        Mark selected services as cancelled
        """
        updated = queryset.update(status='cancelled')
        self.message_user(request, f'{updated} services marked as cancelled.')
    mark_as_cancelled.short_description = 'Mark as cancelled'
    
    def activate_services(self, request, queryset):
        """
        Activate selected services
        """
        updated = queryset.update(is_active=True)
        self.message_user(request, f'{updated} services were activated.')
    activate_services.short_description = 'Activate selected services'
    
    def deactivate_services(self, request, queryset):
        """
        Deactivate selected services
        """
        updated = queryset.update(is_active=False)
        self.message_user(request, f'{updated} services were deactivated.')
    deactivate_services.short_description = 'Deactivate selected services'
    
    def get_queryset(self, request):
        """
        Optimize queryset with select_related
        """
        return super().get_queryset(request).select_related(
            'purchase__customer',
            'product__shop__customer'
        )
    
    def changelist_view(self, request, extra_context=None):
        """
        Add summary statistics to changelist view
        """
        extra_context = extra_context or {}
        
        # Calculate summary statistics
        queryset = self.get_queryset(request)
        stats = {
            'total_services': queryset.count(),
            'completed_services': queryset.filter(status='completed').count(),
            'in_progress_services': queryset.filter(status='in_progress').count(),
            'overdue_services': queryset.filter(
                scheduled_date__lt=timezone.now(),
                status__in=['requested', 'in_progress', 'on_hold']
            ).count() if queryset.exists() else 0,
            'average_rating': queryset.filter(rating__isnull=False).aggregate(
                avg=Avg('rating')
            )['avg'] or 0,
        }
        
        extra_context['summary_stats'] = stats
        
        return super().changelist_view(request, extra_context=extra_context)
