#!/usr/bin/env python3

import requests
import json

def test_dashboard_api():
    """Test the dashboard API endpoints"""
    
    # Try different login credentials
    credentials = [
        {'email': 'admin@test.com', 'password': 'admin123'},
        {'email': 'superadmin@example.com', 'password': 'SuperAdmin123!'},
        {'email': 'admin@example.com', 'password': 'admin123'},
        {'email': 'test@test.com', 'password': 'test123'},
    ]

    print('🔐 Testing different login credentials...')
    token = None
    
    for cred in credentials:
        try:
            login_response = requests.post('http://31.97.224.169:8003/api/auth/login', json=cred)
            if login_response.status_code == 200:
                data = login_response.json()
                print(f'✅ Login successful with {cred["email"]}')
                token = data.get('access_token')
                break
            else:
                print(f'❌ Login failed for {cred["email"]}: {login_response.status_code}')
        except Exception as e:
            print(f'❌ Error with {cred["email"]}: {e}')
    
    if not token:
        print('❌ No valid credentials found. Cannot test dashboard API.')
        return
    
    # Test dashboard stats endpoint
    print('\n📊 Testing dashboard stats endpoint...')
    headers = {'Authorization': f'Bearer {token}'}
    
    try:
        stats_response = requests.get('http://31.97.224.169:8003/api/dashboard/stats', headers=headers)
        
        if stats_response.status_code == 200:
            stats_data = stats_response.json()
            print('✅ Dashboard stats retrieved successfully:')
            print(json.dumps(stats_data, indent=2))
        else:
            print(f'❌ Dashboard stats failed: {stats_response.status_code}')
            print(stats_response.text)
    except Exception as e:
        print(f'❌ Error testing dashboard stats: {e}')
    
    # Test coaches endpoint
    print('\n👨‍🏫 Testing coaches endpoint...')
    try:
        coaches_response = requests.get('http://31.97.224.169:8003/api/coaches', headers=headers)
        
        if coaches_response.status_code == 200:
            coaches_data = coaches_response.json()
            print('✅ Coaches data retrieved successfully:')
            print(f"Total coaches: {len(coaches_data.get('coaches', []))}")
            if coaches_data.get('coaches'):
                print("First coach:", coaches_data['coaches'][0].get('full_name', 'N/A'))
        else:
            print(f'❌ Coaches endpoint failed: {coaches_response.status_code}')
            print(coaches_response.text)
    except Exception as e:
        print(f'❌ Error testing coaches endpoint: {e}')

if __name__ == '__main__':
    test_dashboard_api()
