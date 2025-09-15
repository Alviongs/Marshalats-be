from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional
from enum import Enum
import uuid

class CourseChangeRequestStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"

class CourseChangeRequest(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    student_id: str
    branch_id: str
    current_enrollment_id: str
    new_course_id: str
    reason: str
    status: CourseChangeRequestStatus = CourseChangeRequestStatus.PENDING
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class CourseChangeRequestCreate(BaseModel):
    current_enrollment_id: str
    new_course_id: str
    reason: str

class CourseChangeRequestUpdate(BaseModel):
    status: CourseChangeRequestStatus
