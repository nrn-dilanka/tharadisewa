from django.db import models
from django.core.validators import MinValueValidator
from product.models import Product
from customer.models import Customer
from django.utils import timezone
import uuid

class Purchase(models.Model):
    """
    Purchase model with id, date, and product reference
    """
    
    # Auto-generated UUID as primary key
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        help_text="Auto-generated unique identifier for the purchase"
    )
    
    # Date field for purchase date
    date = models.DateTimeField(
        default=timezone.now,
        help_text="Purchase date and time"
    )
    
    # Product reference - Foreign Key to Product model
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='purchases',
        help_text="The product that was purchased"
    )
    
    # Additional useful fields
    customer = models.ForeignKey(
        Customer,
        on_delete=models.CASCADE,
        related_name='purchases',
        help_text="The customer who made the purchase"
    )
    
    quantity = models.PositiveIntegerField(
        default=1,
        validators=[MinValueValidator(1)],
        help_text="Quantity of products purchased"
    )
    
    unit_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Unit price at the time of purchase"
    )
    
    total_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        help_text="Total purchase amount (quantity × unit_price)"
    )
    
    payment_status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'Pending'),
            ('completed', 'Completed'),
            ('failed', 'Failed'),
            ('refunded', 'Refunded'),
        ],
        default='pending',
        help_text="Payment status of the purchase"
    )
    
    purchase_method = models.CharField(
        max_length=20,
        choices=[
            ('cash', 'Cash'),
            ('card', 'Card'),
            ('bank_transfer', 'Bank Transfer'),
            ('mobile_payment', 'Mobile Payment'),
            ('credit', 'Credit'),
        ],
        default='cash',
        help_text="Method of payment"
    )
    
    notes = models.TextField(
        blank=True,
        null=True,
        help_text="Additional notes about the purchase"
    )
    
    is_active = models.BooleanField(
        default=True,
        help_text="Whether the purchase record is active"
    )
    
    # Auto timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-date', '-created_at']
        verbose_name = "Purchase"
        verbose_name_plural = "Purchases"
        indexes = [
            models.Index(fields=['date']),
            models.Index(fields=['customer', 'date']),
            models.Index(fields=['product', 'date']),
            models.Index(fields=['payment_status']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"Purchase {str(self.id)[:8]} - {self.product.name} by {self.customer.get_full_name()}"
    
    def save(self, *args, **kwargs):
        """
        Override save method to calculate total amount
        """
        # Calculate total amount if not provided
        if not self.total_amount:
            self.total_amount = self.quantity * self.unit_price
        
        super().save(*args, **kwargs)
    
    @property
    def purchase_code(self):
        """
        Generate a human-readable purchase code
        """
        return f"PUR-{str(self.id)[:8].upper()}"
    
    @property
    def shop_info(self):
        """
        Get shop information through product
        """
        if self.product and self.product.shop:
            return {
                'shop_id': self.product.shop.id,
                'shop_name': self.product.shop.name,
                'shop_address': self.product.shop.full_address,
            }
        return None
    
    @property
    def customer_info(self):
        """
        Get customer information
        """
        return {
            'customer_id': self.customer.id,
            'customer_name': self.customer.get_full_name(),
            'customer_username': self.customer.username,
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
            'current_price': self.product.price,
        }
    
    @property
    def purchase_summary(self):
        """
        Get a complete purchase summary
        """
        return {
            'purchase_code': self.purchase_code,
            'date': self.date,
            'customer': self.customer_info,
            'product': self.product_info,
            'shop': self.shop_info,
            'quantity': self.quantity,
            'unit_price': self.unit_price,
            'total_amount': self.total_amount,
            'payment_status': self.payment_status,
            'payment_method': self.purchase_method,
        }
    
    def get_absolute_url(self):
        """
        Get the absolute URL for this purchase
        """
        return f"/api/purchases/{self.id}/"
