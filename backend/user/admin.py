from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html
from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """
    Admin configuration for User model
    """
    list_display = [
        'username', 'email', 'get_full_name', 'role_badge', 'phone_number',
        'is_verified', 'is_active', 'is_staff', 'date_joined'
    ]
    
    list_filter = [
        'role', 'is_active', 'is_staff', 'is_superuser', 'is_verified',
        'date_joined', 'last_login'
    ]
    
    search_fields = [
        'username', 'email', 'first_name', 'last_name', 'phone_number'
    ]
    
    ordering = ['-date_joined']
    
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {
            'fields': ('first_name', 'last_name', 'email', 'phone_number', 
                      'date_of_birth', 'address', 'profile_image')
        }),
        ('Role & Permissions', {
            'fields': ('role', 'is_active', 'is_staff', 'is_superuser', 
                      'is_verified', 'groups', 'user_permissions')
        }),
        ('Important dates', {
            'fields': ('last_login', 'date_joined', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'first_name', 'last_name', 
                      'phone_number', 'role', 'password1', 'password2'),
        }),
    )
    
    readonly_fields = ['date_joined', 'last_login', 'created_at', 'updated_at']
    
    def role_badge(self, obj):
        """Display role with color coding"""
        colors = {
            'admin': 'red',
            'manager': 'purple',
            'staff': 'blue',
            'customer': 'green',
            'technician': 'orange',
            'sales': 'teal',
            'support': 'brown',
            'owner': 'darkred'
        }
        color = colors.get(obj.role, 'gray')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color, obj.get_role_display()
        )
    role_badge.short_description = 'Role'
    role_badge.admin_order_field = 'role'
