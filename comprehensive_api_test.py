#!/usr/bin/env python3
"""
Comprehensive API Testing Script for Marshalats Learning Management System
Tests all endpoints with proper authentication and data validation
"""

import requests
import json
import time
from datetime import datetime
from typing import Dict, Any, Optional

class APITester:
    def __init__(self, base_url: str = "http://localhost:8003"):
        self.base_url = base_url
        self.tokens = {}
        self.test_data = {}
        self.results = {
            "passed": 0,
            "failed": 0,
            "errors": []
        }
    
    def log_result(self, test_name: str, success: bool, message: str = ""):
        """Log test results"""
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status}: {test_name}")
        if message:
            print(f"   {message}")
        
        if success:
            self.results["passed"] += 1
        else:
            self.results["failed"] += 1
            self.results["errors"].append(f"{test_name}: {message}")
    
    def make_request(self, method: str, endpoint: str, data: Dict = None, 
                    token: str = None, expected_status: int = 200) -> Optional[Dict]:
        """Make HTTP request with error handling"""
        url = f"{self.base_url}{endpoint}"
        headers = {"Content-Type": "application/json"}
        
        if token:
            headers["Authorization"] = f"Bearer {token}"
        
        try:
            if method.upper() == "GET":
                response = requests.get(url, headers=headers, timeout=10)
            elif method.upper() == "POST":
                response = requests.post(url, json=data, headers=headers, timeout=10)
            elif method.upper() == "PUT":
                response = requests.put(url, json=data, headers=headers, timeout=10)
            elif method.upper() == "DELETE":
                response = requests.delete(url, headers=headers, timeout=10)
            else:
                raise ValueError(f"Unsupported method: {method}")
            
            if response.status_code == expected_status:
                return response.json() if response.content else {}
            else:
                print(f"   Status: {response.status_code}, Expected: {expected_status}")
                print(f"   Response: {response.text}")
                return None
                
        except requests.exceptions.ConnectionError:
            print(f"   ❌ Connection error - Server not running on {self.base_url}")
            return None
        except requests.exceptions.Timeout:
            print(f"   ❌ Request timeout")
            return None
        except Exception as e:
            print(f"   ❌ Error: {e}")
            return None
    
    def test_health_check(self):
        """Test basic health endpoints"""
        print("\n🏥 Testing Health Endpoints...")
        
        # Test root endpoint
        result = self.make_request("GET", "/")
        self.log_result("Root endpoint", result is not None)
        
        # Test health endpoint
        result = self.make_request("GET", "/health")
        self.log_result("Health endpoint", result is not None)
    
    def test_superadmin_authentication(self):
        """Test superadmin authentication flow"""
        print("\n🔐 Testing SuperAdmin Authentication...")
        
        # Test superadmin registration (if needed)
        register_data = {
            "email": "testsuperadmin@example.com",
            "password": "TestSuperAdmin123!",
            "name": "Test Super Admin"
        }
        
        # Try registration (might fail if user exists)
        self.make_request("POST", "/superadmin/register", register_data, expected_status=201)
        
        # Test superadmin login
        login_data = {
            "email": "testsuperadmin@example.com",
            "password": "TestSuperAdmin123!"
        }
        
        result = self.make_request("POST", "/superadmin/login", login_data)
        if result and "data" in result and "token" in result["data"]:
            self.tokens["superadmin"] = result["data"]["token"]
            self.log_result("SuperAdmin login", True)
            
            # Test token verification
            verify_result = self.make_request("GET", "/superadmin/verify-token", 
                                            token=self.tokens["superadmin"])
            self.log_result("SuperAdmin token verification", verify_result is not None)
        else:
            self.log_result("SuperAdmin login", False, "Failed to get token")
    
    def test_user_authentication(self):
        """Test regular user authentication flow"""
        print("\n👤 Testing User Authentication...")
        
        # Test user registration
        register_data = {
            "email": "testuser@example.com",
            "password": "TestUser123!",
            "first_name": "Test",
            "last_name": "User",
            "mobile": "+1234567890",
            "role": "student"
        }
        
        result = self.make_request("POST", "/auth/register", register_data, expected_status=201)
        self.log_result("User registration", result is not None)
        
        # Test user login
        login_data = {
            "email": "testuser@example.com",
            "password": "TestUser123!"
        }
        
        result = self.make_request("POST", "/auth/login", login_data)
        if result and "access_token" in result:
            self.tokens["user"] = result["access_token"]
            self.log_result("User login", True)
        else:
            self.log_result("User login", False, "Failed to get token")
    
    def test_branch_management(self):
        """Test branch management endpoints"""
        print("\n🏢 Testing Branch Management...")
        
        if "superadmin" not in self.tokens:
            self.log_result("Branch tests", False, "No superadmin token available")
            return
        
        # Test branch creation
        branch_data = {
            "branch": {
                "name": "Test Martial Arts Branch",
                "code": "TMAB01",
                "email": "test@branch.com",
                "phone": "+1234567890",
                "address": {
                    "line1": "123 Test Street",
                    "area": "Test Area",
                    "city": "Test City",
                    "state": "Test State",
                    "pincode": "123456",
                    "country": "Test Country"
                }
            },
            "manager_id": "test-manager-id",
            "operational_details": {
                "courses_offered": ["Karate", "Taekwondo"],
                "timings": [
                    {"day": "Monday", "open": "09:00", "close": "18:00"}
                ],
                "holidays": ["2025-12-25"]
            },
            "assignments": {
                "accessories_available": True,
                "courses": ["Karate"],
                "branch_admins": ["admin-1"]
            },
            "bank_details": {
                "bank_name": "Test Bank",
                "account_number": "1234567890",
                "upi_id": "test@upi"
            }
        }
        
        result = self.make_request("POST", "/branches", branch_data, 
                                 token=self.tokens["superadmin"], expected_status=201)
        if result and "branch_id" in result:
            branch_id = result["branch_id"]
            self.test_data["branch_id"] = branch_id
            self.log_result("Branch creation", True)
            
            # Test get branch
            get_result = self.make_request("GET", f"/branches/{branch_id}", 
                                         token=self.tokens["superadmin"])
            self.log_result("Get branch by ID", get_result is not None)
            
            # Test list branches
            list_result = self.make_request("GET", "/branches", 
                                          token=self.tokens["superadmin"])
            self.log_result("List branches", list_result is not None)
        else:
            self.log_result("Branch creation", False, "Failed to create branch")
    
    def test_course_management(self):
        """Test course management endpoints"""
        print("\n📚 Testing Course Management...")
        
        if "superadmin" not in self.tokens:
            self.log_result("Course tests", False, "No superadmin token available")
            return
        
        # Test course creation
        course_data = {
            "title": "Test Karate Course",
            "code": "TKC001",
            "description": "A comprehensive test karate course",
            "difficulty_level": "Beginner",
            "pricing": {
                "currency": "USD",
                "amount": 100.0
            },
            "settings": {
                "active": True,
                "offers_certification": True
            }
        }
        
        result = self.make_request("POST", "/courses", course_data, 
                                 token=self.tokens["superadmin"], expected_status=201)
        if result and "course_id" in result:
            course_id = result["course_id"]
            self.test_data["course_id"] = course_id
            self.log_result("Course creation", True)
            
            # Test get course
            get_result = self.make_request("GET", f"/courses/{course_id}", 
                                         token=self.tokens["superadmin"])
            self.log_result("Get course by ID", get_result is not None)
            
            # Test list courses
            list_result = self.make_request("GET", "/courses", 
                                          token=self.tokens["superadmin"])
            self.log_result("List courses", list_result is not None)
        else:
            self.log_result("Course creation", False, "Failed to create course")
    
    def test_coach_management(self):
        """Test coach management endpoints"""
        print("\n👨‍🏫 Testing Coach Management...")
        
        if "superadmin" not in self.tokens:
            self.log_result("Coach tests", False, "No superadmin token available")
            return
        
        # Test coach creation
        coach_data = {
            "email": "testcoach@example.com",
            "password": "TestCoach123!",
            "first_name": "Test",
            "last_name": "Coach",
            "mobile": "+1234567891",
            "specializations": ["Karate", "Taekwondo"],
            "experience_years": 5
        }
        
        result = self.make_request("POST", "/coaches", coach_data, 
                                 token=self.tokens["superadmin"], expected_status=201)
        if result and "coach_id" in result:
            coach_id = result["coach_id"]
            self.test_data["coach_id"] = coach_id
            self.log_result("Coach creation", True)
            
            # Test coach login
            coach_login_data = {
                "email": "testcoach@example.com",
                "password": "TestCoach123!"
            }
            
            login_result = self.make_request("POST", "/coaches/login", coach_login_data)
            if login_result and "access_token" in login_result:
                self.tokens["coach"] = login_result["access_token"]
                self.log_result("Coach login", True)
            else:
                self.log_result("Coach login", False)
        else:
            self.log_result("Coach creation", False, "Failed to create coach")
    
    def test_enrollment_management(self):
        """Test enrollment management endpoints"""
        print("\n📝 Testing Enrollment Management...")

        if "superadmin" not in self.tokens or "course_id" not in self.test_data:
            self.log_result("Enrollment tests", False, "Missing prerequisites")
            return

        # Test student enrollment
        enrollment_data = {
            "student_id": "test-student-id",
            "course_id": self.test_data["course_id"],
            "branch_id": self.test_data.get("branch_id", "test-branch-id"),
            "enrollment_date": datetime.now().isoformat()
        }

        result = self.make_request("POST", "/enrollments", enrollment_data,
                                 token=self.tokens["superadmin"], expected_status=201)
        if result:
            self.log_result("Enrollment creation", True)

            # Test get enrollments
            list_result = self.make_request("GET", "/enrollments",
                                          token=self.tokens["superadmin"])
            self.log_result("List enrollments", list_result is not None)
        else:
            self.log_result("Enrollment creation", False)

    def test_payment_management(self):
        """Test payment management endpoints"""
        print("\n💳 Testing Payment Management...")

        if "user" not in self.tokens:
            self.log_result("Payment tests", False, "No user token available")
            return

        # Test student payment
        payment_data = {
            "amount": 100.0,
            "currency": "USD",
            "payment_method": "card",
            "course_id": self.test_data.get("course_id", "test-course-id")
        }

        result = self.make_request("POST", "/payments/students/payments", payment_data,
                                 token=self.tokens["user"], expected_status=201)
        self.log_result("Student payment", result is not None)

    def test_event_management(self):
        """Test event management endpoints"""
        print("\n🎉 Testing Event Management...")

        if "superadmin" not in self.tokens:
            self.log_result("Event tests", False, "No superadmin token available")
            return

        # Test event creation
        event_data = {
            "title": "Test Martial Arts Tournament",
            "description": "A test tournament event",
            "event_date": "2025-06-15T10:00:00",
            "location": "Test Venue",
            "max_participants": 50
        }

        result = self.make_request("POST", "/events", event_data,
                                 token=self.tokens["superadmin"], expected_status=201)
        if result and "event_id" in result:
            event_id = result["event_id"]
            self.log_result("Event creation", True)

            # Test get event
            get_result = self.make_request("GET", f"/events/{event_id}",
                                         token=self.tokens["superadmin"])
            self.log_result("Get event by ID", get_result is not None)
        else:
            self.log_result("Event creation", False)

    def test_request_management(self):
        """Test request management endpoints"""
        print("\n📋 Testing Request Management...")

        if "user" not in self.tokens:
            self.log_result("Request tests", False, "No user token available")
            return

        # Test transfer request
        transfer_data = {
            "current_branch_id": self.test_data.get("branch_id", "test-branch-id"),
            "requested_branch_id": "new-branch-id",
            "reason": "Moving to new location"
        }

        result = self.make_request("POST", "/requests/transfer", transfer_data,
                                 token=self.tokens["user"], expected_status=201)
        self.log_result("Transfer request", result is not None)

        # Test course change request
        course_change_data = {
            "current_course_id": self.test_data.get("course_id", "test-course-id"),
            "requested_course_id": "new-course-id",
            "reason": "Want to try different martial art"
        }

        result = self.make_request("POST", "/requests/course-change", course_change_data,
                                 token=self.tokens["user"], expected_status=201)
        self.log_result("Course change request", result is not None)

    def run_all_tests(self):
        """Run all API tests"""
        print("🚀 Starting Comprehensive API Testing...")
        print(f"Base URL: {self.base_url}")
        print("=" * 60)

        start_time = time.time()

        # Run all test suites
        self.test_health_check()
        self.test_superadmin_authentication()
        self.test_user_authentication()
        self.test_branch_management()
        self.test_course_management()
        self.test_coach_management()
        self.test_enrollment_management()
        self.test_payment_management()
        self.test_event_management()
        self.test_request_management()

        # Print summary
        end_time = time.time()
        duration = end_time - start_time

        print("\n" + "=" * 60)
        print("📊 TEST SUMMARY")
        print("=" * 60)
        print(f"✅ Passed: {self.results['passed']}")
        print(f"❌ Failed: {self.results['failed']}")
        print(f"⏱️  Duration: {duration:.2f} seconds")

        if self.results["errors"]:
            print("\n❌ FAILED TESTS:")
            for error in self.results["errors"]:
                print(f"   • {error}")

        success_rate = (self.results['passed'] / (self.results['passed'] + self.results['failed'])) * 100
        print(f"\n🎯 Success Rate: {success_rate:.1f}%")

        if success_rate >= 80:
            print("🎉 OVERALL STATUS: GOOD")
        elif success_rate >= 60:
            print("⚠️  OVERALL STATUS: NEEDS IMPROVEMENT")
        else:
            print("🚨 OVERALL STATUS: CRITICAL ISSUES")

if __name__ == "__main__":
    tester = APITester()
    tester.run_all_tests()
