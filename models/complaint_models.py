from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, Dict, Any
from enum import Enum
import uuid

class ComplaintStatus(str, Enum):
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    CLOSED = "closed"

class Complaint(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    student_id: str
    branch_id: str
    subject: str
    description: str
    category: str
    coach_id: Optional[str] = None
    status: ComplaintStatus = ComplaintStatus.OPEN
    priority: str = "medium"
    assigned_to: Optional[str] = None
    resolution: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class ComplaintCreate(BaseModel):
    subject: str
    description: str
    category: str
    coach_id: Optional[str] = None
    priority: str = "medium"

class ComplaintUpdate(BaseModel):
    status: Optional[ComplaintStatus] = None
    assigned_to: Optional[str] = None
    resolution: Optional[str] = None
    priority: Optional[str] = None
