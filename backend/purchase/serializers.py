from rest_framework import serializers
from .models import Purchase
from product.models import Product
from customer.models import Customer
from django.utils import timezone

class PurchaseSerializer(serializers.ModelSerializer):
    """
    Main Purchase serializer with all fields and relationships
    """
    
    # Read-only fields for related data
    customer_name = serializers.CharField(source='customer.get_full_name', read_only=True)
    customer_username = serializers.CharField(source='customer.username', read_only=True)
    product_name = serializers.CharField(source='product.name', read_only=True)
    product_code = serializers.CharField(source='product.product_code', read_only=True)
    shop_name = serializers.CharField(source='product.shop.name', read_only=True)
    shop_id = serializers.IntegerField(source='product.shop.id', read_only=True)
    
    # Computed fields
    purchase_code = serializers.CharField(read_only=True)
    customer_info = serializers.DictField(read_only=True)
    product_info = serializers.DictField(read_only=True)
    shop_info = serializers.DictField(read_only=True)
    purchase_summary = serializers.DictField(read_only=True)
    
    class Meta:
        model = Purchase
        fields = [
            'id',
            'date',
            'product',
            'product_name',
            'product_code',
            'customer',
            'customer_name',
            'customer_username',
            'shop_name',
            'shop_id',
            'quantity',
            'unit_price',
            'total_amount',
            'payment_status',
            'purchase_method',
            'notes',
            'is_active',
            'purchase_code',
            'customer_info',
            'product_info',
            'shop_info',
            'purchase_summary',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['id', 'total_amount', 'created_at', 'updated_at']
    
    def validate_product(self, value):
        """
        Validate that the product is active and available
        """
        if not value.is_active:
            raise serializers.ValidationError("Cannot purchase inactive products.")
        return value
    
    def validate_customer(self, value):
        """
        Validate that the customer is active
        """
        if not value.is_active:
            raise serializers.ValidationError("Cannot create purchase for inactive customers.")
        return value
    
    def validate_quantity(self, value):
        """
        Validate purchase quantity
        """
        if value <= 0:
            raise serializers.ValidationError("Quantity must be greater than 0.")
        return value
    
    def validate_unit_price(self, value):
        """
        Validate unit price
        """
        if value <= 0:
            raise serializers.ValidationError("Unit price must be greater than 0.")
        return value
    
    def validate(self, data):
        """
        Cross-field validation
        """
        # Check if product has enough stock
        product = data.get('product')
        quantity = data.get('quantity', 1)
        
        if product and quantity:
            if product.stock_quantity < quantity:
                raise serializers.ValidationError({
                    'quantity': f"Not enough stock. Available: {product.stock_quantity}"
                })
        
        # Set unit price from product if not provided
        if product and not data.get('unit_price'):
            if product.price:
                data['unit_price'] = product.price
            else:
                raise serializers.ValidationError({
                    'unit_price': "Product has no price set. Please specify unit price."
                })
        
        return data

class PurchaseCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating purchases with minimal required fields
    """
    
    class Meta:
        model = Purchase
        fields = [
            'date',
            'product',
            'customer',
            'quantity',
            'unit_price',
            'payment_status',
            'purchase_method',
            'notes'
        ]
    
    def validate_product(self, value):
        """
        Validate product availability
        """
        if not value.is_active:
            raise serializers.ValidationError("Cannot purchase inactive products.")
        return value
    
    def validate_customer(self, value):
        """
        Validate customer status
        """
        if not value.is_active:
            raise serializers.ValidationError("Cannot create purchase for inactive customers.")
        return value

class PurchaseListSerializer(serializers.ModelSerializer):
    """
    Lightweight serializer for purchase lists
    """
    
    customer_name = serializers.CharField(source='customer.get_full_name', read_only=True)
    product_name = serializers.CharField(source='product.name', read_only=True)
    shop_name = serializers.CharField(source='product.shop.name', read_only=True)
    purchase_code = serializers.CharField(read_only=True)
    
    class Meta:
        model = Purchase
        fields = [
            'id',
            'date',
            'customer',
            'customer_name',
            'product',
            'product_name',
            'shop_name',
            'quantity',
            'unit_price',
            'total_amount',
            'payment_status',
            'purchase_method',
            'purchase_code',
            'created_at'
        ]

class PurchaseUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating purchases (limited fields)
    """
    
    class Meta:
        model = Purchase
        fields = [
            'date',
            'quantity',
            'unit_price',
            'payment_status',
            'purchase_method',
            'notes',
            'is_active'
        ]
    
    def validate_quantity(self, value):
        """
        Validate quantity for updates
        """
        if value <= 0:
            raise serializers.ValidationError("Quantity must be greater than 0.")
        
        # Check stock availability for the current product
        instance = self.instance
        if instance and instance.product:
            # Calculate available stock (current stock + quantity being returned from this purchase)
            available_stock = instance.product.stock_quantity + instance.quantity
            if available_stock < value:
                raise serializers.ValidationError(
                    f"Not enough stock. Available: {available_stock}"
                )
        
        return value

class PurchaseStatsSerializer(serializers.Serializer):
    """
    Serializer for purchase statistics
    """
    
    total_purchases = serializers.IntegerField()
    completed_purchases = serializers.IntegerField()
    pending_purchases = serializers.IntegerField()
    failed_purchases = serializers.IntegerField()
    refunded_purchases = serializers.IntegerField()
    total_revenue = serializers.DecimalField(max_digits=15, decimal_places=2)
    average_purchase_amount = serializers.DecimalField(max_digits=10, decimal_places=2, allow_null=True)
    unique_customers = serializers.IntegerField()
    unique_products = serializers.IntegerField()
    purchases_today = serializers.IntegerField()
    revenue_today = serializers.DecimalField(max_digits=15, decimal_places=2)

class CustomerPurchasesSerializer(serializers.ModelSerializer):
    """
    Serializer for customer with their purchases
    """
    
    purchases = PurchaseListSerializer(many=True, read_only=True)
    purchase_count = serializers.IntegerField(read_only=True)
    total_spent = serializers.DecimalField(max_digits=15, decimal_places=2, read_only=True)
    
    class Meta:
        model = Customer
        fields = [
            'id',
            'username',
            'first_name',
            'last_name',
            'email',
            'purchases',
            'purchase_count',
            'total_spent'
        ]

class ProductPurchasesSerializer(serializers.ModelSerializer):
    """
    Serializer for product with its purchases
    """
    
    purchases = PurchaseListSerializer(many=True, read_only=True)
    purchase_count = serializers.IntegerField(read_only=True)
    total_sold_quantity = serializers.IntegerField(read_only=True)
    total_revenue = serializers.DecimalField(max_digits=15, decimal_places=2, read_only=True)
    
    class Meta:
        model = Product
        fields = [
            'id',
            'name',
            'shop',
            'price',
            'stock_quantity',
            'purchases',
            'purchase_count',
            'total_sold_quantity',
            'total_revenue'
        ]

class BulkPurchaseCreateSerializer(serializers.Serializer):
    """
    Serializer for bulk purchase creation
    """
    
    purchases = PurchaseCreateSerializer(many=True)
    
    def validate_purchases(self, value):
        """
        Validate the list of purchases
        """
        if not value:
            raise serializers.ValidationError("Purchases list cannot be empty.")
        
        if len(value) > 50:  # Limit bulk operations
            raise serializers.ValidationError("Cannot create more than 50 purchases at once.")
        
        return value
    
    def create(self, validated_data):
        """
        Create multiple purchases
        """
        purchases_data = validated_data['purchases']
        created_purchases = []
        
        for purchase_data in purchases_data:
            purchase = Purchase.objects.create(**purchase_data)
            created_purchases.append(purchase)
        
        return {'purchases': created_purchases}