from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
from pathlib import Path
import os
from contextlib import asynccontextmanager

# Import routes
from routes import (
    auth_router,
    user_router,
    branch_router,
    course_router,
    enrollment_router,
    payment_router,
    request_router,
    event_router
)

# Import database utility
from utils.database import db

# Load environment variables
ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Import and set the global db variable
    from utils import database
    mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
    client = AsyncIOMotorClient(mongo_url)
    database.db = client[os.environ.get('DB_NAME', 'marshalats')]
    print("Database connection opened.")
    yield
    client.close()
    print("Database connection closed.")

# Create FastAPI app
app = FastAPI(title="Student Management System", version="1.0.0", lifespan=lifespan)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include all routers
app.include_router(auth_router, prefix="/api")
app.include_router(user_router, prefix="/api")
app.include_router(branch_router, prefix="/api")
app.include_router(course_router, prefix="/api")
app.include_router(enrollment_router, prefix="/api")
app.include_router(payment_router, prefix="/api")
app.include_router(request_router, prefix="/api")
app.include_router(event_router, prefix="/api")

# Health check endpoint
@app.get("/")
async def health_check():
    return {"status": "OK", "message": "Student Management System API", "version": "1.0.0"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
db = None

from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    global db
    mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
    client = AsyncIOMotorClient(mongo_url)
    db = client[os.environ.get('DB_NAME', 'marshalats')]
    print("Database connection opened.")
    yield
    client.close()
    print("Database connection closed.")

# Create FastAPI app
app = FastAPI(title="Student Management System", version="1.0.0", lifespan=lifespan)
api_router = APIRouter(prefix="/api")

# Security setup
security = HTTPBearer()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
SECRET_KEY = os.environ.get('SECRET_KEY', 'student_management_secret_key_2025')
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24 hours

# Authentication utilities
def serialize_doc(doc):
    """Convert MongoDB document to JSON serializable format"""
    if doc is None:
        return None
    if isinstance(doc, list):
        return [serialize_doc(item) for item in doc]
    if isinstance(doc, dict):
        result = {}
        for key, value in doc.items():
            if key == "_id":
                continue  # Skip MongoDB _id field
            elif isinstance(value, ObjectId):
                result[key] = str(value)
            elif isinstance(value, dict):
                result[key] = serialize_doc(value)
            elif isinstance(value, list):
                result[key] = serialize_doc(value)
            else:
                result[key] = value
        return result
    return doc

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid authentication credentials")
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid authentication credentials")
    
    user = await db.users.find_one({"id": user_id})
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")
    return serialize_doc(user)

async def get_current_active_user(current_user: dict = Depends(get_current_user)):
    if not current_user.get("is_active", False):
        raise HTTPException(status_code=400, detail="Inactive user")

    # Restrict access for students with overdue payments
    if current_user["role"] == UserRole.STUDENT:
        overdue_payment = await db.payments.find_one({
            "student_id": current_user["id"],
            "payment_status": PaymentStatus.OVERDUE.value
        })
        if overdue_payment:
            raise HTTPException(status_code=403, detail="Access restricted due to overdue payments.")

    return current_user

def require_role(allowed_roles: List[UserRole]):
    async def role_checker(current_user: dict = Depends(get_current_active_user)):
        if current_user["role"] not in [role.value for role in allowed_roles]:
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        return current_user
    return role_checker

# QR Code utilities
def generate_qr_code(data: str) -> str:
    """Generate QR code and return base64 encoded image"""
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(data)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    img_buffer = io.BytesIO()
    img.save(img_buffer, format='PNG')
    img_buffer.seek(0)
    
    return base64.b64encode(img_buffer.getvalue()).decode()

# Notification utilities (Mock implementations - to be replaced with real integrations)
async def send_sms(phone: str, message: str) -> bool:
    """Mock SMS sending - to be replaced with Firebase integration"""
    logging.info(f"Mock SMS sent to {phone}: {message}")
    return True

async def send_whatsapp(phone: str, message: str) -> bool:
    """Mock WhatsApp sending - to be replaced with zaptra.in integration"""
    logging.info(f"Mock WhatsApp sent to {phone}: {message}")
    return True

# Activity Logging utility
async def log_activity(
    request: Request,
    action: str,
    status: str = "success",
    user_id: Optional[str] = None,
    user_name: Optional[str] = None,
    details: Optional[Dict[str, Any]] = None
):
    """Helper function to log user activity."""
    log_entry = ActivityLog(
        user_id=user_id,
        user_name=user_name,
        action=action,
        details=details,
        status=status,
        ip_address=request.client.host if request else "N/A",
        timestamp=datetime.utcnow()
    )
    await db.activity_logs.insert_one(log_entry.dict())

async def check_and_send_stock_alert(product: dict, branch_id: str, new_stock_level: int):
    """Checks if stock is low and sends an alert if needed."""
    threshold = product.get("stock_alert_threshold", 10)
    if new_stock_level <= threshold:
        # Find admins to notify (Super Admins and the Coach Admin of the branch)
        admin_filter = {
            "$or": [
                {"role": UserRole.SUPER_ADMIN.value},
                {"role": UserRole.COACH_ADMIN.value, "branch_id": branch_id}
            ]
        }
        admins = await db.users.find(admin_filter).to_list(length=None)

        template = await db.notification_templates.find_one({"name": "low_stock_alert"})
        if not template or not admins:
            return # Cannot send alert if no template or no admins

        for admin in admins:
            body = template["body"].replace("{{product_name}}", product["name"])
            body = body.replace("{{branch_id}}", branch_id)
            body = body.replace("{{stock_level}}", str(new_stock_level))

            success = False
            if template["type"] == NotificationType.WHATSAPP.value:
                success = await send_whatsapp(admin["phone"], body)
            elif template["type"] == NotificationType.SMS.value:
                success = await send_sms(admin["phone"], body)

            log_entry = NotificationLog(
                user_id=admin["id"],
                template_id=template["id"],
                type=template["type"],
                status="sent" if success else "failed",
                content=body
            )
            await db.notification_logs.insert_one(log_entry.dict())

# AUTHENTICATION ENDPOINTS
@api_router.post("/auth/register")
async def register_user(user_data: UserCreate, request: Request):
    """Register a new student (public endpoint)"""
    # Check if user exists
    existing_user = await db.users.find_one({
        "$or": [{"email": user_data.email}, {"phone": user_data.phone}]
    })
    if existing_user:
        raise HTTPException(status_code=400, detail="User with this email or phone already exists")
    
    # Generate password if not provided
    if not user_data.password:
        user_data.password = secrets.token_urlsafe(8)
    
    # Hash password
    hashed_password = hash_password(user_data.password)
    
    # Create user
    user = BaseUser(**user_data.dict())
    user_dict = user.dict()
    user_dict["password"] = hashed_password
    
    result = await db.users.insert_one(user_dict)
    
    # Send credentials via SMS (mock)
    sms_message = (
        f"Your account has been created.\n"
        f"Email: {user.email}\n"
        f"Password: {user_data.password}\n"
        f"Date of Birth: {user_data.date_of_birth}\n"
        f"Gender: {user_data.gender}"
    )
    await send_sms(user.phone, sms_message)
    
    await log_activity(
        request=request,
        action="user_registration",
        user_id=user.id,
        user_name=user.full_name,
        details={"email": user.email, "role": user.role}
    )

    return {"message": "User registered successfully", "user_id": user.id}

@api_router.post("/auth/login")
async def login(user_credentials: UserLogin, request: Request):
    """User login"""
    user = await db.users.find_one({"email": user_credentials.email})
    if not user or not verify_password(user_credentials.password, user["password"]):
        await log_activity(
            request=request,
            action="login_attempt",
            status="failure",
            details={"email": user_credentials.email, "reason": "Incorrect email or password"}
        )
        raise HTTPException(status_code=401, detail="Incorrect email or password")
    
    if not user.get("is_active", False):
        await log_activity(
            request=request,
            action="login_attempt",
            status="failure",
            user_id=user["id"],
            user_name=user["full_name"],
            details={"email": user_credentials.email, "reason": "Account is deactivated"}
        )
        raise HTTPException(status_code=400, detail="Account is deactivated")
    
    access_token = create_access_token(data={"sub": user["id"]})

    await log_activity(
        request=request,
        action="login_success",
        user_id=user["id"],
        user_name=user["full_name"],
        details={"email": user["email"]}
    )

    return {"access_token": access_token, "token_type": "bearer", "user": {
        "id": user["id"],
        "email": user["email"],
        "role": user["role"],
        "full_name": user["full_name"],
        "date_of_birth": user.get("date_of_birth"),
        "gender": user.get("gender")
    }}

@api_router.post("/auth/forgot-password")
async def forgot_password(forgot_password_data: ForgotPassword):
    """Initiate password reset process"""
    user = await db.users.find_one({"email": forgot_password_data.email})
    if not user:
        # Don't reveal that the user does not exist
        return {"message": "If an account with that email exists, a password reset link has been sent."}

    # Generate a short-lived token for password reset
    reset_token = create_access_token(
        data={"sub": user["id"], "scope": "password_reset"},
        expires_delta=timedelta(minutes=15)
    )

    # In a real application, you would email this token to the user
    # For this example, we'll just log it.
    logging.info(f"Password reset token for {user['email']}: {reset_token}")

    await send_sms(user["phone"], f"Your password reset token is: {reset_token}")

    response = {"message": "If an account with that email exists, a password reset link has been sent."}
    if os.environ.get("TESTING") == "True":
        response["reset_token"] = reset_token
    return response

@api_router.post("/auth/reset-password")
async def reset_password(reset_password_data: ResetPassword):
    """Reset password using a token"""
    try:
        payload = jwt.decode(
            reset_password_data.token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )
        if payload.get("scope") != "password_reset":
            raise HTTPException(status_code=401, detail="Invalid token scope")

        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid token")

    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    new_hashed_password = hash_password(reset_password_data.new_password)
    result = await db.users.update_one(
        {"id": user_id},
        {"$set": {"password": new_hashed_password, "updated_at": datetime.utcnow()}}
    )

    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="User not found")

    return {"message": "Password has been reset successfully."}

