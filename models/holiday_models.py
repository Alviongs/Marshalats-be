from pydantic import BaseModel, Field
from datetime import datetime, date
import uuid

class Holiday(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    branch_id: str
    date: date
    description: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

class HolidayCreate(BaseModel):
    date: date
    description: str
