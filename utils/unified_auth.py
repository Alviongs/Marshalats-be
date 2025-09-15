from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import List
import jwt
import os
from dotenv import load_dotenv
from pathlib import Path

from models.user_models import UserRole
from utils.database import get_db
from utils.helpers import serialize_doc

# Load environment variables
ROOT_DIR = Path(__file__).parent.parent
load_dotenv(ROOT_DIR / '.env')

security = HTTPBearer()
# Use the same SECRET_KEY as the main server
SECRET_KEY = os.environ.get('SECRET_KEY', 'student_management_secret_key_2025')
ALGORITHM = "HS256"

# Debug: Print the SECRET_KEY being used (first 20 chars only for security)
print(f"🔑 unified_auth.py using SECRET_KEY: {SECRET_KEY[:20]}...")

async def get_current_user_or_superadmin(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """
    Unified authentication that handles regular users, superadmins, and coaches
    """
    db = get_db()
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        user_role: str = payload.get("role")

        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid authentication credentials")

        # Check if it's a superadmin token
        if user_role == "superadmin":
            user = await db.superadmins.find_one({"id": user_id})
            if user is None:
                raise HTTPException(status_code=401, detail="Super admin not found")
            # Convert superadmin to user-like format for role checking
            user_data = serialize_doc(user)
            user_data["role"] = "super_admin"  # Convert to UserRole format
            return user_data
        
        # Check if it's a coach token
        if user_role == "coach":
            coach = await db.coaches.find_one({"id": user_id})
            if coach is None:
                raise HTTPException(status_code=401, detail="Coach not found")
            # Convert coach to user-like format for role checking
            coach_data = serialize_doc(coach)
            coach_data["role"] = "coach"  # Set role for UserRole enum
            return coach_data

        # Regular user token (or token without role field)
        user = await db.users.find_one({"id": user_id})
        if user is None:
            raise HTTPException(status_code=401, detail="User not found")

        return serialize_doc(user)

    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid authentication credentials")

def require_role_unified(allowed_roles: List[UserRole]):
    """
    Role checker that works with both regular users and superadmins
    """
    async def role_checker(current_user: dict = Depends(get_current_user_or_superadmin)):
        if not current_user.get("is_active", True):
            raise HTTPException(status_code=400, detail="Inactive user")

        user_role = current_user["role"]

        # Convert super_admin to SUPER_ADMIN enum for comparison
        if user_role == "super_admin":
            if UserRole.SUPER_ADMIN not in allowed_roles:
                raise HTTPException(status_code=403, detail="Insufficient permissions")
        else:
            if user_role not in [role.value for role in allowed_roles]:
                raise HTTPException(status_code=403, detail="Insufficient permissions")

        return current_user
    return role_checker