@api_router.get("/auth/me")
async def get_current_user_info(current_user: dict = Depends(get_current_active_user)):
    """Get current user information"""
    user_info = current_user.copy()
    user_info.pop("password", None)
    user_info["date_of_birth"] = current_user.get("date_of_birth")
    user_info["gender"] = current_user.get("gender")
    return user_info

@api_router.put("/auth/profile")
async def update_profile(
    user_update: UserUpdate,
    current_user: dict = Depends(get_current_active_user)
):
    """Update user profile"""
    update_data = {k: v for k, v in user_update.dict().items() if v is not None}
    update_data["updated_at"] = datetime.utcnow()
    
    # Ensure date_of_birth and gender are included in the update
    if user_update.date_of_birth:
        update_data["date_of_birth"] = user_update.date_of_birth
    if user_update.gender:
        update_data["gender"] = user_update.gender
    
    await db.users.update_one(
        {"id": current_user["id"]},
        {"$set": update_data}
    )
    return {"message": "Profile updated successfully"}

# USER MANAGEMENT ENDPOINTS (Super Admin only)
@api_router.post("/users")
async def create_user(
    user_data: UserCreate,
    request: Request,
    current_user: dict = Depends(require_role([UserRole.SUPER_ADMIN, UserRole.COACH_ADMIN]))
):
    """Create new user (Super Admin or Coach Admin)"""
    # If a coach admin is creating a user, they must be in the same branch
    if current_user["role"] == UserRole.COACH_ADMIN:
        if not current_user.get("branch_id") or user_data.branch_id != current_user["branch_id"]:
            raise HTTPException(status_code=403, detail="Coach Admins can only create users for their own branch.")
        # Coach admins cannot create other admins
        if user_data.role in [UserRole.SUPER_ADMIN, UserRole.COACH_ADMIN]:
            raise HTTPException(status_code=403, detail="Coach Admins cannot create other admin users.")

    # Check if user exists
    existing_user = await db.users.find_one({
        "$or": [{"email": user_data.email}, {"phone": user_data.phone}]
    })
    if existing_user:
        raise HTTPException(status_code=400, detail="User already exists")
    
    # Generate password if not provided
    if not user_data.password:
        user_data.password = secrets.token_urlsafe(8)
    
    hashed_password = hash_password(user_data.password)
    user = BaseUser(**user_data.dict())
    user_dict = user.dict()
    user_dict["password"] = hashed_password
    
    # Ensure date_of_birth and gender are included in the user creation
    if user_data.date_of_birth:
        user_dict["date_of_birth"] = user_data.date_of_birth
    if user_data.gender:
        user_dict["gender"] = user_data.gender

    await db.users.insert_one(user_dict)
    
    # Send credentials
    await send_sms(user.phone, f"Account created. Email: {user.email}, Password: {user_data.password}")
    
    await log_activity(
        request=request,
        action="admin_create_user",
        user_id=current_user["id"],
        user_name=current_user["full_name"],
        details={"created_user_id": user.id, "created_user_email": user.email, "role": user.role}
    )

    return {"message": "User created successfully", "user_id": user.id}

@api_router.get("/users")
async def get_users(
    role: Optional[UserRole] = None,
    branch_id: Optional[str] = None,
    skip: int = 0,
    limit: int = 50,
    current_user: dict = Depends(require_role([UserRole.SUPER_ADMIN, UserRole.COACH_ADMIN]))
):
    """Get users with filtering"""
    filter_query = {}
    if role:
        filter_query["role"] = role.value
    if branch_id:
        filter_query["branch_id"] = branch_id
    
    users = await db.users.find(filter_query).skip(skip).limit(limit).to_list(length=limit)
    for user in users:
        user.pop("password", None)
        user["date_of_birth"] = user.get("date_of_birth")
        user["gender"] = user.get("gender")
    
    return {"users": serialize_doc(users), "total": len(users)}

@api_router.put("/users/{user_id}")
async def update_user(
    user_id: str,
    user_update: UserUpdate,
    request: Request,
    current_user: dict = Depends(require_role([UserRole.SUPER_ADMIN, UserRole.COACH_ADMIN]))
):
    """Update user (Super Admin or Coach Admin)"""
    target_user = await db.users.find_one({"id": user_id})
    if not target_user:
        raise HTTPException(status_code=404, detail="User not found")

    if current_user["role"] == UserRole.COACH_ADMIN:
        # Coach Admins can only update students in their own branch
        if target_user["role"] != UserRole.STUDENT.value:
            raise HTTPException(status_code=403, detail="Coach Admins can only update student profiles.")
        if target_user.get("branch_id") != current_user.get("branch_id"):
            raise HTTPException(status_code=403, detail="Coach Admins can only update students in their own branch.")

    update_data = {k: v for k, v in user_update.dict(exclude_unset=True).items()}
    if not update_data:
        raise HTTPException(status_code=400, detail="No update data provided")

    # Ensure date_of_birth and gender are included in the update
    if user_update.date_of_birth:
        update_data["date_of_birth"] = user_update.date_of_birth
    if user_update.gender:
        update_data["gender"] = user_update.gender

    update_data["updated_at"] = datetime.utcnow()
    
    result = await db.users.update_one(
        {"id": user_id},
        {"$set": update_data}
    )
    
    if result.matched_count == 0:
        # This case should be rare due to the check above, but it's good practice
        raise HTTPException(status_code=404, detail="User not found")
    
    await log_activity(
        request=request,
        action="admin_update_user",
        user_id=current_user["id"],
        user_name=current_user["full_name"],
        details={"updated_user_id": user_id, "update_data": user_update.dict(exclude_unset=True)}
    )

    return {"message": "User updated successfully"}

@api_router.post("/users/{user_id}/force-password-reset")
async def force_password_reset(
    user_id: str,
    request: Request,
    current_user: dict = Depends(require_role([UserRole.SUPER_ADMIN, UserRole.COACH_ADMIN]))
):
    """Force a password reset for a user (Admins only)."""
    target_user = await db.users.find_one({"id": user_id})
    if not target_user:
        raise HTTPException(status_code=404, detail="User not found")

    # Check permissions
    if current_user["role"] == UserRole.COACH_ADMIN:
        if target_user.get("branch_id") != current_user.get("branch_id"):
            raise HTTPException(status_code=403, detail="Coach Admins can only reset passwords for users in their own branch.")
        if target_user.get("role") not in [UserRole.STUDENT.value, UserRole.COACH.value]:
            raise HTTPException(status_code=403, detail="Coach Admins can only reset passwords for Students and Coaches.")

    # Generate a new temporary password
    new_password = secrets.token_urlsafe(8)
    hashed_password = hash_password(new_password)

    # Update the user's password in the database
    await db.users.update_one(
        {"id": user_id},
        {"$set": {"password": hashed_password, "updated_at": datetime.utcnow()}}
    )

    # Log the activity
    await log_activity(
        request=request,
        action="admin_force_password_reset",
        user_id=current_user["id"],
        user_name=current_user["full_name"],
        details={"reset_user_id": user_id, "reset_user_email": target_user["email"]}
    )

    # Send the new password to the user
    message = f"Your password has been reset by an administrator. Your new temporary password is: {new_password}"
    await send_sms(target_user["phone"], message)
    await send_whatsapp(target_user["phone"], message)

    return {"message": f"Password for user {target_user['full_name']} has been reset and sent to them."}

# TRANSFER REQUESTS
@api_router.post("/requests/transfer", status_code=status.HTTP_201_CREATED)
async def create_transfer_request(
    request_data: TransferRequestCreate,
    current_user: dict = Depends(require_role([UserRole.STUDENT]))
):
    """Create a new transfer request."""
    if not current_user.get("branch_id"):
        raise HTTPException(status_code=400, detail="User is not currently assigned to a branch.")

    transfer_request = TransferRequest(
        student_id=current_user["id"],
        current_branch_id=current_user["branch_id"],
        **request_data.dict()
    )
    await db.transfer_requests.insert_one(transfer_request.dict())
    return transfer_request

@api_router.get("/requests/transfer")
async def get_transfer_requests(
    status: Optional[TransferRequestStatus] = None,
    current_user: dict = Depends(require_role([UserRole.SUPER_ADMIN, UserRole.COACH_ADMIN]))
):
    """Get a list of transfer requests."""
    filter_query = {}
    if status:
        filter_query["status"] = status.value

    if current_user["role"] == UserRole.COACH_ADMIN:
        # Coach admins can only see requests for their branch
        filter_query["current_branch_id"] = current_user.get("branch_id")

    requests = await db.transfer_requests.find(filter_query).to_list(1000)
    return {"requests": serialize_doc(requests)}

@api_router.put("/requests/transfer/{request_id}")
async def update_transfer_request(
    request_id: str,
    update_data: TransferRequestUpdate,
    current_user: dict = Depends(require_role([UserRole.SUPER_ADMIN, UserRole.COACH_ADMIN]))
):
    """Update a transfer request (approve/reject)."""
    transfer_request = await db.transfer_requests.find_one({"id": request_id})
    if not transfer_request:
        raise HTTPException(status_code=404, detail="Transfer request not found")

    if current_user["role"] == UserRole.COACH_ADMIN:
        if transfer_request["current_branch_id"] != current_user.get("branch_id"):
            raise HTTPException(status_code=403, detail="You can only manage requests for your own branch.")

    updated_request = await db.transfer_requests.find_one_and_update(
        {"id": request_id},
        {"$set": {"status": update_data.status, "updated_at": datetime.utcnow()}},
        return_document=True
    )

    # If approved, update the student's branch
    if update_data.status == TransferRequestStatus.APPROVED:
        await db.users.update_one(
            {"id": transfer_request["student_id"]},
            {"$set": {"branch_id": transfer_request["new_branch_id"]}}
        )

    return {"message": "Transfer request updated successfully.", "request": serialize_doc(updated_request)}

@api_router.post("/requests/course-change", status_code=status.HTTP_201_CREATED)
async def create_course_change_request(
    request_data: CourseChangeRequestCreate,
    current_user: dict = Depends(require_role([UserRole.STUDENT]))
):
    """Create a new course change request."""
    # Find the current enrollment to ensure it belongs to the student and is active
    current_enrollment = await db.enrollments.find_one({
        "id": request_data.current_enrollment_id,
        "student_id": current_user["id"],
        "is_active": True
    })
    if not current_enrollment:
        raise HTTPException(status_code=404, detail="Active enrollment not found.")

    # Check if the new course exists
    new_course = await db.courses.find_one({"id": request_data.new_course_id})
    if not new_course:
        raise HTTPException(status_code=404, detail="New course not found.")

    course_change_request = CourseChangeRequest(
        student_id=current_user["id"],
        branch_id=current_enrollment["branch_id"],
        **request_data.dict()
    )
    await db.course_change_requests.insert_one(course_change_request.dict())
    return course_change_request

