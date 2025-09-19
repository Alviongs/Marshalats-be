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

def test_correct_branch_creation(token):
    """Test branch creation with CORRECT payload format"""
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # CORRECT payload format for POST /api/branches
    correct_payload = {
        "branch": {
            "name": "Rock martial arts",
            "code": "RMA01",
            "email": "yourname@email.com",
            "phone": "+13455672356",
            "address": {
                "line1": "928#123",
                "area": "Madhapur",
                "city": "Hyderabad",
                "state": "Telangana",
                "pincode": "500089",
                "country": "India"
            }
        },
        "manager_id": "manager-uuid-1234",
        "operational_details": {
            "courses_offered": ["Rock martial arts"],
            "timings": [
                { "day": "Monday", "open": "07:00", "close": "19:00" },
                { "day": "Tuesday", "open": "07:00", "close": "19:00" }
            ],
            "holidays": ["2025-10-02", "2025-12-25"]
        },
        "assignments": {
            "accessories_available": True,
            "courses": ["course-uuid-1", "course-uuid-2", "course-uuid-3"],
            "branch_admins": ["coach-uuid-1", "coach-uuid-2"]
        },
        "bank_details": {
            "bank_name": "State Bank of India",
            "account_number": "XXXXXXXXXXXX",
            "upi_id": "name@ybl"
        }
    }
    
    print("\n🏢 Testing CORRECT branch creation...")
    print("POST /api/branches")
    print("CORRECT Payload Structure:")
    print(json.dumps(correct_payload, indent=2))
    
    response = requests.post(f"{BASE_URL}/branches", json=correct_payload, headers=headers)
    
    print(f"\n📊 Response Status: {response.status_code}")
    print("Response Body:", response.text)
    
    if response.status_code == 200:
        print("✅ Branch creation successful!")
        return response.json()
    else:
        print("❌ Branch creation failed!")
        return None

def show_wrong_format():
    """Show the WRONG format that causes the error"""
    wrong_payload = {
        "branches": [
            {
                "id": "branch-uuid",
                "branch": {
                    "name": "Rock martial arts",
                    "code": "RMA01",
                    # ... rest
                }
                # This is GET response format, NOT POST request format!
            }
        ]
    }
    
    print("\n❌ WRONG FORMAT (This is what you were sending):")
    print("This is the GET response format, not the POST request format!")
    print(json.dumps(wrong_payload, indent=2))

def main():
    print("🚀 Branch Creation - Correct vs Wrong Format")
    print("=" * 60)
    
    # Show wrong format first
    show_wrong_format()
    
    # Get authentication token
    token = get_token()
    if not token:
        return
    
    # Test with correct format
    test_correct_branch_creation(token)

if __name__ == "__main__":
    main()
