from pydantic import BaseModel, Field
from datetime import datetime
import uuid

class Event(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    branch_id: str
    title: str
    description: str
    start_time: datetime
    end_time: datetime
    created_by: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

class EventCreate(BaseModel):
    title: str
    description: str
    start_time: datetime
    end_time: datetime
