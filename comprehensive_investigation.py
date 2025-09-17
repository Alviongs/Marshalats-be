#!/usr/bin/env python3

import requests
import json

def comprehensive_investigation():
    """Comprehensive investigation of location-based branch filtering"""
    
    print('🔍 COMPREHENSIVE BACKEND API ANALYSIS')
    print('=' * 50)

    # Test 1: Check if backend server is running
    print('\n1. Backend Server Status:')
    try:
        response = requests.get('http://31.97.224.169:8003/')
        print(f'✅ Backend server running - Status: {response.status_code}')
    except Exception as e:
        print(f'❌ Backend server not accessible: {e}')
        return False

    # Test 2: Test locations API
    print('\n2. Locations API Test:')
    locations = []
    try:
        response = requests.get('http://31.97.224.169:8003/api/locations/public/details?active_only=true')
        print(f'Status: {response.status_code}')
        if response.status_code == 200:
            data = response.json()
            locations = data.get('locations', [])
            print(f'Found {len(locations)} locations:')
            for loc in locations:
                name = loc.get('name', 'N/A')
                loc_id = loc.get('id', 'N/A')
                state = loc.get('state', 'N/A')
                print(f'  - {name} (ID: {loc_id}) in {state}')
        else:
            print(f'Error: {response.text}')
            return False
    except Exception as e:
        print(f'Error: {e}')
        return False

    # Test 3: Test all branches API
    print('\n3. All Branches API Test:')
    branches = []
    try:
        response = requests.get('http://31.97.224.169:8003/api/branches/public/all?active_only=true')
        print(f'Status: {response.status_code}')
        if response.status_code == 200:
            data = response.json()
            branches = data.get('branches', [])
            print(f'Found {len(branches)} branches:')
            for branch in branches:
                name = branch.get('name', 'N/A')
                branch_id = branch.get('id', 'N/A')
                location_id = branch.get('location_id', 'MISSING')
                address = branch.get('address', {})
                print(f'  - Name: {name}')
                print(f'    ID: {branch_id}')
                print(f'    Location ID: {location_id}')
                print(f'    Address: {address}')
                print()
        else:
            print(f'Error: {response.text}')
            return False
    except Exception as e:
        print(f'Error: {e}')
        return False

    # Test 4: Test branch filtering by location
    print('\n4. Branch Filtering by Location Test:')
    for location in locations:
        location_id = location['id']
        location_name = location['name']
        print(f'\nTesting location: {location_name}')
        
        try:
            response = requests.get(f'http://31.97.224.169:8003/api/branches/public/by-location/{location_id}?active_only=true')
            print(f'  Status: {response.status_code}')
            if response.status_code == 200:
                data = response.json()
                print(f'  Response keys: {list(data.keys())}')
                filtered_branches = data.get('branches', [])
                print(f'  Found {len(filtered_branches)} branches')
                for branch in filtered_branches:
                    branch_name = branch.get('name', 'N/A')
                    print(f'    - {branch_name}')
            else:
                print(f'  Error: {response.text}')
        except Exception as e:
            print(f'  Error: {e}')

    # Test 5: Check API endpoint structure
    print('\n5. API Endpoint Structure Analysis:')
    endpoints_to_test = [
        '/api/branches/public/all',
        '/api/branches/public/by-location/test-id',
        '/api/locations/public/details',
        '/api/locations/public/states'
    ]
    
    for endpoint in endpoints_to_test:
        try:
            response = requests.get(f'http://31.97.224.169:8003{endpoint}')
            print(f'  {endpoint}: Status {response.status_code}')
        except Exception as e:
            print(f'  {endpoint}: Error {e}')

    # Analysis Summary
    print('\n6. ANALYSIS SUMMARY:')
    print(f'  - Locations found: {len(locations)}')
    print(f'  - Branches found: {len(branches)}')
    
    branches_with_location = [b for b in branches if b.get('location_id')]
    branches_without_location = [b for b in branches if not b.get('location_id')]
    
    print(f'  - Branches with location_id: {len(branches_with_location)}')
    print(f'  - Branches without location_id: {len(branches_without_location)}')
    
    if branches_without_location:
        print('\n❌ ISSUE IDENTIFIED:')
        print('  Branches without location_id associations:')
        for branch in branches_without_location:
            print(f'    - {branch.get("name", "N/A")} (ID: {branch.get("id", "N/A")})')
    
    return True

if __name__ == '__main__':
    comprehensive_investigation()
