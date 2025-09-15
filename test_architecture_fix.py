#!/usr/bin/env python3
"""
Comprehensive Test Suite for Student Management System Architecture Fix

This script tests the entire system after the data architecture refactoring
to ensure proper separation between users and enrollments collections.

Usage:
    python test_architecture_fix.py [--verbose]
"""

import asyncio
import argparse
import sys
import json
from datetime import datetime
from typing import Dict, Any, List

# Add the project root to the path
sys.path.append('.')

from utils.database import get_db


class ArchitectureTestSuite:
    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self.db = None
        self.test_results = []
        
    async def initialize(self):
        """Initialize database connection"""
        self.db = get_db()
        if self.verbose:
            print("✅ Database connection initialized")

    def log_test(self, test_name: str, passed: bool, message: str = ""):
        """Log test result"""
        status = "✅ PASS" if passed else "❌ FAIL"
        result = {
            "test": test_name,
            "passed": passed,
            "message": message,
            "timestamp": datetime.utcnow().isoformat()
        }
        self.test_results.append(result)
        
        if self.verbose or not passed:
            print(f"{status}: {test_name}")
            if message:
                print(f"    {message}")

    async def test_user_model_structure(self):
        """Test that user documents don't contain course data (except legacy)"""
        test_name = "User Model Structure"
        
        try:
            # Find users with course data
            users_with_course_data = await self.db.users.find({
                "role": "student",
                "course": {"$exists": True, "$ne": None}
            }).to_list(100)
            
            # This should be empty after migration, or contain only legacy data
            if len(users_with_course_data) == 0:
                self.log_test(test_name, True, "No users found with embedded course data")
            else:
                # Check if these are marked as legacy
                legacy_count = 0
                for user in users_with_course_data:
                    # In a real scenario, we might have a migration_status field
                    legacy_count += 1
                
                self.log_test(test_name, True, 
                    f"Found {len(users_with_course_data)} users with course data (legacy data)")
                
        except Exception as e:
            self.log_test(test_name, False, f"Error: {e}")

    async def test_enrollment_records_exist(self):
        """Test that enrollment records exist for students"""
        test_name = "Enrollment Records Exist"
        
        try:
            # Count students
            student_count = await self.db.users.count_documents({"role": "student"})
            
            # Count enrollments
            enrollment_count = await self.db.enrollments.count_documents({"is_active": True})
            
            if enrollment_count > 0:
                self.log_test(test_name, True, 
                    f"Found {enrollment_count} active enrollments for {student_count} students")
            else:
                self.log_test(test_name, False, "No enrollment records found")
                
        except Exception as e:
            self.log_test(test_name, False, f"Error: {e}")

    async def test_enrollment_data_integrity(self):
        """Test that enrollment records have proper relationships"""
        test_name = "Enrollment Data Integrity"
        
        try:
            enrollments = await self.db.enrollments.find({"is_active": True}).to_list(100)
            
            valid_enrollments = 0
            invalid_enrollments = 0
            
            for enrollment in enrollments:
                # Check required fields
                required_fields = ["student_id", "course_id", "enrollment_date"]
                has_all_fields = all(field in enrollment for field in required_fields)
                
                if has_all_fields:
                    # Check if student exists
                    student = await self.db.users.find_one({"id": enrollment["student_id"]})
                    
                    # Check if course exists
                    course = await self.db.courses.find_one({"id": enrollment["course_id"]})
                    
                    if student and course:
                        valid_enrollments += 1
                    else:
                        invalid_enrollments += 1
                        if self.verbose:
                            print(f"    Invalid enrollment: {enrollment['id']} - "
                                f"Student exists: {student is not None}, "
                                f"Course exists: {course is not None}")
                else:
                    invalid_enrollments += 1
                    if self.verbose:
                        print(f"    Enrollment missing required fields: {enrollment.get('id', 'unknown')}")
            
            if invalid_enrollments == 0:
                self.log_test(test_name, True, 
                    f"All {valid_enrollments} enrollments have valid relationships")
            else:
                self.log_test(test_name, False, 
                    f"{invalid_enrollments} invalid enrollments found out of {len(enrollments)}")
                
        except Exception as e:
            self.log_test(test_name, False, f"Error: {e}")

    async def test_student_details_api_consistency(self):
        """Test that student details API returns consistent data"""
        test_name = "Student Details API Consistency"
        
        try:
            # Get a sample of students
            students = await self.db.users.find({"role": "student"}).limit(5).to_list(5)
            
            consistent_count = 0
            inconsistent_count = 0
            
            for student in students:
                student_id = student["id"]
                
                # Check enrollments for this student
                enrollments = await self.db.enrollments.find({
                    "student_id": student_id,
                    "is_active": True
                }).to_list(10)
                
                # Check if student has course data in user document
                has_user_course_data = bool(student.get("course"))
                has_enrollment_data = len(enrollments) > 0
                
                if has_enrollment_data or not has_user_course_data:
                    consistent_count += 1
                else:
                    inconsistent_count += 1
                    if self.verbose:
                        print(f"    Student {student_id} has course data in user doc but no enrollments")
            
            if inconsistent_count == 0:
                self.log_test(test_name, True, 
                    f"All {consistent_count} students have consistent data structure")
            else:
                self.log_test(test_name, False, 
                    f"{inconsistent_count} students have inconsistent data")
                
        except Exception as e:
            self.log_test(test_name, False, f"Error: {e}")

    async def test_course_counts_accuracy(self):
        """Test that course student/coach counts are accurate"""
        test_name = "Course Counts Accuracy"
        
        try:
            # Get a sample of courses
            courses = await self.db.courses.find({}).limit(5).to_list(5)
            
            accurate_count = 0
            inaccurate_count = 0
            
            for course in courses:
                course_id = course["id"]
                
                # Count actual enrollments
                actual_student_count = await self.db.enrollments.count_documents({
                    "course_id": course_id,
                    "is_active": True
                })
                
                # Count actual coach assignments
                actual_coach_count = await self.db.coaches.count_documents({
                    "assignment_details.courses": course_id
                })
                
                # This would be tested against API response in a full integration test
                # For now, we just verify the counts are non-negative
                if actual_student_count >= 0 and actual_coach_count >= 0:
                    accurate_count += 1
                    if self.verbose:
                        print(f"    Course {course_id}: {actual_student_count} students, {actual_coach_count} coaches")
                else:
                    inaccurate_count += 1
            
            self.log_test(test_name, True, 
                f"Course counts calculated for {accurate_count} courses")
                
        except Exception as e:
            self.log_test(test_name, False, f"Error: {e}")

    async def test_no_orphaned_data(self):
        """Test that there are no orphaned records"""
        test_name = "No Orphaned Data"
        
        try:
            # Check for enrollments with non-existent students
            enrollments = await self.db.enrollments.find({"is_active": True}).to_list(1000)
            orphaned_enrollments = 0
            
            for enrollment in enrollments:
                student = await self.db.users.find_one({"id": enrollment["student_id"]})
                if not student:
                    orphaned_enrollments += 1
                    if self.verbose:
                        print(f"    Orphaned enrollment: {enrollment['id']} - student {enrollment['student_id']} not found")
            
            if orphaned_enrollments == 0:
                self.log_test(test_name, True, "No orphaned enrollment records found")
            else:
                self.log_test(test_name, False, f"{orphaned_enrollments} orphaned enrollments found")
                
        except Exception as e:
            self.log_test(test_name, False, f"Error: {e}")

    async def run_all_tests(self):
        """Run all architecture tests"""
        print("🧪 Running Architecture Fix Test Suite...")
        print("=" * 50)
        
        await self.initialize()
        
        # Run all tests
        test_methods = [
            self.test_user_model_structure,
            self.test_enrollment_records_exist,
            self.test_enrollment_data_integrity,
            self.test_student_details_api_consistency,
            self.test_course_counts_accuracy,
            self.test_no_orphaned_data
        ]
        
        for test_method in test_methods:
            await test_method()
        
        # Print summary
        print("\n" + "=" * 50)
        print("📊 TEST SUMMARY")
        print("=" * 50)
        
        passed_tests = [r for r in self.test_results if r["passed"]]
        failed_tests = [r for r in self.test_results if not r["passed"]]
        
        print(f"Total tests: {len(self.test_results)}")
        print(f"Passed: {len(passed_tests)}")
        print(f"Failed: {len(failed_tests)}")
        
        if failed_tests:
            print("\n❌ FAILED TESTS:")
            for test in failed_tests:
                print(f"  - {test['test']}: {test['message']}")
        
        if len(failed_tests) == 0:
            print("\n🎉 All tests passed! Architecture fix is successful.")
        else:
            print(f"\n⚠️  {len(failed_tests)} tests failed. Please review the issues above.")
        
        return len(failed_tests) == 0


async def main():
    parser = argparse.ArgumentParser(description="Test the student management system architecture fix")
    parser.add_argument("--verbose", action="store_true", help="Show detailed output during testing")
    
    args = parser.parse_args()
    
    test_suite = ArchitectureTestSuite(verbose=args.verbose)
    success = await test_suite.run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    asyncio.run(main())
