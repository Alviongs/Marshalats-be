#!/usr/bin/env python3
"""
Minimal server to test basic functionality
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# Create minimal app
app = FastAPI(title="Minimal Test Server")

# Add CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Minimal server is running"}

@app.get("/test")
async def test():
    return {"status": "ok", "message": "Test endpoint working"}

@app.get("/api/courses/test/payment-info")
async def test_payment_info():
    return {
        "course_fee": 5000,
        "admission_fee": 1000,
        "total_amount": 6000,
        "currency": "INR",
        "course_name": "Test Course",
        "category_name": "Test Category",
        "branch_name": "Test Branch",
        "duration": "3 months"
    }

if __name__ == "__main__":
    print("🚀 Starting minimal server...")
    uvicorn.run(app, host="0.0.0.0", port=8003)
