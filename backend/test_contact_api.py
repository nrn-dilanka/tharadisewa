#!/usr/bin/env python3
"""
Test script for Customer Contact Management API
Run this script to test all the customer contact API endpoints
"""

import requests
import json

# Base URL for the API
BASE_URL = "http://localhost:8000/api"

# Test data for customer contact
test_contact_data = {
    "customer": 1,  # This will be updated with actual customer ID
    "email": "test.contact@example.com",
    "wa_number": "+94771234567",
    "tp_number": "+94112345678",
    "is_primary": True,
    "is_active": True
}

def get_auth_token():
    """
    Get authentication token by logging in or registering
    """
    # Try to login first
    login_data = {
        "username": "testuser123",
        "password": "testpassword123"
    }
    
    response = requests.post(f"{BASE_URL}/auth/login/", json=login_data)
    
    if response.status_code == 200:
        data = response.json()
        return data['data']['tokens']['access'], data['data']['user']['id']
    
    # If login fails, try to register
    register_data = {
        "username": "testuser123",
        "email": "test@example.com",
        "password": "testpassword123",
        "password_confirm": "testpassword123",
        "first_name": "Test",
        "last_name": "User",
        "nic": "123456789V"
    }
    
    response = requests.post(f"{BASE_URL}/auth/register/", json=register_data)
    
    if response.status_code == 201:
        data = response.json()
        return data['data']['tokens']['access'], data['data']['user']['id']
    
    return None, None

def test_create_contact(access_token, customer_id):
    """Test creating a customer contact"""
    print("Testing create customer contact...")
    url = f"{BASE_URL}/contacts/"
    headers = {"Authorization": f"Bearer {access_token}"}
    
    # Update customer ID in test data
    test_contact_data['customer'] = customer_id
    
    response = requests.post(url, json=test_contact_data, headers=headers)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    
    if response.status_code == 201:
        return response.json()['data']['id']
    return None

def test_list_contacts(access_token):
    """Test listing all contacts"""
    print("\nTesting list all contacts...")
    url = f"{BASE_URL}/contacts/"
    headers = {"Authorization": f"Bearer {access_token}"}
    
    response = requests.get(url, headers=headers)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")

def test_get_contact(access_token, contact_id):
    """Test getting a specific contact"""
    print(f"\nTesting get contact {contact_id}...")
    url = f"{BASE_URL}/contacts/{contact_id}/"
    headers = {"Authorization": f"Bearer {access_token}"}
    
    response = requests.get(url, headers=headers)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")

def test_update_contact(access_token, contact_id):
    """Test updating a contact"""
    print(f"\nTesting update contact {contact_id}...")
    url = f"{BASE_URL}/contacts/{contact_id}/"
    headers = {"Authorization": f"Bearer {access_token}"}
    
    update_data = {
        "email": "updated.contact@example.com",
        "wa_number": "+94771234568",
        "tp_number": "+94112345679",
        "is_primary": False
    }
    
    response = requests.put(url, json=update_data, headers=headers)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")

def test_customer_contacts(access_token, customer_id):
    """Test getting contacts for a specific customer"""
    print(f"\nTesting get contacts for customer {customer_id}...")
    url = f"{BASE_URL}/customers/{customer_id}/contacts/"
    headers = {"Authorization": f"Bearer {access_token}"}
    
    response = requests.get(url, headers=headers)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")

def test_customers_with_contacts(access_token):
    """Test getting all customers with their contacts"""
    print("\nTesting get customers with contacts...")
    url = f"{BASE_URL}/customers-with-contacts/"
    headers = {"Authorization": f"Bearer {access_token}"}
    
    response = requests.get(url, headers=headers)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")

def test_set_primary_contact(access_token, contact_id):
    """Test setting a contact as primary"""
    print(f"\nTesting set contact {contact_id} as primary...")
    url = f"{BASE_URL}/contacts/{contact_id}/set-primary/"
    headers = {"Authorization": f"Bearer {access_token}"}
    
    response = requests.post(url, headers=headers)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")

