from pydantic import BaseModel, Field, EmailStr
from datetime import datetime
from typing import Optional
import uuid

class SuperAdmin(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    full_name: str
    email: EmailStr
    phone: str
    password_hash: str
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class SuperAdminRegister(BaseModel):
    full_name: str
    email: EmailStr
    password: str
    phone: str

class SuperAdminLogin(BaseModel):
    email: EmailStr
    password: str

class SuperAdminUpdate(BaseModel):
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None

class SuperAdminResponse(BaseModel):
    id: str
    full_name: str
    email: str
    phone: str
    is_active: bool
    created_at: datetime
    updated_at: datetime

class SuperAdminForgotPassword(BaseModel):
    email: EmailStr

class SuperAdminResetPassword(BaseModel):
    token: str
    new_password: str
