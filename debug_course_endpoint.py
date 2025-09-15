#!/usr/bin/env python3

import asyncio
import os
from datetime import datetime
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables
ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

from utils.database import get_db, init_db
from motor.motor_asyncio import AsyncIOMotorClient

async def debug_course_endpoint():
    """Debug the course endpoint directly"""
    
    # Initialize database connection
    mongo_url = os.getenv("MONGO_URL", "mongodb://localhost:27017")
    client = AsyncIOMotorClient(mongo_url)
    db_name = os.getenv("DB_NAME", "student_management_db")
    database = client.get_database(db_name)
    
    # Initialize the database connection in utils
    init_db(database)
    db = get_db()
    
    branch_id = "98ba0e20-3cce-48fa-8897-f17a8a5213fc"
    
    try:
        print(f"🔍 Looking for branch: {branch_id}")
        
        # First, get the branch to find assigned courses
        branch = await db.branches.find_one({"id": branch_id})
        if not branch:
            print("❌ Branch not found in database")
            return
        
        print(f"✅ Branch found: {branch['branch']['name']}")
        
        # Get course IDs assigned to this branch
        course_ids = branch.get("assignments", {}).get("courses", [])
        print(f"📚 Course IDs assigned to branch: {course_ids}")
        
        if not course_ids:
            print("ℹ️ No courses assigned to this branch")
            return
        
        # Fetch course details for assigned course IDs
        print(f"🔍 Looking for courses with IDs: {course_ids}")
        courses = await db.courses.find({
            "id": {"$in": course_ids},
            "settings.active": True
        }).to_list(length=100)
        
        print(f"✅ Found {len(courses)} active courses")
        
        for course in courses:
            print(f"  - {course.get('name', course.get('title', 'Unknown'))} (ID: {course.get('id')})")
            print(f"    Active: {course.get('settings', {}).get('active', 'Unknown')}")
            print(f"    Full course structure: {course}")
        
        # Also check if there are any courses without the active filter
        all_courses = await db.courses.find({
            "id": {"$in": course_ids}
        }).to_list(length=100)
        
        print(f"\n📊 Total courses (including inactive): {len(all_courses)}")
        for course in all_courses:
            active_status = course.get('settings', {}).get('active', 'Unknown')
            print(f"  - {course.get('name', 'Unknown')} - Active: {active_status}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    asyncio.run(debug_course_endpoint())
