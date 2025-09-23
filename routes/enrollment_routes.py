from fastapi import APIRouter, Depends, status
from typing import Optional
from controllers.enrollment_controller import EnrollmentController
from models.enrollment_models import EnrollmentCreate
from models.student_models import StudentEnrollmentCreate
from models.user_models import UserRole
from utils.auth import require_role, get_current_active_user
from utils.unified_auth import require_role_unified

router = APIRouter()

@router.post("")
async def create_enrollment(
    enrollment_data: EnrollmentCreate,
    current_user: dict = Depends(require_role_unified([UserRole.SUPER_ADMIN, UserRole.COACH_ADMIN, UserRole.BRANCH_MANAGER, UserRole.COACH]))
):
    return await EnrollmentController.create_enrollment(enrollment_data, current_user)

@router.get("")
async def get_enrollments(
    student_id: Optional[str] = None,
    course_id: Optional[str] = None,
    branch_id: Optional[str] = None,
    skip: int = 0,
    limit: int = 50,
    current_user: dict = Depends(get_current_active_user)
):
    return await EnrollmentController.get_enrollments(student_id, course_id, branch_id, skip, limit, current_user)

@router.get("/students/{student_id}/courses")
async def get_student_courses(
    student_id: str,
    current_user: dict = Depends(get_current_active_user)
):
    return await EnrollmentController.get_student_courses(student_id, current_user)

@router.post("/students/enroll", status_code=status.HTTP_201_CREATED)
async def student_enroll_in_course(
    enrollment_data: StudentEnrollmentCreate,
    current_user: dict = Depends(require_role([UserRole.STUDENT]))
):
    return await EnrollmentController.student_enroll_in_course(enrollment_data, current_user)

@router.get("/students/{student_id}")
async def get_student_enrollments(
    student_id: str,
    active_only: bool = True,
    current_user: dict = Depends(require_role_unified([UserRole.SUPER_ADMIN, UserRole.COACH_ADMIN, UserRole.BRANCH_MANAGER, UserRole.STUDENT]))
):
    """Get all enrollments for a specific student - Students can only view their own enrollments"""
    return await EnrollmentController.get_student_enrollments(student_id, current_user, active_only)