def test_toggle_contact_status(access_token, contact_id):
    """Test toggling contact active status"""
    print(f"\nTesting toggle status for contact {contact_id}...")
    url = f"{BASE_URL}/contacts/{contact_id}/toggle-status/"
    headers = {"Authorization": f"Bearer {access_token}"}
    
    response = requests.post(url, headers=headers)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")

def test_bulk_create_contacts(access_token, customer_id):
    """Test bulk creating contacts"""
    print("\nTesting bulk create contacts...")
    url = f"{BASE_URL}/contacts/bulk-create/"
    headers = {"Authorization": f"Bearer {access_token}"}
    
    bulk_data = {
        "contacts": [
            {
                "customer": customer_id,
                "email": "bulk1@example.com",
                "wa_number": "+94771234570",
                "tp_number": "+94112345680",
                "is_primary": False,
                "is_active": True
            },
            {
                "customer": customer_id,
                "email": "bulk2@example.com",
                "wa_number": "+94771234571",
                "tp_number": "+94112345681",
                "is_primary": False,
                "is_active": True
            }
        ]
    }
    
    response = requests.post(url, json=bulk_data, headers=headers)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")

def test_contact_statistics(access_token):
    """Test getting contact statistics"""
    print("\nTesting contact statistics...")
    url = f"{BASE_URL}/contacts/stats/"
    headers = {"Authorization": f"Bearer {access_token}"}
    
    response = requests.get(url, headers=headers)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")

def test_search_contacts(access_token):
    """Test searching contacts"""
    print("\nTesting search contacts...")
    url = f"{BASE_URL}/contacts/?search=test"
    headers = {"Authorization": f"Bearer {access_token}"}
    
    response = requests.get(url, headers=headers)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")

def test_filter_contacts(access_token, customer_id):
    """Test filtering contacts"""
    print(f"\nTesting filter contacts for customer {customer_id}...")
    url = f"{BASE_URL}/contacts/?customer_id={customer_id}&is_active=true"
    headers = {"Authorization": f"Bearer {access_token}"}
    
    response = requests.get(url, headers=headers)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")

def test_delete_contact(access_token, contact_id):
    """Test deleting a contact"""
    print(f"\nTesting delete contact {contact_id}...")
    url = f"{BASE_URL}/contacts/{contact_id}/"
    headers = {"Authorization": f"Bearer {access_token}"}
    
    response = requests.delete(url, headers=headers)
    print(f"Status: {response.status_code}")
    if response.status_code != 204:
        print(f"Response: {response.json()}")
    else:
        print("Contact deleted successfully")

def main():
    """Run all tests"""
    print("=== Customer Contact Management API Test Script ===")
    print("Make sure the Django server is running on http://localhost:8000")
    print("Make sure you have run migrations for both customer and customer_contact apps")
    print()
    
    try:
        # Get authentication token and customer ID
        access_token, customer_id = get_auth_token()
        
        if not access_token:
            print("Error: Could not authenticate. Please check the customer registration/login.")
            return
        
        print(f"Authentication successful! Customer ID: {customer_id}")
        print(f"Access Token: {access_token[:50]}...")
        print()
        
        # Test contact creation
        contact_id = test_create_contact(access_token, customer_id)
        
        if contact_id:
            # Test contact operations
            test_get_contact(access_token, contact_id)
            test_update_contact(access_token, contact_id)
            
            # Test customer-specific operations
            test_customer_contacts(access_token, customer_id)
            test_customers_with_contacts(access_token)
            
            # Test contact management
            test_set_primary_contact(access_token, contact_id)
            test_toggle_contact_status(access_token, contact_id)
            
            # Test bulk operations
            test_bulk_create_contacts(access_token, customer_id)
            
            # Test listing and filtering
            test_list_contacts(access_token)
            test_search_contacts(access_token)
            test_filter_contacts(access_token, customer_id)
            
            # Test statistics
            test_contact_statistics(access_token)
            
            # Test deletion (comment out if you want to keep test data)
            # test_delete_contact(access_token, contact_id)
        
        print("\n=== All customer contact tests completed! ===")
        
    except requests.exceptions.ConnectionError:
        print("Error: Could not connect to the API server.")
        print("Please make sure the Django server is running on http://localhost:8000")
        print("Run: python manage.py runserver")
    
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    main()