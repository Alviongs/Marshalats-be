from fastapi import APIRouter, Depends, status, Query
from typing import Optional
from controllers.payment_controller import PaymentController
from models.student_models import StudentPaymentCreate
from models.payment_models import RegistrationPaymentCreate
from models.user_models import UserRole
from utils.auth import require_role
from utils.unified_auth import require_role_unified, get_current_user_or_superadmin

router = APIRouter()

@router.post("/students/payments", status_code=status.HTTP_201_CREATED)
async def student_process_payment(
    payment_data: StudentPaymentCreate,
    current_user: dict = Depends(require_role([UserRole.STUDENT]))
):
    return await PaymentController.student_process_payment(payment_data, current_user)

@router.post("/process-registration", status_code=status.HTTP_201_CREATED)
async def process_registration_payment(payment_data: RegistrationPaymentCreate):
    """Process payment for student registration (public endpoint)"""
    return await PaymentController.process_registration_payment(payment_data)

@router.get("/course-payment-info")
async def get_course_payment_info(
    course_id: str = Query(..., description="Course ID"),
    branch_id: str = Query(..., description="Branch ID"),
    duration: str = Query(..., description="Duration code")
):
    """Get payment information for a course (public endpoint)"""
    return await PaymentController.get_course_payment_info(course_id, branch_id, duration)

@router.get("/notifications")
async def get_payment_notifications(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    current_user: dict = Depends(require_role_unified([UserRole.SUPER_ADMIN]))
):
    """Get payment notifications for superadmin dashboard"""
    return await PaymentController.get_payment_notifications(skip, limit)

@router.put("/notifications/{notification_id}/read")
async def mark_notification_read(
    notification_id: str,
    current_user: dict = Depends(require_role_unified([UserRole.SUPER_ADMIN]))
):
    """Mark a payment notification as read"""
    return await PaymentController.mark_notification_read(notification_id)

@router.get("/stats")
async def get_payment_stats(
    current_user: dict = Depends(require_role_unified([UserRole.SUPER_ADMIN, UserRole.COACH_ADMIN, UserRole.BRANCH_MANAGER]))
):
    """Get payment statistics for dashboard"""
    return await PaymentController.get_payment_stats(current_user)

@router.get("")
async def get_payments(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    status: Optional[str] = Query(None),
    payment_type: Optional[str] = Query(None),
    current_user: dict = Depends(require_role_unified([UserRole.SUPER_ADMIN, UserRole.COACH_ADMIN, UserRole.BRANCH_MANAGER]))
):
    """Get payments with filtering"""
    return await PaymentController.get_payments(skip, limit, status, payment_type, current_user)
