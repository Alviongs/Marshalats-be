from fastapi import APIRouter, Depends, status
from typing import Optional
from controllers.request_controller import RequestController
from models.transfer_models import TransferRequestCreate, TransferRequestUpdate, TransferRequestStatus
from models.coursechange_models import CourseChangeRequestCreate, CourseChangeRequestUpdate, CourseChangeRequestStatus
from models.user_models import UserRole
from utils.auth import require_role

router = APIRouter()

# Transfer Requests
@router.post("/transfer", status_code=status.HTTP_201_CREATED)
async def create_transfer_request(
    request_data: TransferRequestCreate,
    current_user: dict = Depends(require_role([UserRole.STUDENT]))
):
    return await RequestController.create_transfer_request(request_data, current_user)

@router.get("/transfer")
async def get_transfer_requests(
    status: Optional[TransferRequestStatus] = None,
    current_user: dict = Depends(require_role([UserRole.SUPER_ADMIN, UserRole.COACH_ADMIN]))
):
    return await RequestController.get_transfer_requests(status, current_user)

@router.put("/transfer/{request_id}")
async def update_transfer_request(
    request_id: str,
    update_data: TransferRequestUpdate,
    current_user: dict = Depends(require_role([UserRole.SUPER_ADMIN, UserRole.COACH_ADMIN]))
):
    return await RequestController.update_transfer_request(request_id, update_data, current_user)

# Course Change Requests
@router.post("/course-change", status_code=status.HTTP_201_CREATED)
async def create_course_change_request(
    request_data: CourseChangeRequestCreate,
    current_user: dict = Depends(require_role([UserRole.STUDENT]))
):
    return await RequestController.create_course_change_request(request_data, current_user)

@router.get("/course-change")
async def get_course_change_requests(
    status: Optional[CourseChangeRequestStatus] = None,
    current_user: dict = Depends(require_role([UserRole.SUPER_ADMIN, UserRole.COACH_ADMIN]))
):
    return await RequestController.get_course_change_requests(status, current_user)

@router.put("/course-change/{request_id}")
async def update_course_change_request(
    request_id: str,
    update_data: CourseChangeRequestUpdate,
    current_user: dict = Depends(require_role([UserRole.SUPER_ADMIN, UserRole.COACH_ADMIN]))
):
    return await RequestController.update_course_change_request(request_id, update_data, current_user)
