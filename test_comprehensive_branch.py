#!/usr/bin/env python3
"""
Test script for the comprehensive branch create API
"""
import requests
import json
import asyncio
import motor.motor_asyncio
import os

def test_comprehensive_branch_creation():
    """Test the new comprehensive branch create API"""
    
    # First, let's test login to get a token (assuming we have a super admin user)
    login_url = "http://31.97.224.169:8003/api/auth/login"
    
    # You'll need to create a super admin user first or use existing credentials
    login_data = {
        "email": "fresh.test@example.com",  # Replace with actual super admin email
        "password": "FreshPass123!"  # Replace with actual password
    }
    
    # Test branch data with comprehensive structure
    branch_data = {
        "branch": {
            "name": "Rock martial arts",
            "code": "RMA01",
            "email": "yourname@email.com",
            "phone": "+13455672356",
            "address": {
                "line1": "928#123",
                "area": "Madhapur",
                "city": "Hyderabad",
                "state": "Telangana",
                "pincode": "500089",
                "country": "India"
            }
        },
        "manager_id": "manager-uuid-1234",
        "operational_details": {
            "courses_offered": ["Rock martial arts"],
            "timings": [
                {"day": "Monday", "open": "07:00", "close": "19:00"},
                {"day": "Tuesday", "open": "07:00", "close": "19:00"}
            ],
            "holidays": ["2025-10-02", "2025-12-25"]
        },
        "assignments": {
            "accessories_available": True,
            "courses": ["Taekwondo", "Karate", "Kung Fu"],
            "branch_admins": ["coach-uuid-1", "coach-uuid-2"]
        },
        "bank_details": {
            "bank_name": "State Bank of India",
            "account_number": "XXXXXXXXXXXX",
            "upi_id": "name@ybl"
        }
    }
    
    try:
        print("🔐 Attempting to login...")
        login_response = requests.post(login_url, json=login_data, timeout=10)
        
        if login_response.status_code != 200:
            print("❌ Login failed. Please create a super admin user first or check credentials.")
            print(f"Login response: {login_response.text}")
            return
            
        token = login_response.json()["access_token"]
        print("✅ Login successful!")
        
        # Test branch creation
        branch_url = "http://31.97.224.169:8003/api/branches"
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        print(f"\n🏢 Testing comprehensive branch creation...")
        print(f"Request data: {json.dumps(branch_data, indent=2)}")
        print("-" * 50)
        
        response = requests.post(branch_url, json=branch_data, headers=headers, timeout=10)
        
        print(f"Status Code: {response.status_code}")
        print(f"Response Body: {response.text}")
        
        if response.status_code == 200:
            result = response.json()
            branch_id = result["branch_id"]
            print("✅ Branch creation successful!")
            
            # Test getting the created branch
            print(f"\n🔍 Testing get branch by ID...")
            get_response = requests.get(f"{branch_url}/{branch_id}", headers=headers)
            
            if get_response.status_code == 200:
                branch_details = get_response.json()
                print("✅ Branch retrieval successful!")
                print(f"Retrieved branch: {json.dumps(branch_details, indent=2)}")
                
                # Verify nested structure
                print(f"\n📋 Structure Verification:")
                has_nested_branch = isinstance(branch_details.get("branch"), dict)
                has_operational_details = isinstance(branch_details.get("operational_details"), dict)
                has_assignments = isinstance(branch_details.get("assignments"), dict)
                has_bank_details = isinstance(branch_details.get("bank_details"), dict)
                
                print(f"✅ Nested branch info: {has_nested_branch}")
                print(f"✅ Operational details: {has_operational_details}")
                print(f"✅ Assignments: {has_assignments}")
                print(f"✅ Bank details: {has_bank_details}")
                
                if all([has_nested_branch, has_operational_details, has_assignments, has_bank_details]):
                    print("\n🎉 SUCCESS: Branch API stores and returns comprehensive nested structure!")
                else:
                    print("\n⚠️  Some nested structures are missing")
            else:
                print(f"❌ Failed to retrieve branch: {get_response.text}")
                
        else:
            print(f"⚠️  Branch creation failed with status code: {response.status_code}")
            print(f"Error details: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to the server. Make sure it's running on http://31.97.224.169:8003")
    except requests.exceptions.Timeout:
        print("❌ Request timed out")
    except Exception as e:
        print(f"❌ Error: {e}")

async def check_database_branch_storage():
    """Check how branch data is stored in MongoDB"""
    mongo_url = os.getenv("MONGO_URL", "mongodb://localhost:27017")
    client = motor.motor_asyncio.AsyncIOMotorClient(mongo_url)
    db = client.student_management_db
    
    # Find the most recent branch
    branch = await db.branches.find_one(
        {}, 
        sort=[("created_at", -1)]
    )
    
    if branch:
        print("\n📊 Latest branch data stored in MongoDB:")
        print("=" * 50)
        
        # Remove internal fields for display
        display_branch = {k: v for k, v in branch.items() if k not in ['_id']}
        print(json.dumps(display_branch, indent=2, default=str))
    else:
        print("❌ No branch found in database")
    
    client.close()

if __name__ == "__main__":
    test_comprehensive_branch_creation()
    print(f"\n{'='*50}")
    print("Checking database storage...")
    asyncio.run(check_database_branch_storage())
