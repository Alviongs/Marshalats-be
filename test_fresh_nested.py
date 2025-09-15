#!/usr/bin/env python3
"""
Clean up old user data and test with fresh registration
"""
import asyncio
import motor.motor_asyncio
import os
import requests
import json

async def cleanup_and_test():
    """Clean up old user and test with fresh data"""
    # Connect to MongoDB
    mongo_url = os.getenv("MONGO_URL", "mongodb://localhost:27017")
    client = motor.motor_asyncio.AsyncIOMotorClient(mongo_url)
    db = client.student_management_db
    
    # Delete the old test user
    result = await db.users.delete_many({"email": {"$in": ["pittisunilkumar3@gmail.com", "nested.test@example.com"]}})
    print(f"🗑️  Deleted {result.deleted_count} old user records")
    
    client.close()
    
    # Now register a fresh user
    url = "http://localhost:8003/api/auth/register"
    
    test_user = {
        "email": "fresh.test@example.com",
        "phone": "+1111111111",
        "first_name": "Fresh",
        "last_name": "Test",
        "role": "student",
        "password": "FreshPass123!",
        "date_of_birth": "1995-05-15",
        "gender": "male",
        "biometric_id": "fresh-bio-id",
        "course": {
            "category_id": "fresh-cat-123",
            "course_id": "fresh-course-456",
            "duration": "8-months"
        },
        "branch": {
            "location_id": "fresh-loc-789",
            "branch_id": "fresh-branch-101"
        }
    }
    
    print(f"\n📝 Registering fresh user: {test_user['email']}")
    
    try:
        response = requests.post(url, json=test_user, timeout=10)
        
        if response.status_code == 200:
            print("✅ Registration successful!")
            
            # Now check the stored data
            client = motor.motor_asyncio.AsyncIOMotorClient(mongo_url)
            db = client.student_management_db
            
            user = await db.users.find_one({"email": "fresh.test@example.com"})
            
            if user:
                print("\n📊 Fresh data stored in MongoDB:")
                print("=" * 50)
                
                # Remove password and internal fields for display
                display_user = {k: v for k, v in user.items() if k not in ['password', '_id', 'created_at', 'updated_at']}
                print(json.dumps(display_user, indent=2, default=str))
                
                print(f"\n📋 Structure Check:")
                has_nested_course = 'course' in user and isinstance(user['course'], dict)
                has_nested_branch = 'branch' in user and isinstance(user['branch'], dict)
                
                print(f"✅ Nested course object: {has_nested_course}")
                print(f"✅ Nested branch object: {has_nested_branch}")
                
                if has_nested_course and has_nested_branch:
                    print("🎉 SUCCESS: Data is stored with nested structure exactly as requested!")
                else:
                    print("⚠️  Data is still being stored in flattened structure")
                    
            client.close()
            
        else:
            print(f"❌ Registration failed: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(cleanup_and_test())
