from fastapi import APIRouter, Depends, status
from typing import Optional
from controllers.location_controller import LocationController
from models.location_models import LocationCreate, LocationUpdate
from models.user_models import UserRole
from utils.auth import require_role, get_current_active_user
from utils.unified_auth import require_role_unified, get_current_user_or_superadmin

router = APIRouter()

@router.post("", status_code=status.HTTP_201_CREATED)
async def create_location(
    location_data: LocationCreate,
    current_user: dict = Depends(require_role_unified([UserRole.SUPER_ADMIN]))
):
    """Create a new location - accessible by Super Admin only"""
    return await LocationController.create_location(location_data, current_user)

@router.get("")
async def get_locations(
    active_only: bool = True,
    skip: int = 0,
    limit: int = 50,
    current_user: dict = Depends(get_current_user_or_superadmin)
):
    """Get locations with optional filtering - authenticated endpoint"""
    return await LocationController.get_locations(active_only, skip, limit, current_user)

@router.get("/public/with-branches")
async def get_locations_with_branches(
    active_only: bool = True,
    skip: int = 0,
    limit: int = 100
):
    """Get all locations with their associated branches - Public endpoint (no authentication required)"""
    return await LocationController.get_locations_with_branches(active_only, skip, limit)

@router.get("/public/details")
async def get_locations_with_details(
    location_id: Optional[str] = None,
    include_branches: bool = True,
    include_courses: bool = False,
    active_only: bool = True,
    skip: int = 0,
    limit: int = 50
):
    """Get location details with associated branches - Public endpoint (no authentication required)"""
    return await LocationController.get_locations_with_details(location_id, include_branches, include_courses, active_only, skip, limit)

@router.get("/public/states")
async def get_states(
    active_only: bool = True
):
    """Get unique states from locations - Public endpoint (no authentication required)"""
    return await LocationController.get_states(active_only)

@router.get("/{location_id}")
async def get_location(
    location_id: str,
    current_user: dict = Depends(get_current_user_or_superadmin)
):
    """Get single location by ID - authenticated endpoint"""
    return await LocationController.get_location(location_id, current_user)

@router.put("/{location_id}")
async def update_location(
    location_id: str,
    location_update: LocationUpdate,
    current_user: dict = Depends(require_role_unified([UserRole.SUPER_ADMIN]))
):
    """Update location - accessible by Super Admin only"""
    return await LocationController.update_location(location_id, location_update, current_user)

@router.delete("/{location_id}")
async def delete_location(
    location_id: str,
    current_user: dict = Depends(require_role_unified([UserRole.SUPER_ADMIN]))
):
    """Delete location - accessible by Super Admin only"""
    return await LocationController.delete_location(location_id, current_user)
