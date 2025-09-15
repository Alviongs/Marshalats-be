from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from controllers.superadmin_controller import SuperAdminController
from controllers.coach_controller import CoachController
from models.superadmin_models import SuperAdminRegister, SuperAdminLogin, SuperAdminUpdate, SuperAdminForgotPassword, SuperAdminResetPassword
from models.coach_models import CoachCreate, CoachUpdate

router = APIRouter()
security = HTTPBearer()

async def get_current_superadmin(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Dependency to get current super admin from token"""
    return await SuperAdminController.get_current_superadmin(credentials.credentials)

@router.post("/register")
async def register_superadmin(admin_data: SuperAdminRegister):
    """Register a new super admin"""
    return await SuperAdminController.register_superadmin(admin_data)

@router.post("/login")
async def login_superadmin(login_data: SuperAdminLogin):
    """Login super admin and get JWT token"""
    return await SuperAdminController.login_superadmin(login_data)

@router.post("/forgot-password")
async def forgot_password(forgot_password_data: SuperAdminForgotPassword):
    """Initiate password reset process for superadmin"""
    return await SuperAdminController.forgot_password(forgot_password_data.email)

@router.post("/reset-password")
async def reset_password(reset_password_data: SuperAdminResetPassword):
    """Reset superadmin password using a token"""
    return await SuperAdminController.reset_password(reset_password_data.token, reset_password_data.new_password)

@router.get("/me")
async def get_my_profile(current_admin = Depends(get_current_superadmin)):
    """Get current super admin profile"""
    # Remove password hash from response
    admin_data = {k: v for k, v in current_admin.items() if k != "password_hash"}
    return {
        "status": "success",
        "data": admin_data
    }

@router.put("/me")
async def update_my_profile(
    update_data: SuperAdminUpdate,
    current_admin = Depends(get_current_superadmin)
):
    """Update current super admin profile"""
    try:
        # Convert Pydantic model to dict, excluding None values
        update_dict = update_data.dict(exclude_unset=True)

        updated_admin = await SuperAdminController.update_superadmin_profile(
            current_admin["id"],
            update_dict
        )

        # Remove password hash from response
        admin_data = {k: v for k, v in updated_admin.items() if k != "password_hash"}

        return {
            "status": "success",
            "message": "Profile updated successfully",
            "data": admin_data
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update profile: {str(e)}"
        )

@router.get("/verify-token")
async def verify_token(current_admin = Depends(get_current_superadmin)):
    """Verify if token is valid"""
    return {
        "status": "success",
        "message": "Token is valid",
        "data": {
            "id": current_admin["id"],
            "email": current_admin["email"],
            "full_name": current_admin["full_name"]
        }
    }

@router.post("/coaches")
async def create_coach_as_superadmin(
    coach_data: CoachCreate,
    request: Request,
    current_admin = Depends(get_current_superadmin)
):
    """Create new coach with nested structure (Super Admin only)"""
    # Convert current_admin to the format expected by CoachController
    admin_user = {
        "id": current_admin["id"],
        "full_name": current_admin["full_name"],
        "role": "super_admin"
    }
    
    return await CoachController.create_coach(coach_data, request, admin_user)

@router.get("/coaches")
async def get_coaches_as_superadmin(
    skip: int = 0,
    limit: int = 50,
    active_only: bool = True,
    area_of_expertise: str = None,
    current_admin = Depends(get_current_superadmin)
):
    """Get coaches with filtering (Super Admin only)"""
    return await CoachController.get_coaches(skip, limit, active_only, area_of_expertise)

@router.get("/coaches/{coach_id}")
async def get_coach_by_id_as_superadmin(
    coach_id: str,
    current_admin = Depends(get_current_superadmin)
):
    """Get coach by ID (Super Admin only)"""
    return await CoachController.get_coach_by_id(coach_id)

@router.put("/coaches/{coach_id}")
async def update_coach_as_superadmin(
    coach_id: str,
    coach_update: CoachUpdate,
    request: Request,
    current_admin = Depends(get_current_superadmin)
):
    """Update coach information (Super Admin only)"""
    admin_user = {
        "id": current_admin["id"],
        "full_name": current_admin["full_name"],
        "role": "super_admin"
    }
    
    return await CoachController.update_coach(coach_id, coach_update, request, admin_user)

@router.delete("/coaches/{coach_id}")
async def deactivate_coach_as_superadmin(
    coach_id: str,
    request: Request,
    current_admin = Depends(get_current_superadmin)
):
    """Deactivate coach (Super Admin only)"""
    admin_user = {
        "id": current_admin["id"],
        "full_name": current_admin["full_name"],
        "role": "super_admin"
    }
    
    return await CoachController.deactivate_coach(coach_id, request, admin_user)

@router.get("/coaches/stats/overview")
async def get_coach_stats_as_superadmin(
    current_admin = Depends(get_current_superadmin)
):
    """Get coach statistics (Super Admin only)"""
    return await CoachController.get_coach_stats()
