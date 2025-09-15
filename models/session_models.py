from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional
from enum import Enum
import uuid

class SessionStatus(str, Enum):
    SCHEDULED = "scheduled"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    NO_SHOW = "no_show"

class PaymentStatus(str, Enum):
    PENDING = "pending"
    PAID = "paid"
    OVERDUE = "overdue"
    CANCELLED = "cancelled"

class SessionBooking(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    student_id: str
    course_id: str
    branch_id: str
    coach_id: str
    session_date: datetime
    duration_minutes: int = 60
    fee: float = 250.0
    status: SessionStatus = SessionStatus.SCHEDULED
    payment_status: PaymentStatus = PaymentStatus.PENDING
    notes: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

class SessionBookingCreate(BaseModel):
    course_id: str
    branch_id: str
    coach_id: str
    session_date: datetime
    duration_minutes: int = 60
    notes: Optional[str] = None
