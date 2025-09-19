from pydantic import BaseModel, Field, EmailStr
from datetime import datetime
from typing import Optional, List
import uuid

class PersonalInfo(BaseModel):
    first_name: str
    last_name: str
    gender: Optional[str] = None
    date_of_birth: Optional[str] = None  # Format: YYYY-MM-DD

class ContactInfo(BaseModel):
    email: EmailStr
    country_code: str = "+91"
    phone: str
    password: Optional[str] = None  # Only used during creation

class AddressInfo(BaseModel):
    address: Optional[str] = None
    area: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    zip_code: Optional[str] = None
    country: str = "India"

class ProfessionalInfo(BaseModel):
    designation: str = "Branch Manager"
    education_qualification: Optional[str] = None
    professional_experience: Optional[str] = None
    certifications: Optional[List[str]] = []

class BranchAssignment(BaseModel):
    branch_id: Optional[str] = None
    branch_name: Optional[str] = None
    branch_location: Optional[str] = None

class EmergencyContact(BaseModel):
    name: Optional[str] = None
    phone: Optional[str] = None
    relationship: Optional[str] = None

class BranchManager(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    personal_info: PersonalInfo
    contact_info: ContactInfo
    address_info: Optional[AddressInfo] = None
    professional_info: ProfessionalInfo
    branch_assignment: Optional[BranchAssignment] = None
    emergency_contact: Optional[EmergencyContact] = None
    
    # Computed fields for easy access
    email: str = ""
    phone: str = ""
    first_name: str = ""
    last_name: str = ""
    full_name: str = ""
    
    # Security and status
    password_hash: Optional[str] = None
    is_active: bool = True
    notes: Optional[str] = None
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class BranchManagerCreate(BaseModel):
    personal_info: PersonalInfo
    contact_info: ContactInfo
    address_info: Optional[AddressInfo] = None
    professional_info: ProfessionalInfo
    branch_id: Optional[str] = None  # Direct branch assignment
    emergency_contact: Optional[EmergencyContact] = None
    notes: Optional[str] = None

class BranchManagerUpdate(BaseModel):
    personal_info: Optional[PersonalInfo] = None
    contact_info: Optional[ContactInfo] = None
    address_info: Optional[AddressInfo] = None
    professional_info: Optional[ProfessionalInfo] = None
    branch_assignment: Optional[BranchAssignment] = None
    emergency_contact: Optional[EmergencyContact] = None
    password: Optional[str] = None  # Optional password update
    is_active: Optional[bool] = None
    notes: Optional[str] = None

class BranchManagerResponse(BaseModel):
    id: str
    personal_info: PersonalInfo
    contact_info: dict  # Exclude password
    address_info: Optional[AddressInfo] = None
    professional_info: ProfessionalInfo
    branch_assignment: Optional[BranchAssignment] = None
    emergency_contact: Optional[EmergencyContact] = None
    full_name: str
    is_active: bool
    notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime

class BranchManagerLogin(BaseModel):
    email: EmailStr
    password: str

class BranchManagerLoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    branch_manager: BranchManagerResponse

class BranchManagerForgotPassword(BaseModel):
    email: EmailStr

class BranchManagerResetPassword(BaseModel):
    token: str
    new_password: str
