from fastapi import HTTPException
from typing import Optional, List, Dict, Any
from datetime import datetime

from models.user_models import UserRole
from utils.database import get_db
from utils.helpers import serialize_doc

class BranchesWithCoursesController:
    @staticmethod
    async def get_branches_with_courses(
        branch_id: Optional[str] = None,
        status: Optional[str] = None,
        include_inactive: bool = False,
        current_user: dict = None
    ):
        """
        Get branches with their associated courses based on filtering criteria.
        
        Args:
            branch_id: Filter by specific branch ID, or "all" for all branches
            status: Filter by branch status ("active" or "inactive")
            include_inactive: Include inactive branches when no status filter is applied
            current_user: Current authenticated user
            
        Returns:
            Dict containing branches with courses, summary statistics, and filter info
        """
        if not current_user:
            raise HTTPException(status_code=401, detail="Authentication required")

        db = get_db()
        
        # Build branch filter query
        branch_filter = {}
        
        # Apply branch_id filter
        if branch_id and branch_id != "all":
            branch_filter["id"] = branch_id
        
        # Apply status filter (default to active only unless include_inactive is true)
        if status:
            is_active = status.lower() == "active"
            branch_filter["is_active"] = is_active
        elif not include_inactive:
            # Default behavior: only show active branches unless explicitly requested
            branch_filter["is_active"] = True
        
        # Fetch branches from database
        branches_cursor = db.branches.find(branch_filter)
        branches = await branches_cursor.to_list(length=None)
        
        # If specific branch ID requested but not found
        if branch_id and branch_id != "all" and not branches:
            raise HTTPException(
                status_code=404,
                detail=f"Branch not found with ID: {branch_id}"
            )
        
        # If no branches match the filters
        if not branches:
            return {
                "message": f"No {status} branches found" if status else "No branches found matching criteria",
                "branches": [],
                "total": 0,
                "summary": {
                    "total_branches": 0,
                    "total_courses": 0,
                    "total_students": 0,
                    "total_coaches": 0
                },
                "filters_applied": {
                    "branch_id": branch_id or "all",
                    "status": status or ("all" if include_inactive else "active"),
                    "include_inactive": include_inactive
                }
            }
        
        # Enhance branches with courses and statistics
        enhanced_branches = []
        total_courses = 0
        total_students = 0
        total_coaches = 0
        
        for branch in branches:
            branch_id_current = branch["id"]
            
            # Get courses assigned to this branch
            course_ids = branch.get("assignments", {}).get("courses", [])
            branch_courses = []
            
            if course_ids:
                courses_cursor = db.courses.find({"id": {"$in": course_ids}})
                courses = await courses_cursor.to_list(length=None)
                
                for course in courses:
                    # Serialize and structure course data
                    course_data = serialize_doc(course)
                    
                    # Ensure all required fields are present with defaults
                    structured_course = {
                        "id": course_data.get("id", ""),
                        "title": course_data.get("title", ""),
                        "name": course_data.get("title", ""),  # Use title as name fallback
                        "code": course_data.get("code", ""),
                        "description": course_data.get("description", ""),
                        "difficulty_level": course_data.get("difficulty_level", ""),
                        "pricing": course_data.get("pricing", {
                            "currency": "INR",
                            "amount": 0,
                            "branch_specific_pricing": False
                        }),
                        "student_requirements": course_data.get("student_requirements", {
                            "max_students": 0,
                            "min_age": 0,
                            "max_age": 100,
                            "prerequisites": []
                        }),
                        "settings": course_data.get("settings", {
                            "active": True,
                            "offers_certification": False
                        }),
                        "created_at": course_data.get("created_at", datetime.utcnow().isoformat()),
                        "updated_at": course_data.get("updated_at", datetime.utcnow().isoformat())
                    }
                    branch_courses.append(structured_course)
            
            # Count coaches assigned to this branch
            coach_count = await db.coaches.count_documents({
                "branch_assignments": {"$in": [branch_id_current]},
                "is_active": True
            })
            
            # Count students enrolled in courses at this branch
            student_count = await db.enrollments.count_documents({
                "branch_id": branch_id_current,
                "status": "active"
            })
            
            # Count active courses for this branch
            active_courses = len([c for c in branch_courses if c.get("settings", {}).get("active", True)])
            
            # Serialize branch data
            branch_data = serialize_doc(branch)
            
            # Structure the enhanced branch data
            enhanced_branch = {
                "id": branch_data.get("id", ""),
                "branch": branch_data.get("branch", {}),
                "manager_id": branch_data.get("manager_id", ""),
                "is_active": branch_data.get("is_active", True),
                "operational_details": branch_data.get("operational_details", {}),
                "assignments": branch_data.get("assignments", {}),
                "bank_details": branch_data.get("bank_details", {}),
                "statistics": {
                    "coach_count": coach_count,
                    "student_count": student_count,
                    "course_count": len(branch_courses),
                    "active_courses": active_courses
                },
                "courses": branch_courses,
                "created_at": branch_data.get("created_at", datetime.utcnow().isoformat()),
                "updated_at": branch_data.get("updated_at", datetime.utcnow().isoformat())
            }
            
            enhanced_branches.append(enhanced_branch)
            
            # Update totals
            total_courses += len(branch_courses)
            total_students += student_count
            total_coaches += coach_count
        
        return {
            "message": "Branches with courses retrieved successfully",
            "branches": enhanced_branches,
            "total": len(enhanced_branches),
            "summary": {
                "total_branches": len(enhanced_branches),
                "total_courses": total_courses,
                "total_students": total_students,
                "total_coaches": total_coaches
            },
            "filters_applied": {
                "branch_id": branch_id or "all",
                "status": status or ("all" if include_inactive else "active"),
                "include_inactive": include_inactive
            }
        }
