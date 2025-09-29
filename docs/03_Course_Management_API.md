# Course Management API Documentation

## Overview
The Course Management API provides comprehensive functionality for managing martial arts courses in the Marshalats Learning Management System. It supports complex nested data structures for course content, student requirements, pricing, and media resources.

## Base URL
```
Development: http://31.97.224.169:8003/api/courses
Production: https://edumanage-44.preview.dev.com/api/courses
```

## Authentication
All endpoints require authentication via Bearer token in the Authorization header:
```
Authorization: Bearer <jwt_token>
```

### Getting Authentication Token
To get a superadmin token for course management:

```bash
# Login as superadmin
curl -X POST "http://31.97.224.169:8003/api/superadmin/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "superadmin@example.com",
    "password": "StrongPassword@123"
  }'

# Response will include token in data.token field
{
  "status": "success",
  "message": "Login successful",
  "data": {
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "bearer"
  }
}
```

## User Roles and Permissions

### Course Management Permissions
- **super_admin** - Full course management access (create, read, update, delete)
- **coach_admin** - Can update courses where they are the instructor, view all courses
- **coach** - Can view courses only
- **student** - Can view active courses only

---

## Endpoints

### POST /api/courses
Create a new course with comprehensive nested structure.

**Authentication:** Required
**Permissions:** Super Admin only

**Request Body:**
```json
{
  "title": "Advanced Kung Fu Training",
  "code": "KF-ADV-001",
  "description": "A comprehensive course covering advanced Kung Fu techniques including forms, sparring, and philosophy.",
  "martial_art_style_id": "style-uuid-here",
  "difficulty_level": "Advanced",
  "category_id": "category-uuid-here",
  "instructor_id": "instructor-uuid-here",
  "student_requirements": {
    "max_students": 20,
    "min_age": 16,
    "max_age": 65,
    "prerequisites": ["Basic Kung Fu certification", "6 months experience"]
  },
  "course_content": {
    "syllabus": "Week 1-4: Advanced forms and techniques\nWeek 5-8: Sparring fundamentals\nWeek 9-12: Philosophy and meditation",
    "equipment_required": ["Uniform", "Protective gear", "Training weapons"]
  },
  "media_resources": {
    "course_image_url": "https://example.com/course-image.jpg",
    "promo_video_url": "https://example.com/promo-video.mp4"
  },
  "pricing": {
    "currency": "USD",
    "amount": 299.99,
    "branch_specific_pricing": false
  },
  "settings": {
    "offers_certification": true,
    "active": true
  }
}
```

**Response (201 Created):**
```json
{
  "message": "Course created successfully",
  "course_id": "course-uuid-here"
}
```

### GET /api/courses
Retrieve courses with filtering and pagination options.

**Authentication:** Required
**Permissions:** All authenticated users

**Query Parameters:**
- `category_id` (optional): Filter by course category
- `difficulty_level` (optional): Filter by difficulty (Beginner, Intermediate, Advanced)
- `instructor_id` (optional): Filter by instructor
- `active_only` (optional, default: true): Show only active courses
- `skip` (optional, default: 0): Number of courses to skip for pagination
- `limit` (optional, default: 50, max: 100): Number of courses to return

**Example Request:**
```
GET /api/courses?difficulty_level=Advanced&active_only=true&skip=0&limit=10
```

**Response (200 OK):**
```json
{
  "courses": [
    {
      "id": "course-uuid-here",
      "title": "Advanced Kung Fu Training",
      "code": "KF-ADV-001",
      "description": "A comprehensive course covering advanced Kung Fu techniques.",
      "martial_art_style_id": "style-uuid-here",
      "difficulty_level": "Advanced",
      "category_id": "category-uuid-here",
      "instructor_id": "instructor-uuid-here",
      "student_requirements": {
        "max_students": 20,
        "min_age": 16,
        "max_age": 65,
        "prerequisites": ["Basic Kung Fu certification", "6 months experience"]
      },
      "course_content": {
        "syllabus": "Week 1-4: Advanced forms and techniques...",
        "equipment_required": ["Uniform", "Protective gear", "Training weapons"]
      },
      "media_resources": {
        "course_image_url": "https://example.com/course-image.jpg",
        "promo_video_url": "https://example.com/promo-video.mp4"
      },
      "pricing": {
        "currency": "USD",
        "amount": 299.99,
        "branch_specific_pricing": false
      },
      "settings": {
        "offers_certification": true,
        "active": true
      },
      "created_at": "2024-01-20T10:30:00Z",
      "updated_at": "2024-01-20T10:30:00Z"
    }
  ]
}
```

