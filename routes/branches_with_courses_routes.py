from fastapi import APIRouter, Depends, Query
from typing import Optional

from controllers.branches_with_courses_controller import BranchesWithCoursesController
from utils.unified_auth import get_current_user_or_superadmin, require_role_unified
from models.user_models import UserRole

router = APIRouter()

@router.get("/branches-with-courses")
async def get_branches_with_courses(
    branch_id: Optional[str] = Query(None, description="Filter by specific branch ID, or 'all' for all branches"),
    status: Optional[str] = Query(None, description="Filter by branch status ('active' or 'inactive')"),
    include_inactive: bool = Query(False, description="Include inactive branches when no status filter is applied"),
    current_user: dict = Depends(get_current_user_or_superadmin)
):
    """
    Get branches with their associated courses based on filtering criteria.
    
    **Query Parameters:**
    - `branch_id` (optional): Filter by specific branch ID, or "all" for all branches
    - `status` (optional): Filter by branch status ("active" or "inactive")
    - `include_inactive` (optional): Include inactive branches when no status filter is applied (default: false)
    
    **Authentication:** Requires Bearer token
    
    **Response Format:**
    ```json
    {
        "message": "Branches with courses retrieved successfully",
        "branches": [...],
        "total": 2,
        "summary": {
            "total_branches": 2,
            "total_courses": 5,
            "total_students": 123,
            "total_coaches": 7
        },
        "filters_applied": {
            "branch_id": "all",
            "status": "active",
            "include_inactive": false
        }
    }
    ```
    
    **Error Responses:**
    - 401: Missing or invalid authorization header
    - 404: Specific branch ID not found
    - 500: Internal server error
    """
    return await BranchesWithCoursesController.get_branches_with_courses(
        branch_id=branch_id,
        status=status,
        include_inactive=include_inactive,
        current_user=current_user
    )

@router.get("/branch-details/{branch_id}")
async def get_branch_details_with_courses_and_coaches(
    branch_id: str,
    current_user: dict = Depends(require_role_unified([UserRole.SUPER_ADMIN, UserRole.COACH_ADMIN, UserRole.BRANCH_MANAGER]))
):
    """
    Get detailed branch information including courses and coaches for branch manager dashboard.

    **Path Parameters:**
    - `branch_id`: The specific branch ID to get details for

    **Authentication:** Requires Bearer token with appropriate role

    **Access Control:**
    - Super Admin: Can access any branch
    - Coach Admin: Can access any branch
    - Branch Manager: Can only access branches they manage

    **Response Format:**
    ```json
    {
        "branch": {
            "id": "branch-uuid",
            "branch": {
                "name": "Branch Name",
                "address": {...},
                "phone": "+1234567890",
                "email": "branch@example.com",
                "operating_hours": {...}
            },
            "is_active": true,
            "created_at": "2024-01-01T00:00:00Z",
            "updated_at": "2024-01-01T00:00:00Z",
            "total_students": 150,
            "total_coaches": 8,
            "active_courses": 12,
            "monthly_revenue": 125000
        },
        "courses": [...],
        "coaches": [...],
        "statistics": {...}
    }
    ```

    **Error Responses:**
    - 401: Missing or invalid authorization header
    - 403: Insufficient permissions (branch managers can only access their branches)
    - 404: Branch not found
    - 500: Internal server error
    """
    return await BranchesWithCoursesController.get_branch_details_with_courses_and_coaches(
        branch_id=branch_id,
        current_user=current_user
    )
