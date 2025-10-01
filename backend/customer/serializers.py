from rest_framework import serializers
from .models import Customer


class CustomerCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating customer
    """
    username = serializers.CharField(write_only=True, required=False)
    password = serializers.CharField(write_only=True, required=False)
    create_user_account = serializers.BooleanField(default=False, write_only=True)

    class Meta:
        model = Customer
        fields = (
            'first_name', 'last_name', 'email', 'phone_number', 'nic',
            'address', 'username', 'password', 'create_user_account'
        )

    def validate_nic(self, value):
        """
        Validate NIC format
        """
        import re
        if not re.match(r'^(?:\d{9}[vVxX]|\d{12})$', value):
            raise serializers.ValidationError(
                "NIC must be in format: 123456789V or 123456789012"
            )
        return value.upper()

    def validate(self, attrs):
        """
        Validate required fields for user account creation
        """
        create_user_account = attrs.get('create_user_account', False)
        
        if create_user_account:
            if not attrs.get('username'):
                raise serializers.ValidationError("Username is required when creating user account")
            if not attrs.get('password'):
                raise serializers.ValidationError("Password is required when creating user account")
        
        return attrs

    def create(self, validated_data):
        """
        Create customer and optionally create user account
        """
        create_user_account = validated_data.pop('create_user_account', False)
        username = validated_data.pop('username', None)
        password = validated_data.pop('password', None)
        
        # Create customer
        customer = Customer.objects.create(**validated_data)
        
        # Create user account if requested
        if create_user_account and username and password:
            customer.create_user_account(username, password, 'customer')
        
        return customer


class CustomerSerializer(serializers.ModelSerializer):
    """
    Serializer for customer profile
    """
    full_name = serializers.ReadOnlyField()
    has_user_account = serializers.ReadOnlyField()
    user_info = serializers.SerializerMethodField()
    
    class Meta:
        model = Customer
        fields = (
            'id', 'customer_id', 'email', 'first_name', 'last_name', 'full_name',
            'phone_number', 'nic', 'address', 'is_verified',
            'is_active', 'has_user_account', 'user_info', 'created_at', 'updated_at'
        )
        read_only_fields = ('id', 'customer_id', 'created_at', 'updated_at')
    
    def get_user_info(self, obj):
        """Get associated user account information"""
        if obj.user:
            return {
                'id': obj.user.id,
                'username': obj.user.username,
                'role': obj.user.role,
                'is_active': obj.user.is_active,
                'is_verified': obj.user.is_verified
            }
        return None


class CustomerUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating customer profile
    """
    class Meta:
        model = Customer
        fields = (
            'first_name', 'last_name', 'email', 'phone_number',
            'address'
        )

    def validate_email(self, value):
        """
        Validate that email is unique (excluding current customer)
        """
        if self.instance:
            if Customer.objects.exclude(pk=self.instance.pk).filter(email=value).exists():
                raise serializers.ValidationError("This email is already in use.")
        return value


class CustomerListSerializer(serializers.ModelSerializer):
    """
    Serializer for customer list view
    """
    full_name = serializers.ReadOnlyField()
    has_user_account = serializers.ReadOnlyField()
    
    class Meta:
        model = Customer
        fields = (
            'id', 'customer_id', 'email', 'first_name', 'last_name', 'full_name',
            'phone_number', 'nic', 'address', 'is_verified',
            'is_active', 'has_user_account', 'created_at', 'updated_at'
        )


class CustomerDetailSerializer(serializers.ModelSerializer):
    """
    Detailed serializer for customer with related data
    """
    full_name = serializers.ReadOnlyField()
    has_user_account = serializers.ReadOnlyField()
    user_info = serializers.SerializerMethodField()
    contacts = serializers.SerializerMethodField()
    purchases_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Customer
        fields = '__all__'
    
    def get_user_info(self, obj):
        """Get associated user account information"""
        if obj.user:
            return {
                'id': obj.user.id,
                'username': obj.user.username,
                'role': obj.user.role,
                'is_active': obj.user.is_active,
                'is_verified': obj.user.is_verified,
                'last_login': obj.user.last_login,
                'date_joined': obj.user.date_joined
            }
        return None
    
    def get_contacts(self, obj):
        """Get customer contacts"""
        contacts = obj.contacts.filter(is_active=True)
        return [
            {
                'id': contact.id,
                'email': contact.email,
                'wa_number': contact.wa_number,
                'tp_number': contact.tp_number,
                'is_primary': contact.is_primary
            }
            for contact in contacts
        ]
    
    def get_purchases_count(self, obj):
        """Get count of customer purchases"""
        return obj.purchases.count() if hasattr(obj, 'purchases') else 0


class CreateUserAccountSerializer(serializers.Serializer):
    """
    Serializer for creating user account for existing customer
    """
    username = serializers.CharField(max_length=150)
    password = serializers.CharField(write_only=True)
    role = serializers.CharField(default='customer')
    
    def validate_username(self, value):
        """Validate username is unique"""
        from user.models import User
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("Username already exists")
        return value