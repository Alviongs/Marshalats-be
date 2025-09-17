#!/usr/bin/env python3
"""
Test script to verify branch API accepts superadmin tokens
"""

import requests
import json

BASE_URL = "http://31.97.224.169:8003"

def test_branch_api_with_superadmin():
    """Test that branch API now accepts superadmin tokens"""
    
    print("🔬 Testing Branch API with Superadmin Token")
    print("=" * 50)
    
    try:
        # Step 1: Get superadmin token
        print("1. Getting superadmin token...")
        login_data = {
            "email": "testsuperadmin@example.com",
            "password": "TestSuperAdmin123!"
        }
        
        login_response = requests.post(f"{BASE_URL}/api/superadmin/login", json=login_data, timeout=10)
        print(f"   Login status: {login_response.status_code}")
        
        if login_response.status_code != 200:
            print(f"   ❌ Login failed: {login_response.text}")
            return False
            
        token = login_response.json()["data"]["token"]
        print("   ✅ Superadmin token obtained")
        
        # Step 2: Test GET branches (should work)
        print("\n2. Testing GET /api/branches...")
        headers = {"Authorization": f"Bearer {token}"}
        
        get_response = requests.get(f"{BASE_URL}/api/branches", headers=headers, timeout=10)
        print(f"   GET branches status: {get_response.status_code}")
        
        if get_response.status_code == 200:
            data = get_response.json()
            print(f"   ✅ SUCCESS! Can view branches")
            print(f"   📊 Found {len(data.get('branches', []))} branches")
        elif get_response.status_code == 401:
            print(f"   ❌ Still getting 401 Unauthorized: {get_response.text}")
            return False
        else:
            print(f"   ⚠️  Unexpected status: {get_response.status_code} - {get_response.text}")
        
        # Step 3: Test POST branches (create branch)
        print("\n3. Testing POST /api/branches...")
        
        branch_data = {
            "branch": {
                "name": "Test Branch API",
                "code": "TBAPI",
                "email": "testbranch@example.com",
                "phone": "+1234567890",
                "address": {
                    "street": "123 Test St",
                    "city": "Test City",
                    "state": "Test State",
                    "zip_code": "12345",
                    "country": "Test Country"
                },
                "coordinates": {
                    "latitude": 0.0,
                    "longitude": 0.0
                }
            }
        }
        
        post_response = requests.post(f"{BASE_URL}/api/branches", json=branch_data, headers=headers, timeout=10)
        print(f"   POST branches status: {post_response.status_code}")
        
        if post_response.status_code == 200:
            post_data = post_response.json()
            print(f"   ✅ SUCCESS! Branch created")
            print(f"   📝 Message: {post_data.get('message', 'N/A')}")
            print(f"   🆔 Branch ID: {post_data.get('branch_id', 'N/A')}")
            return True
        elif post_response.status_code == 401:
            print(f"   ❌ Still getting 401 Unauthorized: {post_response.text}")
            return False
        elif post_response.status_code == 500:
            print(f"   ❌ Server Error: {post_response.text}")
            return False
        else:
            print(f"   ⚠️  Unexpected status: {post_response.status_code} - {post_response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Test failed with exception: {e}")
        return False

def main():
    print("🧪 Branch API Superadmin Token Test")
    print("=" * 60)
    
    success = test_branch_api_with_superadmin()
    
    print(f"\n" + "=" * 60)
    if success:
        print("🎉 SUCCESS! Branch API now accepts superadmin tokens!")
        print("✅ You can now use superadmin tokens for:")
        print("   - GET /api/branches")
        print("   - POST /api/branches") 
        print("   - PUT /api/branches/{branch_id}")
        print("   - Branch holiday management endpoints")
    else:
        print("❌ Issue detected. Branch API still has authentication problems.")
        
    print("\n📖 Usage:")
    print("   1. Get superadmin token: POST /api/superadmin/login")
    print("   2. Use token in Authorization header: Bearer <token>")
    print("   3. Access branch endpoints with superadmin permissions")

if __name__ == "__main__":
    main()
