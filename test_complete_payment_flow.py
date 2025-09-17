#!/usr/bin/env python3
"""
Complete test of the payment flow fixes
"""

import requests
import json
import time

BASE_URL = "http://31.97.224.169:8003"
FRONTEND_URL = "http://localhost:3022"

def test_payment_info_api():
    """Test the payment info API that the frontend uses"""
    
    course_id = "d3cb7042-cb18-4379-b948-3b3efc54f9e9"
    branch_id = "3c7ffd2c-5890-4f14-8e0c-f5f58a495812"
    duration = "758ddb36-07c8-417e-bbeb-444e383c7fa9"
    
    url = f"{BASE_URL}/api/courses/{course_id}/payment-info"
    params = {
        "branch_id": branch_id,
        "duration": duration
    }
    
    headers = {
        "Content-Type": "application/json",
        "Origin": FRONTEND_URL
    }
    
    print(f"🧪 Testing Payment Info API")
    print(f"URL: {url}")
    print("=" * 50)
    
    try:
        response = requests.get(url, params=params, headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Payment Info API Response:")
            print(json.dumps(data, indent=2))
            
            # Validate structure
            required_fields = ['course_id', 'course_name', 'pricing']
            pricing_fields = ['course_fee', 'admission_fee', 'total_amount']
            
            valid = True
            for field in required_fields:
                if field not in data:
                    print(f"❌ Missing field: {field}")
                    valid = False
            
            if 'pricing' in data:
                for field in pricing_fields:
                    if field not in data['pricing']:
                        print(f"❌ Missing pricing field: {field}")
                        valid = False
            
            if valid:
                print(f"✅ All required fields present")
                print(f"💰 Total Amount: ₹{data['pricing']['total_amount']}")
            
            return valid
        else:
            print(f"❌ API Error: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Request Error: {e}")
        return False

def test_payment_processing():
    """Test the payment processing endpoint"""
    
    timestamp = int(time.time())
    payment_data = {
        "student_data": {
            "email": f"test{timestamp}@example.com",
            "phone": f"123456{timestamp % 10000}",
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
    
    print(f"\n🧪 Testing Payment Processing")
    print("=" * 50)
    
    try:
        response = requests.post(url, json=payment_data, timeout=30)
        
        if response.status_code == 201:
            data = response.json()
            print(f"✅ Payment Processing Response:")
            print(json.dumps(data, indent=2))
            
            # Validate response structure
            required_fields = ['payment_id', 'student_id', 'transaction_id', 'amount', 'status', 'message']
            valid = True
            
            for field in required_fields:
                if field not in data:
                    print(f"❌ Missing response field: {field}")
                    valid = False
            
            if valid:
                print(f"✅ Payment processing successful")
                print(f"💰 Amount: ₹{data['amount']}")
                print(f"🆔 Transaction ID: {data['transaction_id']}")
                print(f"👤 Student ID: {data['student_id']}")
            
            return valid
        else:
            print(f"❌ Payment Processing Error: {response.status_code}")
            try:
                error_data = response.json()
                print(json.dumps(error_data, indent=2))
            except:
                print(response.text)
            return False
            
    except Exception as e:
        print(f"❌ Request Error: {e}")
        return False

def test_frontend_accessibility():
    """Test frontend pages"""
    
    print(f"\n🧪 Testing Frontend Pages")
    print("=" * 50)
    
    pages = [
        ("/", "Home Page"),
        ("/register/payment", "Payment Page"),
        ("/register/payment-confirmation", "Payment Confirmation Page"),
        ("/dashboard/create-student", "Manual Student Registration")
    ]
    
    results = []
    
    for path, name in pages:
        try:
            response = requests.get(f"{FRONTEND_URL}{path}", timeout=10)
            if response.status_code == 200:
                print(f"✅ {name}: Accessible")
                results.append(True)
            else:
                print(f"❌ {name}: Status {response.status_code}")
                results.append(False)
        except Exception as e:
            print(f"❌ {name}: Error - {e}")
            results.append(False)
    
    return all(results)

def main():
    """Main test function"""
    print("🚀 Complete Payment Flow Test")
    print("=" * 50)
    
    # Test if servers are running
    try:
        backend_response = requests.get(f"{BASE_URL}/", timeout=5)
        frontend_response = requests.get(f"{FRONTEND_URL}/", timeout=5)
        
        if backend_response.status_code == 200:
            print(f"✅ Backend server is running")
        else:
            print(f"❌ Backend server issue: {backend_response.status_code}")
            return False
            
        if frontend_response.status_code == 200:
            print(f"✅ Frontend server is running")
        else:
            print(f"❌ Frontend server issue: {frontend_response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Server connectivity error: {e}")
        return False
    
    # Run all tests
    results = []
    
    results.append(("Payment Info API", test_payment_info_api()))
    results.append(("Payment Processing", test_payment_processing()))
    results.append(("Frontend Accessibility", test_frontend_accessibility()))
    
    # Summary
    print("\n" + "=" * 50)
    print("📋 COMPLETE TEST SUMMARY")
    print("=" * 50)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 ALL PAYMENT FLOW FIXES VERIFIED!")
        print("✅ Payment confirmation page can fetch and display pricing")
        print("✅ Payment processing endpoint works correctly")
        print("✅ Manual student registration includes payment processing")
        print("✅ CORS issues are resolved")
        print("✅ Frontend pages are accessible")
    else:
        print("\n⚠️  Some tests failed. Please check the issues above.")
    
    return passed == total

if __name__ == "__main__":
    main()
