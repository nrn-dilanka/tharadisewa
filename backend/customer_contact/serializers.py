from rest_framework import serializers
from .models import CustomerContact
from customer.models import Customer


class CustomerContactSerializer(serializers.ModelSerializer):
    """
    Serializer for CustomerContact model
    """
    customer_name = serializers.CharField(source='customer.full_name', read_only=True)
    customer_username = serializers.CharField(source='customer.username', read_only=True)
    contact_info = serializers.ReadOnlyField()
    
    class Meta:
        model = CustomerContact
        fields = (
            'id', 'customer', 'customer_name', 'customer_username',
            'email', 'wa_number', 'tp_number', 'is_primary', 'is_active',
            'contact_info', 'created_at', 'updated_at'
        )
        read_only_fields = ('id', 'created_at', 'updated_at')

    def validate_email(self, value):
        """
        Validate that email is unique for this customer
        """
        customer = self.context.get('customer')
        if not customer and self.instance:
            customer = self.instance.customer
            
        if customer:
            existing = CustomerContact.objects.filter(
                customer=customer, 
                email=value
            )
            if self.instance:
                existing = existing.exclude(pk=self.instance.pk)
                
            if existing.exists():
                raise serializers.ValidationError(
                    "This email already exists for this customer."
                )
        return value

    def validate_wa_number(self, value):
        """
        Validate that WhatsApp number is unique for this customer
        """
        customer = self.context.get('customer')
        if not customer and self.instance:
            customer = self.instance.customer
            
        if customer:
            existing = CustomerContact.objects.filter(
                customer=customer, 
                wa_number=value
            )
            if self.instance:
                existing = existing.exclude(pk=self.instance.pk)
                
            if existing.exists():
                raise serializers.ValidationError(
                    "This WhatsApp number already exists for this customer."
                )
        return value

    def validate_tp_number(self, value):
        """
        Validate that telephone number is unique for this customer
        """
        customer = self.context.get('customer')
        if not customer and self.instance:
            customer = self.instance.customer
            
        if customer:
            existing = CustomerContact.objects.filter(
                customer=customer, 
                tp_number=value
            )
            if self.instance:
                existing = existing.exclude(pk=self.instance.pk)
                
            if existing.exists():
                raise serializers.ValidationError(
                    "This telephone number already exists for this customer."
                )
        return value


class CustomerContactCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating CustomerContact
    """
    class Meta:
        model = CustomerContact
        fields = (
            'customer', 'email', 'wa_number', 'tp_number', 
            'is_primary', 'is_active'
        )

    def validate_customer(self, value):
        """
        Validate that customer exists and is active
        """
        if not value.is_active:
            raise serializers.ValidationError(
                "Cannot create contact for inactive customer."
            )
        return value

    def create(self, validated_data):
        """
        Create a new customer contact
        """
        return CustomerContact.objects.create(**validated_data)


class CustomerContactUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating CustomerContact (excluding customer field)
    """
    class Meta:
        model = CustomerContact
        fields = (
            'email', 'wa_number', 'tp_number', 'is_primary', 'is_active'
        )

    def validate_email(self, value):
        """
        Validate that email is unique for this customer
        """
        if self.instance:
            existing = CustomerContact.objects.filter(
                customer=self.instance.customer, 
                email=value
            ).exclude(pk=self.instance.pk)
                
            if existing.exists():
                raise serializers.ValidationError(
                    "This email already exists for this customer."
                )
        return value

    def validate_wa_number(self, value):
        """
        Validate that WhatsApp number is unique for this customer
        """
        if self.instance:
            existing = CustomerContact.objects.filter(
                customer=self.instance.customer, 
                wa_number=value
            ).exclude(pk=self.instance.pk)
                
            if existing.exists():
                raise serializers.ValidationError(
                    "This WhatsApp number already exists for this customer."
                )
        return value

    def validate_tp_number(self, value):
        """
        Validate that telephone number is unique for this customer
        """
        if self.instance:
            existing = CustomerContact.objects.filter(
                customer=self.instance.customer, 
                tp_number=value
            ).exclude(pk=self.instance.pk)
                
            if existing.exists():
                raise serializers.ValidationError(
                    "This telephone number already exists for this customer."
                )
        return value


class CustomerWithContactsSerializer(serializers.ModelSerializer):
    """
    Serializer for Customer with their contacts
    """
    contacts = CustomerContactSerializer(many=True, read_only=True)
    primary_contact = serializers.SerializerMethodField()
    
    class Meta:
        model = Customer
        fields = (
            'id', 'customer_id', 'username', 'email', 'first_name',
            'last_name', 'full_name', 'nic', 'is_verified', 
            'contacts', 'primary_contact'
        )

    def get_primary_contact(self, obj):
        """
        Get the primary contact for this customer
        """
        primary_contact = obj.contacts.filter(is_primary=True, is_active=True).first()
        if primary_contact:
            return CustomerContactSerializer(primary_contact).data
        return None