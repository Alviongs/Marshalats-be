#!/usr/bin/env python3

import requests
import json

def test_simple_dashboard():
    """Simple test of dashboard functionality"""
    
    print('🔐 Testing login...')
    login_response = requests.post('http://31.97.224.169:8003/api/auth/login', json={
        'email': 'admin@test.com',
        'password': 'admin123'
    })
    
    if login_response.status_code != 200:
        print(f'❌ Login failed: {login_response.status_code}')
        print(login_response.text)
        return
    
    data = login_response.json()
    token = data.get('access_token')
    print(f'✅ Login successful')
    
    headers = {'Authorization': f'Bearer {token}'}
    
    # Test basic endpoints that should work
    endpoints_to_test = [
        ('/api/users', 'Users endpoint'),
        ('/api/courses', 'Courses endpoint'),
        ('/api/coaches', 'Coaches endpoint'),
        ('/api/branches', 'Branches endpoint'),
    ]
    
    for endpoint, description in endpoints_to_test:
        try:
            response = requests.get(f'http://31.97.224.169:8003{endpoint}', headers=headers)
            if response.status_code == 200:
                data = response.json()
                print(f'✅ {description}: {response.status_code} - {len(data.get("users", data.get("courses", data.get("coaches", data.get("branches", [])))))} items')
            else:
                print(f'❌ {description}: {response.status_code}')
        except Exception as e:
            print(f'❌ {description}: Error - {e}')
    
    # Test dashboard stats endpoint specifically
    print('\n📊 Testing dashboard stats endpoint...')
    try:
        response = requests.get('http://31.97.224.169:8003/api/dashboard/stats', headers=headers)
        print(f'Dashboard stats response: {response.status_code}')
        if response.status_code == 200:
            print('✅ Dashboard stats working!')
            print(json.dumps(response.json(), indent=2))
        else:
            print(f'❌ Dashboard stats failed: {response.text}')
    except Exception as e:
        print(f'❌ Dashboard stats error: {e}')

if __name__ == '__main__':
    test_simple_dashboard()
