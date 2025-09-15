#!/usr/bin/env python3
"""
Test script for coach login functionality
"""

import requests
import json

BASE_URL = "http://localhost:8003"

def test_coach_login():
    """Test the new coach login API"""
    
    print("🧪 Testing Coach Login API...")
    
    # Step 1: Get superadmin token to create a test coach
    print("\n1. Getting superadmin token...")
    superadmin_login = {
        "email": "testsuperadmin@example.com",
        "password": "TestSuperAdmin123!"
    }
    
    try:
        admin_response = requests.post(f"{BASE_URL}/api/superadmin/login", json=superadmin_login)
        if admin_response.status_code != 200:
            print(f"❌ Superadmin login failed: {admin_response.text}")
            return
            
        admin_token = admin_response.json()["data"]["token"]
        admin_headers = {"Authorization": f"Bearer {admin_token}"}
        print("✅ Superadmin token obtained")
        
        # Step 2: Create a test coach
        print("\n2. Creating test coach...")
        test_coach_data = {
            "personal_info": {
                "first_name": "Test",
                "last_name": "LoginCoach",
                "gender": "Male",
                "date_of_birth": "1988-03-15"
            },
            "contact_info": {
                "email": "testlogincoach@example.com",
                "country_code": "+91",
                "phone": "9988776655",
                "password": "TestCoachLogin123!"
            },
            "address_info": {
                "address": "456 Login Test Street",
                "area": "Login Area",
                "city": "Test City",
                "state": "Test State",
                "zip_code": "654321",
                "country": "India"
            },
            "professional_info": {
                "education_qualification": "Masters in Sports",
                "professional_experience": "4+ years",
                "designation_id": "login-test-001",
                "certifications": ["Login Test Certification"]
            },
            "areas_of_expertise": ["Boxing", "Fitness Training"]
        }
        
        create_response = requests.post(f"{BASE_URL}/api/coaches", 
                                      headers=admin_headers, json=test_coach_data)
        
        if create_response.status_code in [200, 201]:
            print("✅ Test coach created successfully")
            coach_result = create_response.json()
            print(f"Coach ID: {coach_result.get('coach_id')}")
        elif create_response.status_code == 400 and "already exists" in create_response.text:
            print("✅ Test coach already exists (using existing one)")
        else:
            print(f"❌ Coach creation failed: {create_response.text}")
            return
        
        # Step 3: Test coach login
        print("\n3. Testing coach login...")
        coach_login_data = {
            "email": "testlogincoach@example.com",
            "password": "TestCoachLogin123!"
        }
        
        login_response = requests.post(f"{BASE_URL}/api/coaches/login", json=coach_login_data)
        print(f"Login Status: {login_response.status_code}")
        
        if login_response.status_code == 200:
            login_result = login_response.json()
            coach_token = login_result["access_token"]
            print("✅ Coach login successful!")
            print(f"Token (first 50 chars): {coach_token[:50]}...")
            print(f"Coach Name: {login_result['coach']['full_name']}")
            print(f"Token expires in: {login_result['expires_in']} seconds")
            
            # Step 4: Test coach profile endpoint
            print("\n4. Testing coach profile endpoint...")
            coach_headers = {"Authorization": f"Bearer {coach_token}"}
            profile_response = requests.get(f"{BASE_URL}/api/coaches/me", headers=coach_headers)
            
            print(f"Profile Status: {profile_response.status_code}")
            
            if profile_response.status_code == 200:
                profile_data = profile_response.json()
                print("✅ Coach profile endpoint works!")
                print(f"Profile Coach Name: {profile_data['coach']['full_name']}")
                print(f"Profile Coach Email: {profile_data['coach']['contact_info']['email']}")
                
                # Step 5: Test coach token with other endpoints
                print("\n5. Testing coach token with coach management endpoints...")
                coaches_list_response = requests.get(f"{BASE_URL}/api/coaches", headers=coach_headers)
                print(f"Coaches list status: {coaches_list_response.status_code}")
                
                if coaches_list_response.status_code == 403:
                    print("✅ Coach correctly denied access to coach management (as expected)")
                elif coaches_list_response.status_code == 200:
                    print("⚠️  Coach has access to coach management (check permissions)")
                else:
                    print(f"❓ Unexpected response: {coaches_list_response.text}")
                
                print("\n🎉 ALL COACH LOGIN TESTS COMPLETED SUCCESSFULLY!")
                
            else:
                print(f"❌ Coach profile failed: {profile_response.text}")
                
        else:
            print(f"❌ Coach login failed: {login_response.text}")
            
        # Test invalid login
        print("\n6. Testing invalid login...")
        invalid_login = {
            "email": "testlogincoach@example.com",
            "password": "WrongPassword"
        }
        
        invalid_response = requests.post(f"{BASE_URL}/api/coaches/login", json=invalid_login)
        print(f"Invalid login status: {invalid_response.status_code}")
        
        if invalid_response.status_code == 401:
            print("✅ Invalid login correctly rejected")
        else:
            print(f"❌ Invalid login should return 401: {invalid_response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_coach_login()
