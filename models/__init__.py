# Models package for Student Management System

# Import all models for easy access
from .user_models import UserRole, BaseUser, UserCreate, UserLogin, ForgotPassword, ResetPassword, UserUpdate
from .branch_models import Branch, BranchCreate, BranchUpdate
from .branch_manager_models import (
    BranchManager, BranchManagerCreate, BranchManagerUpdate, BranchManagerResponse,
    BranchManagerLogin, BranchManagerLoginResponse, BranchManagerForgotPassword, BranchManagerResetPassword
)
from .course_models import Course, CourseCreate, CourseUpdate
from .category_models import Category, CategoryCreate, CategoryUpdate, CategoryResponse
from .duration_models import Duration, DurationCreate, DurationUpdate, DurationResponse
from .location_models import Location, LocationCreate, LocationUpdate, LocationWithBranches, LocationResponse
from .enrollment_models import PaymentStatus, Enrollment, EnrollmentCreate
from .payment_models import Payment, PaymentProof, PaymentCreate, PaymentStatus, PaymentType, PaymentMethod, RegistrationPaymentCreate, RegistrationPaymentResponse
from .attendance_models import (
    AttendanceMethod, Attendance, AttendanceCreate, BiometricAttendance,
    CoachAttendance, CoachAttendanceCreate, BranchManagerAttendance, BranchManagerAttendanceCreate,
    AttendanceStatus, AttendanceMarkRequest
)
from .product_models import Product, ProductCreate, ProductUpdate, ProductPurchase, ProductPurchaseCreate, RestockRequest
from .notification_models import NotificationType, NotificationTemplate, NotificationTemplateCreate, TriggerNotification, NotificationLog, BroadcastAnnouncement, ClassReminder, PaymentNotification, PaymentNotificationCreate, MessageNotification, MessageNotificationCreate
from .holiday_models import Holiday, HolidayCreate
from .complaint_models import ComplaintStatus, Complaint, ComplaintCreate, ComplaintUpdate
from .rating_models import CoachRating, CoachRatingCreate
from .session_models import SessionStatus, SessionBooking, SessionBookingCreate
from .activitylog_models import ActivityLog
from .transfer_models import TransferRequestStatus, TransferRequest, TransferRequestCreate, TransferRequestUpdate
from .coursechange_models import CourseChangeRequestStatus, CourseChangeRequest, CourseChangeRequestCreate, CourseChangeRequestUpdate
from .event_models import Event, EventCreate
from .qr_models import QRCodeSession
from .student_models import StudentEnrollmentCreate, StudentPaymentCreate, StudentRegistrationPayment, PaymentCalculation, CoursePaymentInfo
from .settings_models import (
    SystemConfiguration, EmailConfiguration, NotificationSettings, SecuritySettings, BackupSettings,
    SystemSettings, SystemSettingsCreate, SystemSettingsUpdate, SystemSettingsResponse,
    SystemSettingsFlatCreate, SystemSettingsFlatResponse
)
from .message_models import (
    MessageStatus, MessagePriority, UserType, MessageParticipant, MessageAttachment,
    Message, MessageThread, MessageCreate, MessageUpdate, MessageResponse, ConversationResponse,
    MessageStats, BulkMessageCreate, MessageSearchQuery
)

__all__ = [
    # User models
    'UserRole', 'BaseUser', 'UserCreate', 'UserLogin', 'ForgotPassword', 'ResetPassword', 'UserUpdate',
    
    # Branch models
    'Branch', 'BranchCreate', 'BranchUpdate',
    
    # Course models
    'Course', 'CourseCreate', 'CourseUpdate',

    # Category models
    'Category', 'CategoryCreate', 'CategoryUpdate', 'CategoryResponse',

    # Duration models
    'Duration', 'DurationCreate', 'DurationUpdate', 'DurationResponse',

    # Location models
    'Location', 'LocationCreate', 'LocationUpdate', 'LocationWithBranches', 'LocationResponse',
    
    # Enrollment models
    'PaymentStatus', 'Enrollment', 'EnrollmentCreate',
    
    # Payment models
    'Payment', 'PaymentProof', 'PaymentCreate', 'PaymentStatus', 'PaymentType', 'PaymentMethod',
    'RegistrationPaymentCreate', 'RegistrationPaymentResponse',
    
    # Attendance models
    'AttendanceMethod', 'Attendance', 'AttendanceCreate', 'BiometricAttendance',
    'CoachAttendance', 'CoachAttendanceCreate', 'BranchManagerAttendance', 'BranchManagerAttendanceCreate',
    'AttendanceStatus', 'AttendanceMarkRequest',
    
    # Product models
    'Product', 'ProductCreate', 'ProductUpdate', 'ProductPurchase', 'ProductPurchaseCreate', 'RestockRequest',
    
    # Notification models
    'NotificationType', 'NotificationTemplate', 'NotificationTemplateCreate', 'TriggerNotification', 'NotificationLog', 'BroadcastAnnouncement', 'ClassReminder', 'PaymentNotification', 'PaymentNotificationCreate', 'MessageNotification', 'MessageNotificationCreate',
    
    # Holiday models
    'Holiday', 'HolidayCreate',
    
    # Complaint models
    'ComplaintStatus', 'Complaint', 'ComplaintCreate', 'ComplaintUpdate',
    
    # Rating models
    'CoachRating', 'CoachRatingCreate',
    
    # Session models
    'SessionStatus', 'SessionBooking', 'SessionBookingCreate',
    
    # Activity log models
    'ActivityLog',
    
    # Transfer models
    'TransferRequestStatus', 'TransferRequest', 'TransferRequestCreate', 'TransferRequestUpdate',
    
    # Course change models
    'CourseChangeRequestStatus', 'CourseChangeRequest', 'CourseChangeRequestCreate', 'CourseChangeRequestUpdate',
    
    # Event models
    'Event', 'EventCreate',
    
    # QR models
    'QRCodeSession',
    
    # Student models
    'StudentEnrollmentCreate', 'StudentPaymentCreate', 'StudentRegistrationPayment',
    'PaymentCalculation', 'CoursePaymentInfo',

    # Message models
    'MessageStatus', 'MessagePriority', 'UserType', 'MessageParticipant', 'MessageAttachment',
    'Message', 'MessageThread', 'MessageCreate', 'MessageUpdate', 'MessageResponse',
    'ConversationResponse', 'MessageStats', 'BulkMessageCreate', 'MessageSearchQuery'
]
