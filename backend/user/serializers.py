from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth import authenticate
from .models import User


class UserCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating a new user
    """
    password = serializers.CharField(
        write_only=True,
        validators=[validate_password],
        style={'input_type': 'password'}
    )
    password_confirm = serializers.CharField(
        write_only=True,
        style={'input_type': 'password'}
    )
    
    class Meta:
        model = User
        fields = [
            'username', 'email', 'first_name', 'last_name', 'phone_number',
            'role', 'date_of_birth', 'address', 'password', 'password_confirm'
        ]
    
    def validate(self, attrs):
        """
        Validate that passwords match
        """
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError("Passwords don't match")
        return attrs
    
    def create(self, validated_data):
        """
        Create user with encrypted password
        """
        validated_data.pop('password_confirm')
        password = validated_data.pop('password')
        
        user = User.objects.create_user(
            password=password,
            **validated_data
        )
        return user


class UserUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating user information
    """
    
    class Meta:
        model = User
        fields = [
            'first_name', 'last_name', 'email', 'phone_number',
            'date_of_birth', 'address', 'profile_image', 'is_verified'
        ]
        read_only_fields = ['username']


class UserDetailSerializer(serializers.ModelSerializer):
    """
    Detailed serializer for user information
    """
    full_name = serializers.CharField(read_only=True)
    permissions_list = serializers.SerializerMethodField()
    dashboard_url = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name', 'full_name',
            'phone_number', 'role', 'date_of_birth', 'address', 'profile_image',
            'is_verified', 'is_active', 'is_staff', 'date_joined', 'last_login',
            'permissions_list', 'dashboard_url', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'username', 'date_joined', 'last_login', 'created_at', 'updated_at'
        ]
    
    def get_permissions_list(self, obj):
        """Get user's permissions based on role"""
        return obj.get_permissions_list()
    
    def get_dashboard_url(self, obj):
        """Get appropriate dashboard URL"""
        return obj.get_dashboard_url()


class UserListSerializer(serializers.ModelSerializer):
    """
    Serializer for user list view
    """
    full_name = serializers.CharField(read_only=True)
    
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'full_name', 'phone_number',
            'role', 'is_verified', 'is_active', 'date_joined'
        ]


class UserProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for user's own profile
    """
    full_name = serializers.CharField(read_only=True)
    
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name', 'full_name',
            'phone_number', 'date_of_birth', 'address', 'profile_image',
            'role', 'is_verified', 'date_joined', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'username', 'role', 'is_verified', 'date_joined', 
            'created_at', 'updated_at'
        ]


class ChangePasswordSerializer(serializers.Serializer):
    """
    Serializer for changing user password
    """
    old_password = serializers.CharField(
        write_only=True,
        style={'input_type': 'password'}
    )
    new_password = serializers.CharField(
        write_only=True,
        validators=[validate_password],
        style={'input_type': 'password'}
    )
    new_password_confirm = serializers.CharField(
        write_only=True,
        style={'input_type': 'password'}
    )
    
    def validate_old_password(self, value):
        """
        Validate that old password is correct
        """
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("Old password is incorrect")
        return value
    
    def validate(self, attrs):
        """
        Validate that new passwords match
        """
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError("New passwords don't match")
        return attrs


class UserLoginSerializer(serializers.Serializer):
    """
    Serializer for user login
    """
    username = serializers.CharField()
    password = serializers.CharField(
        write_only=True,
        style={'input_type': 'password'}
    )
    
    def validate(self, attrs):
        """
        Validate username and password
        """
        username = attrs.get('username')
        password = attrs.get('password')
        
        if username and password:
            user = authenticate(username=username, password=password)
            if user:
                if not user.is_active:
                    raise serializers.ValidationError("User account is disabled")
                attrs['user'] = user
                return attrs
            else:
                raise serializers.ValidationError("Invalid username or password")
        else:
            raise serializers.ValidationError("Must include username and password")


class UserRoleUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating user role (admin only)
    """
    
    class Meta:
        model = User
        fields = ['role', 'is_active', 'is_staff', 'is_verified']
    
    def validate_role(self, value):
        """
        Validate role assignment permissions
        """
        request_user = self.context['request'].user
        
        # Only admins can assign admin role
        if value == 'admin' and not request_user.is_admin():
            raise serializers.ValidationError("Only admins can assign admin role")
        
        # Only admins and managers can assign manager role
        if value == 'manager' and not (request_user.is_admin() or request_user.is_manager()):
            raise serializers.ValidationError("Insufficient permissions to assign manager role")
        
        return value


class UserStatsSerializer(serializers.Serializer):
    """
    Serializer for user statistics
    """
    total_users = serializers.IntegerField()
    active_users = serializers.IntegerField()
    verified_users = serializers.IntegerField()
    staff_users = serializers.IntegerField()
    
    # Role breakdown
    admin_count = serializers.IntegerField()
    manager_count = serializers.IntegerField()
    staff_count = serializers.IntegerField()
    customer_count = serializers.IntegerField()
    technician_count = serializers.IntegerField()
    sales_count = serializers.IntegerField()
    support_count = serializers.IntegerField()
    
    # Time-based stats
    new_users_today = serializers.IntegerField()
    new_users_this_week = serializers.IntegerField()
    new_users_this_month = serializers.IntegerField()


class UserExportSerializer(serializers.ModelSerializer):
    """
    Serializer for exporting user data
    """
    full_name = serializers.CharField(read_only=True)
    role_display = serializers.CharField(source='get_role_display', read_only=True)
    
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name', 'full_name',
            'phone_number', 'role', 'role_display', 'date_of_birth', 'address',
            'is_verified', 'is_active', 'is_staff', 'is_superuser',
            'date_joined', 'last_login', 'created_at', 'updated_at'
        ]