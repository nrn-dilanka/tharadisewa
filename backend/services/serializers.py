from rest_framework import serializers
from .models import Service
from purchase.models import Purchase
from product.models import Product
from django.utils import timezone

class ServiceSerializer(serializers.ModelSerializer):
    """
    Main Service serializer with all fields and relationships
    """
    
    # Read-only fields for related data
    customer_name = serializers.CharField(source='customer.get_full_name', read_only=True)
    customer_username = serializers.CharField(source='customer.username', read_only=True)
    customer_id = serializers.IntegerField(source='customer.id', read_only=True)
    
    purchase_code = serializers.CharField(source='purchase.purchase_code', read_only=True)
    purchase_date = serializers.DateTimeField(source='purchase.date', read_only=True)
    purchase_amount = serializers.DecimalField(source='purchase.total_amount', max_digits=12, decimal_places=2, read_only=True)
    
    product_name = serializers.CharField(source='product.name', read_only=True)
    product_code = serializers.CharField(source='product.product_code', read_only=True)
    
    shop_name = serializers.CharField(source='shop.name', read_only=True)
    shop_id = serializers.IntegerField(source='shop.id', read_only=True)
    
    # Computed fields
    service_code = serializers.CharField(read_only=True)
    customer_info = serializers.DictField(read_only=True)
    purchase_info = serializers.DictField(read_only=True)
    product_info = serializers.DictField(read_only=True)
    shop_info = serializers.DictField(read_only=True)
    service_summary = serializers.DictField(read_only=True)
    duration_since_purchase = serializers.DurationField(read_only=True)
    is_overdue = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = Service
        fields = [
            'id',
            'date',
            'purchase',
            'purchase_code',
            'purchase_date',
            'purchase_amount',
            'product',
            'product_name',
            'product_code',
            'customer_id',
            'customer_name',
            'customer_username',
            'shop_id',
            'shop_name',
            'service_type',
            'description',
            'status',
            'priority',
            'service_cost',
            'technician_notes',
            'customer_feedback',
            'rating',
            'scheduled_date',
            'completed_date',
            'warranty_expires',
            'is_under_warranty',
            'is_active',
            'service_code',
            'customer_info',
            'purchase_info',
            'product_info',
            'shop_info',
            'service_summary',
            'duration_since_purchase',
            'is_overdue',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'completed_date']
    
    def validate_purchase(self, value):
        """
        Validate that the purchase exists and is active
        """
        if not value.is_active:
            raise serializers.ValidationError("Cannot create service for inactive purchases.")
        return value
    
    def validate_product(self, value):
        """
        Validate that the product exists and is active
        """
        if not value.is_active:
            raise serializers.ValidationError("Cannot create service for inactive products.")
        return value
    
    def validate_service_cost(self, value):
        """
        Validate service cost
        """
        if value < 0:
            raise serializers.ValidationError("Service cost cannot be negative.")
        return value
    
    def validate_rating(self, value):
        """
        Validate customer rating
        """
        if value is not None and (value < 1 or value > 5):
            raise serializers.ValidationError("Rating must be between 1 and 5.")
        return value
    
    def validate_scheduled_date(self, value):
        """
        Validate scheduled date
        """
        if value and value < timezone.now():
            raise serializers.ValidationError("Scheduled date cannot be in the past.")
        return value
    
    def validate(self, data):
        """
        Cross-field validation
        """
        # Validate that purchase and product are related
        purchase = data.get('purchase')
        product = data.get('product')
        
        if purchase and product:
            if purchase.product != product:
                raise serializers.ValidationError({
                    'product': "Product must be the same as the product in the purchase."
                })
        
        # Validate scheduled date against service date
        service_date = data.get('date')
        scheduled_date = data.get('scheduled_date')
        
        if service_date and scheduled_date:
            if scheduled_date < service_date:
                raise serializers.ValidationError({
                    'scheduled_date': "Scheduled date cannot be before service date."
                })
        
        return data

class ServiceCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating services with minimal required fields
    """
    
    class Meta:
        model = Service
        fields = [
            'date',
            'purchase',
            'product',
            'service_type',
            'description',
            'status',
            'priority',
            'service_cost',
            'technician_notes',
            'scheduled_date',
            'is_under_warranty'
        ]
    
    def validate_purchase(self, value):
        """
        Validate purchase for creation
        """
        if not value.is_active:
            raise serializers.ValidationError("Cannot create service for inactive purchases.")
        return value
    
    def validate_product(self, value):
        """
        Validate product for creation
        """
        if not value.is_active:
            raise serializers.ValidationError("Cannot create service for inactive products.")
        return value

class ServiceListSerializer(serializers.ModelSerializer):
    """
    Lightweight serializer for service lists
    """
    
    customer_name = serializers.CharField(source='customer.get_full_name', read_only=True)
    purchase_code = serializers.CharField(source='purchase.purchase_code', read_only=True)
    product_name = serializers.CharField(source='product.name', read_only=True)
    shop_name = serializers.CharField(source='shop.name', read_only=True)
    service_code = serializers.CharField(read_only=True)
    is_overdue = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = Service
        fields = [
            'id',
            'date',
            'purchase',
            'purchase_code',
            'product',
            'product_name',
            'customer_name',
            'shop_name',
            'service_type',
            'status',
            'priority',
            'service_cost',
            'rating',
            'scheduled_date',
            'completed_date',
            'is_under_warranty',
            'service_code',
            'is_overdue',
            'created_at'
        ]

class ServiceUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating services (limited fields)
    """
    
    class Meta:
        model = Service
        fields = [
            'date',
            'service_type',
            'description',
            'status',
            'priority',
            'service_cost',
            'technician_notes',
            'customer_feedback',
            'rating',
            'scheduled_date',
            'warranty_expires',
            'is_under_warranty',
            'is_active'
        ]
    
    def validate_status(self, value):
        """
        Validate status changes
        """
        instance = self.instance
        if instance and instance.status == 'completed' and value != 'completed':
            raise serializers.ValidationError("Cannot change status of a completed service.")
        return value

class ServiceStatsSerializer(serializers.Serializer):
    """
    Serializer for service statistics
    """
    
    total_services = serializers.IntegerField()
    requested_services = serializers.IntegerField()
    in_progress_services = serializers.IntegerField()
    completed_services = serializers.IntegerField()
    cancelled_services = serializers.IntegerField()
    on_hold_services = serializers.IntegerField()
    overdue_services = serializers.IntegerField()
    warranty_services = serializers.IntegerField()
    paid_services = serializers.IntegerField()
    total_service_revenue = serializers.DecimalField(max_digits=15, decimal_places=2)
    average_service_cost = serializers.DecimalField(max_digits=10, decimal_places=2, allow_null=True)
    average_rating = serializers.DecimalField(max_digits=3, decimal_places=2, allow_null=True)
    services_today = serializers.IntegerField()
    unique_customers = serializers.IntegerField()
    unique_products = serializers.IntegerField()

class PurchaseServicesSerializer(serializers.ModelSerializer):
    """
    Serializer for purchase with its services
    """
    
    services = ServiceListSerializer(many=True, read_only=True)
    service_count = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = Purchase
        fields = [
            'id',
            'purchase_code',
            'date',
            'customer',
            'product',
            'total_amount',
            'services',
            'service_count'
        ]

class ProductServicesSerializer(serializers.ModelSerializer):
    """
    Serializer for product with its services
    """
    
    services = ServiceListSerializer(many=True, read_only=True)
    service_count = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = Product
        fields = [
            'id',
            'name',
            'shop',
            'price',
            'services',
            'service_count'
        ]

class BulkServiceCreateSerializer(serializers.Serializer):
    """
    Serializer for bulk service creation
    """
    
    services = ServiceCreateSerializer(many=True)
    
    def validate_services(self, value):
        """
        Validate the list of services
        """
        if not value:
            raise serializers.ValidationError("Services list cannot be empty.")
        
        if len(value) > 20:  # Limit bulk operations
            raise serializers.ValidationError("Cannot create more than 20 services at once.")
        
        return value
    
    def create(self, validated_data):
        """
        Create multiple services
        """
        services_data = validated_data['services']
        created_services = []
        
        for service_data in services_data:
            service = Service.objects.create(**service_data)
            created_services.append(service)
        
        return {'services': created_services}