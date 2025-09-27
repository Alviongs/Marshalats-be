#!/usr/bin/env python3
"""
Test script to verify coach authorization logic directly
"""
import asyncio
import os
import sys
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

# Add the current directory to Python path
sys.path.append('.')

# Load environment variables
load_dotenv()

# Import the controller
from controllers.coach_controller import CoachController
from utils.database import init_db

async def test_coach_authorization():
    """Test coach authorization logic directly"""
    
    # Database connection
    MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
    DB_NAME = os.environ.get('DB_NAME', 'marshalats')
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]
    
    # Initialize database connection
    init_db(db)

    print(f"🧪 Testing coach authorization logic directly")
    print("=" * 60)
    
    try:
        # 1. Get the branch manager data
        manager = await db.branch_managers.find_one({"email": "pittisunilkumar3@gmail.com"})
        if not manager:
            print("❌ Branch manager not found!")
            return
            
        # Add role to manager data (simulating what the auth middleware does)
        manager['role'] = 'branch_manager'
        
        print(f"✅ Found branch manager: {manager.get('full_name')}")
        print(f"   Manager ID: {manager.get('id')}")
        
        # 2. Test the coach authorization
        coach_id = "b6c5cc5f-be8d-47b2-aa95-3c1cdcb72a0d"
        print(f"\n🧪 Testing coach access for ID: {coach_id}")
        
        try:
            result = await CoachController.get_coach_by_id(coach_id, manager)
            print("✅ SUCCESS: Coach access allowed!")
            print(f"   Coach name: {result.get('full_name', 'No name')}")
            print(f"   Coach branch: {result.get('branch_id', 'No branch')}")
        except Exception as e:
            print(f"❌ FAILED: Coach access denied - {e}")
            print(f"   Error type: {type(e).__name__}")
            
        # 3. Test with a coach from a different branch
        other_coach_id = "187bed0c-54ce-4d53-a327-49da2950e3e1"
        print(f"\n🧪 Testing access to coach from different branch: {other_coach_id}")
        
        try:
            result = await CoachController.get_coach_by_id(other_coach_id, manager)
            print("❌ UNEXPECTED: Access allowed to coach from different branch!")
            print(f"   Coach name: {result.get('full_name', 'No name')}")
        except Exception as e:
            print(f"✅ EXPECTED: Access denied to coach from different branch - {e}")
            
    except Exception as e:
        print(f"❌ Error during test: {e}")
        import traceback
        traceback.print_exc()
    finally:
        client.close()

if __name__ == "__main__":
    asyncio.run(test_coach_authorization())
