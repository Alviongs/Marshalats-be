import requests
import json

print('=== Testing Categories Public Details ===')
response = requests.get('http://31.97.224.169:8003/categories/public/details?include_courses=true')
print(f'Status: {response.status_code}')
if response.status_code == 200:
    data = response.json()
    print(f'Message: {data.get("message")}')
    print(f'Total: {data.get("total")}')
    print(f'Categories count: {len(data.get("categories", []))}')
    if data.get("categories"):
        print(f'First category: {data["categories"][0].get("name")}')
else:
    print(f'Error: {response.text}')

print('\n=== Testing Categories with Courses and Durations ===')
response = requests.get('http://31.97.224.169:8003/categories/public/with-courses-and-durations')
print(f'Status: {response.status_code}')
if response.status_code == 200:
    data = response.json()
    print(f'Message: {data.get("message")}')
    print(f'Total: {data.get("total")}')
else:
    print(f'Error: {response.text}')

print('\n=== Testing Durations Public All ===')
response = requests.get('http://31.97.224.169:8003/durations/public/all')
print(f'Status: {response.status_code}')
if response.status_code == 200:
    data = response.json()
    print(f'Message: {data.get("message")}')
    print(f'Total: {data.get("total")}')
    print(f'Durations count: {len(data.get("durations", []))}')
else:
    print(f'Error: {response.text}')

print('\n=== Testing Locations Public Details ===')
response = requests.get('http://31.97.224.169:8003/locations/public/details')
print(f'Status: {response.status_code}')
if response.status_code == 200:
    data = response.json()
    print(f'Message: {data.get("message")}')
    print(f'Total: {data.get("total")}')
    print(f'Locations count: {len(data.get("locations", []))}')
else:
    print(f'Error: {response.text}')
