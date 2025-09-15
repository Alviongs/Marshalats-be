#!/usr/bin/env python3

import requests
import json
import sys

# API Configuration
BASE_URL = "http://localhost:8003"
SUPERADMIN_EMAIL = "pittisunilkumar3@gmail.com"
SUPERADMIN_PASSWORD = "StrongPassword@123"

def login_superadmin():
    """Login as superadmin and get token"""
    login_url = f"{BASE_URL}/superadmin/login"
    login_data = {
        "email": SUPERADMIN_EMAIL,
        "password": SUPERADMIN_PASSWORD
    }
    
    try:
        response = requests.post(login_url, json=login_data)
        if response.status_code == 200:
            data = response.json()
            if data.get("status") == "success":
                token = data["data"]["token"]
                print(f"✅ Superadmin login successful")
                return token
            else:
                print(f"❌ Login failed: {data}")
                return None
        else:
            print(f"❌ Login request failed: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"❌ Login error: {e}")
        return None

def test_user_detail_endpoint(token):
    """Test GET /users/{user_id} endpoint"""
    print(f"\n👤 Testing User Detail Endpoint")
    
    # First get list of users to get an ID
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        # Get users list
        response = requests.get(f"{BASE_URL}/users", headers=headers)
        if response.status_code == 200:
            data = response.json()
            users = data.get('users', [])
            if users:
                user_id = users[0]['id']
                print(f"Testing with user ID: {user_id}")
                
                # Test individual user endpoint
                response = requests.get(f"{BASE_URL}/users/{user_id}", headers=headers)
                print(f"Status Code: {response.status_code}")
                
                if response.status_code == 200:
                    user_data = response.json()
                    print(f"✅ User detail endpoint working")
                    print(f"User: {user_data.get('user', {}).get('full_name', 'N/A')}")
                    print(f"Email: {user_data.get('user', {}).get('email', 'N/A')}")
                    print(f"Role: {user_data.get('user', {}).get('role', 'N/A')}")
                    return True
                else:
                    print(f"❌ User detail failed: {response.text}")
                    return False
            else:
                print("❌ No users found to test with")
                return False
        else:
            print(f"❌ Failed to get users list: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ User detail test error: {e}")
        return False

def test_coach_detail_endpoint(token):
    """Test GET /coaches/{coach_id} endpoint"""
    print(f"\n🥋 Testing Coach Detail Endpoint")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        # Get coaches list
        response = requests.get(f"{BASE_URL}/coaches", headers=headers)
        if response.status_code == 200:
            data = response.json()
            coaches = data.get('coaches', [])
            if coaches:
                coach_id = coaches[0]['id']
                print(f"Testing with coach ID: {coach_id}")
                
                # Test individual coach endpoint
                response = requests.get(f"{BASE_URL}/coaches/{coach_id}", headers=headers)
                print(f"Status Code: {response.status_code}")
                
                if response.status_code == 200:
                    coach_data = response.json()
                    print(f"✅ Coach detail endpoint working")
                    print(f"Coach: {coach_data.get('full_name', 'N/A')}")
                    print(f"Email: {coach_data.get('contact_info', {}).get('email', 'N/A')}")
                    print(f"Expertise: {', '.join(coach_data.get('areas_of_expertise', []))}")
                    return True
                else:
                    print(f"❌ Coach detail failed: {response.text}")
                    return False
            else:
                print("❌ No coaches found to test with")
                return False
        else:
            print(f"❌ Failed to get coaches list: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Coach detail test error: {e}")
        return False

def test_course_detail_endpoint(token):
    """Test GET /courses/{course_id} endpoint"""
    print(f"\n📚 Testing Course Detail Endpoint")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        # Get courses list
        response = requests.get(f"{BASE_URL}/courses", headers=headers)
        if response.status_code == 200:
            data = response.json()
            courses = data.get('courses', [])
            if courses:
                course_id = courses[0]['id']
                print(f"Testing with course ID: {course_id}")
                
                # Test individual course endpoint
                response = requests.get(f"{BASE_URL}/courses/{course_id}", headers=headers)
                print(f"Status Code: {response.status_code}")
                
                if response.status_code == 200:
                    course_data = response.json()
                    print(f"✅ Course detail endpoint working")
                    print(f"Course: {course_data.get('name', 'N/A')}")
                    print(f"Difficulty: {course_data.get('difficulty_level', 'N/A')}")
                    print(f"Description: {course_data.get('description', 'N/A')[:50]}...")
                    return True
                else:
                    print(f"❌ Course detail failed: {response.text}")
                    return False
            else:
                print("❌ No courses found to test with")
                return False
        else:
            print(f"❌ Failed to get courses list: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Course detail test error: {e}")
        return False

def test_branch_detail_endpoint(token):
    """Test GET /branches/{branch_id} endpoint"""
    print(f"\n🏢 Testing Branch Detail Endpoint")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        # Get branches list
        response = requests.get(f"{BASE_URL}/branches", headers=headers)
        if response.status_code == 200:
            data = response.json()
            branches = data.get('branches', [])
            if branches:
                branch_id = branches[0]['id']
                print(f"Testing with branch ID: {branch_id}")
                
                # Test individual branch endpoint
                response = requests.get(f"{BASE_URL}/branches/{branch_id}", headers=headers)
                print(f"Status Code: {response.status_code}")
                
                if response.status_code == 200:
                    branch_data = response.json()
                    print(f"✅ Branch detail endpoint working")
                    print(f"Branch: {branch_data.get('branch', {}).get('name', 'N/A')}")
                    print(f"City: {branch_data.get('branch', {}).get('address', {}).get('city', 'N/A')}")
                    print(f"Active: {branch_data.get('is_active', 'N/A')}")
                    return True
                else:
                    print(f"❌ Branch detail failed: {response.text}")
                    return False
            else:
                print("❌ No branches found to test with")
                return False
        else:
            print(f"❌ Failed to get branches list: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Branch detail test error: {e}")
        return False

def main():
    print("🚀 Testing Detail API Endpoints")
    print("=" * 50)
    
    # Login as superadmin
    token = login_superadmin()
    if not token:
        print("❌ Cannot proceed without authentication token")
        sys.exit(1)
    
    # Run tests
    tests_passed = 0
    total_tests = 4
    
    if test_user_detail_endpoint(token):
        tests_passed += 1
    
    if test_coach_detail_endpoint(token):
        tests_passed += 1
        
    if test_course_detail_endpoint(token):
        tests_passed += 1
        
    if test_branch_detail_endpoint(token):
        tests_passed += 1
    
    # Summary
    print("\n" + "=" * 50)
    print(f"🎯 Test Results: {tests_passed}/{total_tests} detail endpoints working")
    
    if tests_passed == total_tests:
        print("✅ All detail API endpoints are working!")
        sys.exit(0)
    else:
        print("❌ Some detail endpoints need attention")
        sys.exit(1)

if __name__ == "__main__":
    main()
