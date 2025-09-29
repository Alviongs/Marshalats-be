#!/usr/bin/env python3
"""
Comprehensive test script for the messaging system
Tests role-based access control, branch filtering, and message functionality
"""

import asyncio
import httpx
import json
from typing import Dict, List, Any
from datetime import datetime

# Test configuration
BASE_URL = "http://localhost:8003"
TEST_USERS = {
    "student": {
        "email": "test.student@example.com",
        "password": "testpass123",
        "role": "student"
    },
    "coach": {
        "email": "test.coach@example.com", 
        "password": "testpass123",
        "role": "coach"
    },
    "branch_manager": {
        "email": "test.manager@example.com",
        "password": "testpass123", 
        "role": "branch_manager"
    },
    "superadmin": {
        "email": "admin@marshalarts.com",
        "password": "admin123",
        "role": "superadmin"
    }
}

class MessagingSystemTester:
    def __init__(self):
        self.client = httpx.AsyncClient(timeout=30.0)
        self.tokens = {}
        self.test_results = []
        
    async def __aenter__(self):
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.aclose()

    def log_test(self, test_name: str, success: bool, message: str = ""):
        """Log test result"""
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status}: {test_name}")
        if message:
            print(f"   {message}")
        
        self.test_results.append({
            "test": test_name,
            "success": success,
            "message": message,
            "timestamp": datetime.now().isoformat()
        })

    async def authenticate_user(self, user_type: str) -> bool:
        """Authenticate a test user and store token"""
        try:
            user_data = TEST_USERS[user_type]
            
            # Try to login
            response = await self.client.post(
                f"{BASE_URL}/api/auth/login",
                json={
                    "email": user_data["email"],
                    "password": user_data["password"]
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                self.tokens[user_type] = data.get("access_token")
                self.log_test(f"Authentication - {user_type}", True, f"Token obtained")
                return True
            else:
                self.log_test(f"Authentication - {user_type}", False, f"Status: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test(f"Authentication - {user_type}", False, f"Error: {str(e)}")
            return False

    def get_auth_headers(self, user_type: str) -> Dict[str, str]:
        """Get authentication headers for user type"""
        token = self.tokens.get(user_type)
        if not token:
            return {}
        return {"Authorization": f"Bearer {token}"}

    async def test_get_recipients(self, user_type: str) -> bool:
        """Test getting available recipients for a user type"""
        try:
            headers = self.get_auth_headers(user_type)
            response = await self.client.get(
                f"{BASE_URL}/api/messages/recipients",
                headers=headers
            )
            
            if response.status_code == 200:
                data = response.json()
                recipients = data.get("recipients", [])
                self.log_test(
                    f"Get Recipients - {user_type}", 
                    True, 
                    f"Found {len(recipients)} recipients"
                )
                return True
            else:
                self.log_test(
                    f"Get Recipients - {user_type}", 
                    False, 
                    f"Status: {response.status_code}"
                )
                return False
                
        except Exception as e:
            self.log_test(f"Get Recipients - {user_type}", False, f"Error: {str(e)}")
            return False

    async def test_send_message(self, sender_type: str, recipient_type: str) -> bool:
        """Test sending a message between user types"""
        try:
            # First get recipients to find a valid recipient
            headers = self.get_auth_headers(sender_type)
            recipients_response = await self.client.get(
                f"{BASE_URL}/api/messages/recipients",
                headers=headers
            )
            
            if recipients_response.status_code != 200:
                self.log_test(
                    f"Send Message {sender_type} -> {recipient_type}", 
                    False, 
                    "Could not get recipients"
                )
                return False
            
            recipients_data = recipients_response.json()
            recipients = recipients_data.get("recipients", [])
            
            # Find a recipient of the target type
            target_recipient = None
            for recipient in recipients:
                if recipient["type"] == recipient_type:
                    target_recipient = recipient
                    break
            
            if not target_recipient:
                self.log_test(
                    f"Send Message {sender_type} -> {recipient_type}", 
                    False, 
                    f"No {recipient_type} recipients found"
                )
                return False
            
            # Send message
            message_data = {
                "recipient_id": target_recipient["id"],
                "recipient_type": recipient_type,
                "subject": f"Test message from {sender_type}",
                "content": f"This is a test message sent from {sender_type} to {recipient_type} at {datetime.now()}",
                "priority": "normal"
            }
            
            response = await self.client.post(
                f"{BASE_URL}/api/messages/send",
                json=message_data,
                headers=headers
            )
            
            if response.status_code == 200:
                data = response.json()
                self.log_test(
                    f"Send Message {sender_type} -> {recipient_type}", 
                    True, 
                    f"Message ID: {data.get('message_id')}"
                )
                return True
            else:
                self.log_test(
                    f"Send Message {sender_type} -> {recipient_type}", 
                    False, 
                    f"Status: {response.status_code}, Response: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_test(
                f"Send Message {sender_type} -> {recipient_type}", 
                False, 
                f"Error: {str(e)}"
            )
            return False

    async def test_get_conversations(self, user_type: str) -> bool:
        """Test getting conversations for a user"""
        try:
            headers = self.get_auth_headers(user_type)
            response = await self.client.get(
                f"{BASE_URL}/api/messages/conversations",
                headers=headers
            )
            
            if response.status_code == 200:
                data = response.json()
                conversations = data.get("conversations", [])
                self.log_test(
                    f"Get Conversations - {user_type}", 
                    True, 
                    f"Found {len(conversations)} conversations"
                )
                return True
            else:
                self.log_test(
                    f"Get Conversations - {user_type}", 
                    False, 
                    f"Status: {response.status_code}"
                )
                return False
                
        except Exception as e:
            self.log_test(f"Get Conversations - {user_type}", False, f"Error: {str(e)}")
            return False

    async def test_message_stats(self, user_type: str) -> bool:
        """Test getting message statistics for a user"""
        try:
            headers = self.get_auth_headers(user_type)
            response = await self.client.get(
                f"{BASE_URL}/api/messages/stats",
                headers=headers
            )
            
            if response.status_code == 200:
                data = response.json()
                stats = data.get("stats", {})
                self.log_test(
                    f"Message Stats - {user_type}", 
                    True, 
                    f"Total: {stats.get('total_messages', 0)}, Unread: {stats.get('unread_messages', 0)}"
                )
                return True
            else:
                self.log_test(
                    f"Message Stats - {user_type}", 
                    False, 
                    f"Status: {response.status_code}"
                )
                return False
                
        except Exception as e:
            self.log_test(f"Message Stats - {user_type}", False, f"Error: {str(e)}")
            return False

    async def test_message_notifications(self, user_type: str) -> bool:
        """Test getting message notifications for a user"""
        try:
            headers = self.get_auth_headers(user_type)
            response = await self.client.get(
                f"{BASE_URL}/api/messages/notifications",
                headers=headers
            )
            
            if response.status_code == 200:
                data = response.json()
                notifications = data.get("notifications", [])
                unread_count = data.get("unread_count", 0)
                self.log_test(
                    f"Message Notifications - {user_type}", 
                    True, 
                    f"Found {len(notifications)} notifications, {unread_count} unread"
                )
                return True
            else:
                self.log_test(
                    f"Message Notifications - {user_type}", 
                    False, 
                    f"Status: {response.status_code}"
                )
                return False
                
        except Exception as e:
            self.log_test(f"Message Notifications - {user_type}", False, f"Error: {str(e)}")
            return False

    async def run_comprehensive_tests(self):
        """Run all messaging system tests"""
        print("🚀 Starting Comprehensive Messaging System Tests")
        print("=" * 60)
        
        # Test 1: Authentication for all user types
        print("\n📋 Phase 1: Authentication Tests")
        auth_success = True
        for user_type in TEST_USERS.keys():
            success = await self.authenticate_user(user_type)
            auth_success = auth_success and success
        
        if not auth_success:
            print("\n❌ Authentication failed for some users. Stopping tests.")
            return
        
        # Test 2: Get recipients for each user type
        print("\n📋 Phase 2: Recipient Access Tests")
        for user_type in TEST_USERS.keys():
            await self.test_get_recipients(user_type)
        
        # Test 3: Send messages between different user types
        print("\n📋 Phase 3: Message Sending Tests")
        message_tests = [
            ("student", "coach"),
            ("student", "branch_manager"), 
            ("student", "superadmin"),
            ("coach", "student"),
            ("coach", "branch_manager"),
            ("coach", "superadmin"),
            ("branch_manager", "student"),
            ("branch_manager", "coach"),
            ("branch_manager", "superadmin"),
            ("superadmin", "student"),
            ("superadmin", "coach"),
            ("superadmin", "branch_manager")
        ]
        
        for sender, recipient in message_tests:
            await self.test_send_message(sender, recipient)
        
        # Test 4: Get conversations for each user type
        print("\n📋 Phase 4: Conversation Retrieval Tests")
        for user_type in TEST_USERS.keys():
            await self.test_get_conversations(user_type)
        
        # Test 5: Get message stats for each user type
        print("\n📋 Phase 5: Message Statistics Tests")
        for user_type in TEST_USERS.keys():
            await self.test_message_stats(user_type)
        
        # Test 6: Get message notifications for each user type
        print("\n📋 Phase 6: Message Notification Tests")
        for user_type in TEST_USERS.keys():
            await self.test_message_notifications(user_type)
        
        # Print summary
        self.print_test_summary()

    def print_test_summary(self):
        """Print test results summary"""
        print("\n" + "=" * 60)
        print("📊 TEST RESULTS SUMMARY")
        print("=" * 60)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["success"])
        failed_tests = total_tests - passed_tests
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests} ✅")
        print(f"Failed: {failed_tests} ❌")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        if failed_tests > 0:
            print("\n❌ Failed Tests:")
            for result in self.test_results:
                if not result["success"]:
                    print(f"  - {result['test']}: {result['message']}")
        
        print("\n" + "=" * 60)

async def main():
    """Main test runner"""
    async with MessagingSystemTester() as tester:
        await tester.run_comprehensive_tests()

if __name__ == "__main__":
    asyncio.run(main())
