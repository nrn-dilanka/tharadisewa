from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.db.models import Sum
from .models import Purchase

@admin.register(Purchase)
class PurchaseAdmin(admin.ModelAdmin):
    """
    Admin interface for Purchase model
    """
    
    list_display = [
        'purchase_code',
        'date_formatted',
        'customer_link',
        'product_link',
        'quantity',
        'unit_price',
        'total_amount',
        'payment_status_colored',
        'purchase_method',
        'is_active',
        'created_at'
    ]
    
    list_filter = [
        'payment_status',
        'purchase_method',
        'is_active',
        'date',
        'created_at',
        'customer'
    ]
    
    search_fields = [
        'customer__username',
        'customer__first_name',
        'customer__last_name',
        'product__name',
        'notes',
        'id'
    ]
    
    readonly_fields = [
        'id',
        'purchase_code',
        'total_amount',
        'customer_info_display',
        'product_info_display',
        'purchase_summary_display',
        'created_at',
        'updated_at'
    ]
    
    fieldsets = (
        ('Basic Information', {
            'fields': (
                'id',
                'purchase_code',
                'date'
            )
        }),
        ('Customer & Product', {
            'fields': (
                'customer',
                'customer_info_display',
                'product',
                'product_info_display'
            )
        }),
        ('Purchase Details', {
            'fields': (
                'quantity',
                'unit_price',
                'total_amount',
                'payment_status',
                'purchase_method',
                'notes',
                'is_active'
            )
        }),
        ('Summary', {
            'fields': (
                'purchase_summary_display',
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
    customer_link.admin_order_field = 'customer__first_name'
    
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
    
    def date_formatted(self, obj):
        """
        Display formatted date
        """
        return obj.date.strftime('%Y-%m-%d %H:%M')
    date_formatted.short_description = 'Purchase Date'
    date_formatted.admin_order_field = 'date'
    
    def payment_status_colored(self, obj):
        """
        Display payment status with colors
        """
        colors = {
            'pending': '#ffc107',
            'completed': '#28a745',
            'failed': '#dc3545',
            'refunded': '#6c757d'
        }
        color = colors.get(obj.payment_status, '#6c757d')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color,
            obj.get_payment_status_display()
        )
    payment_status_colored.short_description = 'Payment Status'
    payment_status_colored.admin_order_field = 'payment_status'
    
    def customer_info_display(self, obj):
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
        return 'No customer assigned'
    customer_info_display.short_description = 'Customer Information'
    
    def product_info_display(self, obj):
        """
        Display formatted product information
        """
        if obj.product:
            return format_html(
                '<strong>Product:</strong> {}<br>'
                '<strong>Code:</strong> {}<br>'
                '<strong>Current Price:</strong> ${}<br>'
                '<strong>Stock:</strong> {}',
                obj.product.name,
                obj.product.product_code,
                obj.product.price or 'Not set',
                obj.product.stock_quantity
            )
        return 'No product assigned'
    product_info_display.short_description = 'Product Information'
    
    def purchase_summary_display(self, obj):
        """
        Display formatted purchase summary
        """
        return format_html(
            '<strong>Purchase Code:</strong> {}<br>'
            '<strong>Date:</strong> {}<br>'
            '<strong>Quantity:</strong> {}<br>'
            '<strong>Unit Price:</strong> ${}<br>'
            '<strong>Total Amount:</strong> ${}<br>'
            '<strong>Payment Status:</strong> {}<br>'
            '<strong>Payment Method:</strong> {}',
            obj.purchase_code,
            obj.date.strftime('%Y-%m-%d %H:%M'),
            obj.quantity,
            obj.unit_price,
            obj.total_amount,
            obj.get_payment_status_display(),
            obj.get_purchase_method_display()
        )
    purchase_summary_display.short_description = 'Purchase Summary'
    
    actions = [
        'mark_as_completed',
        'mark_as_pending',
        'mark_as_failed',
        'activate_purchases',
        'deactivate_purchases'
    ]
    
    def mark_as_completed(self, request, queryset):
        """
        Mark selected purchases as completed
        """
        updated = queryset.update(payment_status='completed')
        self.message_user(
            request,
            f'{updated} purchases marked as completed.'
        )
    mark_as_completed.short_description = 'Mark selected purchases as completed'
    
    def mark_as_pending(self, request, queryset):
        """
        Mark selected purchases as pending
        """
        updated = queryset.update(payment_status='pending')
        self.message_user(
            request,
            f'{updated} purchases marked as pending.'
        )
    mark_as_pending.short_description = 'Mark selected purchases as pending'
    
    def mark_as_failed(self, request, queryset):
        """
        Mark selected purchases as failed
        """
        updated = queryset.update(payment_status='failed')
        self.message_user(
            request,
            f'{updated} purchases marked as failed.'
        )
    mark_as_failed.short_description = 'Mark selected purchases as failed'
    
    def activate_purchases(self, request, queryset):
        """
        Activate selected purchases
        """
        updated = queryset.update(is_active=True)
        self.message_user(
            request,
            f'{updated} purchases were activated.'
        )
    activate_purchases.short_description = 'Activate selected purchases'
    
    def deactivate_purchases(self, request, queryset):
        """
        Deactivate selected purchases
        """
        updated = queryset.update(is_active=False)
        self.message_user(
            request,
            f'{updated} purchases were deactivated.'
        )
    deactivate_purchases.short_description = 'Deactivate selected purchases'
    
    def get_queryset(self, request):
        """
        Optimize queryset with select_related
        """
        return super().get_queryset(request).select_related(
            'customer',
            'product'
        )
    
    def changelist_view(self, request, extra_context=None):
        """
        Add summary statistics to changelist view
        """
        extra_context = extra_context or {}
        
        # Calculate summary statistics
        queryset = self.get_queryset(request)
        stats = {
            'total_purchases': queryset.count(),
            'completed_purchases': queryset.filter(payment_status='completed').count(),
            'pending_purchases': queryset.filter(payment_status='pending').count(),
            'total_revenue': queryset.filter(payment_status='completed').aggregate(
                total=Sum('total_amount')
            )['total'] or 0,
        }
        
        extra_context['summary_stats'] = stats
        
        return super().changelist_view(request, extra_context=extra_context)
