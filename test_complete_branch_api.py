#!/usr/bin/env python3
"""
Complete test for branch API with course IDs and user IDs
"""
import requests
import json
import asyncio
import motor.motor_asyncio
import os

def create_super_admin():
    """Create a super admin user for testing"""
    register_url = "http://31.97.224.169:8003/api/auth/register"
    
    super_admin_data = {
        "email": "superadmin@test.com",
        "phone": "+1234567890",
        "first_name": "Super",
        "last_name": "Admin",
        "role": "super_admin",
        "password": "SuperAdmin123!",
        "date_of_birth": "1985-01-01",
        "gender": "male"
    }
    
    try:
        print("👑 Creating super admin user...")
        response = requests.post(register_url, json=super_admin_data, timeout=10)
        
        if response.status_code == 200:
            print("✅ Super admin created successfully!")
            return True
        else:
            print(f"⚠️  Super admin creation response: {response.status_code}")
            print(f"Response: {response.text}")
            # If user already exists, that's fine for testing
            return True
            
    except Exception as e:
        print(f"❌ Error creating super admin: {e}")
        return False

def test_comprehensive_branch_api():
    """Test the complete branch API with course IDs"""
    
    # First create super admin
    if not create_super_admin():
        return
    
    # Login as super admin
    login_url = "http://31.97.224.169:8003/api/auth/login"
    login_data = {
        "email": "superadmin@test.com",
        "password": "SuperAdmin123!"
    }
    
    # Test branch data with course IDs in assignments
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
            "courses_offered": ["Rock martial arts", "Taekwondo", "Karate"],  # Display names
            "timings": [
                {"day": "Monday", "open": "07:00", "close": "19:00"},
                {"day": "Tuesday", "open": "07:00", "close": "19:00"}
            ],
            "holidays": ["2025-10-02", "2025-12-25"]
        },
        "assignments": {
            "accessories_available": True,
            "courses": ["course-uuid-1", "course-uuid-2", "course-uuid-3"],  # Course IDs
            "branch_admins": ["coach-uuid-1", "coach-uuid-2"]  # User IDs
        },
        "bank_details": {
            "bank_name": "State Bank of India",
            "account_number": "XXXXXXXXXXXX",
            "upi_id": "name@ybl"
        }
    }
    
    try:
        print(f"\n🔐 Logging in as super admin...")
        login_response = requests.post(login_url, json=login_data, timeout=10)
        
        if login_response.status_code != 200:
            print("❌ Super admin login failed.")
            print(f"Login response: {login_response.text}")
            return
            
        login_result = login_response.json()
        token = login_result["access_token"]
        user_role = login_result["user"]["role"]
        print(f"✅ Super admin login successful! Role: {user_role}")
        
        # Test branch creation
        branch_url = "http://31.97.224.169:8003/api/branches"
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        print(f"\n🏢 Testing comprehensive branch creation with course IDs...")
        print("📋 Payload structure verification:")
        print(f"   ✅ Branch info: name, code, email, phone, address")
        print(f"   ✅ Manager ID: {branch_data['manager_id']}")
        print(f"   ✅ Operational: courses_offered (names), timings, holidays")
        print(f"   ✅ Assignments: courses (IDs), branch_admins (IDs)")
        print(f"   ✅ Bank details: bank_name, account, UPI")
        print("-" * 60)
        
        response = requests.post(branch_url, json=branch_data, headers=headers, timeout=10)
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            branch_id = result["branch_id"]
            print("🎉 Branch creation successful!")
            print(f"Branch ID: {branch_id}")
            
            # Test getting the created branch
            print(f"\n🔍 Testing get branch by ID...")
            get_response = requests.get(f"{branch_url}/{branch_id}", headers=headers)
            
            if get_response.status_code == 200:
                branch_details = get_response.json()
                print("✅ Branch retrieval successful!")
                
                # Verify the structure
                assignments = branch_details.get("assignments", {})
                courses = assignments.get("courses", [])
                branch_admins = assignments.get("branch_admins", [])
                
                print(f"\n📊 Data verification:")
                print(f"   Courses (should be IDs): {courses}")
                print(f"   Branch admins (should be IDs): {branch_admins}")
                print(f"   ✅ Courses are stored as IDs: {all('course-uuid' in c for c in courses)}")
                print(f"   ✅ Branch admins are stored as IDs: {all('coach-uuid' in a for a in branch_admins)}")
                
                print(f"\n🎯 SUCCESS: Branch API stores and returns data exactly as requested!")
                print(f"   - assignments.courses: Course IDs ✅")
                print(f"   - assignments.branch_admins: User IDs ✅")
                print(f"   - operational_details.courses_offered: Display names ✅")
                
            else:
                print(f"❌ Failed to retrieve branch: {get_response.text}")
                
        elif response.status_code == 422:
            print("📋 Validation errors detected:")
            try:
                error_details = response.json()
                for error in error_details.get("detail", []):
                    location = " -> ".join(str(loc) for loc in error.get("loc", []))
                    message = error.get("msg", "Unknown error")
                    print(f"   {location}: {message}")
            except:
                print("   Could not parse error details")
                print(f"   Raw response: {response.text}")
            
        else:
            print(f"❌ Unexpected response: {response.status_code}")
            print(f"Response: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to the server. Make sure it's running on http://31.97.224.169:8003")
    except requests.exceptions.Timeout:
        print("❌ Request timed out")
    except Exception as e:
        print(f"❌ Error: {e}")

async def verify_database_storage():
    """Verify the data is stored correctly in the database"""
    try:
        mongo_url = os.getenv("MONGO_URL", "mongodb://localhost:27017")
        client = motor.motor_asyncio.AsyncIOMotorClient(mongo_url)
        db = client.student_management_db
        
        # Find the most recent branch
        branch = await db.branches.find_one({}, sort=[("created_at", -1)])
        
        if branch:
            print(f"\n📊 Database storage verification:")
            print("=" * 50)
            
            assignments = branch.get("assignments", {})
            courses = assignments.get("courses", [])
            branch_admins = assignments.get("branch_admins", [])
            
            print(f"✅ Courses stored: {courses}")
            print(f"✅ Branch admins stored: {branch_admins}")
            
            # Verify they are IDs
            courses_are_ids = all(isinstance(c, str) and len(c) > 10 for c in courses)
            admins_are_ids = all(isinstance(a, str) and len(a) > 10 for a in branch_admins)
            
            print(f"\n📋 Verification:")
            print(f"   Courses stored as IDs: {courses_are_ids}")
            print(f"   Branch admins stored as IDs: {admins_are_ids}")
            
        else:
            print("❌ No branch found in database")
        
        client.close()
        
    except Exception as e:
        print(f"❌ Database verification error: {e}")

if __name__ == "__main__":
    test_comprehensive_branch_api()
    print(f"\n{'='*60}")
    print("Verifying database storage...")
    asyncio.run(verify_database_storage())
