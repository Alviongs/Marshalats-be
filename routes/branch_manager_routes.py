from fastapi import APIRouter, Depends, Request, Query
from typing import Optional

from controllers.branch_manager_controller import BranchManagerController
from models.branch_manager_models import (
    BranchManagerCreate, BranchManagerUpdate, BranchManagerLogin, 
    BranchManagerForgotPassword, BranchManagerResetPassword
)
from models.user_models import UserRole
from utils.unified_auth import require_role_unified

router = APIRouter()

@router.post("/login")
async def branch_manager_login(login_data: BranchManagerLogin):
    """Branch manager login endpoint"""
    # TODO: Implement login functionality similar to coach login
    # For now, return a placeholder response
    from fastapi import HTTPException
    raise HTTPException(status_code=501, detail="Branch manager login not yet implemented")

@router.post("/forgot-password")
async def forgot_password(forgot_password_data: BranchManagerForgotPassword):
    """Initiate password reset process for branch manager"""
    # TODO: Implement forgot password functionality similar to coach
    from fastapi import HTTPException
    raise HTTPException(status_code=501, detail="Branch manager forgot password not yet implemented")

@router.post("/reset-password")
async def reset_password(reset_password_data: BranchManagerResetPassword):
    """Reset branch manager password using a token"""
    # TODO: Implement reset password functionality similar to coach
    from fastapi import HTTPException
    raise HTTPException(status_code=501, detail="Branch manager reset password not yet implemented")

@router.get("/me")
async def get_branch_manager_profile(
    current_user: dict = Depends(require_role_unified([UserRole.BRANCH_MANAGER]))
):
    """Get current branch manager's profile"""
    # Remove sensitive information
    manager_profile = {k: v for k, v in current_user.items() if k not in ["password_hash", "password"]}
    return {
        "branch_manager": manager_profile
    }

@router.post("")
async def create_branch_manager(
    manager_data: BranchManagerCreate,
    request: Request,
    current_user: dict = Depends(require_role_unified([UserRole.SUPER_ADMIN]))
):
    """Create new branch manager with nested structure"""
    return await BranchManagerController.create_branch_manager(manager_data, request, current_user)

@router.get("")
async def get_branch_managers(
    skip: int = Query(0, ge=0, description="Number of branch managers to skip"),
    limit: int = Query(50, ge=1, le=100, description="Number of branch managers to return"),
    active_only: bool = Query(True, description="Filter only active branch managers"),
    current_user: dict = Depends(require_role_unified([UserRole.SUPER_ADMIN]))
):
    """Get list of branch managers with pagination"""
    return await BranchManagerController.get_branch_managers(skip, limit, active_only, current_user)

@router.get("/{manager_id}")
async def get_branch_manager(
    manager_id: str,
    current_user: dict = Depends(require_role_unified([UserRole.SUPER_ADMIN, UserRole.BRANCH_MANAGER]))
):
    """Get specific branch manager by ID"""
    return await BranchManagerController.get_branch_manager(manager_id, current_user)

@router.put("/{manager_id}")
async def update_branch_manager(
    manager_id: str,
    manager_data: BranchManagerUpdate,
    request: Request,
    current_user: dict = Depends(require_role_unified([UserRole.SUPER_ADMIN]))
):
    """Update existing branch manager"""
    return await BranchManagerController.update_branch_manager(manager_id, manager_data, request, current_user)

@router.delete("/{manager_id}")
async def delete_branch_manager(
    manager_id: str,
    request: Request,
    current_user: dict = Depends(require_role_unified([UserRole.SUPER_ADMIN]))
):
    """Delete branch manager"""
    return await BranchManagerController.delete_branch_manager(manager_id, request, current_user)

@router.post("/{manager_id}/send-credentials")
async def send_branch_manager_credentials(
    manager_id: str,
    request: Request,
    current_user: dict = Depends(require_role_unified([UserRole.SUPER_ADMIN]))
):
    """Send login credentials to branch manager via email"""
    return await BranchManagerController.send_credentials_email(manager_id, request, current_user)
