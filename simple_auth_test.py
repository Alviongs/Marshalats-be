#!/usr/bin/env python3
"""
Simple Bearer Token Testing Examples
"""
import requests
import json

def simple_auth_test():
    """Simple step-by-step bearer token testing"""
    
    base_url = "http://localhost:8003/api"
    
    print("🔐 STEP 1: LOGIN TO GET BEARER TOKEN")
    print("=" * 50)
    
    # Step 1: Login to get token
    login_url = f"{base_url}/auth/login"
    login_data = {
        "email": "superadmin@test.com",
        "password": "SuperAdmin123!"
    }
    
    print(f"Request: POST {login_url}")
    print(f"Body: {json.dumps(login_data, indent=2)}")
    
    response = requests.post(login_url, json=login_data)
    
    print(f"\nResponse Status: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        token = result["access_token"]
        
        print(f"✅ Login successful!")
        print(f"Bearer Token: {token}")
        
        print(f"\n🔒 STEP 2: USE BEARER TOKEN IN HEADER")
        print("=" * 50)
        
        # Step 2: Use the token in Authorization header
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        print(f"Headers: {json.dumps(headers, indent=2)}")
        
        # Test protected endpoint
        me_url = f"{base_url}/auth/me"
        print(f"\n📋 STEP 3: TEST PROTECTED ENDPOINT")
        print("=" * 50)
        print(f"Request: GET {me_url}")
        
        me_response = requests.get(me_url, headers=headers)
        print(f"Response Status: {me_response.status_code}")
        
        if me_response.status_code == 200:
            user_data = me_response.json()
            print(f"✅ Protected endpoint accessed successfully!")
            print(f"User Data: {json.dumps(user_data, indent=2)}")
        else:
            print(f"❌ Failed to access protected endpoint: {me_response.text}")
        
        # Test branch creation
        print(f"\n🏢 STEP 4: TEST BRANCH CREATION WITH AUTH")
        print("=" * 50)
        
        branch_url = f"{base_url}/branches"
        branch_data = {
            "branch": {
                "name": "Test Auth Branch",
                "code": "TAB01",
                "email": "test@auth.com",
                "phone": "+1234567890",
                "address": {
                    "line1": "123 Auth St",
                    "area": "Auth Area",
                    "city": "Auth City",
                    "state": "Auth State",
                    "pincode": "123456",
                    "country": "India"
                }
            },
            "manager_id": "auth-manager-uuid",
            "operational_details": {
                "courses_offered": ["Auth Course"],
                "timings": [
                    {"day": "Monday", "open": "09:00", "close": "18:00"}
                ],
                "holidays": ["2025-12-25"]
            },
            "assignments": {
                "accessories_available": True,
                "courses": ["auth-course-uuid-1"],
                "branch_admins": ["auth-admin-uuid-1"]
            },
            "bank_details": {
                "bank_name": "Auth Bank",
                "account_number": "1234567890",
                "upi_id": "auth@upi"
            }
        }
        
        print(f"Request: POST {branch_url}")
        print(f"Headers: Authorization: Bearer {token[:30]}...")
        
        branch_response = requests.post(branch_url, json=branch_data, headers=headers)
        print(f"Response Status: {branch_response.status_code}")
        
        if branch_response.status_code == 200:
            branch_result = branch_response.json()
            print(f"✅ Branch created with authentication!")
            print(f"Branch ID: {branch_result['branch_id']}")
        else:
            print(f"❌ Branch creation failed: {branch_response.text}")
        
    else:
        print(f"❌ Login failed: {response.text}")

def show_curl_examples():
    """Show curl command examples"""
    
    print(f"\n{'='*60}")
    print("📋 CURL COMMAND EXAMPLES")
    print("=" * 60)
    
    # First get token
    print(f"\n1️⃣ LOGIN TO GET TOKEN:")
    print("-" * 30)
    print("""curl -X POST http://localhost:8003/api/auth/login \\
  -H "Content-Type: application/json" \\
  -d '{
    "email": "superadmin@test.com",
    "password": "SuperAdmin123!"
  }'""")
    
    print(f"\n2️⃣ USE TOKEN IN PROTECTED REQUESTS:")
    print("-" * 30)
    print("""curl -X GET http://localhost:8003/api/auth/me \\
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \\
  -H "Content-Type: application/json" """)
    
    print(f"\n3️⃣ CREATE BRANCH WITH AUTH:")
    print("-" * 30)
    print("""curl -X POST http://localhost:8003/api/branches \\
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \\
  -H "Content-Type: application/json" \\
  -d '{
    "branch": {
      "name": "Curl Test Branch",
      "code": "CTB01",
      "email": "curl@test.com",
      "phone": "+1234567890",
      "address": {
        "line1": "123 Curl St",
        "area": "Curl Area",
        "city": "Curl City",
        "state": "Curl State",
        "pincode": "123456",
        "country": "India"
      }
    },
    "manager_id": "curl-manager-uuid",
    "operational_details": {
      "courses_offered": ["Curl Course"],
      "timings": [
        {"day": "Monday", "open": "09:00", "close": "18:00"}
      ],
      "holidays": ["2025-12-25"]
    },
    "assignments": {
      "accessories_available": true,
      "courses": ["curl-course-uuid-1"],
      "branch_admins": ["curl-admin-uuid-1"]
    },
    "bank_details": {
      "bank_name": "Curl Bank",
      "account_number": "1234567890",
      "upi_id": "curl@upi"
    }
  }'""")

def show_postman_guide():
    """Show Postman testing guide"""
    
    print(f"\n{'='*60}")
    print("📮 POSTMAN TESTING GUIDE")
    print("=" * 60)
    
    print("""
🔐 STEP 1: Login Request
   Method: POST
   URL: http://localhost:8003/api/auth/login
   Headers: Content-Type: application/json
   Body (JSON):
   {
     "email": "superadmin@test.com",
     "password": "SuperAdmin123!"
   }

📋 STEP 2: Copy the access_token from response

🔒 STEP 3: Set Authorization Header
   For all protected requests, add header:
   Authorization: Bearer YOUR_ACCESS_TOKEN

✅ STEP 4: Test Protected Endpoints
   GET /api/auth/me
   GET /api/users
   GET /api/branches
   POST /api/branches (with full payload)
   
💡 TIP: In Postman, you can set the token as a variable:
   1. Go to Tests tab in login request
   2. Add: pm.globals.set("token", pm.response.json().access_token);
   3. Use {{token}} in Authorization header: Bearer {{token}}
""")

if __name__ == "__main__":
    print("🧪 BEARER TOKEN AUTHENTICATION TESTING")
    
    simple_auth_test()
    show_curl_examples()
    show_postman_guide()
