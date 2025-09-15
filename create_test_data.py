#!/usr/bin/env python3
"""
Create test data for course list functionality
"""

import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os
from datetime import datetime, timedelta
import uuid

async def create_test_data():
    """Create test branches and enrollments for courses"""
    mongo_url = os.getenv('MONGO_URL', 'mongodb://localhost:27017')
    client = AsyncIOMotorClient(mongo_url)
    db = client.get_database('student_management_db')
    
    print("🏗️ Creating test data for course list...")
    
    # Get existing courses
    courses = await db.courses.find({}).to_list(length=10)
    print(f"Found {len(courses)} courses")
    
    if not courses:
        print("❌ No courses found. Please create some courses first.")
        return
    
    # Create test branches if they don't exist
    existing_branches = await db.branches.count_documents({})
    if existing_branches == 0:
        print("📍 Creating test branches...")
        
        test_branches = [
            {
                "id": str(uuid.uuid4()),
                "branch": {
                    "name": "Downtown Branch",
                    "code": "DT001",
                    "email": "downtown@martialarts.com",
                    "phone": "+1234567890",
                    "address": {
                        "line1": "123 Main Street",
                        "area": "Downtown",
                        "city": "New York",
                        "state": "NY",
                        "pincode": "10001",
                        "country": "USA"
                    }
                },
                "manager_id": "manager-1",
                "operational_details": {
                    "courses_offered": [course["title"] for course in courses[:2]],
                    "timings": [
                        {"day": "Monday", "open": "09:00", "close": "21:00"},
                        {"day": "Tuesday", "open": "09:00", "close": "21:00"}
                    ],
                    "holidays": []
                },
                "assignments": {
                    "accessories_available": True,
                    "courses": [course["id"] for course in courses[:2]],  # Assign first 2 courses
                    "branch_admins": []
                },
                "bank_details": {
                    "bank_name": "Test Bank",
                    "account_number": "1234567890",
                    "upi_id": "test@upi"
                },
                "is_active": True,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            },
            {
                "id": str(uuid.uuid4()),
                "branch": {
                    "name": "Uptown Branch",
                    "code": "UT001",
                    "email": "uptown@martialarts.com",
                    "phone": "+1234567891",
                    "address": {
                        "line1": "456 Oak Avenue",
                        "area": "Uptown",
                        "city": "New York",
                        "state": "NY",
                        "pincode": "10002",
                        "country": "USA"
                    }
                },
                "manager_id": "manager-2",
                "operational_details": {
                    "courses_offered": [course["title"] for course in courses[1:]],
                    "timings": [
                        {"day": "Monday", "open": "08:00", "close": "20:00"},
                        {"day": "Wednesday", "open": "08:00", "close": "20:00"}
                    ],
                    "holidays": []
                },
                "assignments": {
                    "accessories_available": True,
                    "courses": [course["id"] for course in courses[1:]],  # Assign last 2 courses
                    "branch_admins": []
                },
                "bank_details": {
                    "bank_name": "Test Bank 2",
                    "account_number": "0987654321",
                    "upi_id": "test2@upi"
                },
                "is_active": True,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
        ]
        
        await db.branches.insert_many(test_branches)
        print(f"✅ Created {len(test_branches)} test branches")
    else:
        print(f"📍 Found {existing_branches} existing branches")
    
    # Create test student enrollments
    existing_enrollments = await db.enrollments.count_documents({})
    if existing_enrollments == 0:
        print("👥 Creating test student enrollments...")
        
        # Get existing students
        students = await db.users.find({"role": "student"}).to_list(length=10)
        branches = await db.branches.find({}).to_list(length=10)
        
        if students and branches:
            test_enrollments = []
            
            # Create enrollments for each course
            for i, course in enumerate(courses):
                # Create 2-5 enrollments per course
                num_enrollments = min(2 + i, len(students))
                
                for j in range(num_enrollments):
                    student = students[j % len(students)]
                    branch = branches[j % len(branches)]
                    
                    enrollment = {
                        "id": str(uuid.uuid4()),
                        "student_id": student["id"],
                        "course_id": course["id"],
                        "branch_id": branch["id"],
                        "enrollment_date": datetime.utcnow() - timedelta(days=30),
                        "start_date": datetime.utcnow() - timedelta(days=30),
                        "end_date": datetime.utcnow() + timedelta(days=335),  # ~11 months
                        "fee_amount": 5000.0,
                        "admission_fee": 500.0,
                        "payment_status": "paid",
                        "next_due_date": datetime.utcnow() + timedelta(days=30),
                        "is_active": True,
                        "created_at": datetime.utcnow()
                    }
                    test_enrollments.append(enrollment)
            
            if test_enrollments:
                await db.enrollments.insert_many(test_enrollments)
                print(f"✅ Created {len(test_enrollments)} test enrollments")
        else:
            print("⚠️ No students or branches found for creating enrollments")
    else:
        print(f"👥 Found {existing_enrollments} existing enrollments")
    
    print("✅ Test data creation completed!")
    client.close()

if __name__ == "__main__":
    asyncio.run(create_test_data())
