#!/usr/bin/env python3

import requests
import json

def analyze_current_state():
    print("🔍 Analyzing current database state via API...")
    
    # Get locations
    print("\n📍 Locations:")
    try:
        response = requests.get('http://31.97.224.169:8003/api/locations/public/details?active_only=true')
        if response.status_code == 200:
            data = response.json()
            locations = data.get('locations', [])
            for loc in locations:
                name = loc.get('name', 'N/A')
                loc_id = loc.get('id', 'N/A')
                state = loc.get('state', 'N/A')
                print(f"  - {name} (ID: {loc_id}) in {state}")
        else:
            print(f"  Error: {response.status_code}")
    except Exception as e:
        print(f"  Error: {e}")
    
    # Get all branches
    print("\n🏢 All branches:")
    try:
        response = requests.get('http://31.97.224.169:8003/api/branches/public/all?active_only=true')
        if response.status_code == 200:
            data = response.json()
            branches = data.get('branches', [])
            print(f"Found {len(branches)} branches:")
            for branch in branches:
                branch_id = branch.get('id', 'N/A')
                name = branch.get('name', 'N/A')
                location_id = branch.get('location_id', 'MISSING')
                state = branch.get('address', {}).get('state', 'N/A')
                city = branch.get('address', {}).get('city', 'N/A')
                print(f"  - ID: {branch_id}")
                print(f"    Name: {name}")
                print(f"    Location ID: {location_id}")
                print(f"    State: {state}")
                print(f"    City: {city}")
                print()
        else:
            print(f"  Error: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"  Error: {e}")
    
    # Test filtering for each location
    print("\n🧪 Testing branch filtering by location:")
    try:
        # Get locations again for filtering test
        response = requests.get('http://31.97.224.169:8003/api/locations/public/details?active_only=true')
        if response.status_code == 200:
            data = response.json()
            locations = data.get('locations', [])
            
            for loc in locations:
                location_id = loc['id']
                location_name = loc['name']
                
                filter_response = requests.get(f'http://31.97.224.169:8003/api/branches/public/by-location/{location_id}?active_only=true')
                if filter_response.status_code == 200:
                    filter_data = filter_response.json()
                    branch_count = len(filter_data.get('branches', []))
                    print(f"  - {location_name}: {branch_count} branches")
                else:
                    print(f"  - {location_name}: Error {filter_response.status_code}")
    except Exception as e:
        print(f"  Error: {e}")

if __name__ == '__main__':
    analyze_current_state()
