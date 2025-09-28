#!/usr/bin/env python3
"""
Comprehensive Authentication System Testing Script
Tests all authentication flows, token validation, and role-based access control
"""

import requests
import json
import time
import jwt
from datetime import datetime, timedelta
from typing import Dict, Any, Optional

class AuthenticationTester:
    def __init__(self, base_url: str = "http://31.97.224.169:8003"):
        self.base_url = base_url
        self.tokens = {}
        self.users = {}
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
            
            if response.status_code == expected_status:
                return response.json() if response.content else {}
            else:
                print(f"   Status: {response.status_code}, Expected: {expected_status}")
                print(f"   Response: {response.text}")
                return None
                
        except requests.exceptions.ConnectionError:
            print(f"   ❌ Connection error - Server not running on {self.base_url}")
            return None
        except Exception as e:
            print(f"   ❌ Error: {e}")
            return None
    
    def decode_token(self, token: str) -> Optional[Dict]:
        """Decode JWT token without verification for testing"""
        try:
            # Decode without verification to inspect payload
            decoded = jwt.decode(token, options={"verify_signature": False})
            return decoded
        except Exception as e:
            print(f"   ❌ Token decode error: {e}")
            return None
    
    def test_superadmin_authentication(self):
        """Test superadmin authentication flow"""
        print("\n🔐 Testing SuperAdmin Authentication...")
        
        # Test superadmin registration
        register_data = {
            "email": "testsuperadmin@example.com",
            "password": "TestSuperAdmin123!",
            "name": "Test Super Admin"
        }
        
        # Try registration (might fail if user exists, that's OK)
        result = self.make_request("POST", "/superadmin/register", register_data, expected_status=201)
        if result:
            self.log_result("SuperAdmin registration", True)
        else:
            self.log_result("SuperAdmin registration", False, "User might already exist")
        
        # Test superadmin login
        login_data = {
            "email": "testsuperadmin@example.com",
            "password": "TestSuperAdmin123!"
        }
        
        result = self.make_request("POST", "/superadmin/login", login_data)
        if result and "data" in result and "token" in result["data"]:
            token = result["data"]["token"]
            self.tokens["superadmin"] = token
            self.users["superadmin"] = result["data"]
            self.log_result("SuperAdmin login", True)
            
            # Decode and verify token structure
            decoded = self.decode_token(token)
            if decoded:
                expected_fields = ["sub", "role", "exp"]
                has_all_fields = all(field in decoded for field in expected_fields)
                self.log_result("SuperAdmin token structure", has_all_fields, 
                              f"Token payload: {decoded}")
                
                # Check role
                role_correct = decoded.get("role") == "superadmin"
                self.log_result("SuperAdmin token role", role_correct, 
                              f"Role: {decoded.get('role')}")
            
            # Test token verification
            verify_result = self.make_request("GET", "/superadmin/verify-token", 
                                            token=token)
            self.log_result("SuperAdmin token verification", verify_result is not None)
            
            # Test superadmin me endpoint
            me_result = self.make_request("GET", "/superadmin/me", token=token)
            self.log_result("SuperAdmin me endpoint", me_result is not None)
            
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
            "role": "student",
            "gender": "male",
            "date_of_birth": "1995-01-01"
        }
        
        result = self.make_request("POST", "/auth/register", register_data, expected_status=201)
        if result:
            self.log_result("User registration", True)
        else:
            self.log_result("User registration", False, "User might already exist")
        
        # Test user login
        login_data = {
            "email": "testuser@example.com",
            "password": "TestUser123!"
        }
        
        result = self.make_request("POST", "/auth/login", login_data)
        if result and "access_token" in result:
            token = result["access_token"]
            self.tokens["user"] = token
            self.users["user"] = result
            self.log_result("User login", True)
            
            # Decode and verify token structure
            decoded = self.decode_token(token)
            if decoded:
                expected_fields = ["sub", "exp"]
                has_all_fields = all(field in decoded for field in expected_fields)
                self.log_result("User token structure", has_all_fields, 
                              f"Token payload: {decoded}")
            
            # Test user me endpoint
            me_result = self.make_request("GET", "/auth/me", token=token)
            self.log_result("User me endpoint", me_result is not None)
            
        else:
            self.log_result("User login", False, "Failed to get token")
    
    def test_coach_authentication(self):
        """Test coach authentication flow"""
        print("\n👨‍🏫 Testing Coach Authentication...")
        
        # First create a coach (requires superadmin token)
        if "superadmin" not in self.tokens:
            self.log_result("Coach authentication", False, "No superadmin token for coach creation")
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
        if result:
            self.log_result("Coach creation", True)
        else:
            self.log_result("Coach creation", False, "Coach might already exist")
        
        # Test coach login
        coach_login_data = {
            "email": "testcoach@example.com",
            "password": "TestCoach123!"
        }
        
        result = self.make_request("POST", "/coaches/login", coach_login_data)
        if result and "access_token" in result:
            token = result["access_token"]
            self.tokens["coach"] = token
            self.users["coach"] = result
            self.log_result("Coach login", True)
            
            # Decode and verify token structure
            decoded = self.decode_token(token)
            if decoded:
                expected_fields = ["sub", "role", "exp"]
                has_all_fields = all(field in decoded for field in expected_fields)
                self.log_result("Coach token structure", has_all_fields, 
                              f"Token payload: {decoded}")
                
                # Check role
                role_correct = decoded.get("role") == "coach"
                self.log_result("Coach token role", role_correct, 
                              f"Role: {decoded.get('role')}")
            
        else:
            self.log_result("Coach login", False, "Failed to get token")
    
    def test_role_based_access_control(self):
        """Test role-based access control"""
        print("\n🛡️ Testing Role-Based Access Control...")
        
        # Test superadmin access to protected endpoints
        if "superadmin" in self.tokens:
            # Should have access to branch creation
            branch_data = {
                "branch": {
                    "name": "Test Branch",
                    "code": "TB001",
                    "email": "test@branch.com",
                    "phone": "+1234567890",
                    "address": {
                        "line1": "123 Test St",
                        "area": "Test Area",
                        "city": "Test City",
                        "state": "Test State",
                        "pincode": "123456",
                        "country": "Test Country"
                    }
                }
            }
            
            result = self.make_request("POST", "/branches", branch_data, 
                                     token=self.tokens["superadmin"], expected_status=201)
            self.log_result("SuperAdmin branch creation access", result is not None)
            
            # Should have access to coach list
            result = self.make_request("GET", "/coaches", token=self.tokens["superadmin"])
            self.log_result("SuperAdmin coach list access", result is not None)
        
        # Test user access restrictions
        if "user" in self.tokens:
            # Should NOT have access to branch creation
            result = self.make_request("POST", "/branches", {}, 
                                     token=self.tokens["user"], expected_status=403)
            self.log_result("User branch creation restriction", result is None)
            
            # Should have access to own profile
            result = self.make_request("GET", "/auth/me", token=self.tokens["user"])
            self.log_result("User profile access", result is not None)
    
    def test_token_expiration(self):
        """Test token expiration handling"""
        print("\n⏰ Testing Token Expiration...")
        
        # Create a token with very short expiration for testing
        import jwt
        import os
        
        secret_key = os.getenv("SECRET_KEY", "student_management_secret_key_2025")
        
        # Create expired token
        expired_payload = {
            "sub": "test-user-id",
            "role": "student",
            "exp": datetime.utcnow() - timedelta(minutes=1)  # Expired 1 minute ago
        }
        
        expired_token = jwt.encode(expired_payload, secret_key, algorithm="HS256")
        
        # Test with expired token
        result = self.make_request("GET", "/auth/me", token=expired_token, expected_status=401)
        self.log_result("Expired token rejection", result is None)
    
    def test_invalid_tokens(self):
        """Test invalid token handling"""
        print("\n🚫 Testing Invalid Token Handling...")
        
        # Test with malformed token
        result = self.make_request("GET", "/auth/me", token="invalid-token", expected_status=401)
        self.log_result("Malformed token rejection", result is None)
        
        # Test with no token
        result = self.make_request("GET", "/auth/me", expected_status=401)
        self.log_result("No token rejection", result is None)
        
        # Test with wrong secret
        import jwt
        wrong_payload = {
            "sub": "test-user-id",
            "role": "student",
            "exp": datetime.utcnow() + timedelta(hours=1)
        }
        
        wrong_token = jwt.encode(wrong_payload, "wrong-secret", algorithm="HS256")
        result = self.make_request("GET", "/auth/me", token=wrong_token, expected_status=401)
        self.log_result("Wrong secret token rejection", result is None)
    
    def run_all_tests(self):
        """Run all authentication tests"""
        print("🚀 Starting Comprehensive Authentication Testing...")
        print(f"Base URL: {self.base_url}")
        print("=" * 60)
        
        start_time = time.time()
        
        # Run all test suites
        self.test_superadmin_authentication()
        self.test_user_authentication()
        self.test_coach_authentication()
        self.test_role_based_access_control()
        self.test_token_expiration()
        self.test_invalid_tokens()
        
        # Print summary
        end_time = time.time()
        duration = end_time - start_time
        
        print("\n" + "=" * 60)
        print("📊 AUTHENTICATION TEST SUMMARY")
        print("=" * 60)
        print(f"✅ Passed: {self.results['passed']}")
        print(f"❌ Failed: {self.results['failed']}")
        print(f"⏱️  Duration: {duration:.2f} seconds")
        
        if self.results["errors"]:
            print("\n❌ FAILED TESTS:")
            for error in self.results["errors"]:
                print(f"   • {error}")
        
        # Print token summary
        print(f"\n🔑 TOKENS OBTAINED:")
        for user_type, token in self.tokens.items():
            print(f"   • {user_type}: {token[:50]}...")
        
        success_rate = (self.results['passed'] / (self.results['passed'] + self.results['failed'])) * 100
        print(f"\n🎯 Success Rate: {success_rate:.1f}%")
        
        if success_rate >= 90:
            print("🎉 AUTHENTICATION STATUS: EXCELLENT")
        elif success_rate >= 80:
            print("✅ AUTHENTICATION STATUS: GOOD")
        elif success_rate >= 60:
            print("⚠️  AUTHENTICATION STATUS: NEEDS IMPROVEMENT")
        else:
            print("🚨 AUTHENTICATION STATUS: CRITICAL ISSUES")

if __name__ == "__main__":
    tester = AuthenticationTester()
    tester.run_all_tests()
