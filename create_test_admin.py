#!/usr/bin/env python3
"""
Create a test admin user and generate a valid token for frontend testing
"""
import asyncio
import sys
import os
from pathlib import Path
import jwt
from datetime import datetime, timedelta
import bcrypt

# Add the current directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

from motor.motor_asyncio import AsyncIOMotorClient
from utils.database import init_db
from utils.auth import SECRET_KEY, ALGORITHM, hash_password
import uuid

async def create_test_admin():
    """Create a test admin user and generate token"""
    
    print("🔧 Creating Test Admin User for Frontend Testing")
    print("=" * 55)
    
    # Initialize database connection
    mongo_url = os.getenv("MONGO_URL", "mongodb://localhost:27017")
    client = AsyncIOMotorClient(mongo_url)
    db = client.get_database("student_management_db")
    init_db(db)
    
    try:
        # Admin user details
        admin_email = "admin@test.com"
        admin_password = "admin123"
        admin_user_id = str(uuid.uuid4())
        
        # Check if admin already exists
        existing_admin = await db.users.find_one({"email": admin_email})
        if existing_admin:
            print(f"✅ Admin user already exists: {admin_email}")
            admin_user_id = existing_admin["id"]
        else:
            # Create admin user
            hashed_password = hash_password(admin_password)
            admin_user = {
                "id": admin_user_id,
                "email": admin_email,
                "password": hashed_password,
                "full_name": "Test Admin",
                "role": "super_admin",
                "is_active": True,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
                "personal_info": {
                    "first_name": "Test",
                    "last_name": "Admin",
                    "phone": "+1234567890",
                    "date_of_birth": "1990-01-01",
                    "gender": "other"
                },
                "address": {
                    "street": "123 Test St",
                    "city": "Test City",
                    "state": "Test State",
                    "zip_code": "12345",
                    "country": "Test Country"
                }
            }
            
            await db.users.insert_one(admin_user)
            print(f"✅ Created admin user: {admin_email}")
        
        # Generate JWT token
        payload = {
            "sub": admin_user_id,
            "role": "super_admin",
            "exp": datetime.utcnow() + timedelta(hours=24)
        }
        token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
        
        print(f"\n🔑 Authentication Details:")
        print("=" * 30)
        print(f"Email: {admin_email}")
        print(f"Password: {admin_password}")
        print(f"User ID: {admin_user_id}")
        print(f"Role: super_admin")
        print(f"Token: {token}")
        print(f"Token expires: {datetime.utcnow() + timedelta(hours=24)}")
        
        print(f"\n📋 Frontend Setup Instructions:")
        print("=" * 35)
        print("1. Open browser console on the students dashboard page")
        print("2. Run the following commands:")
        print(f"   localStorage.setItem('access_token', '{token}')")
        print(f"   localStorage.setItem('token_type', 'bearer')")
        print(f"   localStorage.setItem('user', JSON.stringify({{")
        print(f"     id: '{admin_user_id}',")
        print(f"     email: '{admin_email}',")
        print(f"     full_name: 'Test Admin',")
        print(f"     role: 'super_admin'")
        print(f"   }}))")
        print("3. Refresh the page")
        print("4. Try deleting a student")
        
        print(f"\n🧪 Test the token with curl:")
        print("=" * 30)
        print(f"curl -X GET http://localhost:8003/users \\")
        print(f"  -H 'Authorization: Bearer {token}' \\")
        print(f"  -H 'Content-Type: application/json'")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
    
    finally:
        client.close()

if __name__ == "__main__":
    asyncio.run(create_test_admin())
