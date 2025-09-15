from fastapi import APIRouter, Depends, status
from controllers.event_controller import EventController
from models.event_models import EventCreate
from models.user_models import UserRole
from utils.auth import require_role, get_current_active_user
from utils.unified_auth import require_role_unified, get_current_user_or_superadmin

router = APIRouter()

@router.post("", status_code=status.HTTP_201_CREATED)
async def create_event(
    event_data: EventCreate,
    current_user: dict = Depends(require_role_unified([UserRole.SUPER_ADMIN, UserRole.COACH_ADMIN]))
):
    return await EventController.create_event(event_data, current_user)

@router.get("")
async def get_events(
    branch_id: str,
    current_user: dict = Depends(get_current_user_or_superadmin)
):
    return await EventController.get_events(branch_id, current_user)

@router.put("/{event_id}")
async def update_event(
    event_id: str,
    event_data: EventCreate,
    current_user: dict = Depends(require_role([UserRole.SUPER_ADMIN, UserRole.COACH_ADMIN]))
):
    return await EventController.update_event(event_id, event_data, current_user)

@router.delete("/{event_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_event(
    event_id: str,
    current_user: dict = Depends(require_role([UserRole.SUPER_ADMIN, UserRole.COACH_ADMIN]))
):
    return await EventController.delete_event(event_id, current_user)
