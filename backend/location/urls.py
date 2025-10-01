from django.urls import path
from . import views

app_name = 'customer_location'

urlpatterns = [
    # Location CRUD operations
    path('locations/', views.CustomerLocationListCreateView.as_view(), name='location_list_create'),
    path('locations/<int:pk>/', views.CustomerLocationDetailView.as_view(), name='location_detail'),
    
    # Shop-specific locations
    path('shops/<int:shop_id>/locations/', views.ShopLocationsView.as_view(), name='shop_locations'),
    
    # Location management
    path('locations/<int:location_id>/set-primary/', views.set_primary_location, name='set_primary_location'),
    path('locations/<int:location_id>/toggle-status/', views.toggle_location_status, name='toggle_location_status'),
    
    # Geographic queries
    path('locations/nearby/', views.NearbyLocationsView.as_view(), name='nearby_locations'),
    path('locations/within-bounds/', views.locations_within_bounds, name='locations_within_bounds'),
    
    # Bulk operations
    path('locations/bulk-create/', views.bulk_create_locations, name='bulk_create_locations'),
    
    # Statistics
    path('locations/stats/', views.location_statistics, name='location_statistics'),
]