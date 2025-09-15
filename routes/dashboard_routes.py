from fastapi import APIRouter, Depends, Query
from typing import Optional
from controllers.dashboard_controller import DashboardController
from models.user_models import UserRole
from utils.unified_auth import require_role_unified, get_current_user_or_superadmin

router = APIRouter()

@router.get("/stats")
async def get_dashboard_stats(
    branch_id: Optional[str] = Query(None, description="Filter by branch ID"),
    current_user: dict = Depends(get_current_user_or_superadmin)
):
    """Get comprehensive dashboard statistics"""
    return await DashboardController.get_dashboard_stats(current_user, branch_id)

@router.get("/recent-activities")
async def get_recent_activities(
    limit: int = Query(10, ge=1, le=50, description="Number of recent activities to return"),
    current_user: dict = Depends(get_current_user_or_superadmin)
):
    """Get recent activities for dashboard"""
    return await DashboardController.get_recent_activities(current_user, limit)
