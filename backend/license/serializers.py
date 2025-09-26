from rest_framework import serializers
from .models import License
from purchase.serializers import PurchaseSerializer
from customer.serializers import CustomerSerializer
from product.serializers import ProductSerializer
from django.utils import timezone
from datetime import datetime, timedelta

class LicenseCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating a new license
    """
    
    class Meta:
        model = License
        fields = [
            'in_date', 'ex_date', 'purchase', 'license_type', 'status',
            'software_name', 'version', 'max_users', 'max_installations',
            'features_enabled', 'restrictions', 'licensed_to', 'organization',
            'contact_email', 'notes', 'terms_accepted', 'auto_renewal',
            'renewal_price', 'support_expires', 'maintenance_expires'
        ]
        extra_kwargs = {
            'in_date': {'required': False},
            'status': {'required': False},
        }
    
    def validate_ex_date(self, value):
        """
        Validate that expiry date is in the future
        """
        if value <= timezone.now():
            raise serializers.ValidationError("Expiry date must be in the future.")
        return value
    
    def validate_purchase(self, value):
        """
        Validate purchase exists and is valid
        """
        if not value:
            raise serializers.ValidationError("Purchase reference is required.")
        return value
    
    def validate(self, data):
        """
        Cross-field validation
        """
        if 'in_date' in data and 'ex_date' in data:
            if data['in_date'] >= data['ex_date']:
                raise serializers.ValidationError("Issue date must be before expiry date.")
        
        if 'support_expires' in data and data['support_expires']:
            if data['support_expires'] < data.get('in_date', timezone.now()):
                raise serializers.ValidationError("Support expiry must be after issue date.")
        
        if 'maintenance_expires' in data and data['maintenance_expires']:
            if data['maintenance_expires'] < data.get('in_date', timezone.now()):
                raise serializers.ValidationError("Maintenance expiry must be after issue date.")
        
        return data

class LicenseUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating an existing license
    """
    
    class Meta:
        model = License
        fields = [
            'ex_date', 'license_type', 'status', 'software_name', 'version',
            'max_users', 'max_installations', 'features_enabled', 'restrictions',
            'licensed_to', 'organization', 'contact_email', 'notes',
            'auto_renewal', 'renewal_price', 'support_expires', 'maintenance_expires',
            'usage_data', 'activation_count', 'last_used_date'
        ]
        extra_kwargs = {
            'license_key': {'read_only': True},
            'license_number': {'read_only': True},
            'in_date': {'read_only': True},
            'purchase': {'read_only': True},
            'activated_date': {'read_only': True},
            'created_at': {'read_only': True},
            'updated_at': {'read_only': True},
        }
    
    def validate_ex_date(self, value):
        """
        Validate that expiry date is reasonable
        """
        if value <= timezone.now():
            raise serializers.ValidationError("Expiry date must be in the future.")
        return value
    
    def validate_status(self, value):
        """
        Validate status transitions
        """
        if self.instance and self.instance.status == 'revoked':
            if value != 'revoked':
                raise serializers.ValidationError("Cannot change status of revoked license.")
        return value

class LicenseDetailSerializer(serializers.ModelSerializer):
    """
    Detailed serializer for license with related data
    """
    purchase = PurchaseSerializer(read_only=True)
    customer = serializers.SerializerMethodField()
    product = serializers.SerializerMethodField()
    shop = serializers.SerializerMethodField()
    is_expired = serializers.BooleanField(read_only=True)
    is_active = serializers.BooleanField(read_only=True)
    days_until_expiry = serializers.IntegerField(read_only=True)
    days_since_issue = serializers.IntegerField(read_only=True)
    license_duration = serializers.IntegerField(read_only=True)
    is_expiring_soon = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = License
        fields = '__all__'
    
    def get_customer(self, obj):
        """
        Get customer information
        """
        if obj.customer:
            return {
                'id': obj.customer.id,
                'full_name': obj.customer.get_full_name(),
                'email': obj.customer.email,
                'phone': obj.customer.phone,
                'nic': obj.customer.nic
            }
        return None
    
    def get_product(self, obj):
        """
        Get product information
        """
        if obj.product:
            return {
                'id': obj.product.id,
                'name': obj.product.name,
                'sku': obj.product.sku,
                'category': obj.product.category,
                'brand': obj.product.brand,
                'model': obj.product.model,
                'price': obj.product.price
            }
        return None
    
    def get_shop(self, obj):
        """
        Get shop information
        """
        if obj.shop:
            return {
                'id': obj.shop.id,
                'name': obj.shop.name,
                'email': obj.shop.email,
                'phone': obj.shop.phone
            }
        return None

