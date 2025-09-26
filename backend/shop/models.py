from django.db import models
from django.core.validators import RegexValidator
from customer.models import Customer


class Shop(models.Model):
    """
    Shop Model with address and customer relation
    """
    # Basic shop information
    name = models.CharField(
        max_length=255,
        help_text="Shop name"
    )
    
    # Postal code with validation
    postal_code_validator = RegexValidator(
        regex=r'^\d{5}$',
        message="Postal code must be 5 digits"
    )
    postal_code = models.CharField(
        max_length=5,
        validators=[postal_code_validator],
        help_text="5-digit postal code"
    )
    
    # Address components
    address_line_1 = models.CharField(
        max_length=255,
        help_text="Address line 1 (Street address, building number)"
    )
    
    address_line_2 = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text="Address line 2 (Apartment, suite, etc.)"
    )
    
    address_line_3 = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text="Address line 3 (Additional address information)"
    )
    
    # City
    city = models.CharField(
        max_length=100,
        help_text="City name"
    )
    
    # Customer relation
    customer = models.ForeignKey(
        Customer,
        on_delete=models.CASCADE,
        related_name='shops',
        help_text="Customer who owns this shop"
    )
    
    # Additional fields
    is_active = models.BooleanField(
        default=True,
        help_text="Is the shop active?"
    )
    
    phone_number = models.CharField(
        max_length=15,
        blank=True,
        null=True,
        help_text="Shop phone number"
    )
    
    email = models.EmailField(
        blank=True,
        null=True,
        help_text="Shop email address"
    )
    
    description = models.TextField(
        blank=True,
        null=True,
        help_text="Shop description"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'shops'
        verbose_name = 'Shop'
        verbose_name_plural = 'Shops'
        ordering = ['-created_at']
        
        # Unique constraint to prevent duplicate shop names for the same customer
        constraints = [
            models.UniqueConstraint(
                fields=['customer', 'name'],
                name='unique_customer_shop_name'
            ),
        ]
    
    def __str__(self):
        return f"{self.name} - {self.customer.full_name}"
    
    @property
    def full_address(self):
        """Return complete formatted address"""
        address_parts = [self.address_line_1]
        
        if self.address_line_2:
            address_parts.append(self.address_line_2)
        if self.address_line_3:
            address_parts.append(self.address_line_3)
            
        address_parts.extend([self.city, self.postal_code])
        
        return ", ".join(address_parts)
    
    @property
    def address_dict(self):
        """Return address as dictionary"""
        return {
            'line_1': self.address_line_1,
            'line_2': self.address_line_2,
            'line_3': self.address_line_3,
            'city': self.city,
            'postal_code': self.postal_code,
            'full_address': self.full_address
        }
    
    @property
    def location_count(self):
        """Count of associated customer locations"""
        return self.customer_locations.filter(is_active=True).count()
