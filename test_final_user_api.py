#!/usr/bin/env python3
"""
Final test to verify the user list API is working
"""
import requests
import json

def test_user_api_final():
    BASE_URL = "http://31.97.224.169:8003"
    
    print("🔬 Final User List API Test")
    print("=" * 40)
    
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
            return
            
        token = login_response.json()["data"]["token"]
        print("   ✅ Login successful")
        
        # Step 2: Test user list API
        print("\n2. Testing user list API...")
        headers = {"Authorization": f"Bearer {token}"}
        
        user_response = requests.get(f"{BASE_URL}/api/users", headers=headers, timeout=10)
        print(f"   API status: {user_response.status_code}")
        
        if user_response.status_code == 200:
            data = user_response.json()
            print("   ✅ SUCCESS! User list API is working!")
            print(f"   📊 Total users: {data.get('total', 0)}")
            print(f"   📋 Retrieved: {len(data.get('users', []))} users")
            print(f"   💬 Message: {data.get('message', 'N/A')}")
            
            # Show sample user data
            users = data.get('users', [])
            if users:
                print(f"\n   👥 Sample users:")
                for i, user in enumerate(users[:3]):
                    print(f"      {i+1}. {user.get('full_name', 'N/A')} ({user.get('role', 'N/A')})")
            else:
                print("   📭 No users found in database")
                
        elif user_response.status_code == 500:
            print(f"   ❌ Server Error: {user_response.text}")
            print("   This indicates there's still an issue with the implementation")
            
        elif user_response.status_code == 401:
            print(f"   ❌ Authentication failed: {user_response.text}")
            
        else:
            print(f"   ❓ Unexpected status {user_response.status_code}: {user_response.text}")
            
        # Step 3: Test with coach token
        print("\n3. Testing with coach token...")
        coach_login = {
            "email": "testlogincoach@example.com",
            "password": "TestCoachLogin123!"
        }
        
        coach_response = requests.post(f"{BASE_URL}/api/coaches/login", json=coach_login, timeout=10)
        print(f"   Coach login status: {coach_response.status_code}")
        
        if coach_response.status_code == 200:
            coach_token = coach_response.json()["access_token"]
            coach_headers = {"Authorization": f"Bearer {coach_token}"}
            
            coach_user_response = requests.get(f"{BASE_URL}/api/users", headers=coach_headers, timeout=10)
            print(f"   Coach API status: {coach_user_response.status_code}")
            
            if coach_user_response.status_code == 200:
                coach_data = coach_user_response.json()
                print(f"   ✅ Coach can access user list!")
                print(f"   📊 Coach sees {coach_data.get('total', 0)} users")
            else:
                print(f"   ❌ Coach access failed: {coach_user_response.text}")
        else:
            print(f"   ⚠️  Coach login failed: {coach_response.text}")
            
    except Exception as e:
        print(f"❌ Test failed with exception: {e}")
        
    print("\n" + "=" * 40)
    print("🏁 Test completed!")

if __name__ == "__main__":
    test_user_api_final()
