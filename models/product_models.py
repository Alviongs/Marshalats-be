from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, Dict
import uuid

class Product(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: str
    category: str
    price: float
    branch_availability: Dict[str, int] = {}
    stock_alert_threshold: int = 10
    image_url: Optional[str] = None
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class ProductCreate(BaseModel):
    name: str
    description: str
    category: str
    price: float
    branch_availability: Optional[Dict[str, int]] = {}
    stock_alert_threshold: Optional[int] = 10
    image_url: Optional[str] = None

class ProductUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    price: Optional[float] = None
    branch_availability: Optional[Dict[str, int]] = None
    stock_alert_threshold: Optional[int] = None
    image_url: Optional[str] = None
    is_active: Optional[bool] = None

class ProductPurchase(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    student_id: str
    product_id: str
    branch_id: str
    quantity: int
    unit_price: float
    total_amount: float
    payment_method: str
    purchase_date: datetime = Field(default_factory=datetime.utcnow)
    created_at: datetime = Field(default_factory=datetime.utcnow)

class ProductPurchaseCreate(BaseModel):
    student_id: str
    product_id: str
    branch_id: str
    quantity: int
    payment_method: str

class RestockRequest(BaseModel):
    branch_id: str
    quantity: int
