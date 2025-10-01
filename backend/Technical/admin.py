from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.db.models import Count
from django.utils import timezone
from datetime import timedelta
from .models import TechnicalModel

@admin.register(TechnicalModel)
class TechnicalModelAdmin(admin.ModelAdmin):
    """
    Admin interface for TechnicalModel
    """
    
    list_display = [
        'brand',
        'model',
        'model_code_display',
        'product_link',
        'year_released',
        'status_colored',
        'specification_count',
        'created_at'
    ]
    
    list_filter = [
        'brand',
        'year_released',
        'country_of_origin',
        'manufacturer',
        'is_active',
        'is_discontinued',
        'created_at'
    ]
    
    search_fields = [
        'brand',
        'model',
        'model_number',
        'series',
        'manufacturer',
        'country_of_origin',
        'product__name',
        'notes'
    ]
    
    readonly_fields = [
        'id',
        'full_model_name',
        'model_code',
        'product_name',
        'product_info_display',
        'specifications_display',
        'technical_summary_display',
        'created_at',
        'updated_at'
    ]
    
    fieldsets = (
        ('Basic Information', {
            'fields': (
                'id',
                'product',
                'product_info_display',
                'brand',
                'model',
                'full_model_name',
                'model_code'
            )
        }),
        ('Technical Details', {
            'fields': (
                'model_number',
                'series',
                'year_released',
                'country_of_origin',
                'manufacturer'
            )
        }),
        ('Status', {
            'fields': (
                'is_active',
                'is_discontinued',
                'notes'
            )
        }),
        ('Specifications', {
            'fields': (
                'specifications',
                'specifications_display'
            ),
            'classes': ('collapse',)
        }),
        ('Summary', {
            'fields': (
                'technical_summary_display',
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
    
    ordering = ['brand', 'model']
    list_per_page = 25
    date_hierarchy = 'created_at'
    
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
    
    def model_code_display(self, obj):
        """
        Display model code with styling
        """
        return format_html(
            '<code style="background: #f8f9fa; padding: 2px 4px; border-radius: 3px;">{}</code>',
            obj.model_code
        )
    model_code_display.short_description = 'Model Code'
    
    def status_colored(self, obj):
        """
        Display status with colors
        """
        if obj.is_discontinued:
            return format_html(
                '<span style="color: #dc3545; font-weight: bold;">⚠ Discontinued</span>'
            )
        elif obj.is_active:
            return format_html(
                '<span style="color: #28a745; font-weight: bold;">✓ Active</span>'
            )
        else:
            return format_html(
                '<span style="color: #ffc107; font-weight: bold;">⏸ Inactive</span>'
            )
    status_colored.short_description = 'Status'
    
    def specification_count(self, obj):
        """
        Display count of specifications
        """
        if obj.specifications:
            count = len(obj.specifications)
            if count > 0:
                return format_html(
                    '<span style="color: #17a2b8;">{} specs</span>',
                    count
                )
        return format_html('<span style="color: #6c757d;">No specs</span>')
    specification_count.short_description = 'Specifications'
    
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
    
    def specifications_display(self, obj):
        """
        Display formatted specifications
        """
        if obj.specifications:
            specs_html = []
            for key, value in obj.get_all_specifications().items():
                specs_html.append(f'<strong>{key}:</strong> {value}')
            
            if specs_html:
                return format_html('<br>'.join(specs_html))
        
        return 'No specifications available'
    specifications_display.short_description = 'Specifications Details'
    
    def technical_summary_display(self, obj):
        """
        Display formatted technical summary
        """
        return format_html(
            '<strong>Brand:</strong> {}<br>'
            '<strong>Model:</strong> {}<br>'
            '<strong>Full Name:</strong> {}<br>'
            '<strong>Code:</strong> {}<br>'
            '<strong>Model Number:</strong> {}<br>'
            '<strong>Series:</strong> {}<br>'
            '<strong>Year:</strong> {}<br>'
            '<strong>Origin:</strong> {}<br>'
            '<strong>Manufacturer:</strong> {}<br>'
            '<strong>Status:</strong> {}',
            obj.brand,
            obj.model,
            obj.full_model_name,
            obj.model_code,
            obj.model_number or 'Not specified',
            obj.series or 'Not specified',
            obj.year_released or 'Not specified',
            obj.country_of_origin or 'Not specified',
            obj.manufacturer or 'Not specified',
            'Active' if obj.is_active else ('Discontinued' if obj.is_discontinued else 'Inactive')
        )
    technical_summary_display.short_description = 'Technical Summary'
    
    actions = [
        'mark_as_active',
        'mark_as_discontinued',
        'reactivate_models',
        'clear_specifications_action'
    ]
    
    def mark_as_active(self, request, queryset):
        """
        Mark selected technical models as active
        """
        updated = queryset.update(is_active=True, is_discontinued=False)
        self.message_user(request, f'{updated} technical models marked as active.')
    mark_as_active.short_description = 'Mark as active'
    
    def mark_as_discontinued(self, request, queryset):
        """
        Mark selected technical models as discontinued
        """
        updated = 0
        for model in queryset:
            if not model.is_discontinued:
                model.mark_as_discontinued()
                updated += 1
        self.message_user(request, f'{updated} technical models marked as discontinued.')
    mark_as_discontinued.short_description = 'Mark as discontinued'
    
    def reactivate_models(self, request, queryset):
        """
        Reactivate selected technical models
        """
        updated = 0
        for model in queryset:
            if model.is_discontinued or not model.is_active:
                model.reactivate()
                updated += 1
        self.message_user(request, f'{updated} technical models reactivated.')
    reactivate_models.short_description = 'Reactivate models'
    
    def clear_specifications_action(self, request, queryset):
        """
        Clear specifications for selected technical models
        """
        updated = 0
        for model in queryset:
            if model.specifications:
                model.clear_specifications()
                updated += 1
        self.message_user(request, f'Specifications cleared for {updated} technical models.')
    clear_specifications_action.short_description = 'Clear specifications'
    
    def get_queryset(self, request):
        """
        Optimize queryset with select_related
        """
        return super().get_queryset(request).select_related(
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
            'total_models': queryset.count(),
            'active_models': queryset.filter(is_active=True).count(),
            'discontinued_models': queryset.filter(is_discontinued=True).count(),
            'total_brands': queryset.values('brand').distinct().count(),
            'models_with_specs': queryset.exclude(specifications__exact={}).count(),
            'recent_models': queryset.filter(
                created_at__gte=timezone.now() - timedelta(days=30)
            ).count() if queryset.exists() else 0,
        }
        
        # Brand distribution
        brand_stats = (
            queryset.values('brand')
            .annotate(count=Count('id'))
            .order_by('-count')[:5]  # Top 5 brands
        )
        stats['top_brands'] = list(brand_stats)
        
        extra_context['summary_stats'] = stats
        
        return super().changelist_view(request, extra_context=extra_context)
