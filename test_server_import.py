#!/usr/bin/env python3
"""
Test script to check if server imports work correctly
"""
import sys
from pathlib import Path

# Add the current directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

try:
    print("Testing server imports...")
    
    # Test basic imports
    print("✅ Testing FastAPI import...")
    from fastapi import FastAPI
    
    print("✅ Testing motor import...")
    from motor.motor_asyncio import AsyncIOMotorClient
    
    print("✅ Testing routes import...")
    from routes import user_router
    
    print("✅ Testing controllers import...")
    from controllers.user_controller import UserController
    
    print("✅ Testing database utils...")
    from utils.database import init_db
    
    print("✅ All imports successful!")
    
    # Try to create the app
    print("✅ Testing app creation...")
    app = FastAPI(title="Test API")
    print("✅ App created successfully!")
    
    print("\n🎉 Server imports test completed successfully!")
    
except ImportError as e:
    print(f"❌ Import error: {e}")
    import traceback
    traceback.print_exc()
except Exception as e:
    print(f"❌ General error: {e}")
    import traceback
    traceback.print_exc()
