from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import RegexValidator


class User(AbstractUser):
    """
    Custom User model with additional fields
    """
    # Override first_name and last_name to make them required
    first_name = models.CharField(
        max_length=30,
        help_text="First name"
    )
    
    last_name = models.CharField(
        max_length=30,
        help_text="Last name"
    )
    
    # Role field with choices
    ROLE_CHOICES = [
        ('admin', 'Administrator'),
        ('manager', 'Manager'),
        ('staff', 'Staff'),
        ('customer', 'Customer'),
        ('technician', 'Technician'),
        ('sales', 'Sales Representative'),
        ('support', 'Support Staff'),
        ('owner', 'Business Owner'),
    ]
    
    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default='customer',
        help_text="User role"
    )
    
    # Phone number with validation
    phone_number_validator = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message="Phone number must be in format: '+94771234567' or '0771234567'"
    )
    phone_number = models.CharField(
        max_length=17,
        validators=[phone_number_validator],
        blank=True,
        help_text="Phone number"
    )
    
    # Email field (inherited from AbstractUser but make it required and unique)
    email = models.EmailField(
        unique=True,
        help_text="Email address"
    )
    
    # Additional fields
    is_verified = models.BooleanField(
        default=False,
        help_text="Whether the user is verified"
    )
    
    profile_image = models.ImageField(
        upload_to='user_profiles/',
        blank=True,
        null=True,
        help_text="Profile image"
    )
    
    date_of_birth = models.DateField(
        blank=True,
        null=True,
        help_text="Date of birth"
    )
    
    address = models.TextField(
        blank=True,
        help_text="Address"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Use username as the username field (default)
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email', 'first_name', 'last_name']
    
    class Meta:
        db_table = 'users'
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.get_full_name()} ({self.username}) - {self.get_role_display()}"
    
    def get_full_name(self):
        """
        Return the first_name plus the last_name, with a space in between.
        """
        full_name = f"{self.first_name} {self.last_name}"
        return full_name.strip()
    
    def get_short_name(self):
        """
        Return the short name for the user.
        """
        return self.first_name
    
    @property
    def full_name(self):
        """Property to get full name"""
        return self.get_full_name()
    
    def is_admin(self):
        """Check if user is admin"""
        return self.role == 'admin'
    
    def is_manager(self):
        """Check if user is manager"""
        return self.role == 'manager'
    
    def is_staff_member(self):
        """Check if user is staff (any staff role)"""
        return self.role in ['admin', 'manager', 'staff', 'technician', 'sales', 'support']
    
    def is_customer_user(self):
        """Check if user is customer"""
        return self.role == 'customer'
    
    def has_permission(self, permission):
        """
        Check if user has specific permission based on role
        """
        admin_permissions = [
            'view_all', 'create_all', 'edit_all', 'delete_all',
            'manage_users', 'manage_settings', 'view_reports'
        ]
        
        manager_permissions = [
            'view_all', 'create_all', 'edit_all', 'view_reports',
            'manage_staff'
        ]
        
        staff_permissions = [
            'view_customers', 'create_customers', 'edit_customers',
            'view_products', 'create_products', 'edit_products',
            'view_orders', 'create_orders', 'edit_orders'
        ]
        
        customer_permissions = [
            'view_own_profile', 'edit_own_profile', 'view_own_orders'
        ]
        
        if self.role == 'admin':
            return permission in admin_permissions
        elif self.role == 'manager':
            return permission in manager_permissions
        elif self.role in ['staff', 'technician', 'sales', 'support']:
            return permission in staff_permissions
        elif self.role == 'customer':
            return permission in customer_permissions
        
        return False
    
    def get_dashboard_url(self):
        """
        Get appropriate dashboard URL based on role
        """
        role_dashboards = {
            'admin': '/admin-dashboard/',
            'manager': '/manager-dashboard/',
            'staff': '/staff-dashboard/',
            'technician': '/technician-dashboard/',
            'sales': '/sales-dashboard/',
            'support': '/support-dashboard/',
            'customer': '/customer-dashboard/',
            'owner': '/owner-dashboard/',
        }
        return role_dashboards.get(self.role, '/dashboard/')
    
    def get_permissions_list(self):
        """
        Get list of permissions for this user based on role
        """
        if self.role == 'admin':
            return [
                'view_all', 'create_all', 'edit_all', 'delete_all',
                'manage_users', 'manage_settings', 'view_reports'
            ]
        elif self.role == 'manager':
            return [
                'view_all', 'create_all', 'edit_all', 'view_reports',
                'manage_staff'
            ]
        elif self.role in ['staff', 'technician', 'sales', 'support']:
            return [
                'view_customers', 'create_customers', 'edit_customers',
                'view_products', 'create_products', 'edit_products',
                'view_orders', 'create_orders', 'edit_orders'
            ]
        elif self.role == 'customer':
            return [
                'view_own_profile', 'edit_own_profile', 'view_own_orders'
            ]
        return []