### GET /api/courses/{course_id}
Retrieve a specific course by ID.

**Authentication:** Required
**Permissions:** All authenticated users

**Path Parameters:**
- `course_id`: UUID of the course

**Response (200 OK):**
```json
{
  "course": {
    "id": "course-uuid-here",
    "title": "Advanced Kung Fu Training",
    "code": "KF-ADV-001",
    "description": "A comprehensive course covering advanced Kung Fu techniques.",
    "martial_art_style_id": "style-uuid-here",
    "difficulty_level": "Advanced",
    "category_id": "category-uuid-here",
    "instructor_id": "instructor-uuid-here",
    "student_requirements": {
      "max_students": 20,
      "min_age": 16,
      "max_age": 65,
      "prerequisites": ["Basic Kung Fu certification", "6 months experience"]
    },
    "course_content": {
      "syllabus": "Week 1-4: Advanced forms and techniques\nWeek 5-8: Sparring fundamentals\nWeek 9-12: Philosophy and meditation",
      "equipment_required": ["Uniform", "Protective gear", "Training weapons"]
    },
    "media_resources": {
      "course_image_url": "https://example.com/course-image.jpg",
      "promo_video_url": "https://example.com/promo-video.mp4"
    },
    "pricing": {
      "currency": "USD",
      "amount": 299.99,
      "branch_specific_pricing": false
    },
    "settings": {
      "offers_certification": true,
      "active": true
    },
    "created_at": "2024-01-20T10:30:00Z",
    "updated_at": "2024-01-20T10:30:00Z"
  }
}
```

### PUT /api/courses/{course_id}
Update an existing course.

**Authentication:** Required
**Permissions:** Super Admin, Coach Admin (instructor only)

**Path Parameters:**
- `course_id`: UUID of the course to update

**Role Restrictions:**
- **Coach Admin:** Can only update courses where they are listed as the instructor

**Request Body (all fields optional):**
```json
{
  "title": "Updated Advanced Kung Fu Training",
  "description": "Updated comprehensive course description",
  "student_requirements": {
    "max_students": 25,
    "min_age": 14,
    "max_age": 70,
    "prerequisites": ["Updated prerequisites"]
  },
  "course_content": {
    "syllabus": "Updated syllabus content",
    "equipment_required": ["Updated equipment list"]
  },
  "media_resources": {
    "course_image_url": "https://example.com/new-image.jpg",
    "promo_video_url": "https://example.com/new-video.mp4"
  },
  "pricing": {
    "currency": "USD",
    "amount": 349.99,
    "branch_specific_pricing": true
  },
  "settings": {
    "offers_certification": true,
    "active": true
  }
}
```

**Response (200 OK):**
```json
{
  "message": "Course updated successfully",
  "course": {
    "id": "course-uuid-here",
    "title": "Updated Advanced Kung Fu Training",
    "updated_at": "2024-01-22T14:30:00Z"
  }
}
```

### GET /api/courses/{course_id}/stats
Get statistics and analytics for a specific course.

**Authentication:** Required
**Permissions:** Super Admin, Coach Admin

**Path Parameters:**
- `course_id`: UUID of the course

**Response (200 OK):**
```json
{
  "course_details": {
    "id": "course-uuid-here",
    "title": "Advanced Kung Fu Training",
    "code": "KF-ADV-001",
    "instructor_id": "instructor-uuid-here",
    "student_requirements": {
      "max_students": 20
    },
    "settings": {
      "active": true,
      "offers_certification": true
    }
  },
  "active_enrollments": 15,
  "enrollment_rate": 75.0,
  "completion_rate": 85.5,
  "average_rating": 4.7
}
```

---

## Data Models

