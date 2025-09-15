from fastapi import HTTPException, status
from datetime import datetime, timedelta
from passlib.context import CryptContext
import jwt
import os
from typing import Optional
from dotenv import load_dotenv
from pathlib import Path

from models.superadmin_models import SuperAdmin, SuperAdminRegister, SuperAdminLogin, SuperAdminResponse
from utils.database import get_db
from utils.helpers import serialize_doc
from utils.email_service import send_password_reset_email

# Load environment variables
ROOT_DIR = Path(__file__).parent.parent
load_dotenv(ROOT_DIR / '.env')

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT settings
SECRET_KEY = os.getenv("SECRET_KEY", "student_management_secret_key_2025")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_HOURS = 24

class SuperAdminController:
    @staticmethod
    def hash_password(password: str) -> str:
        """Hash a password"""
        return pwd_context.hash(password)
    
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash"""
        return pwd_context.verify(plain_password, hashed_password)
    
    @staticmethod
    def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
        """Create JWT access token"""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(hours=ACCESS_TOKEN_EXPIRE_HOURS)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt

    @staticmethod
    async def register_superadmin(admin_data: SuperAdminRegister):
        """Register a new super admin"""
        db = get_db()
        
        # Check if email already exists
        existing_admin = await db.superadmins.find_one({"email": admin_data.email})
        if existing_admin:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already exists"
            )
        
        # Hash password
        hashed_password = SuperAdminController.hash_password(admin_data.password)
        
        # Create super admin
        admin = SuperAdmin(
            full_name=admin_data.full_name,
            email=admin_data.email,
            phone=admin_data.phone,
            password_hash=hashed_password
        )
        
        # Save to database
        admin_dict = admin.dict()
        await db.superadmins.insert_one(admin_dict)
        
        # Return response without password hash
        admin_response = SuperAdminResponse(
            id=admin.id,
            full_name=admin.full_name,
            email=admin.email,
            phone=admin.phone,
            is_active=admin.is_active,
            created_at=admin.created_at,
            updated_at=admin.updated_at
        )
        
        return {
            "status": "success",
            "message": "Super admin registered successfully",
            "data": admin_response.dict()
        }

    @staticmethod
    async def login_superadmin(login_data: SuperAdminLogin):
        """Login super admin and return JWT token"""
        db = get_db()
        
        # Find super admin by email
        admin = await db.superadmins.find_one({"email": login_data.email})
        if not admin:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
        
        # Verify password
        if not SuperAdminController.verify_password(login_data.password, admin["password_hash"]):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
        
        # Check if admin is active
        if not admin.get("is_active", True):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Account is disabled"
            )
        
        # Create access token
        access_token = SuperAdminController.create_access_token(
            data={"sub": admin["id"], "email": admin["email"], "role": "superadmin"}
        )
        
        return {
            "status": "success",
            "message": "Login successful",
            "data": {
                "id": admin["id"],
                "full_name": admin["full_name"],
                "email": admin["email"],
                "phone": admin["phone"],
                "token": access_token,
                "token_type": "bearer",
                "expires_in": ACCESS_TOKEN_EXPIRE_HOURS * 3600  # seconds
            }
        }

    @staticmethod
    async def get_current_superadmin(token: str):
        """Get current super admin from token"""
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            admin_id = payload.get("sub")
            if admin_id is None:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid authentication credentials"
                )
        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has expired"
            )
        except jwt.JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials"
            )
        
        db = get_db()
        admin = await db.superadmins.find_one({"id": admin_id})
        if admin is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Super admin not found"
            )
        
        return serialize_doc(admin)

    @staticmethod
    async def update_superadmin_profile(admin_id: str, update_data: dict):
        """Update super admin profile"""
        from utils.database import get_db
        from utils.helpers import serialize_doc
        from datetime import datetime

        db = get_db()

        # Check if admin exists
        admin = await db.superadmins.find_one({"id": admin_id})
        if admin is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Super admin not found"
            )

        # Check if email is being updated and if it already exists
        if "email" in update_data and update_data["email"] != admin["email"]:
            existing_admin = await db.superadmins.find_one({
                "email": update_data["email"],
                "id": {"$ne": admin_id}
            })
            if existing_admin:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email already exists"
                )

        # Check if phone is being updated and if it already exists
        if "phone" in update_data and update_data["phone"] != admin["phone"]:
            existing_admin = await db.superadmins.find_one({
                "phone": update_data["phone"],
                "id": {"$ne": admin_id}
            })
            if existing_admin:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Phone number already exists"
                )

        # Prepare update data
        update_fields = {}
        for field, value in update_data.items():
            if value is not None:
                update_fields[field] = value

        if update_fields:
            update_fields["updated_at"] = datetime.utcnow()

            # Update the admin
            result = await db.superadmins.update_one(
                {"id": admin_id},
                {"$set": update_fields}
            )

            if result.modified_count == 0:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="No changes were made"
                )

        # Get updated admin data
        updated_admin = await db.superadmins.find_one({"id": admin_id})
        return serialize_doc(updated_admin)

    @staticmethod
    async def forgot_password(email: str):
        """Initiate password reset process for superadmin"""
        db = get_db()
        admin = await db.superadmins.find_one({"email": email})

        if not admin:
            # Don't reveal that the admin does not exist
            return {"message": "If a superadmin account with that email exists, a password reset link has been sent."}

        # Generate a short-lived token for password reset (same as student implementation)
        reset_token = SuperAdminController.create_access_token(
            data={"sub": admin["id"], "scope": "password_reset"},
            expires_delta=timedelta(minutes=15)
        )

        # Send password reset email with superadmin branding using webhook (same as /api/email/send-webhook-email)
        admin_name = admin.get("full_name", "Superadmin")
        from utils.email_service import send_password_reset_email_webhook
        email_sent = await send_password_reset_email_webhook(email, reset_token, admin_name, "superadmin")

        # Log the password reset attempt (same as student implementation)
        import logging
        logging.info(f"Password reset requested for superadmin {email}. Email sent: {email_sent}")

        # Also send SMS as backup (if phone number exists) - same as student implementation
        if admin.get("phone"):
            from utils.helpers import send_sms
            sms_message = f"Superadmin password reset requested for your account. Check your email ({email}) for reset instructions. If you didn't request this, please ignore."
            await send_sms(admin["phone"], sms_message)

        response = {"message": "If a superadmin account with that email exists, a password reset link has been sent."}

        # Include token in response for testing purposes (same as student implementation)
        if os.environ.get("TESTING") == "True":
            response["reset_token"] = reset_token
            response["email_sent"] = email_sent

        return response

    @staticmethod
    async def reset_password(token: str, new_password: str):
        """Reset superadmin password using a token"""
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            if payload.get("scope") != "password_reset":
                raise HTTPException(status_code=401, detail="Invalid token scope")

            admin_id = payload.get("sub")
            if not admin_id:
                raise HTTPException(status_code=401, detail="Invalid token")

        except jwt.PyJWTError:
            raise HTTPException(status_code=401, detail="Invalid or expired token")

        new_hashed_password = SuperAdminController.hash_password(new_password)
        db = get_db()
        result = await db.superadmins.update_one(
            {"id": admin_id},
            {"$set": {"password": new_hashed_password, "updated_at": datetime.utcnow()}}
        )

        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Superadmin not found")

        return {"message": "Password has been reset successfully"}
