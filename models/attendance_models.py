from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List
import uuid
from enum import Enum

class AttendanceMethod(str, Enum):
    QR_CODE = "qr_code"
    BIOMETRIC = "biometric"
    MANUAL = "manual"

class Attendance(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    student_id: str
    course_id: str
    branch_id: str
    attendance_date: datetime
    check_in_time: Optional[datetime] = None
    check_out_time: Optional[datetime] = None
    method: AttendanceMethod
    qr_code_used: Optional[str] = None
    marked_by: Optional[str] = None
    is_present: bool = True
    status: Optional[str] = None  # Store the original status (present, absent, late)
    notes: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

class AttendanceCreate(BaseModel):
    student_id: str
    course_id: str
    branch_id: str
    attendance_date: datetime
    method: AttendanceMethod
    qr_code_used: Optional[str] = None
    notes: Optional[str] = None

class BiometricAttendance(BaseModel):
    device_id: str
    biometric_id: str
    timestamp: datetime

# New models for comprehensive attendance management
class CoachAttendance(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    coach_id: str
    branch_id: str
    attendance_date: datetime
    check_in_time: Optional[datetime] = None
    check_out_time: Optional[datetime] = None
    method: AttendanceMethod
    marked_by: Optional[str] = None
    is_present: bool = True
    notes: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

class CoachAttendanceCreate(BaseModel):
    coach_id: str
    branch_id: str
    attendance_date: datetime
    method: AttendanceMethod
    is_present: bool = True
    notes: Optional[str] = None

class BranchManagerAttendance(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    branch_manager_id: str
    branch_id: str
    attendance_date: datetime
    check_in_time: Optional[datetime] = None
    check_out_time: Optional[datetime] = None
    method: AttendanceMethod
    marked_by: Optional[str] = None
    is_present: bool = True
    notes: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

class BranchManagerAttendanceCreate(BaseModel):
    branch_manager_id: str
    branch_id: str
    attendance_date: datetime
    method: AttendanceMethod
    is_present: bool = True
    notes: Optional[str] = None

class AttendanceStatus(str, Enum):
    PRESENT = "present"
    ABSENT = "absent"
    LATE = "late"

class AttendanceMarkRequest(BaseModel):
    user_id: str
    user_type: str  # "student", "coach", "branch_manager"
    course_id: Optional[str] = None
    branch_id: str
    attendance_date: datetime
    status: AttendanceStatus
    check_in_time: Optional[datetime] = None
    check_out_time: Optional[datetime] = None
    notes: Optional[str] = None

# Bulk attendance classes temporarily removed to fix import issues
# class BulkAttendanceCreate(BaseModel):
#     attendance_records: List["AttendanceCreate"]
#     attendance_date: datetime
#     method: AttendanceMethod = AttendanceMethod.MANUAL

# class BulkCoachAttendanceCreate(BaseModel):
#     attendance_records: List["CoachAttendanceCreate"]
#     attendance_date: datetime
#     method: AttendanceMethod = AttendanceMethod.MANUAL
