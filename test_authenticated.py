import requests
import json

# Get token
token = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1MGY3YzdhYy0yNTkyLTQ0N2YtYmQzNy0zYzBkYWQ1ZDMzMGMiLCJlbWFpbCI6ImFkbWluQHRlc3QuY29tIiwicm9sZSI6InN1cGVyYWRtaW4iLCJleHAiOjE3NTczMTQ5NDh9.ZnhHstNDQVNNqYqHZtKw1sVSZ9PIHSuXZFK3aDZ3hn8'
headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}

print('=== Testing Student Details API (Authenticated) ===')
response = requests.get('http://31.97.224.169:8003/users/students/details', headers=headers)
print(f'Status: {response.status_code}')
if response.status_code == 200:
    data = response.json()
    print(f'Message: {data.get("message")}')
    print(f'Total students: {data.get("total")}')
    print(f'Students count: {len(data.get("students", []))}')
    if data.get("students"):
        student = data["students"][0]
        print(f'First student: {student.get("student_name")}')
        print(f'Courses: {len(student.get("courses", []))}')
else:
    print(f'Error: {response.text}')

print('\n=== Testing Student Details API Without Auth (Should Fail) ===')
response = requests.get('http://31.97.224.169:8003/users/students/details')
print(f'Status: {response.status_code}')
if response.status_code == 401:
    print('✅ Correctly requires authentication')
else:
    print(f'❌ Expected 401, got {response.status_code}')
    print(f'Response: {response.text}')

print('\n=== Testing Public Endpoint Without Auth (Should Work) ===')
response = requests.get('http://31.97.224.169:8003/categories/public/all')
print(f'Status: {response.status_code}')
if response.status_code == 200:
    print('✅ Public endpoint works without authentication')
    data = response.json()
    print(f'Categories: {data.get("total")}')
else:
    print(f'❌ Public endpoint failed: {response.text}')

print('\n=== Testing Durations by Course with Real Course ID (Should Fail Gracefully) ===')
response = requests.get('http://31.97.224.169:8003/durations/public/by-course/test-course-id')
print(f'Status: {response.status_code}')
if response.status_code == 404:
    print('✅ Correctly returns 404 for non-existent course')
else:
    print(f'Response: {response.text}')

print('\n=== Testing Location-Course Duration Combination ===')
location_id = 'a60c5165-60f4-4f65-b66c-433ebdcd9f73'  # Hyderabad
response = requests.get(f'http://31.97.224.169:8003/durations/public/by-location-course?location_id={location_id}&course_id=test-course-id')
print(f'Status: {response.status_code}')
if response.status_code == 404:
    print('✅ Correctly handles non-existent course')
else:
    print(f'Response: {response.text}')

print('\n=== Final Validation: All Endpoints Accessible ===')
endpoints = [
    '/categories/public/all',
    '/categories/public/details',
    '/categories/public/with-courses-and-durations',
    '/durations/public/all',
    '/locations/public/details',
    '/locations/public/with-branches'
]

all_working = True
for endpoint in endpoints:
    response = requests.get(f'http://31.97.224.169:8003{endpoint}')
    if response.status_code == 200:
        print(f'✅ {endpoint}')
    else:
        print(f'❌ {endpoint} - Status: {response.status_code}')
        all_working = False

if all_working:
    print('\n🎉 ALL PUBLIC ENDPOINTS WORKING PERFECTLY!')
else:
    print('\n⚠️ Some endpoints have issues.')
