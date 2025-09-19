#!/usr/bin/env python3
"""
Test CORS configuration by making requests from different origins
"""

import requests
import json

BASE_URL = "http://localhost:8003"

def test_cors_headers():
    """Test CORS headers on the payment info endpoint"""
    
    course_id = "d3cb7042-cb18-4379-b948-3b3efc54f9e9"
    branch_id = "3c7ffd2c-5890-4f14-8e0c-f5f58a495812"
    duration = "758ddb36-07c8-417e-bbeb-444e383c7fa9"
    
    url = f"{BASE_URL}/api/courses/{course_id}/payment-info"
    params = {
        "branch_id": branch_id,
        "duration": duration
    }
    
    # Test with Origin header (simulating frontend request)
    headers = {
        "Origin": "http://localhost:3022",
        "Content-Type": "application/json"
    }
    
    print(f"🧪 Testing CORS Headers")
    print(f"URL: {url}")
    print(f"Origin: {headers['Origin']}")
    print("=" * 50)
    
    try:
        response = requests.get(url, params=params, headers=headers, timeout=10)
        
        print(f"Status Code: {response.status_code}")
        print(f"Response Headers:")
        for key, value in response.headers.items():
            if 'access-control' in key.lower() or 'cors' in key.lower():
                print(f"  {key}: {value}")
        
        if response.status_code == 200:
            print("✅ CORS request successful")
            data = response.json()
            print(f"Response data: {json.dumps(data, indent=2)}")
        else:
            print(f"❌ Request failed: {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

def test_preflight_request():
    """Test CORS preflight request"""
    
    course_id = "d3cb7042-cb18-4379-b948-3b3efc54f9e9"
    branch_id = "3c7ffd2c-5890-4f14-8e0c-f5f58a495812"
    duration = "758ddb36-07c8-417e-bbeb-444e383c7fa9"
    
    url = f"{BASE_URL}/api/courses/{course_id}/payment-info"
    
    # Test OPTIONS request (preflight)
    headers = {
        "Origin": "http://localhost:3022",
        "Access-Control-Request-Method": "GET",
        "Access-Control-Request-Headers": "Content-Type"
    }
    
    print(f"\n🧪 Testing CORS Preflight (OPTIONS)")
    print(f"URL: {url}")
    print("=" * 50)
    
    try:
        response = requests.options(url, headers=headers, timeout=10)
        
        print(f"Status Code: {response.status_code}")
        print(f"Response Headers:")
        for key, value in response.headers.items():
            if 'access-control' in key.lower() or 'allow' in key.lower():
                print(f"  {key}: {value}")
        
        if response.status_code in [200, 204]:
            print("✅ CORS preflight successful")
        else:
            print(f"❌ Preflight failed: {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

def main():
    """Main test function"""
    print("🚀 CORS Configuration Test")
    print("=" * 50)
    
    # Test if server is running
    try:
        response = requests.get(f"{BASE_URL}/", timeout=5)
        print(f"✅ Server is running")
    except Exception as e:
        print(f"❌ Server is not accessible: {e}")
        return False
    
    # Test CORS headers
    test_cors_headers()
    
    # Test preflight request
    test_preflight_request()
    
    print("\n" + "=" * 50)
    print("📋 SUMMARY")
    print("=" * 50)
    print("If CORS headers are present, the frontend should be able to make requests.")
    print("If not, check the FastAPI CORS middleware configuration.")

if __name__ == "__main__":
    main()
