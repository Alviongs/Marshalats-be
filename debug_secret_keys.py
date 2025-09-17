#!/usr/bin/env python3
"""
Debug secret key differences between modules
"""
import os
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables like the main server
load_dotenv()

print("🔍 Debugging Secret Key Configuration")
print("=" * 50)

# Check what's in the .env file
print("📄 .env file contents:")
try:
    with open('.env', 'r') as f:
        for line_num, line in enumerate(f, 1):
            if 'SECRET_KEY' in line:
                print(f"Line {line_num}: {line.strip()}")
except Exception as e:
    print(f"Error reading .env: {e}")

print("\n🔑 Environment Variable Checks:")
print(f"os.environ.get('SECRET_KEY'): {os.environ.get('SECRET_KEY', 'NOT_FOUND')}")
print(f"Default fallback: 'student_management_secret_key_2025'")

# Import and check each module's SECRET_KEY
print("\n📦 Module Secret Key Comparison:")

try:
    from utils.auth import SECRET_KEY as AUTH_SECRET_KEY
    print(f"utils.auth.SECRET_KEY: {AUTH_SECRET_KEY}")
except Exception as e:
    print(f"Error importing from utils.auth: {e}")

try:
    from utils.unified_auth import SECRET_KEY as UNIFIED_AUTH_SECRET_KEY
    print(f"utils.unified_auth.SECRET_KEY: {UNIFIED_AUTH_SECRET_KEY}")
except Exception as e:
    print(f"Error importing from utils.unified_auth: {e}")

# Test JWT creation and validation with both
print("\n🧪 JWT Token Test:")
import jwt
from datetime import datetime, timedelta

test_payload = {
    "sub": "test-user",
    "role": "coach",
    "exp": datetime.utcnow() + timedelta(hours=1)
}

try:
    from utils.auth import SECRET_KEY as AUTH_KEY, ALGORITHM
    
    # Create token with auth module key
    token_auth = jwt.encode(test_payload, AUTH_KEY, algorithm=ALGORITHM)
    print(f"✅ Token created with auth key: {token_auth[:30]}...")
    
    # Try to decode with unified_auth key
    try:
        from utils.unified_auth import SECRET_KEY as UNIFIED_KEY
        decoded = jwt.decode(token_auth, UNIFIED_KEY, algorithms=[ALGORITHM])
        print("✅ Token successfully decoded with unified_auth key")
    except jwt.InvalidSignatureError:
        print("❌ Token signature verification failed with unified_auth key")
        print(f"Auth key: {AUTH_KEY}")
        print(f"Unified key: {UNIFIED_KEY}")
        print(f"Keys match: {AUTH_KEY == UNIFIED_KEY}")
    except Exception as e:
        print(f"❌ Other error: {e}")
        
except Exception as e:
    print(f"❌ Error in JWT test: {e}")

print("=" * 50)
