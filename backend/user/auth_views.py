from rest_framework import status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth import authenticate
from user.serializers import UserDetailSerializer
from user.models import User
from user.permissions import IsAdminUser


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Custom JWT token serializer to include user data
    """
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        
        # Add custom claims
        token['user_id'] = user.id
        token['username'] = user.username
        token['role'] = user.role
        
        return token
    
    def validate(self, attrs):
        data = super().validate(attrs)
        
        # Add user data to response
        data['user'] = UserDetailSerializer(self.user).data
        
        return data


class CustomTokenObtainPairView(TokenObtainPairView):
    """
    Custom JWT token view
    """
    serializer_class = CustomTokenObtainPairSerializer


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def login_view(request):
    """
    Login endpoint that returns JWT tokens and user data
    """
    username = request.data.get('username')
    password = request.data.get('password')
    
    if not username or not password:
        return Response(
            {'message': 'Username and password are required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    user = authenticate(username=username, password=password)
    
    if user:
        if not user.is_active:
            return Response(
                {'message': 'Account is disabled'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)
        access = refresh.access_token
        
        # Add custom claims to access token
        access['user_id'] = user.id
        access['username'] = user.username
        access['role'] = user.role
        
        return Response({
            'access': str(access),
            'refresh': str(refresh),
            'user': UserDetailSerializer(user).data,
            'message': 'Login successful'
        }, status=status.HTTP_200_OK)
    
    return Response(
        {'message': 'Invalid credentials'},
        status=status.HTTP_401_UNAUTHORIZED
    )


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def logout_view(request):
    """
    Logout endpoint that blacklists the refresh token
    """
    try:
        refresh_token = request.data.get('refresh')
        if refresh_token:
            token = RefreshToken(refresh_token)
            token.blacklist()
        
        return Response(
            {'message': 'Logout successful'},
            status=status.HTTP_200_OK
        )
    except Exception as e:
        return Response(
            {'message': 'Logout failed'},
            status=status.HTTP_400_BAD_REQUEST
        )


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def verify_token_view(request):
    """
    Verify if the current token is valid and return user data
    """
    user = request.user
    return Response({
        'valid': True,
        'user': UserDetailSerializer(user).data
    }, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def register_view(request):
    """
    Register endpoint - Only allows registration if no admin exists
    First user becomes admin automatically
    """
    from user.serializers import UserCreateSerializer
    
    # Check if any admin already exists
    admin_exists = User.objects.filter(role='admin').exists()
    
    # If admin exists, don't allow new registrations
    if admin_exists:
        return Response({
            'message': 'Registration is disabled. Please contact administrator for account creation.',
            'error': 'REGISTRATION_DISABLED'
        }, status=status.HTTP_403_FORBIDDEN)
    
    # First user registration - will become admin
    serializer = UserCreateSerializer(data=request.data)
    if serializer.is_valid():
        # Create user with admin role if no admin exists
        user = serializer.save(role='admin')
        user.is_verified = True  # Auto-verify admin
        user.save()
        
        # Generate JWT tokens for the new admin
        refresh = RefreshToken.for_user(user)
        access = refresh.access_token
        
        # Add custom claims
        access['user_id'] = user.id
        access['username'] = user.username
        access['role'] = user.role
        
        return Response({
            'access': str(access),
            'refresh': str(refresh),
            'user': UserDetailSerializer(user).data,
            'message': 'Admin account created successfully. You are now the system administrator.',
            'is_first_admin': True
        }, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAdminUser])
def admin_create_user_view(request):
    """
    Admin endpoint to create new users
    Only admins can access this endpoint
    """
    from user.serializers import UserCreateSerializer
    
    serializer = UserCreateSerializer(data=request.data)
    if serializer.is_valid():
        # Admin can create users with any role except admin (to prevent multiple admins)
        role = request.data.get('role', 'customer')
        if role == 'admin':
            return Response({
                'message': 'Cannot create additional admin users',
                'error': 'ADMIN_CREATION_DENIED'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        user = serializer.save()
        
        return Response({
            'user': UserDetailSerializer(user).data,
            'message': f'User created successfully with role: {user.get_role_display()}'
        }, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PATCH', 'PUT'])
@permission_classes([IsAdminUser])
def admin_update_user_view(request, user_id):
    """
    Admin endpoint to update existing users
    Only admins can access this endpoint
    """
    from user.serializers import AdminUserUpdateSerializer
    
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return Response({
            'message': 'User not found',
            'error': 'USER_NOT_FOUND'
        }, status=status.HTTP_404_NOT_FOUND)
    
    # Prevent admin from changing their own role to avoid lockout
    if user == request.user and 'role' in request.data:
        current_role = user.role
        new_role = request.data.get('role')
        if current_role == 'admin' and new_role != 'admin':
            return Response({
                'message': 'Cannot change your own admin role',
                'error': 'SELF_ROLE_CHANGE_DENIED'
            }, status=status.HTTP_400_BAD_REQUEST)
    
    # Prevent creation of additional admin users
    if 'role' in request.data and request.data['role'] == 'admin' and user.role != 'admin':
        return Response({
            'message': 'Cannot promote users to admin role',
            'error': 'ADMIN_PROMOTION_DENIED'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    serializer = AdminUserUpdateSerializer(
        user, 
        data=request.data, 
        partial=(request.method == 'PATCH')
    )
    
    if serializer.is_valid():
        updated_user = serializer.save()
        
        return Response({
            'user': UserDetailSerializer(updated_user).data,
            'message': f'User updated successfully'
        }, status=status.HTTP_200_OK)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def check_registration_status_view(request):
    """
    Check if registration is available (i.e., no admin exists yet)
    """
    admin_exists = User.objects.filter(role='admin').exists()
    
    return Response({
        'registration_enabled': not admin_exists,
        'admin_exists': admin_exists,
        'message': 'Admin already exists' if admin_exists else 'Registration available for first admin'
    }, status=status.HTTP_200_OK)