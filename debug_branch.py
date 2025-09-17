#!/usr/bin/env python3

import asyncio
import aiohttp
import json

async def debug_branch():
    """Debug the branch data structure"""
    
    # First, login as superadmin to get token
    login_data = {
        "email": "pittisunilkumar3@gmail.com",
        "password": "StrongPassword@123"
    }
    
    async with aiohttp.ClientSession() as session:
        # Login
        print("🔐 Logging in as superadmin...")
        async with session.post("http://31.97.224.169:8003/api/superadmin/login", json=login_data) as response:
            if response.status == 200:
                login_result = await response.json()
                token = login_result.get("access_token") or login_result.get("token") or login_result.get("data", {}).get("token")
                if token:
                    print(f"✅ Login successful!")
                else:
                    print(f"❌ No token in response")
                    return
            else:
                error_text = await response.text()
                print(f"❌ Login failed: {response.status} - {error_text}")
                return
        
        # Get specific branch details
        branch_id = "98ba0e20-3cce-48fa-8897-f17a8a5213fc"
        print(f"\n📋 Getting branch details for: {branch_id}")
        headers = {"Authorization": f"Bearer {token}"}
        async with session.get(f"http://31.97.224.169:8003/api/branches/{branch_id}", headers=headers) as response:
            if response.status == 200:
                branch_result = await response.json()
                print(f"✅ Branch found!")
                print(f"Branch structure:")
                print(json.dumps(branch_result, indent=2))
                
                # Check assignments
                assignments = branch_result.get("assignments", {})
                courses = assignments.get("courses", [])
                print(f"\n🎯 Course assignments: {courses}")
                print(f"Number of assigned courses: {len(courses)}")
                
            else:
                error_text = await response.text()
                print(f"❌ Failed to get branch: {response.status} - {error_text}")

if __name__ == "__main__":
    asyncio.run(debug_branch())
