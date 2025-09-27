from pydantic import BaseModel, Field, EmailStr
from datetime import datetime
from typing import Optional, List, Dict, Any
from enum import Enum
import uuid

class MessageStatus(str, Enum):
    SENT = "sent"
    DELIVERED = "delivered"
    READ = "read"
    ARCHIVED = "archived"
    DELETED = "deleted"

class MessagePriority(str, Enum):
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"

class UserType(str, Enum):
    STUDENT = "student"
    COACH = "coach"
    BRANCH_MANAGER = "branch_manager"
    SUPERADMIN = "superadmin"

class MessageParticipant(BaseModel):
    user_id: str
    user_type: UserType
    user_name: str
    user_email: str
    branch_id: Optional[str] = None  # For role-based filtering

class MessageAttachment(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    filename: str
    file_type: str
    file_size: int
    file_url: str
    uploaded_at: datetime = Field(default_factory=datetime.utcnow)

class Message(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    thread_id: Optional[str] = None  # For grouping related messages
    
    # Sender information
    sender_id: str
    sender_type: UserType
    sender_name: str
    sender_email: str
    sender_branch_id: Optional[str] = None
    
    # Recipient information
    recipient_id: str
    recipient_type: UserType
    recipient_name: str
    recipient_email: str
    recipient_branch_id: Optional[str] = None
    
    # Message content
    subject: str
    content: str
    attachments: Optional[List[MessageAttachment]] = []
    
    # Message metadata
    priority: MessagePriority = MessagePriority.NORMAL
    status: MessageStatus = MessageStatus.SENT
    is_read: bool = False
    is_archived: bool = False
    is_deleted: bool = False
    read_at: Optional[datetime] = None
    
    # Reply information
    reply_to_message_id: Optional[str] = None
    is_reply: bool = False
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Access control - for role-based filtering
    allowed_branches: Optional[List[str]] = []  # Empty means all branches
    is_system_message: bool = False

class MessageThread(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    subject: str
    participants: List[MessageParticipant]
    
    # Thread metadata
    message_count: int = 0
    last_message_id: Optional[str] = None
    last_message_at: Optional[datetime] = None
    last_sender_id: Optional[str] = None
    
    # Thread status
    is_active: bool = True
    is_archived: bool = False
    
    # Access control
    allowed_branches: Optional[List[str]] = []
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class MessageCreate(BaseModel):
    recipient_id: str
    recipient_type: UserType
    subject: str
    content: str
    priority: MessagePriority = MessagePriority.NORMAL
    reply_to_message_id: Optional[str] = None
    thread_id: Optional[str] = None  # Allow explicit thread specification
    attachments: Optional[List[Dict[str, Any]]] = []

class MessageUpdate(BaseModel):
    is_read: Optional[bool] = None
    is_archived: Optional[bool] = None
    is_deleted: Optional[bool] = None
    status: Optional[MessageStatus] = None

class MessageResponse(BaseModel):
    id: str
    thread_id: Optional[str]
    sender_name: str
    sender_type: UserType
    recipient_name: str
    recipient_type: UserType
    subject: str
    content: str
    priority: MessagePriority
    status: MessageStatus
    is_read: bool
    is_archived: bool
    is_reply: bool
    reply_to_message_id: Optional[str]
    attachments: Optional[List[MessageAttachment]]
    created_at: datetime
    updated_at: datetime
    read_at: Optional[datetime]

class ConversationResponse(BaseModel):
    thread_id: str
    subject: str
    participants: List[MessageParticipant]
    message_count: int
    last_message: Optional[MessageResponse]
    last_message_at: Optional[datetime]
    unread_count: int
    is_archived: bool
    created_at: datetime
    updated_at: datetime

class MessageStats(BaseModel):
    total_messages: int
    unread_messages: int
    sent_messages: int
    received_messages: int
    archived_messages: int
    deleted_messages: int
    active_conversations: int

class BulkMessageCreate(BaseModel):
    recipient_ids: List[str]
    recipient_type: UserType
    subject: str
    content: str
    priority: MessagePriority = MessagePriority.NORMAL
    branch_filter: Optional[str] = None  # For branch-specific broadcasts

class MessageSearchQuery(BaseModel):
    query: Optional[str] = None
    sender_type: Optional[UserType] = None
    recipient_type: Optional[UserType] = None
    priority: Optional[MessagePriority] = None
    status: Optional[MessageStatus] = None
    is_read: Optional[bool] = None
    is_archived: Optional[bool] = None
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    branch_id: Optional[str] = None
