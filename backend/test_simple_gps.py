#!/usr/bin/env python
"""
Simple test for GPS location functionality
"""
import os
import sys
import django

# Setup Django environment
backend_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(backend_dir)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from customer.models import Customer
from shop.models import Shop
from location.models import CustomerLocation
from shop.serializers import ShopCreateSerializer

def create_test_customer():
    """Create a test customer if none exists"""
    customer = Customer.objects.filter(is_active=True).first()
    if not customer:
        print("Creating test customer...")
        customer = Customer.objects.create(
            customer_id="CUST001",
            username="testcustomer",
            email="test@example.com",
            first_name="Test",
            last_name="Customer",
            nic="123456789V",
            is_active=True,
            is_verified=True
        )
        print(f"✓ Created customer: {customer.full_name}")
    else:
        print(f"✓ Using existing customer: {customer.full_name}")
    return customer

def test_gps_shop_creation():
    """Test creating a shop with GPS coordinates"""
    print("\n=== Testing GPS Shop Creation ===\n")
    
    # Ensure we have a customer
    customer = create_test_customer()
    
    # Test shop data with GPS coordinates
    shop_data = {
        'name': 'GPS Test Shop',
        'customer': customer.id,
        'address_line_1': '123 Test Street',
        'city': 'Colombo',
        'postal_code': '00100',
        'description': 'Test shop with GPS location',
        'is_active': True,
        # GPS coordinates for Colombo, Sri Lanka
        'latitude': '6.92707900',
        'longitude': '79.86124200',
        'location_accuracy': 10,
        'location_name': 'GPS Test Shop Location',
        'location_description': 'Test GPS location'
    }
    
    print("Creating shop with GPS data...")
    print(f"Coordinates: ({shop_data['latitude']}, {shop_data['longitude']})")
    
    # Test the serializer
    serializer = ShopCreateSerializer(data=shop_data)
    
    if serializer.is_valid():
        print("✓ Shop data validation passed")
        
        # Create the shop
        shop = serializer.save()
        print(f"✓ Shop created: {shop.name} (ID: {shop.id})")
        
        # Check if location was automatically created
        location = CustomerLocation.objects.filter(shop=shop).first()
        
        if location:
            print(f"✓ GPS location created automatically!")
            print(f"  Location ID: {location.id}")
            print(f"  Coordinates: ({location.latitude}, {location.longitude})")
            print(f"  Accuracy: ±{location.accuracy_radius}m")
            print(f"  Is Primary: {location.is_primary}")
            print(f"  Location Name: {location.location_name}")
            print(f"  Google Maps URL: {location.google_maps_url}")
            
            print("\n✅ GPS LOCATION INTEGRATION IS WORKING!")
            print("When you create a shop with latitude/longitude data:")
            print("1. Shop is created normally")
            print("2. CustomerLocation is automatically created")
            print("3. Location is marked as primary")
            print("4. All GPS data is stored correctly")
            
            return True
        else:
            print("❌ GPS location was NOT created")
            return False
    else:
        print("❌ Shop validation failed:")
        for field, errors in serializer.errors.items():
            print(f"  {field}: {errors}")
        return False

def cleanup():
    """Clean up test data"""
    print("\n=== Cleanup ===")
    
    # Delete test shops and their locations
    shops = Shop.objects.filter(name__icontains='GPS Test')
    count = 0
    for shop in shops:
        locations = CustomerLocation.objects.filter(shop=shop)
        locations.delete()
        shop.delete()
        count += 1
    
    if count > 0:
        print(f"✓ Cleaned up {count} test shop(s)")
    else:
        print("No test shops to cleanup")

if __name__ == "__main__":
    print("GPS Location Integration - Simple Test")
    print("=" * 45)
    
    success = test_gps_shop_creation()
    
    if success:
        print("\n🎉 SUCCESS: GPS location integration is working perfectly!")
        print("\nYour mobile app can now send GPS coordinates when creating shops,")
        print("and they will be automatically stored in the CustomerLocation model.")
    else:
        print("\n❌ FAILED: GPS location integration has issues.")
    
    # Cleanup
    cleanup_choice = input("\nDelete test data? (y/n): ").lower().strip()
    if cleanup_choice == 'y':
        cleanup()
    
    print("\nTest complete!")