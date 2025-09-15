#!/usr/bin/env python3

import requests
import json

# API base URL
BASE_URL = "http://localhost:8003/api"

def get_token():
    """Get authentication token"""
    login_data = {
        "email": "superadmin@test.com",
        "password": "SuperAdmin123!"
    }
    
    print("🔐 Logging in as super admin...")
    response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
    
    if response.status_code == 200:
        token = response.json()["access_token"]
        print("✅ Login successful!")
        return token
    else:
        print(f"❌ Login failed: {response.status_code}")
        print("Response:", response.text)
        return None

def test_branch_creation(token):
    """Test branch creation API"""
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # Test branch data
    branch_data = {
        "branch": {
            "name": "Test Martial Arts Center",
            "code": "TMAC01",
            "email": "test@martialarts.com",
            "phone": "+1234567890",
            "address": {
                "line1": "123 Test Street",
                "area": "Test Area",
                "city": "Test City",
                "state": "Test State",
                "pincode": "123456",
                "country": "India"
            }
        },
        "manager_id": "test-manager-uuid-123",
        "operational_details": {
            "courses_offered": ["Karate", "Taekwondo"],
            "timings": [
                {"day": "Monday", "open": "09:00", "close": "18:00"},
                {"day": "Tuesday", "open": "09:00", "close": "18:00"}
            ],
            "holidays": ["2025-12-25", "2025-01-01"]
        },
        "assignments": {
            "accessories_available": True,
            "courses": ["course-uuid-1", "course-uuid-2"],
            "branch_admins": ["admin-uuid-1"]
        },
        "bank_details": {
            "bank_name": "Test Bank",
            "account_number": "1234567890",
            "upi_id": "test@upi"
        }
    }
    
    print("\n🏢 Testing branch creation...")
    print("POST /api/branches")
    print("Payload:", json.dumps(branch_data, indent=2))
    
    response = requests.post(f"{BASE_URL}/branches", json=branch_data, headers=headers)
    
    print(f"\n📊 Response Status: {response.status_code}")
    print("Response Headers:", dict(response.headers))
    print("Response Body:", response.text)
    
    if response.status_code == 200:
        print("✅ Branch creation successful!")
        return response.json()
    else:
        print("❌ Branch creation failed!")
        return None

def test_get_branches(token):
    """Test getting branches to see what's happening"""
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    print("\n📋 Testing GET branches...")
    response = requests.get(f"{BASE_URL}/branches", headers=headers)
    
    print(f"📊 Response Status: {response.status_code}")
    print("Response Body:", response.text)

def main():
    print("🚀 Testing Branch Creation API")
    print("=" * 50)
    
    # Get authentication token
    token = get_token()
    if not token:
        return
    
    # Test branch creation
    result = test_branch_creation(token)
    
    # Test getting branches
    test_get_branches(token)

if __name__ == "__main__":
    main()
