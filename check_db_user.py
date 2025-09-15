#!/usr/bin/env python3
"""
Check MongoDB database to see if user fields are saved correctly
"""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv
import json

async def check_user_in_db():
    """Check if the user was saved with all fields"""
    # Load environment variables
    load_dotenv()
    
    mongo_url = os.getenv("MONGO_URL", "mongodb://localhost:27017")
    db_name = os.getenv("DB_NAME", "student_management_db")
    
    try:
        # Create MongoDB client
        client = AsyncIOMotorClient(mongo_url)
        db = client.get_database(db_name)
        
        # Find the test user we just created
        user = await db.users.find_one({"email": "testuser4@example.com"})
        
        if user:
            print("✅ User found in database!")
            print("\nUser document:")
            
            # Convert ObjectId to string for JSON serialization
            user_dict = {}
            for key, value in user.items():
                if key == "_id":
                    user_dict["_id"] = str(value)
                else:
                    user_dict[key] = value
            
            print(json.dumps(user_dict, indent=2, default=str))
            
            # Check specific fields
            print(f"\n📋 Field Check:")
            print(f"   date_of_birth: {user.get('date_of_birth')} (type: {type(user.get('date_of_birth'))})")
            print(f"   gender: {user.get('gender')} (type: {type(user.get('gender'))})")
            print(f"   biometric_id: {user.get('biometric_id')} (type: {type(user.get('biometric_id'))})")
            
        else:
            print("❌ User not found in database!")
        
        # Close connection
        client.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(check_user_in_db())
