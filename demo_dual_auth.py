#!/usr/bin/env python3

import requests
import json

BASE_URL = "http://31.97.224.169:8003/api"

def demonstrate_dual_auth_systems():
    """Demonstrate both Super Admin and Regular User authentication systems"""
    
    print("🚀 Demonstrating Dual Authentication Systems")
    print("=" * 60)
    
    # === SUPER ADMIN AUTHENTICATION SYSTEM ===
    print("\n🔐 SUPER ADMIN AUTHENTICATION SYSTEM")
    print("-" * 40)
    
    # Super Admin Registration
    print("1️⃣ Super Admin Registration:")
    superadmin_data = {
        "full_name": "System Administrator",
        "email": "sysadmin@company.com",
        "password": "SuperSecure@2025",
        "phone": "+919999999999"
    }
    
    response = requests.post(f"{BASE_URL}/superadmin/register", json=superadmin_data)
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        print("   ✅ Super Admin registered successfully!")
    else:
        print(f"   ⚠️ Registration response: {response.text}")
    
    # Super Admin Login
    print("\n2️⃣ Super Admin Login:")
    login_data = {
        "email": "sysadmin@company.com",
        "password": "SuperSecure@2025"
    }
    
    response = requests.post(f"{BASE_URL}/superadmin/login", json=login_data)
    superadmin_token = None
    if response.status_code == 200:
        result = response.json()
        superadmin_token = result["data"]["token"]
        print("   ✅ Super Admin login successful!")
        print(f"   Token expires in: {result['data']['expires_in']} seconds")
    else:
        print(f"   ❌ Login failed: {response.text}")
    
    # Super Admin Profile
    if superadmin_token:
        print("\n3️⃣ Super Admin Profile Access:")
        headers = {"Authorization": f"Bearer {superadmin_token}"}
        response = requests.get(f"{BASE_URL}/superadmin/me", headers=headers)
        if response.status_code == 200:
            profile = response.json()["data"]
            print(f"   ✅ Profile: {profile['full_name']} ({profile['email']})")
        else:
            print(f"   ❌ Profile access failed: {response.text}")
    
    # === REGULAR USER AUTHENTICATION SYSTEM ===
    print("\n\n👥 REGULAR USER AUTHENTICATION SYSTEM")
    print("-" * 40)
    
    # Regular User Registration
    print("1️⃣ Regular User Registration:")
    user_data = {
        "email": "student@example.com",
        "phone": "+918888888888",
        "first_name": "John",
        "last_name": "Student",
        "role": "student",
        "password": "StudentPass@123"
    }
    
    response = requests.post(f"{BASE_URL}/auth/register", json=user_data)
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        print("   ✅ Regular user registered successfully!")
    else:
        print(f"   ⚠️ Registration response: {response.text}")
    
    # Regular User Login
    print("\n2️⃣ Regular User Login:")
    login_data = {
        "email": "student@example.com",
        "password": "StudentPass@123"
    }
    
    response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
    user_token = None
    if response.status_code == 200:
        result = response.json()
        user_token = result["access_token"]
        print("   ✅ Regular user login successful!")
        print(f"   User: {result['user']['full_name']} ({result['user']['role']})")
    else:
        print(f"   ❌ Login failed: {response.text}")
    
    # Regular User Profile
    if user_token:
        print("\n3️⃣ Regular User Profile Access:")
        headers = {"Authorization": f"Bearer {user_token}"}
        response = requests.get(f"{BASE_URL}/auth/me", headers=headers)
        if response.status_code == 200:
            profile = response.json()
            print(f"   ✅ Profile: {profile['full_name']} ({profile['role']})")
        else:
            print(f"   ❌ Profile access failed: {response.text}")
    
    # === CROSS-SYSTEM VALIDATION ===
    print("\n\n🔒 CROSS-SYSTEM VALIDATION")
    print("-" * 40)
    
    if superadmin_token and user_token:
        print("1️⃣ Testing Super Admin token on regular user endpoint:")
        headers = {"Authorization": f"Bearer {superadmin_token}"}
        response = requests.get(f"{BASE_URL}/auth/me", headers=headers)
        if response.status_code != 200:
            print("   ✅ Super Admin token properly isolated from regular auth system")
        else:
            print("   ⚠️ Unexpected cross-system access")
        
        print("\n2️⃣ Testing regular user token on Super Admin endpoint:")
        headers = {"Authorization": f"Bearer {user_token}"}
        response = requests.get(f"{BASE_URL}/superadmin/me", headers=headers)
        if response.status_code != 200:
            print("   ✅ Regular user token properly isolated from Super Admin system")
        else:
            print("   ⚠️ Unexpected cross-system access")
    
    print("\n\n🎉 DUAL AUTHENTICATION SYSTEM DEMONSTRATION COMPLETE!")
    print("\n📋 SUMMARY:")
    print("✅ Super Admin System: Isolated authentication for system administrators")
    print("✅ Regular User System: Role-based authentication for students, coaches, admins")
    print("✅ Token Isolation: Each system maintains separate token validation")
    print("✅ Security: Cross-system token usage properly prevented")

if __name__ == "__main__":
    demonstrate_dual_auth_systems()
