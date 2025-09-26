from rest_framework import serializers
from .models import Product
from shop.models import Shop

class ProductSerializer(serializers.ModelSerializer):
    """
    Main Product serializer with all fields and relationships
    """
    
    # Read-only fields for related data
    shop_name = serializers.CharField(source='shop.name', read_only=True)
    shop_address = serializers.CharField(source='shop.full_address', read_only=True)
    customer_name = serializers.CharField(source='shop.customer.get_full_name', read_only=True)
    customer_id = serializers.IntegerField(source='shop.customer.id', read_only=True)
    
    # Computed fields
    product_code = serializers.CharField(read_only=True)
    qr_code_url = serializers.CharField(read_only=True)
    shop_info = serializers.DictField(read_only=True)
    
    class Meta:
        model = Product
        fields = [
            'id',
            'shop',
            'shop_name',
            'shop_address',
            'customer_name', 
            'customer_id',
            'name',
            'description',
            'price',
            'sku',
            'is_active',
            'stock_quantity',
            'qr_code',
            'qr_code_url',
            'product_code',
            'shop_info',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['id', 'qr_code', 'created_at', 'updated_at']
    
    def validate_shop(self, value):
        """
        Validate that the shop is active
        """
        if not value.is_active:
            raise serializers.ValidationError("Cannot create products for inactive shops.")
        return value
    
    def validate_name(self, value):
        """
        Validate product name
        """
        if len(value.strip()) < 2:
            raise serializers.ValidationError("Product name must be at least 2 characters long.")
        return value.strip()
    
    def validate_price(self, value):
        """
        Validate product price
        """
        if value is not None and value < 0:
            raise serializers.ValidationError("Price cannot be negative.")
        return value
    
    def validate_stock_quantity(self, value):
        """
        Validate stock quantity
        """
        if value < 0:
            raise serializers.ValidationError("Stock quantity cannot be negative.")
        return value

class ProductCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating products with minimal required fields
    """
    
    class Meta:
        model = Product
        fields = [
            'shop',
            'name',
            'description',
            'price',
            'sku',
            'stock_quantity',
            'is_active'
        ]
    
    def validate_shop(self, value):
        """
        Validate that the shop exists and is active
        """
        if not value.is_active:
            raise serializers.ValidationError("Cannot create products for inactive shops.")
        return value

class ProductListSerializer(serializers.ModelSerializer):
    """
    Lightweight serializer for product lists
    """
    
    shop_name = serializers.CharField(source='shop.name', read_only=True)
    customer_name = serializers.CharField(source='shop.customer.get_full_name', read_only=True)
    product_code = serializers.CharField(read_only=True)
    qr_code_url = serializers.CharField(read_only=True)
    
    class Meta:
        model = Product
        fields = [
            'id',
            'name',
            'shop',
            'shop_name',
            'customer_name',
            'price',
            'sku',
            'is_active',
            'stock_quantity',
            'product_code',
            'qr_code_url',
            'created_at'
        ]

class ProductUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating products (cannot change shop)
    """
    
    class Meta:
        model = Product
        fields = [
            'name',
            'description',
            'price',
            'sku',
            'stock_quantity',
            'is_active'
        ]
    
    def validate_name(self, value):
        """
        Validate product name for updates
        """
        if len(value.strip()) < 2:
            raise serializers.ValidationError("Product name must be at least 2 characters long.")
        
        # Check for uniqueness within the same shop
        instance = self.instance
        if instance:
            existing = Product.objects.filter(
                shop=instance.shop,
                name=value.strip()
            ).exclude(id=instance.id)
            
            if existing.exists():
                raise serializers.ValidationError("A product with this name already exists in this shop.")
        
        return value.strip()

class ProductQRCodeSerializer(serializers.ModelSerializer):
    """
    Serializer specifically for QR code operations
    """
    
    qr_code_url = serializers.CharField(read_only=True)
    product_code = serializers.CharField(read_only=True)
    
    class Meta:
        model = Product
        fields = [
            'id',
            'name',
            'qr_code',
            'qr_code_url',
            'product_code'
        ]

class ProductStatsSerializer(serializers.Serializer):
    """
    Serializer for product statistics
    """
    
    total_products = serializers.IntegerField()
    active_products = serializers.IntegerField()
    inactive_products = serializers.IntegerField()
    products_with_price = serializers.IntegerField()
    products_without_price = serializers.IntegerField()
    products_in_stock = serializers.IntegerField()
    products_out_of_stock = serializers.IntegerField()
    shops_with_products = serializers.IntegerField()
    shops_without_products = serializers.IntegerField()
    average_price = serializers.DecimalField(max_digits=10, decimal_places=2, allow_null=True)
    total_stock_value = serializers.DecimalField(max_digits=15, decimal_places=2, allow_null=True)
    
class ShopProductsSerializer(serializers.ModelSerializer):
    """
    Serializer for shop with its products
    """
    
    products = ProductListSerializer(many=True, read_only=True)
    product_count = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = Shop
        fields = [
            'id',
            'name',
            'full_address',
            'customer',
            'products',
            'product_count'
        ]

class BulkProductCreateSerializer(serializers.Serializer):
    """
    Serializer for bulk product creation
    """
    
    products = ProductCreateSerializer(many=True)
    
    def validate_products(self, value):
        """
        Validate the list of products
        """
        if not value:
            raise serializers.ValidationError("Products list cannot be empty.")
        
        if len(value) > 100:  # Limit bulk operations
            raise serializers.ValidationError("Cannot create more than 100 products at once.")
        
        # Check for duplicate names within the same shop in the batch
        shop_names = {}
        for product_data in value:
            shop_id = product_data.get('shop').id if product_data.get('shop') else None
            name = product_data.get('name', '').strip()
            
            if shop_id and name:
                if shop_id not in shop_names:
                    shop_names[shop_id] = set()
                
                if name in shop_names[shop_id]:
                    raise serializers.ValidationError(f"Duplicate product name '{name}' found for the same shop in the batch.")
                
                shop_names[shop_id].add(name)
        
        return value
    
    def create(self, validated_data):
        """
        Create multiple products
        """
        products_data = validated_data['products']
        created_products = []
        
        for product_data in products_data:
            product = Product.objects.create(**product_data)
            created_products.append(product)
        
        return {'products': created_products}