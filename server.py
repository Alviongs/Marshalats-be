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
    coach_router,
    branch_router,
    branch_manager_router,
    course_router,
    category_router,
    duration_router,
    location_router,
    branch_public_router,
    enrollment_router,
    payment_router,
    request_router,
    event_router,
    search_router,
    email_router,
    dashboard_router,
    settings_router,
    reports_router,
    attendance_router,
    message_router
)
from routes.superadmin_routes import router as superadmin_router
from routes.branches_with_courses_routes import router as branches_with_courses_router

# Import database utility
from utils.database import db

# Load environment variables
ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    mongo_url = os.getenv("MONGO_URL", "mongodb://localhost:27017")
    app.mongodb_client = AsyncIOMotorClient(mongo_url)
    db_name = os.getenv("DB_NAME", "marshalats")
    app.mongodb = app.mongodb_client.get_database(db_name)
    
    # Initialize the database connection in utils
    from utils.database import init_db
    init_db(app.mongodb)
    
    yield
    
    # Shutdown
    app.mongodb_client.close()

# Create FastAPI app
app = FastAPI(
    title="Learning Management System API",
    description="A comprehensive LMS API for managing students, courses, and educational content",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3022",
        "http://127.0.0.1:3022",
        "http://31.97.224.169:3022",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "*"  # Allow all origins for development
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["*"],
)

# Include routers
app.include_router(superadmin_router, prefix="/api/superadmin", tags=["Super Admin"])
app.include_router(auth_router, prefix="/api/auth", tags=["Authentication"])
app.include_router(user_router, prefix="/api/users", tags=["Users"])
app.include_router(coach_router, prefix="/api/coaches", tags=["Coaches"])
app.include_router(branch_router, prefix="/api/branches", tags=["Branches"])
app.include_router(branch_manager_router, prefix="/api/branch-managers", tags=["Branch Managers"])
app.include_router(course_router, prefix="/api/courses", tags=["Courses"])
app.include_router(category_router, prefix="/api/categories", tags=["Categories"])
app.include_router(duration_router, prefix="/api/durations", tags=["Durations"])
app.include_router(location_router, prefix="/api/locations", tags=["Locations"])
app.include_router(branch_public_router, prefix="/api/branches", tags=["Public Branches"])
app.include_router(enrollment_router, prefix="/api/enrollments", tags=["Enrollments"])
app.include_router(payment_router, prefix="/api/payments", tags=["Payments"])
app.include_router(request_router, prefix="/api/requests", tags=["Requests"])
app.include_router(event_router, prefix="/api/events", tags=["Events"])
app.include_router(search_router, prefix="/api/search", tags=["Search"])
app.include_router(email_router, prefix="/api/email", tags=["Email"])
app.include_router(dashboard_router, prefix="/api/dashboard", tags=["Dashboard"])
app.include_router(settings_router, prefix="/api/settings", tags=["Settings"])
app.include_router(reports_router, prefix="/api/reports", tags=["Reports"])
app.include_router(attendance_router, prefix="/api/attendance", tags=["Attendance"])
app.include_router(message_router, prefix="/api/messages", tags=["Messages"])
app.include_router(branches_with_courses_router, prefix="/api", tags=["Branches with Courses"])

@app.get("/")
async def root():
    return {"message": "Learning Management System API is running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": "2024-01-01T00:00:00Z", "version": "updated-coach-auth"}

@app.get("/test-coach-auth")
async def test_coach_auth():
    return {"message": "Coach authorization logic has been updated", "timestamp": "2025-09-20"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8003)
