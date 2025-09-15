#!/usr/bin/env python3

import asyncio
import aiohttp
import json

async def test_branch_courses():
    """Test the new branch courses endpoint"""
    
    # First, login as superadmin to get token
    login_data = {
        "email": "pittisunilkumar3@gmail.com",
        "password": "StrongPassword@123"
    }
    
    async with aiohttp.ClientSession() as session:
        # Login
        print("🔐 Logging in as superadmin...")
        async with session.post("http://localhost:8003/api/superadmin/login", json=login_data) as response:
            if response.status == 200:
                login_result = await response.json()
                token = login_result.get("access_token") or login_result.get("token") or login_result.get("data", {}).get("token")
                if token:
                    print(f"✅ Login successful! Token: {token[:50]}...")
                else:
                    print(f"❌ No token in response: {login_result}")
                    return
            else:
                error_text = await response.text()
                print(f"❌ Login failed: {response.status} - {error_text}")
                return
        
        # Get branches first to find a branch ID
        print("\n📋 Getting branches...")
        headers = {"Authorization": f"Bearer {token}"}
        async with session.get("http://localhost:8003/api/branches", headers=headers) as response:
            if response.status == 200:
                branches_result = await response.json()
                branches = branches_result.get("branches", [])
                if branches:
                    branch_id = branches[0]["id"]
                    branch_name = branches[0]["branch"]["name"]
                    print(f"✅ Found branch: {branch_name} (ID: {branch_id})")
                else:
                    print("❌ No branches found")
                    return
            else:
                print(f"❌ Failed to get branches: {response.status}")
                return
        
        # Test the new endpoint
        print(f"\n🎯 Testing courses for branch: {branch_id}")
        async with session.get(f"http://localhost:8003/api/courses/by-branch/{branch_id}", headers=headers) as response:
            if response.status == 200:
                courses_result = await response.json()
                courses = courses_result.get("courses", [])
                total = courses_result.get("total", 0)
                print(f"✅ Success! Found {total} courses for branch {branch_name}")
                
                for i, course in enumerate(courses[:3], 1):  # Show first 3 courses
                    print(f"  {i}. {course.get('name', 'Unknown')} - {course.get('difficulty_level', 'N/A')} - {course.get('enrolled_students', 0)} students")
                
                if len(courses) > 3:
                    print(f"  ... and {len(courses) - 3} more courses")
                    
            elif response.status == 404:
                print(f"❌ Branch not found: {branch_id}")
            else:
                error_text = await response.text()
                print(f"❌ Failed to get courses: {response.status} - {error_text}")

if __name__ == "__main__":
    asyncio.run(test_branch_courses())
