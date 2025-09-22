from fastapi import APIRouter, Depends, Query
from typing import Optional
from controllers.dashboard_controller import DashboardController
from models.user_models import UserRole
from utils.unified_auth import require_role_unified, get_current_user_or_superadmin

router = APIRouter()

@router.get("/stats")
async def get_dashboard_stats(
    branch_id: Optional[str] = Query(None, description="Filter by branch ID"),
    current_user: dict = Depends(require_role_unified([UserRole.SUPER_ADMIN, UserRole.COACH_ADMIN, UserRole.BRANCH_MANAGER]))
):
    """Get comprehensive dashboard statistics - accessible by Super Admin, Coach Admin, and Branch Manager"""
    return await DashboardController.get_dashboard_stats(current_user, branch_id)

@router.get("/recent-activities")
async def get_recent_activities(
    limit: int = Query(10, ge=1, le=50, description="Number of recent activities to return"),
    current_user: dict = Depends(require_role_unified([UserRole.SUPER_ADMIN, UserRole.COACH_ADMIN, UserRole.BRANCH_MANAGER]))
):
    """Get recent activities for dashboard - accessible by Super Admin, Coach Admin, and Branch Manager"""
    return await DashboardController.get_recent_activities(current_user, limit)
