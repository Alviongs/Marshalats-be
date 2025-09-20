from fastapi import HTTPException, Request
from typing import Optional, List
from datetime import datetime
import secrets
import uuid

from models.coach_models import CoachCreate, CoachUpdate, Coach, CoachResponse, CoachLogin, CoachLoginResponse
from models.user_models import UserRole
from utils.auth import hash_password, verify_password, create_access_token, SECRET_KEY, ALGORITHM
from utils.database import get_db
from utils.helpers import serialize_doc, log_activity, send_sms, send_whatsapp
from utils.email_service import send_password_reset_email
import jwt
from datetime import timedelta

class CoachController:
    @staticmethod
    async def create_coach(
        coach_data: CoachCreate,
        request: Request,
        current_admin: dict
    ):
        """Create new coach with comprehensive nested structure"""
        db = get_db()
        
        # Check if user exists
        full_phone = f"{coach_data.contact_info.country_code}{coach_data.contact_info.phone}"
        existing_coach = await db.coaches.find_one({
            "$or": [
                {"email": coach_data.contact_info.email}, 
                {"phone": full_phone},
                {"contact_info.phone": coach_data.contact_info.phone}
            ]
        })
        if existing_coach:
            raise HTTPException(status_code=400, detail="Coach with this email or phone already exists")
        
        # Generate password if not provided
        if not coach_data.contact_info.password:
            coach_data.contact_info.password = secrets.token_urlsafe(8)
        
        # Hash password
        hashed_password = hash_password(coach_data.contact_info.password)
        
        # Generate full name from first and last name
        full_name = f"{coach_data.personal_info.first_name} {coach_data.personal_info.last_name}".strip()
        
        # Parse and validate date of birth
        try:
            datetime.strptime(coach_data.personal_info.date_of_birth, "%Y-%m-%d")
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")
        
        # Import AssignmentDetails for default creation
        from models.coach_models import AssignmentDetails, EmergencyContact

        # Create coach object
        coach = Coach(
            personal_info=coach_data.personal_info,
            contact_info=coach_data.contact_info,
            address_info=coach_data.address_info,
            professional_info=coach_data.professional_info,
            areas_of_expertise=coach_data.areas_of_expertise,
            branch_id=coach_data.branch_id,  # Include branch assignment
            assignment_details=coach_data.assignment_details or AssignmentDetails(),  # Ensure assignment_details exists
            emergency_contact=coach_data.emergency_contact or EmergencyContact(),  # Ensure emergency_contact exists
            email=coach_data.contact_info.email,
            phone=full_phone,
            first_name=coach_data.personal_info.first_name,
            last_name=coach_data.personal_info.last_name,
            full_name=full_name,
            password_hash=hashed_password
        )
        
        # Convert to dict for storage (exclude password from contact_info)
        coach_dict = coach.dict()
        # Remove password from nested contact_info for storage
        coach_dict["contact_info"] = {
            "email": coach_data.contact_info.email,
            "country_code": coach_data.contact_info.country_code,
            "phone": coach_data.contact_info.phone
        }
        
        # Insert into coaches collection
        result = await db.coaches.insert_one(coach_dict)
        
        # Send credentials via SMS
        sms_message = (
            f"Welcome {full_name}!\n"
            f"Your coach account has been created.\n"
            f"Email: {coach_data.contact_info.email}\n"
            f"Password: {coach_data.contact_info.password}\n"
            f"Role: Coach\n"
            f"Areas of Expertise: {', '.join(coach_data.areas_of_expertise)}"
        )
        await send_sms(full_phone, sms_message)
        
        # Log activity
        await log_activity(
            request=request,
            action="coach_creation",
            user_id=current_admin["id"],
            user_name=current_admin.get("full_name", "Admin"),
            details={
                "created_coach_id": coach.id,
                "coach_email": coach_data.contact_info.email,
                "areas_of_expertise": coach_data.areas_of_expertise
            }
        )

        return {"message": "Coach created successfully", "coach_id": coach.id}

    @staticmethod
    async def get_coaches(
        skip: int = 0,
        limit: int = 50,
        active_only: bool = True,
        area_of_expertise: Optional[str] = None,
        current_user: dict = None
    ):
        """Get coaches with filtering"""
        if not current_user:
            raise HTTPException(status_code=401, detail="Authentication required")

        db = get_db()

        filter_query = {}
        if active_only:
            filter_query["is_active"] = True
        if area_of_expertise:
            filter_query["areas_of_expertise"] = {"$in": [area_of_expertise]}

        # Apply role-based filtering
        current_role = current_user.get("role")
        if current_role == "branch_manager":
            # Branch managers can only see coaches in their managed branches
            # We need to find all branches managed by this branch manager, not just one branch_id

            # Get all branches where this branch manager is the manager
            branch_manager_id = current_user.get("id")
            if not branch_manager_id:
                return {
                    "coaches": [],
                    "total_count": 0,
                    "skip": skip,
                    "limit": limit,
                    "message": "Branch manager ID not found"
                }

            # Find all branches managed by this branch manager
            managed_branches = await db.branches.find({"manager_id": branch_manager_id, "is_active": True}).to_list(length=None)

            if not managed_branches:
                return {
                    "coaches": [],
                    "total_count": 0,
                    "skip": skip,
                    "limit": limit,
                    "message": "No branches assigned to this manager"
                }

            # Get all branch IDs managed by this branch manager
            managed_branch_ids = [branch["id"] for branch in managed_branches]
            print(f"Branch manager {branch_manager_id} manages branches: {managed_branch_ids}")

            # Filter coaches to only those in the managed branches
            filter_query["branch_id"] = {"$in": managed_branch_ids}
        
        coaches = await db.coaches.find(filter_query).skip(skip).limit(limit).to_list(length=limit)
        
        # Convert to response format (remove sensitive data)
        coach_responses = []
        for coach in coaches:
            coach_response = CoachResponse(
                id=coach["id"],
                personal_info=coach["personal_info"],
                contact_info=coach["contact_info"],  # Already cleaned of password
                address_info=coach["address_info"],
                professional_info=coach["professional_info"],
                areas_of_expertise=coach["areas_of_expertise"],
                branch_id=coach.get("branch_id"),  # Include branch assignment
                assignment_details=coach.get("assignment_details"),  # Include course assignments
                emergency_contact=coach.get("emergency_contact"),  # Include emergency contact
                full_name=coach["full_name"],
                is_active=coach["is_active"],
                created_at=coach["created_at"],
                updated_at=coach["updated_at"]
            )
            coach_responses.append(coach_response.dict())
        
        total_count = await db.coaches.count_documents(filter_query)
        
        return {
            "coaches": coach_responses,
            "total": total_count,
            "page": skip // limit + 1 if limit > 0 else 1,
            "limit": limit
        }

    @staticmethod
    async def get_coach_by_id(coach_id: str, current_user: dict = None):
        """Get coach by ID - accessible by Super Admin, Coach Admin, Coach, and Branch Manager"""
        if not current_user:
            raise HTTPException(status_code=401, detail="Authentication required")

        db = get_db()

        coach = await db.coaches.find_one({"id": coach_id})
        if not coach:
            raise HTTPException(status_code=404, detail="Coach not found")

        # Role-based access control
        current_role = current_user.get("role")
        if current_role == "branch_manager":
            # Branch managers can only view coaches working in branches they manage
            print(f"🔍 DEBUG: Branch manager {current_user.get('id')} trying to access coach {coach_id}")
            print(f"🔍 DEBUG: Current user data: {current_user}")
            print(f"🔍 DEBUG: Coach data: {coach}")

            # Get managed branches - try multiple approaches
            managed_branch_ids = []

            # Approach 1: Check branch_assignment field
            branch_assignment = current_user.get("branch_assignment", {})
            if branch_assignment and branch_assignment.get("branch_id"):
                managed_branch_ids.append(branch_assignment.get("branch_id"))
                print(f"🔍 DEBUG: Found branch from branch_assignment: {branch_assignment.get('branch_id')}")

            # Approach 2: Check if this branch manager is assigned as manager_id in any branches
            branch_manager_id = current_user.get("id")
            if branch_manager_id:
                managed_branches = await db.branches.find({"manager_id": branch_manager_id, "is_active": True}).to_list(100)
                for branch in managed_branches:
                    managed_branch_ids.append(branch["id"])
                    print(f"🔍 DEBUG: Found branch from manager_id: {branch['id']}")

            if not managed_branch_ids:
                print(f"🔍 DEBUG: No managed branches found for branch manager")
                raise HTTPException(status_code=403, detail="No branch assignment found for branch manager")

            # Check if coach is assigned to any of the managed branches
            coach_branch_id = coach.get("branch_id")
            print(f"🔍 DEBUG: Coach branch_id: {coach_branch_id}")
            print(f"🔍 DEBUG: Managed branch IDs: {managed_branch_ids}")

            if coach_branch_id not in managed_branch_ids:
                raise HTTPException(status_code=403, detail="You can only view coaches working in branches you manage")

        # Convert to response format
        coach_response = CoachResponse(
            id=coach["id"],
            personal_info=coach["personal_info"],
            contact_info=coach["contact_info"],
            address_info=coach["address_info"],
            professional_info=coach["professional_info"],
            areas_of_expertise=coach["areas_of_expertise"],
            branch_id=coach.get("branch_id"),  # Include branch assignment
            assignment_details=coach.get("assignment_details"),  # Include course assignments
            emergency_contact=coach.get("emergency_contact"),  # Include emergency contact
            full_name=coach["full_name"],
            is_active=coach["is_active"],
            created_at=coach["created_at"],
            updated_at=coach["updated_at"]
        )

        return coach_response.dict()

    @staticmethod
    async def update_coach(
        coach_id: str,
        coach_update: CoachUpdate,
        request: Request,
        current_admin: dict
    ):
        """Update coach information"""
        db = get_db()
        
        # Check if coach exists
        existing_coach = await db.coaches.find_one({"id": coach_id})
        if not existing_coach:
            raise HTTPException(status_code=404, detail="Coach not found")
        
        # Prepare update data
        update_data = {}
        
        if coach_update.personal_info:
            update_data["personal_info"] = coach_update.personal_info.dict()
            # Update derived fields
            update_data["first_name"] = coach_update.personal_info.first_name
            update_data["last_name"] = coach_update.personal_info.last_name
            update_data["full_name"] = f"{coach_update.personal_info.first_name} {coach_update.personal_info.last_name}".strip()
            
            # Validate date format if provided
            if coach_update.personal_info.date_of_birth:
                try:
                    datetime.strptime(coach_update.personal_info.date_of_birth, "%Y-%m-%d")
                except ValueError:
                    raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")
        
        if coach_update.contact_info:
            # Check for email conflicts if email is being changed
            if coach_update.contact_info.email != existing_coach["email"]:
                email_conflict = await db.coaches.find_one({
                    "email": coach_update.contact_info.email,
                    "id": {"$ne": coach_id}
                })
                if email_conflict:
                    raise HTTPException(status_code=400, detail="Email already exists")
            
            # Update contact info (exclude password from nested structure)
            update_data["contact_info"] = {
                "email": coach_update.contact_info.email,
                "country_code": coach_update.contact_info.country_code,
                "phone": coach_update.contact_info.phone
            }
            update_data["email"] = coach_update.contact_info.email
            update_data["phone"] = f"{coach_update.contact_info.country_code}{coach_update.contact_info.phone}"
            
            # Handle password update if provided
            if coach_update.contact_info.password:
                update_data["password_hash"] = hash_password(coach_update.contact_info.password)
        
        if coach_update.address_info:
            update_data["address_info"] = coach_update.address_info.dict()
        
        if coach_update.professional_info:
            update_data["professional_info"] = coach_update.professional_info.dict()
        
        if coach_update.areas_of_expertise:
            update_data["areas_of_expertise"] = coach_update.areas_of_expertise

        if coach_update.branch_id is not None:  # Allow setting to None to remove branch assignment
            update_data["branch_id"] = coach_update.branch_id

        if coach_update.assignment_details is not None:  # Allow updating course assignments
            update_data["assignment_details"] = coach_update.assignment_details.dict()

        if coach_update.emergency_contact is not None:  # Allow updating emergency contact
            update_data["emergency_contact"] = coach_update.emergency_contact.dict()

        if not update_data:
            raise HTTPException(status_code=400, detail="No update data provided")
        
        update_data["updated_at"] = datetime.utcnow()
        
        # Update coach
        result = await db.coaches.update_one(
            {"id": coach_id},
            {"$set": update_data}
        )
        
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Coach not found")
        
        # Log activity
        await log_activity(
            request=request,
            action="coach_update",
            user_id=current_admin["id"],
            user_name=current_admin.get("full_name", "Admin"),
            details={
                "updated_coach_id": coach_id,
                "update_fields": list(update_data.keys())
            }
        )

        return {"message": "Coach updated successfully"}

    @staticmethod
    async def deactivate_coach(
        coach_id: str,
        request: Request,
        current_admin: dict
    ):
        """Deactivate coach"""
        db = get_db()

        # First, get the coach to check if it exists and get branch info
        coach = await db.coaches.find_one({"id": coach_id})
        if not coach:
            raise HTTPException(status_code=404, detail="Coach not found")

        # If current user is a branch manager, ensure they can only delete coaches from their branch
        current_role = current_admin.get("role")
        if current_role == "branch_manager":
            branch_assignment = current_admin.get("branch_assignment")
            if not branch_assignment or not branch_assignment.get("branch_id"):
                raise HTTPException(status_code=403, detail="No branch assigned to this manager")

            # Check if the coach belongs to the branch manager's branch
            if coach.get("branch_id") != branch_assignment["branch_id"]:
                raise HTTPException(status_code=403, detail="You can only delete coaches from your assigned branch")

        result = await db.coaches.update_one(
            {"id": coach_id},
            {"$set": {"is_active": False, "updated_at": datetime.utcnow()}}
        )

        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Coach not found")
        
        # Log activity
        await log_activity(
            request=request,
            action="coach_deactivation",
            user_id=current_admin["id"],
            user_name=current_admin.get("full_name", "Admin"),
            details={"deactivated_coach_id": coach_id}
        )

        return {"message": "Coach deactivated successfully"}

    @staticmethod
    async def get_coach_courses(coach_id: str, current_user: dict = None):
        """Get courses assigned to a specific coach"""
        if not current_user:
            raise HTTPException(status_code=401, detail="Authentication required")

        db = get_db()

        # Verify coach exists
        coach = await db.coaches.find_one({"id": coach_id})
        if not coach:
            raise HTTPException(status_code=404, detail="Coach not found")

        # Role-based access control
        current_role = current_user.get("role")
        if current_role == "branch_manager":
            # Branch managers can only view courses for coaches in branches they manage
            # Get managed branches - try multiple approaches
            managed_branch_ids = []

            # Approach 1: Check branch_assignment field
            branch_assignment = current_user.get("branch_assignment", {})
            if branch_assignment and branch_assignment.get("branch_id"):
                managed_branch_ids.append(branch_assignment.get("branch_id"))

            # Approach 2: Check if this branch manager is assigned as manager_id in any branches
            branch_manager_id = current_user.get("id")
            if branch_manager_id:
                managed_branches = await db.branches.find({"manager_id": branch_manager_id, "is_active": True}).to_list(100)
                for branch in managed_branches:
                    managed_branch_ids.append(branch["id"])

            if not managed_branch_ids:
                raise HTTPException(status_code=403, detail="No branch assignment found for branch manager")

            # Check if coach is assigned to any of the managed branches
            coach_branch_id = coach.get("branch_id")
            if coach_branch_id not in managed_branch_ids:
                raise HTTPException(status_code=403, detail="You can only view courses for coaches in branches you manage")

        # Permission check: coaches can only view their own courses unless admin
        if current_user["role"] == UserRole.COACH and current_user["id"] != coach_id:
            raise HTTPException(status_code=403, detail="You can only view your own course assignments")

        try:
            # Get courses where this coach is the instructor
            courses = await db.courses.find({
                "instructor_id": coach_id,
                "settings.active": True
            }).to_list(length=100)

            # Also get courses from coach's assignment_details
            assigned_course_ids = coach.get("assignment_details", {}).get("courses", [])
            if assigned_course_ids:
                assigned_courses = await db.courses.find({
                    "id": {"$in": assigned_course_ids},
                    "settings.active": True
                }).to_list(length=100)

                # Merge courses (avoid duplicates)
                course_ids_seen = {course["id"] for course in courses}
                for assigned_course in assigned_courses:
                    if assigned_course["id"] not in course_ids_seen:
                        courses.append(assigned_course)

            # Enhance courses with additional data
            enhanced_courses = []
            for course in courses:
                # Get enrollment count for this course
                enrollment_count = await db.enrollments.count_documents({
                    "course_id": course["id"],
                    "is_active": True
                })

                # Get branch information
                branches = await db.branches.find({
                    "assignments.courses": course["id"],
                    "is_active": True
                }).to_list(length=10)

                enhanced_course = serialize_doc(course)
                enhanced_course.update({
                    "name": course.get("title", course.get("name", "Unknown Course")),
                    "enrolled_students": enrollment_count,
                    "difficulty_level": course.get("difficulty_level", "Beginner"),
                    "branch_assignments": [
                        {
                            "branch_id": branch["id"],
                            "branch_name": branch["branch"]["name"]
                        }
                        for branch in branches
                    ]
                })
                enhanced_courses.append(enhanced_course)

            return {"courses": enhanced_courses, "total": len(enhanced_courses)}

        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error fetching coach courses: {str(e)}")

    @staticmethod
    async def get_coach_students(coach_id: str, current_user: dict = None):
        """Get students enrolled in courses taught by a specific coach"""
        if not current_user:
            raise HTTPException(status_code=401, detail="Authentication required")

        db = get_db()

        # Verify coach exists
        coach = await db.coaches.find_one({"id": coach_id})
        if not coach:
            raise HTTPException(status_code=404, detail="Coach not found")

        # Role-based access control
        current_role = current_user.get("role")
        if current_role == "branch_manager":
            # Branch managers can only view students for coaches in branches they manage
            # Get managed branches - try multiple approaches
            managed_branch_ids = []

            # Approach 1: Check branch_assignment field
            branch_assignment = current_user.get("branch_assignment", {})
            if branch_assignment and branch_assignment.get("branch_id"):
                managed_branch_ids.append(branch_assignment.get("branch_id"))

            # Approach 2: Check if this branch manager is assigned as manager_id in any branches
            branch_manager_id = current_user.get("id")
            if branch_manager_id:
                managed_branches = await db.branches.find({"manager_id": branch_manager_id, "is_active": True}).to_list(100)
                for branch in managed_branches:
                    managed_branch_ids.append(branch["id"])

            if not managed_branch_ids:
                raise HTTPException(status_code=403, detail="No branch assignment found for branch manager")

            # Check if coach is assigned to any of the managed branches
            coach_branch_id = coach.get("branch_id")
            if coach_branch_id not in managed_branch_ids:
                raise HTTPException(status_code=403, detail="You can only view students for coaches in branches you manage")

        # Permission check: coaches can only view their own students unless admin
        if current_user["role"] == UserRole.COACH and current_user["id"] != coach_id:
            raise HTTPException(status_code=403, detail="You can only view your own students")

        try:
            # Get courses taught by this coach
            course_ids = []

            # Get courses where this coach is the instructor
            instructor_courses = await db.courses.find({
                "instructor_id": coach_id,
                "settings.active": True
            }).to_list(length=100)
            course_ids.extend([course["id"] for course in instructor_courses])

            # Also get courses from coach's assignment_details
            assigned_course_ids = coach.get("assignment_details", {}).get("courses", [])
            course_ids.extend(assigned_course_ids)

            # Remove duplicates
            course_ids = list(set(course_ids))

            if not course_ids:
                return {"students": [], "total": 0}

            # Get enrollments for these courses
            enrollments = await db.enrollments.find({
                "course_id": {"$in": course_ids},
                "is_active": True
            }).to_list(length=1000)

            # Get student details and course information
            enhanced_students = []
            for enrollment in enrollments:
                # Get student details
                student = await db.users.find_one({
                    "id": enrollment["student_id"],
                    "role": "student"
                })

                # Get course details
                course = await db.courses.find_one({"id": enrollment["course_id"]})

                if student and course:
                    enhanced_student = {
                        "id": student["id"],
                        "student_name": student.get("full_name", f"{student.get('first_name', '')} {student.get('last_name', '')}".strip()),
                        "email": student.get("email", student.get("contact_info", {}).get("email", "")),
                        "course_id": course["id"],
                        "course_name": course.get("title", course.get("name", "Unknown Course")),
                        "enrollment_date": enrollment.get("enrollment_date", enrollment.get("created_at", "")),
                        "status": "active" if enrollment.get("is_active", True) else "inactive",
                        "progress": enrollment.get("progress", 0),
                        "branch_id": enrollment.get("branch_id", "")
                    }
                    enhanced_students.append(enhanced_student)

            return {"students": enhanced_students, "total": len(enhanced_students)}

        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error fetching coach students: {str(e)}")

    @staticmethod
    async def get_coach_stats():
        """Get coach statistics"""
        db = get_db()

        total_coaches = await db.coaches.count_documents({})
        active_coaches = await db.coaches.count_documents({"is_active": True})
        inactive_coaches = total_coaches - active_coaches

        # Get coaches by expertise areas
        pipeline = [
            {"$unwind": "$areas_of_expertise"},
            {"$group": {"_id": "$areas_of_expertise", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}}
        ]
        expertise_stats = await db.coaches.aggregate(pipeline).to_list(length=None)

        return {
            "total_coaches": total_coaches,
            "active_coaches": active_coaches,
            "inactive_coaches": inactive_coaches,
            "expertise_distribution": expertise_stats
        }

    @staticmethod
    async def login_coach(login_data: CoachLogin):
        """Authenticate coach and return JWT token"""
        try:
            db = get_db()
            
            # Find coach by email
            coach = await db.coaches.find_one({"contact_info.email": login_data.email})
            if not coach:
                raise HTTPException(
                    status_code=401,
                    detail="Invalid email or password"
                )
            
            # Verify password
            if not verify_password(login_data.password, coach["password_hash"]):
                raise HTTPException(
                    status_code=401,
                    detail="Invalid email or password"
                )
            
            # Check if coach is active
            if not coach.get("is_active", True):
                raise HTTPException(
                    status_code=401,
                    detail="Account is inactive. Please contact administrator."
                )
            
            # Create access token
            access_token_expires = 60 * 24  # 24 hours in minutes
            access_token = create_access_token(
                data={
                    "sub": coach["id"],
                    "email": coach["contact_info"]["email"],
                    "role": "coach",
                    "coach_id": coach["id"]
                }
            )
            
            # Prepare coach data for response (without sensitive info)
            coach_data = serialize_doc(coach)
            if "password_hash" in coach_data:
                del coach_data["password_hash"]
            
            return {
                "access_token": access_token,
                "token_type": "bearer",
                "coach": coach_data,
                "expires_in": access_token_expires * 60,  # Convert to seconds
                "message": "Login successful"
            }
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Internal server error during coach login: {str(e)}"
            )

    @staticmethod
    async def forgot_password(email: str):
        """Initiate password reset process for coach"""
        db = get_db()
        coach = await db.coaches.find_one({"contact_info.email": email})

        if not coach:
            # Don't reveal that the coach does not exist
            return {"message": "If a coach account with that email exists, a password reset link has been sent."}

        # Generate a short-lived token for password reset (same as student implementation)
        reset_token = create_access_token(
            data={"sub": coach["id"], "scope": "password_reset"},
            expires_delta=timedelta(minutes=15)
        )

        # Send password reset email with coach branding using webhook (same as /api/email/send-webhook-email)
        coach_name = coach.get("full_name", "Coach")
        from utils.email_service import send_password_reset_email_webhook
        email_sent = await send_password_reset_email_webhook(email, reset_token, coach_name, "coach")

        # Log the password reset attempt (same as student implementation)
        import logging
        logging.info(f"Password reset requested for coach {email}. Email sent: {email_sent}")

        # Also send SMS as backup (if phone number exists) - same as student implementation
        coach_phone = coach.get("phone") or coach.get("contact_info", {}).get("phone")
        if coach_phone:
            from utils.helpers import send_sms
            sms_message = f"Coach password reset requested for your account. Check your email ({email}) for reset instructions. If you didn't request this, please ignore."
            await send_sms(coach_phone, sms_message)

        response = {"message": "If a coach account with that email exists, a password reset link has been sent."}

        # Include token in response for testing purposes (same as student implementation)
        import os
        if os.environ.get("TESTING") == "True":
            response["reset_token"] = reset_token
            response["email_sent"] = email_sent

        return response

    @staticmethod
    async def reset_password(token: str, new_password: str):
        """Reset coach password using a token"""
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            if payload.get("scope") != "password_reset":
                raise HTTPException(status_code=401, detail="Invalid token scope")

            coach_id = payload.get("sub")
            if not coach_id:
                raise HTTPException(status_code=401, detail="Invalid token")

        except jwt.PyJWTError:
            raise HTTPException(status_code=401, detail="Invalid or expired token")

        new_hashed_password = hash_password(new_password)
        db = get_db()
        result = await db.coaches.update_one(
            {"id": coach_id},
            {"$set": {"password": new_hashed_password, "updated_at": datetime.utcnow()}}
        )

        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Coach not found")

        return {"message": "Password has been reset successfully"}

    @staticmethod
    async def send_credentials_email(
        coach_id: str,
        request: Request,
        current_admin: dict
    ):
        """Send login credentials to coach via email with secure password reset token"""
        db = get_db()

        # Get coach details
        coach = await db.coaches.find_one({"id": coach_id})
        if not coach:
            raise HTTPException(status_code=404, detail="Coach not found")

        # Get coach email
        coach_email = coach.get("email") or coach.get("contact_info", {}).get("email")
        if not coach_email:
            raise HTTPException(status_code=400, detail="Coach email not found")

        # Get coach name
        coach_name = coach.get("full_name") or f"{coach.get('personal_info', {}).get('first_name', '')} {coach.get('personal_info', {}).get('last_name', '')}".strip()
        if not coach_name:
            coach_name = "Coach"

        # Generate a password reset token for secure access (same as forgot password)
        reset_token = create_access_token(
            data={"sub": coach["id"], "scope": "password_reset"},
            expires_delta=timedelta(minutes=15)
        )

        # Create password reset link
        reset_link = f"http://localhost:3022/coach/reset-password?token={reset_token}"

        # Prepare email content
        subject = "Your Coach Login Credentials - Marshalarts Academy"

        # Create HTML email content (consistent with forgot password styling)
        html_message = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Coach Login Credentials</title>
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
        .header {{ background-color: #f8f9fa; padding: 20px; text-align: center; border-radius: 8px 8px 0 0; }}
        .content {{ background-color: #ffffff; padding: 30px; border: 1px solid #e9ecef; }}
        .footer {{ background-color: #f8f9fa; padding: 15px; text-align: center; border-radius: 0 0 8px 8px; font-size: 12px; color: #6c757d; }}
        .btn {{ display: inline-block; padding: 12px 24px; background-color: #ea580c; color: white; text-decoration: none; border-radius: 5px; font-weight: bold; margin: 20px 0; }}
        .btn:hover {{ opacity: 0.9; }}
        .info-box {{ background-color: #f8f9fa; padding: 15px; border-radius: 5px; margin: 20px 0; }}
        .warning {{ background-color: #fff3cd; border: 1px solid #ffeaa7; padding: 15px; border-radius: 5px; margin: 20px 0; }}
        .role-header {{ color: #ea580c; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1 style="margin: 0; color: #ea580c;">🥋 Marshalarts Academy</h1>
            <p style="margin: 5px 0 0 0; color: #666;">Coach Portal</p>
        </div>

        <div class="content">
            <h2 class="role-header">Welcome to the Coach Portal!</h2>
            <p>Hello <strong>{coach_name}</strong>,</p>

            <p>Your coach account has been created successfully. You can now access the coach portal using your login credentials.</p>

            <div class="info-box">
                <p><strong>📧 Email:</strong> {coach_email}</p>
                <p><strong>🔑 Password Setup:</strong> Click the button below to set up your password securely</p>
                <div style="text-align: center;">
                    <a href="{reset_link}" class="btn">Set Up Your Password</a>
                </div>
            </div>

            <div class="warning">
                <strong>🔒 Security Notice:</strong> This password setup link will expire in 15 minutes for security. After setting your password, you can log in at the coach portal.
            </div>

            <h3 style="color: #ea580c;">Next Steps:</h3>
            <ul>
                <li><strong>Step 1:</strong> Click "Set Up Your Password" button above</li>
                <li><strong>Step 2:</strong> Create a secure password for your account</li>
                <li><strong>Step 3:</strong> Visit the <a href="http://localhost:3022/coach/login" style="color: #ea580c;">Coach Portal</a> to log in</li>
                <li><strong>Step 4:</strong> Complete your profile setup and review your assigned courses</li>
            </ul>

            <p><strong>Important:</strong> The password setup link expires in 15 minutes. If it expires, please contact your administrator for a new link.</p>

            <p>If you have any questions or need assistance, please contact our support team.</p>
        </div>

        <div class="footer">
            <p style="margin: 0;">© 2025 Marshalarts Academy. All rights reserved.</p>
            <p style="margin: 5px 0 0 0;">This is an automated message, please do not reply.</p>
        </div>
    </div>
</body>
</html>""".strip()

        # Plain text version (consistent with forgot password format)
        plain_message = f"""🥋 Welcome to Marshalarts Academy - Coach Portal

Hello {coach_name},

Your coach account has been created successfully. You can now set up your password and access the coach portal.

📧 Email: {coach_email}
🔑 Password Setup: {reset_link}
🔗 Coach Portal: http://localhost:3022/coach/login

🔒 SECURITY NOTICE: The password setup link above will expire in 15 minutes for security. After setting your password, you can log in at the coach portal.

Next Steps:
1. Click the password setup link above
2. Create a secure password for your account
3. Visit the Coach Portal to log in with your email and new password
4. Complete your profile setup and review your assigned courses

IMPORTANT: The password setup link expires in 15 minutes. If it expires, please contact your administrator for a new link.

If you have any questions or need assistance, please contact our support team.

Best regards,
Marshalarts Academy Team

© 2025 Marshalarts Academy. All rights reserved.
This is an automated message, please do not reply.""".strip()

        try:
            # Send email using custom webhook service (same as forgot password implementation)
            from utils.email_service import send_custom_email_webhook
            email_sent = await send_custom_email_webhook(
                coach_email,
                subject,
                html_message,
                plain_message
            )

            # Log the credentials email attempt (same as forgot password implementation)
            import logging
            logging.info(f"Coach credentials email requested for {coach_email}. Email sent: {email_sent}")

            # Log the activity in database
            await log_activity(
                request=request,
                action="send_coach_credentials",
                user_id=current_admin.get("id"),
                user_name=current_admin.get("full_name", "Admin"),
                details={
                    "coach_id": coach_id,
                    "coach_name": coach_name,
                    "coach_email": coach_email,
                    "email_sent": email_sent
                }
            )

            # Prepare response (consistent with forgot password format)
            response = {
                "message": "Login credentials have been sent to the coach's email address",
                "email_sent": email_sent,
                "coach_email": coach_email
            }

            # Include additional info for testing purposes (same as forgot password implementation)
            import os
            if os.environ.get("TESTING") == "True":
                response["coach_id"] = coach_id
                response["coach_name"] = coach_name
                response["reset_token"] = reset_token
                response["reset_link"] = reset_link

            return response

        except Exception as e:
            # Enhanced error logging (consistent with forgot password implementation)
            import logging
            logging.error(f"Failed to send coach credentials email to {coach_email}: {str(e)}")

            raise HTTPException(
                status_code=500,
                detail=f"Failed to send credentials email: {str(e)}"
            )
