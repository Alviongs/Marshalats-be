#!/usr/bin/env python3
"""
Debug script to check what token you're using and suggest the fix
"""

import requests
import json

BASE_URL = "http://localhost:8003"

def debug_permissions():
    """Debug the permissions issue"""
    
    print("🔍 Debugging Permissions Issue...")
    
    # Test different token types
    tokens_to_test = []
    
    # 1. Get superadmin token
    print("\n1. Testing Superadmin Token...")
    try:
        superadmin_login = {
            "email": "testsuperadmin@example.com",
            "password": "TestSuperAdmin123!"
        }
        
        admin_response = requests.post(f"{BASE_URL}/api/superadmin/login", json=superadmin_login)
        if admin_response.status_code == 200:
            admin_token = admin_response.json()["data"]["token"]
            tokens_to_test.append(("Superadmin", admin_token))
            print("✅ Superadmin token obtained")
        else:
            print(f"❌ Superadmin login failed: {admin_response.text}")
    except Exception as e:
        print(f"❌ Superadmin error: {e}")
    
    # 2. Get coach token
    print("\n2. Testing Coach Token...")
    try:
        coach_login = {
            "email": "testlogincoach@example.com",
            "password": "TestCoachLogin123!"
        }
        
        coach_response = requests.post(f"{BASE_URL}/api/coaches/login", json=coach_login)
        if coach_response.status_code == 200:
            coach_token = coach_response.json()["access_token"]
            tokens_to_test.append(("Coach", coach_token))
            print("✅ Coach token obtained")
        else:
            print(f"❌ Coach login failed: {coach_response.text}")
    except Exception as e:
        print(f"❌ Coach error: {e}")
    
    # 3. Test each token with GET /api/coaches
    print(f"\n3. Testing GET /api/coaches with different tokens...")
    
    for token_type, token in tokens_to_test:
        print(f"\n   Testing {token_type} token:")
        headers = {"Authorization": f"Bearer {token}"}
        
        try:
            response = requests.get(f"{BASE_URL}/api/coaches", headers=headers)
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                print(f"   ✅ {token_type} can access GET /api/coaches")
                data = response.json()
                print(f"   Found {data.get('total', 0)} coaches")
            elif response.status_code == 403:
                print(f"   ❌ {token_type} denied access (403 Forbidden)")
            else:
                print(f"   ❓ Unexpected response: {response.text}")
                
        except Exception as e:
            print(f"   ❌ Error testing {token_type}: {e}")
    
    # 4. Show solutions
    print(f"\n4. Solutions:")
    print(f"   Option A: Use Superadmin token (if available above)")
    print(f"   Option B: Allow coaches to see other coaches (modify permissions)")
    print(f"   Option C: Create coach admin user (coach_admin role)")

if __name__ == "__main__":
    debug_permissions()
