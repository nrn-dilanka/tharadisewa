from rest_framework import serializers
from .models import CustomerLocation
from shop.models import Shop


class CustomerLocationSerializer(serializers.ModelSerializer):
    """
    Serializer for CustomerLocation model
    """
    shop_name = serializers.CharField(source='shop.name', read_only=True)
    customer_name = serializers.CharField(source='shop.customer.full_name', read_only=True)
    coordinates = serializers.ReadOnlyField()
    google_maps_url = serializers.ReadOnlyField()
    location_info = serializers.ReadOnlyField()
    
    class Meta:
        model = CustomerLocation
        fields = (
            'id', 'longitude', 'latitude', 'shop', 'shop_name', 'customer_name',
            'location_name', 'address_description', 'is_primary', 'is_active',
            'accuracy_radius', 'coordinates', 'google_maps_url', 'location_info',
            'created_at', 'updated_at'
        )
        read_only_fields = ('id', 'created_at', 'updated_at')

    def validate_longitude(self, value):
        """
        Validate longitude range
        """
        if not -180.0 <= float(value) <= 180.0:
            raise serializers.ValidationError(
                "Longitude must be between -180.0 and 180.0"
            )
        return value

    def validate_latitude(self, value):
        """
        Validate latitude range
        """
        if not -90.0 <= float(value) <= 90.0:
            raise serializers.ValidationError(
                "Latitude must be between -90.0 and 90.0"
            )
        return value

    def validate_shop(self, value):
        """
        Validate that shop exists and is active
        """
        if not value.is_active:
            raise serializers.ValidationError(
                "Cannot create location for inactive shop."
            )
        return value

    def validate(self, attrs):
        """
        Validate unique coordinates per shop
        """
        shop = attrs.get('shop')
        longitude = attrs.get('longitude')
        latitude = attrs.get('latitude')
        
        if shop and longitude is not None and latitude is not None:
            existing = CustomerLocation.objects.filter(
                shop=shop,
                longitude=longitude,
                latitude=latitude
            )
            if self.instance:
                existing = existing.exclude(pk=self.instance.pk)
            
            if existing.exists():
                raise serializers.ValidationError(
                    "A location with these coordinates already exists for this shop."
                )
        
        return attrs


class CustomerLocationCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating CustomerLocation
    """
    class Meta:
        model = CustomerLocation
        fields = (
            'longitude', 'latitude', 'shop', 'location_name', 
            'address_description', 'is_primary', 'is_active', 'accuracy_radius'
        )

    def create(self, validated_data):
        """
        Create a new customer location
        """
        return CustomerLocation.objects.create(**validated_data)


class CustomerLocationUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating CustomerLocation (excluding shop field)
    """
    class Meta:
        model = CustomerLocation
        fields = (
            'longitude', 'latitude', 'location_name', 'address_description',
            'is_primary', 'is_active', 'accuracy_radius'
        )

    def validate(self, attrs):
        """
        Validate unique coordinates per shop (for updates)
        """
        if self.instance:
            longitude = attrs.get('longitude', self.instance.longitude)
            latitude = attrs.get('latitude', self.instance.latitude)
            
            existing = CustomerLocation.objects.filter(
                shop=self.instance.shop,
                longitude=longitude,
                latitude=latitude
            ).exclude(pk=self.instance.pk)
                
            if existing.exists():
                raise serializers.ValidationError(
                    "A location with these coordinates already exists for this shop."
                )
        
        return attrs


class ShopWithLocationsSerializer(serializers.ModelSerializer):
    """
    Serializer for Shop with its locations (avoiding circular import)
    """
    locations = CustomerLocationSerializer(source='customer_locations', many=True, read_only=True)
    primary_location = serializers.SerializerMethodField()
    location_count = serializers.SerializerMethodField()
    customer_name = serializers.CharField(source='customer.full_name', read_only=True)
    
    class Meta:
        model = Shop
        fields = (
            'id', 'name', 'postal_code', 'address_line_1', 'address_line_2',
            'address_line_3', 'city', 'customer', 'customer_name',
            'is_active', 'phone_number', 'email', 'description',
            'locations', 'primary_location', 'location_count',
            'created_at', 'updated_at'
        )
    
    def get_primary_location(self, obj):
        """
        Get the primary location for this shop
        """
        primary_location = obj.customer_locations.filter(is_primary=True, is_active=True).first()
        if primary_location:
            return CustomerLocationSerializer(primary_location).data
        return None
    
    def get_location_count(self, obj):
        """
        Get count of active locations for this shop
        """
        return obj.customer_locations.filter(is_active=True).count()


class NearbyLocationSerializer(serializers.ModelSerializer):
    """
    Serializer for nearby locations search
    """
    shop_name = serializers.CharField(source='shop.name', read_only=True)
    customer_name = serializers.CharField(source='shop.customer.full_name', read_only=True)
    shop_address = serializers.CharField(source='shop.full_address', read_only=True)
    distance_info = serializers.SerializerMethodField()
    
    class Meta:
        model = CustomerLocation
        fields = (
            'id', 'longitude', 'latitude', 'shop', 'shop_name', 'customer_name',
            'shop_address', 'location_name', 'address_description',
            'coordinates', 'google_maps_url', 'distance_info'
        )
    
    def get_distance_info(self, obj):
        """
        Calculate distance information (placeholder for actual distance calculation)
        """
        # In a real implementation, you would calculate actual distance
        # This requires the search coordinates to be passed in context
        search_lat = self.context.get('search_latitude')
        search_lon = self.context.get('search_longitude')
        
        if search_lat is not None and search_lon is not None:
            # Simple distance calculation (not accurate for large distances)
            lat_diff = abs(float(obj.latitude) - float(search_lat))
            lon_diff = abs(float(obj.longitude) - float(search_lon))
            approximate_distance = ((lat_diff ** 2 + lon_diff ** 2) ** 0.5) * 111  # Rough km
            
            return {
                'approximate_distance_km': round(approximate_distance, 2),
                'note': 'Approximate distance calculation'
            }
        
        return None