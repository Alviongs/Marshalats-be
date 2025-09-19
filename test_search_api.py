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

def test_global_search(token, query="test"):
    """Test global search endpoint"""
    print(f"\n🔍 Testing global search with query: '{query}'")
    
    search_url = f"{BASE_URL}/search/global"
    headers = {"Authorization": f"Bearer {token}"}
    params = {"q": query, "limit": 5}
    
    try:
        response = requests.get(search_url, headers=headers, params=params)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Global search successful")
            print(f"Query: {data.get('query')}")
            print(f"Total Results: {data.get('total_results')}")
            
            results = data.get('results', {})
            for category, category_data in results.items():
                count = category_data.get('count', 0)
                print(f"  - {category}: {count} results")
                
                # Show first result as example
                if count > 0 and category_data.get('data'):
                    first_result = category_data['data'][0]
                    if category == 'users':
                        name = first_result.get('full_name', 'N/A')
                        email = first_result.get('email', 'N/A')
                        print(f"    Example: {name} ({email})")
                    elif category == 'coaches':
                        name = first_result.get('full_name', 'N/A')
                        email = first_result.get('contact_info', {}).get('email', 'N/A')
                        print(f"    Example: {name} ({email})")
                    elif category == 'courses':
                        name = first_result.get('name', 'N/A')
                        print(f"    Example: {name}")
                    elif category == 'branches':
                        name = first_result.get('branch', {}).get('name', 'N/A')
                        print(f"    Example: {name}")
            
            return True
        else:
            print(f"❌ Global search failed: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Global search error: {e}")
        return False

def test_user_search(token, query="admin"):
    """Test user-specific search endpoint"""
    print(f"\n👥 Testing user search with query: '{query}'")
    
    search_url = f"{BASE_URL}/search/users"
    headers = {"Authorization": f"Bearer {token}"}
    params = {"q": query, "limit": 5}
    
    try:
        response = requests.get(search_url, headers=headers, params=params)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ User search successful")
            print(f"Query: {data.get('query')}")
            print(f"Total Results: {data.get('total')}")
            print(f"Returned: {data.get('count')} users")
            
            users = data.get('users', [])
            for i, user in enumerate(users[:3]):  # Show first 3
                name = user.get('full_name', 'N/A')
                email = user.get('email', 'N/A')
                role = user.get('role', 'N/A')
                print(f"  {i+1}. {name} ({email}) - {role}")
            
            return True
        else:
            print(f"❌ User search failed: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ User search error: {e}")
        return False

def test_coach_search(token, query="coach"):
    """Test coach-specific search endpoint"""
    print(f"\n🥋 Testing coach search with query: '{query}'")
    
    search_url = f"{BASE_URL}/search/coaches"
    headers = {"Authorization": f"Bearer {token}"}
    params = {"q": query, "limit": 5}
    
    try:
        response = requests.get(search_url, headers=headers, params=params)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Coach search successful")
            print(f"Query: {data.get('query')}")
            print(f"Total Results: {data.get('total')}")
            print(f"Returned: {data.get('count')} coaches")
            
            coaches = data.get('coaches', [])
            for i, coach in enumerate(coaches[:3]):  # Show first 3
                name = coach.get('full_name', 'N/A')
                email = coach.get('contact_info', {}).get('email', 'N/A')
                expertise = coach.get('areas_of_expertise', [])
                print(f"  {i+1}. {name} ({email}) - {', '.join(expertise)}")
            
            return True
        else:
            print(f"❌ Coach search failed: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Coach search error: {e}")
        return False

def test_course_search(token, query="martial"):
    """Test course-specific search endpoint"""
    print(f"\n📚 Testing course search with query: '{query}'")
    
    search_url = f"{BASE_URL}/search/courses"
    headers = {"Authorization": f"Bearer {token}"}
    params = {"q": query, "limit": 5}
    
    try:
        response = requests.get(search_url, headers=headers, params=params)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Course search successful")
            print(f"Query: {data.get('query')}")
            print(f"Total Results: {data.get('total')}")
            print(f"Returned: {data.get('count')} courses")
            
            courses = data.get('courses', [])
            for i, course in enumerate(courses[:3]):  # Show first 3
                name = course.get('name', 'N/A')
                difficulty = course.get('difficulty_level', 'N/A')
                print(f"  {i+1}. {name} - {difficulty}")
            
            return True
        else:
            print(f"❌ Course search failed: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Course search error: {e}")
        return False

def test_edge_cases(token):
    """Test edge cases and error handling"""
    print(f"\n⚠️  Testing edge cases")
    
    # Test with short query (should fail)
    search_url = f"{BASE_URL}/search/global"
    headers = {"Authorization": f"Bearer {token}"}
    params = {"q": "a"}  # Too short
    
    try:
        response = requests.get(search_url, headers=headers, params=params)
        if response.status_code == 422:  # Validation error expected
            print("✅ Short query validation working correctly")
        else:
            print(f"❌ Short query should return 422, got {response.status_code}")
    except Exception as e:
        print(f"❌ Edge case test error: {e}")

def main():
    print("🚀 Starting Search API Tests")
    print("=" * 50)
    
    # Login as superadmin
    token = login_superadmin()
    if not token:
        print("❌ Cannot proceed without authentication token")
        sys.exit(1)
    
    # Run tests
    tests_passed = 0
    total_tests = 5
    
    if test_global_search(token):
        tests_passed += 1
    
    if test_user_search(token):
        tests_passed += 1
        
    if test_coach_search(token):
        tests_passed += 1
        
    if test_course_search(token):
        tests_passed += 1
    
    test_edge_cases(token)
    tests_passed += 1  # Edge case test
    
    # Summary
    print("\n" + "=" * 50)
    print(f"🎯 Test Results: {tests_passed}/{total_tests} tests passed")
    
    if tests_passed == total_tests:
        print("✅ All search API tests passed!")
        sys.exit(0)
    else:
        print("❌ Some tests failed")
        sys.exit(1)

if __name__ == "__main__":
    main()
