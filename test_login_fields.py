#!/usr/bin/env python3
"""
Test login endpoint to see if date_of_birth and gender are returned
"""
import requests
import json

def test_login():
    """Test the /api/auth/login endpoint"""
    
    # First, register a new user with known credentials
    register_url = "http://localhost:8003/api/auth/register"
    register_data = {
        "email": "testlogin@example.com",
        "phone": "+1555555555",
        "full_name": "Test Login User",
        "role": "student",
        "branch_id": "test-branch-login",
        "password": "testpassword123",
        "date_of_birth": "1990-12-25",
        "gender": "male",
        "biometric_id": "login-test-fingerprint"
    }
    
    print("Registering test user...")
    register_response = requests.post(register_url, json=register_data)
    print(f"Registration: {register_response.status_code} - {register_response.text}")
    
    if register_response.status_code == 200 or register_response.status_code == 400:
        # Now test login
        login_url = "http://localhost:8003/api/auth/login"
        login_data = {
            "email": "testlogin@example.com",
            "password": "testpassword123"
        }
        
        print(f"\nTesting login...")
        print(f"Login URL: {login_url}")
        print(f"Login data: {json.dumps(login_data, indent=2)}")
        print("-" * 50)
        
        login_response = requests.post(login_url, json=login_data)
        print(f"Status Code: {login_response.status_code}")
        
        if login_response.status_code == 200:
            response_json = login_response.json()
            print(f"Login Response: {json.dumps(response_json, indent=2)}")
            
            # Check if date_of_birth and gender are present
            user_data = response_json.get("user", {})
            date_of_birth = user_data.get("date_of_birth")
            gender = user_data.get("gender")
            
            print(f"\n📋 Field Check:")
            print(f"   date_of_birth: {date_of_birth}")
            print(f"   gender: {gender}")
            
            if date_of_birth and gender:
                print("✅ SUCCESS: date_of_birth and gender are returned correctly!")
            else:
                print("❌ ISSUE: date_of_birth or gender are missing/null")
        else:
            print(f"❌ Login failed: {login_response.text}")

if __name__ == "__main__":
    test_login()
