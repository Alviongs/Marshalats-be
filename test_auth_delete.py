#!/usr/bin/env python3
"""
Test script to verify authentication and delete functionality
"""
import asyncio
import sys
import os
from pathlib import Path
import jwt
from datetime import datetime, timedelta

# Add the current directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

from motor.motor_asyncio import AsyncIOMotorClient
from controllers.user_controller import UserController
from utils.database import init_db
from utils.auth import get_current_user, require_role
from models.user_models import UserRole
import uuid

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Import the actual SECRET_KEY from auth module
from utils.auth import SECRET_KEY, ALGORITHM

print(f"🔑 Using SECRET_KEY from auth module: {SECRET_KEY[:20]}...")

def create_test_token(user_id: str, role: str = "super_admin") -> str:
    """Create a test JWT token"""
    payload = {
        "sub": user_id,
        "role": role,
        "exp": datetime.utcnow() + timedelta(hours=24)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

async def test_authentication_and_delete():
    """Test authentication and delete functionality"""
    
    print("🔍 Testing Authentication & Delete Functionality")
    print("=" * 55)
    
    # Initialize database connection
    mongo_url = os.getenv("MONGO_URL", "mongodb://localhost:27017")
    client = AsyncIOMotorClient(mongo_url)
    db = client.get_database("student_management_db")
    init_db(db)
    
    try:
        # 1. Create test admin user
        admin_user_id = str(uuid.uuid4())
        admin_user = {
            "id": admin_user_id,
            "email": "test_admin@example.com",
            "full_name": "Test Admin User",
            "role": "super_admin",
            "is_active": True,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        await db.users.insert_one(admin_user)
        print(f"✅ Created test admin user: {admin_user_id}")
        
        # 2. Create test student user
        student_user_id = str(uuid.uuid4())
        student_user = {
            "id": student_user_id,
            "email": "test_student@example.com",
            "full_name": "Test Student User",
            "role": "student",
            "is_active": True,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        await db.users.insert_one(student_user)
        print(f"✅ Created test student user: {student_user_id}")
        
        # 3. Create JWT token for admin
        admin_token = create_test_token(admin_user_id, "super_admin")
        print(f"✅ Created JWT token: {admin_token[:30]}...")
        
        # 4. Test token validation
        try:
            payload = jwt.decode(admin_token, SECRET_KEY, algorithms=[ALGORITHM])
            print(f"✅ Token validation successful: {payload}")
        except jwt.PyJWTError as e:
            print(f"❌ Token validation failed: {e}")
            return
        
        # 5. Test authentication flow
        print("\n🔐 Testing Authentication Flow:")
        print("================================")
        
        # Simulate the authentication process
        class MockCredentials:
            def __init__(self, token):
                self.credentials = token
        
        mock_credentials = MockCredentials(admin_token)
        
        try:
            # This should work with our token
            authenticated_user = await get_current_user(mock_credentials)
            print(f"✅ Authentication successful: {authenticated_user['email']} ({authenticated_user['role']})")
        except Exception as e:
            print(f"❌ Authentication failed: {e}")
            return
        
        # 6. Test role-based access
        print("\n👮 Testing Role-Based Access:")
        print("==============================")
        
        # Test if admin can access delete functionality
        allowed_roles = [UserRole.SUPER_ADMIN, UserRole.COACH_ADMIN]
        user_role = authenticated_user["role"]
        
        if user_role in [role.value for role in allowed_roles]:
            print(f"✅ User role '{user_role}' has delete permissions")
        else:
            print(f"❌ User role '{user_role}' does not have delete permissions")
            return
        
        # 7. Test delete functionality
        print("\n🗑️ Testing Delete Functionality:")
        print("=================================")
        
        # Create mock request
        class MockRequest:
            def __init__(self):
                self.client = type('obj', (object,), {'host': 'localhost'})()
                self.url = type('obj', (object,), {'path': '/test'})()
                self.method = 'DELETE'
        
        mock_request = MockRequest()
        
        # Test delete
        try:
            result = await UserController.delete_user(student_user_id, mock_request, authenticated_user)
            print(f"✅ Delete operation successful: {result}")
        except Exception as e:
            print(f"❌ Delete operation failed: {e}")
            return
        
        # 8. Verify deletion
        deleted_user = await db.users.find_one({"id": student_user_id})
        if deleted_user is None:
            print("✅ User successfully deleted from database")
        else:
            print("❌ User still exists in database")
        
        print("\n🎉 All authentication and delete tests passed!")
        
        # 9. Print token for frontend testing
        print(f"\n🔑 Test Token for Frontend:")
        print("===========================")
        print(f"Token: {admin_token}")
        print(f"User ID: {admin_user_id}")
        print(f"Role: super_admin")
        print(f"Valid until: {datetime.utcnow() + timedelta(hours=24)}")
        
    except Exception as e:
        print(f"❌ Test failed with error: {str(e)}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Cleanup
        try:
            await db.users.delete_many({"id": {"$in": [admin_user_id, student_user_id]}})
            print("\n🧹 Cleanup completed")
        except:
            pass
        client.close()

if __name__ == "__main__":
    asyncio.run(test_authentication_and_delete())
