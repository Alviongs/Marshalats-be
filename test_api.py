#!/usr/bin/env python3
"""
Test script for the auth/register endpoint
"""
import requests
import json

def test_register_endpoint():
    """Test the /api/auth/register endpoint"""
    url = "http://localhost:8003/api/auth/register"
    
    # Test data for user registration
    test_user = {
        "email": "test@example.com",
        "phone": "+1234567890",
        "full_name": "Test User",
        "role": "student",
        "branch_id": "test-branch-id",
        "date_of_birth": "2000-01-01",
        "gender": "male"
    }
    
    try:
        print(f"Testing POST {url}")
        print(f"Request data: {json.dumps(test_user, indent=2)}")
        print("-" * 50)
        
        response = requests.post(url, json=test_user, timeout=10)
        
        print(f"Status Code: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        print(f"Response Body: {response.text}")
        
        if response.status_code == 200:
            print("✅ API endpoint is working correctly!")
        else:
            print(f"⚠️  API returned status code: {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to the server. Make sure it's running on http://localhost:8003")
    except requests.exceptions.Timeout:
        print("❌ Request timed out")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_register_endpoint()
