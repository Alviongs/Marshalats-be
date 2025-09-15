#!/usr/bin/env python3
"""
Data Migration Script: Move Course Data from User Documents to Enrollment Records

This script migrates course and branch information from user documents to proper
enrollment records in the enrollments collection, following proper database
normalization principles.

Usage:
    python migrate_course_data.py [--dry-run] [--verbose]

Options:
    --dry-run    Show what would be migrated without making changes
    --verbose    Show detailed output during migration
"""

import asyncio
import argparse
import sys
from datetime import datetime, timedelta
from typing import List, Dict, Any
import uuid

# Add the project root to the path so we can import our modules
sys.path.append('.')

from utils.database import get_db
from models.enrollment_models import Enrollment


class CourseDataMigrator:
    def __init__(self, dry_run: bool = False, verbose: bool = False):
        self.dry_run = dry_run
        self.verbose = verbose
        self.db = None
        self.stats = {
            'users_processed': 0,
            'users_with_course_data': 0,
            'enrollments_created': 0,
            'errors': 0,
            'skipped': 0
        }

    async def initialize(self):
        """Initialize database connection"""
        self.db = get_db()
        if self.verbose:
            print("✅ Database connection initialized")

    async def find_users_with_course_data(self) -> List[Dict[str, Any]]:
        """Find all users that have course data embedded in their documents"""
        query = {
            "role": "student",
            "$or": [
                {"course": {"$exists": True, "$ne": None}},
                {"branch": {"$exists": True, "$ne": None}}
            ]
        }
        
        users = await self.db.users.find(query).to_list(1000)
        
        if self.verbose:
            print(f"🔍 Found {len(users)} users with embedded course/branch data")
        
        return users

    async def check_existing_enrollment(self, student_id: str, course_id: str) -> bool:
        """Check if an enrollment already exists for this student and course"""
        existing = await self.db.enrollments.find_one({
            "student_id": student_id,
            "course_id": course_id,
            "is_active": True
        })
        return existing is not None

    async def create_enrollment_from_user_data(self, user: Dict[str, Any]) -> bool:
        """Create an enrollment record from user's embedded course data"""
        try:
            student_id = user["id"]
            course_data = user.get("course", {})
            branch_data = user.get("branch", {})
            
            if not course_data or not course_data.get("course_id"):
                if self.verbose:
                    print(f"⚠️  User {student_id} has no valid course data, skipping")
                self.stats['skipped'] += 1
                return False
            
            course_id = course_data["course_id"]
            branch_id = branch_data.get("branch_id") if branch_data else None
            
            # Check if enrollment already exists
            if await self.check_existing_enrollment(student_id, course_id):
                if self.verbose:
                    print(f"⚠️  Enrollment already exists for user {student_id} and course {course_id}, skipping")
                self.stats['skipped'] += 1
                return False
            
            # Get course details to set proper end date and fees
            course = await self.db.courses.find_one({"id": course_id})
            if not course:
                if self.verbose:
                    print(f"⚠️  Course {course_id} not found, using default values")
            
            # Calculate enrollment dates
            enrollment_date = user.get("created_at", datetime.utcnow())
            if isinstance(enrollment_date, str):
                try:
                    enrollment_date = datetime.fromisoformat(enrollment_date.replace('Z', '+00:00'))
                except:
                    enrollment_date = datetime.utcnow()
            
            start_date = enrollment_date
            end_date = start_date + timedelta(days=365)  # Default 1 year
            
            # Create enrollment record
            enrollment = Enrollment(
                student_id=student_id,
                course_id=course_id,
                branch_id=branch_id,
                start_date=start_date,
                end_date=end_date,
                enrollment_date=enrollment_date,
                fee_amount=0.0,  # Will be updated when payment info is available
                admission_fee=0.0,  # Will be updated when payment info is available
                payment_status="paid",  # Assume paid for migrated data
                is_active=True,
                notes=f"Migrated from user document on {datetime.utcnow().isoformat()}"
            )
            
            if not self.dry_run:
                await self.db.enrollments.insert_one(enrollment.dict())
                if self.verbose:
                    print(f"✅ Created enrollment for user {student_id} in course {course_id}")
            else:
                if self.verbose:
                    print(f"🔄 [DRY RUN] Would create enrollment for user {student_id} in course {course_id}")
            
            self.stats['enrollments_created'] += 1
            return True
            
        except Exception as e:
            print(f"❌ Error creating enrollment for user {user.get('id', 'unknown')}: {e}")
            self.stats['errors'] += 1
            return False

    async def remove_course_data_from_user(self, user_id: str) -> bool:
        """Remove course and branch data from user document after successful migration"""
        try:
            if not self.dry_run:
                await self.db.users.update_one(
                    {"id": user_id},
                    {"$unset": {"course": "", "branch": ""}}
                )
                if self.verbose:
                    print(f"🧹 Removed course/branch data from user {user_id}")
            else:
                if self.verbose:
                    print(f"🔄 [DRY RUN] Would remove course/branch data from user {user_id}")
            return True
        except Exception as e:
            print(f"❌ Error removing course data from user {user_id}: {e}")
            return False

    async def migrate_user(self, user: Dict[str, Any]) -> bool:
        """Migrate a single user's course data"""
        self.stats['users_processed'] += 1
        
        if user.get("course") or user.get("branch"):
            self.stats['users_with_course_data'] += 1
            
            # Create enrollment record
            enrollment_created = await self.create_enrollment_from_user_data(user)
            
            if enrollment_created and not self.dry_run:
                # Remove course data from user document
                await self.remove_course_data_from_user(user["id"])
            
            return enrollment_created
        
        return False

    async def run_migration(self):
        """Run the complete migration process"""
        print("🚀 Starting course data migration...")
        print(f"📊 Mode: {'DRY RUN' if self.dry_run else 'LIVE MIGRATION'}")
        print("-" * 50)
        
        await self.initialize()
        
        # Find users with course data
        users = await self.find_users_with_course_data()
        
        if not users:
            print("✅ No users found with embedded course data. Migration not needed.")
            return
        
        print(f"📋 Processing {len(users)} users...")
        
        # Process each user
        for i, user in enumerate(users, 1):
            if self.verbose:
                print(f"\n👤 Processing user {i}/{len(users)}: {user.get('full_name', user.get('id'))}")
            
            await self.migrate_user(user)
        
        # Print summary
        print("\n" + "=" * 50)
        print("📊 MIGRATION SUMMARY")
        print("=" * 50)
        print(f"Users processed: {self.stats['users_processed']}")
        print(f"Users with course data: {self.stats['users_with_course_data']}")
        print(f"Enrollments created: {self.stats['enrollments_created']}")
        print(f"Errors: {self.stats['errors']}")
        print(f"Skipped: {self.stats['skipped']}")
        
        if self.dry_run:
            print("\n🔄 This was a DRY RUN - no changes were made to the database")
            print("Run without --dry-run to perform the actual migration")
        else:
            print("\n✅ Migration completed successfully!")


async def main():
    parser = argparse.ArgumentParser(description="Migrate course data from user documents to enrollment records")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be migrated without making changes")
    parser.add_argument("--verbose", action="store_true", help="Show detailed output during migration")
    
    args = parser.parse_args()
    
    migrator = CourseDataMigrator(dry_run=args.dry_run, verbose=args.verbose)
    await migrator.run_migration()


if __name__ == "__main__":
    asyncio.run(main())
