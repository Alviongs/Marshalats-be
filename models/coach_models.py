from pydantic import BaseModel, Field, EmailStr
from datetime import datetime
from typing import List, Optional
from enum import Enum
import uuid

# Assignment details for coaches
class AssignmentDetails(BaseModel):
    courses: List[str] = Field(default_factory=list)  # List of course IDs assigned to the coach
    salary: Optional[float] = None  # Coach's salary
    join_date: Optional[str] = None  # Date when coach joined (ISO format)

# Emergency contact information
class EmergencyContact(BaseModel):
    name: Optional[str] = None
    phone: Optional[str] = None
    relationship: Optional[str] = None

class PersonalInfo(BaseModel):
    first_name: str
    last_name: str
    gender: str
    date_of_birth: str  # YYYY-MM-DD format

class ContactInfo(BaseModel):
    email: EmailStr
    country_code: str
    phone: str
    password: Optional[str] = None

class AddressInfo(BaseModel):
    address: str
    area: str
    city: str
    state: str
    zip_code: str
    country: str

class ProfessionalInfo(BaseModel):
    education_qualification: str
    professional_experience: str
    designation_id: str
    certifications: List[str]

class CoachCreate(BaseModel):
    personal_info: PersonalInfo
    contact_info: ContactInfo
    address_info: AddressInfo
    professional_info: ProfessionalInfo
    areas_of_expertise: List[str]
    branch_id: Optional[str] = None  # Branch assignment for the coach
    assignment_details: Optional[AssignmentDetails] = None  # Course assignments and other details
    emergency_contact: Optional[EmergencyContact] = None  # Emergency contact information

class CoachUpdate(BaseModel):
    personal_info: Optional[PersonalInfo] = None
    contact_info: Optional[ContactInfo] = None
    address_info: Optional[AddressInfo] = None
    professional_info: Optional[ProfessionalInfo] = None
    areas_of_expertise: Optional[List[str]] = None
    branch_id: Optional[str] = None  # Branch assignment for the coach
    assignment_details: Optional[AssignmentDetails] = None  # Course assignments and other details
    emergency_contact: Optional[EmergencyContact] = None  # Emergency contact information

class CoachLogin(BaseModel):
    email: EmailStr
    password: str

class CoachLoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    coach: dict
    expires_in: int

class Coach(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    personal_info: PersonalInfo
    contact_info: ContactInfo
    address_info: AddressInfo
    professional_info: ProfessionalInfo
    areas_of_expertise: List[str]
    branch_id: Optional[str] = None  # Branch assignment for the coach
    assignment_details: Optional[AssignmentDetails] = None  # Course assignments and other details
    emergency_contact: Optional[EmergencyContact] = None  # Emergency contact information
    # Basic user fields for authentication and identification
    email: EmailStr  # Duplicate from contact_info for easy access
    phone: str  # Full phone with country code
    first_name: str  # Duplicate from personal_info for easy access
    last_name: str  # Duplicate from personal_info for easy access
    full_name: str  # Auto-generated from first_name + last_name
    role: str = "coach"  # Fixed as coach
    is_active: bool = True
    password_hash: str  # Hashed password
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class CoachResponse(BaseModel):
    id: str
    personal_info: PersonalInfo
    contact_info: dict  # ContactInfo without password
    address_info: AddressInfo
    professional_info: ProfessionalInfo
    areas_of_expertise: List[str]
    branch_id: Optional[str] = None  # Branch assignment for the coach
    assignment_details: Optional[AssignmentDetails] = None  # Course assignments and other details
    emergency_contact: Optional[EmergencyContact] = None  # Emergency contact information
    full_name: str
    is_active: bool
    created_at: datetime
    updated_at: datetime

class CoachForgotPassword(BaseModel):
    email: EmailStr

class CoachResetPassword(BaseModel):
    token: str
    new_password: str
