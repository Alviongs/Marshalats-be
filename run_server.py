#!/usr/bin/env python3
"""
Simple server runner
"""

if __name__ == "__main__":
    try:
        print("Starting server...")
        import uvicorn
        from server import app
        
        uvicorn.run(
            app,
            host="0.0.0.0",
            port=8003,
            log_level="info",
            access_log=True
        )
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
