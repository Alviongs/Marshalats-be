#!/usr/bin/env python3
"""
Test Student Management API Fixes

This script tests the fixes implemented for proper data architecture compliance
in student management dashboard functionality.
"""

import requests
import json
import time
import sys
from datetime import datetime

BASE_URL = "http://localhost:8003"

class StudentManagementFixTester:
    def __init__(self):
        self.test_results = []
        self.test_user_id = None
        self.test_enrollment_id = None
        self.auth_token = None
    
    def log_test(self, test_name: str, passed: bool, message: str = "", details: dict = None):
        """Log test result"""
        status = "✅ PASS" if passed else "❌ FAIL"
        result = {
            "test": test_name,
            "passed": passed,
            "message": message,
            "details": details or {},
            "timestamp": datetime.utcnow().isoformat()
        }
        self.test_results.append(result)
        
        print(f"{status}: {test_name}")
        if message:
            print(f"    {message}")
        if details and not passed:
            print(f"    Details: {json.dumps(details, indent=2)}")

    def get_auth_token(self):
        """Get authentication token for API calls"""
        login_payload = {
            "email": "admin@example.com",
            "password": "admin123"
        }
        
        try:
            response = requests.post(f"{BASE_URL}/api/auth/login", json=login_payload)
            if response.status_code == 200:
                data = response.json()
                self.auth_token = data.get('access_token')
                return True
            else:
                return False
        except Exception as e:
            return False

    def test_create_student_with_enrollment(self):
        """Test creating a student and verify enrollment record is created"""
        test_name = "Create Student - Enrollment Record Creation"
        
        timestamp = int(time.time())
        test_payload = {
            "email": f"fix_test_{timestamp}@example.com",
            "phone": f"555999{timestamp % 10000}",
            "first_name": "FixTest",
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
            response = requests.post(f"{BASE_URL}/api/auth/register", json=test_payload)
            
            if response.status_code == 200:
                data = response.json()
                self.test_user_id = data.get('user_id')
                self.test_enrollment_id = data.get('enrollment_id')
                
                if self.test_user_id and self.test_enrollment_id:
                    self.log_test(test_name, True, 
                        f"✅ User: {self.test_user_id}, Enrollment: {self.test_enrollment_id}")
                    return True
                else:
                    self.log_test(test_name, False, 
                        "❌ Missing user_id or enrollment_id in response",
                        {"response": data})
                    return False
            else:
                self.log_test(test_name, False, 
                    f"❌ Registration failed: {response.status_code}",
                    {"response_text": response.text})
                return False
                
        except Exception as e:
            self.log_test(test_name, False, f"❌ Error: {e}")
            return False

    def test_get_user_with_enrollment_data(self):
        """Test the fixed get_user API that includes enrollment data"""
        test_name = "Get User API - Includes Enrollment Data"
        
        if not self.test_user_id or not self.auth_token:
            self.log_test(test_name, False, "❌ Prerequisites not met")
            return False
        
        headers = {
            "Authorization": f"Bearer {self.auth_token}",
            "Content-Type": "application/json"
        }
        
        try:
            response = requests.get(f"{BASE_URL}/api/users/{self.test_user_id}", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                user_data = data.get('user', {})
                enrollments_data = data.get('enrollments', [])
                
                if enrollments_data and len(enrollments_data) > 0:
                    enrollment = enrollments_data[0]
                    has_course_details = 'course_details' in enrollment
                    has_branch_details = 'branch_details' in enrollment
                    
                    if has_course_details and has_branch_details:
                        self.log_test(test_name, True, 
                            f"✅ Returns {len(enrollments_data)} enrollment(s) with enriched data")
                        return True
                    else:
                        self.log_test(test_name, False, 
                            "❌ Enrollment data missing course/branch details",
                            {"enrollment": enrollment})
                        return False
                else:
                    self.log_test(test_name, False, 
                        "❌ No enrollment data returned",
                        {"response": data})
                    return False
            else:
                self.log_test(test_name, False, 
                    f"❌ API call failed: {response.status_code}",
                    {"response_text": response.text})
                return False
                
        except Exception as e:
            self.log_test(test_name, False, f"❌ Error: {e}")
            return False

    def test_update_user_creates_enrollment(self):
        """Test that updating user course data creates/updates enrollment records"""
        test_name = "Update User API - Creates/Updates Enrollment"
        
        if not self.test_user_id or not self.auth_token:
            self.log_test(test_name, False, "❌ Prerequisites not met")
            return False
        
        headers = {
            "Authorization": f"Bearer {self.auth_token}",
            "Content-Type": "application/json"
        }
        
        # Update course information
        update_payload = {
            "first_name": "UpdatedFixTest",
            "course": {
                "category_id": "updated-category-id",
                "course_id": "b14eaffc-e908-4942-b1fe-4ad5cd0a641a",
                "duration": "6-months"
            },
            "branch": {
                "location_id": "updated-location-id",
                "branch_id": "updated-branch-id"
            }
        }
        
        try:
            response = requests.put(f"{BASE_URL}/api/users/{self.test_user_id}", 
                                  json=update_payload, headers=headers)
            
            if response.status_code == 200:
                # Now check if enrollment was updated/created
                time.sleep(1)  # Give it a moment to process
                
                # Get updated user data
                get_response = requests.get(f"{BASE_URL}/api/users/{self.test_user_id}", headers=headers)
                
                if get_response.status_code == 200:
                    data = get_response.json()
                    enrollments = data.get('enrollments', [])
                    
                    if enrollments:
                        # Check if enrollment reflects the update
                        enrollment = enrollments[0]
                        course_id = enrollment.get('course_id')
                        branch_id = enrollment.get('branch_id')
                        
                        if course_id and branch_id:
                            self.log_test(test_name, True, 
                                f"✅ Enrollment updated - Course: {course_id}, Branch: {branch_id}")
                            return True
                        else:
                            self.log_test(test_name, False, 
                                "❌ Enrollment missing course/branch IDs",
                                {"enrollment": enrollment})
                            return False
                    else:
                        self.log_test(test_name, False, 
                            "❌ No enrollment data after update")
                        return False
                else:
                    self.log_test(test_name, False, 
                        f"❌ Failed to get updated user data: {get_response.status_code}")
                    return False
            else:
                self.log_test(test_name, False, 
                    f"❌ Update failed: {response.status_code}",
                    {"response_text": response.text})
                return False
                
        except Exception as e:
            self.log_test(test_name, False, f"❌ Error: {e}")
            return False

    def test_enrollment_api_endpoint(self):
        """Test the dedicated enrollment API endpoint"""
        test_name = "Enrollment API - Get Student Enrollments"
        
        if not self.test_user_id or not self.auth_token:
            self.log_test(test_name, False, "❌ Prerequisites not met")
            return False
        
        headers = {
            "Authorization": f"Bearer {self.auth_token}",
            "Content-Type": "application/json"
        }
        
        try:
            response = requests.get(f"{BASE_URL}/api/enrollments/students/{self.test_user_id}", 
                                  headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                enrollments = data.get('enrollments', [])
                count = data.get('count', 0)
                
                if count > 0 and enrollments:
                    enrollment = enrollments[0]
                    has_course_details = 'course_details' in enrollment
                    has_branch_details = 'branch_details' in enrollment
                    
                    if has_course_details and has_branch_details:
                        self.log_test(test_name, True, 
                            f"✅ Returns {count} enrollment(s) with full details")
                        return True
                    else:
                        self.log_test(test_name, False, 
                            "❌ Enrollment missing enriched details",
                            {"enrollment": enrollment})
                        return False
                else:
                    self.log_test(test_name, False, 
                        f"❌ No enrollments found - Count: {count}")
                    return False
            else:
                self.log_test(test_name, False, 
                    f"❌ API call failed: {response.status_code}",
                    {"response_text": response.text})
                return False
                
        except Exception as e:
            self.log_test(test_name, False, f"❌ Error: {e}")
            return False

    def run_all_tests(self):
        """Run all student management fix tests"""
        print("🔧 Testing Student Management API Fixes...")
        print("=" * 70)
        
        # Get authentication token
        auth_available = self.get_auth_token()
        if not auth_available:
            print("❌ Authentication failed - cannot run tests")
            return False
        
        # Test 1: Create student with enrollment
        self.test_create_student_with_enrollment()
        
        # Test 2: Get user with enrollment data
        self.test_get_user_with_enrollment_data()
        
        # Test 3: Update user creates/updates enrollment
        self.test_update_user_creates_enrollment()
        
        # Test 4: Dedicated enrollment API
        self.test_enrollment_api_endpoint()
        
        # Print summary
        print("\n" + "=" * 70)
        print("📊 STUDENT MANAGEMENT FIX TEST SUMMARY")
        print("=" * 70)
        
        passed_tests = [r for r in self.test_results if r["passed"]]
        failed_tests = [r for r in self.test_results if not r["passed"]]
        
        print(f"Total tests: {len(self.test_results)}")
        print(f"Passed: {len(passed_tests)}")
        print(f"Failed: {len(failed_tests)}")
        
        if failed_tests:
            print("\n❌ FAILED TESTS:")
            for test in failed_tests:
                print(f"  - {test['test']}: {test['message']}")
        
        if len(failed_tests) == 0:
            print("\n🎉 All student management fix tests passed!")
            print("✅ Data architecture compliance restored!")
        else:
            print(f"\n⚠️  {len(failed_tests)} tests failed.")
        
        return len(failed_tests) == 0

def main():
    tester = StudentManagementFixTester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
