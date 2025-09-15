#!/usr/bin/env python3
"""
Setup script to create the superadmin user in the database
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
from controllers.superadmin_controller import SuperAdminController
from motor.motor_asyncio import AsyncIOMotorClient

async def setup_superadmin():
    """Create the superadmin user in the database"""
    
    # Initialize database connection
    mongo_url = os.getenv("MONGO_URL", "mongodb://localhost:27017")
    client = AsyncIOMotorClient(mongo_url)
    db_name = os.getenv("DB_NAME", "student_management_db")
    database = client.get_database(db_name)
    
    # Initialize the database connection in utils
    init_db(database)
    db = get_db()
    
    try:
        # Check if superadmin already exists
        existing_admin = await db.superadmins.find_one({"email": "pittisunilkumar3@gmail.com"})
        
        if existing_admin:
            print(f"✅ SuperAdmin already exists with ID: {existing_admin['id']}")
            print(f"   Email: {existing_admin['email']}")
            print(f"   Full Name: {existing_admin['full_name']}")
            return existing_admin['id']
        
        # Create new superadmin
        superadmin_data = {
            "id": "b3b7c914-4c5c-46f3-bf25-70591b2bb2b4",  # Use the ID from the token
            "full_name": "John Doe",
            "email": "pittisunilkumar3@gmail.com",
            "phone": "+919876543210",
            "password_hash": SuperAdminController.hash_password("StrongPassword@123"),
            "is_active": True,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        # Insert into database
        result = await db.superadmins.insert_one(superadmin_data)
        print(f"✅ Created SuperAdmin with ID: {superadmin_data['id']}")
        print(f"   Email: {superadmin_data['email']}")
        print(f"   Full Name: {superadmin_data['full_name']}")
        
        return superadmin_data['id']
        
    except Exception as e:
        print(f"❌ Error setting up superadmin: {e}")
        raise
    finally:
        client.close()

async def test_superadmin_token():
    """Test creating and validating a superadmin token"""
    
    # Create token
    token_data = {
        "sub": "b3b7c914-4c5c-46f3-bf25-70591b2bb2b4",
        "email": "pittisunilkumar3@gmail.com", 
        "role": "superadmin"
    }
    
    token = SuperAdminController.create_access_token(token_data)
    print(f"✅ Created token: {token[:50]}...")
    
    return token

async def main():
    """Main setup function"""
    print("🚀 Setting up SuperAdmin...")
    
    # Setup superadmin in database
    superadmin_id = await setup_superadmin()
    
    # Test token creation
    token = await test_superadmin_token()
    
    print("\n🎉 Setup complete!")
    print(f"SuperAdmin ID: {superadmin_id}")
    print(f"Email: pittisunilkumar3@gmail.com")
    print(f"Password: StrongPassword@123")
    print(f"Token: {token[:50]}...")

if __name__ == "__main__":
    asyncio.run(main())
