#!/usr/bin/env python3
"""
Test script for the improved register API with new payload structure
"""
import requests
import json

def test_improved_register():
    """Test the improved /api/auth/register endpoint"""
    url = "http://31.97.224.169:8003/api/auth/register"
    
    # Test data for user registration with new structure
    test_user = {
        "email": "pittisunilkumar3@gmail.com",
        "phone": "+9876543210",
        "first_name": "John",
        "last_name": "Doe",
        "role": "student",
        "password": "Neelarani@10",
        "date_of_birth": "2005-08-15",
        "gender": "male",
        "biometric_id": "optional-fingerprint-id",
        "course": {
            "category_id": "category-uuid",
            "course_id": "course-uuid",
            "duration": "6-months"
        },
        "branch": {
            "location_id": "location-uuid",
            "branch_id": "branch-uuid"
        }
    }
    
    try:
        print(f"Testing POST {url}")
        print(f"Request data: {json.dumps(test_user, indent=2)}")
        print("-" * 50)
        
        response = requests.post(url, json=test_user, timeout=10)
        
        print(f"Status Code: {response.status_code}")
        print(f"Response Body: {response.text}")
        
        if response.status_code == 200:
            print("✅ Registration successful!")
            
            # Now test login to see if all fields are returned correctly
            login_data = {
                "email": test_user["email"],
                "password": test_user["password"]
            }
            
            print(f"\n{'='*50}")
            print("Testing login with new user...")
            
            login_response = requests.post("http://31.97.224.169:8003/api/auth/login", json=login_data)
            print(f"Login Status: {login_response.status_code}")
            
            if login_response.status_code == 200:
                login_result = login_response.json()
                print(f"Login Response: {json.dumps(login_result, indent=2)}")
                
                # Check if all fields are present
                user_data = login_result.get("user", {})
                required_fields = ["first_name", "last_name", "full_name", "course", "branch"]
                
                print(f"\n📋 Field Check:")
                for field in required_fields:
                    value = user_data.get(field)
                    print(f"   {field}: {value}")
                
                # Check nested objects
                if user_data.get("course"):
                    course = user_data["course"]
                    print(f"   course.category_id: {course.get('category_id')}")
                    print(f"   course.course_id: {course.get('course_id')}")
                    print(f"   course.duration: {course.get('duration')}")
                
                if user_data.get("branch"):
                    branch = user_data["branch"]
                    print(f"   branch.location_id: {branch.get('location_id')}")
                    print(f"   branch.branch_id: {branch.get('branch_id')}")
                
                print("✅ SUCCESS: New payload structure is working!")
            else:
                print(f"❌ Login failed: {login_response.text}")
                
        else:
            print(f"⚠️  Registration failed with status code: {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to the server. Make sure it's running on http://31.97.224.169:8003")
    except requests.exceptions.Timeout:
        print("❌ Request timed out")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_improved_register()
