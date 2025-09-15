#!/usr/bin/env python3
"""
Test script to verify the student delete functionality
"""
import asyncio
import sys
import os
from pathlib import Path

# Add the current directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

from motor.motor_asyncio import AsyncIOMotorClient
from controllers.user_controller import UserController
from utils.database import init_db
from datetime import datetime
import uuid

async def test_delete_functionality():
    """Test the delete functionality"""
    
    # Initialize database connection
    mongo_url = os.getenv("MONGO_URL", "mongodb://localhost:27017")
    client = AsyncIOMotorClient(mongo_url)
    db = client.get_database("student_management_db")
    init_db(db)
    
    print("🔍 Testing Student Delete Functionality")
    print("=" * 50)
    
    try:
        # Create a test user first
        test_user_id = str(uuid.uuid4())
        test_user = {
            "id": test_user_id,
            "email": "test_delete@example.com",
            "full_name": "Test Delete User",
            "role": "student",
            "is_active": True,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        # Insert test user
        await db.users.insert_one(test_user)
        print(f"✅ Created test user: {test_user_id}")
        
        # Verify user exists
        user_before = await db.users.find_one({"id": test_user_id})
        if user_before:
            print(f"✅ User exists before deletion: {user_before['email']}")
        else:
            print("❌ Test user not found!")
            return
        
        # Create a mock current_user (admin)
        mock_admin = {
            "id": "admin_test_id",
            "full_name": "Test Admin",
            "role": "super_admin"
        }
        
        # Create a mock request object
        class MockRequest:
            def __init__(self):
                self.client = type('obj', (object,), {'host': 'localhost'})()
                self.url = type('obj', (object,), {'path': '/test'})()
                self.method = 'DELETE'
        
        mock_request = MockRequest()
        
        # Test the delete functionality
        print(f"🗑️  Attempting to delete user: {test_user_id}")
        result = await UserController.delete_user(test_user_id, mock_request, mock_admin)
        print(f"✅ Delete result: {result}")
        
        # Verify user is deleted
        user_after = await db.users.find_one({"id": test_user_id})
        if user_after is None:
            print("✅ User successfully deleted from database")
        else:
            print("❌ User still exists in database!")
            
        print("\n🎉 Delete functionality test completed!")
        
    except Exception as e:
        print(f"❌ Error during test: {str(e)}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Cleanup - ensure test user is removed
        try:
            await db.users.delete_one({"id": test_user_id})
        except:
            pass
        client.close()

if __name__ == "__main__":
    asyncio.run(test_delete_functionality())
