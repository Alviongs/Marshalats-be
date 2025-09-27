#!/usr/bin/env python3
"""
Database migration to add unique index for attendance records
This prevents duplicate attendance records for the same student, course, branch, and date
"""

import asyncio
import sys
import os
from datetime import datetime

# Add the parent directory to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.database import get_db

async def create_attendance_unique_index():
    """Create unique compound index for attendance records"""
    try:
        db = get_db()
        if db is None:
            print("❌ Database connection not available")
            return False

        print("🔧 Creating unique index for attendance records...")
        
        # Create compound index on student_id, course_id, branch_id, and attendance_date (day only)
        # This ensures no duplicate attendance records for the same student on the same day
        index_result = await db.attendance.create_index([
            ("student_id", 1),
            ("course_id", 1), 
            ("branch_id", 1),
            ("attendance_date", 1)
        ], 
        unique=True,
        name="unique_student_course_branch_date",
        background=True,
        partialFilterExpression={
            "student_id": {"$exists": True},
            "course_id": {"$exists": True},
            "branch_id": {"$exists": True},
            "attendance_date": {"$exists": True}
        })
        
        print(f"✅ Successfully created unique index: {index_result}")
        
        # Also create a regular index for faster queries by date
        date_index_result = await db.attendance.create_index([
            ("attendance_date", -1)
        ], 
        name="attendance_date_desc",
        background=True)
        
        print(f"✅ Successfully created date index: {date_index_result}")
        
        # Create index for coach queries
        coach_index_result = await db.attendance.create_index([
            ("branch_id", 1),
            ("attendance_date", -1),
            ("student_id", 1)
        ], 
        name="coach_attendance_queries",
        background=True)
        
        print(f"✅ Successfully created coach query index: {coach_index_result}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error creating attendance indexes: {str(e)}")
        return False

async def check_existing_duplicates():
    """Check for existing duplicate attendance records"""
    try:
        db = get_db()
        if db is None:
            print("❌ Database connection not available")
            return
            
        print("🔍 Checking for existing duplicate attendance records...")
        
        # Aggregation pipeline to find duplicates
        pipeline = [
            {
                "$group": {
                    "_id": {
                        "student_id": "$student_id",
                        "course_id": "$course_id", 
                        "branch_id": "$branch_id",
                        "date": {
                            "$dateToString": {
                                "format": "%Y-%m-%d",
                                "date": "$attendance_date"
                            }
                        }
                    },
                    "count": {"$sum": 1},
                    "records": {"$push": "$$ROOT"}
                }
            },
            {
                "$match": {
                    "count": {"$gt": 1}
                }
            }
        ]
        
        duplicates = []
        async for doc in db.attendance.aggregate(pipeline):
            duplicates.append(doc)
            
        if duplicates:
            print(f"⚠️ Found {len(duplicates)} sets of duplicate attendance records:")
            for dup in duplicates:
                print(f"   - Student: {dup['_id']['student_id']}, Course: {dup['_id']['course_id']}, Date: {dup['_id']['date']}, Count: {dup['count']}")
        else:
            print("✅ No duplicate attendance records found")
            
        return duplicates
        
    except Exception as e:
        print(f"❌ Error checking for duplicates: {str(e)}")
        return []

async def main():
    """Main migration function"""
    print("🚀 ATTENDANCE UNIQUE INDEX MIGRATION")
    print("=" * 50)
    
    # Check for existing duplicates first
    duplicates = await check_existing_duplicates()
    
    if duplicates:
        print(f"\n⚠️ WARNING: Found {len(duplicates)} sets of duplicate records.")
        print("You may want to clean these up before creating the unique index.")
        print("The unique index creation may fail if duplicates exist.")
        
        response = input("\nDo you want to continue anyway? (y/N): ")
        if response.lower() != 'y':
            print("Migration cancelled.")
            return
    
    # Create the unique index
    success = await create_attendance_unique_index()
    
    if success:
        print("\n✅ Migration completed successfully!")
        print("Attendance records now have unique constraints to prevent duplicates.")
    else:
        print("\n❌ Migration failed!")
        print("Please check the error messages above and try again.")

if __name__ == "__main__":
    asyncio.run(main())