@api_router.get("/requests/course-change")
async def get_course_change_requests(
    status: Optional[CourseChangeRequestStatus] = None,
    current_user: dict = Depends(require_role([UserRole.SUPER_ADMIN, UserRole.COACH_ADMIN]))
):
    """Get a list of course change requests."""
    filter_query = {}
    if status:
        filter_query["status"] = status.value

    if current_user["role"] == UserRole.COACH_ADMIN:
        filter_query["branch_id"] = current_user.get("branch_id")

    requests = await db.course_change_requests.find(filter_query).to_list(1000)
    return {"requests": serialize_doc(requests)}

@api_router.put("/requests/course-change/{request_id}")
async def update_course_change_request(
    request_id: str,
    update_data: CourseChangeRequestUpdate,
    current_user: dict = Depends(require_role([UserRole.SUPER_ADMIN, UserRole.COACH_ADMIN]))
):
    """Update a course change request (approve/reject)."""
    change_request = await db.course_change_requests.find_one({"id": request_id})
    if not change_request:
        raise HTTPException(status_code=404, detail="Course change request not found")

    if current_user["role"] == UserRole.COACH_ADMIN:
        if change_request["branch_id"] != current_user.get("branch_id"):
            raise HTTPException(status_code=403, detail="You can only manage requests for your own branch.")

    updated_request = await db.course_change_requests.find_one_and_update(
        {"id": request_id},
        {"$set": {"status": update_data.status.value, "updated_at": datetime.utcnow()}},
        return_document=True
    )

    # If approved, perform the change
    if update_data.status == CourseChangeRequestStatus.APPROVED:
        # 1. Deactivate old enrollment
        await db.enrollments.update_one(
            {"id": change_request["current_enrollment_id"]},
            {"$set": {"is_active": False}}
        )

        # 2. Create new enrollment
        new_course = await db.courses.find_one({"id": change_request["new_course_id"]})
        if not new_course:
            # This should be rare, but handle it
            raise HTTPException(status_code=404, detail="New course not found during approval process.")

        # Determine fee for the new course
        fee_amount = new_course.get("base_fee")
        branch_pricing = new_course.get("branch_pricing", {})
        if change_request["branch_id"] in branch_pricing:
            fee_amount = branch_pricing[change_request["branch_id"]]

        # For simplicity, we'll start a new standard enrollment.
        # A real-world scenario might involve complex fee calculations.
        new_enrollment = Enrollment(
            student_id=change_request["student_id"],
            course_id=change_request["new_course_id"],
            branch_id=change_request["branch_id"],
            start_date=datetime.utcnow(),
            end_date=datetime.utcnow() + timedelta(days=new_course["duration_months"] * 30),
            fee_amount=fee_amount,
            admission_fee=0 # No new admission fee for a course change
        )
        await db.enrollments.insert_one(new_enrollment.dict())

    return {"message": "Course change request updated successfully.", "request": serialize_doc(updated_request)}

# BRANCH EVENT MANAGEMENT
@api_router.post("/events", status_code=status.HTTP_201_CREATED)
async def create_event(
    event_data: EventCreate,
    current_user: dict = Depends(require_role([UserRole.SUPER_ADMIN, UserRole.COACH_ADMIN]))
):
    """Create a new branch event."""
    if not current_user.get("branch_id"):
        raise HTTPException(status_code=400, detail="User is not assigned to a branch.")

    event = Event(
        **event_data.dict(),
        branch_id=current_user["branch_id"],
        created_by=current_user["id"]
    )
    await db.events.insert_one(event.dict())
    return event

@api_router.get("/events")
async def get_events(
    branch_id: str,
    current_user: dict = Depends(get_current_active_user)
):
    """Get events for a specific branch."""
    events = await db.events.find({"branch_id": branch_id}).to_list(1000)
    return {"events": serialize_doc(events)}

@api_router.put("/events/{event_id}")
async def update_event(
    event_id: str,
    event_data: EventCreate,
    current_user: dict = Depends(require_role([UserRole.SUPER_ADMIN, UserRole.COACH_ADMIN]))
):
    """Update a branch event."""
    event = await db.events.find_one({"id": event_id})
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")

    if event["branch_id"] != current_user.get("branch_id"):
        raise HTTPException(status_code=403, detail="You can only manage events for your own branch.")

    await db.events.update_one(
        {"id": event_id},
        {"$set": event_data.dict()}
    )
    return {"message": "Event updated successfully"}

@api_router.delete("/events/{event_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_event(
    event_id: str,
    current_user: dict = Depends(require_role([UserRole.SUPER_ADMIN, UserRole.COACH_ADMIN]))
):
    """Delete a branch event."""
    event = await db.events.find_one({"id": event_id})
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")

    if event["branch_id"] != current_user.get("branch_id"):
        raise HTTPException(status_code=403, detail="You can only manage events for your own branch.")

    await db.events.delete_one({"id": event_id})
    return


@api_router.delete("/users/{user_id}")
async def deactivate_user(
    user_id: str,
    request: Request,
    current_user: dict = Depends(require_role([UserRole.SUPER_ADMIN]))
):
    """Deactivate user (Super Admin only)"""
    result = await db.users.update_one(
        {"id": user_id},
        {"$set": {"is_active": False, "updated_at": datetime.utcnow()}}
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="User not found")
    
    await log_activity(
        request=request,
        action="admin_deactivate_user",
        user_id=current_user["id"],
        user_name=current_user["full_name"],
        details={"deactivated_user_id": user_id}
    )

    return {"message": "User deactivated successfully"}

# BRANCH MANAGEMENT ENDPOINTS
@api_router.post("/branches")
async def create_branch(
    branch_data: BranchCreate,
    current_user: dict = Depends(require_role([UserRole.SUPER_ADMIN]))
):
    """Create new branch"""
    branch = Branch(**branch_data.dict())
    await db.branches.insert_one(branch.dict())
    return {"message": "Branch created successfully", "branch_id": branch.id}

@api_router.get("/branches")
async def get_branches(
    skip: int = 0,
    limit: int = 50,
    current_user: dict = Depends(get_current_active_user)
):
    """Get all branches"""
    branches = await db.branches.find({"is_active": True}).skip(skip).limit(limit).to_list(length=limit)
    return {"branches": serialize_doc(branches)}

@api_router.get("/branches/{branch_id}")
async def get_branch(
    branch_id: str,
    current_user: dict = Depends(get_current_active_user)
):
    """Get branch by ID"""
    branch = await db.branches.find_one({"id": branch_id})
    if not branch:
        raise HTTPException(status_code=404, detail="Branch not found")
    return serialize_doc(branch)

