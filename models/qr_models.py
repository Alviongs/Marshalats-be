from pydantic import BaseModel, Field
from datetime import datetime
import uuid

class QRCodeSession(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    branch_id: str
    course_id: str
    qr_code: str
    qr_code_data: str  # Base64 encoded QR image
    generated_by: str  # User ID
    valid_until: datetime
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)
