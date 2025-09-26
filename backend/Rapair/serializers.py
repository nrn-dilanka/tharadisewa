from rest_framework import serializers
from django.utils import timezone
from decimal import Decimal
from .models import Repair


class RepairSerializer(serializers.ModelSerializer):
    """
    Comprehensive serializer for Repair model
    """
    
    # Read-only computed fields
    customer = serializers.SerializerMethodField()
    customer_name = serializers.SerializerMethodField()
    product = serializers.SerializerMethodField()
    product_name = serializers.SerializerMethodField()
    shop = serializers.SerializerMethodField()
    shop_name = serializers.SerializerMethodField()
    is_overdue = serializers.ReadOnlyField()
    duration = serializers.SerializerMethodField()
    days_in_repair = serializers.ReadOnlyField()
    total_parts_cost = serializers.SerializerMethodField()
    
    # Display fields
    repair_type_display = serializers.CharField(source='get_repair_type_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    priority_display = serializers.CharField(source='get_priority_display', read_only=True)
    
    class Meta:
        model = Repair
        fields = [
            'id', 'date', 'purchase', 'repair_code',
            'repair_type', 'repair_type_display', 'status', 'status_display',
            'priority', 'priority_display', 'problem_description', 'diagnosis',
            'repair_notes', 'technician_name', 'estimated_cost', 'actual_cost',
            'parts_used', 'started_date', 'completed_date', 'estimated_completion',
            'is_under_warranty', 'warranty_void', 'quality_check_passed',
            'customer_satisfaction', 'customer_contacted', 'ready_for_pickup',
            'delivered_date', 'customer', 'customer_name', 'product', 'product_name',
            'shop', 'shop_name', 'is_overdue', 'duration', 'days_in_repair',
            'total_parts_cost', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'repair_code', 'is_overdue', 'days_in_repair',
            'created_at', 'updated_at'
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
    
    def get_product(self, obj):
        """Get product information"""
        if obj.product:
            return {
                'id': str(obj.product.id),
                'name': obj.product.name,
                'product_code': obj.product.product_code,
                'price': str(obj.product.price) if obj.product.price else None
            }
        return None
    
    def get_product_name(self, obj):
        """Get product name"""
        return obj.product.name if obj.product else 'Unknown'
    
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
    
    def get_duration(self, obj):
        """Get repair duration in readable format"""
        duration = obj.duration
        if duration:
            total_seconds = int(duration.total_seconds())
            days = total_seconds // 86400
            hours = (total_seconds % 86400) // 3600
            return f"{days} days, {hours} hours"
        return None
    
    def get_total_parts_cost(self, obj):
        """Get total cost of parts used"""
        return obj.calculate_total_parts_cost()


class RepairCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating new repairs
    """
    
    class Meta:
        model = Repair
        fields = [
            'date', 'purchase', 'repair_type', 'priority',
            'problem_description', 'technician_name', 'estimated_cost',
            'estimated_completion', 'is_under_warranty'
        ]
    
    def validate_purchase(self, value):
        """Validate purchase exists and is valid"""
        if not value:
            raise serializers.ValidationError("Purchase reference is required")
        return value
    
    def validate_problem_description(self, value):
        """Validate problem description"""
        if not value or len(value.strip()) < 10:
            raise serializers.ValidationError(
                "Problem description must be at least 10 characters long"
            )
        return value.strip()
    
    def validate_estimated_cost(self, value):
        """Validate estimated cost"""
        if value is not None and value < 0:
            raise serializers.ValidationError(
                "Estimated cost cannot be negative"
            )
        return value
    
    def validate(self, attrs):
        """Validate repair creation data"""
        estimated_completion = attrs.get('estimated_completion')
        
        # Validate estimated completion date
        if estimated_completion and estimated_completion <= timezone.now():
            raise serializers.ValidationError(
                "Estimated completion date must be in the future"
            )
        
        return attrs


class RepairListSerializer(serializers.ModelSerializer):
    """
    Lightweight serializer for repair listings
    """
    
    customer_name = serializers.SerializerMethodField()
    product_name = serializers.SerializerMethodField()
    shop_name = serializers.SerializerMethodField()
    repair_type_display = serializers.CharField(source='get_repair_type_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    priority_display = serializers.CharField(source='get_priority_display', read_only=True)
    is_overdue = serializers.ReadOnlyField()
    days_in_repair = serializers.ReadOnlyField()
    
    class Meta:
        model = Repair
        fields = [
            'id', 'repair_code', 'date', 'repair_type', 'repair_type_display',
            'status', 'status_display', 'priority', 'priority_display',
            'customer_name', 'product_name', 'shop_name', 'technician_name',
            'estimated_cost', 'estimated_completion', 'is_overdue', 'days_in_repair',
            'ready_for_pickup', 'created_at'
        ]
    
    def get_customer_name(self, obj):
        """Get customer name"""
        return obj.customer.get_full_name() if obj.customer else 'Unknown'
    
    def get_product_name(self, obj):
        """Get product name"""
        return obj.product.name if obj.product else 'Unknown'
    
    def get_shop_name(self, obj):
        """Get shop name"""
        return obj.shop.name if obj.shop else 'Unknown'


class RepairUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating repairs
    """
    
    class Meta:
        model = Repair
        fields = [
            'repair_type', 'status', 'priority', 'diagnosis', 'repair_notes',
            'technician_name', 'estimated_cost', 'actual_cost', 'started_date',
            'completed_date', 'estimated_completion', 'warranty_void',
            'quality_check_passed', 'customer_satisfaction', 'customer_contacted',
            'ready_for_pickup', 'delivered_date'
        ]
    
    def validate_status(self, value):
        """Validate status transitions"""
        if self.instance:
            current_status = self.instance.status
            
            # Define valid status transitions
            valid_transitions = {
                'requested': ['diagnosed', 'in_progress', 'cancelled'],
                'diagnosed': ['in_progress', 'waiting_parts', 'cancelled'],
                'in_progress': ['waiting_parts', 'completed', 'failed', 'cancelled'],
                'waiting_parts': ['in_progress', 'completed', 'cancelled'],
                'completed': [],  # Completed repairs cannot change status
                'cancelled': [],  # Cancelled repairs cannot change status
                'failed': ['requested', 'diagnosed']  # Failed repairs can be restarted
            }
            
            if current_status in ['completed', 'cancelled'] and value != current_status:
                raise serializers.ValidationError(
                    f"Cannot change status from {current_status}"
                )
            
            if value not in valid_transitions.get(current_status, []) and value != current_status:
                raise serializers.ValidationError(
                    f"Invalid status transition from {current_status} to {value}"
                )
        
        return value
    
    def validate_customer_satisfaction(self, value):
        """Validate customer satisfaction rating"""
        if value is not None and (value < 1 or value > 5):
            raise serializers.ValidationError(
                "Customer satisfaction rating must be between 1 and 5"
            )
        return value
    
    def validate(self, attrs):
        """Validate update data"""
        # Auto-set dates based on status changes
        status = attrs.get('status', self.instance.status if self.instance else None)
        
        if status == 'in_progress' and not self.instance.started_date:
            attrs['started_date'] = timezone.now()
        
        if status == 'completed':
            if not attrs.get('completed_date'):
                attrs['completed_date'] = timezone.now()
            attrs['ready_for_pickup'] = True
        
        # Validate actual cost
        actual_cost = attrs.get('actual_cost')
        if actual_cost is not None and actual_cost < 0:
            raise serializers.ValidationError(
                "Actual cost cannot be negative"
            )
        
        return attrs


class RepairStatsSerializer(serializers.Serializer):
    """
    Serializer for repair statistics
    """
    
    total_repairs = serializers.IntegerField()
    active_repairs = serializers.IntegerField()
    completed_repairs = serializers.IntegerField()
    cancelled_repairs = serializers.IntegerField()
    overdue_repairs = serializers.IntegerField()
    repairs_by_type = serializers.DictField()
    repairs_by_status = serializers.DictField()
    repairs_by_priority = serializers.DictField()
    average_repair_time = serializers.CharField()
    total_repair_cost = serializers.DecimalField(max_digits=10, decimal_places=2)
    average_repair_cost = serializers.DecimalField(max_digits=10, decimal_places=2)


class RepairSummarySerializer(serializers.Serializer):
    """
    Serializer for repair summary information
    """
    
    repair_code = serializers.CharField()
    date = serializers.DateTimeField()
    customer = serializers.CharField()
    product = serializers.CharField()
    shop = serializers.CharField()
    repair_type = serializers.CharField()
    status = serializers.CharField()
    priority = serializers.CharField()
    problem_description = serializers.CharField()
    diagnosis = serializers.CharField(allow_blank=True)
    technician = serializers.CharField(allow_blank=True)
    estimated_cost = serializers.DecimalField(max_digits=10, decimal_places=2, allow_null=True)
    actual_cost = serializers.DecimalField(max_digits=10, decimal_places=2, allow_null=True)
    parts_cost = serializers.DecimalField(max_digits=10, decimal_places=2)
    is_under_warranty = serializers.BooleanField()
    started_date = serializers.DateTimeField(allow_null=True)
    completed_date = serializers.DateTimeField(allow_null=True)
    estimated_completion = serializers.DateTimeField(allow_null=True)
    is_overdue = serializers.BooleanField()
    days_in_repair = serializers.IntegerField()
    quality_check_passed = serializers.BooleanField()
    customer_satisfaction = serializers.IntegerField(allow_null=True)
    ready_for_pickup = serializers.BooleanField()


class PartsUsedSerializer(serializers.Serializer):
    """
    Serializer for parts used in repairs
    """
    
    name = serializers.CharField()
    quantity = serializers.IntegerField(min_value=1)
    cost = serializers.DecimalField(max_digits=10, decimal_places=2, allow_null=True)
    
    def validate_name(self, value):
        """Validate part name"""
        if not value or len(value.strip()) < 2:
            raise serializers.ValidationError(
                "Part name must be at least 2 characters long"
            )
        return value.strip()