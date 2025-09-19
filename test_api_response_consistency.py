#!/usr/bin/env python3
"""
Test API Response Consistency

This script tests that all API responses maintain consistent structure and format
after the data architecture changes, ensuring frontend applications continue to work.
"""

import requests
import json
import time
import sys
from datetime import datetime

BASE_URL = "http://localhost:8003"

class APIResponseConsistencyTester:
    def __init__(self):
        self.test_results = []
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

    def test_registration_response_structure(self):
        """Test that registration API returns consistent response structure"""
        test_name = "Registration API Response Structure"
        
        test_payload = {
            "email": f"consistency_test_{int(time.time())}@example.com",
            "phone": f"555999{int(time.time()) % 10000}",
            "first_name": "Consistency",
            "last_name": "Test",
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
                
                # Check required fields
                required_fields = ['message', 'user_id']
                missing_fields = [field for field in required_fields if field not in data]
                
                if not missing_fields:
                    # Check if enrollment_id is present for student with course data
                    if 'enrollment_id' in data:
                        self.log_test(test_name, True, 
                            "Response includes all required fields including enrollment_id")
                    else:
                        self.log_test(test_name, True, 
                            "Response includes required fields (enrollment_id may be handled separately)")
                    return True
                else:
                    self.log_test(test_name, False, 
                        f"Response missing required fields: {missing_fields}",
                        {"response": data})
                    return False
            else:
                self.log_test(test_name, False, 
                    f"Registration failed with status {response.status_code}",
                    {"response_text": response.text})
                return False
                
        except Exception as e:
            self.log_test(test_name, False, f"Error during registration: {e}")
            return False

    def test_courses_api_response_structure(self):
        """Test that courses API returns consistent response structure"""
        test_name = "Courses API Response Structure"
        
        try:
            response = requests.get(f"{BASE_URL}/api/courses/public/all")
            
            if response.status_code == 200:
                data = response.json()
                
                # Check top-level structure
                if 'courses' in data:
                    courses = data['courses']
                    if courses:
                        # Check first course structure
                        first_course = courses[0]
                        expected_fields = ['id', 'title', 'masters', 'students']
                        missing_fields = [field for field in expected_fields if field not in first_course]
                        
                        if not missing_fields:
                            # Verify count fields are numeric
                            masters_count = first_course.get('masters', 0)
                            students_count = first_course.get('students', 0)
                            
                            if isinstance(masters_count, (int, float)) and isinstance(students_count, (int, float)):
                                self.log_test(test_name, True, 
                                    f"Response structure consistent with {len(courses)} courses")
                                return True
                            else:
                                self.log_test(test_name, False, 
                                    "Count fields are not numeric",
                                    {"masters_type": type(masters_count), "students_type": type(students_count)})
                                return False
                        else:
                            self.log_test(test_name, False, 
                                f"Course missing required fields: {missing_fields}",
                                {"first_course": first_course})
                            return False
                    else:
                        self.log_test(test_name, True, 
                            "API works but no courses found")
                        return True
                else:
                    self.log_test(test_name, False, 
                        "Response missing 'courses' field",
                        {"response": data})
                    return False
            else:
                self.log_test(test_name, False, 
                    f"API call failed with status {response.status_code}",
                    {"response_text": response.text})
                return False
                
        except Exception as e:
            self.log_test(test_name, False, f"Error during API call: {e}")
            return False

    def test_categories_api_response_structure(self):
        """Test that categories API returns consistent response structure"""
        test_name = "Categories API Response Structure"
        
        try:
            response = requests.get(f"{BASE_URL}/api/categories/public/all")
            
            if response.status_code == 200:
                data = response.json()
                
                # Check top-level structure
                if 'categories' in data:
                    categories = data['categories']
                    if categories:
                        # Check first category structure
                        first_category = categories[0]
                        expected_fields = ['id', 'name']
                        missing_fields = [field for field in expected_fields if field not in first_category]
                        
                        if not missing_fields:
                            self.log_test(test_name, True, 
                                f"Response structure consistent with {len(categories)} categories")
                            return True
                        else:
                            self.log_test(test_name, False, 
                                f"Category missing required fields: {missing_fields}",
                                {"first_category": first_category})
                            return False
                    else:
                        self.log_test(test_name, True, 
                            "API works but no categories found")
                        return True
                else:
                    self.log_test(test_name, False, 
                        "Response missing 'categories' field",
                        {"response": data})
                    return False
            else:
                self.log_test(test_name, False, 
                    f"API call failed with status {response.status_code}",
                    {"response_text": response.text})
                return False
                
        except Exception as e:
            self.log_test(test_name, False, f"Error during API call: {e}")
            return False

    def test_locations_api_response_structure(self):
        """Test that locations API returns consistent response structure"""
        test_name = "Locations API Response Structure"
        
        try:
            response = requests.get(f"{BASE_URL}/api/locations/public/with-branches")
            
            if response.status_code == 200:
                data = response.json()
                
                # Check top-level structure
                if 'locations' in data:
                    locations = data['locations']
                    if locations:
                        # Check first location structure
                        first_location = locations[0]
                        expected_fields = ['id', 'name']
                        missing_fields = [field for field in expected_fields if field not in first_location]
                        
                        if not missing_fields:
                            # Check if branches are included
                            if 'branches' in first_location:
                                branches = first_location['branches']
                                if branches:
                                    first_branch = branches[0]
                                    branch_expected_fields = ['id', 'name']
                                    branch_missing_fields = [field for field in branch_expected_fields if field not in first_branch]
                                    
                                    if not branch_missing_fields:
                                        self.log_test(test_name, True, 
                                            f"Response structure consistent with {len(locations)} locations and nested branches")
                                        return True
                                    else:
                                        self.log_test(test_name, False, 
                                            f"Branch missing required fields: {branch_missing_fields}",
                                            {"first_branch": first_branch})
                                        return False
                                else:
                                    self.log_test(test_name, True, 
                                        f"Response structure consistent with {len(locations)} locations (no branches)")
                                    return True
                            else:
                                self.log_test(test_name, True, 
                                    f"Response structure consistent with {len(locations)} locations (branches not included)")
                                return True
                        else:
                            self.log_test(test_name, False, 
                                f"Location missing required fields: {missing_fields}",
                                {"first_location": first_location})
                            return False
                    else:
                        self.log_test(test_name, True, 
                            "API works but no locations found")
                        return True
                else:
                    self.log_test(test_name, False, 
                        "Response missing 'locations' field",
                        {"response": data})
                    return False
            else:
                self.log_test(test_name, False, 
                    f"API call failed with status {response.status_code}",
                    {"response_text": response.text})
                return False
                
        except Exception as e:
            self.log_test(test_name, False, f"Error during API call: {e}")
            return False

    def run_all_tests(self):
        """Run all API response consistency tests"""
        print("🧪 Testing API Response Consistency...")
        print("=" * 60)
        
        # Test 1: Registration API response structure
        self.test_registration_response_structure()
        
        # Test 2: Courses API response structure
        self.test_courses_api_response_structure()
        
        # Test 3: Categories API response structure
        self.test_categories_api_response_structure()
        
        # Test 4: Locations API response structure
        self.test_locations_api_response_structure()
        
        # Print summary
        print("\n" + "=" * 60)
        print("📊 API RESPONSE CONSISTENCY TEST SUMMARY")
        print("=" * 60)
        
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
            print("\n🎉 All API response consistency tests passed!")
        else:
            print(f"\n⚠️  {len(failed_tests)} tests failed. Consistency issues detected.")
        
        return len(failed_tests) == 0

def main():
    tester = APIResponseConsistencyTester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
