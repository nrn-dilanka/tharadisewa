from django.db import models
from django.core.validators import RegexValidator
from customer.models import Customer


class CustomerContact(models.Model):
    """
    Customer Contact Information Model
    """
    # Foreign key to Customer
    customer = models.ForeignKey(
        Customer,
        on_delete=models.CASCADE,
        related_name='contacts',
        help_text="Customer reference"
    )
    
    # Email field
    email = models.EmailField(
        max_length=254,
        help_text="Contact email address"
    )
    
    # WhatsApp number with validation
    wa_number_validator = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message="WhatsApp number must be in format: '+94771234567' or '0771234567'"
    )
    wa_number = models.CharField(
        max_length=17,
        validators=[wa_number_validator],
        help_text="WhatsApp number"
    )
    
    # Telephone number with validation
    tp_number_validator = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message="Telephone number must be in format: '+94112345678' or '0112345678'"
    )
    tp_number = models.CharField(
        max_length=17,
        validators=[tp_number_validator],
        help_text="Telephone number"
    )
    
    # Additional fields
    is_primary = models.BooleanField(
        default=False,
        help_text="Is this the primary contact?"
    )
    
    is_active = models.BooleanField(
        default=True,
        help_text="Is this contact active?"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'customer_contacts'
        verbose_name = 'Customer Contact'
        verbose_name_plural = 'Customer Contacts'
        ordering = ['-created_at']
        
        # Ensure unique combination of customer and contact type
        constraints = [
            models.UniqueConstraint(
                fields=['customer', 'email'],
                name='unique_customer_email'
            ),
            models.UniqueConstraint(
                fields=['customer', 'wa_number'],
                name='unique_customer_wa_number'
            ),
            models.UniqueConstraint(
                fields=['customer', 'tp_number'],
                name='unique_customer_tp_number'
            ),
        ]
    
    def __str__(self):
        return f"{self.customer.full_name} - {self.email}"
    
    def save(self, *args, **kwargs):
        # If this is set as primary, make sure no other contact for this customer is primary
        if self.is_primary:
            CustomerContact.objects.filter(
                customer=self.customer,
                is_primary=True
            ).exclude(pk=self.pk).update(is_primary=False)
        
        super().save(*args, **kwargs)
    
    @property
    def contact_info(self):
        """Return formatted contact information"""
        return {
            'email': self.email,
            'whatsapp': self.wa_number,
            'telephone': self.tp_number,
            'is_primary': self.is_primary
        }
