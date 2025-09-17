#!/usr/bin/env python3
"""
Check what endpoints are registered in the running server
"""

import requests
import json

BASE_URL = "http://31.97.224.169:8003"

def check_registered_endpoints():
    """Check what endpoints are registered"""
    try:
        response = requests.get(f"{BASE_URL}/openapi.json", timeout=10)
        if response.status_code == 200:
            openapi_data = response.json()
            paths = openapi_data.get("paths", {})
            
            print("🔍 Registered API Endpoints:")
            print("=" * 50)
            
            payment_endpoints = []
            course_endpoints = []
            
            for path, methods in paths.items():
                if "/payments" in path:
                    payment_endpoints.append(path)
                elif "/courses" in path:
                    course_endpoints.append(path)
            
            print("\n💰 Payment Endpoints:")
            if payment_endpoints:
                for endpoint in sorted(payment_endpoints):
                    print(f"  ✅ {endpoint}")
            else:
                print("  ❌ No payment endpoints found")
            
            print("\n📚 Course Endpoints (payment-related):")
            course_payment_endpoints = [ep for ep in course_endpoints if "payment" in ep]
            if course_payment_endpoints:
                for endpoint in sorted(course_payment_endpoints):
                    print(f"  ✅ {endpoint}")
            else:
                print("  ❌ No course payment endpoints found")
            
            print(f"\n📊 Total endpoints: {len(paths)}")
            print(f"💰 Payment endpoints: {len(payment_endpoints)}")
            print(f"📚 Course payment endpoints: {len(course_payment_endpoints)}")
            
            return len(payment_endpoints) > 0 or len(course_payment_endpoints) > 0
            
        else:
            print(f"❌ Failed to get OpenAPI spec: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error checking endpoints: {e}")
        return False

def test_specific_endpoints():
    """Test specific payment endpoints we expect"""
    print("\n🧪 Testing Expected Payment Endpoints:")
    print("=" * 50)
    
    expected_endpoints = [
        ("GET", "/api/payments/stats", "Payment Stats"),
        ("GET", "/api/payments", "Payment List"),
        ("GET", "/api/payments/notifications", "Payment Notifications"),
        ("POST", "/api/payments/process-registration", "Process Registration"),
        ("GET", "/api/courses/{id}/payment-info", "Course Payment Info")
    ]
    
    for method, endpoint, name in expected_endpoints:
        test_url = endpoint.replace("{id}", "test-id")
        full_url = f"{BASE_URL}{test_url}"
        
        try:
            if method == "GET":
                response = requests.get(full_url, timeout=5)
            elif method == "POST":
                response = requests.post(full_url, json={}, timeout=5)
            
            status = response.status_code
            
            if status == 404:
                print(f"  ❌ {name}: Not Found (404)")
            elif status in [200, 401, 403, 422]:
                print(f"  ✅ {name}: Exists ({status})")
            else:
                print(f"  ⚠️  {name}: Unexpected ({status})")
                
        except Exception as e:
            print(f"  ❌ {name}: Error - {e}")

def main():
    """Main function"""
    print("🔍 Endpoint Registration Check")
    print("=" * 50)
    
    # Check if server is running
    try:
        response = requests.get(f"{BASE_URL}/", timeout=5)
        print(f"✅ Server is running on {BASE_URL}")
    except Exception as e:
        print(f"❌ Server is not accessible: {e}")
        return False
    
    # Check registered endpoints
    endpoints_found = check_registered_endpoints()
    
    # Test specific endpoints
    test_specific_endpoints()
    
    print("\n" + "=" * 50)
    print("📋 SUMMARY")
    print("=" * 50)
    
    if endpoints_found:
        print("✅ Payment endpoints are registered in OpenAPI spec")
    else:
        print("❌ Payment endpoints are NOT registered in OpenAPI spec")
        print("   This suggests an issue with route registration")
    
    return endpoints_found

if __name__ == "__main__":
    main()
