# Comprehensive API Documentation

## 📋 Table of Contents
1. [Overview](#overview)
2. [Authentication](#authentication)
3. [Student Details API](#student-details-api)
4. [Enhanced Course and Category APIs](#enhanced-course-and-category-apis)
5. [Location-Based Data APIs](#location-based-data-apis)
6. [Error Handling](#error-handling)
7. [Testing Examples](#testing-examples)

## Overview

**Base URL**: `http://localhost:8003` (Development) | `https://edumanage-44.preview.dev.com` (Production)

This documentation covers all implemented API endpoints including both authenticated and public endpoints for comprehensive data access.

## Authentication

### Authenticated Endpoints
```
Authorization: Bearer <your_jwt_token>
```

### Public Endpoints
No authentication required - can be accessed directly.

---

## Student Details API

### GET /users/students/details
**Authentication**: Required (Super Admin, Coach Admin, Coach)

**Description**: Returns detailed student information with course enrollment data.

**Response Example**:
```json
{
  "message": "Retrieved 5 student details successfully",
  "students": [
    {
      "student_id": "student-uuid-123",
      "student_name": "John Doe",
      "gender": "male",
      "age": 25,
      "courses": [
        {
          "course_name": "Advanced Kung Fu Training",
          "level": "Advanced",
          "duration": "90 days",
          "enrollment_date": "2024-01-15T10:30:00Z",
          "payment_status": "paid"
        }
      ],
      "email": "john.doe@example.com",
      "phone": "+1234567890",
      "action": "view_profile"
    }
  ],
  "total": 5
}
```

**cURL Example**:
```bash
curl -X GET "http://localhost:8003/users/students/details" \
  -H "Authorization: Bearer <your_token>"
```

---

## Enhanced Course and Category APIs

### 1. GET /categories/public/details
**Authentication**: Not required (Public)

**Description**: Returns category details with associated courses.

**Query Parameters**:
- `category_id` (optional) - Specific category ID
- `include_courses` (boolean, default: true) - Include associated courses
- `active_only` (boolean, default: true) - Filter active items only
- `skip` (integer, default: 0) - Pagination offset
- `limit` (integer, default: 50, max: 100) - Records per page

**Response Example**:
```json
{
  "message": "Retrieved 2 categories with details successfully",
  "categories": [
    {
      "id": "category-uuid-123",
      "name": "Martial Arts",
      "code": "MA",
      "description": "Traditional martial arts training",
      "icon_url": "https://example.com/icon.png",
      "color_code": "#FF5722",
      "course_count": 8,
      "courses": [
        {
          "id": "course-uuid-456",
          "title": "Advanced Kung Fu Training",
          "code": "KF-ADV-001",
          "difficulty_level": "Advanced",
          "pricing": {
            "currency": "INR",
            "amount": 8500
          },
          "duration_options": ["3M", "6M", "1Y"]
        }
      ],
      "subcategories": [
        {
          "id": "subcat-uuid-789",
          "name": "Kung Fu",
          "code": "KF",
          "course_count": 5
        }
      ]
    }
  ],
  "total": 2
}
```

**cURL Example**:
```bash
curl -X GET "http://localhost:8003/categories/public/details?include_courses=true&active_only=true"
```

### 2. GET /courses/public/by-category/{category_id}
**Authentication**: Not required (Public)

**Description**: Returns all courses filtered by category.

**Path Parameters**:
- `category_id` (required) - Category UUID

**Query Parameters**:
- `difficulty_level` (optional) - Filter by difficulty (Beginner, Intermediate, Advanced)
- `active_only` (boolean, default: true) - Filter active courses only
- `include_durations` (boolean, default: true) - Include available durations
- `skip` (integer, default: 0) - Pagination offset
- `limit` (integer, default: 50, max: 100) - Records per page

**Response Example**:
```json
{
  "message": "Retrieved 5 courses for category successfully",
  "category": {
    "id": "category-uuid-123",
    "name": "Martial Arts",
    "code": "MA"
  },
  "courses": [
    {
      "id": "course-uuid-456",
      "title": "Advanced Kung Fu Training",
      "code": "KF-ADV-001",
      "description": "Comprehensive advanced training",
      "difficulty_level": "Advanced",
      "pricing": {
        "currency": "INR",
        "amount": 8500
      },
      "student_requirements": {
        "max_students": 20,
        "min_age": 16,
        "max_age": 50,
        "prerequisites": ["Basic Kung Fu"]
      },
      "available_durations": [
        {
          "id": "duration-uuid-123",
          "name": "3 Months",
          "code": "3M",
          "duration_months": 3,
          "pricing_multiplier": 1.0
        }
      ],
      "locations_offered": [
        {
          "location_id": "loc-uuid-789",
          "location_name": "Hyderabad",
          "branch_count": 3
        }
      ]
    }
  ],
  "total": 5
}
```

**cURL Example**:
```bash
curl -X GET "http://localhost:8003/courses/public/by-category/category-uuid-123?difficulty_level=Advanced&include_durations=true"
```

### 3. GET /durations/public/by-course/{course_id}
**Authentication**: Not required (Public)

**Description**: Returns available durations for a specific course.

**Path Parameters**:
- `course_id` (required) - Course UUID

**Query Parameters**:
- `active_only` (boolean, default: true) - Filter active durations only
- `include_pricing` (boolean, default: true) - Include pricing calculations

**Response Example**:
```json
{
  "message": "Retrieved 3 durations for course successfully",
  "course": {
    "id": "course-uuid-456",
    "title": "Advanced Kung Fu Training",
    "base_price": 8500,
    "currency": "INR"
  },
  "durations": [
    {
      "id": "duration-uuid-123",
      "name": "3 Months",
      "code": "3M",
      "duration_months": 3,
      "duration_days": 90,
      "pricing_multiplier": 1.0,
      "calculated_price": 8500,
      "description": "Standard 3-month course"
    },
    {
      "id": "duration-uuid-456",
      "name": "6 Months",
      "code": "6M",
      "duration_months": 6,
      "duration_days": 180,
      "pricing_multiplier": 1.8,
      "calculated_price": 15300,
      "description": "Extended 6-month course"
    }
  ],
  "total": 3
}
```

**cURL Example**:
```bash
curl -X GET "http://localhost:8003/durations/public/by-course/course-uuid-456?include_pricing=true"
```

### 4. GET /categories/public/with-courses-and-durations
**Authentication**: Not required (Public)

**Description**: Returns categories with their courses and available durations in nested structure.

**Query Parameters**:
- `category_id` (optional) - Specific category ID
- `active_only` (boolean, default: true) - Filter active items only
- `include_locations` (boolean, default: false) - Include location data
- `skip` (integer, default: 0) - Pagination offset
- `limit` (integer, default: 20, max: 50) - Records per page

**Response Example**:
```json
{
  "message": "Retrieved 2 categories with complete hierarchy successfully",
  "categories": [
    {
      "id": "category-uuid-123",
      "name": "Martial Arts",
      "code": "MA",
      "description": "Traditional martial arts training",
      "course_count": 8,
      "courses": [
        {
          "id": "course-uuid-456",
          "title": "Advanced Kung Fu Training",
          "code": "KF-ADV-001",
          "difficulty_level": "Advanced",
          "base_pricing": {
            "currency": "INR",
            "amount": 8500
          },
          "durations": [
            {
              "id": "duration-uuid-123",
              "name": "3 Months",
              "code": "3M",
              "duration_months": 3,
              "pricing_multiplier": 1.0,
              "final_price": 8500
            },
            {
              "id": "duration-uuid-456",
              "name": "6 Months",
              "code": "6M",
              "duration_months": 6,
              "pricing_multiplier": 1.8,
              "final_price": 15300
            }
          ],
          "locations_available": [
            {
              "location_id": "loc-uuid-789",
              "location_name": "Hyderabad",
              "branch_count": 3
            }
          ]
        }
      ]
    }
  ],
  "total": 2
}
```

**cURL Example**:
```bash
curl -X GET "http://localhost:8003/categories/public/with-courses-and-durations?active_only=true&include_locations=true"
```

---

## Location-Based Data APIs

### 1. GET /locations/public/details
**Authentication**: Not required (Public)

**Description**: Returns location details with associated branches.

**Query Parameters**:
- `location_id` (optional) - Specific location ID
- `include_branches` (boolean, default: true) - Include branch details
- `include_courses` (boolean, default: false) - Include available courses
- `active_only` (boolean, default: true) - Filter active items only
- `skip` (integer, default: 0) - Pagination offset
- `limit` (integer, default: 50, max: 100) - Records per page

**Response Example**:
```json
{
  "message": "Retrieved 2 locations with details successfully",
  "locations": [
    {
      "id": "location-uuid-123",
      "name": "Hyderabad",
      "code": "HYD",
      "state": "Telangana",
      "country": "India",
      "timezone": "Asia/Kolkata",
      "branch_count": 3,
      "branches": [
        {
          "id": "branch-uuid-456",
          "name": "Hitech City Branch",
          "code": "HYD-HTC-001",
          "email": "hitech@example.com",
          "phone": "+91-9876543210",
          "address": {
            "line1": "123 Cyber Towers",
            "area": "Hitech City",
            "city": "Hyderabad",
            "state": "Telangana",
            "pincode": "500081",
            "country": "India"
          },
          "courses_offered": ["Kung Fu", "Karate", "Taekwondo"],
          "course_count": 8,
          "timings": [
            {
              "day": "Monday",
              "open": "06:00",
              "close": "22:00"
            }
          ]
        }
      ],
      "total_courses_available": 15
    }
  ],
  "total": 2
}
```

**cURL Example**:
```bash
curl -X GET "http://localhost:8003/locations/public/details?include_branches=true&include_courses=true"
```

### 2. GET /branches/public/by-location/{location_id}
**Authentication**: Not required (Public)

**Description**: Returns branches filtered by location.

**Path Parameters**:
- `location_id` (required) - Location UUID

**Query Parameters**:
- `include_courses` (boolean, default: true) - Include available courses
- `include_timings` (boolean, default: true) - Include operational timings
- `active_only` (boolean, default: true) - Filter active branches only
- `skip` (integer, default: 0) - Pagination offset
- `limit` (integer, default: 50, max: 100) - Records per page

**Response Example**:
```json
{
  "message": "Retrieved 3 branches for location successfully",
  "location": {
    "id": "location-uuid-123",
    "name": "Hyderabad",
    "code": "HYD",
    "state": "Telangana"
  },
  "branches": [
    {
      "id": "branch-uuid-456",
      "name": "Hitech City Branch",
      "code": "HYD-HTC-001",
      "email": "hitech@example.com",
      "phone": "+91-9876543210",
      "address": {
        "line1": "123 Cyber Towers",
        "area": "Hitech City",
        "city": "Hyderabad",
        "state": "Telangana",
        "pincode": "500081",
        "country": "India"
      },
      "available_courses": [
        {
          "id": "course-uuid-789",
          "title": "Advanced Kung Fu Training",
          "code": "KF-ADV-001",
          "category": "Martial Arts",
          "difficulty_level": "Advanced",
          "pricing": {
            "currency": "INR",
            "amount": 8500
          }
        }
      ],
      "timings": [
        {
          "day": "Monday",
          "open": "06:00",
          "close": "22:00"
        },
        {
          "day": "Tuesday",
          "open": "06:00",
          "close": "22:00"
        }
      ],
      "course_count": 8
    }
  ],
  "total": 3
}
```

**cURL Example**:
```bash
curl -X GET "http://localhost:8003/branches/public/by-location/location-uuid-123?include_courses=true"
```

### 3. GET /courses/public/by-location/{location_id}
**Authentication**: Not required (Public)

**Description**: Returns courses available at a specific location.

**Path Parameters**:
- `location_id` (required) - Location UUID

**Query Parameters**:
- `category_id` (optional) - Filter by category
- `difficulty_level` (optional) - Filter by difficulty
- `include_durations` (boolean, default: true) - Include available durations
- `include_branches` (boolean, default: false) - Include branch details
- `active_only` (boolean, default: true) - Filter active courses only
- `skip` (integer, default: 0) - Pagination offset
- `limit` (integer, default: 50, max: 100) - Records per page

**Response Example**:
```json
{
  "message": "Retrieved 8 courses for location successfully",
  "location": {
    "id": "location-uuid-123",
    "name": "Hyderabad",
    "code": "HYD",
    "branch_count": 3
  },
  "courses": [
    {
      "id": "course-uuid-456",
      "title": "Advanced Kung Fu Training",
      "code": "KF-ADV-001",
      "description": "Comprehensive advanced training",
      "category": {
        "id": "category-uuid-123",
        "name": "Martial Arts",
        "code": "MA"
      },
      "difficulty_level": "Advanced",
      "pricing": {
        "currency": "INR",
        "amount": 8500
      },
      "available_durations": [
        {
          "id": "duration-uuid-123",
          "name": "3 Months",
          "code": "3M",
          "final_price": 8500
        }
      ],
      "branches_offering": [
        {
          "id": "branch-uuid-456",
          "name": "Hitech City Branch",
          "code": "HYD-HTC-001",
          "area": "Hitech City"
        }
      ]
    }
  ],
  "total": 8
}
```

**cURL Example**:
```bash
curl -X GET "http://localhost:8003/courses/public/by-location/location-uuid-123?category_id=category-uuid-123&include_durations=true"
```

### 4. GET /durations/public/by-location-course
**Authentication**: Not required (Public)

**Description**: Returns durations based on location and course combination.

**Query Parameters**:
- `location_id` (required) - Location UUID
- `course_id` (required) - Course UUID
- `include_pricing` (boolean, default: true) - Include pricing calculations
- `include_branches` (boolean, default: false) - Include branch availability

**Response Example**:
```json
{
  "message": "Retrieved 3 durations for location-course combination successfully",
  "location": {
    "id": "location-uuid-123",
    "name": "Hyderabad",
    "code": "HYD"
  },
  "course": {
    "id": "course-uuid-456",
    "title": "Advanced Kung Fu Training",
    "base_price": 8500
  },
  "durations": [
    {
      "id": "duration-uuid-123",
      "name": "3 Months",
      "code": "3M",
      "duration_months": 3,
      "duration_days": 90,
      "pricing_multiplier": 1.0,
      "final_price": 8500,
      "available_at_branches": [
        {
          "branch_id": "branch-uuid-456",
          "branch_name": "Hitech City Branch",
          "availability": "available"
        }
      ]
    }
  ],
  "total": 3
}
```

**cURL Example**:
```bash
curl -X GET "http://localhost:8003/durations/public/by-location-course?location_id=location-uuid-123&course_id=course-uuid-456&include_branches=true"
```

### 5. GET /categories/public/location-hierarchy
**Authentication**: Not required (Public)

**Description**: Returns complete hierarchy when a category is selected - category details, courses, locations, branches, and durations.

**Query Parameters**:
- `category_id` (required) - Category UUID
- `location_id` (optional) - Filter by specific location
- `active_only` (boolean, default: true) - Filter active items only
- `include_pricing` (boolean, default: true) - Include pricing calculations

**Response Example**:
```json
{
  "message": "Retrieved complete hierarchy for category successfully",
  "category": {
    "id": "category-uuid-123",
    "name": "Martial Arts",
    "code": "MA",
    "description": "Traditional martial arts training",
    "course_count": 8
  },
  "courses": [
    {
      "id": "course-uuid-456",
      "title": "Advanced Kung Fu Training",
      "code": "KF-ADV-001",
      "difficulty_level": "Advanced",
      "base_pricing": {
        "currency": "INR",
        "amount": 8500
      },
      "locations": [
        {
          "location_id": "location-uuid-123",
          "location_name": "Hyderabad",
          "location_code": "HYD",
          "state": "Telangana",
          "branches": [
            {
              "branch_id": "branch-uuid-456",
              "branch_name": "Hitech City Branch",
              "branch_code": "HYD-HTC-001",
              "address": {
                "area": "Hitech City",
                "city": "Hyderabad",
                "pincode": "500081"
              },
              "contact": {
                "email": "hitech@example.com",
                "phone": "+91-9876543210"
              },
              "timings": [
                {
                  "day": "Monday",
                  "open": "06:00",
                  "close": "22:00"
                }
              ]
            }
          ],
          "branch_count": 3
        }
      ],
      "durations": [
        {
          "id": "duration-uuid-123",
          "name": "3 Months",
          "code": "3M",
          "duration_months": 3,
          "pricing_multiplier": 1.0,
          "final_price": 8500
        },
        {
          "id": "duration-uuid-456",
          "name": "6 Months",
          "code": "6M",
          "duration_months": 6,
          "pricing_multiplier": 1.8,
          "final_price": 15300
        }
      ]
    }
  ],
  "summary": {
    "total_courses": 8,
    "total_locations": 2,
    "total_branches": 5,
    "total_durations": 4,
    "price_range": {
      "min": 8500,
      "max": 25500,
      "currency": "INR"
    }
  }
}
```

**cURL Example**:
```bash
curl -X GET "http://localhost:8003/categories/public/location-hierarchy?category_id=category-uuid-123&include_pricing=true"
```

---

## Error Handling

All endpoints return consistent error responses:

### 400 Bad Request
```json
{
  "detail": "Invalid request parameters or missing required fields"
}
```

### 404 Not Found
```json
{
  "detail": "Resource not found"
}
```

### 422 Validation Error
```json
{
  "detail": [
    {
      "loc": ["query", "category_id"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

### 500 Internal Server Error
```json
{
  "detail": "Internal server error"
}
```

---

## Testing Examples

### Complete Workflow Testing

#### 1. Category Selection Workflow
```bash
# Step 1: Get all categories with courses and durations
curl -X GET "http://localhost:8003/categories/public/with-courses-and-durations?active_only=true"

# Step 2: Get complete hierarchy for a specific category
curl -X GET "http://localhost:8003/categories/public/location-hierarchy?category_id=category-uuid-123"

# Step 3: Get courses by category
curl -X GET "http://localhost:8003/courses/public/by-category/category-uuid-123?include_durations=true"
```

#### 2. Location Selection Workflow
```bash
# Step 1: Get all locations with branches
curl -X GET "http://localhost:8003/locations/public/details?include_branches=true&include_courses=true"

# Step 2: Get branches by location
curl -X GET "http://localhost:8003/branches/public/by-location/location-uuid-123?include_courses=true"

# Step 3: Get courses by location
curl -X GET "http://localhost:8003/courses/public/by-location/location-uuid-123?include_durations=true"
```

#### 3. Course Selection Workflow
```bash
# Step 1: Get courses by category
curl -X GET "http://localhost:8003/courses/public/by-category/category-uuid-123"

# Step 2: Get durations for specific course
curl -X GET "http://localhost:8003/durations/public/by-course/course-uuid-456?include_pricing=true"

# Step 3: Get durations by location and course
curl -X GET "http://localhost:8003/durations/public/by-location-course?location_id=location-uuid-123&course_id=course-uuid-456"
```

### Postman Collection Import

```json
{
  "info": {
    "name": "Comprehensive API Collection",
    "description": "Complete collection for all implemented endpoints"
  },
  "variable": [
    {
      "key": "base_url",
      "value": "http://localhost:8003"
    }
  ],
  "item": [
    {
      "name": "Categories",
      "item": [
        {
          "name": "Get Categories with Details",
          "request": {
            "method": "GET",
            "url": "{{base_url}}/categories/public/details?include_courses=true"
          }
        },
        {
          "name": "Get Category Location Hierarchy",
          "request": {
            "method": "GET",
            "url": "{{base_url}}/categories/public/location-hierarchy?category_id={{category_id}}"
          }
        }
      ]
    },
    {
      "name": "Courses",
      "item": [
        {
          "name": "Get Courses by Category",
          "request": {
            "method": "GET",
            "url": "{{base_url}}/courses/public/by-category/{{category_id}}?include_durations=true"
          }
        },
        {
          "name": "Get Courses by Location",
          "request": {
            "method": "GET",
            "url": "{{base_url}}/courses/public/by-location/{{location_id}}?include_durations=true"
          }
        }
      ]
    }
  ]
}
```

---

## Performance Notes

- All public endpoints are optimized for performance with proper database indexing
- Pagination is implemented to handle large datasets efficiently
- Response caching is recommended for frequently accessed endpoints
- Rate limiting is applied to prevent abuse (100 requests per minute per IP)

## Data Consistency

All endpoints ensure data consistency by:
- Using proper database relationships and joins
- Implementing data validation at multiple levels
- Providing consistent response formats across all endpoints
- Handling edge cases and missing data gracefully
