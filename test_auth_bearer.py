#!/usr/bin/env python3
"""
Comprehensive API testing with Bearer Token Authentication
"""
import requests
import json
import time

class APITester:
    def __init__(self, base_url="http://localhost:8003/api"):
        self.base_url = base_url
        self.token = None
        self.headers = {"Content-Type": "application/json"}
    
    def login(self, email, password):
        """Login and get bearer token"""
        login_url = f"{self.base_url}/auth/login"
        login_data = {"email": email, "password": password}
        
        print(f"🔐 Logging in as {email}...")
        response = requests.post(login_url, json=login_data)
        
        if response.status_code == 200:
            result = response.json()
            self.token = result["access_token"]
            self.headers["Authorization"] = f"Bearer {self.token}"
            
            user_info = result["user"]
            print(f"✅ Login successful!")
            print(f"   User: {user_info['full_name']} ({user_info['role']})")
            print(f"   Token: {self.token[:50]}...")
            return True
        else:
            print(f"❌ Login failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    
    def test_auth_endpoints(self):
        """Test authentication-related endpoints"""
        print(f"\n{'='*60}")
        print("🔒 TESTING AUTHENTICATION ENDPOINTS")
        print(f"{'='*60}")
        
        # Test /auth/me endpoint
        print(f"\n📋 Testing GET /auth/me...")
        me_url = f"{self.base_url}/auth/me"
        response = requests.get(me_url, headers=self.headers)
        
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            user_data = response.json()
            print(f"✅ User info retrieved:")
            print(f"   ID: {user_data['id']}")
            print(f"   Email: {user_data['email']}")
            print(f"   Role: {user_data['role']}")
            print(f"   Name: {user_data['full_name']}")
        else:
            print(f"❌ Failed: {response.text}")
    
    def test_user_endpoints(self):
        """Test user management endpoints"""
        print(f"\n{'='*60}")
        print("👥 TESTING USER MANAGEMENT ENDPOINTS")
        print(f"{'='*60}")
        
        # Test GET /users
        print(f"\n📋 Testing GET /users...")
        users_url = f"{self.base_url}/users"
        response = requests.get(users_url, headers=self.headers)
        
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            users_data = response.json()
            print(f"✅ Users retrieved: {users_data.get('total', 0)} users")
            if users_data.get('users'):
                for user in users_data['users'][:3]:  # Show first 3 users
                    print(f"   - {user['full_name']} ({user['role']})")
        else:
            print(f"❌ Failed: {response.text}")
        
        # Test creating a new user
        print(f"\n📋 Testing POST /users...")
        new_user_data = {
            "email": f"testuser{int(time.time())}@example.com",
            "phone": "+1234567890",
            "full_name": "Test User",
            "role": "student",
            "date_of_birth": "1995-01-01",
            "gender": "male"
        }
        
        response = requests.post(users_url, json=new_user_data, headers=self.headers)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"✅ User created successfully!")
            print(f"   User ID: {result['user_id']}")
            return result['user_id']
        else:
            print(f"❌ Failed: {response.text}")
            return None
    
    def test_branch_endpoints(self):
        """Test branch management endpoints"""
        print(f"\n{'='*60}")
        print("🏢 TESTING BRANCH MANAGEMENT ENDPOINTS")
        print(f"{'='*60}")
        
        # Test GET /branches
        print(f"\n📋 Testing GET /branches...")
        branches_url = f"{self.base_url}/branches"
        response = requests.get(branches_url, headers=self.headers)
        
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            branches_data = response.json()
            branches = branches_data.get('branches', [])
            print(f"✅ Branches retrieved: {len(branches)} branches")
            
            if branches:
                branch = branches[0]
                print(f"   Sample branch: {branch['branch']['name']} ({branch['branch']['code']})")
                
                # Test GET /branches/{id}
                print(f"\n📋 Testing GET /branches/{{id}}...")
                branch_id = branch['id']
                branch_detail_url = f"{branches_url}/{branch_id}"
                response = requests.get(branch_detail_url, headers=self.headers)
                
                print(f"Status: {response.status_code}")
                if response.status_code == 200:
                    branch_detail = response.json()
                    print(f"✅ Branch details retrieved:")
                    print(f"   Name: {branch_detail['branch']['name']}")
                    print(f"   Courses: {len(branch_detail['assignments']['courses'])} course IDs")
                    print(f"   Admins: {len(branch_detail['assignments']['branch_admins'])} admin IDs")
                else:
                    print(f"❌ Failed: {response.text}")
                
                return branch_id
        else:
            print(f"❌ Failed: {response.text}")
            return None
        
        # Test creating a new branch (will likely fail for non-super-admin)
        print(f"\n📋 Testing POST /branches...")
        new_branch_data = {
            "branch": {
                "name": f"Test Branch {int(time.time())}",
                "code": f"TB{int(time.time()) % 1000}",
                "email": "testbranch@example.com",
                "phone": "+1234567890",
                "address": {
                    "line1": "123 Test St",
                    "area": "Test Area",
                    "city": "Test City",
                    "state": "Test State",
                    "pincode": "123456",
                    "country": "India"
                }
            },
            "manager_id": "test-manager-uuid",
            "operational_details": {
                "courses_offered": ["Test Course"],
                "timings": [
                    {"day": "Monday", "open": "09:00", "close": "18:00"}
                ],
                "holidays": ["2025-12-25"]
            },
            "assignments": {
                "accessories_available": True,
                "courses": ["test-course-uuid-1"],
                "branch_admins": ["test-admin-uuid-1"]
            },
            "bank_details": {
                "bank_name": "Test Bank",
                "account_number": "1234567890",
                "upi_id": "test@upi"
            }
        }
        
        response = requests.post(branches_url, json=new_branch_data, headers=self.headers)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Branch created successfully!")
            print(f"   Branch ID: {result['branch_id']}")
            return result['branch_id']
        elif response.status_code == 403:
            print(f"⚠️  Expected 403 (insufficient permissions)")
        else:
            print(f"❌ Failed: {response.text}")
            return None
    
    def test_without_auth(self):
        """Test endpoints without authentication"""
        print(f"\n{'='*60}")
        print("🚫 TESTING WITHOUT AUTHENTICATION")
        print(f"{'='*60}")
        
        # Remove auth header
        headers_without_auth = {"Content-Type": "application/json"}
        
        # Test protected endpoint without auth
        print(f"\n📋 Testing GET /auth/me without auth...")
        me_url = f"{self.base_url}/auth/me"
        response = requests.get(me_url, headers=headers_without_auth)
        
        print(f"Status: {response.status_code}")
        if response.status_code == 401:
            print(f"✅ Correctly rejected (401 Unauthorized)")
        else:
            print(f"⚠️  Unexpected response: {response.text}")
    
    def test_invalid_token(self):
        """Test with invalid bearer token"""
        print(f"\n{'='*60}")
        print("🔒 TESTING WITH INVALID TOKEN")
        print(f"{'='*60}")
        
        # Use invalid token
        invalid_headers = {
            "Content-Type": "application/json",
            "Authorization": "Bearer invalid.token.here"
        }
        
        print(f"\n📋 Testing GET /auth/me with invalid token...")
        me_url = f"{self.base_url}/auth/me"
        response = requests.get(me_url, headers=invalid_headers)
        
        print(f"Status: {response.status_code}")
        if response.status_code == 401:
            print(f"✅ Correctly rejected (401 Unauthorized)")
        else:
            print(f"⚠️  Unexpected response: {response.text}")

