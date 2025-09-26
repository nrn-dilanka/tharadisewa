from django.db import models
from django.core.validators import MinLengthValidator
import uuid

class TechnicalModel(models.Model):
    """
    Model to represent technical specifications and model information for products
    """
    
    # Primary key - UUID
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        help_text="Unique identifier for the technical model"
    )
    
    # Product reference (Foreign Key)
    product = models.ForeignKey(
        'product.Product',
        on_delete=models.CASCADE,
        related_name='technical_models',
        help_text="Reference to the product this technical model belongs to"
    )
    
    # Brand field
    brand = models.CharField(
        max_length=100,
        validators=[MinLengthValidator(2)],
        help_text="Brand name of the product"
    )
    
    # Model field  
    model = models.CharField(
        max_length=150,
        validators=[MinLengthValidator(1)],
        help_text="Model name/number of the product"
    )
    
    # Additional technical specification fields
    model_number = models.CharField(
        max_length=50,
        blank=True,
        help_text="Official model number"
    )
    
    series = models.CharField(
        max_length=100,
        blank=True,
        help_text="Product series name"
    )
    
    year_released = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Year the model was released"
    )
    
    country_of_origin = models.CharField(
        max_length=100,
        blank=True,
        help_text="Country where the product was manufactured"
    )
    
    manufacturer = models.CharField(
        max_length=150,
        blank=True,
        help_text="Manufacturer name (may differ from brand)"
    )
    
    # Technical specifications
    specifications = models.JSONField(
        default=dict,
        blank=True,
        help_text="Technical specifications as JSON (dimensions, weight, power, etc.)"
    )
    
    # Status and metadata
    is_active = models.BooleanField(
        default=True,
        help_text="Whether this technical model is active"
    )
    
    is_discontinued = models.BooleanField(
        default=False,
        help_text="Whether this model has been discontinued"
    )
    
    notes = models.TextField(
        blank=True,
        help_text="Additional notes about the technical model"
    )
    
    # Timestamps
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="When the technical model was created"
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="When the technical model was last updated"
    )
    
    class Meta:
        ordering = ['brand', 'model']
        indexes = [
            models.Index(fields=['brand']),
            models.Index(fields=['model']),
            models.Index(fields=['brand', 'model']),
            models.Index(fields=['product']),
            models.Index(fields=['year_released']),
            models.Index(fields=['is_active']),
        ]
        unique_together = ['product', 'brand', 'model']
        verbose_name = 'Technical Model'
        verbose_name_plural = 'Technical Models'
    
    def __str__(self):
        return f"{self.brand} {self.model} - {self.product.name}"
    
    @property
    def full_model_name(self):
        """
        Return full model name combining brand and model
        """
        return f"{self.brand} {self.model}"
    
    @property
    def model_code(self):
        """
        Generate a model code based on brand and model
        """
        brand_code = self.brand[:3].upper().replace(' ', '')
        model_code = self.model[:5].upper().replace(' ', '')
        return f"{brand_code}-{model_code}"
    
    @property
    def shop(self):
        """
        Get shop from product
        """
        return self.product.shop if self.product else None
    
    @property
    def product_name(self):
        """
        Get product name
        """
        return self.product.name if self.product else 'Unknown'
    
    def get_specification(self, key, default=None):
        """
        Get a specific specification value
        """
        return self.specifications.get(key, default)
    
    def set_specification(self, key, value):
        """
        Set a specific specification value
        """
        if not isinstance(self.specifications, dict):
            self.specifications = {}
        self.specifications[key] = value
    
    def get_all_specifications(self):
        """
        Get formatted specifications
        """
        if not self.specifications:
            return {}
        
        formatted_specs = {}
        for key, value in self.specifications.items():
            # Format key for display
            display_key = key.replace('_', ' ').title()
            formatted_specs[display_key] = value
        
        return formatted_specs
    
    def get_technical_summary(self):
        """
        Get formatted technical summary
        """
        return {
            'id': str(self.id),
            'brand': self.brand,
            'model': self.model,
            'full_name': self.full_model_name,
            'model_code': self.model_code,
            'model_number': self.model_number,
            'series': self.series,
            'year_released': self.year_released,
            'country_of_origin': self.country_of_origin,
            'manufacturer': self.manufacturer,
            'product': {
                'id': str(self.product.id),
                'name': self.product.name,
                'shop': self.product.shop.name if self.product.shop else None
            },
            'specifications': self.get_all_specifications(),
            'is_active': self.is_active,
            'is_discontinued': self.is_discontinued,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }
    
    def mark_as_discontinued(self):
        """
        Mark the technical model as discontinued
        """
        self.is_discontinued = True
        self.is_active = False
        self.save()
    
    def reactivate(self):
        """
        Reactivate the technical model
        """
        self.is_active = True
        self.is_discontinued = False
        self.save()
    
    def update_specifications(self, new_specs):
        """
        Update specifications with new data
        """
        if not isinstance(self.specifications, dict):
            self.specifications = {}
        
        self.specifications.update(new_specs)
        self.save()
    
    def clear_specifications(self):
        """
        Clear all specifications
        """
        self.specifications = {}
        self.save()
    
    @classmethod
    def get_by_brand(cls, brand_name):
        """
        Get all technical models by brand
        """
        return cls.objects.filter(
            brand__icontains=brand_name,
            is_active=True
        )
    
    @classmethod
    def get_active_models(cls):
        """
        Get all active technical models
        """
        return cls.objects.filter(is_active=True)
    
    @classmethod
    def search_models(cls, query):
        """
        Search technical models by brand, model, or product name
        """
        return cls.objects.filter(
            models.Q(brand__icontains=query) |
            models.Q(model__icontains=query) |
            models.Q(product__name__icontains=query) |
            models.Q(model_number__icontains=query) |
            models.Q(series__icontains=query)
        ).filter(is_active=True)
