from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .auth_views import (
    CustomTokenObtainPairView,
    login_view,
    logout_view,
    verify_token_view,
    register_view,
    admin_create_user_view,
    admin_update_user_view,
    check_registration_status_view
)
from .test_views import test_connection, health_check

app_name = 'auth'

urlpatterns = [
    # JWT Token endpoints
    path('token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # Authentication endpoints
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('register/', register_view, name='register'),
    path('verify/', verify_token_view, name='verify_token'),
    
    # Admin user management endpoints
    path('admin/create-user/', admin_create_user_view, name='admin_create_user'),
    path('admin/update-user/<int:user_id>/', admin_update_user_view, name='admin_update_user'),
    path('registration-status/', check_registration_status_view, name='registration_status'),
    
    # Test endpoints
    path('test-connection/', test_connection, name='test_connection'),
    path('health/', health_check, name='health_check'),
]