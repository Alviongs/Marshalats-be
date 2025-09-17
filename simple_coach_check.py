#!/usr/bin/env python3
"""
Simple script to check coach data structure via API
"""

import requests
import json

BASE_URL = "http://31.97.224.169:8003"

def check_coach_data():
    """Check coach data structure via API"""
    
    print("🔍 Checking coach data structure via API...")
    
    try:
        # Get superadmin token
        superadmin_login = {
            "email": "testsuperadmin@example.com",
            "password": "TestSuperAdmin123!"
        }
        
        admin_response = requests.post(f"{BASE_URL}/api/superadmin/login", json=superadmin_login)
        if admin_response.status_code != 200:
            print(f"❌ Can't get admin token: {admin_response.text}")
            return
            
        admin_token = admin_response.json()["data"]["token"]
        admin_headers = {"Authorization": f"Bearer {admin_token}"}
        
        # Get coaches data
        coaches_response = requests.get(f"{BASE_URL}/api/coaches", headers=admin_headers)
        if coaches_response.status_code == 200:
            coaches_data = coaches_response.json()
            
            if coaches_data.get("coaches"):
                sample_coach = coaches_data["coaches"][0]
                print("✅ Found coach data")
                print("\nCoach structure:")
                
                def print_structure(obj, indent=0):
                    spaces = "  " * indent
                    if isinstance(obj, dict):
                        for key, value in obj.items():
                            if "password" in key.lower():
                                print(f"{spaces}{key}: [PASSWORD FIELD]")
                            elif isinstance(value, dict):
                                print(f"{spaces}{key}:")
                                print_structure(value, indent + 1)
                            elif isinstance(value, list):
                                print(f"{spaces}{key}: [list with {len(value)} items]")
                            else:
                                print(f"{spaces}{key}: {type(value).__name__}")
                
                print_structure(sample_coach)
            else:
                print("❌ No coaches found in response")
        else:
            print(f"❌ Failed to get coaches: {coaches_response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    check_coach_data()
