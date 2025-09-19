from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
from dotenv import load_dotenv
from pathlib import Path

# Import routes
from routes import (
    branch_manager_router,
)

# Load environment variables
ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# Create FastAPI app without database lifespan
app = FastAPI(
    title="Learning Management System API",
    description="A comprehensive LMS API for managing students, courses, and educational content",
    version="1.0.0"
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
app.include_router(branch_manager_router, prefix="/api/branch-managers", tags=["Branch Managers"])

@app.get("/")
async def root():
    return {"message": "Learning Management System API is running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": "2024-01-01T00:00:00Z"}

if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting server without database...")
    uvicorn.run(app, host="0.0.0.0", port=8003)
