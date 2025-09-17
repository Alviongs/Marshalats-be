#!/usr/bin/env python3
"""
Test coach login and JWT token validation
"""
import requests
import jwt
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Use the same secret key loading as the backend
SECRET_KEY = os.environ.get('SECRET_KEY', 'student_management_secret_key_2025')
ALGORITHM = "HS256"

print(f"🔑 Using SECRET_KEY: {SECRET_KEY}")
print(f"🔧 Using ALGORITHM: {ALGORITHM}")
BASE_URL = "http://31.97.224.169:8003"

def test_coach_login():
    """Test coach login and validate the returned JWT token"""
    print("🔐 Testing Coach Login and JWT Token")
    
    # Test coach credentials from user
    login_data = {
        "email": "pittisunilkumar3@gmail.com",
        "password": "Neelarani@10"
    }
    
    print(f"📧 Attempting login with email: {login_data['email']}")
    
    try:
        # Make login request
        response = requests.post(f"{BASE_URL}/api/coaches/login", json=login_data)
        
        print(f"📊 Response Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Login successful!")
            
            # Extract token
            token = data.get("access_token")
            if token:
                print(f"🎫 Full token: {token}")

                # Try to decode payload without verification first
                try:
                    # Decode without verification to see payload
                    unverified_payload = jwt.decode(token, options={"verify_signature": False})
                    print(f"📋 Unverified payload: {unverified_payload}")
                except Exception as e:
                    print(f"❌ Could not decode unverified payload: {e}")

                # Now try with verification
                try:
                    decoded = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
                    print("✅ Token validation successful!")
                    print(f"📋 Verified payload: {decoded}")

                    # Test API call with token
                    test_api_with_token(token, decoded.get("sub"))

                except jwt.ExpiredSignatureError:
                    print("❌ Token is expired")
                except jwt.InvalidSignatureError:
                    print("❌ Token signature verification failed")
                    print(f"Expected SECRET_KEY: {SECRET_KEY}")

                    # Try with different possible keys
                    possible_keys = [
                        'student_management_secret_key_2025',
                        'student_management_secret_key_2025_secure',
                        'your-super-secret-jwt-key-change-this-in-production-martial-arts-app-2024'
                    ]

                    for key in possible_keys:
                        try:
                            test_decoded = jwt.decode(token, key, algorithms=[ALGORITHM])
                            print(f"✅ Token works with key: {key}")
                            break
                        except:
                            continue
                    else:
                        print("❌ Token doesn't work with any known keys")

                except jwt.InvalidTokenError as e:
                    print(f"❌ Other token validation error: {e}")
            else:
                print("❌ No token in response")
                
        else:
            print(f"❌ Login failed: {response.status_code}")
            try:
                error_data = response.json()
                print(f"Error details: {error_data}")
            except:
                print(f"Error text: {response.text}")
                
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to backend server. Is it running on localhost:8003?")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

def test_api_with_token(token, coach_id):
    """Test API endpoint with the JWT token"""
    print(f"\n🌐 Testing API with token for coach: {coach_id}")
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # Test the courses endpoint
    try:
        response = requests.get(f"{BASE_URL}/api/coaches/{coach_id}/courses", headers=headers)
        print(f"📊 Courses API Status: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Courses API call successful!")
            data = response.json()
            print(f"📚 Courses data: {data}")
        else:
            print(f"❌ Courses API failed: {response.status_code}")
            try:
                error_data = response.json()
                print(f"Error details: {error_data}")
            except:
                print(f"Error text: {response.text}")
                
    except Exception as e:
        print(f"❌ API test error: {e}")

def list_available_coaches():
    """List available coaches for testing"""
    print("\n👥 Available coaches in database:")
    try:
        # This would require a database connection - simplified for now
        print("Please check your database for available coach credentials")
        print("Common test credentials might be:")
        print("- Email: coach@example.com, Password: password123")
        print("- Email: test.coach@example.com, Password: testpass")
    except Exception as e:
        print(f"Could not list coaches: {e}")

if __name__ == "__main__":
    print("=" * 60)
    list_available_coaches()
    print("=" * 60)
    test_coach_login()
    print("=" * 60)
