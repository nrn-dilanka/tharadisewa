from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


class CustomerLocation(models.Model):
    """
    Customer Location Model with geographic coordinates and shop relation
    """
    # Geographic coordinates
    longitude = models.DecimalField(
        max_digits=11,
        decimal_places=8,
        validators=[
            MinValueValidator(-180.0),
            MaxValueValidator(180.0)
        ],
        help_text="Longitude coordinate (-180.0 to 180.0)"
    )
    
    latitude = models.DecimalField(
        max_digits=10,
        decimal_places=8,
        validators=[
            MinValueValidator(-90.0),
            MaxValueValidator(90.0)
        ],
        help_text="Latitude coordinate (-90.0 to 90.0)"
    )
    
    # Shop relation - importing here to avoid circular import
    shop = models.ForeignKey(
        'shop.Shop',
        on_delete=models.CASCADE,
        related_name='customer_locations',
        help_text="Related shop"
    )
    
    # Additional location information
    location_name = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text="Optional name for this location"
    )
    
    address_description = models.TextField(
        blank=True,
        null=True,
        help_text="Description of the location address"
    )
    
    is_primary = models.BooleanField(
        default=False,
        help_text="Is this the primary location for the shop?"
    )
    
    is_active = models.BooleanField(
        default=True,
        help_text="Is this location active?"
    )
    
    accuracy_radius = models.PositiveIntegerField(
        blank=True,
        null=True,
        help_text="GPS accuracy radius in meters"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'customer_locations'
        verbose_name = 'Customer Location'
        verbose_name_plural = 'Customer Locations'
        ordering = ['-created_at']
        
        # Unique constraint for coordinates per shop
        constraints = [
            models.UniqueConstraint(
                fields=['shop', 'longitude', 'latitude'],
                name='unique_shop_coordinates'
            ),
        ]
        
        # Index for geographic queries
        indexes = [
            models.Index(fields=['longitude', 'latitude']),
            models.Index(fields=['shop', 'is_active']),
        ]
    
    def __str__(self):
        if self.location_name:
            return f"{self.location_name} ({self.latitude}, {self.longitude})"
        return f"{self.shop.name} Location ({self.latitude}, {self.longitude})"
    
    def save(self, *args, **kwargs):
        # If this is set as primary, make sure no other location for this shop is primary
        if self.is_primary:
            CustomerLocation.objects.filter(
                shop=self.shop,
                is_primary=True
            ).exclude(pk=self.pk).update(is_primary=False)
        
        super().save(*args, **kwargs)
    
    @property
    def coordinates(self):
        """Return coordinates as a tuple"""
        return (float(self.latitude), float(self.longitude))
    
    @property
    def google_maps_url(self):
        """Generate Google Maps URL for this location"""
        return f"https://www.google.com/maps?q={self.latitude},{self.longitude}"
    
    @property
    def location_info(self):
        """Return complete location information"""
        return {
            'coordinates': self.coordinates,
            'longitude': float(self.longitude),
            'latitude': float(self.latitude),
            'location_name': self.location_name,
            'address_description': self.address_description,
            'is_primary': self.is_primary,
            'accuracy_radius': self.accuracy_radius,
            'google_maps_url': self.google_maps_url
        }
    
    @classmethod
    def get_nearby_locations(cls, latitude, longitude, radius_km=5):
        """
        Get locations within a certain radius (in kilometers)
        This is a simplified version - for production use PostGIS
        """
        # Rough approximation: 1 degree ≈ 111 km
        lat_delta = radius_km / 111.0
        lon_delta = radius_km / (111.0 * abs(float(latitude)))
        
        return cls.objects.filter(
            latitude__range=(float(latitude) - lat_delta, float(latitude) + lat_delta),
            longitude__range=(float(longitude) - lon_delta, float(longitude) + lon_delta),
            is_active=True
        )
