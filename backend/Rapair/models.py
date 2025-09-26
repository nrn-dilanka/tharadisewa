from django.db import models
from django.utils import timezone
from django.core.validators import MinLengthValidator
import uuid

class Repair(models.Model):
    """
    Model to represent repair records for purchased products
    """
    
    # Primary key - UUID
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        help_text="Unique identifier for the repair record"
    )
    
    # Date field
    date = models.DateTimeField(
        default=timezone.now,
        help_text="Date and time when the repair was initiated"
    )
    
    # Purchase reference (Foreign Key)
    purchase = models.ForeignKey(
        'purchase.Purchase',
        on_delete=models.CASCADE,
        related_name='repairs',
        help_text="Reference to the purchase this repair is for"
    )
    
    # Additional fields for comprehensive repair management
    repair_code = models.CharField(
        max_length=20,
        unique=True,
        blank=True,
        help_text="Auto-generated repair code"
    )
    
    repair_type = models.CharField(
        max_length=50,
        choices=[
            ('warranty', 'Warranty Repair'),
            ('paid', 'Paid Repair'),
            ('emergency', 'Emergency Repair'),
            ('maintenance', 'Preventive Maintenance'),
            ('replacement', 'Part Replacement'),
            ('diagnostic', 'Diagnostic Check'),
            ('software', 'Software Repair'),
            ('hardware', 'Hardware Repair'),
        ],
        default='warranty',
        help_text="Type of repair being performed"
    )
    
    status = models.CharField(
        max_length=20,
        choices=[
            ('requested', 'Repair Requested'),
            ('diagnosed', 'Diagnosed'),
            ('in_progress', 'In Progress'),
            ('waiting_parts', 'Waiting for Parts'),
            ('completed', 'Completed'),
            ('cancelled', 'Cancelled'),
            ('failed', 'Repair Failed'),
        ],
        default='requested',
        help_text="Current status of the repair"
    )
    
    priority = models.CharField(
        max_length=20,
        choices=[
            ('low', 'Low Priority'),
            ('normal', 'Normal Priority'),
            ('high', 'High Priority'),
            ('urgent', 'Urgent'),
        ],
        default='normal',
        help_text="Repair priority level"
    )
    
    problem_description = models.TextField(
        help_text="Description of the problem reported by customer"
    )
    
    diagnosis = models.TextField(
        blank=True,
        help_text="Technical diagnosis of the problem"
    )
    
    repair_notes = models.TextField(
        blank=True,
        help_text="Detailed notes about the repair process"
    )
    
    technician_name = models.CharField(
        max_length=100,
        blank=True,
        help_text="Name of the technician handling the repair"
    )
    
    estimated_cost = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Estimated repair cost"
    )
    
    actual_cost = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Actual repair cost"
    )
    
    parts_used = models.JSONField(
        default=list,
        blank=True,
        help_text="List of parts used in the repair"
    )
    
    # Date fields
    started_date = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When the repair work actually started"
    )
    
    completed_date = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When the repair was completed"
    )
    
    estimated_completion = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Estimated completion date"
    )
    
    # Warranty and quality
    is_under_warranty = models.BooleanField(
        default=False,
        help_text="Whether this repair is covered under warranty"
    )
    
    warranty_void = models.BooleanField(
        default=False,
        help_text="Whether this repair voids the product warranty"
    )
    
    quality_check_passed = models.BooleanField(
        default=False,
        help_text="Whether the repair passed quality check"
    )
    
    customer_satisfaction = models.IntegerField(
        choices=[(i, f"{i} Star{'s' if i != 1 else ''}") for i in range(1, 6)],
        null=True,
        blank=True,
        help_text="Customer satisfaction rating (1-5 stars)"
    )
    
    # Contact and delivery
    customer_contacted = models.BooleanField(
        default=False,
        help_text="Whether customer has been contacted about repair status"
    )
    
    ready_for_pickup = models.BooleanField(
        default=False,
        help_text="Whether the repaired item is ready for customer pickup"
    )
    
    delivered_date = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When the repaired item was delivered to customer"
    )
    
    # Timestamps
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="When the repair record was created"
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="When the repair record was last updated"
    )
    
    class Meta:
        ordering = ['-date', '-created_at']
        indexes = [
            models.Index(fields=['date']),
            models.Index(fields=['status']),
            models.Index(fields=['repair_code']),
            models.Index(fields=['purchase']),
            models.Index(fields=['repair_type']),
            models.Index(fields=['priority']),
            models.Index(fields=['completed_date']),
        ]
        verbose_name = 'Repair'
        verbose_name_plural = 'Repairs'
    
    def __str__(self):
        return f"Repair {self.repair_code} - {self.purchase.product.name if self.purchase else 'No Product'}"
    
    def save(self, *args, **kwargs):
        """
        Override save to generate repair code
        """
        if not self.repair_code:
            self.repair_code = self.generate_repair_code()
        super().save(*args, **kwargs)
    
    def generate_repair_code(self):
        """
        Generate unique repair code
        """
        from datetime import datetime
        now = datetime.now()
        prefix = f"RPR{now.strftime('%Y%m')}"
        
        # Get the last repair code for this month
        last_repair = Repair.objects.filter(
            repair_code__startswith=prefix
        ).order_by('repair_code').last()
        
        if last_repair:
            try:
                last_number = int(last_repair.repair_code[-4:])
                new_number = last_number + 1
            except (ValueError, IndexError):
                new_number = 1
        else:
            new_number = 1
        
        return f"{prefix}{new_number:04d}"
    
    @property
    def customer(self):
        """
        Get customer from purchase
        """
        return self.purchase.customer if self.purchase else None
    
    @property
    def product(self):
        """
        Get product from purchase
        """
        return self.purchase.product if self.purchase else None
    
    @property
    def shop(self):
        """
        Get shop from purchase
        """
        if self.purchase and self.purchase.product:
            return self.purchase.product.shop
        return None
    
    @property
    def is_overdue(self):
        """
        Check if repair is overdue based on estimated completion
        """
        if self.estimated_completion and self.status not in ['completed', 'cancelled']:
            return timezone.now() > self.estimated_completion
        return False
    
    @property
    def duration(self):
        """
        Calculate repair duration
        """
        if self.started_date and self.completed_date:
            return self.completed_date - self.started_date
        elif self.started_date:
            return timezone.now() - self.started_date
        return None
    
    @property
    def days_in_repair(self):
        """
        Calculate number of days in repair
        """
        duration = self.duration
        if duration:
            return duration.days
        return 0
    
    def mark_as_started(self):
        """
        Mark repair as started
        """
        if not self.started_date:
            self.started_date = timezone.now()
        self.status = 'in_progress'
        self.save()
    
    def mark_as_completed(self):
        """
        Mark repair as completed
        """
        self.status = 'completed'
        self.completed_date = timezone.now()
        self.ready_for_pickup = True
        self.save()
    
    def mark_as_delivered(self):
        """
        Mark repair as delivered to customer
        """
        self.delivered_date = timezone.now()
        self.save()
    
    def add_part_used(self, part_name, quantity=1, cost=None):
        """
        Add a part to the parts used list
        """
        if not isinstance(self.parts_used, list):
            self.parts_used = []
        
        part_entry = {
            'name': part_name,
            'quantity': quantity,
            'cost': float(cost) if cost else None,
            'added_date': timezone.now().isoformat()
        }
        
        self.parts_used.append(part_entry)
        self.save()
    
    def calculate_total_parts_cost(self):
        """
        Calculate total cost of parts used
        """
        if not self.parts_used:
            return 0
        
        total = 0
        for part in self.parts_used:
            if part.get('cost') and part.get('quantity'):
                total += float(part['cost']) * int(part['quantity'])
        
        return total
    
    def get_repair_summary(self):
        """
        Get formatted repair summary
        """
        return {
            'repair_code': self.repair_code,
            'date': self.date,
            'customer': self.customer.get_full_name() if self.customer else 'Unknown',
            'product': self.product.name if self.product else 'Unknown',
            'shop': self.shop.name if self.shop else 'Unknown',
            'repair_type': self.get_repair_type_display(),
            'status': self.get_status_display(),
            'priority': self.get_priority_display(),
            'problem_description': self.problem_description,
            'diagnosis': self.diagnosis,
            'technician': self.technician_name,
            'estimated_cost': self.estimated_cost,
            'actual_cost': self.actual_cost,
            'parts_cost': self.calculate_total_parts_cost(),
            'is_under_warranty': self.is_under_warranty,
            'started_date': self.started_date,
            'completed_date': self.completed_date,
            'estimated_completion': self.estimated_completion,
            'is_overdue': self.is_overdue,
            'days_in_repair': self.days_in_repair,
            'quality_check_passed': self.quality_check_passed,
            'customer_satisfaction': self.customer_satisfaction,
            'ready_for_pickup': self.ready_for_pickup
        }
    
    @classmethod
    def get_active_repairs(cls):
        """
        Get all active repairs (not completed or cancelled)
        """
        return cls.objects.filter(
            status__in=['requested', 'diagnosed', 'in_progress', 'waiting_parts']
        )
    
    @classmethod
    def get_overdue_repairs(cls):
        """
        Get all overdue repairs
        """
        return cls.objects.filter(
            estimated_completion__lt=timezone.now(),
            status__in=['requested', 'diagnosed', 'in_progress', 'waiting_parts']
        )
