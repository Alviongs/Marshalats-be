from pydantic import BaseModel, Field, EmailStr
from datetime import datetime, date
from typing import Optional, Dict, List
import uuid

class Address(BaseModel):
    line1: str
    area: str
    city: str
    state: str
    pincode: str
    country: str

class BranchInfo(BaseModel):
    name: str
    code: str
    email: EmailStr
    phone: str
    address: Address

class OperationalTiming(BaseModel):
    day: str
    open: str  # Format: "HH:MM"
    close: str  # Format: "HH:MM"

class OperationalDetails(BaseModel):
    courses_offered: List[str]  # Course names for display purposes
    timings: List[OperationalTiming]
    holidays: List[str]  # List of date strings in YYYY-MM-DD format

class Assignments(BaseModel):
    accessories_available: bool
    courses: List[str]  # List of course IDs (UUIDs)
    branch_admins: List[str]  # List of user IDs (UUIDs) for coaches

class BankDetails(BaseModel):
    bank_name: str
    account_number: str
    upi_id: str

class Branch(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    branch: BranchInfo
    location_id: str  # Reference to location
    manager_id: str
    operational_details: OperationalDetails
    assignments: Assignments
    bank_details: BankDetails
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class BranchCreate(BaseModel):
    branch: BranchInfo
    location_id: str  # Reference to location
    manager_id: str
    operational_details: OperationalDetails
    assignments: Assignments
    bank_details: BankDetails

class BranchUpdate(BaseModel):
    branch: Optional[BranchInfo] = None
    location_id: Optional[str] = None  # Reference to location
    manager_id: Optional[str] = None
    operational_details: Optional[OperationalDetails] = None
    assignments: Optional[Assignments] = None
    bank_details: Optional[BankDetails] = None
    is_active: Optional[bool] = None
