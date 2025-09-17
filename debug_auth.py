#!/usr/bin/env python3
"""
Debug script to test authentication with exact token
"""

import requests
import json

BASE_URL = "http://31.97.224.169:8003"

def debug_auth_issue():
    """Debug the 401 issue step by step"""
    
    print("🔍 Debugging Authentication Issue...")
    
    # Step 1: Login to get fresh token
    print("\n1. Getting fresh superadmin token...")
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
            print(f"✅ Token received: {token[:50]}...")
            
            # Step 2: Test superadmin verify endpoint
            print("\n2. Testing superadmin verify endpoint...")
            headers = {"Authorization": f"Bearer {token}"}
            verify_response = requests.get(f"{BASE_URL}/api/superadmin/verify-token", headers=headers)
            print(f"Verify Status: {verify_response.status_code}")
            
            if verify_response.status_code == 200:
                print("✅ Superadmin verify works")
                
                # Step 3: Test regular coach endpoint (the failing one)
                print("\n3. Testing regular coach endpoint (GET /api/coaches)...")
                coach_response = requests.get(f"{BASE_URL}/api/coaches", headers=headers)
                print(f"Coach endpoint status: {coach_response.status_code}")
                print(f"Response: {coach_response.text}")
                
                if coach_response.status_code == 401:
                    print("❌ Still getting 401 - investigating...")
                    
                    # Step 4: Test POST to coaches (the exact failing endpoint)
                    print("\n4. Testing POST /api/coaches...")
                    test_coach_data = {
                        "personal_info": {
                            "first_name": "Debug",
                            "last_name": "Test",
                            "gender": "Male",
                            "date_of_birth": "1990-01-01"
                        },
                        "contact_info": {
                            "email": f"debugtest{hash(token) % 10000}@example.com",
                            "country_code": "+91",
                            "phone": "9876543210",
                            "password": "DebugPassword123!"
                        },
                        "address_info": {
                            "address": "Debug Address",
                            "area": "Debug Area",
                            "city": "Debug City",
                            "state": "Debug State",
                            "zip_code": "123456",
                            "country": "India"
                        },
                        "professional_info": {
                            "education_qualification": "Debug Qualification",
                            "professional_experience": "1+ years",
                            "designation_id": "debug-001",
                            "certifications": ["Debug Cert"]
                        },
                        "areas_of_expertise": ["Debug Skill"]
                    }
                    
                    post_response = requests.post(f"{BASE_URL}/api/coaches", 
                                                headers=headers, json=test_coach_data)
                    print(f"POST Status: {post_response.status_code}")
                    print(f"POST Response: {post_response.text}")
                    
                elif coach_response.status_code == 200:
                    print("✅ Regular coach endpoint works!")
                    
            else:
                print(f"❌ Superadmin verify failed: {verify_response.text}")
                
        else:
            print(f"❌ Login failed: {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    debug_auth_issue()
