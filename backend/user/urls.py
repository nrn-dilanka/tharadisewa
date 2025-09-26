from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserViewSet

# Create router and register viewsets
router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')

app_name = 'user'

urlpatterns = [
    # API endpoints
    path('api/', include(router.urls)),
]

# Available API endpoints:
# GET /api/users/ - List all users (with filtering, search, pagination)
# POST /api/users/ - Create new user (registration)
# GET /api/users/{id}/ - Get user details
# PUT /api/users/{id}/ - Update user (full update)
# PATCH /api/users/{id}/ - Update user (partial update)
# DELETE /api/users/{id}/ - Delete user

# Profile management:
# GET /api/users/profile/ - Get current user's profile
# PUT /api/users/profile/ - Update current user's profile
# PATCH /api/users/profile/ - Partial update current user's profile
# POST /api/users/change_password/ - Change current user's password

# User management (admin/staff):
# GET /api/users/staff/ - Get all staff users
# GET /api/users/customers/ - Get all customer users
# GET /api/users/statistics/ - Get user statistics (admin only)
# GET /api/users/export/ - Export users to CSV (admin only)

# User actions:
# PATCH /api/users/{id}/update_role/ - Update user role (admin/manager)
# POST /api/users/{id}/activate/ - Activate user account
# POST /api/users/{id}/deactivate/ - Deactivate user account
# POST /api/users/{id}/verify/ - Verify user account

# Bulk operations:
# POST /api/users/bulk_operations/ - Bulk operations on users (admin only)