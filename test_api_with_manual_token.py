#!/usr/bin/env python3
"""
Test API endpoints with manually created JWT token
"""
import requests
import jwt
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

SECRET_KEY = os.environ.get('SECRET_KEY', 'student_management_secret_key_2025')
ALGORITHM = "HS256"
BASE_URL = "http://31.97.224.169:8003"

def create_test_token():
    """Create a test JWT token for the known coach"""
    coach_id = "b6c5cc5f-be8d-47b2-aa95-3c1cdcb72a0d"  # From database check
    
    token_data = {
        "sub": coach_id,
        "email": "pittisunilkumar3@gmail.com",
        "role": "coach",
        "coach_id": coach_id,
        "exp": datetime.utcnow() + timedelta(hours=24)
    }
    
    token = jwt.encode(token_data, SECRET_KEY, algorithm=ALGORITHM)
    print(f"🎫 Created test token: {token[:50]}...")
    return token, coach_id

def test_api_endpoints(token, coach_id):
    """Test various API endpoints with the token"""
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    endpoints = [
        f"/api/coaches/{coach_id}/courses",
        f"/api/coaches/{coach_id}/students",
        f"/api/coaches/{coach_id}"
    ]
    
    for endpoint in endpoints:
        print(f"\n🌐 Testing: {endpoint}")
        try:
            response = requests.get(f"{BASE_URL}{endpoint}", headers=headers)
            print(f"📊 Status: {response.status_code}")
            
            if response.status_code == 200:
                print("✅ Success!")
                data = response.json()
                print(f"📄 Response: {str(data)[:200]}...")
            else:
                print(f"❌ Failed: {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"Error: {error_data}")
                except:
                    print(f"Error text: {response.text}")
                    
        except requests.exceptions.ConnectionError:
            print("❌ Connection error - is the backend running?")
        except Exception as e:
            print(f"❌ Error: {e}")

def test_token_validation():
    """Test if our manually created token is valid"""
    token, coach_id = create_test_token()
    
    print("🔍 Validating manually created token...")
    try:
        decoded = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        print("✅ Token is valid!")
        print(f"📋 Decoded: {decoded}")
        
        # Test API endpoints
        test_api_endpoints(token, coach_id)
        
    except jwt.ExpiredSignatureError:
        print("❌ Token expired")
    except jwt.InvalidTokenError as e:
        print(f"❌ Token invalid: {e}")

if __name__ == "__main__":
    print("=" * 60)
    print("🧪 Testing API with manually created JWT token")
    print("=" * 60)
    test_token_validation()
    print("=" * 60)
