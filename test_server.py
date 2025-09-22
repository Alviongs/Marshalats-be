#!/usr/bin/env python3
"""
Minimal test server to check if uvicorn works
"""

from fastapi import FastAPI
import uvicorn

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Test server is running"}

@app.get("/health")
async def health():
    return {"status": "healthy"}

if __name__ == "__main__":
    print("Starting test server...")
    try:
        uvicorn.run(app, host="0.0.0.0", port=8003)
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
