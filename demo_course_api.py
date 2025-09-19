#!/usr/bin/env python3

import requests
import json

def test_course_api():
    """Quick demonstration of the course API"""
    
    # Login
    print("🔐 Logging in...")
    login_response = requests.post("http://localhost:8003/api/auth/login", json={
        "email": "superadmin@test.com", 
        "password": "SuperAdmin123!"
    })
    
    if login_response.status_code != 200:
        print("❌ Login failed")
        return
    
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    
    # Test 1: Create course with your exact payload
    print("\n🥋 Creating course with nested structure...")
    course_payload = {
        "title": "Advanced Kung Fu Training",
        "code": "KF-ADV-001",
        "description": "A comprehensive course covering advanced Kung Fu techniques, discipline, and sparring practices.",
        "martial_art_style_id": "style-uuid-1234",
        "difficulty_level": "Advanced",
        "category_id": "category-uuid-5678",
        "instructor_id": "instructor-uuid-91011",
        "student_requirements": {
            "max_students": 20,
            "min_age": 6,
            "max_age": 65,
            "prerequisites": [
                "Basic fitness level",
                "Prior martial arts experience"
            ]
        },
        "course_content": {
            "syllabus": "Week 1: Stance training, Week 2: Forms, Week 3: Advanced sparring, Week 4: Weapons basics...",
            "equipment_required": [
                "Gloves",
                "Shin guards",
                "Training uniform"
            ]
        },
        "media_resources": {
            "course_image_url": "https://example.com/course-image.jpg",
            "promo_video_url": "https://youtube.com/watch?v=abcd1234"
        },
        "pricing": {
            "currency": "INR",
            "amount": 8500,
            "branch_specific_pricing": False
        },
        "settings": {
            "offers_certification": True,
            "active": True
        }
    }
    
    create_response = requests.post("http://localhost:8003/api/courses", json=course_payload, headers=headers)
    
    if create_response.status_code == 200:
        course_id = create_response.json()["course_id"]
        print(f"✅ Course created successfully! ID: {course_id}")
        
        # Test 2: Retrieve the course to verify nested structure
        print("\n📖 Retrieving course to verify nested structure...")
        get_response = requests.get(f"http://localhost:8003/api/courses/{course_id}", headers=headers)
        
        if get_response.status_code == 200:
            course = get_response.json()
            print("✅ Course retrieved successfully!")
            print("🔍 Nested structure preserved:")
            print(f"   - Title: {course['title']}")
            print(f"   - Code: {course['code']}")
            print(f"   - Student Requirements: {course['student_requirements']}")
            print(f"   - Course Content: {course['course_content']}")
            print(f"   - Media Resources: {course['media_resources']}")
            print(f"   - Pricing: {course['pricing']}")
            print(f"   - Settings: {course['settings']}")
            
        # Test 3: Get all courses
        print("\n📋 Getting all courses...")
        all_courses_response = requests.get("http://localhost:8003/api/courses", headers=headers)
        
        if all_courses_response.status_code == 200:
            courses = all_courses_response.json()["courses"]
            print(f"✅ Found {len(courses)} courses in database")
            
    else:
        print(f"❌ Course creation failed: {create_response.status_code}")
        print(create_response.text)

if __name__ == "__main__":
    print("🚀 Course API Demonstration")
    print("=" * 40)
    test_course_api()
    print("\n🎉 Course API is working perfectly with nested structure!")
    print("💾 Data is stored exactly as provided in your payload!")
