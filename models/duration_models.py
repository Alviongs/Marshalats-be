from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional
import uuid

class Duration(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str  # e.g., "3 Months", "6 Months", "1 Year"
    code: str  # e.g., "3M", "6M", "1Y"
    duration_months: int  # Duration in months
    duration_days: Optional[int] = None  # Optional duration in days for more precision
    description: Optional[str] = None
    is_active: bool = True
    display_order: int = 0  # For sorting durations
    pricing_multiplier: float = 1.0  # Multiplier for base course pricing
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class DurationCreate(BaseModel):
    name: str
    code: str
    duration_months: int
    duration_days: Optional[int] = None
    description: Optional[str] = None
    is_active: bool = True
    display_order: int = 0
    pricing_multiplier: float = 1.0

class DurationUpdate(BaseModel):
    name: Optional[str] = None
    code: Optional[str] = None
    duration_months: Optional[int] = None
    duration_days: Optional[int] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None
    display_order: Optional[int] = None
    pricing_multiplier: Optional[float] = None

class DurationResponse(BaseModel):
    id: str
    name: str
    code: str
    duration_months: int
    duration_days: Optional[int] = None
    description: Optional[str] = None
    is_active: bool
    display_order: int
    pricing_multiplier: float
    enrollment_count: Optional[int] = None  # Number of enrollments using this duration
    created_at: datetime
    updated_at: datetime
