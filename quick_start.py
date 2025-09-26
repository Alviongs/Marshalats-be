#!/usr/bin/env python3
"""
Quick server start with error handling
"""

import sys
import os

def main():
    try:
        print("🚀 Quick Start - Marshalats Backend")
        print("=" * 40)
        
        # Import required modules
        print("📦 Importing modules...")
        import uvicorn
        from server import app
        
        print("✅ Modules imported successfully")
        print("🌐 Starting server on http://localhost:8003")
        print("📖 API docs will be at http://localhost:8003/docs")
        print("🛑 Press Ctrl+C to stop")
        print("-" * 40)
        
        # Start the server
        uvicorn.run(
            app,
            host="127.0.0.1",  # Try localhost instead of 0.0.0.0
            port=8003,
            log_level="info"
        )
        
    except ImportError as e:
        print(f"❌ Import Error: {e}")
        print("💡 Make sure all dependencies are installed")
        return 1
        
    except OSError as e:
        if "Address already in use" in str(e):
            print("❌ Port 8003 is already in use")
            print("💡 Try killing existing processes or use a different port")
        else:
            print(f"❌ OS Error: {e}")
        return 1
        
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
        return 0
        
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())
