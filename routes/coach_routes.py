from fastapi import APIRouter, Depends, Request, Query
from typing import Optional

from controllers.coach_controller import CoachController
from models.coach_models import CoachCreate, CoachUpdate, CoachLogin, CoachForgotPassword, CoachResetPassword
from models.user_models import UserRole
from utils.unified_auth import require_role_unified

router = APIRouter()

@router.post("/login")
async def coach_login(login_data: CoachLogin):
    """Coach login endpoint"""
    return await CoachController.login_coach(login_data)

@router.post("/forgot-password")
async def forgot_password(forgot_password_data: CoachForgotPassword):
    """Initiate password reset process for coach"""
    return await CoachController.forgot_password(forgot_password_data.email)

@router.post("/reset-password")
async def reset_password(reset_password_data: CoachResetPassword):
    """Reset coach password using a token"""
    return await CoachController.reset_password(reset_password_data.token, reset_password_data.new_password)



@router.post("")
async def create_coach(
    coach_data: CoachCreate,
    request: Request,
    current_user: dict = Depends(require_role_unified([UserRole.SUPER_ADMIN, UserRole.COACH_ADMIN, UserRole.BRANCH_MANAGER]))
):
    """Create new coach with nested structure"""
    return await CoachController.create_coach(coach_data, request, current_user)

@router.get("")
async def get_coaches(
    skip: int = Query(0, ge=0, description="Number of coaches to skip"),
    limit: int = Query(50, ge=1, le=100, description="Number of coaches to return"),
    active_only: bool = Query(True, description="Filter only active coaches"),
    area_of_expertise: Optional[str] = Query(None, description="Filter by area of expertise"),
    current_user: dict = Depends(require_role_unified([UserRole.SUPER_ADMIN, UserRole.COACH_ADMIN, UserRole.COACH, UserRole.BRANCH_MANAGER]))
):
    """Get coaches with filtering options"""
    return await CoachController.get_coaches(skip, limit, active_only, area_of_expertise, current_user)

@router.get("/me")
async def get_my_profile(
    current_user: dict = Depends(require_role_unified([UserRole.COACH]))
):
    """Get current coach's profile"""
    return await CoachController.get_coach_by_id(current_user["id"], current_user)

@router.put("/me")
async def update_my_profile(
    coach_update: CoachUpdate,
    request: Request,
    current_user: dict = Depends(require_role_unified([UserRole.COACH]))
):
    """Update current coach's profile"""
    return await CoachController.update_coach_profile(current_user["id"], coach_update, request, current_user)

@router.get("/{coach_id}")
async def get_coach_by_id(
    coach_id: str,
    current_user: dict = Depends(require_role_unified([UserRole.SUPER_ADMIN, UserRole.COACH_ADMIN, UserRole.COACH, UserRole.BRANCH_MANAGER]))
):
    """Get coach by ID - accessible by Super Admin, Coach Admin, Coach, and Branch Manager"""
    return await CoachController.get_coach_by_id(coach_id, current_user)

@router.put("/{coach_id}")
async def update_coach(
    coach_id: str,
    coach_update: CoachUpdate,
    request: Request,
    current_user: dict = Depends(require_role_unified([UserRole.SUPER_ADMIN, UserRole.COACH_ADMIN]))
):
    """Update coach information"""
    return await CoachController.update_coach(coach_id, coach_update, request, current_user)

@router.delete("/{coach_id}")
async def deactivate_coach(
    coach_id: str,
    request: Request,
    current_user: dict = Depends(require_role_unified([UserRole.SUPER_ADMIN, UserRole.BRANCH_MANAGER]))
):
    """Deactivate coach (Super Admin and Branch Manager)"""
    return await CoachController.deactivate_coach(coach_id, request, current_user)

@router.get("/{coach_id}/courses")
async def get_coach_courses(
    coach_id: str,
    current_user: dict = Depends(require_role_unified([UserRole.SUPER_ADMIN, UserRole.COACH_ADMIN, UserRole.COACH, UserRole.BRANCH_MANAGER]))
):
    """Get courses assigned to a specific coach"""
    return await CoachController.get_coach_courses(coach_id, current_user)

@router.get("/{coach_id}/students")
async def get_coach_students(
    coach_id: str,
    current_user: dict = Depends(require_role_unified([UserRole.SUPER_ADMIN, UserRole.COACH_ADMIN, UserRole.COACH, UserRole.BRANCH_MANAGER]))
):
    """Get students enrolled in courses taught by a specific coach"""
    return await CoachController.get_coach_students(coach_id, current_user)

@router.post("/{coach_id}/send-credentials")
async def send_coach_credentials(
    coach_id: str,
    request: Request,
    current_user: dict = Depends(require_role_unified([UserRole.SUPER_ADMIN, UserRole.COACH_ADMIN]))
):
    """Send login credentials to coach via email"""
    return await CoachController.send_credentials_email(coach_id, request, current_user)

@router.get("/stats/overview")
async def get_coach_stats(
    current_user: dict = Depends(require_role_unified([UserRole.SUPER_ADMIN, UserRole.COACH_ADMIN]))
):
    """Get coach statistics and analytics"""
    return await CoachController.get_coach_stats()
