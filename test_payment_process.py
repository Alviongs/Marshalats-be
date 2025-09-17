#!/usr/bin/env python3
"""
Test the payment processing endpoint with the exact frontend data
"""

import requests
import json
import time

BASE_URL = "http://31.97.224.169:8003"

def test_payment_processing():
    """Test the payment processing endpoint"""
    
    # Sample data that matches what the frontend sends
    payment_data = {
        "student_data": {
            "email": f"test{int(time.time())}@example.com",
            "phone": f"123456{int(time.time()) % 10000}",
            "first_name": "Test",
            "last_name": "Student",
            "full_name": "Test Student",
            "role": "student",
            "is_active": True,
            "date_of_birth": "1990-01-01",
            "gender": "male"
        },
        "course_id": "d3cb7042-cb18-4379-b948-3b3efc54f9e9",
        "branch_id": "3c7ffd2c-5890-4f14-8e0c-f5f58a495812",
        "category_id": "test-category-id",
        "duration": "758ddb36-07c8-417e-bbeb-444e383c7fa9",
        "payment_method": "credit_card"
    }
    
    url = f"{BASE_URL}/api/payments/process-registration"
    
    print(f"🧪 Testing Payment Processing Endpoint")
    print(f"URL: {url}")
    print(f"Data: {json.dumps(payment_data, indent=2)}")
    print("=" * 60)
    
    try:
        response = requests.post(url, json=payment_data, timeout=30)
        
        print(f"Status Code: {response.status_code}")
        print(f"Response Headers:")
        for key, value in response.headers.items():
            if any(keyword in key.lower() for keyword in ['content-type', 'server']):
                print(f"  {key}: {value}")
        
        try:
            response_data = response.json()
            print(f"\nResponse:")
            print(json.dumps(response_data, indent=2))
        except:
            print(f"Raw Response: {response.text}")
        
        return response.status_code == 201
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_with_typo():
    """Test with the typo that might be in the backend"""
    
    # Sample data with the typo
    payment_data = {
        "stuudent_data": {  # Note the typo
            "email": "test@example.com",
            "phone": "1234567890",
            "first_name": "Test",
            "last_name": "Student",
            "full_name": "Test Student",
            "role": "student",
            "is_active": True,
            "date_of_birth": "1990-01-01",
            "gender": "male"
        },
        "course_id": "d3cb7042-cb18-4379-b948-3b3efc54f9e9",
        "branch_id": "3c7ffd2c-5890-4f14-8e0c-f5f58a495812",
        "category_id": "test-category-id",
        "duration": "758ddb36-07c8-417e-bbeb-444e383c7fa9",
        "payment_method": "credit_card"
    }
    
    url = f"{BASE_URL}/api/payments/process-registration"
    
    print(f"\n🧪 Testing with Typo (stuudent_data)")
    print(f"URL: {url}")
    print("=" * 60)
    
    try:
        response = requests.post(url, json=payment_data, timeout=30)
        
        print(f"Status Code: {response.status_code}")
        
        try:
            response_data = response.json()
            print(f"Response:")
            print(json.dumps(response_data, indent=2))
        except:
            print(f"Raw Response: {response.text}")
        
        return response.status_code == 201
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    """Main test function"""
    print("🚀 Payment Processing Test")
    print("=" * 60)
    
    # Test if server is running
    try:
        response = requests.get(f"{BASE_URL}/", timeout=5)
        print(f"✅ Server is running")
    except Exception as e:
        print(f"❌ Server is not accessible: {e}")
        return False
    
    # Test normal payment processing
    success1 = test_payment_processing()
    
    # Test with typo
    success2 = test_with_typo()
    
    print("\n" + "=" * 60)
    print("📋 SUMMARY")
    print("=" * 60)
    
    if success1:
        print("✅ Normal payment processing works")
    else:
        print("❌ Normal payment processing failed")
    
    if success2:
        print("✅ Payment processing with typo works")
    else:
        print("❌ Payment processing with typo failed")
    
    return success1 or success2

if __name__ == "__main__":
    main()
