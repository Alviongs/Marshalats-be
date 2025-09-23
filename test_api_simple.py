#!/usr/bin/env python3
"""
Simple test script for Branch Manager API endpoints
"""

import requests
import json

# Configuration
BASE_URL = "http://localhost:8003"
SUPERADMIN_EMAIL = "pittisunilkumar3@gmail.com"
SUPERADMIN_PASSWORD = "StrongPassword@123"

def test_health():
    """Test if server is running"""
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        print(f"✅ Server health check: {response.status_code} - {response.json()}")
        return True
    except Exception as e:
        print(f"❌ Server not responding: {e}")
        return False

def test_superadmin_login():
    """Test superadmin login"""
    try:
        response = requests.post(
            f"{BASE_URL}/api/superadmin/login",
            json={
                "email": SUPERADMIN_EMAIL,
                "password": SUPERADMIN_PASSWORD
            },
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            token = data.get("access_token")
            print(f"✅ Superadmin login successful: {token[:20]}...")
            return token
        else:
            print(f"❌ Superadmin login failed: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"❌ Login error: {e}")
        return None

def test_branch_managers_list(token):
    """Test getting branch managers list"""
    try:
        response = requests.get(
            f"{BASE_URL}/api/branch-managers",
            headers={"Authorization": f"Bearer {token}"},
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Branch managers list: {len(data.get('branch_managers', []))} managers found")
            print(f"   Total count: {data.get('total_count', 0)}")
            return True
        else:
            print(f"❌ Branch managers list failed: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ List error: {e}")
        return False

def main():
    print("🚀 Testing Branch Manager API")
    print("=" * 40)
    
    # Test server health
    if not test_health():
        print("❌ Server is not running. Please start the server first.")
        return
    
    # Test superadmin login
    token = test_superadmin_login()
    if not token:
        print("❌ Cannot proceed without authentication token")
        return
    
    # Test branch managers list
    test_branch_managers_list(token)
    
    print("=" * 40)
    print("🏁 API test completed")

if __name__ == "__main__":
    main()
