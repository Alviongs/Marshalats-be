#!/usr/bin/env python3
"""
Test script to debug the dashboard API for branch managers
"""
import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.database import get_db, init_db
from controllers.dashboard_controller import DashboardController
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

async def test_dashboard_api():
    """Test the dashboard API with a real branch manager"""
    
    # Load environment variables
    load_dotenv()
    
    # Connect to database
    mongo_url = os.getenv("MONGO_URL", "mongodb://localhost:27017")
    client = AsyncIOMotorClient(mongo_url)
    db_name = os.getenv("DB_NAME", "marshalats")
    database = client.get_database(db_name)
    
    # Initialize database connection
    init_db(database)
    db = get_db()
    
    print("🔍 Testing Dashboard API for Branch Manager")
    print("=" * 50)
    
    # Find a branch manager in the database
    branch_manager = await db.branch_managers.find_one({"is_active": True})
    if not branch_manager:
        print("❌ No active branch managers found in database")
        return
    
    print(f"📋 Found branch manager: {branch_manager.get('full_name', 'Unknown')}")
    print(f"📧 Email: {branch_manager.get('email', 'Unknown')}")
    print(f"🆔 ID: {branch_manager.get('id', 'Unknown')}")
    
    # Check branch assignment
    branch_assignment = branch_manager.get('branch_assignment', {})
    print(f"🏢 Branch assignment: {branch_assignment}")
    
    # Find branches managed by this branch manager
    managed_branches = await db.branches.find({"manager_id": branch_manager["id"], "is_active": True}).to_list(length=None)
    print(f"🏢 Managed branches: {len(managed_branches)}")
    for branch in managed_branches:
        print(f"   - {branch.get('id')}: {branch.get('branch', {}).get('name', 'Unknown')}")
    
    if not managed_branches:
        print("❌ No branches found for this branch manager")
        return
    
    # Create mock current_user object
    current_user = {
        "id": branch_manager["id"],
        "email": branch_manager["email"],
        "role": "branch_manager"
    }
    
    print("\n🔍 Testing Dashboard Controller...")
    try:
        result = await DashboardController.get_dashboard_stats(current_user)
        print("✅ Dashboard API call successful!")
        print(f"📊 Dashboard stats: {result}")
        
        stats = result.get("dashboard_stats", {})
        print("\n📈 Individual Stats:")
        print(f"   Active Students: {stats.get('active_students', 'N/A')}")
        print(f"   Total Users: {stats.get('total_users', 'N/A')}")
        print(f"   Active Courses: {stats.get('active_courses', 'N/A')}")
        print(f"   Total Courses: {stats.get('total_courses', 'N/A')}")
        print(f"   Active Coaches: {stats.get('active_coaches', 'N/A')}")
        print(f"   Total Coaches: {stats.get('total_coaches', 'N/A')}")
        print(f"   Active Enrollments: {stats.get('active_enrollments', 'N/A')}")
        print(f"   Total Revenue: {stats.get('total_revenue', 'N/A')}")
        print(f"   Monthly Revenue: {stats.get('monthly_revenue', 'N/A')}")
        
    except Exception as e:
        print(f"❌ Dashboard API call failed: {str(e)}")
        import traceback
        traceback.print_exc()
    
    # Let's also check the actual data in the database
    print("\n🔍 Checking Database Data...")
    managed_branch_ids = [branch["id"] for branch in managed_branches]
    
    # Check students
    student_count = await db.users.count_documents({
        "role": "student",
        "is_active": True,
        "branch_id": {"$in": managed_branch_ids}
    })
    print(f"👥 Students in managed branches: {student_count}")
    
    # Check coaches
    coach_count = await db.coaches.count_documents({
        "is_active": True,
        "branch_id": {"$in": managed_branch_ids}
    })
    print(f"👨‍🏫 Coaches in managed branches: {coach_count}")
    
    # Check courses (via branch assignments)
    course_ids_set = set()
    for branch in managed_branches:
        branch_course_ids = branch.get("assignments", {}).get("courses", [])
        course_ids_set.update(branch_course_ids)
    
    if course_ids_set:
        course_count = await db.courses.count_documents({
            "settings.active": True,
            "id": {"$in": list(course_ids_set)}
        })
        print(f"📚 Active courses in managed branches: {course_count}")
    else:
        print(f"📚 No courses assigned to managed branches")
    
    # Check enrollments
    enrollment_count = await db.enrollments.count_documents({
        "is_active": True,
        "branch_id": {"$in": managed_branch_ids}
    })
    print(f"📝 Active enrollments in managed branches: {enrollment_count}")
    
    # Close database connection
    client.close()

if __name__ == "__main__":
    asyncio.run(test_dashboard_api())
