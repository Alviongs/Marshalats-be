#!/usr/bin/env python3
"""
Test Basic Student Creation

This script tests the basic student creation functionality to verify
that enrollment records are being created properly.
"""

import requests
import json
import time
import sys
from datetime import datetime

BASE_URL = "http://localhost:8003"

def test_student_registration_with_enrollment():
    """Test student registration creates enrollment record"""
    print("🧪 Testing Student Registration with Enrollment Creation...")
    
    timestamp = int(time.time())
    test_payload = {
        "email": f"basic_test_{timestamp}@example.com",
        "phone": f"555111{timestamp % 10000}",
        "first_name": "BasicTest",
        "last_name": "Student",
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
    
    try:
        print(f"📤 Sending registration request...")
        response = requests.post(f"{BASE_URL}/api/auth/register", json=test_payload)
        
        print(f"📥 Response Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"📄 Response Data: {json.dumps(data, indent=2)}")
            
            user_id = data.get('user_id')
            enrollment_id = data.get('enrollment_id')
            
            if user_id and enrollment_id:
                print(f"✅ SUCCESS: Student created with enrollment!")
                print(f"   👤 User ID: {user_id}")
                print(f"   📚 Enrollment ID: {enrollment_id}")
                return True
            elif user_id:
                print(f"⚠️  PARTIAL: User created but no enrollment ID returned")
                print(f"   👤 User ID: {user_id}")
                return False
            else:
                print(f"❌ FAILED: No user ID in response")
                return False
        else:
            print(f"❌ FAILED: Registration failed with status {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False

def test_student_registration_without_course():
    """Test student registration without course data"""
    print("\n🧪 Testing Student Registration without Course Data...")
    
    timestamp = int(time.time())
    test_payload = {
        "email": f"no_course_test_{timestamp}@example.com",
        "phone": f"555222{timestamp % 10000}",
        "first_name": "NoCourse",
        "last_name": "Student",
        "role": "student",
        "password": "TestPassword123!",
        "date_of_birth": "1990-01-01",
        "gender": "female"
        # No course or branch data
    }
    
    try:
        print(f"📤 Sending registration request...")
        response = requests.post(f"{BASE_URL}/api/auth/register", json=test_payload)
        
        print(f"📥 Response Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"📄 Response Data: {json.dumps(data, indent=2)}")
            
            user_id = data.get('user_id')
            enrollment_id = data.get('enrollment_id')
            
            if user_id and not enrollment_id:
                print(f"✅ SUCCESS: Student created without enrollment (as expected)")
                print(f"   👤 User ID: {user_id}")
                return True
            elif user_id and enrollment_id:
                print(f"⚠️  UNEXPECTED: Enrollment created without course data")
                print(f"   👤 User ID: {user_id}")
                print(f"   📚 Enrollment ID: {enrollment_id}")
                return False
            else:
                print(f"❌ FAILED: No user ID in response")
                return False
        else:
            print(f"❌ FAILED: Registration failed with status {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False

def main():
    print("🚀 Basic Student Creation Tests")
    print("=" * 50)
    
    # Test 1: Registration with course data
    test1_passed = test_student_registration_with_enrollment()
    
    # Test 2: Registration without course data
    test2_passed = test_student_registration_without_course()
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 TEST SUMMARY")
    print("=" * 50)
    
    total_tests = 2
    passed_tests = sum([test1_passed, test2_passed])
    
    print(f"Total tests: {total_tests}")
    print(f"Passed: {passed_tests}")
    print(f"Failed: {total_tests - passed_tests}")
    
    if passed_tests == total_tests:
        print("\n🎉 All basic tests passed!")
        print("✅ Student registration with enrollment creation is working correctly!")
    else:
        print(f"\n⚠️  {total_tests - passed_tests} test(s) failed.")
    
    return passed_tests == total_tests

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
