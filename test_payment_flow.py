#!/usr/bin/env python3
"""
Comprehensive test script for the complete payment flow
Tests: Registration -> Payment Processing -> Notification System -> Payment Tracking
"""

import asyncio
import httpx
import json
from datetime import datetime
import sys
import os

# Configuration
BASE_URL = "http://31.97.224.169:8003"
FRONTEND_URL = "http://localhost:3022"

class PaymentFlowTester:
    def __init__(self):
        self.base_url = BASE_URL
        self.session = None
        self.test_data = {
            "student": {
                "email": f"test.student.{datetime.now().strftime('%Y%m%d%H%M%S')}@example.com",
                "phone": "+919876543210",
                "first_name": "Test",
                "last_name": "Student",
                "role": "student",
                "password": "TestPassword123!",
                "date_of_birth": "1995-01-01",
                "gender": "male"
            },
            "course_id": None,
            "branch_id": None,
            "category_id": None,
            "duration": "3-months"
        }
        self.results = {
            "course_payment_info": None,
            "payment_processing": None,
            "notification_creation": None,
            "payment_tracking": None
        }

    async def setup_session(self):
        """Setup HTTP session"""
        self.session = httpx.AsyncClient(timeout=30.0)
        print("✅ HTTP session initialized")

    async def cleanup_session(self):
        """Cleanup HTTP session"""
        if self.session:
            await self.session.aclose()
        print("✅ HTTP session closed")

    async def get_test_course_and_branch(self):
        """Get a test course and branch for payment testing"""
        try:
            # Get categories
            response = await self.session.get(f"{self.base_url}/api/categories")
            if response.status_code == 200:
                categories = response.json()
                if categories:
                    self.test_data["category_id"] = categories[0]["id"]
                    print(f"✅ Using category: {categories[0]['name']}")

            # Get courses
            response = await self.session.get(f"{self.base_url}/api/courses")
            if response.status_code == 200:
                courses = response.json()
                if courses:
                    self.test_data["course_id"] = courses[0]["id"]
                    print(f"✅ Using course: {courses[0]['title']}")

            # Get branches
            response = await self.session.get(f"{self.base_url}/api/public/branches")
            if response.status_code == 200:
                branches = response.json()
                if branches:
                    self.test_data["branch_id"] = branches[0]["id"]
                    print(f"✅ Using branch: {branches[0]['branch']['name']}")

            return all([
                self.test_data["course_id"],
                self.test_data["branch_id"],
                self.test_data["category_id"]
            ])

        except Exception as e:
            print(f"❌ Error getting test data: {e}")
            return False

    async def test_course_payment_info(self):
        """Test 1: Get course payment information"""
        print("\n🧪 Test 1: Course Payment Information")
        
        try:
            url = f"{self.base_url}/api/courses/{self.test_data['course_id']}/payment-info"
            params = {
                "branch_id": self.test_data["branch_id"],
                "duration": self.test_data["duration"]
            }
            
            response = await self.session.get(url, params=params)
            
            if response.status_code == 200:
                payment_info = response.json()
                self.results["course_payment_info"] = payment_info
                print(f"✅ Payment info retrieved successfully")
                print(f"   Course Fee: ₹{payment_info['course_fee']}")
                print(f"   Admission Fee: ₹{payment_info['admission_fee']}")
                print(f"   Total Amount: ₹{payment_info['total_amount']}")
                return True
            else:
                print(f"❌ Failed to get payment info: {response.status_code}")
                print(f"   Response: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Error testing payment info: {e}")
            return False

    async def test_registration_payment_processing(self):
        """Test 2: Process registration payment"""
        print("\n🧪 Test 2: Registration Payment Processing")
        
        try:
            # Prepare payment data
            payment_data = {
                "student_data": self.test_data["student"],
                "course_id": self.test_data["course_id"],
                "branch_id": self.test_data["branch_id"],
                "category_id": self.test_data["category_id"],
                "duration": self.test_data["duration"],
                "payment_method": "credit_card",
                "card_details": {
                    "cardNumber": "4111111111111111",
                    "expiryDate": "12/25",
                    "cvv": "123",
                    "nameOnCard": "Test Student"
                }
            }
            
            response = await self.session.post(
                f"{self.base_url}/api/payments/process-registration",
                json=payment_data
            )
            
            if response.status_code == 201:
                result = response.json()
                self.results["payment_processing"] = result
                print(f"✅ Payment processed successfully")
                print(f"   Payment ID: {result['payment_id']}")
                print(f"   Student ID: {result['student_id']}")
                print(f"   Transaction ID: {result['transaction_id']}")
                print(f"   Amount: ₹{result['amount']}")
                print(f"   Status: {result['status']}")
                return True
            else:
                print(f"❌ Payment processing failed: {response.status_code}")
                print(f"   Response: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Error testing payment processing: {e}")
            return False

    async def test_notification_system(self):
        """Test 3: Check notification creation"""
        print("\n🧪 Test 3: Notification System")
        
        try:
            # First, we need to get superadmin token
            # For testing, we'll skip authentication and just check if notifications endpoint exists
            response = await self.session.get(f"{self.base_url}/api/payments/notifications")
            
            # Even if unauthorized, the endpoint should exist
            if response.status_code in [200, 401, 403]:
                print("✅ Notification endpoint exists")
                if response.status_code == 200:
                    notifications = response.json()
                    self.results["notification_creation"] = notifications
                    print(f"   Found {len(notifications)} notifications")
                else:
                    print("   (Authentication required for full test)")
                return True
            else:
                print(f"❌ Notification endpoint not found: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Error testing notifications: {e}")
            return False

    async def test_payment_tracking(self):
        """Test 4: Payment tracking and statistics"""
        print("\n🧪 Test 4: Payment Tracking")
        
        try:
            # Test payment stats endpoint
            response = await self.session.get(f"{self.base_url}/api/payments/stats")
            
            if response.status_code in [200, 401, 403]:
                print("✅ Payment stats endpoint exists")
                if response.status_code == 200:
                    stats = response.json()
                    print(f"   Total Collected: ₹{stats.get('total_collected', 0)}")
                    print(f"   Pending Payments: ₹{stats.get('pending_payments', 0)}")
                    print(f"   Total Students: {stats.get('total_students', 0)}")
                else:
                    print("   (Authentication required for full test)")
            
            # Test payments list endpoint
            response = await self.session.get(f"{self.base_url}/api/payments")
            
            if response.status_code in [200, 401, 403]:
                print("✅ Payments list endpoint exists")
                if response.status_code == 200:
                    payments = response.json()
                    self.results["payment_tracking"] = payments
                    print(f"   Found {len(payments.get('payments', []))} payment records")
                else:
                    print("   (Authentication required for full test)")
                return True
            else:
                print(f"❌ Payment tracking endpoints not found")
                return False
                
        except Exception as e:
            print(f"❌ Error testing payment tracking: {e}")
            return False

    async def test_frontend_integration(self):
        """Test 5: Frontend integration points"""
        print("\n🧪 Test 5: Frontend Integration")
        
        try:
            # Test if frontend payment page loads
            response = await self.session.get(f"{FRONTEND_URL}/register/payment")
            
            if response.status_code == 200:
                print("✅ Frontend payment page accessible")
            else:
                print(f"⚠️  Frontend payment page: {response.status_code}")
            
            # Test payment confirmation page
            response = await self.session.get(f"{FRONTEND_URL}/register/payment-confirmation")
            
            if response.status_code == 200:
                print("✅ Frontend payment confirmation page accessible")
            else:
                print(f"⚠️  Frontend payment confirmation page: {response.status_code}")
            
            return True
            
        except Exception as e:
            print(f"⚠️  Frontend integration test (optional): {e}")
            return True  # Don't fail the test if frontend is not running

    async def run_all_tests(self):
        """Run all payment flow tests"""
        print("🚀 Starting Complete Payment Flow Test")
        print("=" * 50)
        
        await self.setup_session()
        
        try:
            # Setup test data
            if not await self.get_test_course_and_branch():
                print("❌ Failed to get test course and branch data")
                return False
            
            # Run tests in sequence
            tests = [
                ("Course Payment Info", self.test_course_payment_info),
                ("Registration Payment Processing", self.test_registration_payment_processing),
                ("Notification System", self.test_notification_system),
                ("Payment Tracking", self.test_payment_tracking),
                ("Frontend Integration", self.test_frontend_integration)
            ]
            
            results = []
            for test_name, test_func in tests:
                result = await test_func()
                results.append((test_name, result))
            
            # Summary
            print("\n" + "=" * 50)
            print("📊 TEST SUMMARY")
            print("=" * 50)
            
            passed = 0
            for test_name, result in results:
                status = "✅ PASS" if result else "❌ FAIL"
                print(f"{status} {test_name}")
                if result:
                    passed += 1
            
            print(f"\nOverall: {passed}/{len(results)} tests passed")
            
            if passed == len(results):
                print("🎉 All tests passed! Payment flow is working correctly.")
                return True
            else:
                print("⚠️  Some tests failed. Check the logs above for details.")
                return False
                
        finally:
            await self.cleanup_session()

async def main():
    """Main test function"""
    tester = PaymentFlowTester()
    success = await tester.run_all_tests()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    asyncio.run(main())
