from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional
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
