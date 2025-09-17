#!/usr/bin/env python3
"""
Test JWT token creation and validation
"""
import os
import jwt
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

SECRET_KEY = os.environ.get('SECRET_KEY', 'student_management_secret_key_2025')
ALGORITHM = "HS256"

def test_jwt_creation_and_validation():
    print("🔐 JWT Token Test")
    print(f"SECRET_KEY: {SECRET_KEY}")
    print(f"ALGORITHM: {ALGORITHM}")
    
    # Create a test token (similar to coach login)
    test_data = {
        "sub": "test-coach-id-123",
        "email": "test@coach.com",
        "role": "coach",
        "coach_id": "test-coach-id-123",
        "exp": datetime.utcnow() + timedelta(hours=24)
    }
    
    print(f"\n📝 Creating token with data: {test_data}")
    
    # Create token
    try:
        token = jwt.encode(test_data, SECRET_KEY, algorithm=ALGORITHM)
        print(f"✅ Token created successfully")
        print(f"🎫 Token: {token[:50]}...")
        
        # Validate token
        try:
            decoded = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            print(f"✅ Token validation successful")
            print(f"📋 Decoded data: {decoded}")
            return True
        except jwt.ExpiredSignatureError:
            print("❌ Token expired")
            return False
        except jwt.InvalidTokenError as e:
            print(f"❌ Token validation failed: {e}")
            return False
            
    except Exception as e:
        print(f"❌ Token creation failed: {e}")
        return False

def test_token_from_frontend():
    """Test a token that might be stored in frontend localStorage"""
    print("\n🌐 Testing token from frontend...")
    
    # This would be the token from localStorage - you can paste a real token here for testing
    frontend_token = input("Paste a token from frontend localStorage (or press Enter to skip): ").strip()
    
    if not frontend_token:
        print("⏭️ Skipping frontend token test")
        return
    
    try:
        decoded = jwt.decode(frontend_token, SECRET_KEY, algorithms=[ALGORITHM])
        print(f"✅ Frontend token is valid")
        print(f"📋 Decoded data: {decoded}")
    except jwt.ExpiredSignatureError:
        print("❌ Frontend token expired")
    except jwt.InvalidTokenError as e:
        print(f"❌ Frontend token validation failed: {e}")

if __name__ == "__main__":
    print("=" * 50)
    success = test_jwt_creation_and_validation()
    test_token_from_frontend()
    print("=" * 50)
    
    if success:
        print("✅ JWT system is working correctly")
    else:
        print("❌ JWT system has issues")
