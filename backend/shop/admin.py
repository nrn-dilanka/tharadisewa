from django.contrib import admin
from .models import Shop


@admin.register(Shop)
class ShopAdmin(admin.ModelAdmin):
    """
    Admin interface for Shop model
    """
    list_display = (
        'id', 'name', 'customer', 'city', 'postal_code',
        'is_active', 'location_count', 'created_at'
    )
    list_filter = (
        'is_active', 'city', 'postal_code', 'created_at', 'updated_at'
    )
    search_fields = (
        'name', 'customer__username', 'customer__first_name', 
        'customer__last_name', 'address_line_1', 'address_line_2',
        'address_line_3', 'city', 'postal_code', 'phone_number', 'email'
    )
    ordering = ('-created_at',)
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'customer')
        }),
        ('Address Details', {
            'fields': (
                'address_line_1', 'address_line_2', 'address_line_3',
                'city', 'postal_code'
            )
        }),
        ('Contact Information', {
            'fields': ('phone_number', 'email')
        }),
        ('Additional Info', {
            'fields': ('description', 'is_active')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ('created_at', 'updated_at', 'location_count')
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('customer')
    
    def customer_name(self, obj):
        return obj.customer.full_name
    customer_name.short_description = 'Customer Name'
    
    def location_count(self, obj):
        return obj.location_count
    location_count.short_description = 'Locations'
