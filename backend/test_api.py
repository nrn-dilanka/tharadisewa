#!/usr/bin/env python3
"""
Test script for Customer Management API
Run this script to test all the API endpoints
"""

import requests
import json

# Base URL for the API
BASE_URL = "http://localhost:8000/api"

# Test data
test_customer = {
    "username": "testuser123",
    "email": "test@example.com",
    "password": "testpassword123",
    "password_confirm": "testpassword123",
    "first_name": "Test",
    "last_name": "User",
    "nic": "123456789V"
}

def test_registration():
    """Test customer registration"""
    print("Testing customer registration...")
    url = f"{BASE_URL}/auth/register/"
    response = requests.post(url, json=test_customer)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    
    if response.status_code == 201:
        data = response.json()
        return data['data']['tokens']['access'], data['data']['tokens']['refresh']
    return None, None

def test_login():
    """Test customer login"""
    print("\nTesting customer login...")
    url = f"{BASE_URL}/auth/login/"
    login_data = {
        "username": test_customer["username"],
        "password": test_customer["password"]
    }
    response = requests.post(url, json=login_data)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    
    if response.status_code == 200:
        data = response.json()
        return data['data']['tokens']['access'], data['data']['tokens']['refresh']
    return None, None

def test_profile(access_token):
    """Test getting customer profile"""
    print("\nTesting get profile...")
    url = f"{BASE_URL}/profile/"
    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get(url, headers=headers)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")

def test_update_profile(access_token):
    """Test updating customer profile"""
    print("\nTesting update profile...")
    url = f"{BASE_URL}/profile/"
    headers = {"Authorization": f"Bearer {access_token}"}
    update_data = {
        "first_name": "Updated Test",
        "email": "updated.test@example.com"
    }
    response = requests.put(url, json=update_data, headers=headers)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")

def test_change_password(access_token):
    """Test changing password"""
    print("\nTesting change password...")
    url = f"{BASE_URL}/auth/change-password/"
    headers = {"Authorization": f"Bearer {access_token}"}
    password_data = {
        "old_password": test_customer["password"],
        "new_password": "newpassword123",
        "new_password_confirm": "newpassword123"
    }
    response = requests.post(url, json=password_data, headers=headers)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")

def test_refresh_token(refresh_token):
    """Test refreshing access token"""
    print("\nTesting token refresh...")
    url = f"{BASE_URL}/auth/refresh/"
    refresh_data = {"refresh": refresh_token}
    response = requests.post(url, json=refresh_data)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")

def test_customer_list(access_token):
    """Test getting customer list"""
    print("\nTesting customer list...")
    url = f"{BASE_URL}/customers/"
    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get(url, headers=headers)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")

def test_customer_stats(access_token):
    """Test getting customer statistics"""
    print("\nTesting customer statistics...")
    url = f"{BASE_URL}/stats/"
    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get(url, headers=headers)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")

def test_logout(access_token, refresh_token):
    """Test customer logout"""
    print("\nTesting logout...")
    url = f"{BASE_URL}/auth/logout/"
    headers = {"Authorization": f"Bearer {access_token}"}
    logout_data = {"refresh": refresh_token}
    response = requests.post(url, json=logout_data, headers=headers)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")

def main():
    """Run all tests"""
    print("=== Customer Management API Test Script ===")
    print("Make sure the Django server is running on http://localhost:8000")
    print()
    
    try:
        # Test registration
        access_token, refresh_token = test_registration()
        
        if not access_token:
            # If registration fails (user might already exist), try login
            access_token, refresh_token = test_login()
        
        if access_token:
            # Test profile operations
            test_profile(access_token)
            test_update_profile(access_token)
            
            # Test customer management
            test_customer_list(access_token)
            test_customer_stats(access_token)
            
            # Test token refresh
            test_refresh_token(refresh_token)
            
            # Test password change
            test_change_password(access_token)
            
            # Test logout
            test_logout(access_token, refresh_token)
            
        print("\n=== All tests completed! ===")
        
    except requests.exceptions.ConnectionError:
        print("Error: Could not connect to the API server.")
        print("Please make sure the Django server is running on http://localhost:8000")
        print("Run: python manage.py runserver")
    
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    main()