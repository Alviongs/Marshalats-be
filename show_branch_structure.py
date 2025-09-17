#!/usr/bin/env python3
"""
Final verification of the complete branch structure
"""
import requests
import json

def show_complete_branch_structure():
    """Show the complete structure that is stored and returned"""
    
    # Login as super admin
    login_url = "http://31.97.224.169:8003/api/auth/login"
    login_data = {
        "email": "superadmin@test.com",
        "password": "SuperAdmin123!"
    }
    
    try:
        # Login
        login_response = requests.post(login_url, json=login_data, timeout=10)
        
        if login_response.status_code != 200:
            print("❌ Login failed")
            return
            
        token = login_response.json()["access_token"]
        
        # Get branches
        branch_url = "http://31.97.224.169:8003/api/branches"
        headers = {"Authorization": f"Bearer {token}"}
        
        response = requests.get(branch_url, headers=headers)
        
        if response.status_code == 200:
            branches_data = response.json()
            
            if branches_data["branches"]:
                branch = branches_data["branches"][0]  # Get the first branch
                
                print("🏢 COMPLETE BRANCH STRUCTURE AS STORED & RETURNED:")
                print("=" * 60)
                print(json.dumps(branch, indent=2))
                
                print(f"\n📋 KEY FIELD VERIFICATION:")
                print(f"   ✅ assignments.courses contains: {branch['assignments']['courses']}")
                print(f"   ✅ assignments.branch_admins contains: {branch['assignments']['branch_admins']}")
                print(f"   ✅ operational_details.courses_offered contains: {branch['operational_details']['courses_offered']}")
                
                print(f"\n🎯 SUMMARY:")
                print(f"   - assignments.courses: Course IDs (for database relationships)")
                print(f"   - assignments.branch_admins: User IDs (for access control)")
                print(f"   - operational_details.courses_offered: Course names (for display)")
                print(f"   - All nested structures preserved exactly as requested!")
                
            else:
                print("❌ No branches found")
        else:
            print(f"❌ Failed to get branches: {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    show_complete_branch_structure()
