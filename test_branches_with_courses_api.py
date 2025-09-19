#!/usr/bin/env python3
"""
Test script for the new branches-with-courses API endpoint
"""

import requests
import json
from pathlib import Path

# Configuration
BASE_URL = "http://localhost:8003"
TOKEN_FILE = Path(__file__).parent / "admin_token.txt"

def get_admin_token():
    """Get admin token from file"""
    try:
        with open(TOKEN_FILE, 'r') as f:
            return f.read().strip()
    except FileNotFoundError:
        print(f"❌ Token file not found: {TOKEN_FILE}")
        return None

def make_request(endpoint, params=None):
    """Make authenticated request to API"""
    token = get_admin_token()
    if not token:
        return None
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    url = f"{BASE_URL}{endpoint}"
    try:
        response = requests.get(url, headers=headers, params=params or {})
        return response
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
        return None

def test_basic_endpoint():
    """Test basic endpoint without parameters"""
    print("🧪 Testing basic endpoint...")
    response = make_request("/api/branches-with-courses")
    
    if not response:
        return False
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Success! Found {data.get('total', 0)} branches")
        print(f"   Summary: {data.get('summary', {})}")
        return True
    else:
        print(f"❌ Failed with status {response.status_code}: {response.text}")
        return False

def test_branch_filtering():
    """Test branch ID filtering"""
    print("\n🧪 Testing branch ID filtering...")
    
    # First get all branches to find a valid ID
    response = make_request("/api/branches-with-courses")
    if not response or response.status_code != 200:
        print("❌ Could not get branches for filtering test")
        return False
    
    data = response.json()
    branches = data.get('branches', [])
    
    if not branches:
        print("⚠️  No branches found for filtering test")
        return True
    
    # Test with first branch ID
    branch_id = branches[0]['id']
    print(f"   Testing with branch ID: {branch_id}")
    
    response = make_request("/api/branches-with-courses", {"branch_id": branch_id})
    if response and response.status_code == 200:
        filtered_data = response.json()
        if filtered_data.get('total') == 1:
            print(f"✅ Branch filtering works! Got 1 branch as expected")
            return True
        else:
            print(f"❌ Expected 1 branch, got {filtered_data.get('total')}")
            return False
    else:
        print(f"❌ Branch filtering failed: {response.status_code if response else 'No response'}")
        return False

def test_invalid_branch():
    """Test error handling for invalid branch ID"""
    print("\n🧪 Testing invalid branch ID...")
    response = make_request("/api/branches-with-courses", {"branch_id": "invalid-branch-id"})
    
    if response and response.status_code == 404:
        print("✅ Error handling works! Got 404 for invalid branch ID")
        return True
    else:
        print(f"❌ Expected 404, got {response.status_code if response else 'No response'}")
        return False

def test_status_filtering():
    """Test status filtering"""
    print("\n🧪 Testing status filtering...")
    
    # Test active branches
    response = make_request("/api/branches-with-courses", {"status": "active"})
    if response and response.status_code == 200:
        data = response.json()
        print(f"✅ Active branches: {data.get('total', 0)}")
        
        # Test inactive branches
        response = make_request("/api/branches-with-courses", {"status": "inactive"})
        if response and response.status_code == 200:
            inactive_data = response.json()
            print(f"✅ Inactive branches: {inactive_data.get('total', 0)}")
            return True
    
    print("❌ Status filtering test failed")
    return False

def test_authentication():
    """Test authentication requirement"""
    print("\n🧪 Testing authentication...")
    
    try:
        response = requests.get(f"{BASE_URL}/api/branches-with-courses")
        if response.status_code == 401:
            print("✅ Authentication required! Got 401 without token")
            return True
        else:
            print(f"❌ Expected 401, got {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Authentication test failed: {e}")
        return False

def test_response_structure():
    """Test response structure matches expected format"""
    print("\n🧪 Testing response structure...")
    response = make_request("/api/branches-with-courses")
    
    if not response or response.status_code != 200:
        print("❌ Could not get response for structure test")
        return False
    
    data = response.json()
    required_fields = ['message', 'branches', 'total', 'summary', 'filters_applied']
    
    for field in required_fields:
        if field not in data:
            print(f"❌ Missing required field: {field}")
            return False
    
    # Check summary structure
    summary = data.get('summary', {})
    summary_fields = ['total_branches', 'total_courses', 'total_students', 'total_coaches']
    
    for field in summary_fields:
        if field not in summary:
            print(f"❌ Missing summary field: {field}")
            return False
    
    # Check branch structure if branches exist
    branches = data.get('branches', [])
    if branches:
        branch = branches[0]
        branch_fields = ['id', 'branch', 'is_active', 'courses', 'statistics']
        
        for field in branch_fields:
            if field not in branch:
                print(f"❌ Missing branch field: {field}")
                return False
    
    print("✅ Response structure is correct!")
    return True

def main():
    """Run all tests"""
    print("🚀 Testing Branches with Courses API Endpoint")
    print("=" * 50)
    
    tests = [
        test_basic_endpoint,
        test_branch_filtering,
        test_invalid_branch,
        test_status_filtering,
        test_authentication,
        test_response_structure
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! The API is working correctly.")
    else:
        print("⚠️  Some tests failed. Please check the implementation.")
    
    return passed == total

if __name__ == "__main__":
    main()
