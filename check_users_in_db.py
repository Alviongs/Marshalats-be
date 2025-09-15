#!/usr/bin/env python3
"""
Check what users exist in the database
"""

import asyncio
import os
from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient
import json

async def check_users():
    """Check what users exist in the database"""
    load_dotenv()
    
    mongo_url = os.getenv("MONGO_URL", "mongodb://localhost:27017")
    db_name = os.getenv("DB_NAME", "student_management_db")
    
    print('🔍 CHECKING USERS IN DATABASE')
    print('='*60)
    print(f'📊 MongoDB URL: {mongo_url}')
    print(f'📊 Database: {db_name}')
    
    try:
        # Connect to MongoDB
        client = AsyncIOMotorClient(mongo_url)
        db = client.get_database(db_name)
        
        # Count total users
        total_users = await db.users.count_documents({})
        print(f'\n👥 Total users in database: {total_users}')
        
        if total_users == 0:
            print('❌ No users found in database!')
            print('🔧 You need to register a user first before testing password reset')
            return
        
        # Get all users (limit to 10 for display)
        users = await db.users.find({}).limit(10).to_list(length=10)
        
        print(f'\n📋 Users in database:')
        print('-'*60)
        
        for i, user in enumerate(users, 1):
            print(f'{i}. Email: {user.get("email", "N/A")}')
            print(f'   Name: {user.get("full_name", "N/A")}')
            print(f'   Role: {user.get("role", "N/A")}')
            print(f'   Active: {user.get("is_active", "N/A")}')
            print(f'   ID: {user.get("id", "N/A")}')
            print()
        
        # Check specifically for our test email
        test_user = await db.users.find_one({"email": "pittisunilkumar3@gmail.com"})
        
        print('🔍 Checking for test email: pittisunilkumar3@gmail.com')
        if test_user:
            print('✅ Test user found!')
            print(f'   Name: {test_user.get("full_name", "N/A")}')
            print(f'   Role: {test_user.get("role", "N/A")}')
            print(f'   Active: {test_user.get("is_active", "N/A")}')
        else:
            print('❌ Test user NOT found!')
            print('🔧 This explains why password reset is not working')
            
            # Suggest using an existing user
            if users:
                print(f'\\n💡 Try using one of these existing emails instead:')
                for user in users[:3]:
                    print(f'   - {user.get("email", "N/A")}')
        
        client.close()
        
    except Exception as e:
        print(f'❌ Database error: {e}')

if __name__ == "__main__":
    asyncio.run(check_users())
