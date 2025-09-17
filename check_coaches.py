#!/usr/bin/env python3
"""
Check available coaches in the database
"""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
DB_NAME = os.environ.get('DB_NAME', 'student_management_db')

async def check_coaches():
    """Check coaches in the database"""
    print("👥 Checking coaches in database...")
    
    try:
        # Connect to MongoDB
        client = AsyncIOMotorClient(MONGO_URL)
        db = client[DB_NAME]
        
        # Get coaches collection
        coaches = await db.coaches.find({}).to_list(length=10)
        
        if coaches:
            print(f"✅ Found {len(coaches)} coaches:")
            for i, coach in enumerate(coaches, 1):
                print(f"\n{i}. Coach ID: {coach.get('id', 'N/A')}")
                print(f"   Name: {coach.get('full_name', 'N/A')}")
                print(f"   Email: {coach.get('contact_info', {}).get('email', 'N/A')}")
                print(f"   Active: {coach.get('is_active', 'N/A')}")
                print(f"   Role: {coach.get('role', 'N/A')}")
        else:
            print("❌ No coaches found in database")
            print("You may need to create a test coach first")
            
        # Close connection
        client.close()
        
    except Exception as e:
        print(f"❌ Error checking coaches: {e}")

if __name__ == "__main__":
    asyncio.run(check_coaches())
