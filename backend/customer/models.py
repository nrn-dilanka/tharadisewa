from django.db import models
from django.core.validators import RegexValidator


class Customer(models.Model):
    """
    Customer model with customer-specific information
    """
    
    # NIC field with validation for Sri Lankan NIC format
    nic_validator = RegexValidator(
        regex=r'^(?:\d{9}[vVxX]|\d{12})$',
        message="NIC must be in format: 123456789V or 123456789012"
    )
    nic = models.CharField(
        max_length=12,
        unique=True,
        validators=[nic_validator],
        help_text="National Identity Card number"
    )
    
    # Custom ID field (separate from Django's auto ID)
    customer_id = models.CharField(
        max_length=20,
        unique=True,
        blank=True,
        help_text="Custom customer ID"
    )
    
    # Customer basic information
    first_name = models.CharField(
        max_length=30,
        help_text="First name"
    )
    
    last_name = models.CharField(
        max_length=30,
        help_text="Last name"
    )
    
    # Email field
    email = models.EmailField(
        unique=True,
        help_text="Email address"
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
    
    # Optional user reference for authentication
    user = models.OneToOneField(
        'user.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='customer_profile',
        help_text="Associated user account"
    )
    
    # Additional customer fields
    date_of_birth = models.DateField(
        blank=True,
        null=True,
        help_text="Date of birth"
    )
    
    address = models.TextField(
        blank=True,
        help_text="Customer address"
    )
    
    is_verified = models.BooleanField(
        default=False,
        help_text="Whether the customer is verified"
    )
    
    is_active = models.BooleanField(
        default=True,
        help_text="Whether the customer is active"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'customers'
        verbose_name = 'Customer'
        verbose_name_plural = 'Customers'
    
    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.customer_id})"
    
    def save(self, *args, **kwargs):
        # Auto-generate customer_id if not provided
        if not self.customer_id:
            # Get the last customer ID and increment
            last_customer = Customer.objects.filter(
                customer_id__startswith='CUST'
            ).order_by('customer_id').last()
            
            if last_customer:
                last_id = int(last_customer.customer_id[4:])
                new_id = last_id + 1
            else:
                new_id = 1
                
            self.customer_id = f"CUST{new_id:06d}"  # Format: CUST000001
            
        super().save(*args, **kwargs)
    
    def get_full_name(self):
        """
        Return the first_name plus the last_name, with a space in between.
        """
        full_name = f"{self.first_name} {self.last_name}"
        return full_name.strip()
    
    @property
    def full_name(self):
        return self.get_full_name()
    
    @property
    def has_user_account(self):
        """Check if customer has an associated user account"""
        return self.user is not None
    
    def create_user_account(self, username, password, role='customer'):
        """
        Create a user account for this customer
        """
        from user.models import User
        
        if self.user:
            return self.user
        
        user = User.objects.create_user(
            username=username,
            email=self.email,
            first_name=self.first_name,
            last_name=self.last_name,
            phone_number=self.phone_number,
            role=role,
            password=password
        )
        
        self.user = user
        self.save()
        
        return user
