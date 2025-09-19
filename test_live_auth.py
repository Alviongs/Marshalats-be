#!/usr/bin/env python3
"""
Comprehensive test to verify all coach endpoints work with superadmin token
"""

import requests
import json
import time

BASE_URL = "http://localhost:8003"

def test_all_coach_endpoints():
    """Test all coach endpoints with superadmin authentication"""
    
    print("🔍 Comprehensive Coach Endpoint Test...")
    
    # Get fresh token
    print("\n1. Getting fresh superadmin token...")
    login_data = {
        "email": "testsuperadmin@example.com",
        "password": "TestSuperAdmin123!"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/superadmin/login", json=login_data)
        if response.status_code != 200:
            print(f"❌ Login failed: {response.text}")
            return
            
        token = response.json()["data"]["token"]
        headers = {"Authorization": f"Bearer {token}"}
        print(f"✅ Token: {token[:50]}...")
        
        # Test all endpoints
        endpoints_to_test = [
            ("GET", "/api/coaches", "Get all coaches"),
            ("GET", "/api/coaches/stats/overview", "Get coach statistics"),
            ("GET", "/api/superadmin/coaches", "Get coaches via superadmin"),
            ("GET", "/api/superadmin/verify-token", "Verify superadmin token"),
        ]
        
        print(f"\n2. Testing {len(endpoints_to_test)} endpoints...")
        
        for method, endpoint, description in endpoints_to_test:
            print(f"\n   Testing {method} {endpoint} - {description}")
            
            if method == "GET":
                test_response = requests.get(f"{BASE_URL}{endpoint}", headers=headers)
            elif method == "POST":
                test_response = requests.post(f"{BASE_URL}{endpoint}", headers=headers, json={})
                
            print(f"   Status: {test_response.status_code}")
            
            if test_response.status_code == 200:
                print(f"   ✅ Success")
            else:
                print(f"   ❌ Failed: {test_response.text[:100]}...")
        
        # Test POST coach creation with unique email
        print(f"\n3. Testing POST /api/coaches (coach creation)...")
        unique_email = f"test{int(time.time())}@example.com"
        
        coach_data = {
            "personal_info": {
                "first_name": "Live",
                "last_name": "Test",
                "gender": "Female",
                "date_of_birth": "1992-05-15"
            },
            "contact_info": {
                "email": unique_email,
                "country_code": "+1",
                "phone": "5551234567",
                "password": "LiveTest123!"
            },
            "address_info": {
                "address": "Live Test Address",
                "area": "Test Area",
                "city": "Test City",
                "state": "Test State",
                "zip_code": "12345",
                "country": "USA"
            },
            "professional_info": {
                "education_qualification": "Masters Degree",
                "professional_experience": "5+ years",
                "designation_id": "live-test-001",
                "certifications": ["Live Test Certification"]
            },
            "areas_of_expertise": ["Testing", "Debugging"]
        }
        
        create_response = requests.post(f"{BASE_URL}/api/coaches", 
                                      headers=headers, json=coach_data)
        print(f"   Status: {create_response.status_code}")
        
        if create_response.status_code in [200, 201]:
            result = create_response.json()
            coach_id = result.get("coach_id")
            print(f"   ✅ Coach created successfully: {coach_id}")
            
            # Test GET specific coach
            if coach_id:
                print(f"\n4. Testing GET /api/coaches/{coach_id}")
                get_coach_response = requests.get(f"{BASE_URL}/api/coaches/{coach_id}", headers=headers)
                print(f"   Status: {get_coach_response.status_code}")
                if get_coach_response.status_code == 200:
                    print(f"   ✅ Individual coach retrieval works")
                else:
                    print(f"   ❌ Failed: {get_coach_response.text[:100]}...")
        else:
            print(f"   ❌ Coach creation failed: {create_response.text}")
            
        print(f"\n🎉 All tests completed!")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_all_coach_endpoints()
