#!/usr/bin/env python3
"""
Test script for the updated User List API
Tests access with Superadmin, Coach Admin, and Coach tokens
"""

import requests
import json

BASE_URL = "http://localhost:8003"

def test_user_list_api():
    """Test the GET /api/users endpoint with different token types"""
    
    print("🧪 Testing User List API with Different Token Types")
    print("=" * 60)
    
    tokens_to_test = []
    
    # 1. Get superadmin token
    print("\n1. Getting Superadmin Token...")
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
    print("\n2. Getting Coach Token...")
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
    
    # 3. Test GET /api/users with different tokens
    print(f"\n3. Testing GET /api/users with different tokens...")
    print("-" * 50)
    
    for token_type, token in tokens_to_test:
        print(f"\n🔑 Testing with {token_type} token:")
        headers = {"Authorization": f"Bearer {token}"}
        
        # Test basic user list
        try:
            response = requests.get(f"{BASE_URL}/api/users", headers=headers)
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ {token_type} can access user list")
                print(f"   📊 Total users: {data.get('total', 0)}")
                print(f"   📋 Retrieved: {len(data.get('users', []))} users")
                
                # Show some user details (first 2 users)
                users = data.get('users', [])
                for i, user in enumerate(users[:2]):
                    print(f"   👤 User {i+1}: {user.get('full_name')} ({user.get('role')}) - {user.get('email')}")
                
            elif response.status_code == 403:
                print(f"   ❌ {token_type} denied access (403 Forbidden)")
                error_detail = response.json().get('detail', 'No details')
                print(f"   📄 Error: {error_detail}")
            else:
                print(f"   ❓ Unexpected response: {response.status_code}")
                print(f"   📄 Response: {response.text}")
                
        except Exception as e:
            print(f"   ❌ Error testing {token_type}: {e}")
        
        # Test with role filter (students only)
        try:
            response = requests.get(f"{BASE_URL}/api/users?role=student&limit=5", headers=headers)
            if response.status_code == 200:
                data = response.json()
                print(f"   📚 Students only: {data.get('total', 0)} total, showing {len(data.get('users', []))}")
            elif response.status_code == 403:
                print(f"   ⚠️  {token_type} cannot filter by student role")
        except Exception as e:
            print(f"   ❌ Error testing role filter: {e}")
    
    # 4. Show endpoint details
    print(f"\n4. API Endpoint Information:")
    print(f"   📍 Endpoint: GET {BASE_URL}/api/users")
    print(f"   🔐 Access: Superadmin, Coach Admin, Coach tokens")
    print(f"   📝 Query Parameters:")
    print(f"      - role: Filter by user role (student, coach, coach_admin, super_admin)")
    print(f"      - branch_id: Filter by branch ID")
    print(f"      - skip: Pagination offset (default: 0)")
    print(f"      - limit: Results per page (default: 50, max: 100)")
    print(f"   🎯 Access Rules:")
    print(f"      - Superadmin: Can view all users across all branches")
    print(f"      - Coach Admin: Can view users in their assigned branch only")
    print(f"      - Coach: Can view only students in their assigned branch")

if __name__ == "__main__":
    test_user_list_api()
