#!/usr/bin/env python3
"""
Simple test for coach creation using the superadmin API
"""

import requests
import json

# API Configuration
BASE_URL = "http://31.97.224.169:8003/api"

def test_coach_creation_with_superadmin():
    print("🚀 Testing Coach Creation API with Super Admin Authentication")
    print("=" * 60)
    
    # Step 1: Super Admin Login (using the superadmin endpoint)
    print("\n1. Logging in as Super Admin (superadmin endpoint)...")
    login_data = {
        "email": "superadmin@example.com",
        "password": "StrongPassword@123"
    }
    
    try:
        login_response = requests.post(f"{BASE_URL}/superadmin/login", json=login_data)
        if login_response.status_code == 200:
            token = login_response.json()["data"]["token"]
            print("✅ Super Admin login successful!")
        else:
            print(f"❌ Super Admin login failed: {login_response.text}")
            return
    except Exception as e:
        print(f"❌ Login error: {e}")
        return
    
    # Step 2: Create Coach with Nested Structure
    print("\n2. Creating coach with nested structure...")
    
    coach_data = {
        "personal_info": {
            "first_name": "Ravi",
            "last_name": "Kumar", 
            "gender": "Male",
            "date_of_birth": "1985-06-15"
        },
        "contact_info": {
            "email": "ravi.kumar@martialarts.com",
            "country_code": "+91",
            "phone": "9876543210",
            "password": "SecurePassword@123"
        },
        "address_info": {
            "address": "123 MG Road",
            "area": "Indiranagar",
            "city": "Bengaluru",
            "state": "Karnataka",
            "zip_code": "560038",
            "country": "India"
        },
        "professional_info": {
            "education_qualification": "Bachelor of Physical Education",
            "professional_experience": "5+ years in martial arts training",
            "designation_id": "senior-instructor-001",
            "certifications": [
                "Black Belt in Karate",
                "Certified Fitness Trainer",
                "Sports Injury Prevention Certificate"
            ]
        },
        "areas_of_expertise": [
            "Taekwondo",
            "Karate",
            "Kung Fu", 
            "Mixed Martial Arts",
            "Self Defense"
        ]
    }
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    try:
        coach_response = requests.post(f"{BASE_URL}/superadmin/coaches", json=coach_data, headers=headers)
        print(f"Status Code: {coach_response.status_code}")
        print(f"Response: {coach_response.text}")
        
        if coach_response.status_code == 200:
            result = coach_response.json()
            print("✅ Coach created successfully!")
            print(f"   Coach ID: {result.get('coach_id')}")
            print(f"   Message: {result.get('message')}")
        else:
            print(f"❌ Coach creation failed: {coach_response.text}")
            print(f"   Status Code: {coach_response.status_code}")
            
    except Exception as e:
        print(f"❌ Coach creation error: {e}")
    
    print("\n" + "=" * 60)
    print("🏁 Coach Creation API Test Completed!")

if __name__ == "__main__":
    test_coach_creation_with_superadmin()
