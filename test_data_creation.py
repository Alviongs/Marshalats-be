import requests
import json

# Get token
token = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1MGY3YzdhYy0yNTkyLTQ0N2YtYmQzNy0zYzBkYWQ1ZDMzMGMiLCJlbWFpbCI6ImFkbWluQHRlc3QuY29tIiwicm9sZSI6InN1cGVyYWRtaW4iLCJleHAiOjE3NTczMTQ5NDh9.ZnhHstNDQVNNqYqHZtKw1sVSZ9PIHSuXZFK3aDZ3hn8'
headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}

# Create test categories
print('=== Creating Test Categories ===')
categories = [
    {
        'name': 'Martial Arts',
        'code': 'MA',
        'description': 'Traditional and modern martial arts disciplines',
        'is_active': True,
        'display_order': 1,
        'color_code': '#FF5722'
    },
    {
        'name': 'Fitness',
        'code': 'FIT',
        'description': 'Physical fitness and wellness programs',
        'is_active': True,
        'display_order': 2,
        'color_code': '#4CAF50'
    }
]

created_categories = []
for category in categories:
    try:
        response = requests.post('http://31.97.224.169:8003/categories', json=category, headers=headers)
        print(f'Creating {category["name"]}: Status {response.status_code}')
        if response.status_code in [200, 201]:
            data = response.json()
            created_categories.append(data.get('category_id'))
            print(f'  Created successfully: {data.get("category_id")}')
        else:
            print(f'  Error: {response.text}')
    except Exception as e:
        print(f'  Exception: {e}')

print(f'Created categories: {created_categories}')

# Create test durations
print('\n=== Creating Test Durations ===')
durations = [
    {
        'name': '3 Months',
        'code': '3M',
        'duration_months': 3,
        'duration_days': 90,
        'description': 'Standard 3-month course duration',
        'is_active': True,
        'display_order': 1,
        'pricing_multiplier': 1.0
    },
    {
        'name': '6 Months',
        'code': '6M',
        'duration_months': 6,
        'duration_days': 180,
        'description': 'Extended 6-month course duration',
        'is_active': True,
        'display_order': 2,
        'pricing_multiplier': 1.8
    },
    {
        'name': '1 Year',
        'code': '1Y',
        'duration_months': 12,
        'duration_days': 365,
        'description': 'Full year comprehensive training',
        'is_active': True,
        'display_order': 3,
        'pricing_multiplier': 3.0
    }
]

created_durations = []
for duration in durations:
    try:
        response = requests.post('http://31.97.224.169:8003/durations', json=duration, headers=headers)
        print(f'Creating {duration["name"]}: Status {response.status_code}')
        if response.status_code in [200, 201]:
            data = response.json()
            created_durations.append(data.get('duration_id'))
            print(f'  Created successfully: {data.get("duration_id")}')
        else:
            print(f'  Error: {response.text}')
    except Exception as e:
        print(f'  Exception: {e}')

print(f'Created durations: {created_durations}')

# Create test locations
print('\n=== Creating Test Locations ===')
locations = [
    {
        'name': 'Hyderabad',
        'code': 'HYD',
        'state': 'Telangana',
        'country': 'India',
        'timezone': 'Asia/Kolkata',
        'is_active': True,
        'display_order': 1,
        'description': 'IT hub of South India'
    },
    {
        'name': 'Mumbai',
        'code': 'MUM',
        'state': 'Maharashtra',
        'country': 'India',
        'timezone': 'Asia/Kolkata',
        'is_active': True,
        'display_order': 2,
        'description': 'Financial capital of India'
    }
]

created_locations = []
for location in locations:
    try:
        response = requests.post('http://31.97.224.169:8003/locations', json=location, headers=headers)
        print(f'Creating {location["name"]}: Status {response.status_code}')
        if response.status_code in [200, 201]:
            data = response.json()
            created_locations.append(data.get('location_id'))
            print(f'  Created successfully: {data.get("location_id")}')
        else:
            print(f'  Error: {response.text}')
    except Exception as e:
        print(f'  Exception: {e}')

print(f'Created locations: {created_locations}')

print('\n=== Test Data Creation Complete ===')
print(f'Categories: {len(created_categories)}')
print(f'Durations: {len(created_durations)}')
print(f'Locations: {len(created_locations)}')
