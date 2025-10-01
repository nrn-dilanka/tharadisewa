from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.db.models import Count, Avg, Sum
from django.utils import timezone
from datetime import timedelta
from .models import Repair

@admin.register(Repair)
class RepairAdmin(admin.ModelAdmin):
    """
    Admin interface for Repair model
    """
    
    list_display = [
        'repair_code',
        'date_formatted',
        'customer_link',
        'product_link',
        'purchase_link',
        'repair_type_colored',
        'status_colored',
        'priority_colored',
        'technician_name',
        'estimated_cost',
        'is_overdue_check',
        'days_in_repair_display',
        'created_at'
    ]
    
    list_filter = [
        'repair_type',
        'status',
        'priority',
        'is_under_warranty',
        'quality_check_passed',
        'ready_for_pickup',
        'technician_name',
        'date',
        'estimated_completion',
        'created_at'
    ]
    
    search_fields = [
        'repair_code',
        'problem_description',
        'diagnosis',
        'repair_notes',
        'technician_name',
        'purchase__customer__first_name',
        'purchase__customer__last_name',
        'purchase__customer__username',
        'purchase__product__name'
    ]
    
    readonly_fields = [
        'id',
        'repair_code',
        'customer',
        'product',
        'is_overdue',
        'duration',
        'days_in_repair',
        'customer_info_display',
        'product_info_display',
        'purchase_info_display',
        'repair_summary_display',
        'parts_summary_display',
        'created_at',
        'updated_at'
    ]
    
    fieldsets = (
        ('Basic Information', {
            'fields': (
                'id',
                'repair_code',
                'date',
                'purchase',
                'purchase_info_display'
            )
        }),
        ('Repair Details', {
            'fields': (
                'repair_type',
                'status',
                'priority',
                'problem_description',
                'diagnosis',
                'repair_notes',
                'technician_name'
            )
        }),
        ('Related Information', {
            'fields': (
                'customer_info_display',
                'product_info_display'
            )
        }),
        ('Costs and Parts', {
            'fields': (
                'estimated_cost',
                'actual_cost',
                'parts_used',
                'parts_summary_display'
            )
        }),
        ('Timeline', {
            'fields': (
                'started_date',
                'completed_date',
                'estimated_completion',
                'duration',
                'days_in_repair',
                'is_overdue'
            )
        }),
        ('Quality and Warranty', {
            'fields': (
                'is_under_warranty',
                'warranty_void',
                'quality_check_passed',
                'customer_satisfaction'
            )
        }),
        ('Customer Communication', {
            'fields': (
                'customer_contacted',
                'ready_for_pickup',
                'delivered_date'
            )
        }),
        ('Summary', {
            'fields': (
                'repair_summary_display',
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
    product_link.admin_order_field = 'purchase__product__name'
    
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
    
    def date_formatted(self, obj):
        """
        Display formatted date
        """
        return obj.date.strftime('%Y-%m-%d %H:%M')
    date_formatted.short_description = 'Repair Date'
    date_formatted.admin_order_field = 'date'
    
    def repair_type_colored(self, obj):
        """
        Display repair type with colors
        """
        colors = {
            'warranty': '#28a745',
            'paid': '#17a2b8',
            'emergency': '#dc3545',
            'maintenance': '#ffc107',
            'replacement': '#6f42c1',
            'diagnostic': '#fd7e14',
            'software': '#20c997',
            'hardware': '#6c757d'
        }
        color = colors.get(obj.repair_type, '#6c757d')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color,
            obj.get_repair_type_display()
        )
    repair_type_colored.short_description = 'Repair Type'
    repair_type_colored.admin_order_field = 'repair_type'
    
    def status_colored(self, obj):
        """
        Display status with colors
        """
        colors = {
            'requested': '#6c757d',
            'diagnosed': '#17a2b8',
            'in_progress': '#ffc107',
            'waiting_parts': '#fd7e14',
            'completed': '#28a745',
            'cancelled': '#dc3545',
            'failed': '#dc3545'
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
            'normal': '#17a2b8',
            'high': '#ffc107',
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
    
    def is_overdue_check(self, obj):
        """
        Display overdue status
        """
        if obj.is_overdue:
            return format_html('<span style="color: #dc3545; font-weight: bold;">⚠ OVERDUE</span>')
        elif obj.status == 'completed':
            return format_html('<span style="color: #28a745;">✓ Completed</span>')
        else:
            return format_html('<span style="color: #6c757d;">• On Track</span>')
    is_overdue_check.short_description = 'Timeline'
    
    def days_in_repair_display(self, obj):
        """
        Display days in repair
        """
        days = obj.days_in_repair
        if days > 0:
            if days > 7:
                color = '#dc3545'  # Red for long repairs
            elif days > 3:
                color = '#ffc107'  # Yellow for medium repairs
            else:
                color = '#28a745'  # Green for quick repairs
            
            return format_html(
                '<span style="color: {};">{} days</span>',
                color,
                days
            )
        return '0 days'
    days_in_repair_display.short_description = 'Days in Repair'
    
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
        return 'No customer information'
    customer_info_display.short_description = 'Customer Information'
    
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
    
    def parts_summary_display(self, obj):
        """
        Display formatted parts summary
        """
        if obj.parts_used:
            parts_html = []
            total_cost = 0
            
            for part in obj.parts_used:
                name = part.get('name', 'Unknown')
                quantity = part.get('quantity', 1)
                cost = part.get('cost', 0)
                
                if cost:
                    part_total = float(cost) * int(quantity)
                    total_cost += part_total
                    parts_html.append(
                        f'<strong>{name}</strong>: {quantity} × ${cost} = ${part_total:.2f}'
                    )
                else:
                    parts_html.append(f'<strong>{name}</strong>: {quantity}')
            
            if parts_html:
                parts_display = '<br>'.join(parts_html)
                if total_cost > 0:
                    parts_display += f'<br><strong>Total Parts Cost: ${total_cost:.2f}</strong>'
                return format_html(parts_display)
        
        return 'No parts used'
    parts_summary_display.short_description = 'Parts Used Summary'
    
    def repair_summary_display(self, obj):
        """
        Display formatted repair summary
        """
        return format_html(
            '<strong>Repair Code:</strong> {}<br>'
            '<strong>Type:</strong> {}<br>'
            '<strong>Status:</strong> {}<br>'
            '<strong>Priority:</strong> {}<br>'
            '<strong>Problem:</strong> {}<br>'
            '<strong>Technician:</strong> {}<br>'
            '<strong>Est. Cost:</strong> ${}<br>'
            '<strong>Actual Cost:</strong> ${}<br>'
            '<strong>Under Warranty:</strong> {}<br>'
            '<strong>Days in Repair:</strong> {}<br>'
            '<strong>Quality Check:</strong> {}<br>'
            '<strong>Ready for Pickup:</strong> {}',
            obj.repair_code,
            obj.get_repair_type_display(),
            obj.get_status_display(),
            obj.get_priority_display(),
            obj.problem_description[:100] + ('...' if len(obj.problem_description) > 100 else ''),
            obj.technician_name or 'Not assigned',
            obj.estimated_cost or '0.00',
            obj.actual_cost or '0.00',
            'Yes' if obj.is_under_warranty else 'No',
            obj.days_in_repair,
            'Passed' if obj.quality_check_passed else 'Not checked',
            'Yes' if obj.ready_for_pickup else 'No'
        )
    repair_summary_display.short_description = 'Repair Summary'
    
    actions = [
        'mark_as_in_progress',
        'mark_as_completed',
        'mark_as_cancelled',
        'mark_ready_for_pickup',
        'contact_customers'
    ]
    
    def mark_as_in_progress(self, request, queryset):
        """
        Mark selected repairs as in progress
        """
        updated = 0
        for repair in queryset.filter(status__in=['requested', 'diagnosed']):
            repair.mark_as_started()
            updated += 1
        self.message_user(request, f'{updated} repairs marked as in progress.')
    mark_as_in_progress.short_description = 'Mark as in progress'
    
    def mark_as_completed(self, request, queryset):
        """
        Mark selected repairs as completed
        """
        updated = 0
        for repair in queryset.filter(status='in_progress'):
            repair.mark_as_completed()
            updated += 1
        self.message_user(request, f'{updated} repairs marked as completed.')
    mark_as_completed.short_description = 'Mark as completed'
    
    def mark_as_cancelled(self, request, queryset):
        """
        Mark selected repairs as cancelled
        """
        updated = queryset.exclude(status__in=['completed', 'cancelled']).update(
            status='cancelled'
        )
        self.message_user(request, f'{updated} repairs marked as cancelled.')
    mark_as_cancelled.short_description = 'Mark as cancelled'
    
    def mark_ready_for_pickup(self, request, queryset):
        """
        Mark selected repairs as ready for pickup
        """
        updated = queryset.filter(status='completed').update(ready_for_pickup=True)
        self.message_user(request, f'{updated} repairs marked as ready for pickup.')
    mark_ready_for_pickup.short_description = 'Mark ready for pickup'
    
    def contact_customers(self, request, queryset):
        """
        Mark customers as contacted for selected repairs
        """
        updated = queryset.update(customer_contacted=True)
        self.message_user(request, f'Customers contacted for {updated} repairs.')
    contact_customers.short_description = 'Mark customers as contacted'
    
    def get_queryset(self, request):
        """
        Optimize queryset with select_related
        """
        return super().get_queryset(request).select_related(
            'purchase__customer',
            'purchase__product'
        )
    
    def changelist_view(self, request, extra_context=None):
        """
        Add summary statistics to changelist view
        """
        extra_context = extra_context or {}
        
        # Calculate summary statistics
        queryset = self.get_queryset(request)
        stats = {
            'total_repairs': queryset.count(),
            'active_repairs': queryset.filter(
                status__in=['requested', 'diagnosed', 'in_progress', 'waiting_parts']
            ).count(),
            'completed_repairs': queryset.filter(status='completed').count(),
            'overdue_repairs': queryset.filter(
                estimated_completion__lt=timezone.now(),
                status__in=['requested', 'diagnosed', 'in_progress', 'waiting_parts']
            ).count() if queryset.exists() else 0,
            'ready_for_pickup': queryset.filter(ready_for_pickup=True, delivered_date__isnull=True).count(),
            'average_repair_time': 0,
            'total_repair_cost': queryset.filter(actual_cost__isnull=False).aggregate(
                total=Sum('actual_cost')
            )['total'] or 0,
        }
        
        # Calculate average repair time
        completed_repairs = queryset.filter(
            status='completed',
            started_date__isnull=False,
            completed_date__isnull=False
        )
        
        if completed_repairs.exists():
            total_days = 0
            count = 0
            for repair in completed_repairs:
                duration = repair.completed_date - repair.started_date
                total_days += duration.days
                count += 1
            
            if count > 0:
                stats['average_repair_time'] = total_days / count
        
        extra_context['summary_stats'] = stats
        
        return super().changelist_view(request, extra_context=extra_context)
