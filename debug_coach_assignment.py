#!/usr/bin/env python3
"""
Debug script to check coach assignment data structure
"""

import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient

async def debug_coach_assignment():
    """Debug coach assignment data structure"""
    mongo_url = os.getenv('MONGO_URL', 'mongodb://localhost:27017')
    client = AsyncIOMotorClient(mongo_url)
    db = client.get_database('student_management_db')
    
    print("🔍 Debugging Coach Assignment Data Structure")
    print("=" * 50)
    
    # Get the course
    course = await db.courses.find_one({"settings.active": True})
    if course:
        course_id = course['id']
        print(f"\n📚 Course: {course.get('title')} (ID: {course_id})")
        
        # Get coaches assigned to this course using our current query
        print(f"\n🔍 Query: coaches.find({{'assignment_details.courses': '{course_id}', 'is_active': True}})")
        coaches_query1 = await db.coaches.find({
            "assignment_details.courses": course_id,
            "is_active": True
        }).to_list(10)
        print(f"Result: {len(coaches_query1)} coaches found")
        
        # Try alternative query structure
        print(f"\n🔍 Alternative Query: coaches.find({{'assignment_details.courses': {{'$in': ['{course_id}']}}, 'is_active': True}})")
        coaches_query2 = await db.coaches.find({
            "assignment_details.courses": {"$in": [course_id]},
            "is_active": True
        }).to_list(10)
        print(f"Result: {len(coaches_query2)} coaches found")
        
        # Get all coaches and examine their structure
        print(f"\n👨‍🏫 All Active Coaches:")
        all_coaches = await db.coaches.find({"is_active": True}).to_list(10)
        for coach in all_coaches:
            print(f"\n   Coach: {coach.get('full_name', 'N/A')}")
            print(f"   ID: {coach.get('id', 'N/A')}")
            print(f"   Assignment Details: {coach.get('assignment_details', {})}")
            
            assignment_details = coach.get('assignment_details', {})
            if assignment_details:
                courses = assignment_details.get('courses', [])
                print(f"   Assigned Courses: {courses}")
                print(f"   Course ID Match: {course_id in courses}")
                print(f"   Course ID Type: {type(course_id)}")
                if courses:
                    print(f"   First Course Type: {type(courses[0])}")
                    print(f"   Exact Match Check: {courses[0] == course_id}")
    
    client.close()

if __name__ == "__main__":
    asyncio.run(debug_coach_assignment())
