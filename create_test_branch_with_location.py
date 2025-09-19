#!/usr/bin/env python3

import requests
import json

def create_test_branch():
    """Create a test branch with proper location association"""
    
    print("🏗️ Creating test branch with location association...")
    
    # Step 1: Get locations
    print("\n📍 Getting locations...")
    try:
        response = requests.get('http://localhost:8003/api/locations/public/details?active_only=true')
        if response.status_code == 200:
            data = response.json()
            locations = data.get('locations', [])
            print(f"Found {len(locations)} locations:")
            for loc in locations:
                print(f"  - {loc['name']} (ID: {loc['id']}) in {loc['state']}")
        else:
            print(f"❌ Failed to get locations: {response.status_code}")
            return
    except Exception as e:
        print(f"❌ Error getting locations: {e}")
        return
    
    if not locations:
        print("❌ No locations found!")
        return
    
    # Step 2: Get authentication token (you would need to implement this)
    print("\n🔑 Getting authentication token...")
    # For now, we'll simulate the branch creation data
    
    # Create test branches for each location
    for i, location in enumerate(locations):
        location_id = location['id']
        location_name = location['name']
        location_state = location['state']
        
        test_branch_data = {
            "branch": {
                "name": f"{location_name} Martial Arts Academy",
                "code": f"{location_name[:3].upper()}-001",
                "email": f"{location_name.lower().replace(' ', '')}@martialarts.com",
                "phone": f"+91-{9000000000 + i}",
                "address": {
                    "line1": f"{100 + i*10} Main Street",
                    "area": f"Central {location_name}",
                    "city": location_name,
                    "state": location_state,
                    "pincode": f"{500000 + i}",
                    "country": "India"
                }
            },
            "location_id": location_id,
            "manager_id": f"manager-{location_id}",
            "operational_details": {
                "courses_offered": ["Karate", "Taekwondo", "Kung Fu"],
                "timings": [
                    {"day": "Monday", "open": "06:00", "close": "22:00"},
                    {"day": "Tuesday", "open": "06:00", "close": "22:00"},
                    {"day": "Wednesday", "open": "06:00", "close": "22:00"},
                    {"day": "Thursday", "open": "06:00", "close": "22:00"},
                    {"day": "Friday", "open": "06:00", "close": "22:00"},
                    {"day": "Saturday", "open": "08:00", "close": "20:00"},
                    {"day": "Sunday", "open": "08:00", "close": "18:00"}
                ],
                "holidays": ["2025-01-01", "2025-08-15", "2025-10-02", "2025-12-25"]
            },
            "assignments": {
                "accessories_available": True,
                "courses": [],
                "branch_admins": []
            },
            "bank_details": {
                "bank_name": f"State Bank of {location_state}",
                "account_number": f"1234567890{i}",
                "upi_id": f"{location_name.lower().replace(' ', '')}@sbi"
            }
        }
        
        print(f"\n📋 Test branch data for {location_name}:")
        print(f"  - Name: {test_branch_data['branch']['name']}")
        print(f"  - Code: {test_branch_data['branch']['code']}")
        print(f"  - Location ID: {test_branch_data['location_id']}")
        print(f"  - City: {test_branch_data['branch']['address']['city']}")
        print(f"  - State: {test_branch_data['branch']['address']['state']}")
        
        # Save the test data to a file for manual creation
        filename = f"test_branch_{location_name.lower().replace(' ', '_')}.json"
        with open(filename, 'w') as f:
            json.dump(test_branch_data, f, indent=2)
        print(f"  - Saved to: {filename}")
    
    print("\n💡 To create these branches:")
    print("1. Use the frontend create branch form at http://localhost:3022/dashboard/create-branch")
    print("2. Or use the API with proper authentication:")
    print("   POST /api/branches with the JSON data from the files")
    
    print("\n🧪 Current filtering status:")
    for location in locations:
        location_id = location['id']
        location_name = location['name']
        
        try:
            response = requests.get(f'http://localhost:8003/api/branches/public/by-location/{location_id}?active_only=true')
            if response.status_code == 200:
                data = response.json()
                branch_count = len(data.get('branches', []))
                print(f"  - {location_name}: {branch_count} branches")
            else:
                print(f"  - {location_name}: Error {response.status_code}")
        except Exception as e:
            print(f"  - {location_name}: Error {e}")

if __name__ == '__main__':
    create_test_branch()
