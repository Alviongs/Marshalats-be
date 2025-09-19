#!/usr/bin/env python3
"""
Test script for Branch Manager API endpoints
"""

import asyncio
import httpx
import json
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:8003"
SUPERADMIN_EMAIL = "pittisunilkumar3@gmail.com"
SUPERADMIN_PASSWORD = "StrongPassword@123"

class BranchManagerAPITester:
    def __init__(self):
        self.base_url = BASE_URL
        self.token = None
        self.created_manager_id = None

    async def get_superadmin_token(self):
        """Get superadmin authentication token"""
        print("🔐 Getting superadmin token...")
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/api/superadmin/login",
                json={
                    "email": SUPERADMIN_EMAIL,
                    "password": SUPERADMIN_PASSWORD
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                self.token = data.get("access_token")
                print(f"✅ Got superadmin token: {self.token[:20]}...")
                return True
            else:
                print(f"❌ Failed to get token: {response.status_code} - {response.text}")
                return False

    async def test_create_branch_manager(self):
        """Test creating a new branch manager"""
        print("\n📝 Testing branch manager creation...")
        
        # Get available branches first
        branches = await self.get_branches()
        branch_id = branches[0]["id"] if branches else None
        
        manager_data = {
            "personal_info": {
                "first_name": "John",
                "last_name": "Manager",
                "gender": "male",
                "date_of_birth": "1985-06-15"
            },
            "contact_info": {
                "email": f"test.manager.{datetime.now().strftime('%Y%m%d%H%M%S')}@example.com",
                "country_code": "+91",
                "phone": "9876543210",
                "password": "TestPassword@123"
            },
            "address_info": {
                "address": "123 Test Street",
                "area": "Test Area",
                "city": "Test City",
                "state": "Test State",
                "zip_code": "123456",
                "country": "India"
            },
            "professional_info": {
                "designation": "Branch Manager",
                "education_qualification": "MBA",
                "professional_experience": "5 years",
                "certifications": ["Management Certification", "Leadership Training"]
            },
            "branch_id": branch_id,
            "emergency_contact": {
                "name": "Jane Manager",
                "phone": "9876543211",
                "relationship": "spouse"
            },
            "notes": "Test branch manager created via API"
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/api/branch-managers",
                json=manager_data,
                headers={"Authorization": f"Bearer {self.token}"}
            )
            
            if response.status_code == 200:
                data = response.json()
                self.created_manager_id = data["branch_manager"]["id"]
                print(f"✅ Branch manager created successfully: {self.created_manager_id}")
                print(f"   Name: {data['branch_manager']['full_name']}")
                print(f"   Email: {data['branch_manager']['email']}")
                return True
            else:
                print(f"❌ Failed to create branch manager: {response.status_code} - {response.text}")
                return False

    async def test_get_branch_managers(self):
        """Test getting list of branch managers"""
        print("\n📋 Testing branch managers list...")
        
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/api/branch-managers",
                headers={"Authorization": f"Bearer {self.token}"}
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Retrieved {len(data['branch_managers'])} branch managers")
                print(f"   Total count: {data['total_count']}")
                return True
            else:
                print(f"❌ Failed to get branch managers: {response.status_code} - {response.text}")
                return False

    async def test_get_branch_manager_by_id(self):
        """Test getting specific branch manager by ID"""
        if not self.created_manager_id:
            print("⚠️  Skipping get by ID test - no manager created")
            return False
            
        print(f"\n👤 Testing get branch manager by ID: {self.created_manager_id}")
        
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/api/branch-managers/{self.created_manager_id}",
                headers={"Authorization": f"Bearer {self.token}"}
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Retrieved branch manager: {data['full_name']}")
                print(f"   Email: {data['email']}")
                print(f"   Active: {data['is_active']}")
                return True
            else:
                print(f"❌ Failed to get branch manager: {response.status_code} - {response.text}")
                return False

    async def test_update_branch_manager(self):
        """Test updating branch manager"""
        if not self.created_manager_id:
            print("⚠️  Skipping update test - no manager created")
            return False
            
        print(f"\n✏️  Testing branch manager update: {self.created_manager_id}")
        
        update_data = {
            "professional_info": {
                "designation": "Senior Branch Manager",
                "education_qualification": "MBA in Management",
                "professional_experience": "7 years",
                "certifications": ["Advanced Management", "Leadership Excellence"]
            },
            "notes": "Updated via API test"
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.put(
                f"{self.base_url}/api/branch-managers/{self.created_manager_id}",
                json=update_data,
                headers={"Authorization": f"Bearer {self.token}"}
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Branch manager updated successfully")
                print(f"   New designation: {data['branch_manager']['professional_info']['designation']}")
                return True
            else:
                print(f"❌ Failed to update branch manager: {response.status_code} - {response.text}")
                return False

    async def test_send_credentials(self):
        """Test sending credentials email"""
        if not self.created_manager_id:
            print("⚠️  Skipping send credentials test - no manager created")
            return False
            
        print(f"\n📧 Testing send credentials: {self.created_manager_id}")
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/api/branch-managers/{self.created_manager_id}/send-credentials",
                headers={"Authorization": f"Bearer {self.token}"}
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Credentials sent successfully")
                print(f"   Email: {data['email']}")
                return True
            else:
                print(f"❌ Failed to send credentials: {response.status_code} - {response.text}")
                return False

    async def test_delete_branch_manager(self):
        """Test deleting branch manager"""
        if not self.created_manager_id:
            print("⚠️  Skipping delete test - no manager created")
            return False
            
        print(f"\n🗑️  Testing branch manager deletion: {self.created_manager_id}")
        
        async with httpx.AsyncClient() as client:
            response = await client.delete(
                f"{self.base_url}/api/branch-managers/{self.created_manager_id}",
                headers={"Authorization": f"Bearer {self.token}"}
            )
            
            if response.status_code == 200:
                print(f"✅ Branch manager deleted successfully")
                return True
            else:
                print(f"❌ Failed to delete branch manager: {response.status_code} - {response.text}")
                return False

    async def get_branches(self):
        """Helper method to get available branches"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/api/branches",
                headers={"Authorization": f"Bearer {self.token}"}
            )
            
            if response.status_code == 200:
                data = response.json()
                return data.get("branches", [])
            else:
                print(f"⚠️  Could not fetch branches: {response.status_code}")
                return []

    async def run_all_tests(self):
        """Run all API tests"""
        print("🚀 Starting Branch Manager API Tests")
        print("=" * 50)
        
        # Get authentication token
        if not await self.get_superadmin_token():
            print("❌ Cannot proceed without authentication token")
            return
        
        # Run tests in sequence
        tests = [
            self.test_create_branch_manager,
            self.test_get_branch_managers,
            self.test_get_branch_manager_by_id,
            self.test_update_branch_manager,
            self.test_send_credentials,
            self.test_delete_branch_manager
        ]
        
        passed = 0
        total = len(tests)
        
        for test in tests:
            try:
                if await test():
                    passed += 1
            except Exception as e:
                print(f"❌ Test failed with exception: {str(e)}")
        
        print("\n" + "=" * 50)
        print(f"🏁 Test Results: {passed}/{total} tests passed")
        
        if passed == total:
            print("🎉 All tests passed!")
        else:
            print("⚠️  Some tests failed. Check the output above.")

async def main():
    tester = BranchManagerAPITester()
    await tester.run_all_tests()

if __name__ == "__main__":
    asyncio.run(main())