@api_router.put("/branches/{branch_id}")
async def update_branch(
    branch_id: str,
    branch_update: BranchUpdate,
    current_user: dict = Depends(require_role([UserRole.SUPER_ADMIN, UserRole.COACH_ADMIN]))
):
    """Update branch"""
    # Coach Admin permission check
    if current_user["role"] == UserRole.COACH_ADMIN:
        if current_user.get("branch_id") != branch_id:
            raise HTTPException(status_code=403, detail="You can only update your own branch.")
        # Restrict fields a Coach Admin can update
        update_dict = branch_update.dict(exclude_unset=True)
        restricted_fields = ["manager_id", "is_active"]
        for field in restricted_fields:
            if field in update_dict:
                raise HTTPException(status_code=403, detail=f"You do not have permission to update the '{field}' field.")

    update_data = {k: v for k, v in branch_update.dict(exclude_unset=True).items()}
    if not update_data:
        raise HTTPException(status_code=400, detail="No update data provided")

    update_data["updated_at"] = datetime.utcnow()
    
    result = await db.branches.update_one(
        {"id": branch_id},
        {"$set": update_data}
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Branch not found")
    
    return {"message": "Branch updated successfully"}

@api_router.post("/branches/{branch_id}/holidays", status_code=status.HTTP_201_CREATED)
async def create_holiday(
    branch_id: str,
    holiday_data: HolidayCreate,
    current_user: dict = Depends(require_role([UserRole.SUPER_ADMIN, UserRole.COACH_ADMIN]))
):
    """Create a new holiday for a branch."""
    if current_user["role"] == UserRole.COACH_ADMIN and current_user.get("branch_id") != branch_id:
        raise HTTPException(status_code=403, detail="You can only add holidays to your own branch.")

    holiday = Holiday(
        **holiday_data.dict(),
        branch_id=branch_id
    )
    # Convert date to datetime for MongoDB serialization
    holiday_dict = holiday.dict()
    holiday_dict["date"] = datetime.combine(holiday_dict["date"], datetime.min.time())

    await db.holidays.insert_one(holiday_dict)
    return holiday

@api_router.get("/branches/{branch_id}/holidays")
async def get_holidays(
    branch_id: str,
    current_user: dict = Depends(get_current_active_user)
):
    """Get all holidays for a specific branch."""
    holidays = await db.holidays.find({"branch_id": branch_id}).to_list(1000)
    return {"holidays": serialize_doc(holidays)}

@api_router.delete("/branches/{branch_id}/holidays/{holiday_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_holiday(
    branch_id: str,
    holiday_id: str,
    current_user: dict = Depends(require_role([UserRole.SUPER_ADMIN, UserRole.COACH_ADMIN]))
):
    """Delete a holiday for a branch."""
    if current_user["role"] == UserRole.COACH_ADMIN and current_user.get("branch_id") != branch_id:
        raise HTTPException(status_code=403, detail="You can only delete holidays from your own branch.")

    result = await db.holidays.delete_one({"id": holiday_id, "branch_id": branch_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Holiday not found")
    return

# COURSE MANAGEMENT ENDPOINTS
@api_router.post("/courses")
async def create_course(
    course_data: CourseCreate,
    current_user: dict = Depends(require_role([UserRole.SUPER_ADMIN]))
):
    """Create new course"""
    course = Course(**course_data.dict())
    await db.courses.insert_one(course.dict())
    return {"message": "Course created successfully", "course_id": course.id}

@api_router.get("/courses")
async def get_courses(
    branch_id: Optional[str] = None,
    category: Optional[str] = None,
    level: Optional[str] = None,
    skip: int = 0,
    limit: int = 50,
    current_user: dict = Depends(get_current_active_user)
):
    """Get courses"""
    filter_query = {"is_active": True}
    
    if category:
        filter_query["category"] = category
    if level:
        filter_query["level"] = level

    courses = await db.courses.find(filter_query).skip(skip).limit(limit).to_list(length=limit)
    
    # Filter by branch pricing if branch_id provided
    if branch_id:
        courses = [c for c in courses if branch_id in c.get("branch_pricing", {})]
    
    return {"courses": serialize_doc(courses)}

@api_router.put("/courses/{course_id}")
async def update_course(
    course_id: str,
    course_update: CourseUpdate,
    current_user: dict = Depends(require_role([UserRole.SUPER_ADMIN, UserRole.COACH_ADMIN]))
):
    """Update course"""
    update_data = {k: v for k, v in course_update.dict().items() if v is not None}
    update_data["updated_at"] = datetime.utcnow()
    
    result = await db.courses.update_one(
        {"id": course_id},
        {"$set": update_data}
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Course not found")
    
    return {"message": "Course updated successfully"}

@api_router.get("/courses/{course_id}/stats")
async def get_course_stats(
    course_id: str,
    current_user: dict = Depends(require_role([UserRole.SUPER_ADMIN, UserRole.COACH_ADMIN]))
):
    """Get statistics for a specific course."""
    course = await db.courses.find_one({"id": course_id})
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")

    active_enrollments = await db.enrollments.count_documents({"course_id": course_id, "is_active": True})

    stats = {
        "course_details": serialize_doc(course),
        "active_enrollments": active_enrollments
    }
    return stats

# STUDENT ENROLLMENT ENDPOINTS
@api_router.post("/enrollments")
async def create_enrollment(
    enrollment_data: EnrollmentCreate,
    current_user: dict = Depends(require_role([UserRole.SUPER_ADMIN, UserRole.COACH_ADMIN]))
):
    """Create student enrollment"""
    # Validate student, course, and branch exist
    student = await db.users.find_one({"id": enrollment_data.student_id, "role": "student"})
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    
    course = await db.courses.find_one({"id": enrollment_data.course_id})
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    
    branch = await db.branches.find_one({"id": enrollment_data.branch_id})
    if not branch:
        raise HTTPException(status_code=404, detail="Branch not found")
    
    # Calculate end date
    end_date = enrollment_data.start_date + timedelta(days=course["duration_months"] * 30)
    
    enrollment = Enrollment(
        **enrollment_data.dict(),
        end_date=end_date,
        next_due_date=enrollment_data.start_date + timedelta(days=30)
    )
    
    await db.enrollments.insert_one(enrollment.dict())
    
    # Create initial payment records
    admission_payment = Payment(
        student_id=enrollment_data.student_id,
        enrollment_id=enrollment.id,
        amount=enrollment_data.admission_fee,
        payment_type="admission_fee",
        payment_method="pending",
        payment_status=PaymentStatus.PENDING,
        due_date=datetime.utcnow() + timedelta(days=7)
    )
    
    course_payment = Payment(
        student_id=enrollment_data.student_id,
        enrollment_id=enrollment.id,
        amount=enrollment_data.fee_amount,
        payment_type="course_fee",
        payment_method="pending", 
        payment_status=PaymentStatus.PENDING,
        due_date=enrollment_data.start_date
    )
    
    await db.payments.insert_many([admission_payment.dict(), course_payment.dict()])
    
    # Send enrollment confirmation
    await send_whatsapp(student["phone"], f"Welcome! You're enrolled in {course['name']}. Start date: {enrollment_data.start_date.date()}")
    
    return {"message": "Enrollment created successfully", "enrollment_id": enrollment.id}

@api_router.get("/enrollments")
async def get_enrollments(
    student_id: Optional[str] = None,
    course_id: Optional[str] = None,
    branch_id: Optional[str] = None,
    skip: int = 0,
    limit: int = 50,
    current_user: dict = Depends(get_current_active_user)
):
    """Get enrollments with filtering"""
    filter_query = {}
    if student_id:
        filter_query["student_id"] = student_id
    if course_id:
        filter_query["course_id"] = course_id
    if branch_id:
        filter_query["branch_id"] = branch_id
    
    # Role-based filtering
    if current_user["role"] == "student":
        filter_query["student_id"] = current_user["id"]
    elif current_user["role"] == "coach_admin" and current_user.get("branch_id"):
        filter_query["branch_id"] = current_user["branch_id"]
    
    enrollments = await db.enrollments.find(filter_query).skip(skip).limit(limit).to_list(length=limit)
    return {"enrollments": serialize_doc(enrollments)}

@api_router.get("/students/{student_id}/courses")
async def get_student_courses(
    student_id: str,
    current_user: dict = Depends(get_current_active_user)
):
    """Get student's enrolled courses"""
    # Check permission
    if current_user["role"] == "student" and current_user["id"] != student_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    enrollments = await db.enrollments.find({"student_id": student_id, "is_active": True}).to_list(length=100)
    
    # Enrich with course details
    course_ids = [e["course_id"] for e in enrollments]
    courses = await db.courses.find({"id": {"$in": course_ids}}).to_list(length=100)
    
    course_dict = {c["id"]: c for c in courses}
    
    result = []
    for enrollment in enrollments:
        course = course_dict.get(enrollment["course_id"])
        if course:
            result.append({
                "enrollment": enrollment,
                "course": course
            })
    
    return {"enrolled_courses": serialize_doc(result)}

@api_router.post("/students/enroll", status_code=status.HTTP_201_CREATED)
async def student_enroll_in_course(
    enrollment_data: StudentEnrollmentCreate,
    current_user: dict = Depends(require_role([UserRole.STUDENT]))
):
    """Allow a student to enroll themselves in a course."""
    student_id = current_user["id"]

    # Validate student, course, and branch exist
    student = await db.users.find_one({"id": student_id, "role": "student"})
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    course = await db.courses.find_one({"id": enrollment_data.course_id})
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")

    branch = await db.branches.find_one({"id": enrollment_data.branch_id})
    if not branch:
        raise HTTPException(status_code=404, detail="Branch not found")

    # Check if student is already enrolled in this course
    existing_enrollment = await db.enrollments.find_one({
        "student_id": student_id,
        "course_id": enrollment_data.course_id,
        "is_active": True
    })
    if existing_enrollment:
        raise HTTPException(status_code=400, detail="Student already enrolled in this course.")

    # Determine fee_amount based on branch pricing
    admission_fee = 500.0 # Fixed admission fee
    fee_amount = course["base_fee"]
    if enrollment_data.branch_id in course.get("branch_pricing", {}):
        fee_amount = course["branch_pricing"][enrollment_data.branch_id]

    # Calculate end date
    end_date = enrollment_data.start_date + timedelta(days=course["duration_months"] * 30)

    enrollment = Enrollment(
        student_id=student_id,
        course_id=enrollment_data.course_id,
        branch_id=enrollment_data.branch_id,
        start_date=enrollment_data.start_date,
        end_date=end_date,
        fee_amount=fee_amount,
        admission_fee=admission_fee,
        next_due_date=enrollment_data.start_date + timedelta(days=30)
    )

    await db.enrollments.insert_one(enrollment.dict())

    # Create initial payment records (pending)
    admission_payment = Payment(
        student_id=student_id,
        enrollment_id=enrollment.id,
        amount=admission_fee,
        payment_type="admission_fee",
        payment_method="pending",
        payment_status=PaymentStatus.PENDING,
        due_date=datetime.utcnow() + timedelta(days=7)
    )

    course_payment = Payment(
        student_id=student_id,
        enrollment_id=enrollment.id,
        amount=fee_amount,
        payment_type="course_fee",
        payment_method="pending",
        payment_status=PaymentStatus.PENDING,
        due_date=enrollment_data.start_date
    )

    await db.payments.insert_many([admission_payment.dict(), course_payment.dict()])

    # Send enrollment confirmation
    await send_whatsapp(student["phone"], f"Welcome! You're enrolled in {course['name']}. Start date: {enrollment_data.start_date.date()}")

    return {"message": "Enrollment created successfully", "enrollment_id": enrollment.id}

@api_router.post("/students/payments", status_code=status.HTTP_201_CREATED)
async def student_process_payment(
    payment_data: StudentPaymentCreate,
    current_user: dict = Depends(require_role([UserRole.STUDENT]))
):
    """Allow a student to process a payment for their enrollment."""
    student_id = current_user["id"]

    # Validate enrollment and payment
    enrollment = await db.enrollments.find_one({"id": payment_data.enrollment_id, "student_id": student_id})
    if not enrollment:
        raise HTTPException(status_code=404, detail="Enrollment not found or does not belong to you.")

    # Find the pending payment for this enrollment
    # This assumes there's a specific pending payment the student is trying to clear
    # In a real system, you might have a more complex payment reconciliation logic
    pending_payment = await db.payments.find_one({
        "enrollment_id": payment_data.enrollment_id,
        "student_id": student_id,
        "payment_status": PaymentStatus.PENDING.value,
        "amount": payment_data.amount # Ensure the amount matches
    })

    if not pending_payment:
        raise HTTPException(status_code=400, detail="No matching pending payment found for this enrollment and amount.")

    # Simulate payment gateway interaction (update payment status)
    update_data = {
        "payment_status": PaymentStatus.PAID,
        "payment_method": payment_data.payment_method,
        "transaction_id": payment_data.transaction_id,
        "payment_date": datetime.utcnow(),
        "notes": payment_data.notes,
        "updated_at": datetime.utcnow()
    }

    result = await db.payments.update_one(
        {"id": pending_payment["id"]},
        {"$set": update_data}
    )

    if result.matched_count == 0:
        raise HTTPException(status_code=500, detail="Failed to update payment status.")

    # Update enrollment payment status if needed (e.g., if all payments are cleared)
    # This logic might need to be more sophisticated in a real app
    await db.enrollments.update_one(
        {"id": enrollment["id"]},
        {"$set": {"payment_status": PaymentStatus.PAID}} # Simplified: mark enrollment paid if this payment clears it
    )

    # Send payment confirmation
    await send_whatsapp(current_user["phone"], f"Payment of ₹{payment_data.amount} received for enrollment {payment_data.enrollment_id}. Thank you!")

    return {"message": "Payment processed successfully", "payment_id": pending_payment["id"]}

# ATTENDANCE SYSTEM ENDPOINTS
@api_router.post("/attendance/biometric")
async def biometric_attendance(
    attendance_data: BiometricAttendance
):
    """
    Record attendance from a biometric device.
    This is a mock implementation and assumes the device sends a unique biometric ID.
    """
    # 1. Find the user associated with the biometric ID
    user = await db.users.find_one({"biometric_id": attendance_data.biometric_id, "is_active": True})
    if not user:
        # In a real system, you might log this failed attempt.
        raise HTTPException(status_code=404, detail="User with this biometric ID not found.")

    student_id = user["id"]

    # 2. Find the student's current active enrollment
    # This is a simplification. A real system might need more logic to determine the correct course.
    enrollment = await db.enrollments.find_one({"student_id": student_id, "is_active": True})
    if not enrollment:
        raise HTTPException(status_code=400, detail="No active enrollment found for this student.")

    # 3. Check if attendance has already been marked for this course today
    today = attendance_data.timestamp.date()
    start_of_day = datetime.combine(today, datetime.min.time())
    end_of_day = datetime.combine(today, datetime.max.time())

    existing_attendance = await db.attendance.find_one({
        "student_id": student_id,
        "course_id": enrollment["course_id"],
        "attendance_date": {"$gte": start_of_day, "$lte": end_of_day}
    })
    if existing_attendance:
        return {"message": "Attendance already marked for today."}

    # 4. Create the attendance record
    attendance = Attendance(
        student_id=student_id,
        course_id=enrollment["course_id"],
        branch_id=enrollment["branch_id"],
        attendance_date=attendance_data.timestamp,
        check_in_time=attendance_data.timestamp,
        method=AttendanceMethod.BIOMETRIC,
        notes=f"Biometric check-in from device {attendance_data.device_id}"
    )

    await db.attendance.insert_one(attendance.dict())

    return {"message": "Attendance marked successfully", "attendance_id": attendance.id}

@api_router.post("/attendance/generate-qr")
async def generate_attendance_qr(
    course_id: str,
    branch_id: str,
    valid_minutes: int = 30,
    current_user: dict = Depends(require_role([UserRole.SUPER_ADMIN, UserRole.COACH_ADMIN, UserRole.COACH]))
):
    """Generate QR code for attendance"""
    # Validate course and branch
    course = await db.courses.find_one({"id": course_id})
    branch = await db.branches.find_one({"id": branch_id})
    
    if not course or not branch:
        raise HTTPException(status_code=404, detail="Course or branch not found")
    
    # Generate unique QR data
    qr_data = f"attendance:{course_id}:{branch_id}:{int(datetime.utcnow().timestamp())}"
    qr_code_image = generate_qr_code(qr_data)
    
    # Store QR session
    qr_session = QRCodeSession(
        branch_id=branch_id,
        course_id=course_id,
        qr_code=qr_data,
        qr_code_data=qr_code_image,
        generated_by=current_user["id"],
        valid_until=datetime.utcnow() + timedelta(minutes=valid_minutes)
    )
    
    await db.qr_sessions.insert_one(qr_session.dict())
    
    return {
        "qr_code_id": qr_session.id,
        "qr_code_data": qr_code_image,
        "valid_until": qr_session.valid_until,
        "course_name": course["name"]
    }

@api_router.post("/attendance/scan-qr")
async def scan_qr_attendance(
    qr_code: str,
    current_user: dict = Depends(get_current_active_user)
):
    """Mark attendance via QR code scan"""
    if current_user["role"] != "student":
        raise HTTPException(status_code=403, detail="Only students can scan QR codes")
    
    # Find valid QR session
    qr_session = await db.qr_sessions.find_one({
        "qr_code": qr_code,
        "is_active": True,
        "valid_until": {"$gt": datetime.utcnow()}
    })
    
    if not qr_session:
        raise HTTPException(status_code=400, detail="Invalid or expired QR code")
    
    # Check if student is enrolled in this course
    enrollment = await db.enrollments.find_one({
        "student_id": current_user["id"],
        "course_id": qr_session["course_id"],
        "branch_id": qr_session["branch_id"],
        "is_active": True
    })
    
    if not enrollment:
        raise HTTPException(status_code=400, detail="You are not enrolled in this course")
    
    # Check if already marked attendance today
    today = datetime.utcnow().date()
    existing_attendance = await db.attendance.find_one({
        "student_id": current_user["id"],
        "course_id": qr_session["course_id"],
        "attendance_date": {
            "$gte": datetime.combine(today, datetime.min.time()),
            "$lt": datetime.combine(today + timedelta(days=1), datetime.min.time())
        }
    })
    
    if existing_attendance:
        raise HTTPException(status_code=400, detail="Attendance already marked for today")
    
    # Create attendance record
    attendance = Attendance(
        student_id=current_user["id"],
        course_id=qr_session["course_id"],
        branch_id=qr_session["branch_id"],
        attendance_date=datetime.utcnow(),
        check_in_time=datetime.utcnow(),
        method=AttendanceMethod.QR_CODE,
        qr_code_used=qr_code
    )
    
    await db.attendance.insert_one(attendance.dict())
    
    return {"message": "Attendance marked successfully", "attendance_id": attendance.id}

@api_router.post("/attendance/manual")
async def manual_attendance(
    attendance_data: AttendanceCreate,
    current_user: dict = Depends(require_role([UserRole.SUPER_ADMIN, UserRole.COACH_ADMIN, UserRole.COACH]))
):
    """Manually mark attendance"""
    attendance = Attendance(
        **attendance_data.dict(),
        check_in_time=datetime.utcnow(),
        marked_by=current_user["id"]
    )
    
    await db.attendance.insert_one(attendance.dict())
    return {"message": "Attendance marked successfully", "attendance_id": attendance.id}

@api_router.get("/attendance/reports")
async def get_attendance_reports(
    student_id: Optional[str] = None,
    course_id: Optional[str] = None,
    branch_id: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    current_user: dict = Depends(get_current_active_user)
):
    """Get attendance reports"""
    filter_query = {}
    
    if student_id:
        filter_query["student_id"] = student_id
    if course_id:
        filter_query["course_id"] = course_id
    if branch_id:
        filter_query["branch_id"] = branch_id
    
    if start_date and end_date:
        filter_query["attendance_date"] = {"$gte": start_date, "$lte": end_date}
    
    # Role-based filtering
    if current_user["role"] == "student":
        filter_query["student_id"] = current_user["id"]
    elif current_user["role"] == "coach_admin" and current_user.get("branch_id"):
        filter_query["branch_id"] = current_user["branch_id"]
    
    attendance_records = await db.attendance.find(filter_query).to_list(length=1000)
    return {"attendance_records": serialize_doc(attendance_records)}

@api_router.get("/attendance/reports/export")
async def export_attendance_reports(
    student_id: Optional[str] = None,
    course_id: Optional[str] = None,
    branch_id: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    current_user: dict = Depends(get_current_active_user)
):
    """Export attendance reports as a CSV file."""
    filter_query = {}

    if student_id:
        filter_query["student_id"] = student_id
    if course_id:
        filter_query["course_id"] = course_id
    if branch_id:
        filter_query["branch_id"] = branch_id

    if start_date and end_date:
        filter_query["attendance_date"] = {"$gte": start_date, "$lte": end_date}

    if current_user["role"] == "student":
        filter_query["student_id"] = current_user["id"]
    elif current_user["role"] == "coach_admin" and current_user.get("branch_id"):
        filter_query["branch_id"] = current_user["branch_id"]

    attendance_records = await db.attendance.find(filter_query).to_list(length=None)

    output = io.StringIO()
    writer = csv.writer(output)

    headers = ["attendance_id", "student_id", "course_id", "branch_id", "attendance_date", "check_in_time", "method", "is_present", "notes"]
    writer.writerow(headers)

    for record in attendance_records:
        row = [
            record.get("id"),
            record.get("student_id"),
            record.get("course_id"),
            record.get("branch_id"),
            record.get("attendance_date"),
            record.get("check_in_time"),
            record.get("method"),
            record.get("is_present"),
            record.get("notes")
        ]
        writer.writerow(row)

    output.seek(0)

    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename=attendance_report_{datetime.now().date()}.csv"}
    )

# PAYMENT MANAGEMENT ENDPOINTS
@api_router.post("/payments")
async def process_payment(
    payment_data: PaymentCreate,
    current_user: dict = Depends(require_role([UserRole.SUPER_ADMIN, UserRole.COACH_ADMIN]))
):
    """Process payment"""
    payment = Payment(
        **payment_data.dict(),
        payment_status=PaymentStatus.PAID if payment_data.transaction_id else PaymentStatus.PENDING,
        payment_date=datetime.utcnow() if payment_data.transaction_id else None
    )
    
    await db.payments.insert_one(payment.dict())
    
    # Update enrollment payment status if needed
    if payment.payment_status == PaymentStatus.PAID:
        enrollment = await db.enrollments.find_one({"id": payment.enrollment_id})
        if enrollment:
            # Calculate next due date
            next_due = datetime.utcnow() + timedelta(days=30)
            await db.enrollments.update_one(
                {"id": payment.enrollment_id},
                {"$set": {"payment_status": PaymentStatus.PAID, "next_due_date": next_due}}
            )
    
    # Send payment confirmation
    student = await db.users.find_one({"id": payment.student_id})
    if student:
        message = f"Payment received: ₹{payment.amount} for {payment.payment_type}. Thank you!"
        await send_whatsapp(student["phone"], message)
    
    return {"message": "Payment processed successfully", "payment_id": payment.id}

class PaymentUpdate(BaseModel):
    payment_status: PaymentStatus
    transaction_id: Optional[str] = None
    notes: Optional[str] = None

@api_router.put("/payments/{payment_id}")
async def update_payment(
    payment_id: str,
    payment_update: PaymentUpdate,
    current_user: dict = Depends(require_role([UserRole.SUPER_ADMIN, UserRole.COACH_ADMIN]))
):
    """Update a payment's status."""
    update_data = payment_update.dict(exclude_unset=True)
    update_data["updated_at"] = datetime.utcnow()
    if payment_update.payment_status == PaymentStatus.PAID:
        update_data["payment_date"] = datetime.utcnow()

    result = await db.payments.update_one(
        {"id": payment_id},
        {"$set": update_data}
    )

    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Payment not found")

    return {"message": "Payment updated successfully"}

@api_router.post("/payments/{payment_id}/proof")
async def submit_payment_proof(
    payment_id: str,
    proof_data: PaymentProof,
    current_user: dict = Depends(require_role([UserRole.STUDENT]))
):
    """Submit proof of payment for an offline transaction."""
    payment = await db.payments.find_one({"id": payment_id, "student_id": current_user["id"]})
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found or you do not have permission to update it.")

    await db.payments.update_one(
        {"id": payment_id},
        {"$set": {"payment_proof": proof_data.proof, "updated_at": datetime.utcnow()}}
    )
    return {"message": "Payment proof submitted successfully."}

@api_router.get("/payments")
async def get_payments(
    student_id: Optional[str] = None,
    enrollment_id: Optional[str] = None,
    payment_status: Optional[PaymentStatus] = None,
    skip: int = 0,
    limit: int = 50,
    current_user: dict = Depends(get_current_active_user)
):
    """Get payments with filtering"""
    filter_query = {}
    
    if student_id:
        filter_query["student_id"] = student_id
    if enrollment_id:
        filter_query["enrollment_id"] = enrollment_id
    if payment_status:
        filter_query["payment_status"] = payment_status.value
    
    # Role-based filtering
    if current_user["role"] == "student":
        filter_query["student_id"] = current_user["id"]
    
    payments = await db.payments.find(filter_query).skip(skip).limit(limit).to_list(length=limit)
    return {"payments": serialize_doc(payments)}

@api_router.get("/payments/dues")
async def get_outstanding_dues(
    branch_id: Optional[str] = None,
    current_user: dict = Depends(get_current_active_user)
):
    """Get outstanding dues"""
    filter_query = {"payment_status": PaymentStatus.PENDING.value, "due_date": {"$lt": datetime.utcnow()}}
    
    if current_user["role"] == "student":
        filter_query["student_id"] = current_user["id"]
    
    overdue_payments = await db.payments.find(filter_query).to_list(length=1000)
    
    # Group by student
    dues_by_student = {}
    for payment in overdue_payments:
        student_id = payment["student_id"]
        if student_id not in dues_by_student:
            dues_by_student[student_id] = {"total_amount": 0, "payments": []}
        dues_by_student[student_id]["total_amount"] += payment["amount"]
        dues_by_student[student_id]["payments"].append(payment)
    
    return {"outstanding_dues": serialize_doc(dues_by_student)}

@api_router.post("/payments/send-reminders")
async def send_payment_reminders(
    current_user: dict = Depends(require_role([UserRole.SUPER_ADMIN, UserRole.COACH_ADMIN]))
):
    """
    Find all pending/overdue payments and send reminders.
    """
    # Find payments that are pending or overdue
    due_payments_cursor = db.payments.find({
        "payment_status": {"$in": [PaymentStatus.PENDING.value, PaymentStatus.OVERDUE.value]}
    })
    due_payments = await due_payments_cursor.to_list(length=None)

    if not due_payments:
        return {"message": "No due payments found to send reminders for."}

    reminders_sent = 0
    for payment in due_payments:
        student = await db.users.find_one({"id": payment["student_id"]})
        if student:
            message = (
                f"Hi {student['full_name']}, this is a friendly reminder that your payment of "
                f"₹{payment['amount']} for enrollment {payment['enrollment_id']} is due on "
                f"{payment['due_date'].date()}. Thank you."
            )
            await send_sms(student["phone"], message)
            await send_whatsapp(student["phone"], message)
            reminders_sent += 1

    return {"message": f"Successfully sent {reminders_sent} payment reminders."}

# PRODUCTS/ACCESSORIES MANAGEMENT
@api_router.post("/products")
async def create_product(
    product_data: ProductCreate,
    current_user: dict = Depends(require_role([UserRole.SUPER_ADMIN]))
):
    """Create product"""
    product = Product(**product_data.dict())
    await db.products.insert_one(product.dict())
    return {"message": "Product created successfully", "product_id": product.id}

@api_router.get("/products")
async def get_products(
    branch_id: Optional[str] = None,
    category: Optional[str] = None,
    current_user: dict = Depends(get_current_active_user)
):
    """Get products catalog"""
    filter_query = {"is_active": True}
    
    if category:
        filter_query["category"] = category
    
    products = await db.products.find(filter_query).to_list(length=1000)
    
    # Filter by branch availability if specified
    if branch_id:
        products = [p for p in products if branch_id in p.get("branch_availability", {})]
    
    return {"products": serialize_doc(products)}

@api_router.put("/products/{product_id}")
async def update_product(
    product_id: str,
    product_update: ProductUpdate,
    current_user: dict = Depends(require_role([UserRole.SUPER_ADMIN]))
):
    """Update product details (Super Admin only)"""
    update_data = {k: v for k, v in product_update.dict(exclude_unset=True).items()}
    if not update_data:
        raise HTTPException(status_code=400, detail="No update data provided")

    update_data["updated_at"] = datetime.utcnow()

    result = await db.products.update_one(
        {"id": product_id},
        {"$set": update_data}
    )

    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Product not found")

    return {"message": "Product updated successfully"}

@api_router.post("/products/{product_id}/restock")
async def restock_product(
    product_id: str,
    restock_data: RestockRequest,
    current_user: dict = Depends(require_role([UserRole.SUPER_ADMIN, UserRole.COACH_ADMIN]))
):
    """Restock a product at a specific branch."""
    # Coach Admins can only restock for their own branch
    if current_user["role"] == UserRole.COACH_ADMIN:
        if restock_data.branch_id != current_user.get("branch_id"):
            raise HTTPException(status_code=403, detail="You can only restock products for your own branch.")

    # Find the product
    product = await db.products.find_one({"id": product_id})
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    # Use $inc to atomically update the stock count
    update_result = await db.products.update_one(
        {"id": product_id},
        {"$inc": {f"branch_availability.{restock_data.branch_id}": restock_data.quantity}}
    )

    if update_result.matched_count == 0:
        # This should be rare due to the check above
        raise HTTPException(status_code=404, detail="Product not found during update.")

    return {"message": f"Successfully added {restock_data.quantity} units to product {product['name']} at branch {restock_data.branch_id}."}

@api_router.get("/products/purchases")
async def get_product_purchases(
    student_id: Optional[str] = None,
    branch_id: Optional[str] = None,
    skip: int = 0,
    limit: int = 50,
    current_user: dict = Depends(get_current_active_user)
):
    """Get product purchases with filtering"""
    filter_query = {}
    if student_id:
        filter_query["student_id"] = student_id
    if branch_id:
        filter_query["branch_id"] = branch_id

    if current_user["role"] == UserRole.STUDENT:
        filter_query["student_id"] = current_user["id"]
    elif current_user["role"] == UserRole.COACH_ADMIN:
        filter_query["branch_id"] = current_user.get("branch_id")

    purchases = await db.product_purchases.find(filter_query).skip(skip).limit(limit).to_list(length=limit)
    return {"purchases": serialize_doc(purchases)}

@api_router.post("/products/purchase")
async def purchase_product(
    purchase_data: ProductPurchaseCreate,
    current_user: dict = Depends(get_current_active_user)
):
    """Record offline product purchase"""
    # Validate product and stock
    product = await db.products.find_one({"id": purchase_data.product_id})
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    branch_stock = product.get("branch_availability", {}).get(purchase_data.branch_id, 0)
    if branch_stock < purchase_data.quantity:
        raise HTTPException(status_code=400, detail="Insufficient stock")
    
    # Create purchase record
    purchase = ProductPurchase(
        **purchase_data.dict(),
        unit_price=product["price"],
        total_amount=product["price"] * purchase_data.quantity
    )
    
    await db.product_purchases.insert_one(purchase.dict())
    
    # Update stock
    new_stock = branch_stock - purchase_data.quantity
    await db.products.update_one(
        {"id": purchase_data.product_id},
        {"$set": {f"branch_availability.{purchase_data.branch_id}": new_stock}}
    )
    
    # Check for stock alert
    await check_and_send_stock_alert(product, purchase_data.branch_id, new_stock)

    return {"message": "Purchase recorded successfully", "purchase_id": purchase.id, "total_amount": purchase.total_amount}

class StudentProductPurchaseCreate(BaseModel):
    product_id: str
    quantity: int
    payment_method: str # e.g., "online", "upi", "card"

@api_router.post("/students/products/purchase", status_code=status.HTTP_201_CREATED)
async def student_purchase_product(
    purchase_data: StudentProductPurchaseCreate,
    current_user: dict = Depends(require_role([UserRole.STUDENT]))
):
    """Allow a student to purchase a product online."""
    student_id = current_user["id"]
    branch_id = current_user.get("branch_id")

    if not branch_id:
        raise HTTPException(status_code=400, detail="Student is not assigned to a branch.")

    # Validate product and stock
    product = await db.products.find_one({"id": purchase_data.product_id})
    if not product:
        raise HTTPException(status_code=404, detail="Product not found.")

    branch_stock = product.get("branch_availability", {}).get(branch_id, 0)
    if branch_stock < purchase_data.quantity:
        raise HTTPException(status_code=400, detail="Insufficient stock at your branch.")

    # Calculate total amount
    unit_price = product["price"]
    total_amount = unit_price * purchase_data.quantity

    # Create ProductPurchase record
    purchase = ProductPurchase(
        student_id=student_id,
        product_id=purchase_data.product_id,
        branch_id=branch_id,
        quantity=purchase_data.quantity,
        unit_price=unit_price,
        total_amount=total_amount,
        payment_method=purchase_data.payment_method,
        purchase_date=datetime.utcnow()
    )
    await db.product_purchases.insert_one(purchase.dict())

    # Update stock
    new_stock = branch_stock - purchase_data.quantity
    await db.products.update_one(
        {"id": purchase_data.product_id},
        {"$set": {f"branch_availability.{branch_id}": new_stock}}
    )

    # Check for stock alert
    await check_and_send_stock_alert(product, branch_id, new_stock)

    # Create Payment record for the purchase
    payment = Payment(
        student_id=student_id,
        enrollment_id="", # No enrollment for product purchases
        amount=total_amount,
        payment_type="accessory_purchase",
        payment_method=purchase_data.payment_method,
        payment_status=PaymentStatus.PAID, # Assuming online payment is immediately paid
        transaction_id=str(uuid.uuid4()), # Generate a dummy transaction ID
        due_date=datetime.utcnow(),
        notes=f"Online purchase of {purchase_data.quantity} x {product['name']}"
    )
    await db.payments.insert_one(payment.dict())

    # Send confirmation
    await send_whatsapp(current_user["phone"], f"Thank you for your purchase of {purchase_data.quantity} x {product['name']} for ₹{total_amount}. Your order is confirmed!")

    return {"message": "Product purchased successfully", "purchase_id": purchase.id, "total_amount": total_amount}

# COMPLAINTS & FEEDBACK SYSTEM
@api_router.post("/complaints")
async def create_complaint(
    complaint_data: ComplaintCreate,
    current_user: dict = Depends(require_role([UserRole.STUDENT]))
):
    """Submit complaint (Students only)"""
    complaint = Complaint(
        **complaint_data.dict(),
        student_id=current_user["id"],
        branch_id=current_user.get("branch_id") or ""
    )
    
    await db.complaints.insert_one(complaint.dict())
    
    # Notify admins
    admins = await db.users.find({"role": {"$in": ["super_admin", "coach_admin"]}}).to_list(length=100)
    for admin in admins:
        message = f"New complaint from {current_user['full_name']}: {complaint.subject}"
        await send_whatsapp(admin["phone"], message)
    
    return {"message": "Complaint submitted successfully", "complaint_id": complaint.id}

@api_router.get("/complaints")
async def get_complaints(
    status: Optional[ComplaintStatus] = None,
    category: Optional[str] = None,
    current_user: dict = Depends(get_current_active_user)
):
    """Get complaints"""
    filter_query = {}
    
    if status:
        filter_query["status"] = status.value
    if category:
        filter_query["category"] = category
    
    # Role-based filtering
    if current_user["role"] == "student":
        filter_query["student_id"] = current_user["id"]
    
    complaints = await db.complaints.find(filter_query).to_list(length=1000)
    return {"complaints": serialize_doc(complaints)}

@api_router.put("/complaints/{complaint_id}")
async def update_complaint(
    complaint_id: str,
    complaint_update: ComplaintUpdate,
    current_user: dict = Depends(require_role([UserRole.SUPER_ADMIN, UserRole.COACH_ADMIN]))
):
    """Update complaint status and notify the student."""
    # Get original complaint to find the student
    complaint = await db.complaints.find_one({"id": complaint_id})
    if not complaint:
        raise HTTPException(status_code=404, detail="Complaint not found")

    update_data = {k: v for k, v in complaint_update.dict(exclude_unset=True).items() if v is not None}
    update_data["updated_at"] = datetime.utcnow()
    
    result = await db.complaints.update_one(
        {"id": complaint_id},
        {"$set": update_data}
    )
    
    if result.matched_count == 0:
        # This check is now slightly redundant but safe
        raise HTTPException(status_code=404, detail="Complaint not found")
    
    # Send notification to the student
    if complaint_update.status:
        student = await db.users.find_one({"id": complaint["student_id"]})
        # This assumes a template with this name exists. It should be created in the DB.
        template = await db.notification_templates.find_one({"name": "complaint_status_update"})
        if student and template:
            body = template["body"].replace("{{subject}}", complaint["subject"]).replace("{{status}}", complaint_update.status.value)

            success = False
            if template["type"] == NotificationType.WHATSAPP.value:
                success = await send_whatsapp(student["phone"], body)
            elif template["type"] == NotificationType.SMS.value:
                success = await send_sms(student["phone"], body)

            log_entry = NotificationLog(
                user_id=student["id"],
                template_id=template["id"],
                type=template["type"],
                status="sent" if success else "failed",
                content=body
            )
            await db.notification_logs.insert_one(log_entry.dict())

    return {"message": "Complaint updated successfully"}

@api_router.post("/feedback/coaches")
async def rate_coach(
    rating_data: CoachRatingCreate,
    current_user: dict = Depends(require_role([UserRole.STUDENT]))
):
    """Rate and review coach"""
    if rating_data.rating < 1 or rating_data.rating > 5:
        raise HTTPException(status_code=400, detail="Rating must be between 1 and 5")
    
    rating = CoachRating(
        **rating_data.dict(),
        student_id=current_user["id"],
        branch_id=current_user.get("branch_id", "")
    )
    
    await db.coach_ratings.insert_one(rating.dict())
    return {"message": "Rating submitted successfully", "rating_id": rating.id}

@api_router.get("/coaches/{coach_id}/ratings")
async def get_coach_ratings(
    coach_id: str,
    current_user: dict = Depends(get_current_active_user)
):
    """Get all ratings for a specific coach."""
    ratings = await db.coach_ratings.find({"coach_id": coach_id}).to_list(1000)
    return {"ratings": serialize_doc(ratings)}

# SESSION BOOKING SYSTEM
@api_router.post("/sessions/book")
async def book_session(
    booking_data: SessionBookingCreate,
    current_user: dict = Depends(require_role([UserRole.STUDENT]))
):
    """Book individual session"""
    # Validate coach availability (simplified)
    existing_booking = await db.session_bookings.find_one({
        "coach_id": booking_data.coach_id,
        "session_date": booking_data.session_date,
        "status": {"$ne": SessionStatus.CANCELLED.value}
    })
    
    if existing_booking:
        raise HTTPException(status_code=400, detail="Coach not available at this time")
    
    booking = SessionBooking(
        **booking_data.dict(),
        student_id=current_user["id"]
    )
    
    await db.session_bookings.insert_one(booking.dict())
    
    # Create payment record
    payment = Payment(
        student_id=current_user["id"],
        enrollment_id="",  # No enrollment for individual sessions
        amount=booking.fee,
        payment_type="session_fee",
        payment_method="pending",
        payment_status=PaymentStatus.PENDING,
        due_date=booking.session_date
    )
    await db.payments.insert_one(payment.dict())
    
    return {"message": "Session booked successfully", "booking_id": booking.id, "fee": booking.fee}

@api_router.get("/sessions/my-bookings")
async def get_my_bookings(
    current_user: dict = Depends(require_role([UserRole.STUDENT]))
):
    """Get student's session bookings"""
    bookings = await db.session_bookings.find({"student_id": current_user["id"]}).to_list(length=1000)
    return {"bookings": serialize_doc(bookings)}

# REPORTING & ANALYTICS ENDPOINTS
@api_router.get("/admin/activity-logs")
async def get_activity_logs(
    request: Request,
    user_id: Optional[str] = None,
    action: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    skip: int = 0,
    limit: int = 100,
    current_user: dict = Depends(require_role([UserRole.SUPER_ADMIN]))
):
    """Get user activity logs (Super Admin only)"""
    filter_query = {}
    if user_id:
        filter_query["user_id"] = user_id
    if action:
        filter_query["action"] = action
    if start_date and end_date:
        filter_query["timestamp"] = {"$gte": start_date, "$lte": end_date}

    logs = await db.activity_logs.find(filter_query).sort("timestamp", -1).skip(skip).limit(limit).to_list(length=limit)
    total = await db.activity_logs.count_documents(filter_query)

    return {"logs": serialize_doc(logs), "total": total}

@api_router.get("/reports/dashboard")
async def get_dashboard_stats(
    branch_id: Optional[str] = None,
    current_user: dict = Depends(get_current_active_user)
):
    """Get dashboard statistics"""
    stats = {}
    
    # Filter by role and branch
    filter_query = {}
    if current_user["role"] == "coach_admin" and current_user.get("branch_id"):
        filter_query["branch_id"] = current_user["branch_id"]
    elif branch_id:
        filter_query["branch_id"] = branch_id
    
    # Total students
    student_count = await db.users.count_documents({"role": "student", "is_active": True})
    stats["total_students"] = student_count
    
    # Active enrollments
    enrollment_count = await db.enrollments.count_documents({**filter_query, "is_active": True})
    stats["active_enrollments"] = enrollment_count
    
    # Pending payments
    pending_payments = await db.payments.count_documents({"payment_status": PaymentStatus.PENDING.value})
    stats["pending_payments"] = pending_payments
    
    # Overdue payments
    overdue_count = await db.payments.count_documents({
        "payment_status": PaymentStatus.PENDING.value,
        "due_date": {"$lt": datetime.utcnow()}
    })
    stats["overdue_payments"] = overdue_count
    
    # Today's attendance
    today = datetime.utcnow().date()
    today_attendance = await db.attendance.count_documents({
        "attendance_date": {
            "$gte": datetime.combine(today, datetime.min.time()),
            "$lt": datetime.combine(today + timedelta(days=1), datetime.min.time())
        }
    })
    stats["today_attendance"] = today_attendance
    
    return {"dashboard_stats": stats}

@api_router.get("/reports/financial")
async def get_financial_report(
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    current_user: dict = Depends(require_role([UserRole.SUPER_ADMIN]))
):
    """Get a financial report summary."""
    # Base match query
    match_query_paid = {"payment_status": PaymentStatus.PAID.value}
    match_query_pending = {"payment_status": PaymentStatus.PENDING.value}

    # Add date range filter if provided
    if start_date and end_date:
        date_filter = {"payment_date": {"$gte": start_date, "$lte": end_date}}
        match_query_paid.update(date_filter)
        pending_date_filter = {"due_date": {"$gte": start_date, "$lte": end_date}}
        match_query_pending.update(pending_date_filter)

    total_collected_cursor = db.payments.aggregate([
        {"$match": match_query_paid},
        {"$group": {"_id": None, "total": {"$sum": "$amount"}}}
    ])
    total_collected_list = await total_collected_cursor.to_list(1)

    outstanding_dues_cursor = db.payments.aggregate([
        {"$match": match_query_pending},
        {"$group": {"_id": None, "total": {"$sum": "$amount"}}}
    ])
    outstanding_dues_list = await outstanding_dues_cursor.to_list(1)

    report = {
        "total_collected": total_collected_list[0]["total"] if total_collected_list else 0,
        "outstanding_dues": outstanding_dues_list[0]["total"] if outstanding_dues_list else 0,
        "report_generated_at": datetime.utcnow()
    }
    if start_date and end_date:
        report["start_date"] = start_date
        report["end_date"] = end_date

    return report

@api_router.get("/reports/branch/{branch_id}")
async def get_branch_report(
    branch_id: str,
    current_user: dict = Depends(require_role([UserRole.SUPER_ADMIN, UserRole.COACH_ADMIN]))
):
    """Get a detailed report for a specific branch."""
    if current_user["role"] == UserRole.COACH_ADMIN and current_user.get("branch_id") != branch_id:
        raise HTTPException(status_code=403, detail="You can only access reports for your own branch.")

    branch = await db.branches.find_one({"id": branch_id})
    if not branch:
        raise HTTPException(status_code=404, detail="Branch not found")

    # Aggregate data for the report
    total_students = await db.users.count_documents({"role": "student", "branch_id": branch_id, "is_active": True})
    active_enrollments = await db.enrollments.count_documents({"branch_id": branch_id, "is_active": True})

    payments_summary = await db.payments.aggregate([
        {"$match": {"student_id": {"$in": [user["id"] for user in await db.users.find({"branch_id": branch_id}).to_list(1000)]}}},
        {"$group": {
            "_id": "$payment_status",
            "total_amount": {"$sum": "$amount"},
            "count": {"$sum": 1}
        }}
    ]).to_list(1000)

    report = {
        "branch_details": serialize_doc(branch),
        "total_students": total_students,
        "active_enrollments": active_enrollments,
        "payments_summary": payments_summary,
        "report_generated_at": datetime.utcnow()
    }
    return report

# Add middleware and startup
app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# NOTIFICATION MANAGEMENT
notification_router = APIRouter(prefix="/notifications", tags=["Notifications"])

@notification_router.post("/templates", status_code=status.HTTP_201_CREATED, response_model=NotificationTemplate)
async def create_notification_template(
    template_data: NotificationTemplateCreate,
    current_user: dict = Depends(require_role([UserRole.SUPER_ADMIN]))
):
    """Create a new notification template."""
    template = NotificationTemplate(**template_data.dict())
    await db.notification_templates.insert_one(template.dict())
    return template

@notification_router.get("/templates")
async def get_notification_templates(
    current_user: dict = Depends(require_role([UserRole.SUPER_ADMIN]))
):
    """Get all notification templates."""
    templates = await db.notification_templates.find().to_list(1000)
    return {"templates": serialize_doc(templates)}

@notification_router.get("/templates/{template_id}")
async def get_notification_template(
    template_id: str,
    current_user: dict = Depends(require_role([UserRole.SUPER_ADMIN]))
):
    """Get a single notification template by ID."""
    template = await db.notification_templates.find_one({"id": template_id})
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    return serialize_doc(template)

@notification_router.put("/templates/{template_id}")
async def update_notification_template(
    template_id: str,
    template_update: NotificationTemplateCreate,
    current_user: dict = Depends(require_role([UserRole.SUPER_ADMIN]))
):
    """Update a notification template."""
    update_data = template_update.dict()
    update_data["updated_at"] = datetime.utcnow()

    result = await db.notification_templates.update_one(
        {"id": template_id},
        {"$set": update_data}
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Template not found")
    return {"message": "Template updated successfully"}

@notification_router.delete("/templates/{template_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_notification_template(
    template_id: str,
    current_user: dict = Depends(require_role([UserRole.SUPER_ADMIN]))
):
    """Delete a notification template."""
    result = await db.notification_templates.delete_one({"id": template_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Template not found")
    return

@notification_router.post("/trigger")
async def trigger_notification(
    trigger_data: TriggerNotification,
    current_user: dict = Depends(require_role([UserRole.SUPER_ADMIN, UserRole.COACH_ADMIN]))
):
    """Trigger a notification for a specific user using a template."""
    user = await db.users.find_one({"id": trigger_data.user_id})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    template = await db.notification_templates.find_one({"id": trigger_data.template_id})
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")

    # Render the template
    body = template["body"]
    for key, value in trigger_data.context.items():
        body = body.replace(f"{{{{{key}}}}}", str(value))

    # Send the notification
    success = False
    if template["type"] == NotificationType.SMS.value:
        success = await send_sms(user["phone"], body)
    elif template["type"] == NotificationType.WHATSAPP.value:
        success = await send_whatsapp(user["phone"], body)

    # Log the notification attempt
    log_entry = NotificationLog(
        user_id=user["id"],
        template_id=template["id"],
        type=template["type"],
        status="sent" if success else "failed",
        content=body
    )
    await db.notification_logs.insert_one(log_entry.dict())

    if not success:
        raise HTTPException(status_code=500, detail="Failed to send notification.")

    return {"message": "Notification sent successfully."}

@notification_router.post("/broadcast")
async def broadcast_announcement(
    broadcast_data: BroadcastAnnouncement,
    current_user: dict = Depends(require_role([UserRole.SUPER_ADMIN, UserRole.COACH_ADMIN]))
):
    """Broadcast a notification to all users or users in a specific branch."""
    # Coach Admins can only broadcast to their own branch
    if current_user["role"] == UserRole.COACH_ADMIN:
        if broadcast_data.branch_id != current_user.get("branch_id"):
            raise HTTPException(status_code=403, detail="You can only broadcast to your own branch.")

    template = await db.notification_templates.find_one({"id": broadcast_data.template_id})
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")

    # Find target users
    user_filter = {"is_active": True}
    if broadcast_data.branch_id:
        user_filter["branch_id"] = broadcast_data.branch_id

    users_to_notify = await db.users.find(user_filter).to_list(length=None)

    # Render the template (context is the same for all users in a broadcast)
    body = template["body"]
    if broadcast_data.context:
        for key, value in broadcast_data.context.items():
            body = body.replace(f"{{{{{key}}}}}", str(value))

    # Send and log notifications
    sent_count = 0
    for user in users_to_notify:
        success = False
        if template["type"] == NotificationType.SMS.value:
            success = await send_sms(user["phone"], body)
        elif template["type"] == NotificationType.WHATSAPP.value:
            success = await send_whatsapp(user["phone"], body)

        log_entry = NotificationLog(
            user_id=user["id"],
            template_id=template["id"],
            type=template["type"],
            status="sent" if success else "failed",
            content=body
        )
        await db.notification_logs.insert_one(log_entry.dict())
        if success:
            sent_count += 1

    return {"message": f"Broadcast sent. Attempted to notify {len(users_to_notify)} users, successfully sent to {sent_count}."}

@notification_router.get("/logs")
async def get_notification_logs(
    user_id: Optional[str] = None,
    template_id: Optional[str] = None,
    status: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    current_user: dict = Depends(require_role([UserRole.SUPER_ADMIN, UserRole.COACH_ADMIN]))
):
    """Get a log of all notifications that have been sent."""
    filter_query = {}
    if user_id:
        filter_query["user_id"] = user_id
    if template_id:
        filter_query["template_id"] = template_id
    if status:
        filter_query["status"] = status

    # Coach Admins can only see logs for users in their branch
    if current_user["role"] == UserRole.COACH_ADMIN:
        branch_users = await db.users.find({"branch_id": current_user.get("branch_id")}).to_list(length=None)
        user_ids_in_branch = [user["id"] for user in branch_users]

        if "user_id" in filter_query:
            # If user_id filter is already present, ensure it's a user in the admin's branch
            if filter_query["user_id"] not in user_ids_in_branch:
                return {"logs": [], "total": 0} # Return empty if they ask for a user outside their branch
        else:
            filter_query["user_id"] = {"$in": user_ids_in_branch}

    logs = await db.notification_logs.find(filter_query).sort("created_at", -1).skip(skip).limit(limit).to_list(length=limit)
    total = await db.notification_logs.count_documents(filter_query)

    return {"logs": serialize_doc(logs), "total": total}

api_router.include_router(notification_router)

# REMINDERS
reminders_router = APIRouter(prefix="/reminders", tags=["Reminders"])

@reminders_router.post("/class")
async def send_class_reminders(
    reminder_data: ClassReminder,
    current_user: dict = Depends(require_role([UserRole.SUPER_ADMIN, UserRole.COACH_ADMIN]))
):
    """
    Send class reminders to all students enrolled in a specific course/branch.
    In a real application, this would be triggered by a scheduler.
    """
    # Find the course
    course = await db.courses.find_one({"id": reminder_data.course_id})
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")

    # Find a suitable template
    template = await db.notification_templates.find_one({"name": "class_reminder"})
    if not template:
        raise HTTPException(status_code=404, detail="Notification template 'class_reminder' not found.")

    # Find all active enrollments for this course/branch
    enrollment_filter = {
        "course_id": reminder_data.course_id,
        "branch_id": reminder_data.branch_id,
        "is_active": True
    }
    enrollments = await db.enrollments.find(enrollment_filter).to_list(length=None)

    student_ids = [e["student_id"] for e in enrollments]
    if not student_ids:
        return {"message": "No students to remind for this class."}

    students = await db.users.find({"id": {"$in": student_ids}}).to_list(length=None)

    sent_count = 0
    for student in students:
        body = template["body"].replace("{{student_name}}", student["full_name"]).replace("{{course_name}}", course["name"])

        success = False
        if template["type"] == NotificationType.WHATSAPP.value:
            success = await send_whatsapp(student["phone"], body)
        elif template["type"] == NotificationType.SMS.value:
            success = await send_sms(student["phone"], body)

        log_entry = NotificationLog(
            user_id=student["id"],
            template_id=template["id"],
            type=template["type"],
            status="sent" if success else "failed",
            content=body
        )
        await db.notification_logs.insert_one(log_entry.dict())
        if success:
            sent_count += 1

    return {"message": f"Sent {sent_count} class reminders for course '{course['name']}'."}

api_router.include_router(reminders_router)


# Include API routes
app.include_router(api_router)

# Health check endpoint
@app.get("/")
async def health_check():
    return {"status": "OK", "message": "Student Management System API", "version": "1.0.0"}
