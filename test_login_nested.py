#!/usr/bin/env python3
"""
Test login to verify nested objects are returned correctly
"""
import requests
import json

def test_login_with_nested_structure():
    """Test login and verify nested objects in response"""
    
    login_url = "http://localhost:8003/api/auth/login"
    
    # Login with the fresh user
    login_data = {
        "email": "fresh.test@example.com",
        "password": "FreshPass123!"
    }
    
    try:
        print("🔐 Testing login with nested structure...")
        print(f"Logging in: {login_data['email']}")
        
        response = requests.post(login_url, json=login_data, timeout=10)
        
        if response.status_code == 200:
            login_result = response.json()
            print("✅ Login successful!")
            
            print("\n📊 Login Response:")
            print("=" * 50)
            print(json.dumps(login_result, indent=2))
            
            # Check the user object structure
            user_data = login_result.get("user", {})
            
            print(f"\n📋 Response Structure Check:")
            has_nested_course = isinstance(user_data.get("course"), dict)
            has_nested_branch = isinstance(user_data.get("branch"), dict)
            
            print(f"✅ Has nested course object: {has_nested_course}")
            print(f"✅ Has nested branch object: {has_nested_branch}")
            
            if has_nested_course:
                course = user_data["course"]
                print(f"   - Course category_id: {course.get('category_id')}")
                print(f"   - Course course_id: {course.get('course_id')}")
                print(f"   - Course duration: {course.get('duration')}")
                
            if has_nested_branch:
                branch = user_data["branch"]
                print(f"   - Branch location_id: {branch.get('location_id')}")
                print(f"   - Branch branch_id: {branch.get('branch_id')}")
            
            if has_nested_course and has_nested_branch:
                print("\n🎉 SUCCESS: Login returns nested structure correctly!")
                print("✅ API now stores AND returns data exactly as requested!")
            else:
                print("\n⚠️  Login response doesn't have proper nested structure")
                
        else:
            print(f"❌ Login failed: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_login_with_nested_structure()
