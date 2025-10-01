from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CustomerViewSet

# Create router and register viewsets
router = DefaultRouter()
router.register(r'customers', CustomerViewSet, basename='customer')

app_name = 'customer'

urlpatterns = [
    # API endpoints - removed extra /api/ prefix since it's already in main urls.py
    path('', include(router.urls)),
]

# Available API endpoints:
# GET /api/customers/ - List all customers (with filtering, search, pagination)
# POST /api/customers/ - Create new customer (registration)
# GET /api/customers/{id}/ - Get customer details
# PUT /api/customers/{id}/ - Update customer (full update)
# PATCH /api/customers/{id}/ - Update customer (partial update)
# DELETE /api/customers/{id}/ - Delete customer

# Custom endpoints:
# GET /api/customers/statistics/ - Get customer statistics
# GET /api/customers/verified/ - Get verified customers
# GET /api/customers/unverified/ - Get unverified customers
# GET /api/customers/with_accounts/ - Get customers with user accounts
# GET /api/customers/without_accounts/ - Get customers without user accounts
# GET /api/customers/export/ - Export customers to CSV

# Customer actions:
# POST /api/customers/{id}/create_user_account/ - Create user account for customer
# POST /api/customers/{id}/verify/ - Verify/unverify customer
# POST /api/customers/{id}/activate/ - Activate/deactivate customer

# Bulk operations:
# POST /api/customers/bulk_operations/ - Bulk operations on customers