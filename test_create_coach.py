#!/usr/bin/env python3

import requests
import json

# Try different superadmin credentials
credentials = [
    {'email': 'pittisunilkumar3@gmail.com', 'password': 'StrongPassword@123'},
    {'email': 'superadmin@test.com', 'password': 'SuperAdmin123!'},
    {'email': 'admin@marshalats.com', 'password': 'admin123'}
]

for cred in credentials:
    print(f'Trying {cred["email"]}...')
    login_response = requests.post('http://31.97.224.169:8003/api/superadmin/login', json=cred)
    
    if login_response.status_code == 200:
        token = login_response.json()['data']['token']
        print(f'Success! Got token: {token[:50]}...')
        
        # Create a test coach
        coach_data = {
            'personal_info': {
                'first_name': 'John',
                'last_name': 'Smith',
                'gender': 'Male',
                'date_of_birth': '1985-05-15'
            },
            'contact_info': {
                'email': 'john.smith@test.com',
                'country_code': '+1',
                'phone': '1234567890',
                'password': 'TestPass123!'
            },
            'address_info': {
                'address': '123 Test Street',
                'area': 'Downtown',
                'city': 'Test City',
                'state': 'Test State',
                'zip_code': '12345',
                'country': 'USA'
            },
            'professional_info': {
                'education_qualification': 'Bachelor in Sports Science',
                'professional_experience': '5 years',
                'designation_id': 'senior-coach',
                'certifications': ['Black Belt Karate', 'CPR Certified']
            },
            'areas_of_expertise': ['Martial Arts', 'Self Defense'],
            'branch_id': 'c9ed7bb7-c31e-4b0f-9edf-760b41de9628'
        }
        
        create_response = requests.post('http://31.97.224.169:8003/api/coaches',
            headers={'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'},
            json=coach_data)
        
        print(f'Create coach response: {create_response.status_code}')
        if create_response.status_code == 201:
            print('Coach created successfully!')
            print(f'Response: {create_response.json()}')
        else:
            print(f'Failed to create coach: {create_response.text}')
        
        # Now test getting coaches
        print('\nTesting coaches API...')
        coaches_response = requests.get('http://31.97.224.169:8003/api/coaches?active_only=true&limit=10',
            headers={'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'})

        print(f'Get coaches response: {coaches_response.status_code}')
        if coaches_response.status_code == 200:
            coaches_data = coaches_response.json()
            print(f'Found {len(coaches_data["coaches"])} coaches')
            for coach in coaches_data["coaches"]:
                email = coach.get("email") or coach.get("contact_info", {}).get("email", "No email")
                print(f'  - {coach["full_name"]} ({email}) - Branch: {coach["branch_id"]}')
        else:
            print(f'Failed to get coaches: {coaches_response.text}')

        # Test branch managers
        print('\nTesting branch managers API...')
        managers_response = requests.get('http://31.97.224.169:8003/api/branch-managers',
            headers={'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'})

        print(f'Get branch managers response: {managers_response.status_code}')
        if managers_response.status_code == 200:
            managers_data = managers_response.json()
            print(f'Found {len(managers_data.get("branch_managers", []))} branch managers')
            for manager in managers_data.get("branch_managers", []):
                branch_assignment = manager.get("branch_assignment") or {}
                branch_id = branch_assignment.get("branch_id", "No branch") if isinstance(branch_assignment, dict) else "No branch"
                print(f'  - {manager.get("full_name", "Unknown")} ({manager.get("email", "No email")}) - Branch: {branch_id}')
        else:
            print(f'Failed to get branch managers: {managers_response.text}')

        # Test branch manager login and coaches API
        print('\n' + '='*50)
        print('TESTING BRANCH MANAGER AUTHENTICATION')
        print('='*50)

        # First, create a new branch manager with known credentials
        print('\nCreating a new branch manager with known credentials...')
        new_manager_data = {
            'personal_info': {
                'first_name': 'Test',
                'last_name': 'Manager',
                'gender': 'Male',
                'date_of_birth': '1985-06-15'
            },
            'contact_info': {
                'email': 'test.branch.manager.new@example.com',
                'country_code': '+1',
                'phone': '8888888888',
                'password': 'TestManager123!'
            },
            'address_info': {
                'address': '123 Manager Street',
                'area': 'Manager Area',
                'city': 'Manager City',
                'state': 'Manager State',
                'zip_code': '12345',
                'country': 'USA'
            },
            'professional_info': {
                'designation': 'Branch Manager',
                'education_qualification': 'MBA',
                'professional_experience': '5 years',
                'certifications': ['Management Certification']
            },
            'branch_id': 'c9ed7bb7-c31e-4b0f-9edf-760b41de9628'
        }

        create_manager_response = requests.post('http://31.97.224.169:8003/api/branch-managers',
            headers={'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'},
            json=new_manager_data)

        print(f'Create branch manager response: {create_manager_response.status_code}')
        if create_manager_response.status_code in [200, 201]:
            print('✅ Branch manager created successfully!')
            print(f'Response: {create_manager_response.json()}')
        else:
            print(f'❌ Failed to create branch manager: {create_manager_response.text}')

        # Try to login as branch manager
        branch_manager_credentials = [
            {'email': 'test.branch.manager.new@example.com', 'password': 'TestManager123!'},
            {'email': 'test.manager2@example.com', 'password': 'password123'},
            {'email': 'pittisunilkumar3@gmail.com', 'password': 'password123'},
            {'email': 'test.manager@example.com', 'password': 'password123'}
        ]

        for bm_cred in branch_manager_credentials:
            print(f'\nTrying branch manager login: {bm_cred["email"]}...')
            bm_login_response = requests.post('http://31.97.224.169:8003/api/branch-managers/login', json=bm_cred)

            if bm_login_response.status_code == 200:
                bm_token = bm_login_response.json()['access_token']
                print(f'✅ Branch manager login successful! Token: {bm_token[:50]}...')

                # Test /api/branch-managers/me
                print('\nTesting /api/branch-managers/me...')
                me_response = requests.get('http://31.97.224.169:8003/api/branch-managers/me',
                    headers={'Authorization': f'Bearer {bm_token}', 'Content-Type': 'application/json'})

                print(f'Branch manager profile response: {me_response.status_code}')
                if me_response.status_code == 200:
                    profile_data = me_response.json()
                    print(f'Profile: {json.dumps(profile_data, indent=2)}')
                else:
                    print(f'Failed to get profile: {me_response.text}')

                # Test coaches API with branch manager token
                print('\nTesting coaches API with branch manager token...')
                bm_coaches_response = requests.get('http://31.97.224.169:8003/api/coaches?active_only=true&limit=100',
                    headers={'Authorization': f'Bearer {bm_token}', 'Content-Type': 'application/json'})

                print(f'Branch manager coaches response: {bm_coaches_response.status_code}')
                if bm_coaches_response.status_code == 200:
                    bm_coaches_data = bm_coaches_response.json()
                    print(f'Found {len(bm_coaches_data.get("coaches", []))} coaches for branch manager')
                    for coach in bm_coaches_data.get("coaches", []):
                        email = coach.get("email") or coach.get("contact_info", {}).get("email", "No email")
                        print(f'  - {coach["full_name"]} ({email}) - Branch: {coach["branch_id"]}')
                else:
                    print(f'Failed to get coaches: {bm_coaches_response.text}')

                # Test students API with branch manager token
                print('\nTesting students API with branch manager token...')
                bm_students_response = requests.get('http://31.97.224.169:8003/api/users/students/details',
                    headers={'Authorization': f'Bearer {bm_token}', 'Content-Type': 'application/json'})

                print(f'Branch manager students response: {bm_students_response.status_code}')
                if bm_students_response.status_code == 200:
                    bm_students_data = bm_students_response.json()
                    students_list = bm_students_data.get("students", [])
                    print(f'Found {len(students_list)} students for branch manager')
                    for student in students_list[:3]:  # Show first 3 students
                        print(f'  - {student.get("full_name", "Unknown")} ({student.get("email", "No email")}) - Branch: {student.get("branch_id", "No branch")}')
                    if len(students_list) > 3:
                        print(f'  ... and {len(students_list) - 3} more students')
                else:
                    print(f'Failed to get students: {bm_students_response.text}')

                # Test courses API with branch manager token
                print('\nTesting courses API with branch manager token...')
                profile_data = me_response.json()
                branch_assignment = profile_data.get("branch_manager", {}).get("branch_assignment")
                branch_id = branch_assignment.get("branch_id") if branch_assignment else None
                if branch_id:
                    bm_courses_response = requests.get(f'http://31.97.224.169:8003/api/courses/by-branch/{branch_id}',
                        headers={'Authorization': f'Bearer {bm_token}', 'Content-Type': 'application/json'})

                    print(f'Branch manager courses response: {bm_courses_response.status_code}')
                    if bm_courses_response.status_code == 200:
                        bm_courses_data = bm_courses_response.json()
                        courses_list = bm_courses_data.get("courses", [])
                        print(f'Found {len(courses_list)} courses for branch manager')
                        for course in courses_list[:3]:  # Show first 3 courses
                            print(f'  - {course.get("name", "Unknown")} ({course.get("category_name", "No category")}) - Level: {course.get("difficulty_level", "Unknown")}')
                        if len(courses_list) > 3:
                            print(f'  ... and {len(courses_list) - 3} more courses')
                    else:
                        print(f'Failed to get courses: {bm_courses_response.text}')
                else:
                    print('No branch ID found in branch manager profile')

                # If no coaches found, let's check if branch assignment is the issue
                if len(bm_coaches_data.get("coaches", [])) == 0:
                    print('\n🔍 DIAGNOSIS: No coaches found. Checking branch assignment...')
                    profile_data = me_response.json()
                    branch_assignment = profile_data.get("branch_manager", {}).get("branch_assignment")

                    if branch_assignment is None:
                        print('❌ ISSUE FOUND: Branch manager has no branch assignment!')
                        print('💡 SOLUTION: The branch manager needs to be assigned to a branch.')
                        print('   This explains why no coaches are returned - the backend filters coaches by branch.')
                        print('   The coaches exist in branch c9ed7bb7-c31e-4b0f-9edf-760b41de9628')
                        print('   But this branch manager is not assigned to any branch.')
                    else:
                        print(f'✅ Branch assignment exists: {branch_assignment}')
                        print('❌ BACKEND ISSUE: Branch manager has correct assignment but coaches API still returns 0 coaches.')
                        print('💡 SOLUTION: The backend filtering logic in CoachController.get_coaches() needs to be fixed.')
                        print('   The issue is likely in how the branch_assignment is being used for filtering.')

                break
            else:
                print(f'❌ Branch manager login failed: {bm_login_response.status_code} - {bm_login_response.text}')

        break
    else:
        print(f'Failed: {login_response.status_code} - {login_response.text}')
