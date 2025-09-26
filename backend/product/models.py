from django.db import models
from django.core.validators import RegexValidator
from shop.models import Shop
import qrcode
from io import BytesIO
from django.core.files import File
from PIL import Image
import uuid

class Product(models.Model):
    """
    Product model with shop relation, name, and QR code functionality
    """
    
    # Auto-generated UUID as primary key
    id = models.UUIDField(
        primary_key=True, 
        default=uuid.uuid4, 
        editable=False,
        help_text="Auto-generated unique identifier for the product"
    )
    
    # Shop relation - Foreign Key to Shop model
    shop = models.ForeignKey(
        Shop,
        on_delete=models.CASCADE,
        related_name='products',
        help_text="The shop this product belongs to"
    )
    
    # Product name with validation
    name = models.CharField(
        max_length=255,
        help_text="Product name (max 255 characters)",
        validators=[
            RegexValidator(
                regex=r'^[a-zA-Z0-9\s\-_.()&]+$',
                message="Product name can only contain letters, numbers, spaces, hyphens, underscores, periods, parentheses, and ampersands"
            )
        ]
    )
    
    # QR Code field - stores the generated QR code image
    qr_code = models.ImageField(
        upload_to='product_qr_codes/',
        blank=True,
        null=True,
        help_text="Auto-generated QR code for the product"
    )
    
    # Additional useful fields
    description = models.TextField(
        blank=True,
        null=True,
        help_text="Product description"
    )
    
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True,
        help_text="Product price (optional)"
    )
    
    sku = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        help_text="Stock Keeping Unit (SKU) - optional"
    )
    
    is_active = models.BooleanField(
        default=True,
        help_text="Whether the product is active"
    )
    
    stock_quantity = models.IntegerField(
        default=0,
        help_text="Available stock quantity"
    )
    
    # Auto timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at', 'name']
        unique_together = ['shop', 'name']  # Unique product name per shop
        verbose_name = "Product"
        verbose_name_plural = "Products"
        indexes = [
            models.Index(fields=['shop', 'is_active']),
            models.Index(fields=['name']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"{self.name} - {self.shop.name}"
    
    def save(self, *args, **kwargs):
        """
        Override save method to generate QR code automatically
        """
        # Save the instance first to get the ID
        super().save(*args, **kwargs)
        
        # Generate QR code if it doesn't exist
        if not self.qr_code:
            self.generate_qr_code()
    
    def generate_qr_code(self):
        """
        Generate QR code for the product containing product information
        """
        try:
            # Create QR code data - can be customized based on requirements
            qr_data = {
                'product_id': str(self.id),
                'product_name': self.name,
                'shop_name': self.shop.name,
                'shop_id': self.shop.id,
            }
            
            # Convert to string format for QR code
            qr_string = f"PRODUCT_ID:{self.id}|NAME:{self.name}|SHOP:{self.shop.name}|SHOP_ID:{self.shop.id}"
            
            # Create QR code instance
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            
            # Add data to QR code
            qr.add_data(qr_string)
            qr.make(fit=True)
            
            # Create QR code image
            qr_image = qr.make_image(fill_color="black", back_color="white")
            
            # Convert PIL image to Django file
            buffer = BytesIO()
            qr_image.save(buffer, format='PNG')
            buffer.seek(0)
            
            # Create filename
            filename = f'product_{self.id}_qr.png'
            
            # Save to the qr_code field
            self.qr_code.save(
                filename,
                File(buffer),
                save=False
            )
            
            # Save the instance again to update the qr_code field
            super().save(update_fields=['qr_code'])
            
        except Exception as e:
            print(f"Error generating QR code for product {self.id}: {str(e)}")
    
    def regenerate_qr_code(self):
        """
        Regenerate QR code (useful if product details change)
        """
        # Delete existing QR code file
        if self.qr_code:
            self.qr_code.delete(save=False)
        
        # Generate new QR code
        self.generate_qr_code()
    
    @property
    def qr_code_url(self):
        """
        Get the URL of the QR code image
        """
        if self.qr_code:
            return self.qr_code.url
        return None
    
    @property
    def shop_info(self):
        """
        Get shop information as a dictionary
        """
        return {
            'shop_id': self.shop.id,
            'shop_name': self.shop.name,
            'shop_address': self.shop.full_address,
            'customer_name': self.shop.customer.get_full_name(),
        }
    
    @property
    def product_code(self):
        """
        Generate a human-readable product code
        """
        return f"PRD-{str(self.id)[:8].upper()}"
    
    def get_absolute_url(self):
        """
        Get the absolute URL for this product
        """
        return f"/api/products/{self.id}/"