### Course Object Structure
```json
{
  "id": "string (UUID)",
  "title": "string",
  "code": "string (unique course code)",
  "description": "string",
  "martial_art_style_id": "string (UUID)",
  "difficulty_level": "string (Beginner|Intermediate|Advanced)",
  "category_id": "string (UUID)",
  "instructor_id": "string (UUID)",
  "student_requirements": {
    "max_students": "integer",
    "min_age": "integer",
    "max_age": "integer",
    "prerequisites": ["string array"]
  },
  "course_content": {
    "syllabus": "string (detailed course outline)",
    "equipment_required": ["string array"]
  },
  "media_resources": {
    "course_image_url": "string (optional)",
    "promo_video_url": "string (optional)"
  },
  "pricing": {
    "currency": "string (USD, EUR, INR, etc.)",
    "amount": "float",
    "branch_specific_pricing": "boolean"
  },
  "settings": {
    "offers_certification": "boolean",
    "active": "boolean"
  },
  "created_at": "string (ISO 8601)",
  "updated_at": "string (ISO 8601)"
}
```

### Difficulty Levels
- `"Beginner"` - Entry-level courses for new students
- `"Intermediate"` - Courses requiring some prior experience
- `"Advanced"` - Expert-level courses with significant prerequisites

### Course Categories
Courses are organized by categories (category_id references):
- Martial Arts Fundamentals
- Weapons Training
- Competition Preparation
- Self-Defense
- Philosophy and Meditation
- Instructor Training

---

## Error Responses

### 400 Bad Request
```json
{
  "detail": "Invalid course data",
  "errors": [
    {
      "field": "code",
      "message": "Course code already exists"
    }
  ]
}
```

### 401 Unauthorized
```json
{
  "detail": "Invalid authentication credentials"
}
```

### 403 Forbidden
```json
{
  "detail": "You can only update courses where you are the instructor"
}
```

### 404 Not Found
```json
{
  "detail": "Course not found"
}
```

---

## Usage Examples

### Create a New Course (Super Admin)
```bash
curl -X POST "http://31.97.224.169:8003/api/courses" \
  -H "Authorization: Bearer <super_admin_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Beginner Karate",
    "code": "KAR-BEG-001",
    "description": "Introduction to Karate fundamentals",
    "difficulty_level": "Beginner",
    "student_requirements": {
      "max_students": 30,
      "min_age": 6,
      "max_age": 99,
      "prerequisites": []
    },
    "pricing": {
      "currency": "USD",
      "amount": 149.99,
      "branch_specific_pricing": false
    },
    "settings": {
      "offers_certification": true,
      "active": true
    }
  }'
```

### Get Active Advanced Courses
```bash
curl -X GET "http://31.97.224.169:8003/api/courses?difficulty_level=Advanced&active_only=true" \
  -H "Authorization: Bearer <token>"
```

### Update Course Pricing (Coach Admin)
```bash
curl -X PUT "http://31.97.224.169:8003/api/courses/course-uuid-here" \
  -H "Authorization: Bearer <coach_admin_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "pricing": {
      "currency": "USD",
      "amount": 199.99,
      "branch_specific_pricing": true
    }
  }'
```

---

## Integration Notes

### Course Enrollment Integration
- Courses integrate with the Enrollment API for student registration
- Student requirements are validated during enrollment
- Course capacity is checked against max_students setting

### Instructor Integration
- instructor_id references users with "coach" or "coach_admin" roles
- Instructors can update their own courses (coach_admin permission)
- Course statistics include instructor performance metrics

### Branch Integration
- Courses can have branch-specific pricing
- Branch availability affects course visibility
- Course schedules are managed at the branch level

### Payment Integration
- Course pricing integrates with the Payment API
- Supports multiple currencies
- Branch-specific pricing allows regional variations

---

## Working Example - Complete Course Management Flow

### Step 1: Get Superadmin Token
```bash
curl -X POST "http://31.97.224.169:8003/api/superadmin/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "superadmin@example.com",
    "password": "StrongPassword@123"
  }'
```

### Step 2: Create a Course
```bash
curl -X POST "http://31.97.224.169:8003/api/courses" \
  -H "Authorization: Bearer <token_from_step_1>" \
  -H "Content-Type: application/json" \
  -d '{
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
      "branch_specific_pricing": false
    },
    "settings": {
      "offers_certification": true,
      "active": true
    }
  }'
```

### Step 3: Retrieve All Courses
```bash
curl -X GET "http://31.97.224.169:8003/api/courses" \
  -H "Authorization: Bearer <token_from_step_1>"
```

### Step 4: Get Specific Course
```bash
curl -X GET "http://31.97.224.169:8003/api/courses/<course_id_from_step_2>" \
  -H "Authorization: Bearer <token_from_step_1>"
```

**Status:** ✅ All course APIs are fully functional and tested (Updated: 2025-09-06)
