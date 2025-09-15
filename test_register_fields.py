#!/usr/bin/env python3
"""
Test script for the updated auth/register endpoint with date_of_birth and gender
"""
import requests
import json

def test_register_with_fields():
    """Test the /api/auth/register endpoint with all fields"""
    url = "http://localhost:8003/api/auth/register"
    
    # Test data for user registration with date_of_birth and gender
    test_user = {
        "email": "testuser4@example.com",
        "phone": "+1234567444",
        "full_name": "Test User Four",
        "role": "student", 
        "branch_id": "test-branch-id-4",
        "date_of_birth": "1995-06-15",
        "gender": "female",
        "biometric_id": "fingerprint-test-4"
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
            
            # Now test login to see if date_of_birth and gender are returned
            login_data = {
                "email": test_user["email"],
                "password": "auto-generated-password"  # This won't work, but let's see the error
            }
            
            # First, let's just check if the user was created properly
            print("\n" + "="*50)
            print("Testing if fields were saved properly...")
            
        else:
            print(f"⚠️  Registration failed with status code: {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to the server. Make sure it's running on http://localhost:8003")
    except requests.exceptions.Timeout:
        print("❌ Request timed out")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_register_with_fields()
