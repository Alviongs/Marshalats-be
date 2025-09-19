#!/usr/bin/env python3
"""
Test script to verify nested object storage in database
"""
import requests
import json
import asyncio
import motor.motor_asyncio
import os
from pymongo import MongoClient

async def check_database_storage():
    """Check how data is actually stored in MongoDB"""
    # Connect to MongoDB
    mongo_url = os.getenv("MONGO_URL", "mongodb://localhost:27017")
    client = motor.motor_asyncio.AsyncIOMotorClient(mongo_url)
    db = client.student_management_db
    
    # Find the most recent user
    user = await db.users.find_one(
        {"email": "pittisunilkumar3@gmail.com"}, 
        sort=[("created_at", -1)]
    )
    
    if user:
        print("📊 Data stored in MongoDB:")
        print("=" * 50)
        
        # Remove password and internal fields for display
        display_user = {k: v for k, v in user.items() if k not in ['password', '_id', 'created_at', 'updated_at']}
        print(json.dumps(display_user, indent=2, default=str))
        
        print("\n📋 Structure Check:")
        print(f"✅ Nested course object: {'course' in user and isinstance(user['course'], dict)}")
        print(f"✅ Nested branch object: {'branch' in user and isinstance(user['branch'], dict)}")
        
        if user.get('course'):
            course = user['course']
            print(f"   - Course category_id: {course.get('category_id')}")
            print(f"   - Course course_id: {course.get('course_id')}")
            print(f"   - Course duration: {course.get('duration')}")
            
        if user.get('branch'):
            branch = user['branch']
            print(f"   - Branch location_id: {branch.get('location_id')}")
            print(f"   - Branch branch_id: {branch.get('branch_id')}")
    else:
        print("❌ No user found in database")
    
    client.close()

def test_registration_and_check_storage():
    """Test registration and verify storage"""
    url = "http://localhost:8003/api/auth/register"
    
    # Create a new test user with unique email
    test_user = {
        "email": "nested.test@example.com",
        "phone": "+1234567890",
        "first_name": "Nested",
        "last_name": "User",
        "role": "student",
        "password": "TestPass123!",
        "date_of_birth": "2000-01-01",
        "gender": "female",
        "biometric_id": "test-bio-id",
        "course": {
            "category_id": "cat-12345",
            "course_id": "course-67890",
            "duration": "12-months"
        },
        "branch": {
            "location_id": "loc-abcde",
            "branch_id": "branch-fghij"
        }
    }
    
    try:
        print("🧪 Testing nested object storage...")
        print(f"Registering user: {test_user['email']}")
        
        response = requests.post(url, json=test_user, timeout=10)
        
        if response.status_code == 200:
            print("✅ Registration successful!")
            
            # Now check the database
            print("\n🔍 Checking database storage...")
            asyncio.run(check_database_storage())
            
        else:
            print(f"❌ Registration failed: {response.status_code}")
            print(f"Response: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to server. Make sure it's running on localhost:8001")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_registration_and_check_storage()
