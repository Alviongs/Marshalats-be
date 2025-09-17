import requests
import json

# Get token
token = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1MGY3YzdhYy0yNTkyLTQ0N2YtYmQzNy0zYzBkYWQ1ZDMzMGMiLCJlbWFpbCI6ImFkbWluQHRlc3QuY29tIiwicm9sZSI6InN1cGVyYWRtaW4iLCJleHAiOjE3NTczMTQ5NDh9.ZnhHstNDQVNNqYqHZtKw1sVSZ9PIHSuXZFK3aDZ3hn8'
headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}

# Test data IDs
category_id_ma = '7b656efc-65bf-463d-8aad-0e1cf28117e4'  # Martial Arts
category_id_fit = '5de1c515-dc37-4b08-bb8b-1d4412539f76'  # Fitness
location_id_hyd = 'a60c5165-60f4-4f65-b66c-433ebdcd9f73'  # Hyderabad
location_id_mum = 'e5bacaa2-54b5-4730-9451-1881048730cb'  # Mumbai

print('=== Creating Test Courses ===')
courses = [
    {
        'title': 'Advanced Kung Fu Training',
        'code': 'KF-ADV-001',
        'description': 'Comprehensive advanced Kung Fu training program',
        'category_id': category_id_ma,
        'difficulty_level': 'Advanced',
        'pricing': {
            'currency': 'INR',
            'amount': 8500
        },
        'student_requirements': {
            'max_students': 20,
            'min_age': 16,
            'max_age': 50,
            'prerequisites': ['Basic Kung Fu']
        },
        'settings': {
            'active': True,
            'offers_certification': True
        },
        'media_resources': {
            'course_image_url': 'https://example.com/kungfu.jpg',
            'promo_video_url': 'https://example.com/kungfu-promo.mp4'
        }
    },
    {
        'title': 'Beginner Karate',
        'code': 'KAR-BEG-001',
        'description': 'Introduction to Karate for beginners',
        'category_id': category_id_ma,
        'difficulty_level': 'Beginner',
        'pricing': {
            'currency': 'INR',
            'amount': 5000
        },
        'student_requirements': {
            'max_students': 30,
            'min_age': 8,
            'max_age': 60,
            'prerequisites': []
        },
        'settings': {
            'active': True,
            'offers_certification': True
        }
    },
    {
        'title': 'Fitness Bootcamp',
        'code': 'FIT-BOOT-001',
        'description': 'High-intensity fitness training program',
        'category_id': category_id_fit,
        'difficulty_level': 'Intermediate',
        'pricing': {
            'currency': 'INR',
            'amount': 6000
        },
        'student_requirements': {
            'max_students': 25,
            'min_age': 18,
            'max_age': 45,
            'prerequisites': ['Basic fitness level']
        },
        'settings': {
            'active': True,
            'offers_certification': False
        }
    }
]

created_courses = []
for course in courses:
    try:
        response = requests.post('http://31.97.224.169:8003/courses', json=course, headers=headers)
        print(f'Creating {course["title"]}: Status {response.status_code}')
        if response.status_code in [200, 201]:
            data = response.json()
            course_id = data.get('course_id')
            created_courses.append(course_id)
            print(f'  Created successfully: {course_id}')
        else:
            print(f'  Error: {response.text}')
    except Exception as e:
        print(f'  Exception: {e}')

print(f'Created courses: {created_courses}')

print('\n=== Creating Test Branches ===')
branches = [
    {
        'branch': {
            'name': 'Hitech City Branch',
            'code': 'HYD-HTC-001',
            'email': 'hitech@martialarts.com',
            'phone': '+91-9876543210',
            'address': {
                'line1': '123 Cyber Towers',
                'area': 'Hitech City',
                'city': 'Hyderabad',
                'state': 'Telangana',
                'pincode': '500081',
                'country': 'India'
            }
        },
        'operational_details': {
            'courses_offered': ['Kung Fu', 'Karate', 'Fitness'],
            'timings': [
                {'day': 'Monday', 'open': '06:00', 'close': '22:00'},
                {'day': 'Tuesday', 'open': '06:00', 'close': '22:00'},
                {'day': 'Wednesday', 'open': '06:00', 'close': '22:00'},
                {'day': 'Thursday', 'open': '06:00', 'close': '22:00'},
                {'day': 'Friday', 'open': '06:00', 'close': '22:00'},
                {'day': 'Saturday', 'open': '07:00', 'close': '20:00'},
                {'day': 'Sunday', 'open': '08:00', 'close': '18:00'}
            ]
        },
        'assignments': {
            'courses': created_courses[:2] if len(created_courses) >= 2 else created_courses
        },
        'is_active': True
    },
    {
        'branch': {
            'name': 'Bandra Branch',
            'code': 'MUM-BAN-001',
            'email': 'bandra@martialarts.com',
            'phone': '+91-9876543211',
            'address': {
                'line1': '456 Linking Road',
                'area': 'Bandra West',
                'city': 'Mumbai',
                'state': 'Maharashtra',
                'pincode': '400050',
                'country': 'India'
            }
        },
        'operational_details': {
            'courses_offered': ['Fitness', 'Martial Arts'],
            'timings': [
                {'day': 'Monday', 'open': '06:00', 'close': '22:00'},
                {'day': 'Tuesday', 'open': '06:00', 'close': '22:00'},
                {'day': 'Wednesday', 'open': '06:00', 'close': '22:00'},
                {'day': 'Thursday', 'open': '06:00', 'close': '22:00'},
                {'day': 'Friday', 'open': '06:00', 'close': '22:00'},
                {'day': 'Saturday', 'open': '07:00', 'close': '20:00'},
                {'day': 'Sunday', 'open': '08:00', 'close': '18:00'}
            ]
        },
        'assignments': {
            'courses': created_courses[-1:] if created_courses else []
        },
        'is_active': True
    }
]

created_branches = []
for branch in branches:
    try:
        response = requests.post('http://31.97.224.169:8003/branches', json=branch, headers=headers)
        print(f'Creating {branch["branch"]["name"]}: Status {response.status_code}')
        if response.status_code in [200, 201]:
            data = response.json()
            branch_id = data.get('branch_id')
            created_branches.append(branch_id)
            print(f'  Created successfully: {branch_id}')
        else:
            print(f'  Error: {response.text}')
    except Exception as e:
        print(f'  Exception: {e}')

print(f'Created branches: {created_branches}')

print('\n=== Test Data Creation Complete ===')
print(f'Courses: {len(created_courses)}')
print(f'Branches: {len(created_branches)}')
