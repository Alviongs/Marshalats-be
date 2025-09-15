from fastapi import HTTPException, Depends
from typing import Optional
from datetime import datetime

from models.course_models import CourseCreate, CourseUpdate, Course
from models.user_models import UserRole
from utils.auth import require_role, get_current_active_user
from utils.database import get_db
from utils.helpers import serialize_doc

class CourseController:
    @staticmethod
    async def create_course(
        course_data: CourseCreate,
        current_user: dict = None
    ):
        """Create new course with comprehensive nested structure"""
        if not current_user:
            raise HTTPException(status_code=401, detail="Authentication required")

        db = get_db()
        course = Course(**course_data.dict())

        # Store the course with nested structure exactly as provided
        course_dict = course.dict()

        await db.courses.insert_one(course_dict)
        return {"message": "Course created successfully", "course_id": course.id}

    @staticmethod
    async def get_courses(
        category_id: Optional[str] = None,
        difficulty_level: Optional[str] = None,
        instructor_id: Optional[str] = None,
        active_only: bool = True,
        skip: int = 0,
        limit: int = 50,
        current_user: dict = None
    ):
        """Get courses with enhanced data including branch assignments, instructor counts, and student enrollments"""
        if not current_user:
            raise HTTPException(status_code=401, detail="Authentication required")

        db = get_db()
        filter_query = {}

        if active_only:
            filter_query["settings.active"] = True
        if category_id:
            filter_query["category_id"] = category_id
        if difficulty_level:
            filter_query["difficulty_level"] = difficulty_level
        if instructor_id:
            filter_query["instructor_id"] = instructor_id

        courses = await db.courses.find(filter_query).skip(skip).limit(limit).to_list(length=limit)

        # Enhance courses with additional data
        enhanced_courses = []
        for course in courses:
            # Get branch assignments for this course
            branches = await db.branches.find({
                "assignments.courses": course["id"],
                "is_active": True
            }).to_list(length=100)

            # Get instructor assignments (coaches assigned to this course)
            # Query coaches collection for coaches assigned to this specific course
            instructors = await db.coaches.find({
                "assignment_details.courses": course["id"],
                "is_active": True
            }).to_list(length=100)

            # Get student enrollment count
            enrollment_count = await db.enrollments.count_documents({
                "course_id": course["id"],
                "is_active": True
            })

            # Create enhanced course object
            enhanced_course = serialize_doc(course)
            enhanced_course.update({
                "branch_assignments": [
                    {
                        "branch_id": branch["id"],
                        "branch_name": branch["branch"]["name"],
                        "branch_code": branch["branch"]["code"],
                        "location": f"{branch['branch']['address']['area']}, {branch['branch']['address']['city']}"
                    }
                    for branch in branches
                ],
                "instructor_count": len(instructors),
                "instructor_assignments": [
                    {
                        "instructor_id": instructor["id"],
                        "instructor_name": instructor.get("full_name", f"{instructor.get('first_name', '')} {instructor.get('last_name', '')}".strip()),
                        "email": instructor.get("email", instructor.get("contact_info", {}).get("email", ""))
                    }
                    for instructor in instructors
                ],
                "student_enrollment_count": enrollment_count,
                # Add display fields for frontend compatibility
                "name": course["title"],  # Map title to name for frontend
                "branches": len(branches),  # Number of branches
                "masters": len(instructors),  # Number of instructors
                "students": enrollment_count,  # Number of students
                "icon": "🥋",  # Default icon for martial arts courses
                "enabled": course.get("settings", {}).get("active", True)
            })

            enhanced_courses.append(enhanced_course)

        return {"courses": enhanced_courses}

    @staticmethod
    async def get_course(
        course_id: str,
        current_user: dict = None
    ):
        """Get course by ID with nested structure"""
        if not current_user:
            raise HTTPException(status_code=401, detail="Authentication required")

        db = get_db()
        course = await db.courses.find_one({"id": course_id})
        if not course:
            raise HTTPException(status_code=404, detail="Course not found")
        return serialize_doc(course)

    @staticmethod
    async def get_courses_by_branch(
        branch_id: str,
        current_user: dict = None
    ):
        """Get courses assigned to a specific branch"""
        if not current_user:
            raise HTTPException(status_code=401, detail="Authentication required")

        db = get_db()

        try:
            # First, get the branch to find assigned courses
            branch = await db.branches.find_one({"id": branch_id})
            if not branch:
                raise HTTPException(status_code=404, detail=f"Branch not found: {branch_id}")

            # Get course IDs assigned to this branch
            course_ids = branch.get("assignments", {}).get("courses", [])

            if not course_ids:
                return {"courses": [], "total": 0}

            # Fetch course details for assigned course IDs
            courses = await db.courses.find({
                "id": {"$in": course_ids},
                "settings.active": True
            }).to_list(length=100)

            # Enhance courses with additional data
            enhanced_courses = []
            for course in courses:
                # Get instructor assignments (coaches assigned to this course at this branch)
                instructors = await db.coaches.find({
                    "assignment_details.courses": course["id"],
                    "branch_id": branch_id,
                    "is_active": True
                }).to_list(length=100)

                # Get student enrollment count for this course at this branch
                enrollment_count = await db.enrollments.count_documents({
                    "course_id": course["id"],
                    "branch_id": branch_id,
                    "is_active": True
                })

                # Create enhanced course object
                enhanced_course = serialize_doc(course)
                # Use 'title' field for course name (not 'name')
                enhanced_course.update({
                    "name": course.get("title", course.get("name", "Unknown Course")),
                    "enrolled_students": enrollment_count,
                    "instructor_name": instructors[0].get("full_name", f"{instructors[0].get('first_name', '')} {instructors[0].get('last_name', '')}".strip()) if instructors else None,
                    "instructor_count": len(instructors),
                    "difficulty_level": course.get("difficulty_level", "Beginner")
                })
                enhanced_courses.append(enhanced_course)

            return {"courses": enhanced_courses, "total": len(enhanced_courses)}

        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

    @staticmethod
    async def update_course(
        course_id: str,
        course_update: CourseUpdate,
        current_user: dict = None
    ):
        """Update course with nested structure"""
        if not current_user:
            raise HTTPException(status_code=401, detail="Authentication required")

        db = get_db()
        
        # Check if course exists
        existing_course = await db.courses.find_one({"id": course_id})
        if not existing_course:
            raise HTTPException(status_code=404, detail="Course not found")
        
        # Coach Admin permission check
        if current_user["role"] == UserRole.COACH_ADMIN:
            # Check if user is the instructor of this course or can manage it
            if existing_course.get("instructor_id") != current_user["id"]:
                raise HTTPException(status_code=403, detail="You can only update courses where you are the instructor.")

        update_data = {k: v for k, v in course_update.dict(exclude_unset=True).items()}
        if not update_data:
            raise HTTPException(status_code=400, detail="No update data provided")

        update_data["updated_at"] = datetime.utcnow()
        
        result = await db.courses.update_one(
            {"id": course_id},
            {"$set": update_data}
        )
        
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Course not found")
        
        return {"message": "Course updated successfully"}

    @staticmethod
    async def get_course_stats(
        course_id: str,
        current_user: dict = None
    ):
        """Get statistics for a specific course."""
        if not current_user:
            raise HTTPException(status_code=401, detail="Authentication required")

        db = get_db()
        course = await db.courses.find_one({"id": course_id})
        if not course:
            raise HTTPException(status_code=404, detail="Course not found")

        active_enrollments = await db.enrollments.count_documents({"course_id": course_id, "is_active": True})

        stats = {
            "course_details": serialize_doc(course),
            "active_enrollments": active_enrollments
        }
        return stats

    @staticmethod
    async def delete_course(
        course_id: str,
        current_user: dict = None
    ):
        """Delete course (soft delete by setting active to False)"""
        if not current_user:
            raise HTTPException(status_code=401, detail="Authentication required")

        db = get_db()

        # Check if course exists
        existing_course = await db.courses.find_one({"id": course_id})
        if not existing_course:
            raise HTTPException(status_code=404, detail="Course not found")

        # Soft delete by setting settings.active to False
        result = await db.courses.update_one(
            {"id": course_id},
            {"$set": {"settings.active": False, "updated_at": datetime.utcnow()}}
        )

        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Course not found")

        return {"message": "Course deleted successfully"}

    @staticmethod
    async def get_public_courses(
        active_only: bool = True,
        skip: int = 0,
        limit: int = 100
    ):
        """Get all courses with enhanced data - Public endpoint (no authentication required)"""
        db = get_db()

        # Build query
        query = {}
        if active_only:
            query["settings.active"] = True

        # Apply pagination
        if limit > 100:
            limit = 100  # Cap at 100 for public endpoint

        # Get courses
        courses_cursor = db.courses.find(query).skip(skip).limit(limit)
        courses = await courses_cursor.to_list(limit)

        # Enhance courses with additional data
        enhanced_courses = []
        for course in courses:
            # Get branch assignments for this course
            branches = await db.branches.find({
                "assignments.courses": course["id"],
                "is_active": True
            }).to_list(length=100)

            # Get instructor assignments (coaches assigned to this course)
            # Query coaches collection for coaches assigned to this specific course
            instructors = await db.coaches.find({
                "assignment_details.courses": course["id"],
                "is_active": True
            }).to_list(length=100)

            # Get student enrollment count
            enrollment_count = await db.enrollments.count_documents({
                "course_id": course["id"],
                "is_active": True
            })

            # Create enhanced course object
            enhanced_course = serialize_doc(course)
            enhanced_course.update({
                "branch_assignments": [
                    {
                        "branch_id": branch["id"],
                        "branch_name": branch["branch"]["name"],
                        "branch_code": branch["branch"]["code"],
                        "location": f"{branch['branch']['address']['area']}, {branch['branch']['address']['city']}"
                    }
                    for branch in branches
                ],
                "instructor_count": len(instructors),
                "instructor_assignments": [
                    {
                        "instructor_id": instructor["id"],
                        "instructor_name": instructor.get("full_name", f"{instructor.get('first_name', '')} {instructor.get('last_name', '')}".strip()),
                        "email": instructor.get("email", instructor.get("contact_info", {}).get("email", ""))
                    }
                    for instructor in instructors
                ],
                "student_enrollment_count": enrollment_count,
                # Add display fields for frontend compatibility
                "name": course["title"],  # Map title to name for frontend
                "branches": len(branches),  # Number of branches
                "masters": len(instructors),  # Number of instructors
                "students": enrollment_count,  # Number of students
                "icon": "🥋",  # Default icon for martial arts courses
                "enabled": course.get("settings", {}).get("active", True)
            })

            enhanced_courses.append(enhanced_course)

        # Get total count
        total = await db.courses.count_documents(query)

        return {
            "message": f"Retrieved {len(enhanced_courses)} courses successfully",
            "courses": enhanced_courses,
            "total": total,
            "skip": skip,
            "limit": limit
        }

    @staticmethod
    async def get_courses_by_category(
        category_id: str,
        difficulty_level: Optional[str] = None,
        active_only: bool = True,
        include_durations: bool = True,
        skip: int = 0,
        limit: int = 50
    ):
        """Get all courses filtered by category - Public endpoint"""
        db = get_db()

        # Verify category exists
        category = await db.categories.find_one({"id": category_id})
        if not category:
            raise HTTPException(status_code=404, detail="Category not found")

        # Build query
        query = {"category_id": category_id}
        if difficulty_level:
            query["difficulty_level"] = difficulty_level
        if active_only:
            query["settings.active"] = True

        # Apply pagination
        if limit > 100:
            limit = 100

        # Get courses
        courses_cursor = db.courses.find(query).skip(skip).limit(limit)
        courses = await courses_cursor.to_list(limit)

        # Get total count
        total = await db.courses.count_documents(query)

        # Enrich courses with additional data
        enriched_courses = []
        for course in courses:
            # Get available durations
            available_durations = []
            if include_durations:
                durations = await db.durations.find({"is_active": True}).sort("display_order", 1).to_list(100)
                base_price = course.get("pricing", {}).get("amount", 0)

                for duration in durations:
                    multiplier = duration.get("pricing_multiplier", 1.0)
                    duration_data = {
                        "id": duration["id"],
                        "name": duration["name"],
                        "duration_months": duration["duration_months"],
                        "pricing_multiplier": multiplier
                    }
                    available_durations.append(duration_data)

            # Get locations where this course is offered
            branches = await db.branches.find({
                "assignments.courses": course["id"],
                "is_active": True
            }).to_list(100)

            location_map = {}
            for branch in branches:
                city = branch["branch"]["address"]["city"]
                if city not in location_map:
                    # Try to find location record
                    location = await db.locations.find_one({
                        "name": {"$regex": city, "$options": "i"},
                        "is_active": True
                    })
                    location_map[city] = {
                        "location_id": location["id"] if location else None,
                        "location_name": location["name"] if location else city,
                        "branch_count": 1
                    }
                else:
                    location_map[city]["branch_count"] += 1

            course_data = {
                "id": course["id"],
                "title": course["title"],
                "code": course["code"],
                "description": course["description"],
                "difficulty_level": course["difficulty_level"],
                "pricing": {
                    "currency": course.get("pricing", {}).get("currency", "INR"),
                    "amount": course.get("pricing", {}).get("amount", 0)
                },
                "student_requirements": course.get("student_requirements", {}),
                "available_durations": available_durations,
                "locations_offered": list(location_map.values())
            }
            enriched_courses.append(course_data)

        return {
            "message": f"Retrieved {len(enriched_courses)} courses for category successfully",
            "category": {
                "id": category["id"],
                "name": category["name"],
                "code": category["code"]
            },
            "courses": enriched_courses,
            "total": total
        }

    @staticmethod
    async def get_courses_by_location(
        location_id: str,
        category_id: Optional[str] = None,
        difficulty_level: Optional[str] = None,
        include_durations: bool = True,
        include_branches: bool = False,
        active_only: bool = True,
        skip: int = 0,
        limit: int = 50
    ):
        """Get courses available at a specific location - Public endpoint"""
        db = get_db()

        # Verify location exists
        location = await db.locations.find_one({"id": location_id})
        if not location:
            raise HTTPException(status_code=404, detail="Location not found")

        # Find branches in this location
        branches = await db.branches.find({
            "branch.address.city": {"$regex": location["name"], "$options": "i"},
            "is_active": True
        }).to_list(100)

        if not branches:
            return {
                "message": "No branches found for this location",
                "location": {
                    "id": location["id"],
                    "name": location["name"],
                    "code": location["code"],
                    "branch_count": 0
                },
                "courses": [],
                "total": 0
            }

        # Get all course IDs offered at these branches
        course_ids = set()
        branch_course_map = {}

        for branch in branches:
            branch_courses = branch.get("assignments", {}).get("courses", [])
            course_ids.update(branch_courses)

            for course_id in branch_courses:
                if course_id not in branch_course_map:
                    branch_course_map[course_id] = []
                branch_course_map[course_id].append({
                    "id": branch["id"],
                    "name": branch["branch"]["name"],
                    "code": branch["branch"]["code"],
                    "area": branch["branch"]["address"]["area"]
                })

        # Build course query
        course_query = {"id": {"$in": list(course_ids)}}
        if category_id:
            course_query["category_id"] = category_id
        if difficulty_level:
            course_query["difficulty_level"] = difficulty_level
        if active_only:
            course_query["settings.active"] = True

        # Apply pagination
        if limit > 100:
            limit = 100

        # Get courses
        courses_cursor = db.courses.find(course_query).skip(skip).limit(limit)
        courses = await courses_cursor.to_list(limit)

        # Get total count
        total = await db.courses.count_documents(course_query)

        # Enrich courses with additional data
        enriched_courses = []
        for course in courses:
            # Get category info
            category = await db.categories.find_one({"id": course["category_id"]})

            # Get available durations
            available_durations = []
            if include_durations:
                durations = await db.durations.find({"is_active": True}).sort("display_order", 1).to_list(100)
                base_price = course.get("pricing", {}).get("amount", 0)

                for duration in durations:
                    multiplier = duration.get("pricing_multiplier", 1.0)
                    final_price = base_price * multiplier
                    duration_data = {
                        "id": duration["id"],
                        "name": duration["name"],
                        "duration_months": duration["duration_months"],
                        "final_price": final_price
                    }
                    available_durations.append(duration_data)

            # Get branches offering this course
            branches_offering = []
            if include_branches:
                branches_offering = branch_course_map.get(course["id"], [])

            course_data = {
                "id": course["id"],
                "title": course["title"],
                "code": course["code"],
                "description": course["description"],
                "category": {
                    "id": category["id"] if category else None,
                    "name": category["name"] if category else "Unknown",
                    "code": category["code"] if category else "UNK"
                },
                "difficulty_level": course["difficulty_level"],
                "pricing": {
                    "currency": course.get("pricing", {}).get("currency", "INR"),
                    "amount": course.get("pricing", {}).get("amount", 0)
                },
                "available_durations": available_durations,
                "branches_offering": branches_offering
            }
            enriched_courses.append(course_data)

        return {
            "message": f"Retrieved {len(enriched_courses)} courses for location successfully",
            "location": {
                "id": location["id"],
                "name": location["name"],
                "code": location["code"],
                "branch_count": len(branches)
            },
            "courses": enriched_courses,
            "total": total
        }
