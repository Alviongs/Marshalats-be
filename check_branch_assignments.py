#!/usr/bin/env python3
"""
Check branch assignments for courses
"""

import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os

async def check_branches():
    mongo_url = os.getenv('MONGO_URL', 'mongodb://localhost:27017')
    client = AsyncIOMotorClient(mongo_url)
    db = client.get_database('student_management_db')
    
    branches = await db.branches.find({}).to_list(length=10)
    courses = await db.courses.find({}).to_list(length=5)
    
    print(f'Found {len(branches)} branches and {len(courses)} courses')
    
    for branch in branches:
        branch_name = branch.get('branch', {}).get('name', 'Unknown')
        print(f'Branch: {branch_name}')
        assigned_courses = branch.get('assignments', {}).get('courses', [])
        print(f'  Assigned courses: {assigned_courses}')
    
    print('\nCourse IDs:')
    for course in courses:
        title = course.get('title', 'Unknown')
        course_id = course.get('id')
        print(f'  {title}: {course_id}')
    
    client.close()

if __name__ == "__main__":
    asyncio.run(check_branches())
