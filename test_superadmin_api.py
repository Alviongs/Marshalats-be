#!/usr/bin/env python3

import requests
import json

# API base URL
BASE_URL = "http://31.97.224.169:8003/api"

def test_superadmin_registration():
    """Test super admin registration"""
    admin_data = {
        "full_name": "John Doe",
        "email": "superadmin@example.com",
        "password": "StrongPassword@123",
        "phone": "+919876543210"
    }
    
    print("🔐 Testing Super Admin Registration...")
    print("POST /api/superadmin/register")
    print("Payload:", json.dumps(admin_data, indent=2))
    
    response = requests.post(f"{BASE_URL}/superadmin/register", json=admin_data)
    
    print(f"\n📊 Response Status: {response.status_code}")
    print("Response Body:", response.text)
    
    if response.status_code == 200:
        print("✅ Super admin registration successful!")
        return response.json()
    else:
        print("❌ Super admin registration failed!")
        return None

def test_superadmin_login():
    """Test super admin login"""
    login_data = {
        "email": "superadmin@example.com",
        "password": "StrongPassword@123"
    }
    
    print("\n🔑 Testing Super Admin Login...")
    print("POST /api/superadmin/login")
    print("Payload:", json.dumps(login_data, indent=2))
    
    response = requests.post(f"{BASE_URL}/superadmin/login", json=login_data)
    
    print(f"\n📊 Response Status: {response.status_code}")
    print("Response Body:", response.text)
    
    if response.status_code == 200:
        print("✅ Super admin login successful!")
        return response.json()
    else:
        print("❌ Super admin login failed!")
        return None

def test_superadmin_profile(token):
    """Test getting super admin profile"""
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    print("\n👤 Testing Get Super Admin Profile...")
    print("GET /api/superadmin/me")
    
    response = requests.get(f"{BASE_URL}/superadmin/me", headers=headers)
    
    print(f"\n📊 Response Status: {response.status_code}")
    print("Response Body:", response.text)
    
    if response.status_code == 200:
        print("✅ Profile retrieved successfully!")
        return response.json()
    else:
        print("❌ Profile retrieval failed!")
        return None

def test_token_verification(token):
    """Test token verification"""
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    print("\n🔍 Testing Token Verification...")
    print("GET /api/superadmin/verify-token")
    
    response = requests.get(f"{BASE_URL}/superadmin/verify-token", headers=headers)
    
    print(f"\n📊 Response Status: {response.status_code}")
    print("Response Body:", response.text)
    
    if response.status_code == 200:
        print("✅ Token verification successful!")
        return response.json()
    else:
        print("❌ Token verification failed!")
        return None

def test_duplicate_registration():
    """Test duplicate email registration"""
    admin_data = {
        "full_name": "Jane Doe",
        "email": "superadmin@example.com",  # Same email
        "password": "AnotherPassword@456",
        "phone": "+919876543211"
    }
    
    print("\n🚫 Testing Duplicate Email Registration...")
    response = requests.post(f"{BASE_URL}/superadmin/register", json=admin_data)
    
    print(f"📊 Response Status: {response.status_code}")
    print("Response Body:", response.text)
    
    if response.status_code == 400:
        print("✅ Duplicate email properly rejected!")
    else:
        print("❌ Duplicate email validation failed!")

def main():
    print("🚀 Testing Super Admin Authentication API")
    print("=" * 60)
    
    # Test 1: Register super admin
    registration_result = test_superadmin_registration()
    
    # Test 2: Login super admin
    if registration_result:
        login_result = test_superadmin_login()
        
        if login_result and "data" in login_result and "token" in login_result["data"]:
            token = login_result["data"]["token"]
            
            # Test 3: Get profile
            test_superadmin_profile(token)
            
            # Test 4: Verify token
            test_token_verification(token)
    
    # Test 5: Try duplicate registration
    test_duplicate_registration()
    
    print("\n🎉 Super Admin API testing completed!")

if __name__ == "__main__":
    main()
