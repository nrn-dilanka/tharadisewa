from rest_framework import serializers
from django.utils import timezone
from decimal import Decimal
from .models import Bill


class BillSerializer(serializers.ModelSerializer):
    """
    Comprehensive serializer for Bill model
    """
    
    # Read-only computed fields
    bill_code = serializers.ReadOnlyField()
    customer = serializers.SerializerMethodField()
    customer_name = serializers.SerializerMethodField()
    shop = serializers.SerializerMethodField()
    shop_name = serializers.SerializerMethodField()
    service_type = serializers.SerializerMethodField()
    service_description = serializers.SerializerMethodField()
    purchase_code = serializers.SerializerMethodField()
    is_overdue = serializers.ReadOnlyField()
    days_until_due = serializers.ReadOnlyField()
    payment_method_display = serializers.ReadOnlyField()
    
    # Display fields
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = Bill
        fields = [
            'id', 'date', 'amount', 'service', 'purchase',
            'bill_number', 'bill_code', 'status', 'status_display',
            'due_date', 'paid_date', 'notes',
            'tax_rate', 'tax_amount', 'discount_rate', 'discount_amount',
            'subtotal', 'customer', 'customer_name', 'shop', 'shop_name',
            'service_type', 'service_description', 'purchase_code',
            'is_overdue', 'days_until_due', 'payment_method_display',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'bill_number', 'bill_code', 'amount', 'tax_amount',
            'discount_amount', 'is_overdue', 'days_until_due',
            'payment_method_display', 'created_at', 'updated_at'
        ]
    
    def get_customer(self, obj):
        """Get customer information"""
        if obj.customer:
            return {
                'id': str(obj.customer.id),
                'username': obj.customer.username,
                'first_name': obj.customer.first_name,
                'last_name': obj.customer.last_name,
                'full_name': obj.customer.get_full_name(),
                'email': obj.customer.email
            }
        return None
    
    def get_customer_name(self, obj):
        """Get customer full name"""
        return obj.customer.get_full_name() if obj.customer else 'Unknown'
    
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
    
    def get_service_type(self, obj):
        """Get service type"""
        return obj.service.get_service_type_display() if obj.service else 'N/A'
    
    def get_service_description(self, obj):
        """Get service description"""
        return obj.service.description if obj.service else 'N/A'
    
    def get_purchase_code(self, obj):
        """Get purchase code"""
        return obj.purchase.purchase_code if obj.purchase else 'N/A'


class BillCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating new bills
    """
    
    class Meta:
        model = Bill
        fields = [
            'date', 'service', 'purchase', 'subtotal',
            'tax_rate', 'discount_rate', 'due_date', 'notes'
        ]
    
    def validate(self, attrs):
        """Validate bill creation data"""
        service = attrs.get('service')
        purchase = attrs.get('purchase')
        
        # Validate that service and purchase are related
        if service and purchase:
            if service.purchase != purchase:
                raise serializers.ValidationError(
                    "Service must be related to the specified purchase"
                )
        
        # Validate subtotal
        subtotal = attrs.get('subtotal', 0)
        if subtotal <= 0:
            raise serializers.ValidationError(
                "Subtotal must be greater than 0"
            )
        
        # Validate tax rate
        tax_rate = attrs.get('tax_rate', 0)
        if tax_rate < 0 or tax_rate > 100:
            raise serializers.ValidationError(
                "Tax rate must be between 0 and 100"
            )
        
        # Validate discount rate
        discount_rate = attrs.get('discount_rate', 0)
        if discount_rate < 0 or discount_rate > 100:
            raise serializers.ValidationError(
                "Discount rate must be between 0 and 100"
            )
        
        return attrs
    
    def create(self, validated_data):
        """Create bill with calculated amounts"""
        subtotal = validated_data.get('subtotal', 0)
        tax_rate = validated_data.get('tax_rate', 0)
        discount_rate = validated_data.get('discount_rate', 0)
        
        # Calculate amounts
        tax_amount = (subtotal * tax_rate) / 100
        discount_amount = (subtotal * discount_rate) / 100
        total_amount = subtotal + tax_amount - discount_amount
        
        # Create bill
        bill = Bill.objects.create(
            **validated_data,
            tax_amount=tax_amount,
            discount_amount=discount_amount,
            amount=total_amount
        )
        
        return bill


class BillListSerializer(serializers.ModelSerializer):
    """
    Lightweight serializer for bill listings
    """
    
    customer_name = serializers.SerializerMethodField()
    shop_name = serializers.SerializerMethodField()
    service_type = serializers.SerializerMethodField()
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    is_overdue = serializers.ReadOnlyField()
    
    class Meta:
        model = Bill
        fields = [
            'id', 'bill_number', 'date', 'amount', 'status', 'status_display',
            'due_date', 'customer_name', 'shop_name', 'service_type',
            'is_overdue', 'created_at'
        ]
    
    def get_customer_name(self, obj):
        """Get customer name"""
        return obj.customer.get_full_name() if obj.customer else 'Unknown'
    
    def get_shop_name(self, obj):
        """Get shop name"""
        return obj.shop.name if obj.shop else 'Unknown'
    
    def get_service_type(self, obj):
        """Get service type"""
        return obj.service.get_service_type_display() if obj.service else 'N/A'


class BillUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating bills
    """
    
    class Meta:
        model = Bill
        fields = [
            'status', 'due_date', 'paid_date', 'notes',
            'tax_rate', 'discount_rate', 'subtotal'
        ]
    
    def validate_status(self, value):
        """Validate status transitions"""
        if self.instance and self.instance.status == 'paid':
            if value != 'paid':
                raise serializers.ValidationError(
                    "Cannot change status of a paid bill"
                )
        return value
    
    def validate(self, attrs):
        """Validate update data"""
        # If marking as paid, set paid_date
        if attrs.get('status') == 'paid' and not attrs.get('paid_date'):
            attrs['paid_date'] = timezone.now()
        
        # Recalculate amounts if rates or subtotal changed
        if any(key in attrs for key in ['subtotal', 'tax_rate', 'discount_rate']):
            subtotal = attrs.get('subtotal', self.instance.subtotal)
            tax_rate = attrs.get('tax_rate', self.instance.tax_rate)
            discount_rate = attrs.get('discount_rate', self.instance.discount_rate)
            
            # Calculate new amounts
            tax_amount = (subtotal * tax_rate) / 100
            discount_amount = (subtotal * discount_rate) / 100
            total_amount = subtotal + tax_amount - discount_amount
            
            attrs.update({
                'tax_amount': tax_amount,
                'discount_amount': discount_amount,
                'amount': total_amount
            })
        
        return attrs


class BillStatsSerializer(serializers.Serializer):
    """
    Serializer for bill statistics
    """
    
    total_bills = serializers.IntegerField()
    total_amount = serializers.DecimalField(max_digits=10, decimal_places=2)
    paid_bills = serializers.IntegerField()
    paid_amount = serializers.DecimalField(max_digits=10, decimal_places=2)
    pending_bills = serializers.IntegerField()
    pending_amount = serializers.DecimalField(max_digits=10, decimal_places=2)
    overdue_bills = serializers.IntegerField()
    overdue_amount = serializers.DecimalField(max_digits=10, decimal_places=2)
    average_bill_amount = serializers.DecimalField(max_digits=10, decimal_places=2)
    total_tax_collected = serializers.DecimalField(max_digits=10, decimal_places=2)
    total_discounts_given = serializers.DecimalField(max_digits=10, decimal_places=2)


class BillSummarySerializer(serializers.Serializer):
    """
    Serializer for bill summary information
    """
    
    bill_number = serializers.CharField()
    date = serializers.DateTimeField()
    customer = serializers.CharField()
    service_type = serializers.CharField()
    subtotal = serializers.DecimalField(max_digits=10, decimal_places=2)
    tax_rate = serializers.DecimalField(max_digits=5, decimal_places=2)
    tax_amount = serializers.DecimalField(max_digits=10, decimal_places=2)
    discount_rate = serializers.DecimalField(max_digits=5, decimal_places=2)
    discount_amount = serializers.DecimalField(max_digits=10, decimal_places=2)
    total_amount = serializers.DecimalField(max_digits=10, decimal_places=2)
    status = serializers.CharField()
    due_date = serializers.DateTimeField(allow_null=True)
    is_overdue = serializers.BooleanField()