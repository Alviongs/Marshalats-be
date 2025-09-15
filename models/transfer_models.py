from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional
from enum import Enum
import uuid

class TransferRequestStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"

class TransferRequest(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    student_id: str
    current_branch_id: str
    new_branch_id: str
    reason: str
    status: TransferRequestStatus = TransferRequestStatus.PENDING
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class TransferRequestCreate(BaseModel):
    new_branch_id: str
    reason: str

class TransferRequestUpdate(BaseModel):
    status: TransferRequestStatus
