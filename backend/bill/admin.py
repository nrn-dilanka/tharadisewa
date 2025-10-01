from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.db.models import Sum, Avg
from django.utils import timezone
from .models import Bill

@admin.register(Bill)
class BillAdmin(admin.ModelAdmin):
    """
    Admin interface for Bill model
    """
    
    list_display = [
        'bill_number',
        'date_formatted',
        'customer_link',
        'service_link',
        'purchase_link',
        'amount_colored',
        'status_colored',
        'due_date_formatted',
        'is_overdue_check',
        'payment_status_display',
        'created_at'
    ]
    
    list_filter = [
        'status',
        'date',
        'due_date',
        'service__service_type',
        'created_at',
        'tax_rate',
    ]
    
    search_fields = [
        'bill_number',
        'notes',
        'purchase__customer__first_name',
        'purchase__customer__last_name',
        'purchase__customer__username',
        'service__description',
        'service__product__name'
    ]
    
    readonly_fields = [
        'id',
        'bill_number',
        'bill_code',
        'amount',
        'tax_amount',
        'discount_amount',
        'customer_display',
        'service_info_display',
        'purchase_info_display',
        'bill_summary_display',
        'is_overdue',
        'days_until_due',
        'payment_method_display',
        'created_at',
        'updated_at'
    ]
    
    fieldsets = (
        ('Basic Information', {
            'fields': (
                'id',
                'bill_number',
                'bill_code',
                'date',
                'amount'
            )
        }),
        ('References', {
            'fields': (
                'service',
                'service_info_display',
                'purchase', 
                'purchase_info_display',
                'customer_display'
            )
        }),
        ('Bill Details', {
            'fields': (
                'subtotal',
                'tax_rate',
                'tax_amount',
                'discount_rate',
                'discount_amount',
                'status',
                'due_date',
                'paid_date'
            )
        }),
        ('Additional Information', {
            'fields': (
                'notes',
                'is_overdue',
                'days_until_due',
                'payment_method_display'
            )
        }),
        ('Summary', {
            'fields': (
                'bill_summary_display',
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
    
    def service_link(self, obj):
        """
        Display service as a link to service admin
        """
        if obj.service:
            url = reverse('admin:services_service_change', args=[obj.service.id])
            return format_html('<a href="{}">{}</a>', url, obj.service.service_code)
        return '-'
    service_link.short_description = 'Service'
    service_link.admin_order_field = 'service__date'
    
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
    date_formatted.short_description = 'Bill Date'
    date_formatted.admin_order_field = 'date'
    
    def due_date_formatted(self, obj):
        """
        Display formatted due date
        """
        if obj.due_date:
            return obj.due_date.strftime('%Y-%m-%d %H:%M')
        return 'No due date'
    due_date_formatted.short_description = 'Due Date'
    due_date_formatted.admin_order_field = 'due_date'
    
    def amount_colored(self, obj):
        """
        Display amount with colors based on value
        """
        if obj.amount > 1000:
            color = '#28a745'  # Green for high amounts
        elif obj.amount > 500:
            color = '#ffc107'  # Yellow for medium amounts
        else:
            color = '#6c757d'  # Gray for low amounts
        
        return format_html(
            '<span style="color: {}; font-weight: bold;">${}</span>',
            color,
            obj.amount
        )
    amount_colored.short_description = 'Amount'
    amount_colored.admin_order_field = 'amount'
    
    def status_colored(self, obj):
        """
        Display status with colors
        """
        colors = {
            'pending': '#ffc107',
            'paid': '#28a745',
            'overdue': '#dc3545',
            'cancelled': '#6c757d'
        }
        color = colors.get(obj.status, '#6c757d')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color,
            obj.get_status_display()
        )
    status_colored.short_description = 'Status'
    status_colored.admin_order_field = 'status'
    
    def is_overdue_check(self, obj):
        """
        Display overdue status
        """
        if obj.is_overdue:
            return format_html('<span style="color: #dc3545; font-weight: bold;">⚠ OVERDUE</span>')
        elif obj.status == 'paid':
            return format_html('<span style="color: #28a745;">✓ Paid</span>')
        else:
            return format_html('<span style="color: #6c757d;">• On Time</span>')
    is_overdue_check.short_description = 'Payment Status'
    
    def payment_status_display(self, obj):
        """
        Display payment status with date
        """
        if obj.status == 'paid' and obj.paid_date:
            return format_html(
                '<span style="color: #28a745;">Paid on {}</span>',
                obj.paid_date.strftime('%Y-%m-%d')
            )
        elif obj.is_overdue:
            days_overdue = abs(obj.days_until_due) if obj.days_until_due else 0
            return format_html(
                '<span style="color: #dc3545;">{} days overdue</span>',
                days_overdue
            )
        elif obj.days_until_due is not None:
            if obj.days_until_due > 0:
                return format_html(
                    '<span style="color: #ffc107;">{} days remaining</span>',
                    obj.days_until_due
                )
            else:
                return format_html('<span style="color: #6c757d;">No due date</span>')
        return 'Pending'
    payment_status_display.short_description = 'Payment Info'
    
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
    
    def service_info_display(self, obj):
        """
        Display formatted service information
        """
        if obj.service:
            return format_html(
                '<strong>Code:</strong> {}<br>'
                '<strong>Type:</strong> {}<br>'
                '<strong>Date:</strong> {}<br>'
                '<strong>Status:</strong> {}',
                obj.service.service_code,
                obj.service.get_service_type_display(),
                obj.service.date.strftime('%Y-%m-%d'),
                obj.service.get_status_display()
            )
        return 'No service information'
    service_info_display.short_description = 'Service Information'
    
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
    
    def bill_summary_display(self, obj):
        """
        Display formatted bill summary
        """
        return format_html(
            '<strong>Bill Number:</strong> {}<br>'
            '<strong>Subtotal:</strong> ${}<br>'
            '<strong>Tax ({}%):</strong> ${}<br>'
            '<strong>Discount ({}%):</strong> ${}<br>'
            '<strong>Total Amount:</strong> ${}<br>'
            '<strong>Status:</strong> {}<br>'
            '<strong>Due Date:</strong> {}',
            obj.bill_number,
            obj.subtotal,
            obj.tax_rate,
            obj.tax_amount,
            obj.discount_rate,
            obj.discount_amount,
            obj.amount,
            obj.get_status_display(),
            obj.due_date.strftime('%Y-%m-%d %H:%M') if obj.due_date else 'Not set'
        )
    bill_summary_display.short_description = 'Bill Summary'
    
    actions = [
        'mark_as_paid',
        'mark_as_pending',
        'mark_as_cancelled',
        'send_reminder',
        'apply_late_fee'
    ]
    
    def mark_as_paid(self, request, queryset):
        """
        Mark selected bills as paid
        """
        updated = 0
        for bill in queryset.filter(status__in=['pending', 'overdue']):
            bill.mark_as_paid()
            updated += 1
        self.message_user(request, f'{updated} bills marked as paid.')
    mark_as_paid.short_description = 'Mark as paid'
    
    def mark_as_pending(self, request, queryset):
        """
        Mark selected bills as pending
        """
        updated = queryset.exclude(status='paid').update(
            status='pending',
            paid_date=None
        )
        self.message_user(request, f'{updated} bills marked as pending.')
    mark_as_pending.short_description = 'Mark as pending'
    
    def mark_as_cancelled(self, request, queryset):
        """
        Mark selected bills as cancelled
        """
        updated = queryset.exclude(status='paid').update(status='cancelled')
        self.message_user(request, f'{updated} bills marked as cancelled.')
    mark_as_cancelled.short_description = 'Mark as cancelled'
    
    def send_reminder(self, request, queryset):
        """
        Send payment reminders for selected bills
        """
        pending_bills = queryset.filter(status__in=['pending', 'overdue'])
        count = pending_bills.count()
        
        # Here you would implement actual reminder sending logic
        # For now, just show a message
        self.message_user(request, f'Reminders sent for {count} bills.')
    send_reminder.short_description = 'Send payment reminders'
    
    def apply_late_fee(self, request, queryset):
        """
        Apply late fees to overdue bills
        """
        overdue_bills = queryset.filter(status='overdue')
        updated = 0
        
        for bill in overdue_bills:
            # Apply 5% late fee
            late_fee = bill.subtotal * 0.05
            bill.subtotal += late_fee
            bill.save()  # This will recalculate the total amount
            updated += 1
        
        self.message_user(request, f'Late fees applied to {updated} bills.')
    apply_late_fee.short_description = 'Apply late fees to overdue bills'
    
    def get_queryset(self, request):
        """
        Optimize queryset with select_related
        """
        return super().get_queryset(request).select_related(
            'service',
            'purchase__customer',
            'service__product'
        )
    
    def changelist_view(self, request, extra_context=None):
        """
        Add summary statistics to changelist view
        """
        extra_context = extra_context or {}
        
        # Calculate summary statistics
        queryset = self.get_queryset(request)
        stats = {
            'total_bills': queryset.count(),
            'total_amount': queryset.aggregate(total=Sum('amount'))['total'] or 0,
            'paid_bills': queryset.filter(status='paid').count(),
            'paid_amount': queryset.filter(status='paid').aggregate(total=Sum('amount'))['total'] or 0,
            'pending_bills': queryset.filter(status='pending').count(),
            'pending_amount': queryset.filter(status='pending').aggregate(total=Sum('amount'))['total'] or 0,
            'overdue_bills': queryset.filter(status='overdue').count(),
            'overdue_amount': queryset.filter(status='overdue').aggregate(total=Sum('amount'))['total'] or 0,
            'average_bill_amount': queryset.aggregate(avg=Avg('amount'))['avg'] or 0,
        }
        
        extra_context['summary_stats'] = stats
        
        return super().changelist_view(request, extra_context=extra_context)
