#!/usr/bin/env python3
"""
Test script to verify SuperAdmin authentication and DELETE endpoint functionality
"""
import asyncio
import jwt
import os
import sys
from datetime import datetime, timedelta
from motor.motor_asyncio import AsyncIOMotorClient

from utils.database import init_db

# Configuration
SECRET_KEY = os.getenv('SECRET_KEY', 'student_management_secret_key_2025_secure')
ALGORITHM = 'HS256'
MONGO_URL = os.getenv('MONGO_URL', 'mongodb://localhost:27017')

print('🔍 Testing SuperAdmin Authentication & DELETE Endpoint')
print('=' * 60)

async def test_auth_and_delete():
    """Test the complete authentication and delete flow"""
    
    # 1. Connect to database
    client = AsyncIOMotorClient(MONGO_URL)
    db = client.get_database('student_management_db')
    init_db(db)
    
    # 2. Create test superadmin
    superadmin_id = 'test-superadmin-123'
    superadmin_data = {
        'id': superadmin_id,
        'email': 'test@superadmin.com',
        'full_name': 'Test SuperAdmin',
        'role': 'superadmin',
        'is_active': True,
        'created_at': datetime.utcnow()
    }
    
    await db.superadmins.delete_one({'id': superadmin_id})
    await db.superadmins.insert_one(superadmin_data)
    print(f'✅ Created test superadmin: {superadmin_id}')
    
    # 3. Create test student to delete
    student_id = 'test-student-456'
    student_data = {
        'id': student_id,
        'email': 'test@student.com',
        'full_name': 'Test Student',
        'role': 'student',
        'is_active': True,
        'created_at': datetime.utcnow()
    }
    
    await db.users.delete_one({'id': student_id})
    await db.users.insert_one(student_data)
    print(f'✅ Created test student: {student_id}')
    
    # 4. Create SuperAdmin JWT token
    payload = {
        'sub': superadmin_id,
        'role': 'superadmin',
        'exp': datetime.utcnow() + timedelta(hours=24)
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    print(f'✅ Created SuperAdmin token: {token[:30]}...')
    
    # 5. Test token validation
    try:
        decoded = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        print(f'✅ Token validation successful: {decoded}')
    except Exception as e:
        print(f'❌ Token validation failed: {e}')
        return False
    
    # 6. Test unified auth system
    from utils.unified_auth import get_current_user_or_superadmin
    from fastapi.security import HTTPAuthorizationCredentials
    
    class MockCredentials:
        def __init__(self, token):
            self.credentials = token
    
    try:
        mock_creds = MockCredentials(token)
        current_user = await get_current_user_or_superadmin(mock_creds)
        print(f'✅ Unified auth successful: {current_user}')
        print(f'   - User ID: {current_user["id"]}')
        print(f'   - Role: {current_user["role"]}')
        print(f'   - Active: {current_user.get("is_active", True)}')
    except Exception as e:
        print(f'❌ Unified auth failed: {e}')
        return False
    
    # 7. Test role checking
    from utils.unified_auth import require_role_unified
    from models.user_models import UserRole
    
    try:
        role_checker = require_role_unified([UserRole.SUPER_ADMIN, UserRole.COACH_ADMIN])
        validated_user = await role_checker(current_user)
        print(f'✅ Role validation successful: {validated_user["role"]}')
    except Exception as e:
        print(f'❌ Role validation failed: {e}')
        return False
    
    # 8. Test delete functionality
    from controllers.user_controller import UserController
    from fastapi import Request
    
    class MockRequest:
        def __init__(self):
            self.client = type('obj', (object,), {'host': 'localhost'})
            self.url = type('obj', (object,), {'path': '/test'})
    
    try:
        mock_request = MockRequest()
        result = await UserController.delete_user(student_id, mock_request, current_user)
        print(f'✅ Delete operation successful: {result}')
        
        # Verify student was deleted
        deleted_student = await db.users.find_one({'id': student_id})
        if deleted_student is None:
            print(f'✅ Student successfully deleted from database')
        else:
            print(f'❌ Student still exists in database')
            
    except Exception as e:
        print(f'❌ Delete operation failed: {e}')
        return False
    
    # Cleanup
    await db.superadmins.delete_one({'id': superadmin_id})
    await db.users.delete_one({'id': student_id})
    print(f'🧹 Cleanup completed')
    
    client.close()
    return True

# Run the test
if __name__ == "__main__":
    success = asyncio.run(test_auth_and_delete())
    if success:
        print("\n🎉 All tests passed! Backend authentication and delete functionality working correctly.")
    else:
        print("\n❌ Some tests failed. Check the output above for details.")
