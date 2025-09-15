#!/usr/bin/env python3

import requests
import json

def test_categories_and_courses():
    print('Testing Categories API...')
    categories_response = requests.get('http://localhost:8003/api/categories/public/details?active_only=true')
    print(f'Categories Status: {categories_response.status_code}')

    if categories_response.status_code == 200:
        categories_data = categories_response.json()
        print(f'Found {len(categories_data["categories"])} categories')
        
        # Test with first category that has courses
        for category in categories_data['categories']:
            if category['course_count'] > 0:
                category_id = category['id']
                category_name = category['name']
                print(f'\nTesting Courses API for category: {category_name} ({category_id})')
                
                courses_response = requests.get(f'http://localhost:8003/api/courses/public/by-category/{category_id}?active_only=true')
                print(f'Courses Status: {courses_response.status_code}')
                
                if courses_response.status_code == 200:
                    courses_data = courses_response.json()
                    print(f'Found {len(courses_data["courses"])} courses')
                    
                    # Check if courses have duration options
                    for course in courses_data['courses']:
                        durations = course.get('available_durations', [])
                        print(f'  Course: {course["title"]} has {len(durations)} duration options')
                        if durations:
                            print(f'    Sample duration: {durations[0]["name"]} ({durations[0]["duration_months"]} months)')
                break
    else:
        print('Categories API failed:', categories_response.text)

if __name__ == '__main__':
    test_categories_and_courses()
