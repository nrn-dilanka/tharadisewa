from django.db import models
from django.core.validators import MinValueValidator
from django.utils import timezone
from purchase.models import Purchase
from product.models import Product
from customer.models import Customer
import uuid

class Service(models.Model):
    """
    Service model with id, date, purchase reference, and product reference
    """
    
    # Auto-generated UUID as primary key
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        help_text="Auto-generated unique identifier for the service"
    )
    
    # Date field for service date
    date = models.DateTimeField(
        default=timezone.now,
        help_text="Service date and time"
    )
    
    # Purchase reference - Foreign Key to Purchase model
    purchase = models.ForeignKey(
        Purchase,
        on_delete=models.CASCADE,
        related_name='services',
        help_text="The purchase this service is related to"
    )
    
    # Product reference - Foreign Key to Product model
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='services',
        help_text="The product this service is for"
    )
    
    # Additional useful fields
    service_type = models.CharField(
        max_length=50,
        choices=[
            ('warranty', 'Warranty Service'),
            ('repair', 'Repair Service'),
            ('maintenance', 'Maintenance'),
            ('replacement', 'Replacement'),
            ('installation', 'Installation'),
            ('support', 'Technical Support'),
            ('consultation', 'Consultation'),
            ('training', 'Training'),
        ],
        default='warranty',
        help_text="Type of service provided"
    )
    
    description = models.TextField(
        help_text="Detailed description of the service provided"
    )
    
    status = models.CharField(
        max_length=20,
        choices=[
            ('requested', 'Requested'),
            ('in_progress', 'In Progress'),
            ('completed', 'Completed'),
            ('cancelled', 'Cancelled'),
            ('on_hold', 'On Hold'),
        ],
        default='requested',
        help_text="Current status of the service"
    )
    
    priority = models.CharField(
        max_length=10,
        choices=[
            ('low', 'Low'),
            ('medium', 'Medium'),
            ('high', 'High'),
            ('urgent', 'Urgent'),
        ],
        default='medium',
        help_text="Priority level of the service"
    )
    
    service_cost = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00,
        validators=[MinValueValidator(0)],
        help_text="Cost of the service"
    )
    
    technician_notes = models.TextField(
        blank=True,
        null=True,
        help_text="Notes from the technician"
    )
    
    customer_feedback = models.TextField(
        blank=True,
        null=True,
        help_text="Customer feedback about the service"
    )
    
    rating = models.IntegerField(
        blank=True,
        null=True,
        choices=[(i, str(i)) for i in range(1, 6)],
        help_text="Customer rating (1-5 stars)"
    )
    
    scheduled_date = models.DateTimeField(
        blank=True,
        null=True,
        help_text="Scheduled service date (if different from service date)"
    )
    
    completed_date = models.DateTimeField(
        blank=True,
        null=True,
        help_text="Date when service was completed"
    )
    
    warranty_expires = models.DateField(
        blank=True,
        null=True,
        help_text="Service warranty expiration date"
    )
    
    is_under_warranty = models.BooleanField(
        default=False,
        help_text="Whether the service is covered under warranty"
    )
    
    is_active = models.BooleanField(
        default=True,
        help_text="Whether the service record is active"
    )
    
    # Auto timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-date', '-created_at']
        verbose_name = "Service"
        verbose_name_plural = "Services"
        indexes = [
            models.Index(fields=['date']),
            models.Index(fields=['purchase', 'date']),
            models.Index(fields=['product', 'date']),
            models.Index(fields=['status']),
            models.Index(fields=['service_type']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"Service {str(self.id)[:8]} - {self.service_type} for {self.product.name}"
    
    def save(self, *args, **kwargs):
        """
        Override save method for additional logic
        """
        # Auto-set completed_date when status changes to completed
        if self.status == 'completed' and not self.completed_date:
            self.completed_date = timezone.now()
        
        # Clear completed_date if status is not completed
        if self.status != 'completed' and self.completed_date:
            self.completed_date = None
        
        super().save(*args, **kwargs)
    
    @property
    def service_code(self):
        """
        Generate a human-readable service code
        """
        return f"SRV-{str(self.id)[:8].upper()}"
    
    @property
    def customer(self):
        """
        Get customer through purchase
        """
        return self.purchase.customer if self.purchase else None
    
    @property
    def shop(self):
        """
        Get shop through product
        """
        return self.product.shop if self.product else None
    
    @property
    def customer_info(self):
        """
        Get customer information through purchase
        """
        if self.purchase and self.purchase.customer:
            customer = self.purchase.customer
            return {
                'customer_id': customer.id,
                'customer_name': customer.get_full_name(),
                'customer_username': customer.username,
            }
        return None
    
    @property
    def purchase_info(self):
        """
        Get purchase information
        """
        return {
            'purchase_id': str(self.purchase.id),
            'purchase_code': self.purchase.purchase_code,
            'purchase_date': self.purchase.date,
            'purchase_amount': self.purchase.total_amount,
        }
    
    @property
    def product_info(self):
        """
        Get product information
        """
        return {
            'product_id': str(self.product.id),
            'product_name': self.product.name,
            'product_code': self.product.product_code,
        }
    
    @property
    def shop_info(self):
        """
        Get shop information through product
        """
        if self.product and self.product.shop:
            shop = self.product.shop
            return {
                'shop_id': shop.id,
                'shop_name': shop.name,
                'shop_address': shop.full_address,
            }
        return None
    
    @property
    def service_summary(self):
        """
        Get a complete service summary
        """
        return {
            'service_code': self.service_code,
            'service_type': self.service_type,
            'status': self.status,
            'priority': self.priority,
            'date': self.date,
            'customer': self.customer_info,
            'purchase': self.purchase_info,
            'product': self.product_info,
            'shop': self.shop_info,
            'service_cost': self.service_cost,
            'is_under_warranty': self.is_under_warranty,
            'rating': self.rating,
        }
    
    @property
    def duration_since_purchase(self):
        """
        Calculate duration since the original purchase
        """
        if self.purchase and self.purchase.date:
            return self.date - self.purchase.date
        return None
    
    @property
    def is_overdue(self):
        """
        Check if scheduled service is overdue
        """
        if self.scheduled_date and self.status not in ['completed', 'cancelled']:
            return timezone.now() > self.scheduled_date
        return False
    
    def get_absolute_url(self):
        """
        Get the absolute URL for this service
        """
        return f"/api/services/{self.id}/"
    
    def clean(self):
        """
        Custom validation
        """
        from django.core.exceptions import ValidationError
        
        # Validate that purchase and product are related
        if self.purchase and self.product:
            if self.purchase.product != self.product:
                raise ValidationError("Product must be the same as the product in the purchase.")
        
        # Validate scheduled date
        if self.scheduled_date and self.scheduled_date < self.date:
            raise ValidationError("Scheduled date cannot be before service date.")
        
        # Validate rating
        if self.rating and (self.rating < 1 or self.rating > 5):
            raise ValidationError("Rating must be between 1 and 5.")
        
        super().clean()
