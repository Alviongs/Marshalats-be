from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, Dict, Any
import uuid
from enum import Enum

class PaymentStatus(str, Enum):
    PENDING = "pending"
    PAID = "paid"
    OVERDUE = "overdue"
    CANCELLED = "cancelled"
    PROCESSING = "processing"
    FAILED = "failed"

class PaymentType(str, Enum):
    ADMISSION_FEE = "admission_fee"
    COURSE_FEE = "course_fee"
    MONTHLY_FEE = "monthly_fee"
    REGISTRATION_FEE = "registration_fee"

class PaymentMethod(str, Enum):
    CREDIT_CARD = "credit_card"
    DEBIT_CARD = "debit_card"
    UPI = "upi"
    NET_BANKING = "net_banking"
    DIGITAL_WALLET = "digital_wallet"
    CASH = "cash"
    BANK_TRANSFER = "bank_transfer"

class Payment(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    student_id: str
    enrollment_id: Optional[str] = None  # Made optional for registration payments
    amount: float
    payment_type: PaymentType
    payment_method: PaymentMethod
    payment_status: PaymentStatus
    transaction_id: Optional[str] = None
    payment_date: Optional[datetime] = None
    due_date: datetime
    notes: Optional[str] = None
    payment_proof: Optional[str] = None
    # Registration-specific fields
    registration_data: Optional[Dict[str, Any]] = None  # Store registration context
    course_details: Optional[Dict[str, Any]] = None  # Course information
    branch_details: Optional[Dict[str, Any]] = None  # Branch information
    # Notification tracking
    notification_sent: bool = False
    notification_sent_at: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class PaymentProof(BaseModel):
    proof: str

class PaymentCreate(BaseModel):
    student_id: str
    enrollment_id: Optional[str] = None
    amount: float
    payment_type: PaymentType
    payment_method: PaymentMethod
    due_date: datetime
    transaction_id: Optional[str] = None
    notes: Optional[str] = None
    registration_data: Optional[Dict[str, Any]] = None
    course_details: Optional[Dict[str, Any]] = None
    branch_details: Optional[Dict[str, Any]] = None

# New model for registration payment processing
class RegistrationPaymentCreate(BaseModel):
    student_data: Dict[str, Any]  # Complete student registration data
    course_id: str
    branch_id: str
    category_id: str
    duration: str
    payment_method: PaymentMethod
    card_details: Optional[Dict[str, str]] = None  # For card payments

class RegistrationPaymentResponse(BaseModel):
    payment_id: str
    student_id: str
    transaction_id: str
    amount: float
    status: PaymentStatus
    message: str
