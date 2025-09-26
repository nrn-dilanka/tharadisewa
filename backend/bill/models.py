from django.db import models
from django.utils import timezone
from django.core.validators import MinValueValidator
from decimal import Decimal
import uuid

class Bill(models.Model):
    """
    Model to represent bills for services and purchases
    """
    
    # Primary key - UUID
    id = models.UUIDField(
        primary_key=True, 
        default=uuid.uuid4, 
        editable=False,
        help_text="Unique identifier for the bill"
    )
    
    # Date field
    date = models.DateTimeField(
        default=timezone.now,
        help_text="Date and time when the bill was created"
    )
    
    # Amount field
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))],
        help_text="Total bill amount"
    )
    
    # Service reference (Foreign Key)
    service = models.ForeignKey(
        'services.Service',
        on_delete=models.CASCADE,
        related_name='bills',
        help_text="Reference to the service this bill is for"
    )
    
    # Purchase reference (Foreign Key)
    purchase = models.ForeignKey(
        'purchase.Purchase',
        on_delete=models.CASCADE,
        related_name='bills',
        help_text="Reference to the purchase this bill is associated with"
    )
    
    # Additional fields for better bill management
    bill_number = models.CharField(
        max_length=20,
        unique=True,
        blank=True,
        help_text="Auto-generated bill number"
    )
    
    status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'Pending'),
            ('paid', 'Paid'),
            ('overdue', 'Overdue'),
            ('cancelled', 'Cancelled'),
        ],
        default='pending',
        help_text="Bill payment status"
    )
    
    due_date = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Due date for bill payment"
    )
    
    paid_date = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Date when bill was paid"
    )
    
    notes = models.TextField(
        blank=True,
        help_text="Additional notes about the bill"
    )
    
    # Tax and discount fields
    tax_rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0.00'))],
        help_text="Tax rate percentage (0-100)"
    )
    
    tax_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0.00'))],
        help_text="Calculated tax amount"
    )
    
    discount_rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0.00'))],
        help_text="Discount rate percentage (0-100)"
    )
    
    discount_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0.00'))],
        help_text="Calculated discount amount"
    )
    
    subtotal = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0.00'))],
        help_text="Subtotal before tax and discount"
    )
    
    # Timestamps
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="When the bill was created"
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="When the bill was last updated"
    )
    
    class Meta:
        ordering = ['-date', '-created_at']
        indexes = [
            models.Index(fields=['date']),
            models.Index(fields=['status']),
            models.Index(fields=['bill_number']),
            models.Index(fields=['service']),
            models.Index(fields=['purchase']),
            models.Index(fields=['due_date']),
        ]
        verbose_name = 'Bill'
        verbose_name_plural = 'Bills'
    
    def __str__(self):
        return f"Bill {self.bill_number} - ${self.amount}"
    
    def save(self, *args, **kwargs):
        """
        Override save to generate bill number and calculate amounts
        """
        # Generate bill number if not exists
        if not self.bill_number:
            self.bill_number = self.generate_bill_number()
        
        # Calculate tax amount
        if self.tax_rate > 0:
            self.tax_amount = (self.subtotal * self.tax_rate) / 100
        
        # Calculate discount amount  
        if self.discount_rate > 0:
            self.discount_amount = (self.subtotal * self.discount_rate) / 100
        
        # Calculate final amount
        self.amount = self.subtotal + self.tax_amount - self.discount_amount
        
        super().save(*args, **kwargs)
    
    def generate_bill_number(self):
        """
        Generate unique bill number
        """
        from datetime import datetime
        now = datetime.now()
        prefix = f"BILL{now.strftime('%Y%m')}"
        
        # Get the last bill number for this month
        last_bill = Bill.objects.filter(
            bill_number__startswith=prefix
        ).order_by('bill_number').last()
        
        if last_bill:
            try:
                last_number = int(last_bill.bill_number[-4:])
                new_number = last_number + 1
            except (ValueError, IndexError):
                new_number = 1
        else:
            new_number = 1
        
        return f"{prefix}{new_number:04d}"
    
    @property
    def bill_code(self):
        """
        Return bill number as code
        """
        return self.bill_number
    
    @property
    def customer(self):
        """
        Get customer from purchase
        """
        return self.purchase.customer if self.purchase else None
    
    @property
    def shop(self):
        """
        Get shop from purchase/service
        """
        if self.purchase and self.purchase.product:
            return self.purchase.product.shop
        elif self.service and self.service.product:
            return self.service.product.shop
        return None
    
    @property
    def is_overdue(self):
        """
        Check if bill is overdue
        """
        if self.due_date and self.status == 'pending':
            return timezone.now() > self.due_date
        return False
    
    @property
    def days_until_due(self):
        """
        Calculate days until due date
        """
        if self.due_date:
            delta = self.due_date - timezone.now()
            return delta.days
        return None
    
    @property
    def payment_method_display(self):
        """
        Display payment method if available
        """
        # This can be extended based on payment integration
        return "Cash" if self.status == 'paid' else "Pending"
    
    def mark_as_paid(self):
        """
        Mark bill as paid
        """
        self.status = 'paid'
        self.paid_date = timezone.now()
        self.save()
    
    def mark_as_overdue(self):
        """
        Mark bill as overdue
        """
        if self.is_overdue:
            self.status = 'overdue'
            self.save()
    
    def calculate_totals(self, subtotal=None):
        """
        Calculate all totals based on subtotal
        """
        if subtotal is not None:
            self.subtotal = Decimal(str(subtotal))
        
        # Calculate tax
        self.tax_amount = (self.subtotal * self.tax_rate) / 100
        
        # Calculate discount
        self.discount_amount = (self.subtotal * self.discount_rate) / 100
        
        # Calculate final amount
        self.amount = self.subtotal + self.tax_amount - self.discount_amount
        
        return {
            'subtotal': self.subtotal,
            'tax_amount': self.tax_amount,
            'discount_amount': self.discount_amount,
            'total_amount': self.amount
        }
    
    def get_bill_summary(self):
        """
        Get formatted bill summary
        """
        return {
            'bill_number': self.bill_number,
            'date': self.date,
            'customer': self.customer.get_full_name() if self.customer else 'Unknown',
            'service_type': self.service.get_service_type_display() if self.service else 'N/A',
            'subtotal': self.subtotal,
            'tax_rate': self.tax_rate,
            'tax_amount': self.tax_amount,
            'discount_rate': self.discount_rate,
            'discount_amount': self.discount_amount,
            'total_amount': self.amount,
            'status': self.get_status_display(),
            'due_date': self.due_date,
            'is_overdue': self.is_overdue
        }
