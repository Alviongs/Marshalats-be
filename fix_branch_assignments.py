#!/usr/bin/env python3
"""
Fix branch assignments to use correct course IDs
"""

import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os

async def fix_branch_assignments():
    mongo_url = os.getenv('MONGO_URL', 'mongodb://localhost:27017')
    client = AsyncIOMotorClient(mongo_url)
    db = client.get_database('student_management_db')
    
    print("🔧 Fixing branch assignments...")
    
    # Get all courses
    courses = await db.courses.find({}).to_list(length=10)
    course_ids = [course["id"] for course in courses]
    
    print(f"Found {len(courses)} courses with IDs: {course_ids}")
    
    # Get all branches
    branches = await db.branches.find({}).to_list(length=10)
    
    for i, branch in enumerate(branches):
        branch_name = branch.get('branch', {}).get('name', 'Unknown')
        print(f"Updating branch: {branch_name}")
        
        # Assign courses to branches in a round-robin fashion
        if i == 0:
            # First branch gets first 2 courses
            assigned_courses = course_ids[:2] if len(course_ids) >= 2 else course_ids
        elif i == 1:
            # Second branch gets last 2 courses
            assigned_courses = course_ids[-2:] if len(course_ids) >= 2 else course_ids
        else:
            # Other branches get all courses
            assigned_courses = course_ids
        
        # Update the branch assignments
        await db.branches.update_one(
            {"id": branch["id"]},
            {
                "$set": {
                    "assignments.courses": assigned_courses,
                    "operational_details.courses_offered": [
                        next((c["title"] for c in courses if c["id"] == cid), "Unknown")
                        for cid in assigned_courses
                    ]
                }
            }
        )
        
        print(f"  Assigned {len(assigned_courses)} courses: {assigned_courses}")
    
    print("✅ Branch assignments updated!")
    client.close()

if __name__ == "__main__":
    asyncio.run(fix_branch_assignments())
