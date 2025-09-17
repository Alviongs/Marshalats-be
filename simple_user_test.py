#!/usr/bin/env python3
"""
Simple test to verify user list API
"""
import requests

def simple_test():
    try:
        # Test login first
        print("Testing superadmin login...")
        login_data = {
            "email": "testsuperadmin@example.com",
            "password": "TestSuperAdmin123!"
        }
        
        login_response = requests.post("http://31.97.224.169:8003/api/superadmin/login", json=login_data)
        print(f"Login response: {login_response.status_code}")
        
        if login_response.status_code == 200:
            token = login_response.json()["data"]["token"]
            print("Login successful, testing user list...")
            
            # Test user list
            headers = {"Authorization": f"Bearer {token}"}
            user_response = requests.get("http://31.97.224.169:8003/api/users", headers=headers)
            
            print(f"User list response: {user_response.status_code}")
            if user_response.status_code == 200:
                data = user_response.json()
                print(f"SUCCESS! Found {data.get('total', 0)} users")
                return True
            else:
                print(f"Error: {user_response.text}")
                return False
        else:
            print(f"Login failed: {login_response.text}")
            return False
            
    except Exception as e:
        print(f"Exception: {e}")
        return False

if __name__ == "__main__":
    simple_test()
