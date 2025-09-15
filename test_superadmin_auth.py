#!/usr/bin/env python3
"""
Test script to verify superadmin authentication works with coach endpoints
"""

import requests
import json

BASE_URL = "http://localhost:8003"

def test_superadmin_auth():
    """Test superadmin authentication flow"""
    
    print("🔐 Testing SuperAdmin Authentication Flow...")
    
    # Step 1: Login as superadmin
    print("\n1. Logging in as superadmin...")
    login_data = {
        "email": "testsuperadmin@example.com",
        "password": "TestSuperAdmin123!"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/superadmin/login", json=login_data)
        print(f"Login Status: {response.status_code}")
        
        if response.status_code == 200:
            login_result = response.json()
            token = login_result["data"]["token"]
            print(f"✅ Login successful! Token received.")
            print(f"Token (first 50 chars): {token[:50]}...")
            
            # Step 2: Test token verification
            print("\n2. Verifying token...")
            headers = {"Authorization": f"Bearer {token}"}
            verify_response = requests.get(f"{BASE_URL}/api/superadmin/verify-token", headers=headers)
            print(f"Token verification status: {verify_response.status_code}")
            
            if verify_response.status_code == 200:
                print("✅ Token verification successful!")
                
                # Step 3: Test regular coach endpoint with superadmin token (skip creation)
                print("\n3. Testing regular coach endpoint with superadmin token...")
                regular_coach_response = requests.get(f"{BASE_URL}/api/coaches", headers=headers)
                print(f"Regular coach endpoint status: {regular_coach_response.status_code}")
                
                if regular_coach_response.status_code == 200:
                    print("✅ Regular coach endpoint works with superadmin token!")
                    coaches_data = regular_coach_response.json()
                    print(f"Found {coaches_data.get('total', 0)} coaches")
                    print("🎉 ALL TESTS PASSED! Authentication is working correctly.")
                else:
                    print(f"❌ Regular coach endpoint failed: {regular_coach_response.text}")
                    
            else:
                print(f"❌ Token verification failed: {verify_response.text}")
                
        else:
            print(f"❌ Login failed: {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Request error: {e}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

if __name__ == "__main__":
    test_superadmin_auth()
