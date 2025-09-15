from fastapi import HTTPException, Depends, status, Request
from typing import Optional
from datetime import datetime, timedelta
import secrets
import jwt
import os
import logging
import uuid

from models.user_models import UserCreate, UserLogin, ForgotPassword, ResetPassword, UserUpdate, BaseUser, UserRole
from utils.auth import hash_password, verify_password, create_access_token, get_current_active_user, SECRET_KEY, ALGORITHM
from utils.database import get_db
from utils.helpers import serialize_doc, log_activity, send_sms
from utils.email_service import send_password_reset_email

class AuthController:
    @staticmethod
    async def register_user(user_data: UserCreate, request: Request):
        """Register a new student (public endpoint)"""
        db = get_db()
        
        # Check if user exists
        existing_user = await db.users.find_one({
            "$or": [{"email": user_data.email}, {"phone": user_data.phone}]
        })
        if existing_user:
            raise HTTPException(status_code=400, detail="User with this email or phone already exists")
        
        # Generate password if not provided
        if not user_data.password:
            user_data.password = secrets.token_urlsafe(8)
        
        # Hash password
        hashed_password = hash_password(user_data.password)
        
        # Generate full name from first and last name
        full_name = f"{user_data.first_name} {user_data.last_name}".strip()
        
        # Create user dictionary with nested structure exactly as requested
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

        result = await db.users.insert_one(user_dict)

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
                # Log error but don't fail the registration if enrollment creation fails
                print(f"❌ Error creating enrollment record: {e}")
                pass
        
        # Send credentials via SMS (mock)
        course_info = "No course selected"
        branch_info = "No branch assigned"

        if enrollment_id and user_data.course and user_data.branch:
            course_info = f"Course: {user_data.course.course_id} ({user_data.course.duration})"
            branch_info = f"Branch: {user_data.branch.branch_id}"
        elif user_data.branch_id:
            branch_info = f"Branch: {user_data.branch_id}"

        sms_message = (
            f"Welcome {user_dict['full_name']}!\n"
            f"Your account has been created.\n"
            f"Email: {user_dict['email']}\n"
            f"Password: {user_data.password}\n"
            f"Date of Birth: {user_dict['date_of_birth']}\n"
            f"Gender: {user_dict['gender']}\n"
            f"{course_info}\n"
            f"{branch_info}"
        )
        await send_sms(user_dict["phone"], sms_message)
        
        await log_activity(
            request=request,
            action="user_registration",
            user_id=user_dict["id"],
            user_name=user_dict["full_name"],
            details={"email": user_dict["email"], "role": user_dict["role"]}
        )

        response_data = {"message": "User registered successfully", "user_id": user_dict["id"]}
        if enrollment_id:
            response_data["enrollment_id"] = enrollment_id
            response_data["message"] = "User registered and enrolled successfully"

        return response_data

    @staticmethod
    async def login(user_credentials: UserLogin, request: Request):
        """User login"""
        db = get_db()
        
        user = await db.users.find_one({"email": user_credentials.email})
        if not user or not verify_password(user_credentials.password, user["password"]):
            await log_activity(
                request=request,
                action="login_attempt",
                status="failure",
                details={"email": user_credentials.email, "reason": "Incorrect email or password"}
            )
            raise HTTPException(status_code=401, detail="Incorrect email or password")
        
        if not user.get("is_active", False):
            await log_activity(
                request=request,
                action="login_attempt",
                status="failure",
                user_id=user["id"],
                user_name=user["full_name"],
                details={"email": user_credentials.email, "reason": "Account is deactivated"}
            )
            raise HTTPException(status_code=400, detail="Account is deactivated")
        
        access_token = create_access_token(data={"sub": user["id"], "role": user["role"]})

        await log_activity(
            request=request,
            action="login_success",
            user_id=user["id"],
            user_name=user["full_name"],
            details={"email": user["email"]}
        )

        return {"access_token": access_token, "token_type": "bearer", "user": {
            "id": user["id"],
            "email": user["email"],
            "role": user["role"],
            "first_name": user.get("first_name"),
            "last_name": user.get("last_name"),
            "full_name": user["full_name"],
            "date_of_birth": user.get("date_of_birth"),
            "gender": user.get("gender"),
            "course": user.get("course"),  # Return nested course object directly
            "branch": user.get("branch")   # Return nested branch object directly
        }}

    @staticmethod
    async def forgot_password(forgot_password_data: ForgotPassword):
        """Initiate password reset process with email functionality"""
        db = get_db()
        user = await db.users.find_one({"email": forgot_password_data.email})
        if not user:
            # Don't reveal that the user does not exist
            return {"message": "If an account with that email exists, a password reset link has been sent."}

        # Generate a short-lived token for password reset
        reset_token = create_access_token(
            data={"sub": user["id"], "scope": "password_reset"},
            expires_delta=timedelta(minutes=15)
        )

        # Send password reset email
        user_name = user.get("full_name", f"{user.get('first_name', '')} {user.get('last_name', '')}").strip()
        email_sent = await send_password_reset_email(
            to_email=user["email"],
            reset_token=reset_token,
            user_name=user_name or "User"
        )

        # Log the password reset attempt
        logging.info(f"Password reset requested for {user['email']}. Email sent: {email_sent}")

        # Also send SMS as backup (if phone number exists)
        if user.get("phone"):
            sms_message = f"Password reset requested for your account. Check your email ({user['email']}) for reset instructions. If you didn't request this, please ignore."
            await send_sms(user["phone"], sms_message)

        response = {"message": "If an account with that email exists, a password reset link has been sent."}

        # Include token in response for testing purposes
        if os.environ.get("TESTING") == "True":
            response["reset_token"] = reset_token
            response["email_sent"] = email_sent

        return response

    @staticmethod
    async def reset_password(reset_password_data: ResetPassword):
        """Reset password using a token"""
        try:
            payload = jwt.decode(
                reset_password_data.token,
                SECRET_KEY,
                algorithms=[ALGORITHM]
            )
            if payload.get("scope") != "password_reset":
                raise HTTPException(status_code=401, detail="Invalid token scope")

            user_id = payload.get("sub")
            if not user_id:
                raise HTTPException(status_code=401, detail="Invalid token")

        except jwt.PyJWTError:
            raise HTTPException(status_code=401, detail="Invalid or expired token")

        new_hashed_password = hash_password(reset_password_data.new_password)
        db = get_db()
        result = await db.users.update_one(
            {"id": user_id},
            {"$set": {"password": new_hashed_password, "updated_at": datetime.utcnow()}}
        )

        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="User not found")

        return {"message": "Password has been reset successfully."}

    @staticmethod
    async def get_current_user_info(current_user: dict = Depends(get_current_active_user)):
        """Get current user information"""
        user_info = current_user.copy()
        user_info.pop("password", None)
        user_info["date_of_birth"] = current_user.get("date_of_birth")
        user_info["gender"] = current_user.get("gender")
        return user_info

    @staticmethod
    async def update_profile(user_update: UserUpdate, current_user: dict = Depends(get_current_active_user)):
        """Update user profile"""
        update_data = {k: v for k, v in user_update.dict().items() if v is not None}
        update_data["updated_at"] = datetime.utcnow()
        
        # Ensure date_of_birth and gender are included in the update
        if user_update.date_of_birth:
            update_data["date_of_birth"] = user_update.date_of_birth
        if user_update.gender:
            update_data["gender"] = user_update.gender
        
        db = get_db()
        await db.users.update_one(
            {"id": current_user["id"]},
            {"$set": update_data}
        )
        return {"message": "Profile updated successfully"}

    @staticmethod
    async def check_user_exists(email: str):
        """Check if a user exists with the given email address"""
        db = get_db()

        try:
            # Find user by email
            user = await db.users.find_one({"email": email})

            if user:
                return {
                    "exists": True,
                    "name": user.get("name", "User"),
                    "email": email
                }
            else:
                return {
                    "exists": False,
                    "name": "User",
                    "email": email
                }

        except Exception as e:
            logging.error(f"Error checking user existence: {e}")
            # Return False for security (don't reveal system errors)
            return {
                "exists": False,
                "name": "User",
                "email": email
            }
