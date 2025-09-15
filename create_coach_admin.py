#!/usr/bin/env python3
"""
Script to create a coach admin user for testing
"""
import asyncio
import os
from datetime import datetime
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables
ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

from utils.database import get_db, init_db
from utils.auth import hash_password, create_access_token
from motor.motor_asyncio import AsyncIOMotorClient

async def create_coach_admin():
    """Create a coach admin user in the database"""
    
    # Initialize database connection
    mongo_url = os.getenv("MONGO_URL", "mongodb://localhost:27017")
    client = AsyncIOMotorClient(mongo_url)
    db_name = os.getenv("DB_NAME", "student_management_db")
    database = client.get_database(db_name)
    
    # Initialize the database connection in utils
    init_db(database)
    db = get_db()
    
    try:
        # Check if coach admin already exists
        existing_admin = await db.users.find_one({"email": "test@gmail.com"})
        
        if existing_admin:
            print(f"✅ Coach Admin already exists with ID: {existing_admin['id']}")
            print(f"   Email: {existing_admin['email']}")
            print(f"   Full Name: {existing_admin['full_name']}")
            print(f"   Role: {existing_admin['role']}")
            return existing_admin['id']
        
        # Create new coach admin
        coach_admin_data = {
            "id": "coach-admin-001",
            "email": "test@gmail.com",
            "phone": "+1234567890",
            "first_name": "Test",
            "last_name": "Coach Admin",
            "full_name": "Test Coach Admin",
            "role": "coach_admin",
            "password": hash_password("12345678"),
            "biometric_id": None,
            "is_active": True,
            "date_of_birth": "1990-01-01",
            "gender": "other",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        # Insert into database
        result = await db.users.insert_one(coach_admin_data)
        print(f"✅ Created Coach Admin with ID: {coach_admin_data['id']}")
        print(f"   Email: {coach_admin_data['email']}")
        print(f"   Full Name: {coach_admin_data['full_name']}")
        print(f"   Role: {coach_admin_data['role']}")
        
        return coach_admin_data['id']
        
    except Exception as e:
        print(f"❌ Error creating coach admin: {e}")
        raise
    finally:
        client.close()

async def test_coach_admin_token():
    """Test creating a coach admin token"""
    
    # Create token
    token_data = {
        "sub": "coach-admin-001",
        "email": "test@gmail.com", 
        "role": "coach_admin"
    }
    
    token = create_access_token(token_data)
    print(f"✅ Created coach admin token: {token[:50]}...")
    
    return token

async def create_test_student():
    """Create a test student for deletion testing"""
    
    # Initialize database connection
    mongo_url = os.getenv("MONGO_URL", "mongodb://localhost:27017")
    client = AsyncIOMotorClient(mongo_url)
    db_name = os.getenv("DB_NAME", "student_management_db")
    database = client.get_database(db_name)
    
    # Initialize the database connection in utils
    init_db(database)
    db = get_db()
    
    try:
        # Create test student
        student_data = {
            "id": "test-student-for-deletion",
            "email": "deleteme@example.com",
            "phone": "+1234567999",
            "first_name": "Delete",
            "last_name": "Me",
            "full_name": "Delete Me",
            "role": "student",
            "password": hash_password("password123"),
            "biometric_id": None,
            "is_active": True,
            "date_of_birth": "2000-01-01",
            "gender": "other",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        # Insert into database
        result = await db.users.insert_one(student_data)
        print(f"✅ Created test student with ID: {student_data['id']}")
        print(f"   Email: {student_data['email']}")
        print(f"   Full Name: {student_data['full_name']}")
        
        return student_data['id']
        
    except Exception as e:
        print(f"❌ Error creating test student: {e}")
        raise
    finally:
        client.close()

async def main():
    """Main setup function"""
    print("🚀 Setting up Coach Admin and Test Data...")
    
    # Create coach admin
    coach_admin_id = await create_coach_admin()
    
    # Create test student
    student_id = await create_test_student()
    
    # Test token creation
    token = await test_coach_admin_token()
    
    print("\n🎉 Setup complete!")
    print(f"Coach Admin ID: {coach_admin_id}")
    print(f"Email: test@gmail.com")
    print(f"Password: 12345678")
    print(f"Test Student ID: {student_id}")
    print(f"Token: {token[:50]}...")

if __name__ == "__main__":
    asyncio.run(main())
