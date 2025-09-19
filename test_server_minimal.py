#!/usr/bin/env python3
"""
Minimal server test without database dependencies
"""
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Create a minimal test app
app = FastAPI(title="Test Branch Manager Auth")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Test server running"}

@app.get("/api/branch-managers/me")
async def test_branch_manager_me():
    return {
        "branch_manager": {
            "id": "test-id",
            "full_name": "Test Manager",
            "email": "test@example.com",
            "role": "branch_manager"
        }
    }

if __name__ == "__main__":
    print("🚀 Starting minimal test server on port 8003...")
    uvicorn.run(app, host="0.0.0.0", port=8003)
