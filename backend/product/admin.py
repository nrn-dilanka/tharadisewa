from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import Product

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    """
    Admin interface for Product model
    """
    
    list_display = [
        'product_code',
        'name',
        'price',
        'stock_quantity',
        'is_active',
        'qr_code_preview',
        'created_at'
    ]
    
    list_filter = [
        'is_active',
        'created_at',
        'updated_at'
    ]
    
    search_fields = [
        'name',
        'description',
        'sku'
    ]
    
    readonly_fields = [
        'id',
        'product_code',
        'qr_code_preview',
        'qr_code_url',
        'created_at',
        'updated_at'
    ]
    
    fieldsets = (
        ('Basic Information', {
            'fields': (
                'id',
                'product_code',
                'name',
                'description'
            )
        }),
        ('Product Details', {
            'fields': (
                'price',
                'sku',
                'stock_quantity',
                'is_active'
            )
        }),
        ('QR Code', {
            'fields': (
                'qr_code',
                'qr_code_preview',
                'qr_code_url'
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
    
    ordering = ['-created_at', 'name']
    list_per_page = 25
    
    def qr_code_preview(self, obj):
        """
        Display QR code image preview
        """
        if obj.qr_code:
            return format_html(
                '<img src="{}" width="50" height="50" style="object-fit: contain;" />',
                obj.qr_code.url
            )
        return 'No QR Code'
    qr_code_preview.short_description = 'QR Code Preview'
    
    actions = ['activate_products', 'deactivate_products', 'regenerate_qr_codes']
    
    def activate_products(self, request, queryset):
        """
        Bulk activate selected products
        """
        updated = queryset.update(is_active=True)
        self.message_user(
            request,
            f'{updated} products were successfully activated.'
        )
    activate_products.short_description = 'Activate selected products'
    
    def deactivate_products(self, request, queryset):
        """
        Bulk deactivate selected products
        """
        updated = queryset.update(is_active=False)
        self.message_user(
            request,
            f'{updated} products were successfully deactivated.'
        )
    deactivate_products.short_description = 'Deactivate selected products'
    
    def regenerate_qr_codes(self, request, queryset):
        """
        Bulk regenerate QR codes for selected products
        """
        count = 0
        for product in queryset:
            try:
                product.regenerate_qr_code()
                count += 1
            except Exception:
                pass
        
        self.message_user(
            request,
            f'QR codes regenerated for {count} products.'
        )
    regenerate_qr_codes.short_description = 'Regenerate QR codes for selected products'
