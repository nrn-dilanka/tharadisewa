from rest_framework import serializers
from .models import Shop
from customer.models import Customer
from customer_location.models import CustomerLocation


class ShopSerializer(serializers.ModelSerializer):
    """
    Serializer for Shop model
    """
    customer_name = serializers.CharField(source='customer.full_name', read_only=True)
    customer_username = serializers.CharField(source='customer.username', read_only=True)
    full_address = serializers.ReadOnlyField()
    address_dict = serializers.ReadOnlyField()
    location_count = serializers.ReadOnlyField()
    
    class Meta:
        model = Shop
        fields = (
            'id', 'name', 'postal_code', 'address_line_1', 'address_line_2',
            'address_line_3', 'city', 'customer', 'customer_name', 'customer_username',
            'is_active', 'phone_number', 'email', 'description',
            'full_address', 'address_dict', 'location_count',
            'created_at', 'updated_at'
        )
        read_only_fields = ('id', 'created_at', 'updated_at')

    def validate_postal_code(self, value):
        """
        Validate postal code format
        """
        if not value.isdigit() or len(value) != 5:
            raise serializers.ValidationError(
                "Postal code must be exactly 5 digits"
            )
        return value

    def validate_customer(self, value):
        """
        Validate that customer exists and is active
        """
        if not value.is_active:
            raise serializers.ValidationError(
                "Cannot create shop for inactive customer."
            )
        return value


class ShopCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating Shop
    """
    class Meta:
        model = Shop
        fields = (
            'name', 'postal_code', 'address_line_1', 'address_line_2',
            'address_line_3', 'city', 'customer', 'phone_number', 
            'email', 'description', 'is_active'
        )

    def validate(self, attrs):
        """
        Validate unique shop name per customer
        """
        customer = attrs.get('customer')
        name = attrs.get('name')
        
        if customer and name:
            existing = Shop.objects.filter(customer=customer, name=name)
            if self.instance:
                existing = existing.exclude(pk=self.instance.pk)
            
            if existing.exists():
                raise serializers.ValidationError(
                    "A shop with this name already exists for this customer."
                )
        
        return attrs

    def create(self, validated_data):
        """
        Create a new shop
        """
        return Shop.objects.create(**validated_data)


class ShopUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating Shop (excluding customer field)
    """
    class Meta:
        model = Shop
        fields = (
            'name', 'postal_code', 'address_line_1', 'address_line_2',
            'address_line_3', 'city', 'phone_number', 'email', 
            'description', 'is_active'
        )

    def validate_name(self, value):
        """
        Validate unique shop name per customer
        """
        if self.instance:
            existing = Shop.objects.filter(
                customer=self.instance.customer, 
                name=value
            ).exclude(pk=self.instance.pk)
                
            if existing.exists():
                raise serializers.ValidationError(
                    "A shop with this name already exists for this customer."
                )
        return value


class ShopWithLocationsSerializer(serializers.ModelSerializer):
    """
    Serializer for Shop with its locations
    """
    customer_name = serializers.CharField(source='customer.full_name', read_only=True)
    customer_username = serializers.CharField(source='customer.username', read_only=True)
    full_address = serializers.ReadOnlyField()
    address_dict = serializers.ReadOnlyField()
    locations = serializers.SerializerMethodField()
    primary_location = serializers.SerializerMethodField()
    
    class Meta:
        model = Shop
        fields = (
            'id', 'name', 'postal_code', 'address_line_1', 'address_line_2',
            'address_line_3', 'city', 'customer', 'customer_name', 'customer_username',
            'is_active', 'phone_number', 'email', 'description',
            'full_address', 'address_dict', 'locations', 'primary_location',
            'created_at', 'updated_at'
        )
    
    def get_locations(self, obj):
        """
        Get all locations for this shop
        """
        from customer_location.serializers import CustomerLocationSerializer
        locations = obj.customer_locations.filter(is_active=True).order_by('-is_primary', '-created_at')
        return CustomerLocationSerializer(locations, many=True).data
    
    def get_primary_location(self, obj):
        """
        Get the primary location for this shop
        """
        from customer_location.serializers import CustomerLocationSerializer
        primary_location = obj.customer_locations.filter(is_primary=True, is_active=True).first()
        if primary_location:
            return CustomerLocationSerializer(primary_location).data
        return None


class CustomerWithShopsSerializer(serializers.ModelSerializer):
    """
    Serializer for Customer with their shops
    """
    shops = ShopSerializer(many=True, read_only=True)
    active_shops = serializers.SerializerMethodField()
    shop_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Customer
        fields = (
            'id', 'customer_id', 'username', 'email', 'first_name',
            'last_name', 'full_name', 'nic', 'is_verified', 
            'shops', 'active_shops', 'shop_count'
        )

    def get_active_shops(self, obj):
        """
        Get only active shops for this customer
        """
        active_shops = obj.shops.filter(is_active=True)
        return ShopSerializer(active_shops, many=True).data
    
    def get_shop_count(self, obj):
        """
        Get count of active shops for this customer
        """
        return obj.shops.filter(is_active=True).count()