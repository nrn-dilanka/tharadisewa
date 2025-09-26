from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import LicenseViewSet

# Create router and register viewsets
router = DefaultRouter()
router.register(r'licenses', LicenseViewSet, basename='license')

app_name = 'license'

urlpatterns = [
    # API endpoints
    path('api/', include(router.urls)),
]

# Available API endpoints:
# GET /api/licenses/ - List all licenses (with filtering, search, pagination)
# POST /api/licenses/ - Create new license
# GET /api/licenses/{id}/ - Get license details
# PUT /api/licenses/{id}/ - Update license (full update)
# PATCH /api/licenses/{id}/ - Update license (partial update)
# DELETE /api/licenses/{id}/ - Delete license

# Custom endpoints:
# GET /api/licenses/active/ - Get active licenses
# GET /api/licenses/expired/ - Get expired licenses
# GET /api/licenses/expiring_soon/ - Get licenses expiring soon
# GET /api/licenses/dashboard/ - Get dashboard data
# GET /api/licenses/statistics/ - Get license statistics
# GET /api/licenses/export/ - Export licenses to CSV

# License-specific actions:
# POST /api/licenses/{id}/activate/ - Activate license
# POST /api/licenses/{id}/suspend/ - Suspend license
# POST /api/licenses/{id}/revoke/ - Revoke license
# POST /api/licenses/{id}/renew/ - Renew license
# POST /api/licenses/{id}/update_usage/ - Update usage data
# GET /api/licenses/{id}/summary/ - Get license summary
# POST /api/licenses/{id}/add_feature/ - Add feature to license
# POST /api/licenses/{id}/remove_feature/ - Remove feature from license

# Bulk operations:
# POST /api/licenses/bulk_operations/ - Bulk operations on licenses
# POST /api/licenses/activate_by_key/ - Activate license by key