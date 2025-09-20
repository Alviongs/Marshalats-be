from fastapi import HTTPException, Depends, Request
from typing import Optional, List
from datetime import datetime, date
import secrets
import uuid

from models.user_models import UserCreate, UserUpdate, BaseUser, UserRole
from utils.auth import hash_password, require_role, get_current_active_user
from utils.unified_auth import require_role_unified, get_current_user_or_superadmin
from utils.database import get_db
from utils.helpers import serialize_doc, log_activity, send_sms, send_whatsapp

class UserController:
    @staticmethod
    async def create_user(
        user_data: UserCreate,
        request: Request,
        current_user: dict = None
    ):
        """Create new user (Super Admin or Coach Admin)"""
        if not current_user:
            raise HTTPException(status_code=401, detail="Authentication required")
            
        # Get current user role as enum
        current_role = current_user.get("role")
        if isinstance(current_role, str):
            try:
                current_role = UserRole(current_role)
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid user role")
        
        # If a coach admin is creating a user, they must be in the same branch
        if current_role == UserRole.COACH_ADMIN:
            if not current_user.get("branch_id") or user_data.branch_id != current_user["branch_id"]:
                raise HTTPException(status_code=403, detail="Coach Admins can only create users for their own branch.")
            # Coach admins cannot create other admins
            if user_data.role in [UserRole.SUPER_ADMIN, UserRole.COACH_ADMIN]:
                raise HTTPException(status_code=403, detail="Coach Admins cannot create other admin users.")

        # Check if user exists
        db = get_db()
        existing_user = await db.users.find_one({
            "$or": [{"email": user_data.email}, {"phone": user_data.phone}]
        })
        if existing_user:
            raise HTTPException(status_code=400, detail="User already exists")
        
        # Generate password if not provided
        if not user_data.password:
            user_data.password = secrets.token_urlsafe(8)

        hashed_password = hash_password(user_data.password)

        # Generate full name from first and last name
        full_name = f"{user_data.first_name} {user_data.last_name}".strip()

        # Create user dictionary with proper structure (similar to registration API)
        user_dict = {
            "id": str(uuid.uuid4()),
            "email": user_data.email,
            "phone": user_data.phone,
            "first_name": user_data.first_name,
            "last_name": user_data.last_name,
            "full_name": full_name,
            "role": user_data.role.value,  # Convert enum to string
            "biometric_id": user_data.biometric_id,
            "is_active": True,
            "date_of_birth": user_data.date_of_birth.isoformat() if user_data.date_of_birth else None,
            "gender": user_data.gender,
            "password": hashed_password,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }

        # Set branch_id for staff members
        if user_data.branch_id:
            user_dict["branch_id"] = user_data.branch_id

        # BACKWARD COMPATIBILITY: Store course and branch data in user document
        # This ensures existing frontend integrations continue to work
        if user_data.course:
            user_dict["course"] = {
                "category_id": user_data.course.category_id,
                "course_id": user_data.course.course_id,
                "duration": user_data.course.duration
            }

        if user_data.branch:
            user_dict["branch"] = {
                "location_id": user_data.branch.location_id,
                "branch_id": user_data.branch.branch_id
            }
            # Also set branch_id for easier querying
            if not user_dict.get("branch_id"):
                user_dict["branch_id"] = user_data.branch.branch_id

        await db.users.insert_one(user_dict)

        # Create enrollment record if course information is provided (for students)
        enrollment_id = None
        if user_data.course and user_data.branch and user_data.role == UserRole.STUDENT:
            try:
                from models.enrollment_models import Enrollment, PaymentStatus
                from datetime import timedelta

                # Create enrollment record in the proper collection
                enrollment = Enrollment(
                    student_id=user_dict["id"],
                    course_id=user_data.course.course_id,
                    branch_id=user_data.branch.branch_id,
                    start_date=datetime.utcnow(),
                    end_date=datetime.utcnow() + timedelta(days=365),  # Default 1 year
                    fee_amount=0.0,  # Will be updated when payment is processed
                    admission_fee=0.0,  # Will be updated when payment is processed
                    payment_status=PaymentStatus.PENDING,
                    enrollment_date=datetime.utcnow(),
                    is_active=True
                )

                enrollment_result = await db.enrollments.insert_one(enrollment.dict())
                enrollment_id = enrollment.id

            except Exception as e:
                # Log error but don't fail the user creation if enrollment creation fails
                print(f"❌ Error creating enrollment record: {e}")
                pass
        
        # Send credentials
        await send_sms(user_dict["phone"], f"Account created. Email: {user_dict['email']}, Password: {user_data.password}")

        await log_activity(
            request=request,
            action="admin_create_user",
            user_id=current_user["id"],
            user_name=current_user["full_name"],
            details={"created_user_id": user_dict["id"], "created_user_email": user_dict["email"], "role": user_dict["role"]}
        )

        response_data = {"message": "User created successfully", "user_id": user_dict["id"]}
        if enrollment_id:
            response_data["enrollment_id"] = enrollment_id
            response_data["message"] = "User created and enrolled successfully"

        return response_data

    @staticmethod
    async def get_users(
        role: Optional[UserRole] = None,
        branch_id: Optional[str] = None,
        skip: int = 0,
        limit: int = 50,
        current_user: dict = None
    ):
        """Get users with filtering - accessible by Super Admin, Coach Admin, and Coach"""
        if not current_user:
            raise HTTPException(status_code=401, detail="Authentication required")
            
        filter_query = {}
        
        # Get current user role as enum
        current_role = current_user.get("role")
        if isinstance(current_role, str):
            try:
                current_role = UserRole(current_role)
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid user role")
        
        # Apply role-based filtering
        if current_role == UserRole.COACH_ADMIN:
            # Coach admins can only see users in their branch
            if current_user.get("branch_id"):
                filter_query["branch_id"] = current_user["branch_id"]
        elif current_role == UserRole.COACH:
            # Coaches can only see students in their branch
            if current_user.get("branch_id"):
                filter_query["branch_id"] = current_user["branch_id"]
            filter_query["role"] = UserRole.STUDENT.value  # Only show students to coaches
        
        # Apply additional filters
        if role:
            # Only allow if current user has permission to see this role
            if current_role == UserRole.COACH and role != UserRole.STUDENT:
                raise HTTPException(status_code=403, detail="Coaches can only view student users")
            filter_query["role"] = role.value
            
        if branch_id:
            # Ensure user can only filter by their own branch if not super admin
            if current_role in [UserRole.COACH_ADMIN, UserRole.COACH]:
                if current_user.get("branch_id") != branch_id:
                    raise HTTPException(status_code=403, detail="You can only view users from your own branch")
            filter_query["branch_id"] = branch_id
        
        db = get_db()
        users = await db.users.find(filter_query).skip(skip).limit(limit).to_list(length=limit)
        total_count = await db.users.count_documents(filter_query)
        
        for user in users:
            user.pop("password", None)
            user["date_of_birth"] = user.get("date_of_birth")
            user["gender"] = user.get("gender")
        
        return {
            "users": serialize_doc(users),
            "total": total_count,
            "skip": skip,
            "limit": limit,
            "message": f"Retrieved {len(users)} users"
        }

    @staticmethod
    async def get_user(
        user_id: str,
        current_user: dict = None
    ):
        """Get single user by ID - accessible by Super Admin, Coach Admin, and Coach"""
        if not current_user:
            raise HTTPException(status_code=401, detail="Authentication required")

        db = get_db()
        user = await db.users.find_one({"id": user_id})

        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        # Get current user role as enum
        current_role = current_user.get("role")
        if isinstance(current_role, str):
            try:
                current_role = UserRole(current_role)
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid user role")

        # Role-based access control
        if current_role in [UserRole.COACH_ADMIN, UserRole.COACH]:
            # Coach Admin and Coach can only view users from their own branch
            if current_user.get("branch_id") != user.get("branch_id"):
                raise HTTPException(status_code=403, detail="You can only view users from your own branch")

        # Remove sensitive information
        user.pop("password", None)
        user["date_of_birth"] = user.get("date_of_birth")
        user["gender"] = user.get("gender")

        # For students, also fetch enrollment data to provide complete course information
        enrollments = []
        if user.get("role") == "student":
            try:
                enrollments = await db.enrollments.find({
                    "student_id": user_id,
                    "is_active": True
                }).to_list(100)

                # Enrich enrollment data with course and branch details
                for enrollment in enrollments:
                    # Get course details
                    course = await db.courses.find_one({"id": enrollment["course_id"]})
                    if course:
                        enrollment["course_details"] = {
                            "id": course["id"],
                            "title": course.get("title", "Unknown Course"),
                            "category_id": course.get("category_id"),
                            "difficulty_level": course.get("difficulty_level", "Beginner")
                        }

                    # Get branch details
                    branch = await db.branches.find_one({"id": enrollment["branch_id"]})
                    if branch:
                        enrollment["branch_details"] = {
                            "id": branch["id"],
                            "name": branch.get("branch", {}).get("name", "Unknown Branch"),
                            "location_id": branch.get("branch", {}).get("address", {}).get("city", "")
                        }

            except Exception as e:
                print(f"Error fetching enrollment data for user {user_id}: {e}")
                # Don't fail the request if enrollment fetch fails

        return {
            "user": serialize_doc(user),
            "enrollments": serialize_doc(enrollments),
            "message": "User retrieved successfully"
        }

    @staticmethod
    async def handle_enrollment_updates(user_id: str, course_data: dict, branch_data: dict):
        """Handle enrollment record updates when course/branch data changes"""
        db = get_db()

        try:
            # Check if user has existing active enrollments
            existing_enrollments = await db.enrollments.find({
                "student_id": user_id,
                "is_active": True
            }).to_list(100)

            if course_data and branch_data:
                course_id = course_data.get("course_id")
                branch_id = branch_data.get("branch_id")

                if course_id and branch_id:
                    # Check if enrollment already exists for this course/branch combination
                    existing_enrollment = None
                    for enrollment in existing_enrollments:
                        if (enrollment.get("course_id") == course_id and
                            enrollment.get("branch_id") == branch_id):
                            existing_enrollment = enrollment
                            break

                    if existing_enrollment:
                        # Update existing enrollment
                        await db.enrollments.update_one(
                            {"id": existing_enrollment["id"]},
                            {"$set": {
                                "updated_at": datetime.utcnow(),
                                "is_active": True
                            }}
                        )
                        print(f"✅ Updated existing enrollment: {existing_enrollment['id']}")
                    else:
                        # Create new enrollment record
                        from models.enrollment_models import Enrollment, PaymentStatus
                        from datetime import timedelta

                        enrollment = Enrollment(
                            student_id=user_id,
                            course_id=course_id,
                            branch_id=branch_id,
                            start_date=datetime.utcnow(),
                            end_date=datetime.utcnow() + timedelta(days=365),
                            fee_amount=0.0,
                            admission_fee=0.0,
                            payment_status=PaymentStatus.PENDING,
                            enrollment_date=datetime.utcnow(),
                            is_active=True
                        )

                        await db.enrollments.insert_one(enrollment.dict())
                        print(f"✅ Created new enrollment: {enrollment.id}")

                        # Deactivate other enrollments for this student
                        for old_enrollment in existing_enrollments:
                            if old_enrollment["id"] != enrollment.id:
                                await db.enrollments.update_one(
                                    {"id": old_enrollment["id"]},
                                    {"$set": {"is_active": False, "updated_at": datetime.utcnow()}}
                                )
                                print(f"✅ Deactivated old enrollment: {old_enrollment['id']}")

        except Exception as e:
            print(f"❌ Error handling enrollment updates: {e}")
            # Don't fail the user update if enrollment handling fails

    @staticmethod
    async def update_user(
        user_id: str,
        user_update: UserUpdate,
        request: Request,
        current_user: dict = None
    ):
        """Update user (Super Admin or Coach Admin)"""
        if not current_user:
            raise HTTPException(status_code=401, detail="Authentication required")
            
        target_user = await get_db().users.find_one({"id": user_id})
        if not target_user:
            raise HTTPException(status_code=404, detail="User not found")

        # Get current user role as enum
        current_role = current_user.get("role")
        if isinstance(current_role, str):
            try:
                current_role = UserRole(current_role)
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid user role")

        if current_role == UserRole.COACH_ADMIN:
            # Coach Admins can only update students in their own branch
            if target_user["role"] != UserRole.STUDENT.value:
                raise HTTPException(status_code=403, detail="Coach Admins can only update student profiles.")
            if target_user.get("branch_id") != current_user.get("branch_id"):
                raise HTTPException(status_code=403, detail="Coach Admins can only update students in their own branch.")

        # Convert user_update to dict and handle date serialization
        update_dict = user_update.dict(exclude_unset=True)
        update_data = {}

        for k, v in update_dict.items():
            if k == "date_of_birth" and isinstance(v, date):
                # Convert date object to ISO string for MongoDB compatibility
                update_data[k] = v.isoformat()
            elif k == "course" and v:
                # Handle nested course object (v could be dict or CourseInfo object)
                if isinstance(v, dict):
                    update_data["course"] = v
                else:
                    update_data["course"] = {
                        "category_id": v.category_id,
                        "course_id": v.course_id,
                        "duration": v.duration
                    }
            elif k == "branch" and v:
                # Handle nested branch object (v could be dict or BranchInfo object)
                if isinstance(v, dict):
                    update_data["branch"] = v
                else:
                    update_data["branch"] = {
                        "location_id": v.location_id,
                        "branch_id": v.branch_id
                    }
            elif k in ["course_category_id", "course_id", "course_duration", "location_id"]:
                # Handle flat fields for backward compatibility
                # Convert flat fields to nested structure
                if k == "course_category_id":
                    if "course" not in update_data:
                        update_data["course"] = {}
                    update_data["course"]["category_id"] = v
                elif k == "course_id":
                    if "course" not in update_data:
                        update_data["course"] = {}
                    update_data["course"]["course_id"] = v
                elif k == "course_duration":
                    if "course" not in update_data:
                        update_data["course"] = {}
                    update_data["course"]["duration"] = v
                elif k == "location_id":
                    if "branch" not in update_data:
                        update_data["branch"] = {}
                    update_data["branch"]["location_id"] = v
            else:
                update_data[k] = v

        if not update_data:
            raise HTTPException(status_code=400, detail="No update data provided")

        update_data["updated_at"] = datetime.utcnow()

        # Handle enrollment updates if course/branch data is being changed
        if target_user.get("role") == "student" and ("course" in update_data or "branch" in update_data):
            course_data = update_data.get("course", {})
            branch_data = update_data.get("branch", {})

            # Only handle enrollment if both course and branch data are provided
            if course_data and branch_data:
                await UserController.handle_enrollment_updates(user_id, course_data, branch_data)

        result = await get_db().users.update_one(
            {"id": user_id},
            {"$set": update_data}
        )

        if result.matched_count == 0:
            # This case should be rare due to the check above, but it's good practice
            raise HTTPException(status_code=404, detail="User not found")
        
        await log_activity(
            request=request,
            action="admin_update_user",
            user_id=current_user["id"],
            user_name=current_user["full_name"],
            details={"updated_user_id": user_id, "update_data": user_update.dict(exclude_unset=True)}
        )

        return {"message": "User updated successfully"}

    @staticmethod
    async def force_password_reset(
        user_id: str,
        request: Request,
        current_user: dict = None
    ):
        """Force a password reset for a user (Admins only)."""
        if not current_user:
            raise HTTPException(status_code=401, detail="Authentication required")
            
        target_user = await get_db().users.find_one({"id": user_id})
        if not target_user:
            raise HTTPException(status_code=404, detail="User not found")

        # Get current user role as enum
        current_role = current_user.get("role")
        if isinstance(current_role, str):
            try:
                current_role = UserRole(current_role)
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid user role")

        # Check permissions
        if current_role == UserRole.COACH_ADMIN:
            if target_user.get("branch_id") != current_user.get("branch_id"):
                raise HTTPException(status_code=403, detail="Coach Admins can only reset passwords for users in their own branch.")
            if target_user.get("role") not in [UserRole.STUDENT.value, UserRole.COACH.value]:
                raise HTTPException(status_code=403, detail="Coach Admins can only reset passwords for Students and Coaches.")

        # Generate a new temporary password
        new_password = secrets.token_urlsafe(8)
        hashed_password = hash_password(new_password)

        # Update the user's password in the database
        await get_db().users.update_one(
            {"id": user_id},
            {"$set": {"password": hashed_password, "updated_at": datetime.utcnow()}}
        )

        # Log the activity
        await log_activity(
            request=request,
            action="admin_force_password_reset",
            user_id=current_user["id"],
            user_name=current_user["full_name"],
            details={"reset_user_id": user_id, "reset_user_email": target_user["email"]}
        )

        # Send the new password to the user
        message = f"Your password has been reset by an administrator. Your new temporary password is: {new_password}"
        await send_sms(target_user["phone"], message)
        await send_whatsapp(target_user["phone"], message)

        return {"message": f"Password for user {target_user['full_name']} has been reset and sent to them."}

    @staticmethod
    async def deactivate_user(
        user_id: str,
        request: Request,
        current_user: dict = None
    ):
        """Deactivate user (Super Admin only)"""
        if not current_user:
            raise HTTPException(status_code=401, detail="Authentication required")

        result = await get_db().users.update_one(
            {"id": user_id},
            {"$set": {"is_active": False, "updated_at": datetime.utcnow()}}
        )

        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="User not found")

        await log_activity(
            request=request,
            action="admin_deactivate_user",
            user_id=current_user["id"],
            user_name=current_user["full_name"],
            details={"deactivated_user_id": user_id}
        )

        return {"message": "User deactivated successfully"}

    @staticmethod
    async def delete_user(
        user_id: str,
        request: Request,
        current_user: dict = None
    ):
        """Permanently delete user (Super Admin only)"""
        if not current_user:
            raise HTTPException(status_code=401, detail="Authentication required")

        # Check if user exists
        user = await get_db().users.find_one({"id": user_id})
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        # Don't allow deletion of super admin users
        if user.get("role") == "super_admin":
            raise HTTPException(status_code=403, detail="Cannot delete super admin users")

        # If current user is a branch manager, ensure they can only delete students from their branch
        current_role = current_user.get("role")
        if current_role == "branch_manager":
            branch_assignment = current_user.get("branch_assignment")
            if not branch_assignment or not branch_assignment.get("branch_id"):
                raise HTTPException(status_code=403, detail="No branch assigned to this manager")

            # For students, check if they have any enrollments in courses from this branch
            # or if their branch_id matches (if they have one)
            user_branch_id = user.get("branch_id")
            user_enrollments = user.get("enrollments", [])

            # Check if student belongs to branch manager's branch
            belongs_to_branch = False
            if user_branch_id == branch_assignment["branch_id"]:
                belongs_to_branch = True
            elif user_enrollments:
                # Check enrollments for branch match
                for enrollment in user_enrollments:
                    if enrollment.get("branch_id") == branch_assignment["branch_id"]:
                        belongs_to_branch = True
                        break

            if not belongs_to_branch:
                raise HTTPException(status_code=403, detail="You can only delete students from your assigned branch")

        # Delete user from database
        result = await get_db().users.delete_one({"id": user_id})

        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="User not found")

        # Log the deletion activity
        await log_activity(
            request=request,
            action="admin_delete_user",
            user_id=current_user["id"],
            user_name=current_user["full_name"],
            details={"deleted_user_id": user_id, "deleted_user_email": user.get("email", "N/A")}
        )

        return {"message": "User deleted successfully"}

    @staticmethod
    async def get_student_details(
        current_user: dict = Depends(get_current_user_or_superadmin)
    ):
        """Get detailed student information with course enrollment data (Authenticated endpoint)"""

        if not current_user:
            raise HTTPException(status_code=401, detail="Authentication required")

        db = get_db()

        # Build query based on user role
        query = {"role": "student", "is_active": True}

        # Role-based access control
        current_role = current_user.get("role")
        if isinstance(current_role, str):
            try:
                current_role = UserRole(current_role)
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid user role")

        # Apply branch filtering for non-super-admin users
        if current_role != UserRole.SUPER_ADMIN:
            if current_role == UserRole.BRANCH_MANAGER:
                # Branch managers can see students from their managed branches
                # We need to find all branches managed by this branch manager, not just one branch_id

                # Get all branches where this branch manager is the manager
                branch_manager_id = current_user.get("id")
                if not branch_manager_id:
                    raise HTTPException(status_code=403, detail="Branch manager ID not found")

                # Find all branches managed by this branch manager
                managed_branches = await db.branches.find({"manager_id": branch_manager_id, "is_active": True}).to_list(length=None)

                if not managed_branches:
                    raise HTTPException(status_code=403, detail="No branches assigned to this manager")

                # Get all branch IDs managed by this branch manager
                managed_branch_ids = [branch["id"] for branch in managed_branches]
                print(f"Branch manager {branch_manager_id} manages branches for students: {managed_branch_ids}")

                # Store for later use in enrollment filtering
                managed_branch_ids_for_students = managed_branch_ids
            else:
                # For other roles (coaches, etc.), use their branch_id
                user_branch_id = current_user.get("branch_id")
                if not user_branch_id:
                    raise HTTPException(status_code=403, detail="User not assigned to any branch")
                query["branch_id"] = user_branch_id

        # Get students
        students_cursor = db.users.find(query)
        students = await students_cursor.to_list(1000)

        if not students:
            return {
                "message": "No students found",
                "students": [],
                "total": 0
            }

        # Enrich student data with course and enrollment information
        enriched_students = []

        # For branch managers, we need to filter students based on their enrollments
        if current_role == UserRole.BRANCH_MANAGER and 'managed_branch_ids_for_students' in locals():
            # Get all enrollments for all managed branches
            branch_enrollments = await db.enrollments.find({"branch_id": {"$in": managed_branch_ids_for_students}, "is_active": True}).to_list(1000)
            branch_student_ids = list(set([enrollment["student_id"] for enrollment in branch_enrollments]))

            print(f"Found {len(branch_enrollments)} enrollments across {len(managed_branch_ids_for_students)} managed branches")
            print(f"Unique student IDs with enrollments: {len(branch_student_ids)}")

            # Filter students to only include those with enrollments in the managed branches
            students = [student for student in students if student["id"] in branch_student_ids]

        for student in students:
            student_id = student["id"]

            # Calculate age from date_of_birth
            age = None
            if student.get("date_of_birth"):
                if isinstance(student["date_of_birth"], str):
                    try:
                        birth_date = datetime.strptime(student["date_of_birth"], "%Y-%m-%d").date()
                    except ValueError:
                        birth_date = None
                elif isinstance(student["date_of_birth"], date):
                    birth_date = student["date_of_birth"]
                else:
                    birth_date = None

                if birth_date:
                    today = date.today()
                    age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))

            # Get course information from multiple sources
            courses_info = []

            # Method 1: Check for enrollments in enrollments collection
            enrollments = await db.enrollments.find({"student_id": student_id, "is_active": True}).to_list(100)

            for enrollment in enrollments:
                course = await db.courses.find_one({"id": enrollment["course_id"]})
                if course:
                    # Calculate duration from enrollment dates
                    duration_days = None
                    if enrollment.get("start_date") and enrollment.get("end_date"):
                        start_date = enrollment["start_date"]
                        end_date = enrollment["end_date"]
                        if isinstance(start_date, str):
                            start_date = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
                        if isinstance(end_date, str):
                            end_date = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
                        duration_days = (end_date - start_date).days

                    # Determine level from course difficulty
                    level = course.get("difficulty_level", "Beginner")

                    courses_info.append({
                        "course_id": enrollment["course_id"],
                        "course_name": course.get("title", "Unknown Course"),
                        "level": level,
                        "duration": f"{duration_days} days" if duration_days else "Not specified",
                        "enrollment_date": enrollment.get("enrollment_date"),
                        "payment_status": enrollment.get("payment_status", "pending"),
                        "branch_id": enrollment.get("branch_id")
                    })

            # DEPRECATED: Legacy fallback for students with course data in user documents
            # This will be removed after data migration is complete
            if not courses_info and student.get("course"):
                course_info = student["course"]
                branch_info = student.get("branch", {})

                # Get course details from courses collection
                course_id = course_info.get("course_id")
                course = await db.courses.find_one({"id": course_id})
                if course:
                    # Get branch details
                    branch_name = "Not specified"
                    if branch_info.get("branch_id"):
                        branch = await db.branches.find_one({"id": branch_info["branch_id"]})
                        if branch:
                            branch_name = branch.get("name", "Unknown Branch")

                    # Get duration details - handle both UUID and string formats
                    duration_name = course_info.get("duration", "Not specified")
                    if course_info.get("duration"):
                        # If it's already a readable string, use it directly
                        if isinstance(course_info["duration"], str) and not course_info["duration"].startswith(("uuid-", "duration-")):
                            duration_name = course_info["duration"]
                        else:
                            # Try to look up in durations collection
                            duration = await db.durations.find_one({"id": course_info["duration"]})
                            if duration:
                                duration_name = duration.get("name", duration_name)

                    courses_info.append({
                        "course_name": course.get("title", "Unknown Course"),
                        "level": course.get("difficulty_level", "Beginner"),
                        "duration": duration_name,
                        "enrollment_date": student.get("created_at"),
                        "payment_status": "paid",  # Assume paid for registration-based students
                        "source": "legacy_user_document"  # Mark as legacy data for migration tracking
                    })

            # Prepare student details response
            student_details = {
                "id": student_id,
                "student_id": student_id,
                "full_name": student.get("full_name", f"{student.get('first_name', '')} {student.get('last_name', '')}").strip(),
                "student_name": student.get("full_name", f"{student.get('first_name', '')} {student.get('last_name', '')}").strip(),
                "first_name": student.get("first_name", ""),
                "last_name": student.get("last_name", ""),
                "email": student.get("email"),
                "phone": student.get("phone"),
                "role": student.get("role", "student"),
                "gender": student.get("gender", "Not specified"),
                "age": age,
                "date_of_birth": student.get("date_of_birth"),
                "is_active": student.get("is_active", True),
                "created_at": student.get("created_at"),
                "branch_id": student.get("branch_id"),
                "address": student.get("address"),
                "courses": courses_info,
                "enrollments": courses_info,  # For compatibility with frontend
                "action": "view_profile"  # Default action - can be customized based on requirements
            }

            enriched_students.append(student_details)

        return {
            "message": f"Retrieved {len(enriched_students)} student details successfully",
            "students": enriched_students,
            "total": len(enriched_students)
        }

    @staticmethod
    async def get_user_enrollments(user_id: str, current_user: dict = None):
        """Get enrollment history for a specific student"""
        if not current_user:
            raise HTTPException(status_code=401, detail="Authentication required")

        db = get_db()

        # Verify user exists and is a student
        user = await db.users.find_one({"id": user_id})
        if not user:
            raise HTTPException(status_code=404, detail="Student not found")

        if user.get("role") != "student":
            raise HTTPException(status_code=400, detail="User is not a student")

        # Permission check: coaches can only view students from their branch
        current_role = current_user.get("role")
        if current_role in ["coach", "coach_admin"] and current_user.get("branch_id"):
            if user.get("branch_id") != current_user["branch_id"]:
                raise HTTPException(status_code=403, detail="You can only view students from your branch")

        try:
            # Get enrollments for this student
            enrollments = await db.enrollments.find({
                "student_id": user_id
            }).sort("created_at", -1).to_list(length=100)

            # Enhance enrollments with course and branch information
            enhanced_enrollments = []
            for enrollment in enrollments:
                # Get course details
                course = await db.courses.find_one({"id": enrollment.get("course_id")})

                # Get branch details
                branch = await db.branches.find_one({"id": enrollment.get("branch_id")})

                enhanced_enrollment = serialize_doc(enrollment)
                enhanced_enrollment.update({
                    "course_name": course.get("title", course.get("name", "Unknown Course")) if course else "Unknown Course",
                    "course_difficulty": course.get("difficulty_level", "Beginner") if course else "Beginner",
                    "branch_name": branch.get("branch", {}).get("name", "Unknown Branch") if branch else "Unknown Branch",
                    "enrollment_date": enrollment.get("enrollment_date", enrollment.get("created_at", "")),
                    "completion_date": enrollment.get("completion_date"),
                    "status": enrollment.get("status", "active"),
                    "progress": enrollment.get("progress", 0),
                    "is_active": enrollment.get("is_active", True)
                })
                enhanced_enrollments.append(enhanced_enrollment)

            return {
                "enrollments": enhanced_enrollments,
                "total": len(enhanced_enrollments)
            }

        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error fetching enrollment history: {str(e)}")

    @staticmethod
    async def get_user_payments(user_id: str, current_user: dict = None):
        """Get payment history for a specific student"""
        if not current_user:
            raise HTTPException(status_code=401, detail="Authentication required")

        db = get_db()

        # Verify user exists and is a student
        user = await db.users.find_one({"id": user_id})
        if not user:
            raise HTTPException(status_code=404, detail="Student not found")

        if user.get("role") != "student":
            raise HTTPException(status_code=400, detail="User is not a student")

        # Permission check: coaches can only view students from their branch
        current_role = current_user.get("role")
        if current_role in ["coach", "coach_admin"] and current_user.get("branch_id"):
            if user.get("branch_id") != current_user["branch_id"]:
                raise HTTPException(status_code=403, detail="You can only view students from your branch")

        try:
            # Get payments for this student with course and enrollment information
            pipeline = [
                {"$match": {"student_id": user_id}},
                {
                    "$lookup": {
                        "from": "enrollments",
                        "localField": "enrollment_id",
                        "foreignField": "id",
                        "as": "enrollment_info"
                    }
                },
                {"$unwind": {"path": "$enrollment_info", "preserveNullAndEmptyArrays": True}},
                {
                    "$lookup": {
                        "from": "courses",
                        "localField": "enrollment_info.course_id",
                        "foreignField": "id",
                        "as": "course_info"
                    }
                },
                {"$unwind": {"path": "$course_info", "preserveNullAndEmptyArrays": True}},
                {
                    "$project": {
                        "id": 1,
                        "student_id": 1,
                        "enrollment_id": 1,
                        "amount": 1,
                        "payment_type": 1,
                        "payment_method": 1,
                        "payment_status": 1,
                        "transaction_id": 1,
                        "payment_date": 1,
                        "due_date": 1,
                        "notes": 1,
                        "course_name": {"$ifNull": ["$course_info.title", "$course_info.name"]},
                        "course_difficulty": "$course_info.difficulty_level",
                        "enrollment_date": "$enrollment_info.enrollment_date",
                        "created_at": 1,
                        "updated_at": 1
                    }
                },
                {"$sort": {"created_at": -1}}
            ]

            payments = await db.payments.aggregate(pipeline).to_list(length=100)

            # Convert to serializable format
            enhanced_payments = []
            for payment in payments:
                enhanced_payment = {}
                for key, value in payment.items():
                    if key == "_id":
                        continue
                    elif hasattr(value, 'isoformat'):  # datetime objects
                        enhanced_payment[key] = value.isoformat()
                    else:
                        enhanced_payment[key] = value

                # Add formatted payment description
                course_name = enhanced_payment.get("course_name", "Course")
                payment_type = enhanced_payment.get("payment_type", "payment")
                enhanced_payment["description"] = f"{course_name} - {payment_type.replace('_', ' ').title()}"

                enhanced_payments.append(enhanced_payment)

            return {
                "payments": enhanced_payments,
                "total": len(enhanced_payments)
            }

        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error fetching payment history: {str(e)}")