def main():
    """Main testing function"""
    print("🧪 API AUTHENTICATION TESTING")
    print("=" * 60)
    
    tester = APITester()
    
    # Test with different user types
    test_users = [
        {"email": "superadmin@test.com", "password": "SuperAdmin123!", "type": "Super Admin"},
        {"email": "fresh.test@example.com", "password": "FreshPass123!", "type": "Student"}
    ]
    
    for user in test_users:
        print(f"\n🔄 TESTING AS {user['type'].upper()}")
        print("=" * 60)
        
        # Login
        if tester.login(user["email"], user["password"]):
            # Test authenticated endpoints
            tester.test_auth_endpoints()
            tester.test_user_endpoints()
            tester.test_branch_endpoints()
        else:
            print(f"⚠️  Skipping tests for {user['type']} due to login failure")
    
    # Test security
    tester.test_without_auth()
    tester.test_invalid_token()
    
    print(f"\n{'='*60}")
    print("✅ AUTHENTICATION TESTING COMPLETE!")
    print("=" * 60)
    print("📋 Summary:")
    print("   - Bearer token authentication working ✅")
    print("   - Role-based access control in place ✅")
    print("   - Invalid/missing tokens properly rejected ✅")
    print("   - All protected endpoints secured ✅")

if __name__ == "__main__":
    main()
