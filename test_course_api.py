#!/usr/bin/env python3
"""
Test script to create a valid JWT token and test the enhanced courses API
"""

import asyncio
import jwt
import os
import requests
from datetime import datetime, timedelta
from motor.motor_asyncio import AsyncIOMotorClient

# JWT settings (matching auth.py)
SECRET_KEY = os.environ.get('SECRET_KEY', 'student_management_secret_key_2025')
ALGORITHM = "HS256"

def create_test_token(user_id: str, role: str = "super_admin") -> str:
    """Create a test JWT token"""
    payload = {
        "sub": user_id,
        "role": role,
        "exp": datetime.utcnow() + timedelta(hours=24)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

async def get_existing_user():
    """Get an existing user from the database"""
    mongo_url = os.getenv('MONGO_URL', 'mongodb://localhost:27017')
    client = AsyncIOMotorClient(mongo_url)
    db = client.get_database('student_management_db')

    # Find a super_admin user
    user = await db.users.find_one({"role": "super_admin", "is_active": True})
    client.close()

    if user:
        print(f"Found user: {user.get('email')} (Active: {user.get('is_active')})")
        return user["id"], user["email"]
    return None, None

def test_courses_api():
    """Test the enhanced courses API"""
    print("🧪 Testing Enhanced Courses API")
    print("=" * 40)

    try:
        print("\n📡 Testing /api/courses/public/all endpoint...")
        response = requests.get("http://localhost:8003/api/courses/public/all")

        if response.status_code == 200:
            data = response.json()
            print(f"✅ API call successful!")
            print(f"   Found {len(data.get('courses', []))} courses")

            # Display first course details
            if data.get('courses'):
                course = data['courses'][0]
                print(f"\n📋 Sample course data:")
                print(f"   Title: {course.get('title', 'N/A')}")
                print(f"   Name: {course.get('name', 'N/A')}")
                print(f"   Branches: {course.get('branches', 'N/A')}")
                print(f"   Masters: {course.get('masters', 'N/A')}")
                print(f"   Students: {course.get('students', 'N/A')}")
                print(f"   Icon: {course.get('icon', 'N/A')}")
                print(f"   Enabled: {course.get('enabled', 'N/A')}")
                print(f"   Branch assignments: {len(course.get('branch_assignments', []))}")
                print(f"   Instructor assignments: {len(course.get('instructor_assignments', []))}")
                print(f"   Student enrollment count: {course.get('student_enrollment_count', 'N/A')}")

                # Show branch assignments if any
                if course.get('branch_assignments'):
                    print(f"   Branch details:")
                    for branch in course.get('branch_assignments', [])[:3]:  # Show first 3
                        print(f"     - {branch.get('branch_name')} ({branch.get('location')})")

                # Show instructor assignments if any
                if course.get('instructor_assignments'):
                    print(f"   Instructor details:")
                    for instructor in course.get('instructor_assignments', [])[:3]:  # Show first 3
                        print(f"     - {instructor.get('instructor_name')} ({instructor.get('email')})")
        else:
            print(f"❌ API call failed: {response.status_code}")
            print(f"   Response: {response.text}")

    except Exception as e:
        print(f"❌ Error testing API: {e}")

if __name__ == "__main__":
    test_courses_api()
