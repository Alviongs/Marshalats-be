#!/usr/bin/env python3
"""
Final test for User List API
Tests the GET /api/users endpoint with different token types
"""

import requests
import json
import time

BASE_URL = "http://localhost:8003"

def test_user_list_api():
    """Test the GET /api/users endpoint with different token types"""
    
    print("🧪 Testing User List API - Final Version")
    print("=" * 60)
    
    tokens_to_test = []
    
    # 1. Get superadmin token
    print("\n1. Getting Superadmin Token...")
    try:
        superadmin_login = {
            "email": "testsuperadmin@example.com",
            "password": "TestSuperAdmin123!"
        }
        
        admin_response = requests.post(f"{BASE_URL}/api/superadmin/login", json=superadmin_login, timeout=10)
        print(f"   Superadmin Login Status: {admin_response.status_code}")
        
        if admin_response.status_code == 200:
            admin_token = admin_response.json()["data"]["token"]
            tokens_to_test.append(("Superadmin", admin_token))
            print("   ✅ Superadmin token obtained")
        else:
            print(f"   ❌ Superadmin login failed: {admin_response.text}")
    except Exception as e:
        print(f"   ❌ Superadmin error: {e}")
    
    # 2. Get coach token
    print("\n2. Getting Coach Token...")
    try:
        coach_login = {
            "email": "testlogincoach@example.com",
            "password": "TestCoachLogin123!"
        }
        
        coach_response = requests.post(f"{BASE_URL}/api/coaches/login", json=coach_login, timeout=10)
        print(f"   Coach Login Status: {coach_response.status_code}")
        
        if coach_response.status_code == 200:
            coach_token = coach_response.json()["access_token"]
            tokens_to_test.append(("Coach", coach_token))
            print("   ✅ Coach token obtained")
        else:
            print(f"   ❌ Coach login failed: {coach_response.text}")
    except Exception as e:
        print(f"   ❌ Coach error: {e}")
    
    # 3. Test GET /api/users with different tokens
    print(f"\n3. Testing GET /api/users with different tokens...")
    print("-" * 50)
    
    for token_type, token in tokens_to_test:
        print(f"\n🔑 Testing with {token_type} token:")
        headers = {"Authorization": f"Bearer {token}"}
        
        try:
            # Test basic user list
            response = requests.get(f"{BASE_URL}/api/users", headers=headers, timeout=10)
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ {token_type} can access user list!")
                print(f"   📊 Total users in database: {data.get('total', 0)}")
                print(f"   📋 Retrieved in this request: {len(data.get('users', []))} users")
                print(f"   📄 Message: {data.get('message', 'N/A')}")
                
                # Show first few users
                users = data.get('users', [])
                if users:
                    print(f"   👤 Sample users:")
                    for i, user in enumerate(users[:3]):
                        print(f"      {i+1}. {user.get('full_name', 'N/A')} ({user.get('role', 'N/A')}) - {user.get('email', 'N/A')}")
                        if user.get('branch_id'):
                            print(f"         Branch: {user.get('branch_id')}")
                
            elif response.status_code == 403:
                print(f"   ❌ {token_type} denied access (403 Forbidden)")
                try:
                    error_detail = response.json().get('detail', 'No details')
                    print(f"   📄 Error: {error_detail}")
                except:
                    print(f"   📄 Raw response: {response.text}")
            elif response.status_code == 500:
                print(f"   ❌ Server Error (500)")
                print(f"   📄 Response: {response.text}")
            else:
                print(f"   ❓ Unexpected response: {response.status_code}")
                print(f"   📄 Response: {response.text}")
                
        except Exception as e:
            print(f"   ❌ Error testing {token_type}: {e}")
        
        # Test with query parameters
        if token_type in ["Superadmin", "Coach"]:
            try:
                print(f"   🔍 Testing with query parameters...")
                params_response = requests.get(
                    f"{BASE_URL}/api/users?limit=5&skip=0", 
                    headers=headers, 
                    timeout=10
                )
                if params_response.status_code == 200:
                    params_data = params_response.json()
                    print(f"   ✅ Query params work: Got {len(params_data.get('users', []))} users")
                else:
                    print(f"   ⚠️  Query params failed: {params_response.status_code}")
            except Exception as e:
                print(f"   ❌ Query params error: {e}")
    
    # 4. Test without authentication
    print(f"\n4. Testing without authentication...")
    try:
        no_auth_response = requests.get(f"{BASE_URL}/api/users", timeout=10)
        print(f"   Status without auth: {no_auth_response.status_code}")
        if no_auth_response.status_code == 401:
            print("   ✅ Correctly requires authentication")
        else:
            print(f"   ⚠️  Unexpected status: {no_auth_response.text}")
    except Exception as e:
        print(f"   ❌ No auth test error: {e}")
    
    # 5. Summary
    print(f"\n5. API Summary:")
    print(f"   📍 Endpoint: GET {BASE_URL}/api/users")
    print(f"   🔐 Authentication: Bearer Token Required")
    print(f"   👥 Supported Roles: Superadmin, Coach Admin, Coach")
    print(f"   📝 Query Parameters:")
    print(f"      - role: Filter by user role")
    print(f"      - branch_id: Filter by branch")
    print(f"      - skip: Pagination offset")
    print(f"      - limit: Results per page")
    print(f"   🎯 Access Rules:")
    print(f"      - Superadmin: Can view all users")
    print(f"      - Coach Admin: Can view users in their branch")
    print(f"      - Coach: Can view only students in their branch")

if __name__ == "__main__":
    test_user_list_api()
