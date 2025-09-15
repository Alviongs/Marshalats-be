#!/usr/bin/env python3
"""
Test script to investigate superadmin permissions issue
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
from utils.auth import require_role, get_current_user
from utils.unified_auth import require_role_unified, get_current_user_or_superadmin
from models.user_models import UserRole
from controllers.superadmin_controller import SuperAdminController
import uuid

async def test_superadmin_permissions():
    """Test superadmin permissions with both auth systems"""
    
    print("🔍 Testing SuperAdmin Permissions Issue")
    print("=" * 50)
    
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
        
        # 2. Create superadmin JWT token (as created by superadmin login)
        superadmin_token = SuperAdminController.create_access_token(
            data={"sub": superadmin_id, "email": "test_superadmin@example.com", "role": "superadmin"}
        )
        print(f"✅ Created superadmin token: {superadmin_token[:30]}...")
        
        # 3. Test token payload
        from utils.auth import SECRET_KEY, ALGORITHM
        from controllers.superadmin_controller import SECRET_KEY as SUPERADMIN_SECRET_KEY

        print(f"Auth SECRET_KEY: {SECRET_KEY[:20]}...")
        print(f"SuperAdmin SECRET_KEY: {SUPERADMIN_SECRET_KEY[:20]}...")

        try:
            payload = jwt.decode(superadmin_token, SUPERADMIN_SECRET_KEY, algorithms=[ALGORITHM])
            print(f"✅ Token payload: {payload}")
            print(f"   - Role in token: '{payload.get('role')}'")
            print(f"   - Expected by backend: '{UserRole.SUPER_ADMIN.value}'")
        except Exception as e:
            print(f"❌ Token decode failed: {e}")
            return
        
        # 4. Test with regular auth system (used by DELETE endpoint)
        print(f"\n🔐 Testing Regular Auth System (require_role):")
        print("=" * 50)
        
        class MockCredentials:
            def __init__(self, token):
                self.credentials = token
        
        mock_credentials = MockCredentials(superadmin_token)
        
        try:
            # This should fail because regular auth looks in users collection
            user = await get_current_user(mock_credentials)
            print(f"❌ Regular auth should have failed but got: {user}")
        except Exception as e:
            print(f"✅ Regular auth failed as expected: {e}")
        
        # 5. Test with unified auth system
        print(f"\n🔐 Testing Unified Auth System (require_role_unified):")
        print("=" * 55)
        
        try:
            # This should work because unified auth handles superadmins
            user = await get_current_user_or_superadmin(mock_credentials)
            print(f"✅ Unified auth successful: {user['email']} (role: {user['role']})")
        except Exception as e:
            print(f"❌ Unified auth failed: {e}")
        
        # 6. Test role checking
        print(f"\n👮 Testing Role Checking:")
        print("=" * 30)
        
        # Test unified auth role checking
        try:
            user = await get_current_user_or_superadmin(mock_credentials)
            allowed_roles = [UserRole.SUPER_ADMIN, UserRole.COACH_ADMIN]
            user_role = user["role"]
            
            print(f"User role from unified auth: '{user_role}'")
            print(f"Allowed roles: {[role.value for role in allowed_roles]}")
            
            if user_role in [role.value for role in allowed_roles]:
                print(f"✅ Role check PASSED: '{user_role}' is in allowed roles")
            else:
                print(f"❌ Role check FAILED: '{user_role}' is NOT in allowed roles")
                
        except Exception as e:
            print(f"❌ Role checking failed: {e}")
        
        # 7. Show the fix needed
        print(f"\n🛠️ Fix Required:")
        print("=" * 20)
        print("The DELETE /users/{user_id} endpoint uses:")
        print("  require_role([UserRole.SUPER_ADMIN, UserRole.COACH_ADMIN])")
        print("")
        print("But it should use:")
        print("  require_role_unified([UserRole.SUPER_ADMIN, UserRole.COACH_ADMIN])")
        print("")
        print("This is because:")
        print("- require_role only works with regular users (users collection)")
        print("- require_role_unified works with superadmins, coaches, and users")
        print("- Superadmins are stored in superadmins collection, not users collection")
        
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Cleanup
        try:
            await db.superadmins.delete_one({"id": superadmin_id})
            print(f"\n🧹 Cleanup completed")
        except:
            pass
        client.close()

if __name__ == "__main__":
    asyncio.run(test_superadmin_permissions())