class LicenseListSerializer(serializers.ModelSerializer):
    """
    Serializer for license list view
    """
    customer_name = serializers.SerializerMethodField()
    product_name = serializers.SerializerMethodField()
    shop_name = serializers.SerializerMethodField()
    is_expired = serializers.BooleanField(read_only=True)
    is_active = serializers.BooleanField(read_only=True)
    days_until_expiry = serializers.IntegerField(read_only=True)
    is_expiring_soon = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = License
        fields = [
            'id', 'license_number', 'license_key', 'software_name', 'version',
            'license_type', 'status', 'in_date', 'ex_date', 'licensed_to',
            'organization', 'max_users', 'max_installations', 'auto_renewal',
            'customer_name', 'product_name', 'shop_name', 'is_expired',
            'is_active', 'days_until_expiry', 'is_expiring_soon', 'created_at'
        ]
    
    def get_customer_name(self, obj):
        """
        Get customer full name
        """
        return obj.customer.get_full_name() if obj.customer else None
    
    def get_product_name(self, obj):
        """
        Get product name
        """
        return obj.product.name if obj.product else None
    
    def get_shop_name(self, obj):
        """
        Get shop name
        """
        return obj.shop.name if obj.shop else None

class LicenseActivationSerializer(serializers.Serializer):
    """
    Serializer for license activation
    """
    license_key = serializers.CharField(max_length=100)
    terms_accepted = serializers.BooleanField(default=True)
    activation_info = serializers.JSONField(required=False)
    
    def validate_license_key(self, value):
        """
        Validate license key exists and is activatable
        """
        try:
            license_obj = License.objects.get(license_key=value)
            if license_obj.status in ['revoked']:
                raise serializers.ValidationError("This license has been revoked.")
            if license_obj.is_expired:
                raise serializers.ValidationError("This license has expired.")
        except License.DoesNotExist:
            raise serializers.ValidationError("Invalid license key.")
        return value
    
    def validate_terms_accepted(self, value):
        """
        Validate terms are accepted
        """
        if not value:
            raise serializers.ValidationError("Terms must be accepted to activate license.")
        return value

class LicenseRenewalSerializer(serializers.Serializer):
    """
    Serializer for license renewal
    """
    renewal_period_days = serializers.IntegerField(min_value=1, max_value=3650)
    new_expiry_date = serializers.DateTimeField(required=False)
    renewal_type = serializers.ChoiceField(
        choices=[
            ('extend', 'Extend Current License'),
            ('new_period', 'New Period from Today'),
            ('custom_date', 'Custom Expiry Date')
        ],
        default='extend'
    )
    
    def validate(self, data):
        """
        Cross-field validation for renewal
        """
        renewal_type = data.get('renewal_type', 'extend')
        
        if renewal_type == 'custom_date':
            if 'new_expiry_date' not in data:
                raise serializers.ValidationError("Custom expiry date is required for custom renewal.")
            if data['new_expiry_date'] <= timezone.now():
                raise serializers.ValidationError("New expiry date must be in the future.")
        
        return data

class LicenseUsageSerializer(serializers.Serializer):
    """
    Serializer for updating license usage
    """
    usage_info = serializers.JSONField()
    session_duration = serializers.IntegerField(required=False, min_value=0)
    features_used = serializers.ListField(
        child=serializers.CharField(max_length=100),
        required=False
    )
    user_count = serializers.IntegerField(required=False, min_value=0)
    installation_info = serializers.JSONField(required=False)
    
    def validate_usage_info(self, value):
        """
        Validate usage info is a dictionary
        """
        if not isinstance(value, dict):
            raise serializers.ValidationError("Usage info must be a dictionary.")
        return value

