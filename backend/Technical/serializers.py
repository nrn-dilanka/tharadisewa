from rest_framework import serializers
from .models import TechnicalModel


class TechnicalModelSerializer(serializers.ModelSerializer):
    """
    Comprehensive serializer for TechnicalModel
    """
    
    # Read-only computed fields
    full_model_name = serializers.ReadOnlyField()
    model_code = serializers.ReadOnlyField()
    shop = serializers.SerializerMethodField()
    shop_name = serializers.SerializerMethodField()
    product_name = serializers.ReadOnlyField()
    product_info = serializers.SerializerMethodField()
    all_specifications = serializers.SerializerMethodField()
    
    class Meta:
        model = TechnicalModel
        fields = [
            'id', 'product', 'brand', 'model',
            'model_number', 'series', 'year_released',
            'country_of_origin', 'manufacturer', 'specifications',
            'is_active', 'is_discontinued', 'notes',
            'full_model_name', 'model_code', 'shop', 'shop_name',
            'product_name', 'product_info', 'all_specifications',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'full_model_name', 'model_code', 'product_name',
            'created_at', 'updated_at'
        ]
    
    def get_shop(self, obj):
        """Get shop information"""
        if obj.shop:
            return {
                'id': str(obj.shop.id),
                'name': obj.shop.name,
                'address': obj.shop.full_address
            }
        return None
    
    def get_shop_name(self, obj):
        """Get shop name"""
        return obj.shop.name if obj.shop else 'Unknown'
    
    def get_product_info(self, obj):
        """Get product information"""
        if obj.product:
            return {
                'id': str(obj.product.id),
                'name': obj.product.name,
                'product_code': obj.product.product_code,
                'price': str(obj.product.price) if obj.product.price else None,
                'stock_quantity': obj.product.stock_quantity
            }
        return None
    
    def get_all_specifications(self, obj):
        """Get formatted specifications"""
        return obj.get_all_specifications()


class TechnicalModelCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating new technical models
    """
    
    class Meta:
        model = TechnicalModel
        fields = [
            'product', 'brand', 'model', 'model_number',
            'series', 'year_released', 'country_of_origin',
            'manufacturer', 'specifications', 'notes'
        ]
    
    def validate_brand(self, value):
        """Validate brand name"""
        if len(value.strip()) < 2:
            raise serializers.ValidationError(
                "Brand name must be at least 2 characters long"
            )
        return value.strip().title()
    
    def validate_model(self, value):
        """Validate model name"""
        if len(value.strip()) < 1:
            raise serializers.ValidationError(
                "Model name is required"
            )
        return value.strip()
    
    def validate_year_released(self, value):
        """Validate release year"""
        if value is not None:
            current_year = 2025  # Based on context date
            if value < 1900 or value > current_year + 5:
                raise serializers.ValidationError(
                    f"Year must be between 1900 and {current_year + 5}"
                )
        return value
    
    def validate(self, attrs):
        """Validate technical model data"""
        product = attrs.get('product')
        brand = attrs.get('brand')
        model = attrs.get('model')
        
        # Check for duplicate brand-model combination for the same product
        if TechnicalModel.objects.filter(
            product=product,
            brand=brand,
            model=model
        ).exists():
            raise serializers.ValidationError(
                f"Technical model with brand '{brand}' and model '{model}' "
                f"already exists for this product"
            )
        
        return attrs


class TechnicalModelListSerializer(serializers.ModelSerializer):
    """
    Lightweight serializer for technical model listings
    """
    
    full_model_name = serializers.ReadOnlyField()
    model_code = serializers.ReadOnlyField()
    shop_name = serializers.SerializerMethodField()
    product_name = serializers.ReadOnlyField()
    
    class Meta:
        model = TechnicalModel
        fields = [
            'id', 'brand', 'model', 'full_model_name', 'model_code',
            'year_released', 'is_active', 'is_discontinued',
            'shop_name', 'product_name', 'created_at'
        ]
    
    def get_shop_name(self, obj):
        """Get shop name"""
        return obj.shop.name if obj.shop else 'Unknown'


class TechnicalModelUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating technical models
    """
    
    class Meta:
        model = TechnicalModel
        fields = [
            'brand', 'model', 'model_number', 'series',
            'year_released', 'country_of_origin', 'manufacturer',
            'specifications', 'is_active', 'is_discontinued', 'notes'
        ]
    
    def validate_brand(self, value):
        """Validate brand name"""
        if len(value.strip()) < 2:
            raise serializers.ValidationError(
                "Brand name must be at least 2 characters long"
            )
        return value.strip().title()
    
    def validate_model(self, value):
        """Validate model name"""
        if len(value.strip()) < 1:
            raise serializers.ValidationError(
                "Model name is required"
            )
        return value.strip()
    
    def validate(self, attrs):
        """Validate update data"""
        if self.instance:
            brand = attrs.get('brand', self.instance.brand)
            model = attrs.get('model', self.instance.model)
            
            # Check for duplicate if brand or model changed
            if (attrs.get('brand') or attrs.get('model')):
                existing = TechnicalModel.objects.filter(
                    product=self.instance.product,
                    brand=brand,
                    model=model
                ).exclude(id=self.instance.id)
                
                if existing.exists():
                    raise serializers.ValidationError(
                        f"Technical model with brand '{brand}' and model '{model}' "
                        f"already exists for this product"
                    )
        
        return attrs


class TechnicalModelStatsSerializer(serializers.Serializer):
    """
    Serializer for technical model statistics
    """
    
    total_models = serializers.IntegerField()
    active_models = serializers.IntegerField()
    discontinued_models = serializers.IntegerField()
    total_brands = serializers.IntegerField()
    models_by_brand = serializers.DictField()
    models_by_year = serializers.DictField()
    recent_additions = serializers.IntegerField()


class TechnicalModelSearchSerializer(serializers.Serializer):
    """
    Serializer for search results
    """
    
    query = serializers.CharField(read_only=True)
    total_results = serializers.IntegerField(read_only=True)
    results = TechnicalModelListSerializer(many=True, read_only=True)


class SpecificationSerializer(serializers.Serializer):
    """
    Serializer for handling specifications
    """
    
    specifications = serializers.JSONField()
    
    def validate_specifications(self, value):
        """Validate specifications format"""
        if not isinstance(value, dict):
            raise serializers.ValidationError(
                "Specifications must be a dictionary/object"
            )
        
        # Validate that all keys are strings
        for key in value.keys():
            if not isinstance(key, str):
                raise serializers.ValidationError(
                    "All specification keys must be strings"
                )
        
        return value


class TechnicalModelSummarySerializer(serializers.Serializer):
    """
    Serializer for technical model summary
    """
    
    id = serializers.UUIDField()
    brand = serializers.CharField()
    model = serializers.CharField()
    full_name = serializers.CharField()
    model_code = serializers.CharField()
    model_number = serializers.CharField(allow_blank=True)
    series = serializers.CharField(allow_blank=True)
    year_released = serializers.IntegerField(allow_null=True)
    country_of_origin = serializers.CharField(allow_blank=True)
    manufacturer = serializers.CharField(allow_blank=True)
    product = serializers.DictField()
    specifications = serializers.DictField()
    is_active = serializers.BooleanField()
    is_discontinued = serializers.BooleanField()
    created_at = serializers.DateTimeField()
    updated_at = serializers.DateTimeField()


class BrandListSerializer(serializers.Serializer):
    """
    Serializer for brand listings
    """
    
    brand = serializers.CharField()
    model_count = serializers.IntegerField()
    active_models = serializers.IntegerField()
    latest_year = serializers.IntegerField(allow_null=True)