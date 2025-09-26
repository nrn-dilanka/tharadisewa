from django.db import models
from django.utils import timezone
from django.core.validators import MinLengthValidator
from datetime import datetime, timedelta
import uuid

class License(models.Model):
    """
    Model to represent software/product licenses for purchased products
    """
    
    # Primary key - UUID
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        help_text="Unique identifier for the license"
    )
    
    # Issue date (in date)
    in_date = models.DateTimeField(
        default=timezone.now,
        help_text="Date when the license was issued"
    )
    
    # Expiry date (ex date)
    ex_date = models.DateTimeField(
        help_text="Date when the license expires"
    )
    
    # Purchase reference (Foreign Key)
    purchase = models.ForeignKey(
        'purchase.Purchase',
        on_delete=models.CASCADE,
        related_name='licenses',
        help_text="Reference to the purchase this license is for"
    )
    
    # Additional fields for comprehensive license management
    license_key = models.CharField(
        max_length=100,
        unique=True,
        blank=True,
        help_text="Auto-generated license key"
    )
    
    license_type = models.CharField(
        max_length=50,
        choices=[
            ('trial', 'Trial License'),
            ('standard', 'Standard License'),
            ('premium', 'Premium License'),
            ('enterprise', 'Enterprise License'),
            ('educational', 'Educational License'),
            ('commercial', 'Commercial License'),
            ('personal', 'Personal License'),
            ('developer', 'Developer License'),
        ],
        default='standard',
        help_text="Type of license"
    )
    
    status = models.CharField(
        max_length=20,
        choices=[
            ('active', 'Active'),
            ('expired', 'Expired'),
            ('suspended', 'Suspended'),
            ('revoked', 'Revoked'),
            ('pending', 'Pending Activation'),
        ],
        default='pending',
        help_text="Current status of the license"
    )
    
    license_number = models.CharField(
        max_length=30,
        unique=True,
        blank=True,
        help_text="Auto-generated license number"
    )
    
    # License details
    software_name = models.CharField(
        max_length=150,
        blank=True,
        help_text="Name of the software/product being licensed"
    )
    
    version = models.CharField(
        max_length=50,
        blank=True,
        help_text="Version of the software"
    )
    
    max_users = models.PositiveIntegerField(
        default=1,
        help_text="Maximum number of users allowed"
    )
    
    max_installations = models.PositiveIntegerField(
        default=1,
        help_text="Maximum number of installations allowed"
    )
    
    features_enabled = models.JSONField(
        default=list,
        blank=True,
        help_text="List of enabled features"
    )
    
    restrictions = models.JSONField(
        default=dict,
        blank=True,
        help_text="License restrictions and limitations"
    )
    
    # Activation and usage
    activated_date = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Date when the license was activated"
    )
    
    activation_count = models.PositiveIntegerField(
        default=0,
        help_text="Number of times license has been activated"
    )
    
    last_used_date = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Date when the license was last used"
    )
    
    usage_data = models.JSONField(
        default=dict,
        blank=True,
        help_text="Usage statistics and data"
    )
    
    # Support and maintenance
    support_expires = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Date when support expires"
    )
    
    maintenance_expires = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Date when maintenance expires"
    )
    
    auto_renewal = models.BooleanField(
        default=False,
        help_text="Whether license auto-renews"
    )
    
    renewal_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Price for license renewal"
    )
    
    # License holder information
    licensed_to = models.CharField(
        max_length=200,
        blank=True,
        help_text="Name of the license holder"
    )
    
    organization = models.CharField(
        max_length=200,
        blank=True,
        help_text="Organization name"
    )
    
    contact_email = models.EmailField(
        blank=True,
        help_text="Contact email for license holder"
    )
    
    # Notes and documentation
    notes = models.TextField(
        blank=True,
        help_text="Additional notes about the license"
    )
    
    terms_accepted = models.BooleanField(
        default=False,
        help_text="Whether license terms have been accepted"
    )
    
    terms_accepted_date = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Date when terms were accepted"
    )
    
    # Timestamps
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="When the license was created"
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="When the license was last updated"
    )
    
    class Meta:
        ordering = ['-in_date', '-created_at']
        indexes = [
            models.Index(fields=['in_date']),
            models.Index(fields=['ex_date']),
            models.Index(fields=['status']),
            models.Index(fields=['license_key']),
            models.Index(fields=['license_number']),
            models.Index(fields=['purchase']),
            models.Index(fields=['license_type']),
        ]
        verbose_name = 'License'
        verbose_name_plural = 'Licenses'
    
    def __str__(self):
        return f"License {self.license_number} - {self.software_name or 'Product'}"
    
    def save(self, *args, **kwargs):
        """
        Override save to generate license number and key
        """
        if not self.license_number:
            self.license_number = self.generate_license_number()
        
        if not self.license_key:
            self.license_key = self.generate_license_key()
        
        # Auto-populate software name from product if not set
        if not self.software_name and self.purchase and self.purchase.product:
            self.software_name = self.purchase.product.name
        
        # Auto-populate licensed_to from customer if not set
        if not self.licensed_to and self.purchase and self.purchase.customer:
            self.licensed_to = self.purchase.customer.get_full_name()
            self.contact_email = self.purchase.customer.email or ''
        
        super().save(*args, **kwargs)
    
    def generate_license_number(self):
        """
        Generate unique license number
        """
        from datetime import datetime
        now = datetime.now()
        prefix = f"LIC{now.strftime('%Y%m')}"
        
        # Get the last license number for this month
        last_license = License.objects.filter(
            license_number__startswith=prefix
        ).order_by('license_number').last()
        
        if last_license:
            try:
                last_number = int(last_license.license_number[-4:])
                new_number = last_number + 1
            except (ValueError, IndexError):
                new_number = 1
        else:
            new_number = 1
        
        return f"{prefix}{new_number:04d}"
    
    def generate_license_key(self):
        """
        Generate unique license key
        """
        import random
        import string
        
        # Generate a license key in format: XXXX-XXXX-XXXX-XXXX
        segments = []
        for _ in range(4):
            segment = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
            segments.append(segment)
        
        key = '-'.join(segments)
        
        # Ensure uniqueness
        while License.objects.filter(license_key=key).exists():
            segments = []
            for _ in range(4):
                segment = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
                segments.append(segment)
            key = '-'.join(segments)
        
        return key
    
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
    def is_expired(self):
        """
        Check if license is expired
        """
        return timezone.now() > self.ex_date
    
    @property
    def is_active(self):
        """
        Check if license is currently active
        """
        return self.status == 'active' and not self.is_expired
    
    @property
    def days_until_expiry(self):
        """
        Calculate days until expiry
        """
        if self.ex_date:
            delta = self.ex_date - timezone.now()
            return delta.days
        return None
    
    @property
    def days_since_issue(self):
        """
        Calculate days since issue
        """
        delta = timezone.now() - self.in_date
        return delta.days
    
    @property
    def license_duration(self):
        """
        Calculate total license duration in days
        """
        delta = self.ex_date - self.in_date
        return delta.days
    
    @property
    def is_expiring_soon(self):
        """
        Check if license is expiring within 30 days
        """
        days_left = self.days_until_expiry
        return days_left is not None and 0 <= days_left <= 30
    
    def activate(self):
        """
        Activate the license
        """
        self.status = 'active'
        self.activated_date = timezone.now()
        self.activation_count += 1
        if not self.terms_accepted:
            self.terms_accepted = True
            self.terms_accepted_date = timezone.now()
        self.save()
    
    def suspend(self):
        """
        Suspend the license
        """
        self.status = 'suspended'
        self.save()
    
    def revoke(self):
        """
        Revoke the license
        """
        self.status = 'revoked'
        self.save()
    
    def renew(self, new_expiry_date):
        """
        Renew the license with new expiry date
        """
        self.ex_date = new_expiry_date
        if self.status in ['expired', 'suspended']:
            self.status = 'active'
        self.save()
    
    def extend_license(self, days):
        """
        Extend license by specified number of days
        """
        self.ex_date += timedelta(days=days)
        self.save()
    
    def update_usage(self, usage_info):
        """
        Update usage data
        """
        if not isinstance(self.usage_data, dict):
            self.usage_data = {}
        
        self.usage_data.update(usage_info)
        self.last_used_date = timezone.now()
        self.save()
    
    def add_feature(self, feature_name):
        """
        Add a feature to the license
        """
        if not isinstance(self.features_enabled, list):
            self.features_enabled = []
        
        if feature_name not in self.features_enabled:
            self.features_enabled.append(feature_name)
            self.save()
    
    def remove_feature(self, feature_name):
        """
        Remove a feature from the license
        """
        if isinstance(self.features_enabled, list) and feature_name in self.features_enabled:
            self.features_enabled.remove(feature_name)
            self.save()
    
    def get_license_summary(self):
        """
        Get formatted license summary
        """
        return {
            'license_number': self.license_number,
            'license_key': self.license_key,
            'software_name': self.software_name,
            'version': self.version,
            'license_type': self.get_license_type_display(),
            'status': self.get_status_display(),
            'licensed_to': self.licensed_to,
            'organization': self.organization,
            'issue_date': self.in_date,
            'expiry_date': self.ex_date,
            'days_until_expiry': self.days_until_expiry,
            'is_active': self.is_active,
            'is_expired': self.is_expired,
            'is_expiring_soon': self.is_expiring_soon,
            'max_users': self.max_users,
            'max_installations': self.max_installations,
            'features_enabled': self.features_enabled,
            'activated_date': self.activated_date,
            'activation_count': self.activation_count,
            'last_used_date': self.last_used_date,
            'auto_renewal': self.auto_renewal,
            'customer': self.customer.get_full_name() if self.customer else None,
            'product': self.product.name if self.product else None,
            'shop': self.shop.name if self.shop else None
        }
    
    @classmethod
    def get_active_licenses(cls):
        """
        Get all active licenses
        """
        return cls.objects.filter(status='active', ex_date__gt=timezone.now())
    
    @classmethod
    def get_expired_licenses(cls):
        """
        Get all expired licenses
        """
        return cls.objects.filter(
            models.Q(status='expired') | models.Q(ex_date__lt=timezone.now())
        )
    
    @classmethod
    def get_expiring_soon(cls, days=30):
        """
        Get licenses expiring within specified days
        """
        cutoff_date = timezone.now() + timedelta(days=days)
        return cls.objects.filter(
            status='active',
            ex_date__lte=cutoff_date,
            ex_date__gt=timezone.now()
        )
    
    def check_and_update_status(self):
        """
        Check and update license status based on expiry
        """
        if self.is_expired and self.status == 'active':
            self.status = 'expired'
            self.save()
            return True
        return False
