from django.contrib import admin
from .models import CustomerLocation


@admin.register(CustomerLocation)
class CustomerLocationAdmin(admin.ModelAdmin):
    """
    Admin interface for CustomerLocation model
    """
    list_display = (
        'id', 'shop', 'customer_name', 'latitude', 'longitude',
        'location_name', 'is_primary', 'is_active', 'created_at'
    )
    list_filter = (
        'is_primary', 'is_active', 'created_at', 'updated_at',
        'shop__city'
    )
    search_fields = (
        'location_name', 'address_description', 'shop__name',
        'shop__customer__username', 'shop__customer__first_name', 
        'shop__customer__last_name'
    )
    ordering = ('-created_at',)
    
    fieldsets = (
        ('Shop Information', {
            'fields': ('shop',)
        }),
        ('Geographic Coordinates', {
            'fields': ('longitude', 'latitude', 'accuracy_radius')
        }),
        ('Location Details', {
            'fields': ('location_name', 'address_description')
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
        return super().get_queryset(request).select_related('shop__customer')
    
    def customer_name(self, obj):
        return obj.shop.customer.full_name
    customer_name.short_description = 'Customer Name'
    
    def shop_name(self, obj):
        return obj.shop.name
    shop_name.short_description = 'Shop Name'
