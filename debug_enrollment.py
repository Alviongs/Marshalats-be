#!/usr/bin/env python3
"""
Debug enrollment creation during registration
"""

import requests
import json
import time

BASE_URL = "http://31.97.224.169:8003"

def test_registration_with_debug():
    """Test registration and check for enrollment creation"""
    
    test_payload = {
        "email": f"debug_test_{int(time.time())}@example.com",
        "phone": f"999888{int(time.time()) % 10000}",
        "first_name": "Debug",
        "last_name": "Test",
        "role": "student",
        "password": "TestPassword123!",
        "date_of_birth": "1990-01-01",
        "gender": "male",
        "course": {
            "category_id": "test-category-id",
            "course_id": "b14eaffc-e908-4942-b1fe-4ad5cd0a641a",
            "duration": "3-months"
        },
        "branch": {
            "location_id": "test-location-id",
            "branch_id": "test-branch-id"
        }
    }
    
    print("🧪 Testing registration with course data...")
    print(f"📤 Payload: {json.dumps(test_payload, indent=2)}")
    
    try:
        response = requests.post(f"{BASE_URL}/api/auth/register", json=test_payload)
        
        print(f"📥 Response Status: {response.status_code}")
        print(f"📥 Response Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"📥 Response Data: {json.dumps(data, indent=2)}")
            
            # Check if enrollment_id is in response
            if 'enrollment_id' in data:
                print(f"✅ Enrollment ID found: {data['enrollment_id']}")
            else:
                print("❌ No enrollment ID in response")
                
            # Check message for enrollment indication
            message = data.get('message', '')
            if 'enrolled' in message.lower():
                print(f"✅ Enrollment indicated in message: {message}")
            else:
                print(f"⚠️  Message doesn't indicate enrollment: {message}")
                
        else:
            print(f"❌ Registration failed: {response.text}")
            
    except Exception as e:
        print(f"❌ Error during registration: {e}")

if __name__ == "__main__":
    test_registration_with_debug()
