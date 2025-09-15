from fastapi import APIRouter, Depends, Request, Path
from typing import Optional
from controllers.user_controller import UserController
from models.user_models import UserCreate, UserUpdate, UserRole
from utils.auth import require_role
from utils.unified_auth import require_role_unified, get_current_user_or_superadmin

router = APIRouter()

@router.post("")
async def create_user(
    user_data: UserCreate,
    request: Request,
    current_user: dict = Depends(require_role_unified([UserRole.SUPER_ADMIN, UserRole.COACH_ADMIN]))
):
    return await UserController.create_user(user_data, request, current_user)

@router.get("")
async def get_users(
    role: Optional[UserRole] = None,
    branch_id: Optional[str] = None,
    skip: int = 0,
    limit: int = 50,
    current_user: dict = Depends(require_role_unified([UserRole.SUPER_ADMIN, UserRole.COACH_ADMIN, UserRole.COACH]))
):
    """Get users with filtering - accessible by Super Admin, Coach Admin, and Coach"""
    return await UserController.get_users(role, branch_id, skip, limit, current_user)

@router.get("/students/details")
async def get_student_details(
    current_user: dict = Depends(require_role_unified([UserRole.SUPER_ADMIN, UserRole.COACH_ADMIN, UserRole.COACH]))
):
    """Get detailed student information with course enrollment data (Authenticated endpoint)"""
    return await UserController.get_student_details(current_user)

@router.get("/{user_id}/enrollments")
async def get_user_enrollments(
    user_id: str,
    current_user: dict = Depends(require_role_unified([UserRole.SUPER_ADMIN, UserRole.COACH_ADMIN, UserRole.COACH]))
):
    """Get enrollment history for a specific student"""
    return await UserController.get_user_enrollments(user_id, current_user)

@router.get("/{user_id}/payments")
async def get_user_payments(
    user_id: str,
    current_user: dict = Depends(require_role_unified([UserRole.SUPER_ADMIN, UserRole.COACH_ADMIN, UserRole.COACH]))
):
    """Get payment history for a specific student"""
    return await UserController.get_user_payments(user_id, current_user)

@router.get("/{user_id}")
async def get_user_by_id(
    user_id: str = Path(..., description="User ID"),
    current_user: dict = Depends(get_current_user_or_superadmin)
):
    """Get single user by ID - accessible by Super Admin, Coach Admin, and Coach"""
    return await UserController.get_user(user_id, current_user)

@router.put("/{user_id}")
async def update_user(
    user_id: str,
    user_update: UserUpdate,
    request: Request,
    current_user: dict = Depends(require_role_unified([UserRole.SUPER_ADMIN, UserRole.COACH_ADMIN]))
):
    return await UserController.update_user(user_id, user_update, request, current_user)

@router.post("/{user_id}/force-password-reset")
async def force_password_reset(
    user_id: str,
    request: Request,
    current_user: dict = Depends(require_role_unified([UserRole.SUPER_ADMIN, UserRole.COACH_ADMIN]))
):
    return await UserController.force_password_reset(user_id, request, current_user)

@router.delete("/{user_id}")
async def delete_user(
    user_id: str,
    request: Request,
    current_user: dict = Depends(require_role_unified([UserRole.SUPER_ADMIN, UserRole.COACH_ADMIN]))
):
    """Permanently delete user - accessible by Super Admin and Coach Admin"""
    return await UserController.delete_user(user_id, request, current_user)

@router.patch("/{user_id}/deactivate")
async def deactivate_user(
    user_id: str,
    request: Request,
    current_user: dict = Depends(require_role_unified([UserRole.SUPER_ADMIN]))
):
    """Deactivate user (soft delete) - accessible by Super Admin only"""
    return await UserController.deactivate_user(user_id, request, current_user)
