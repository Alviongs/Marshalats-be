#!/usr/bin/env python3

import requests
import json

def test_frontend_backend_integration():
    """Test frontend-backend integration for location-based branch filtering"""
    
    print('🌐 FRONTEND-BACKEND INTEGRATION TEST')
    print('=' * 50)

    # Test the exact API calls that the frontend makes
    print('\n1. Testing Frontend API Calls:')

    # Test locations API (used by frontend dropdowns)
    print('\nTesting locations API:')
    try:
        # Try frontend proxy first
        response = requests.get('http://localhost:3022/api/locations/public/details?active_only=true')
        print(f'Frontend → Locations API: Status {response.status_code}')
        if response.status_code != 200:
            # Try direct backend call
            response = requests.get('http://31.97.224.169:8003/api/locations/public/details?active_only=true')
            print(f'Direct → Locations API: Status {response.status_code}')
            if response.status_code == 200:
                data = response.json()
                locations = data.get('locations', [])
                print(f'Locations found: {len(locations)}')
                for loc in locations:
                    print(f'  - {loc.get("name")} (ID: {loc.get("id")})')
    except Exception as e:
        print(f'Error: {e}')

    # Test branches API (used by frontend dropdowns)
    print('\nTesting branches by location API:')
    location_id = '07a19e09-0ef3-49ef-ba1d-4278af845685'  # Hyderabad
    try:
        # Try frontend proxy first
        response = requests.get(f'http://localhost:3022/api/branches/public/by-location/{location_id}?active_only=true')
        print(f'Frontend → Branches API: Status {response.status_code}')
        if response.status_code != 200:
            # Try direct backend call
            response = requests.get(f'http://31.97.224.169:8003/api/branches/public/by-location/{location_id}?active_only=true')
            print(f'Direct → Branches API: Status {response.status_code}')
            if response.status_code == 200:
                data = response.json()
                branches = data.get('branches', [])
                print(f'Branches found: {len(branches)}')
                print('Response structure:')
                print(json.dumps(data, indent=2))
    except Exception as e:
        print(f'Error: {e}')

    print('\n2. Testing All Branches API:')
    try:
        response = requests.get('http://31.97.224.169:8003/api/branches/public/all?active_only=true')
        print(f'Status: {response.status_code}')
        if response.status_code == 200:
            data = response.json()
            branches = data.get('branches', [])
            print(f'Total branches: {len(branches)}')
            for branch in branches:
                name = branch.get('name', 'N/A')
                location_id = branch.get('location_id', 'MISSING')
                print(f'  - {name} (location_id: {location_id})')
    except Exception as e:
        print(f'Error: {e}')

    print('\n3. Testing Frontend Pages Accessibility:')
    frontend_pages = [
        ('Create Student', 'http://localhost:3022/dashboard/create-student'),
        ('Create Branch', 'http://localhost:3022/dashboard/create-branch'),
        ('Register Select Branch', 'http://localhost:3022/register/select-branch')
    ]
    
    for page_name, url in frontend_pages:
        try:
            response = requests.get(url, timeout=5)
            print(f'{page_name}: Status {response.status_code}')
        except Exception as e:
            print(f'{page_name}: Error {e}')

if __name__ == '__main__':
    test_frontend_backend_integration()
