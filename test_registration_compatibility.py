#!/usr/bin/env python3
"""
Test Registration API Backward Compatibility

This script tests the registration API to ensure it maintains backward compatibility
after the data architecture changes.
"""

import requests
import json
import time
import sys
from datetime import datetime

BASE_URL = "http://31.97.224.169:8003"

class RegistrationCompatibilityTester:
    def __init__(self):
        self.test_results = []
        self.test_user_ids = []  # Track created users for cleanup
    
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

    def test_registration_payload_acceptance(self):
        """Test that registration API accepts the same payload structure as before"""
        test_name = "Registration Payload Acceptance"
        
        # Test payload with course and branch data (legacy format)
        test_payload = {
            "email": f"test_compat_{int(time.time())}@example.com",
            "phone": f"123456{int(time.time()) % 10000}",
            "first_name": "Test",
            "last_name": "User",
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
                user_id = data.get('user_id')
                if user_id:
                    self.test_user_ids.append(user_id)
                
                # Check response structure
                expected_fields = ['message', 'user_id']
                has_all_fields = all(field in data for field in expected_fields)
                
                if has_all_fields:
                    self.log_test(test_name, True, 
                        f"API accepts legacy payload and returns expected response structure")
                    return data
                else:
                    self.log_test(test_name, False, 
                        f"Response missing expected fields", 
                        {"response": data, "expected_fields": expected_fields})
                    return None
            else:
                self.log_test(test_name, False, 
                    f"Registration failed with status {response.status_code}", 
                    {"response_text": response.text})
                return None
                
        except Exception as e:
            self.log_test(test_name, False, f"Error during registration: {e}")
            return None

    def test_enrollment_record_creation(self, user_data):
        """Test that enrollment records are created when course data is provided"""
        test_name = "Enrollment Record Creation"
        
        if not user_data or not user_data.get('user_id'):
            self.log_test(test_name, False, "No user data available for testing")
            return False
        
        user_id = user_data['user_id']
        
        # For now, we'll test this by checking if the API indicates enrollment creation
        # In a full implementation, we'd query the database directly
        enrollment_id = user_data.get('enrollment_id')
        
        if enrollment_id:
            self.log_test(test_name, True, 
                f"Enrollment record created with ID: {enrollment_id}")
            return True
        else:
            # Check if the message indicates enrollment was handled
            message = user_data.get('message', '')
            if 'enrolled' in message.lower():
                self.log_test(test_name, True, 
                    f"Enrollment indicated in response message: {message}")
                return True
            else:
                self.log_test(test_name, False, 
                    "No enrollment record created or indicated in response",
                    {"response": user_data})
                return False

    def test_response_format_consistency(self, user_data):
        """Test that response format is consistent with previous versions"""
        test_name = "Response Format Consistency"
        
        if not user_data:
            self.log_test(test_name, False, "No user data available for testing")
            return False
        
        # Expected response structure
        expected_structure = {
            'message': str,
            'user_id': str
        }
        
        # Optional fields that might be present
        optional_fields = ['enrollment_id']
        
        issues = []
        
        # Check required fields
        for field, expected_type in expected_structure.items():
            if field not in user_data:
                issues.append(f"Missing required field: {field}")
            elif not isinstance(user_data[field], expected_type):
                issues.append(f"Field {field} has wrong type: expected {expected_type.__name__}, got {type(user_data[field]).__name__}")
        
        # Check for unexpected fields (excluding optional ones)
        allowed_fields = set(expected_structure.keys()).union(set(optional_fields))
        unexpected_fields = set(user_data.keys()) - allowed_fields
        
        if unexpected_fields:
            issues.append(f"Unexpected fields in response: {list(unexpected_fields)}")
        
        if not issues:
            self.log_test(test_name, True, "Response format is consistent")
            return True
        else:
            self.log_test(test_name, False, "Response format issues found", 
                {"issues": issues, "response": user_data})
            return False

    def test_registration_without_course_data(self):
        """Test registration without course data (should still work)"""
        test_name = "Registration Without Course Data"
        
        test_payload = {
            "email": f"test_no_course_{int(time.time())}@example.com",
            "phone": f"987654{int(time.time()) % 10000}",
            "first_name": "Test",
            "last_name": "NoCourse",
            "role": "student",
            "password": "TestPassword123!",
            "date_of_birth": "1990-01-01",
            "gender": "female"
        }
        
        try:
            response = requests.post(f"{BASE_URL}/api/auth/register", json=test_payload)
            
            if response.status_code == 200:
                data = response.json()
                user_id = data.get('user_id')
                if user_id:
                    self.test_user_ids.append(user_id)
                
                self.log_test(test_name, True, 
                    "Registration works without course data")
                return True
            else:
                self.log_test(test_name, False, 
                    f"Registration failed with status {response.status_code}",
                    {"response_text": response.text})
                return False
                
        except Exception as e:
            self.log_test(test_name, False, f"Error during registration: {e}")
            return False

    def test_staff_registration(self):
        """Test registration for staff members (coaches, admins)"""
        test_name = "Staff Registration"
        
        test_payload = {
            "email": f"test_coach_{int(time.time())}@example.com",
            "phone": f"555123{int(time.time()) % 10000}",
            "first_name": "Test",
            "last_name": "Coach",
            "role": "coach",
            "password": "TestPassword123!",
            "branch_id": "test-branch-id"
        }
        
        try:
            response = requests.post(f"{BASE_URL}/api/auth/register", json=test_payload)
            
            if response.status_code == 200:
                data = response.json()
                user_id = data.get('user_id')
                if user_id:
                    self.test_user_ids.append(user_id)
                
                self.log_test(test_name, True, 
                    "Staff registration works with branch_id")
                return True
            else:
                self.log_test(test_name, False, 
                    f"Staff registration failed with status {response.status_code}",
                    {"response_text": response.text})
                return False
                
        except Exception as e:
            self.log_test(test_name, False, f"Error during staff registration: {e}")
            return False

    def run_all_tests(self):
        """Run all registration compatibility tests"""
        print("🧪 Testing Registration API Backward Compatibility...")
        print("=" * 60)
        
        # Test 1: Basic payload acceptance and response format
        user_data = self.test_registration_payload_acceptance()
        
        # Test 2: Enrollment record creation
        self.test_enrollment_record_creation(user_data)
        
        # Test 3: Response format consistency
        self.test_response_format_consistency(user_data)
        
        # Test 4: Registration without course data
        self.test_registration_without_course_data()
        
        # Test 5: Staff registration
        self.test_staff_registration()
        
        # Print summary
        print("\n" + "=" * 60)
        print("📊 REGISTRATION API COMPATIBILITY TEST SUMMARY")
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
            print("\n🎉 All registration compatibility tests passed!")
        else:
            print(f"\n⚠️  {len(failed_tests)} tests failed. Compatibility issues detected.")
        
        print(f"\n📝 Created {len(self.test_user_ids)} test users during testing")
        
        return len(failed_tests) == 0

def main():
    tester = RegistrationCompatibilityTester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
