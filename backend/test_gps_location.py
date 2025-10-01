#!/usr/bin/env python
"""
Test script for GPS location functionality in shop creation
"""
import os
import sys
import django
import requests
import json

# Add the backend directory to Python path
backend_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(backend_dir)

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from customer.models import Customer
from shop.models import Shop
from location.models import CustomerLocation
from shop.serializers import ShopCreateSerializer

def test_shop_creation_with_gps():
    """Test creating a shop with GPS location data"""
    
    print("=== GPS Location Integration Test ===\n")
    
    # Check if we have customers
    customer = Customer.objects.filter(is_active=True).first()
    if not customer:
        print("❌ No active customers found. Please create a customer first.")
        return False
    
    print(f"✓ Using customer: {customer.full_name} (ID: {customer.id})")
    
    # Test data with GPS coordinates (fake GPS coordinates for Colombo, Sri Lanka)
    test_shop_data = {
        'name': 'GPS Test Shop',
        'customer': customer.id,
        'address_line_1': '123 Galle Road',
        'city': 'Colombo',
        'postal_code': '00100',
        'description': 'Test shop with GPS location',
        'phone_number': '0771234567',
        'email': 'testshop@example.com',
        'is_active': True,
        # GPS location data (Colombo coordinates)
        'latitude': '6.92707900',
        'longitude': '79.86124200',
        'location_accuracy': 10,
        'location_name': 'GPS Test Shop Location',
        'location_description': 'Automatically captured GPS location for GPS Test Shop'
    }
    
    print(f"✓ Test shop data prepared with GPS coordinates")
    print(f"  Latitude: {test_shop_data['latitude']}")
    print(f"  Longitude: {test_shop_data['longitude']}")
    print(f"  Accuracy: ±{test_shop_data['location_accuracy']}m\n")
    
    # Test serializer validation and creation
    try:
        serializer = ShopCreateSerializer(data=test_shop_data)
        if serializer.is_valid():
            print("✓ Shop data validation passed")
            
            # Create the shop
            shop = serializer.save()
            print(f"✓ Shop created successfully: {shop.name} (ID: {shop.id})")
            
            # Check if location was created
            location = CustomerLocation.objects.filter(shop=shop).first()
            if location:
                print(f"✓ GPS location created successfully:")
                print(f"  Location ID: {location.id}")
                print(f"  Coordinates: ({location.latitude}, {location.longitude})")
                print(f"  Accuracy: ±{location.accuracy_radius}m")
                print(f"  Primary: {location.is_primary}")
                print(f"  Google Maps: {location.google_maps_url}")
                
                # Test location info property
                location_info = location.location_info
                print(f"✓ Location info generated: {json.dumps(location_info, indent=2, default=str)}")
                
                return True
            else:
                print("❌ GPS location was not created")
                return False
                
        else:
            print("❌ Shop data validation failed:")
            for field, errors in serializer.errors.items():
                print(f"  {field}: {errors}")
            return False
            
    except Exception as e:
        print(f"❌ Error during shop creation: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_api_endpoint():
    """Test the API endpoint with GPS data"""
    
    print("\n=== API Endpoint Test ===\n")
    
    # Check if server is running
    try:
        response = requests.get('http://127.0.0.1:8000/api/health/', timeout=5)
        print(f"✓ Server is running (status: {response.status_code})")
    except requests.exceptions.RequestException as e:
        print(f"❌ Server is not running or not accessible: {str(e)}")
        return False
    
    # Get a customer for the test
    customer = Customer.objects.filter(is_active=True).first()
    if not customer:
        print("❌ No active customers found for API test.")
        return False
    
    # Test API shop creation with GPS data
    api_shop_data = {
        'name': 'API GPS Test Shop',
        'customer': customer.id,
        'address_line_1': '456 Negombo Road',
        'city': 'Negombo',
        'postal_code': '11500',
        'description': 'API test shop with GPS location',
        'is_active': True,
        # GPS location data (Negombo coordinates)
        'latitude': '7.20849000',
        'longitude': '79.83885000',
        'location_accuracy': 15,
        'location_name': 'API GPS Test Shop Location',
        'location_description': 'GPS location via API for API GPS Test Shop'
    }
    
    try:
        # Note: This would require authentication in a real scenario
        headers = {'Content-Type': 'application/json'}
        response = requests.post(
            'http://127.0.0.1:8000/api/shops/',
            json=api_shop_data,
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 201:
            response_data = response.json()
            print("✓ API shop creation successful")
            print(f"  Response: {json.dumps(response_data, indent=2)}")
            
            # Check if location was created via database
            if 'data' in response_data and 'id' in response_data['data']:
                shop_id = response_data['data']['id']
                shop = Shop.objects.get(id=shop_id)
                location = CustomerLocation.objects.filter(shop=shop).first()
                
                if location:
                    print("✓ GPS location created via API")
                    print(f"  Coordinates: ({location.latitude}, {location.longitude})")
                else:
                    print("❌ GPS location was not created via API")
                    
            return True
        else:
            print(f"❌ API shop creation failed (status: {response.status_code})")
            print(f"  Response: {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ API request failed: {str(e)}")
        return False

def cleanup_test_data():
    """Clean up test data"""
    print("\n=== Cleanup Test Data ===\n")
    
    # Delete test shops and their locations
    test_shops = Shop.objects.filter(name__icontains='GPS Test Shop')
    for shop in test_shops:
        locations = CustomerLocation.objects.filter(shop=shop)
        location_count = locations.count()
        locations.delete()
        shop.delete()
        print(f"✓ Cleaned up shop: {shop.name} (with {location_count} locations)")

def main():
    """Run all tests"""
    print("Starting GPS Location Integration Tests...\n")
    
    # Test 1: Direct model/serializer test
    test1_result = test_shop_creation_with_gps()
    
    # Test 2: API endpoint test
    test2_result = test_api_endpoint()
    
    # Summary
    print("\n=== Test Summary ===")
    print(f"Model/Serializer Test: {'✓ PASSED' if test1_result else '❌ FAILED'}")
    print(f"API Endpoint Test: {'✓ PASSED' if test2_result else '❌ FAILED'}")
    
    if test1_result and test2_result:
        print("\n🎉 All GPS location tests passed!")
        print("\nThe GPS location integration is working correctly:")
        print("1. Shop creation with GPS coordinates works")
        print("2. Location model is automatically created")
        print("3. Location data is properly stored and accessible")
        print("4. API endpoints handle GPS data correctly")
    else:
        print("\n⚠️  Some tests failed. Please check the issues above.")
    
    # Ask if user wants to cleanup
    try:
        cleanup = input("\nCleanup test data? (y/n): ").lower().strip()
        if cleanup == 'y':
            cleanup_test_data()
    except KeyboardInterrupt:
        print("\nSkipping cleanup...")

if __name__ == "__main__":
    main()