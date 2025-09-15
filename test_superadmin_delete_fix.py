#!/usr/bin/env python3
"""
Test script to verify the superadmin delete fix works
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
from utils.database import init_db
from utils.unified_auth import require_role_unified
from models.user_models import UserRole
from controllers.superadmin_controller import SuperAdminController
from controllers.user_controller import UserController
import uuid

async def test_superadmin_delete_fix():
    """Test that superadmin can now delete users"""
    
    print("🔍 Testing SuperAdmin Delete Fix")
    print("=" * 40)
    
    # Initialize database connection
    mongo_url = os.getenv("MONGO_URL", "mongodb://localhost:27017")
    client = AsyncIOMotorClient(mongo_url)
    db = client.get_database("student_management_db")
    init_db(db)
    
    try:
        # 1. Create a test superadmin
        superadmin_id = str(uuid.uuid4())
        superadmin_data = {
            "id": superadmin_id,
            "email": "test_superadmin@example.com",
            "full_name": "Test SuperAdmin",
            "phone": "+1234567890",
            "password_hash": SuperAdminController.hash_password("admin123"),
            "is_active": True,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        await db.superadmins.insert_one(superadmin_data)
        print(f"✅ Created test superadmin: {superadmin_id}")
        
        # 2. Create a test student to delete
        student_id = str(uuid.uuid4())
        student_data = {
            "id": student_id,
            "email": "test_student@example.com",
            "full_name": "Test Student",
            "role": "student",
            "is_active": True,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        await db.users.insert_one(student_data)
        print(f"✅ Created test student: {student_id}")
        
        # 3. Create superadmin JWT token
        superadmin_token = SuperAdminController.create_access_token(
            data={"sub": superadmin_id, "email": "test_superadmin@example.com", "role": "superadmin"}
        )
        print(f"✅ Created superadmin token")
        
        # 4. Test unified auth with superadmin token
        print(f"\n🔐 Testing Unified Auth with SuperAdmin Token:")
        print("=" * 50)
        
        class MockCredentials:
            def __init__(self, token):
                self.credentials = token
        
        mock_credentials = MockCredentials(superadmin_token)
        
        # Import the unified auth function
        from utils.unified_auth import get_current_user_or_superadmin
        
        try:
            authenticated_user = await get_current_user_or_superadmin(mock_credentials)
            print(f"✅ Unified auth successful:")
            print(f"   - Email: {authenticated_user['email']}")
            print(f"   - Role: {authenticated_user['role']}")
            print(f"   - ID: {authenticated_user['id']}")
        except Exception as e:
            print(f"❌ Unified auth failed: {e}")
            return
        
        # 5. Test role checking
        print(f"\n👮 Testing Role Authorization:")
        print("=" * 35)
        
        allowed_roles = [UserRole.SUPER_ADMIN, UserRole.COACH_ADMIN]
        user_role = authenticated_user["role"]
        
        print(f"User role: '{user_role}'")
        print(f"Allowed roles: {[role.value for role in allowed_roles]}")
        
        if user_role in [role.value for role in allowed_roles]:
            print(f"✅ Role authorization PASSED")
        else:
            print(f"❌ Role authorization FAILED")
            return
        
        # 6. Test the actual delete functionality
        print(f"\n🗑️ Testing Delete Functionality:")
        print("=" * 35)
        
        # Create mock request
        class MockRequest:
            def __init__(self):
                self.client = type('obj', (object,), {'host': 'localhost'})()
                self.url = type('obj', (object,), {'path': '/test'})()
                self.method = 'DELETE'
        
        mock_request = MockRequest()
        
        try:
            # Test the delete operation
            result = await UserController.delete_user(student_id, mock_request, authenticated_user)
            print(f"✅ Delete operation successful: {result}")
        except Exception as e:
            print(f"❌ Delete operation failed: {e}")
            return
        
        # 7. Verify student was deleted
        deleted_student = await db.users.find_one({"id": student_id})
        if deleted_student is None:
            print("✅ Student successfully deleted from database")
        else:
            print("❌ Student still exists in database")
            return
        
        print(f"\n🎉 SuperAdmin Delete Fix Test PASSED!")
        print("=" * 45)
        print("✅ SuperAdmin can now successfully delete users")
        print("✅ Unified authentication working correctly")
        print("✅ Role authorization working correctly")
        print("✅ Delete operation working correctly")
        
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Cleanup
        try:
            await db.superadmins.delete_one({"id": superadmin_id})
            await db.users.delete_one({"id": student_id})
            print(f"\n🧹 Cleanup completed")
        except:
            pass
        client.close()

if __name__ == "__main__":
    asyncio.run(test_superadmin_delete_fix())
