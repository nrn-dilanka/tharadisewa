from django.urls import path
from . import views

app_name = 'shop'

urlpatterns = [
    # Shop CRUD operations
    path('shops/', views.ShopListCreateView.as_view(), name='shop_list_create'),
    path('shops/<int:pk>/', views.ShopDetailView.as_view(), name='shop_detail'),
    
    # Customer-specific shops
    path('customers/<int:customer_id>/shops/', views.CustomerShopsView.as_view(), name='customer_shops'),
    path('customers-with-shops/', views.CustomersWithShopsView.as_view(), name='customers_with_shops'),
    
    # Shops with locations
    path('shops-with-locations/', views.ShopsWithLocationsView.as_view(), name='shops_with_locations'),
    
    # Shop management
    path('shops/<int:shop_id>/toggle-status/', views.toggle_shop_status, name='toggle_shop_status'),
    
    # Location-based queries
    path('shops/city/<str:city_name>/', views.shops_by_city, name='shops_by_city'),
    path('shops/postal-code/<str:postal_code>/', views.shops_by_postal_code, name='shops_by_postal_code'),
    
    # Bulk operations
    path('shops/bulk-create/', views.bulk_create_shops, name='bulk_create_shops'),
    
    # Statistics
    path('shops/stats/', views.shop_statistics, name='shop_statistics'),
]