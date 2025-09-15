from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional
import uuid

class CoachRating(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    student_id: str
    coach_id: str
    branch_id: str
    rating: int
    review: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

class CoachRatingCreate(BaseModel):
    coach_id: str
    rating: int
    review: Optional[str] = None
