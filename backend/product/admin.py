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
        'shop_link',
        'customer_name',
        'price',
        'stock_quantity',
        'is_active',
        'qr_code_preview',
        'created_at'
    ]
    
    list_filter = [
        'is_active',
        'shop',
        'shop__customer',
        'created_at',
        'updated_at'
    ]
    
    search_fields = [
        'name',
        'description',
        'sku',
        'shop__name',
        'shop__customer__username',
        'shop__customer__first_name',
        'shop__customer__last_name'
    ]
    
    readonly_fields = [
        'id',
        'product_code',
        'qr_code_preview',
        'qr_code_url',
        'shop_info',
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
        ('Shop & Customer', {
            'fields': (
                'shop',
                'shop_info'
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
    
    def shop_link(self, obj):
        """
        Display shop name as a link to shop admin
        """
        if obj.shop:
            url = reverse('admin:shop_shop_change', args=[obj.shop.id])
            return format_html('<a href="{}">{}</a>', url, obj.shop.name)
        return '-'
    shop_link.short_description = 'Shop'
    shop_link.admin_order_field = 'shop__name'
    
    def customer_name(self, obj):
        """
        Display customer name
        """
        if obj.shop and obj.shop.customer:
            return obj.shop.customer.get_full_name()
        return '-'
    customer_name.short_description = 'Customer'
    customer_name.admin_order_field = 'shop__customer__first_name'
    
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
    
    def shop_info(self, obj):
        """
        Display formatted shop information
        """
        if obj.shop:
            return format_html(
                '<strong>Shop:</strong> {}<br>'
                '<strong>Customer:</strong> {}<br>'
                '<strong>Address:</strong> {}',
                obj.shop.name,
                obj.shop.customer.get_full_name(),
                obj.shop.full_address
            )
        return 'No shop assigned'
    shop_info.short_description = 'Shop Information'
    
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
    
    def get_queryset(self, request):
        """
        Optimize queryset with select_related
        """
        return super().get_queryset(request).select_related(
            'shop',
            'shop__customer'
        )
