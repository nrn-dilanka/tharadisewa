from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from .models import Customer


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    """
    Admin interface for Customer model
    """
    list_display = (
        'customer_id', 'full_name', 'email', 'phone_number', 'nic',
        'is_verified', 'is_active', 'has_user_account_badge', 'created_at'
    )
    list_filter = (
        'is_active', 'is_verified', 'created_at', 'updated_at'
    )
    search_fields = (
        'customer_id', 'first_name', 'last_name', 'email', 'nic', 'phone_number'
    )
    ordering = ('-created_at',)
    
    fieldsets = (
        ('Basic Information', {
            'fields': (
                'customer_id', 'first_name', 'last_name', 'email', 
                'phone_number', 'nic'
            )
        }),
        ('Personal Details', {
            'fields': ('date_of_birth', 'address')
        }),
        ('Status', {
            'fields': ('is_verified', 'is_active')
        }),
        ('User Account', {
            'fields': ('user', 'user_info'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ('customer_id', 'created_at', 'updated_at', 'user_info')
    
    def has_user_account_badge(self, obj):
        """Display user account status with badge"""
        if obj.has_user_account:
            user_url = reverse('admin:user_user_change', args=[obj.user.id])
            return format_html(
                '<a href="{}" style="color: green; font-weight: bold;">✓ Has Account</a>',
                user_url
            )
        else:
            return format_html('<span style="color: red;">✗ No Account</span>')
    has_user_account_badge.short_description = 'User Account'
    
    def user_info(self, obj):
        """Display user account information"""
        if obj.user:
            user_url = reverse('admin:user_user_change', args=[obj.user.id])
            return format_html(
                '<strong>Username:</strong> <a href="{}">{}</a><br>'
                '<strong>Role:</strong> {}<br>'
                '<strong>Active:</strong> {}<br>'
                '<strong>Verified:</strong> {}',
                user_url, obj.user.username,
                obj.user.get_role_display(),
                'Yes' if obj.user.is_active else 'No',
                'Yes' if obj.user.is_verified else 'No'
            )
        return 'No user account linked'
    user_info.short_description = 'User Account Info'
    
    actions = ['verify_customers', 'unverify_customers', 'activate_customers', 'deactivate_customers']
    
    def verify_customers(self, request, queryset):
        """Verify selected customers"""
        count = queryset.update(is_verified=True)
        self.message_user(request, f'{count} customers were verified.')
    verify_customers.short_description = 'Verify selected customers'
    
    def unverify_customers(self, request, queryset):
        """Unverify selected customers"""
        count = queryset.update(is_verified=False)
        self.message_user(request, f'{count} customers were unverified.')
    unverify_customers.short_description = 'Unverify selected customers'
    
    def activate_customers(self, request, queryset):
        """Activate selected customers"""
        count = queryset.update(is_active=True)
        self.message_user(request, f'{count} customers were activated.')
    activate_customers.short_description = 'Activate selected customers'
    
    def deactivate_customers(self, request, queryset):
        """Deactivate selected customers"""
        count = queryset.update(is_active=False)
        self.message_user(request, f'{count} customers were deactivated.')
    deactivate_customers.short_description = 'Deactivate selected customers'
