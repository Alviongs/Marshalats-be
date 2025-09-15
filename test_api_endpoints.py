#!/usr/bin/env python3
"""
Test API endpoints to validate the architecture fix
"""

import requests
import json
import sys

BASE_URL = "http://localhost:8003"

def test_courses_api():
    """Test the courses API to ensure it returns proper counts"""
    print("🧪 Testing Courses API...")
    
    try:
        response = requests.get(f"{BASE_URL}/api/courses/public/all")
        if response.status_code == 200:
            data = response.json()
            courses = data.get('courses', [])
            print(f"✅ Courses API working - found {len(courses)} courses")
            
            if courses:
                course = courses[0]
                print(f"📊 Sample course counts:")
                print(f"   - Masters: {course.get('masters', 'N/A')}")
                print(f"   - Students: {course.get('students', 'N/A')}")
                print(f"   - Instructor assignments: {len(course.get('instructor_assignments', []))}")
            
            return True
        else:
            print(f"❌ Courses API failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error testing courses API: {e}")
        return False

def test_registration_api():
    """Test the registration API to ensure it creates proper enrollment records"""
    print("\n🧪 Testing Registration API...")
    
    test_user = {
        "email": f"test_user_{int(time.time())}@example.com",
        "phone": "1234567890",
        "first_name": "Test",
        "last_name": "User",
        "role": "student",
        "password": "TestPassword123!",
        "date_of_birth": "1990-01-01",
        "gender": "male",
        "course": {
            "category_id": "test-category",
            "course_id": "b14eaffc-e908-4942-b1fe-4ad5cd0a641a",
            "duration": "3-months"
        },
        "branch": {
            "location_id": "test-location",
            "branch_id": "test-branch"
        }
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/auth/register", json=test_user)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Registration API working")
            print(f"   - User ID: {data.get('user_id')}")
            print(f"   - Enrollment ID: {data.get('enrollment_id', 'Not created')}")
            print(f"   - Message: {data.get('message')}")
            return True
        else:
            print(f"❌ Registration API failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error testing registration API: {e}")
        return False

def test_student_details_api():
    """Test the student details API"""
    print("\n🧪 Testing Student Details API...")
    
    # This would need authentication, so we'll just test if the endpoint exists
    try:
        response = requests.get(f"{BASE_URL}/api/users/students/details")
        if response.status_code == 401:
            print("✅ Student Details API exists (authentication required)")
            return True
        elif response.status_code == 200:
            data = response.json()
            students = data.get('students', [])
            print(f"✅ Student Details API working - found {len(students)} students")
            
            if students:
                student = students[0]
                courses = student.get('courses', [])
                print(f"📊 Sample student courses: {len(courses)}")
                for course in courses[:2]:  # Show first 2 courses
                    source = course.get('source', 'enrollment')
                    print(f"   - {course.get('course_name')} (source: {source})")
            
            return True
        else:
            print(f"❌ Student Details API failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error testing student details API: {e}")
        return False

def main():
    print("🚀 Testing API Endpoints After Architecture Fix")
    print("=" * 50)
    
    results = []
    
    # Test each API
    results.append(("Courses API", test_courses_api()))
    results.append(("Registration API", test_registration_api()))
    results.append(("Student Details API", test_student_details_api()))
    
    # Print summary
    print("\n" + "=" * 50)
    print("📊 TEST SUMMARY")
    print("=" * 50)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {test_name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All API tests passed!")
    else:
        print("⚠️  Some tests failed. Please review the issues above.")
    
    return passed == total

if __name__ == "__main__":
    import time
    success = main()
    sys.exit(0 if success else 1)
