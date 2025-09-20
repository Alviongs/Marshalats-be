from fastapi import APIRouter, Depends, Query
from typing import Optional
from datetime import datetime
from controllers.attendance_controller import AttendanceController
from models.attendance_models import AttendanceCreate, BiometricAttendance
from models.user_models import UserRole
from utils.unified_auth import require_role_unified, get_current_user_or_superadmin

router = APIRouter()

@router.get("/reports")
async def get_attendance_reports(
    student_id: Optional[str] = Query(None),
    coach_id: Optional[str] = Query(None),
    course_id: Optional[str] = Query(None),
    branch_id: Optional[str] = Query(None),
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    current_user: dict = Depends(require_role_unified([UserRole.SUPER_ADMIN, UserRole.COACH_ADMIN, UserRole.COACH, UserRole.BRANCH_MANAGER]))
):
    """Get attendance reports with filtering"""
    return await AttendanceController.get_attendance_reports(
        student_id, coach_id, course_id, branch_id, start_date, end_date, current_user
    )

@router.get("/students")
async def get_student_attendance(
    branch_id: Optional[str] = Query(None),
    course_id: Optional[str] = Query(None),
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    current_user: dict = Depends(require_role_unified([UserRole.SUPER_ADMIN, UserRole.COACH_ADMIN, UserRole.COACH, UserRole.BRANCH_MANAGER]))
):
    """Get student attendance data"""
    return await AttendanceController.get_student_attendance(
        branch_id, course_id, start_date, end_date, current_user
    )

@router.get("/coaches")
async def get_coach_attendance(
    branch_id: Optional[str] = Query(None),
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    current_user: dict = Depends(require_role_unified([UserRole.SUPER_ADMIN, UserRole.COACH_ADMIN, UserRole.BRANCH_MANAGER]))
):
    """Get coach attendance data"""
    return await AttendanceController.get_coach_attendance(
        branch_id, start_date, end_date, current_user
    )

@router.get("/stats")
async def get_attendance_stats(
    branch_id: Optional[str] = Query(None),
    current_user: dict = Depends(require_role_unified([UserRole.SUPER_ADMIN, UserRole.COACH_ADMIN, UserRole.BRANCH_MANAGER]))
):
    """Get attendance statistics"""
    return await AttendanceController.get_attendance_stats(branch_id, current_user)

@router.post("/manual")
async def mark_manual_attendance(
    attendance_data: AttendanceCreate,
    current_user: dict = Depends(require_role_unified([UserRole.SUPER_ADMIN, UserRole.COACH_ADMIN, UserRole.COACH]))
):
    """Manually mark attendance"""
    return await AttendanceController.mark_manual_attendance(attendance_data, current_user)

@router.post("/biometric")
async def biometric_attendance(
    attendance_data: BiometricAttendance
):
    """Record attendance from biometric device"""
    return await AttendanceController.biometric_attendance(attendance_data)

@router.get("/export")
async def export_attendance_reports(
    student_id: Optional[str] = Query(None),
    coach_id: Optional[str] = Query(None),
    course_id: Optional[str] = Query(None),
    branch_id: Optional[str] = Query(None),
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    format: str = Query("csv", regex="^(csv|excel)$"),
    current_user: dict = Depends(require_role_unified([UserRole.SUPER_ADMIN, UserRole.COACH_ADMIN, UserRole.BRANCH_MANAGER]))
):
    """Export attendance reports"""
    return await AttendanceController.export_attendance_reports(
        student_id, coach_id, course_id, branch_id, start_date, end_date, format, current_user
    )
