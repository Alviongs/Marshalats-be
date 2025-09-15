from fastapi import APIRouter, Depends, Query
from typing import Optional

from controllers.branches_with_courses_controller import BranchesWithCoursesController
from utils.unified_auth import get_current_user_or_superadmin

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
