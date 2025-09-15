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
    # Startup
    mongo_url = os.getenv("MONGO_URI", "mongodb://localhost:27017")
    app.mongodb_client = AsyncIOMotorClient(mongo_url)
    app.mongodb = app.mongodb_client.get_database("lms_db")
    
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
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_router, prefix="/api/auth", tags=["Authentication"])
app.include_router(user_router, prefix="/api/users", tags=["Users"])
app.include_router(branch_router, prefix="/api/branches", tags=["Branches"])
app.include_router(course_router, prefix="/api/courses", tags=["Courses"])
app.include_router(enrollment_router, prefix="/api/enrollments", tags=["Enrollments"])
app.include_router(payment_router, prefix="/api/payments", tags=["Payments"])
app.include_router(request_router, prefix="/api/requests", tags=["Requests"])
app.include_router(event_router, prefix="/api/events", tags=["Events"])

@app.get("/")
async def root():
    return {"message": "Learning Management System API is running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": "2024-01-01T00:00:00Z"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
