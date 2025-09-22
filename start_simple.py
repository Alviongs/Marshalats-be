#!/usr/bin/env python3
"""
Simple server starter with error handling
"""

import sys
import traceback

def start_server():
    try:
        print("🚀 Starting Marshalats Backend Server...")
        print("📍 Loading modules...")
        
        import uvicorn
        print("✅ uvicorn imported")
        
        from server import app
        print("✅ app imported")
        
        print("🌐 Starting server on http://0.0.0.0:8003")
        uvicorn.run(
            app,
            host="0.0.0.0",
            port=8003,
            log_level="info"
        )
        
    except ImportError as e:
        print(f"❌ Import Error: {e}")
        traceback.print_exc()
    except Exception as e:
        print(f"❌ Server Error: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    start_server()
