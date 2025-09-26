from django.urls import path
from . import views

app_name = 'customer_contact'

urlpatterns = [
    # Contact CRUD operations
    path('contacts/', views.CustomerContactListCreateView.as_view(), name='contact_list_create'),
    path('contacts/<int:pk>/', views.CustomerContactDetailView.as_view(), name='contact_detail'),
    
    # Customer-specific contacts
    path('customers/<int:customer_id>/contacts/', views.CustomerContactsByCustomerView.as_view(), name='customer_contacts'),
    path('customers-with-contacts/', views.CustomerWithContactsListView.as_view(), name='customers_with_contacts'),
    
    # Contact management
    path('contacts/<int:contact_id>/set-primary/', views.set_primary_contact, name='set_primary_contact'),
    path('contacts/<int:contact_id>/toggle-status/', views.toggle_contact_status, name='toggle_contact_status'),
    
    # Bulk operations
    path('contacts/bulk-create/', views.bulk_create_contacts, name='bulk_create_contacts'),
    
    # Statistics
    path('contacts/stats/', views.contact_statistics, name='contact_statistics'),
]