#!/usr/bin/env python3

import requests
import json

# API base URL
BASE_URL = "http://31.97.224.169:8003/api"

def get_token():
    """Get authentication token"""
    login_data = {
        "email": "superadmin@example.com",
        "password": "StrongPassword@123"
    }

    print("🔐 Logging in as super admin...")
    response = requests.post(f"{BASE_URL}/superadmin/login", json=login_data)

    if response.status_code == 200:
        token = response.json()["data"]["token"]
        print("✅ Login successful!")
        return token
    else:
        print(f"❌ Login failed: {response.status_code}")
        print("Response:", response.text)
        return None

def test_course_creation(token):
    """Test course creation with comprehensive nested structure"""
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # Your exact payload structure
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
    
    print("\n🥋 Testing course creation...")
    print("POST /api/courses")
    print("Payload:", json.dumps(course_payload, indent=2))
    
    response = requests.post(f"{BASE_URL}/courses", json=course_payload, headers=headers)
    
    print(f"\n📊 Response Status: {response.status_code}")
    print("Response Body:", response.text)
    
    if response.status_code == 200:
        print("✅ Course creation successful!")
        return response.json()
    else:
        print("❌ Course creation failed!")
        return None

def test_get_courses(token):
    """Test getting courses to verify nested structure is preserved"""
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    print("\n📋 Testing GET courses...")
    response = requests.get(f"{BASE_URL}/courses", headers=headers)
    
    print(f"📊 Response Status: {response.status_code}")
    if response.status_code == 200:
        courses = response.json()["courses"]
        print(f"Found {len(courses)} courses")
        if courses:
            latest_course = courses[-1]
            print(f"Latest course: {latest_course['title']} (ID: {latest_course['id']})")
            print("Nested structure preserved:")
            print(f"- Student Requirements: {latest_course['student_requirements']}")
            print(f"- Course Content: {latest_course['course_content']}")
            print(f"- Media Resources: {latest_course['media_resources']}")
            print(f"- Pricing: {latest_course['pricing']}")
            print(f"- Settings: {latest_course['settings']}")
    else:
        print("Response Body:", response.text)

def test_get_specific_course(token, course_id):
    """Test getting a specific course by ID"""
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    print(f"\n🎯 Testing GET course by ID: {course_id}")
    response = requests.get(f"{BASE_URL}/courses/{course_id}", headers=headers)
    
    print(f"📊 Response Status: {response.status_code}")
    if response.status_code == 200:
        course = response.json()
        print("✅ Course retrieved successfully!")
        print("Complete nested structure:")
        print(json.dumps(course, indent=2))
    else:
        print("Response Body:", response.text)

def main():
    print("🚀 Testing Course Creation API with Nested Structure")
    print("=" * 60)
    
    # Get authentication token
    token = get_token()
    if not token:
        return
    
    # Test course creation
    result = test_course_creation(token)
    if result:
        course_id = result.get("course_id")
        
        # Test getting all courses
        test_get_courses(token)
        
        # Test getting specific course
        if course_id:
            test_get_specific_course(token, course_id)

if __name__ == "__main__":
    main()
