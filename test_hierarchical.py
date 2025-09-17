import requests
import json

# Test data IDs
category_id = '7b656efc-65bf-463d-8aad-0e1cf28117e4'  # Martial Arts
location_id = 'a60c5165-60f4-4f65-b66c-433ebdcd9f73'  # Hyderabad

print('=== Testing Category Location Hierarchy ===')
response = requests.get(f'http://31.97.224.169:8003/categories/public/location-hierarchy?category_id={category_id}')
print(f'Status: {response.status_code}')
if response.status_code == 200:
    data = response.json()
    print(f'Message: {data.get("message")}')
    print(f'Category: {data.get("category", {}).get("name")}')
    print(f'Courses count: {len(data.get("courses", []))}')
    if data.get("summary"):
        print(f'Summary: {data["summary"]}')
else:
    print(f'Error: {response.text}')

print('\n=== Testing Courses by Category ===')
response = requests.get(f'http://31.97.224.169:8003/courses/public/by-category/{category_id}')
print(f'Status: {response.status_code}')
if response.status_code == 200:
    data = response.json()
    print(f'Message: {data.get("message")}')
    print(f'Category: {data.get("category", {}).get("name")}')
    print(f'Courses count: {len(data.get("courses", []))}')
else:
    print(f'Error: {response.text}')

print('\n=== Testing Courses by Location ===')
response = requests.get(f'http://31.97.224.169:8003/courses/public/by-location/{location_id}')
print(f'Status: {response.status_code}')
if response.status_code == 200:
    data = response.json()
    print(f'Message: {data.get("message")}')
    print(f'Location: {data.get("location", {}).get("name")}')
    print(f'Courses count: {len(data.get("courses", []))}')
else:
    print(f'Error: {response.text}')

print('\n=== Testing Branches by Location ===')
response = requests.get(f'http://31.97.224.169:8003/branches/public/by-location/{location_id}')
print(f'Status: {response.status_code}')
if response.status_code == 200:
    data = response.json()
    print(f'Message: {data.get("message")}')
    print(f'Location: {data.get("location", {}).get("name")}')
    print(f'Branches count: {len(data.get("branches", []))}')
else:
    print(f'Error: {response.text}')

print('\n=== Testing Error Handling - Invalid Category ID ===')
response = requests.get('http://31.97.224.169:8003/categories/public/location-hierarchy?category_id=invalid-uuid')
print(f'Status: {response.status_code}')
if response.status_code == 404:
    print('✅ Correctly returned 404 for invalid ID')
else:
    print(f'❌ Expected 404, got {response.status_code}')
    print(f'Response: {response.text}')

print('\n=== Testing Error Handling - Invalid Location ID ===')
response = requests.get('http://31.97.224.169:8003/branches/public/by-location/invalid-uuid')
print(f'Status: {response.status_code}')
if response.status_code == 404:
    print('✅ Correctly returned 404 for invalid ID')
else:
    print(f'❌ Expected 404, got {response.status_code}')
    print(f'Response: {response.text}')

print('\n=== Testing Pagination ===')
response = requests.get('http://31.97.224.169:8003/categories/public/details?skip=0&limit=1')
print(f'Status: {response.status_code}')
if response.status_code == 200:
    data = response.json()
    print(f'Message: {data.get("message")}')
    print(f'Total available: {data.get("total")}')
    print(f'Returned count: {len(data.get("categories", []))}')
    if len(data.get("categories", [])) == 1:
        print('✅ Pagination working correctly')
    else:
        print('❌ Pagination not working as expected')
else:
    print(f'Error: {response.text}')
