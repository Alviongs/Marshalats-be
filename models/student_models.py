from pydantic import BaseModel
from datetime import datetime
from typing import Optional, Dict, Any
from enum import Enum

class StudentEnrollmentCreate(BaseModel):
    course_id: str
    branch_id: str
    start_date: datetime

class StudentPaymentCreate(BaseModel):
    enrollment_id: str
    amount: float
    payment_method: str
    transaction_id: str = None
    notes: str = None

# New models for registration payment flow
class StudentRegistrationPayment(BaseModel):
    student_id: str
    course_id: str
    branch_id: str
    category_id: str
    duration: str
    total_amount: float
    admission_fee: float
    course_fee: float
    payment_method: str
    payment_status: str = "pending"
    transaction_id: Optional[str] = None
    payment_date: Optional[datetime] = None
    created_at: datetime = datetime.utcnow()

class PaymentCalculation(BaseModel):
    course_fee: float
    admission_fee: float = 500.0  # Default admission fee
    total_amount: float
    currency: str = "INR"
    duration_multiplier: float = 1.0

class CoursePaymentInfo(BaseModel):
    course_id: str
    course_name: str
    category_name: str
    branch_name: str
    duration: str
    pricing: PaymentCalculation