class LicenseSummarySerializer(serializers.ModelSerializer):
    """
    Serializer for license summary/dashboard
    """
    customer_name = serializers.SerializerMethodField()
    product_name = serializers.SerializerMethodField()
    days_until_expiry = serializers.IntegerField(read_only=True)
    is_expired = serializers.BooleanField(read_only=True)
    is_active = serializers.BooleanField(read_only=True)
    is_expiring_soon = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = License
        fields = [
            'id', 'license_number', 'software_name', 'license_type', 'status',
            'ex_date', 'licensed_to', 'customer_name', 'product_name',
            'days_until_expiry', 'is_expired', 'is_active', 'is_expiring_soon'
        ]
    
    def get_customer_name(self, obj):
        return obj.customer.get_full_name() if obj.customer else None
    
    def get_product_name(self, obj):
        return obj.product.name if obj.product else None

class LicenseStatsSerializer(serializers.Serializer):
    """
    Serializer for license statistics
    """
    total_licenses = serializers.IntegerField()
    active_licenses = serializers.IntegerField()
    expired_licenses = serializers.IntegerField()
    expiring_soon = serializers.IntegerField()
    suspended_licenses = serializers.IntegerField()
    revoked_licenses = serializers.IntegerField()
    pending_licenses = serializers.IntegerField()
    
    # License type breakdown
    trial_licenses = serializers.IntegerField()
    standard_licenses = serializers.IntegerField()
    premium_licenses = serializers.IntegerField()
    enterprise_licenses = serializers.IntegerField()
    
    # Usage statistics
    total_activations = serializers.IntegerField()
    avg_license_duration = serializers.FloatField()
    renewal_rate = serializers.FloatField()
    
    # Time-based stats
    licenses_this_month = serializers.IntegerField()
    licenses_this_year = serializers.IntegerField()
    expiring_this_month = serializers.IntegerField()
    
class LicenseExportSerializer(serializers.ModelSerializer):
    """
    Serializer for exporting license data
    """
    customer_name = serializers.SerializerMethodField()
    customer_email = serializers.SerializerMethodField()
    customer_phone = serializers.SerializerMethodField()
    product_name = serializers.SerializerMethodField()
    product_sku = serializers.SerializerMethodField()
    shop_name = serializers.SerializerMethodField()
    purchase_date = serializers.SerializerMethodField()
    purchase_amount = serializers.SerializerMethodField()
    days_until_expiry = serializers.IntegerField(read_only=True)
    license_age_days = serializers.SerializerMethodField()
    
    class Meta:
        model = License
        fields = [
            'license_number', 'license_key', 'software_name', 'version',
            'license_type', 'status', 'in_date', 'ex_date', 'licensed_to',
            'organization', 'contact_email', 'max_users', 'max_installations',
            'activated_date', 'activation_count', 'last_used_date',
            'auto_renewal', 'support_expires', 'maintenance_expires',
            'customer_name', 'customer_email', 'customer_phone',
            'product_name', 'product_sku', 'shop_name', 'purchase_date',
            'purchase_amount', 'days_until_expiry', 'license_age_days',
            'created_at', 'updated_at'
        ]
    
    def get_customer_name(self, obj):
        return obj.customer.get_full_name() if obj.customer else ''
    
    def get_customer_email(self, obj):
        return obj.customer.email if obj.customer else ''
    
    def get_customer_phone(self, obj):
        return obj.customer.phone if obj.customer else ''
    
    def get_product_name(self, obj):
        return obj.product.name if obj.product else ''
    
    def get_product_sku(self, obj):
        return obj.product.sku if obj.product else ''
    
    def get_shop_name(self, obj):
        return obj.shop.name if obj.shop else ''
    
    def get_purchase_date(self, obj):
        if obj.purchase:
            return obj.purchase.purchase_date
        return None
    
    def get_purchase_amount(self, obj):
        if obj.purchase:
            return obj.purchase.total_amount
        return None
    
    def get_license_age_days(self, obj):
        return obj.days_since_issue