from django.contrib import admin
from .models import CustomerContact


@admin.register(CustomerContact)
class CustomerContactAdmin(admin.ModelAdmin):
    """
    Admin interface for CustomerContact model
    """
    list_display = (
        'id', 'customer', 'email', 'wa_number', 'tp_number',
        'is_primary', 'is_active', 'created_at'
    )
    list_filter = (
        'is_primary', 'is_active', 'created_at', 'updated_at'
    )
    search_fields = (
        'customer__username', 'customer__first_name', 'customer__last_name',
        'email', 'wa_number', 'tp_number'
    )
    ordering = ('-created_at',)
    
    fieldsets = (
        ('Customer Information', {
            'fields': ('customer',)
        }),
        ('Contact Details', {
            'fields': ('email', 'wa_number', 'tp_number')
        }),
        ('Status', {
            'fields': ('is_primary', 'is_active')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ('created_at', 'updated_at')
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('customer')
    
    def customer_name(self, obj):
        return obj.customer.full_name
    customer_name.short_description = 'Customer Name'
