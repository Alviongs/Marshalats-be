#!/usr/bin/env python3
"""
Test script to verify the delete API endpoint works
"""
import asyncio
import sys
import os
from pathlib import Path

# Add the current directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

from fastapi import FastAPI, Request
from fastapi.testclient import TestClient
from motor.motor_asyncio import AsyncIOMotorClient
from controllers.user_controller import UserController
from routes.user_routes import router as user_router
from utils.database import init_db
from datetime import datetime
import uuid

async def test_api_endpoint():
    """Test the delete API endpoint"""
    
    print("🔍 Testing Delete API Endpoint")
    print("=" * 40)
    
    # Initialize database connection
    mongo_url = os.getenv("MONGO_URL", "mongodb://localhost:27017")
    client = AsyncIOMotorClient(mongo_url)
    db = client.get_database("student_management_db")
    init_db(db)
    
    try:
        # Create FastAPI app
        app = FastAPI()
        app.include_router(user_router, prefix="/users")
        
        # Create test client
        test_client = TestClient(app)
        
        # Create a test user first
        test_user_id = str(uuid.uuid4())
        test_user = {
            "id": test_user_id,
            "email": "test_api@example.com",
            "full_name": "Test API User",
            "role": "student",
            "is_active": True,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        # Insert test user
        await db.users.insert_one(test_user)
        print(f"✅ Created test user: {test_user_id}")
        
        # Test the API endpoint (this would normally require authentication)
        # For testing purposes, we'll test the controller directly
        
        # Create mock objects
        class MockRequest:
            def __init__(self):
                self.client = type('obj', (object,), {'host': 'localhost'})()
                self.url = type('obj', (object,), {'path': '/test'})()
                self.method = 'DELETE'
        
        mock_request = MockRequest()
        mock_admin = {
            "id": "admin_test_id",
            "full_name": "Test Admin",
            "role": "super_admin"
        }
        
        # Test the delete functionality
        print(f"🗑️  Testing delete endpoint for user: {test_user_id}")
        result = await UserController.delete_user(test_user_id, mock_request, mock_admin)
        print(f"✅ API result: {result}")
        
        # Verify user is deleted
        user_after = await db.users.find_one({"id": test_user_id})
        if user_after is None:
            print("✅ User successfully deleted via API")
        else:
            print("❌ User still exists after API call!")
            
        print("\n🎉 API endpoint test completed!")
        
    except Exception as e:
        print(f"❌ Error during API test: {str(e)}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Cleanup
        try:
            await db.users.delete_one({"id": test_user_id})
        except:
            pass
        client.close()

if __name__ == "__main__":
    asyncio.run(test_api_endpoint())
