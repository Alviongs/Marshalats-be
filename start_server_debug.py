#!/usr/bin/env python3
"""
Debug script to start server and check for issues
"""

import sys
import traceback

def main():
    try:
        print("🔄 Importing server...")
        from server import app
        print("✅ Server imported successfully")
        
        print("🔄 Starting server...")
        import uvicorn
        
        # Start server with debug info
        uvicorn.run(
            app, 
            host="0.0.0.0", 
            port=8003,
            log_level="info",
            access_log=True
        )
        
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        print("📋 Full traceback:")
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
