#!/usr/bin/env python3
"""
Test script to verify course counts are working correctly
"""

import asyncio
import os
import requests
from motor.motor_asyncio import AsyncIOMotorClient

async def check_database_data():
    """Check what data exists in the database"""
    mongo_url = os.getenv('MONGO_URL', 'mongodb://localhost:27017')
    client = AsyncIOMotorClient(mongo_url)
    db = client.get_database('student_management_db')
    
    print("🔍 Checking Database Data")
    print("=" * 40)
    
    # Check courses
    courses = await db.courses.find({"settings.active": True}).to_list(10)
    print(f"\n📚 Active Courses: {len(courses)}")
    for course in courses:
        print(f"   - {course.get('title', 'N/A')} (ID: {course.get('id', 'N/A')})")
    
    # Check coaches
    coaches = await db.coaches.find({"is_active": True}).to_list(10)
    print(f"\n👨‍🏫 Active Coaches: {len(coaches)}")
    for coach in coaches:
        assignment_details = coach.get('assignment_details', {})
        assigned_courses = assignment_details.get('courses', [])
        print(f"   - {coach.get('full_name', 'N/A')} (Assigned to {len(assigned_courses)} courses)")
        if assigned_courses:
            print(f"     Courses: {assigned_courses}")
    
    # Check enrollments
    enrollments = await db.enrollments.find({"is_active": True}).to_list(10)
    print(f"\n🎓 Active Enrollments: {len(enrollments)}")
    enrollment_by_course = {}
    for enrollment in enrollments:
        course_id = enrollment.get('course_id', 'Unknown')
        if course_id not in enrollment_by_course:
            enrollment_by_course[course_id] = 0
        enrollment_by_course[course_id] += 1
    
    for course_id, count in enrollment_by_course.items():
        print(f"   - Course {course_id}: {count} students")
    
    client.close()
    return courses

async def assign_coach_to_course():
    """Assign a coach to a course for testing"""
    mongo_url = os.getenv('MONGO_URL', 'mongodb://localhost:27017')
    client = AsyncIOMotorClient(mongo_url)
    db = client.get_database('student_management_db')
    
    # Get first course and first coach
    course = await db.courses.find_one({"settings.active": True})
    coach = await db.coaches.find_one({"is_active": True})
    
    if course and coach:
        course_id = course['id']
        coach_id = coach['id']
        
        print(f"\n🔗 Assigning coach {coach.get('full_name')} to course {course.get('title')}")
        
        # Update coach's assignment_details to include this course
        current_assignments = coach.get('assignment_details', {}).get('courses', [])
        if course_id not in current_assignments:
            current_assignments.append(course_id)
            
            await db.coaches.update_one(
                {"id": coach_id},
                {"$set": {"assignment_details.courses": current_assignments}}
            )
            print(f"✅ Coach assigned successfully!")
        else:
            print(f"ℹ️ Coach already assigned to this course")
    else:
        print("❌ No course or coach found for assignment")
    
    client.close()

def test_api_counts():
    """Test the API to see the updated counts"""
    print("\n🧪 Testing API Counts After Assignment")
    print("=" * 40)
    
    try:
        response = requests.get("http://localhost:8003/api/courses/public/all")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ API call successful!")
            print(f"   Found {len(data.get('courses', []))} courses")
            
            for i, course in enumerate(data.get('courses', []), 1):
                print(f"\n📋 Course {i}: {course.get('title', 'N/A')}")
                print(f"   Branches: {course.get('branches', 'N/A')}")
                print(f"   Masters/Coaches: {course.get('masters', 'N/A')}")
                print(f"   Students: {course.get('students', 'N/A')}")
                print(f"   Instructor assignments: {len(course.get('instructor_assignments', []))}")
                print(f"   Student enrollment count: {course.get('student_enrollment_count', 'N/A')}")
                
                # Show instructor details
                if course.get('instructor_assignments'):
                    print(f"   Assigned instructors:")
                    for instructor in course.get('instructor_assignments', []):
                        print(f"     - {instructor.get('instructor_name')} ({instructor.get('email')})")
        else:
            print(f"❌ API call failed: {response.status_code}")
            print(f"   Response: {response.text}")
    
    except Exception as e:
        print(f"❌ Error testing API: {e}")

async def main():
    """Main test function"""
    print("🚀 Course Counts Verification Test")
    print("=" * 50)
    
    # Check current database state
    courses = await check_database_data()
    
    if courses:
        # Test API before assignment
        test_api_counts()
        
        # Assign a coach to a course
        await assign_coach_to_course()
        
        # Test API after assignment
        test_api_counts()
    else:
        print("❌ No courses found in database")

if __name__ == "__main__":
    asyncio.run(main())
