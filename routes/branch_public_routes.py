from fastapi import APIRouter
from typing import Optional
from controllers.location_controller import LocationController
from controllers.branch_controller import BranchController

router = APIRouter()

@router.get("/public/by-location/{location_id}")
async def get_branches_by_location(
    location_id: str,
    include_courses: bool = True,
    include_timings: bool = True,
    active_only: bool = True,
    skip: int = 0,
    limit: int = 50
):
    """Get branches filtered by location - Public endpoint (no authentication required)"""
    return await LocationController.get_branches_by_location(location_id, include_courses, include_timings, active_only, skip, limit)

@router.get("/public/all")
async def get_all_branches_public(
    active_only: bool = True,
    skip: int = 0,
    limit: int = 100
):
    """Get all branches - Public endpoint (no authentication required)"""
    return await BranchController.get_branches_public(active_only, skip, limit)
