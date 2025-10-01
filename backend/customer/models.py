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
        
        # Check if this is a new customer
        is_new = self.pk is None
        super().save(*args, **kwargs)
        
        # After saving, update primary contact email if it exists and email changed
        if not is_new:
            primary_contact = self.get_primary_contact()
            if primary_contact and primary_contact.email != self.email:
                primary_contact.email = self.email
                primary_contact.save()
    
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
    
    # Customer Contact Relations
    def get_contacts(self):
        """
        Get all contacts for this customer
        """
        return self.contacts.filter(is_active=True)
    
    def get_primary_contact(self):
        """
        Get the primary contact for this customer
        """
        return self.contacts.filter(is_primary=True, is_active=True).first()
    
    def add_contact(self, email, wa_number, tp_number, is_primary=False):
        """
        Add a new contact for this customer
        """
        from customer_contact.models import CustomerContact
        
        # If this will be primary, set others to non-primary
        if is_primary:
            self.contacts.filter(is_primary=True).update(is_primary=False)
        
        contact = CustomerContact.objects.create(
            customer=self,
            email=email,
            wa_number=wa_number,
            tp_number=tp_number,
            is_primary=is_primary
        )
        
        return contact
    
    def update_primary_contact(self, contact_id):
        """
        Set a specific contact as primary for this customer
        """
        # Set all contacts to non-primary
        self.contacts.all().update(is_primary=False)
        
        # Set the specified contact as primary
        contact = self.contacts.filter(id=contact_id).first()
        if contact:
            contact.is_primary = True
            contact.save()
            return contact
        return None
    
    def get_contact_summary(self):
        """
        Get a summary of all customer contacts
        """
        contacts = self.get_contacts()
        primary_contact = self.get_primary_contact()
        
        return {
            'total_contacts': contacts.count(),
            'primary_contact': {
                'email': primary_contact.email if primary_contact else None,
                'whatsapp': primary_contact.wa_number if primary_contact else None,
                'telephone': primary_contact.tp_number if primary_contact else None,
            } if primary_contact else None,
            'all_contacts': [contact.contact_info for contact in contacts],
        }
    
    @property
    def primary_email(self):
        """Get primary contact email, fallback to customer email"""
        primary_contact = self.get_primary_contact()
        return primary_contact.email if primary_contact else self.email
    
    @property
    def primary_whatsapp(self):
        """Get primary WhatsApp number"""
        primary_contact = self.get_primary_contact()
        return primary_contact.wa_number if primary_contact else None
    
    @property
    def primary_telephone(self):
        """Get primary telephone number, fallback to customer phone"""
        primary_contact = self.get_primary_contact()
        return primary_contact.tp_number if primary_contact else self.phone_number
