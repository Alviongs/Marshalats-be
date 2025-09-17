#!/usr/bin/env python3
"""
Test the payment info endpoint specifically
"""

import requests
import json

BASE_URL = "http://31.97.224.169:8003"

def test_payment_info_endpoint():
    """Test the payment info endpoint with the exact parameters from the error"""
    
    course_id = "d3cb7042-cb18-4379-b948-3b3efc54f9e9"
    branch_id = "3c7ffd2c-5890-4f14-8e0c-f5f58a495812"
    duration = "758ddb36-07c8-417e-bbeb-444e383c7fa9"
    
    url = f"{BASE_URL}/api/courses/{course_id}/payment-info"
    params = {
        "branch_id": branch_id,
        "duration": duration
    }
    
    print(f"🧪 Testing Payment Info Endpoint")
    print(f"URL: {url}")
    print(f"Params: {params}")
    print("=" * 50)
    
    try:
        response = requests.get(url, params=params, timeout=10)
        
        print(f"Status Code: {response.status_code}")
        print(f"Headers: {dict(response.headers)}")
        
        try:
            response_data = response.json()
            print(f"Response: {json.dumps(response_data, indent=2)}")
        except:
            print(f"Raw Response: {response.text}")
            
        return response.status_code == 200
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_simple_course_endpoint():
    """Test if basic course endpoints work"""
    
    print(f"\n🧪 Testing Basic Course Endpoints")
    print("=" * 50)
    
    # Test courses list
    try:
        response = requests.get(f"{BASE_URL}/api/courses", timeout=10)
        print(f"Courses list: {response.status_code}")
        if response.status_code == 200:
            courses = response.json()
            print(f"Found {len(courses)} courses")
            if courses:
                print(f"First course ID: {courses[0].get('id', 'N/A')}")
        else:
            print(f"Error: {response.text[:200]}")
    except Exception as e:
        print(f"Courses list error: {e}")
    
    # Test branches
    try:
        response = requests.get(f"{BASE_URL}/api/public/branches", timeout=10)
        print(f"Branches list: {response.status_code}")
        if response.status_code == 200:
            branches = response.json()
            print(f"Found {len(branches)} branches")
            if branches:
                print(f"First branch ID: {branches[0].get('id', 'N/A')}")
    except Exception as e:
        print(f"Branches list error: {e}")

def main():
    """Main test function"""
    print("🚀 Payment Info Endpoint Test")
    print("=" * 50)
    
    # Test if server is running
    try:
        response = requests.get(f"{BASE_URL}/", timeout=5)
        print(f"✅ Server is running")
    except Exception as e:
        print(f"❌ Server is not accessible: {e}")
        return False
    
    # Test basic endpoints first
    test_simple_course_endpoint()
    
    # Test payment info endpoint
    success = test_payment_info_endpoint()
    
    print("\n" + "=" * 50)
    print("📋 SUMMARY")
    print("=" * 50)
    
    if success:
        print("✅ Payment info endpoint is working correctly")
    else:
        print("❌ Payment info endpoint has issues")
        print("💡 This might be due to:")
        print("   - Missing course/branch/duration data in database")
        print("   - Database connection issues")
        print("   - Implementation errors in the controller")
    
    return success

if __name__ == "__main__":
    main()
