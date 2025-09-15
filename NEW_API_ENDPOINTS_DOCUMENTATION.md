# New API Endpoints Documentation

This document provides comprehensive documentation for the newly implemented API endpoints as requested.

## Overview

The following API endpoints have been implemented:

1. **Student Details API (Authenticated)** - Returns detailed student information with course enrollment data
2. **Public Courses API** - Returns all available courses without authentication
3. **Categories Management API** - Full CRUD operations for course categories
4. **Duration Management API** - Full CRUD operations for course durations
5. **Locations and Branches API** - Returns all locations with their associated branches

## Base URL

```
Development: http://localhost:8003
Production: https://edumanage-44.preview.dev.com
```

## Authentication

### Authenticated Endpoints
Authenticated endpoints require a Bearer token in the Authorization header:

```
Authorization: Bearer <your_jwt_token>
```

### Public Endpoints
Public endpoints do not require authentication and can be accessed directly.

---

## 1. Student Details API (Authenticated)

### GET /users/students/details

**Description**: Returns detailed student information with their associated course enrollment data.

**Authentication**: Required (Super Admin, Coach Admin, or Coach)

**Access Control**:
- **Super Admin**: Can view all students across all branches
- **Coach Admin**: Can view students in their assigned branch only
- **Coach**: Can view students in their assigned branch only

**Request Headers**:
```
Authorization: Bearer <token>
Content-Type: application/json
```

**Response Format**:
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

## 2. Public Courses API

### GET /courses/public/all

**Description**: Returns all available courses without requiring authentication.

**Authentication**: Not required (Public endpoint)

**Query Parameters**:
- `active_only` (boolean, default: true) - Filter for active courses only
- `skip` (integer, default: 0) - Number of records to skip for pagination
- `limit` (integer, default: 100, max: 100) - Number of records to return

**Response Format**:
```json
{
  "message": "Retrieved 3 courses successfully",
  "courses": [
    {
      "id": "course-uuid-123",
      "title": "Advanced Kung Fu Training",
      "code": "KF-ADV-001",
      "description": "A comprehensive course covering advanced Kung Fu techniques.",
      "difficulty_level": "Advanced",
      "category_id": "category-uuid-456",
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
      "offers_certification": true,
      "media_resources": {
        "course_image_url": "https://example.com/course-image.jpg",
        "promo_video_url": "https://example.com/promo-video.mp4"
      },
      "created_at": "2024-01-01T00:00:00Z"
    }
  ],
  "total": 3,
  "skip": 0,
  "limit": 100
}
```

**cURL Example**:
```bash
curl -X GET "http://localhost:8003/courses/public/all?active_only=true&limit=50"
```

---

## 3. Categories Management API

### 3.1 GET /categories/public/all (Public)

**Description**: Returns all course categories without requiring authentication.

**Authentication**: Not required (Public endpoint)

**Query Parameters**:
- `active_only` (boolean, default: true) - Filter for active categories only
- `include_subcategories` (boolean, default: true) - Include subcategories in response
- `skip` (integer, default: 0) - Number of records to skip for pagination
- `limit` (integer, default: 100, max: 100) - Number of records to return

**Response Format**:
```json
{
  "message": "Retrieved 2 categories successfully",
  "categories": [
    {
      "id": "category-uuid-123",
      "name": "Martial Arts",
      "code": "MA",
      "description": "Traditional and modern martial arts disciplines",
      "icon_url": "https://example.com/martial-arts-icon.png",
      "color_code": "#FF5722",
      "course_count": 15,
      "subcategories": [
        {
          "id": "subcat-uuid-456",
          "name": "Kung Fu",
          "code": "KF",
          "description": "Chinese martial arts",
          "course_count": 8
        }
      ]
    }
  ],
  "total": 2,
  "skip": 0,
  "limit": 100
}
```

### 3.2 POST /categories (Authenticated - Super Admin Only)

**Description**: Create a new category.

**Authentication**: Required (Super Admin only)

**Request Body**:
```json
{
  "name": "Martial Arts",
  "code": "MA",
  "description": "Traditional and modern martial arts disciplines",
  "parent_category_id": null,
  "is_active": true,
  "display_order": 1,
  "icon_url": "https://example.com/icon.png",
  "color_code": "#FF5722"
}
```

**Response Format**:
```json
{
  "message": "Category created successfully",
  "category_id": "category-uuid-123"
}
```

### 3.3 GET /categories (Authenticated)

**Description**: Get categories with filtering options.

**Authentication**: Required

**Query Parameters**:
- `parent_id` (string, optional) - Filter by parent category ID
- `active_only` (boolean, default: true) - Filter for active categories only
- `include_subcategories` (boolean, default: false) - Include subcategories
- `skip` (integer, default: 0) - Pagination offset
- `limit` (integer, default: 50) - Number of records to return

### 3.4 PUT /categories/{category_id} (Authenticated - Super Admin Only)

**Description**: Update an existing category.

**Authentication**: Required (Super Admin only)

### 3.5 DELETE /categories/{category_id} (Authenticated - Super Admin Only)

**Description**: Delete a category (only if no courses or subcategories exist).

**Authentication**: Required (Super Admin only)

---

## 4. Duration Management API

### 4.1 GET /durations/public/all (Public)

**Description**: Returns all available course durations without requiring authentication.

**Authentication**: Not required (Public endpoint)

**Query Parameters**:
- `active_only` (boolean, default: true) - Filter for active durations only
- `skip` (integer, default: 0) - Number of records to skip for pagination
- `limit` (integer, default: 100, max: 100) - Number of records to return

**Response Format**:
```json
{
  "message": "Retrieved 4 durations successfully",
  "durations": [
    {
      "id": "duration-uuid-123",
      "name": "3 Months",
      "code": "3M",
      "duration_months": 3,
      "duration_days": 90,
      "description": "Standard 3-month course duration",
      "pricing_multiplier": 1.0
    },
    {
      "id": "duration-uuid-456",
      "name": "6 Months",
      "code": "6M",
      "duration_months": 6,
      "duration_days": 180,
      "description": "Extended 6-month course duration",
      "pricing_multiplier": 1.8
    }
  ],
  "total": 4,
  "skip": 0,
  "limit": 100
}
```

### 4.2 POST /durations (Authenticated - Super Admin Only)

**Description**: Create a new duration.

**Authentication**: Required (Super Admin only)

**Request Body**:
```json
{
  "name": "3 Months",
  "code": "3M",
  "duration_months": 3,
  "duration_days": 90,
  "description": "Standard 3-month course duration",
  "is_active": true,
  "display_order": 1,
  "pricing_multiplier": 1.0
}
```

**Response Format**:
```json
{
  "message": "Duration created successfully",
  "duration_id": "duration-uuid-123"
}
```

### 4.3 GET /durations (Authenticated)

**Description**: Get durations with filtering options.

**Authentication**: Required

### 4.4 PUT /durations/{duration_id} (Authenticated - Super Admin Only)

**Description**: Update an existing duration.

**Authentication**: Required (Super Admin only)

### 4.5 DELETE /durations/{duration_id} (Authenticated - Super Admin Only)

**Description**: Delete a duration.

**Authentication**: Required (Super Admin only)

---

## 5. Locations and Branches API

### GET /locations/public/with-branches

**Description**: Returns all locations with their associated branches without requiring authentication.

**Authentication**: Not required (Public endpoint)

**Query Parameters**:
- `active_only` (boolean, default: true) - Filter for active locations and branches only
- `skip` (integer, default: 0) - Number of records to skip for pagination
- `limit` (integer, default: 100, max: 100) - Number of records to return

**Response Format**:
```json
{
  "message": "Retrieved 2 locations with branches successfully",
  "locations": [
    {
      "id": "location-uuid-123",
      "name": "Hyderabad",
      "code": "HYD",
      "state": "Telangana",
      "country": "India",
      "timezone": "Asia/Kolkata",
      "is_active": true,
      "display_order": 1,
      "description": "IT hub of South India",
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
          "timings": [
            {
              "day": "Monday",
              "open": "06:00",
              "close": "22:00"
            }
          ]
        }
      ],
      "created_at": "2024-01-01T00:00:00Z",
      "updated_at": "2024-01-01T00:00:00Z"
    }
  ],
  "total": 2,
  "skip": 0,
  "limit": 100
}
```

**cURL Example**:
```bash
curl -X GET "http://localhost:8003/locations/public/with-branches?active_only=true"
```

---

## Error Responses

All endpoints return consistent error responses:

### 400 Bad Request
```json
{
  "detail": "Invalid request parameters or data"
}
```

### 401 Unauthorized
```json
{
  "detail": "Authentication required"
}
```

### 403 Forbidden
```json
{
  "detail": "Insufficient permissions"
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
      "loc": ["body", "field_name"],
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

## Rate Limiting

Public endpoints are limited to 100 requests per minute per IP address to prevent abuse.

## Data Validation

All endpoints include comprehensive data validation using Pydantic models to ensure data integrity and consistency.

## Pagination

All list endpoints support pagination with `skip` and `limit` parameters. Public endpoints have a maximum limit of 100 records per request.

---

## Implementation Notes

### Database Collections

The following new MongoDB collections have been created:

1. **categories** - Stores course category information
2. **durations** - Stores course duration options
3. **locations** - Stores location/city information

### Authentication Integration

All authenticated endpoints integrate with the existing JWT authentication system and support both regular user tokens and superadmin tokens.

### Role-Based Access Control

The APIs implement proper RBAC:
- **Super Admin**: Full access to all endpoints and operations
- **Coach Admin**: Limited access based on branch assignment
- **Coach**: Read-only access to students in their branch
- **Student**: No access to these management APIs

### Data Relationships

- Categories support hierarchical structure with parent-child relationships
- Locations are linked to branches through city name matching
- Durations include pricing multipliers for flexible pricing
- Student details aggregate data from users, enrollments, and courses collections

---

## Testing Examples

### 1. Test Student Details API

```bash
# First, get an authentication token
curl -X POST "http://localhost:8003/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@example.com",
    "password": "admin123"
  }'

# Use the token to get student details
curl -X GET "http://localhost:8003/users/students/details" \
  -H "Authorization: Bearer <token_from_login>"
```

### 2. Test Public Courses API

```bash
# No authentication required
curl -X GET "http://localhost:8003/courses/public/all?active_only=true&limit=10"
```

### 3. Test Categories API

```bash
# Public endpoint - no auth required
curl -X GET "http://localhost:8003/categories/public/all?include_subcategories=true"

# Create category (requires Super Admin token)
curl -X POST "http://localhost:8003/categories" \
  -H "Authorization: Bearer <super_admin_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Martial Arts",
    "code": "MA",
    "description": "Traditional martial arts training",
    "is_active": true,
    "display_order": 1
  }'
```

### 4. Test Durations API

```bash
# Public endpoint
curl -X GET "http://localhost:8003/durations/public/all"

# Create duration (requires Super Admin token)
curl -X POST "http://localhost:8003/durations" \
  -H "Authorization: Bearer <super_admin_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "3 Months",
    "code": "3M",
    "duration_months": 3,
    "duration_days": 90,
    "pricing_multiplier": 1.0
  }'
```

### 5. Test Locations and Branches API

```bash
# Public endpoint
curl -X GET "http://localhost:8003/locations/public/with-branches?active_only=true"
```

---

## Postman Collection

A Postman collection with all the new endpoints is available. Import the following JSON structure:

```json
{
  "info": {
    "name": "New API Endpoints",
    "description": "Collection for newly implemented API endpoints"
  },
  "item": [
    {
      "name": "Student Details",
      "request": {
        "method": "GET",
        "header": [
          {
            "key": "Authorization",
            "value": "Bearer {{token}}"
          }
        ],
        "url": {
          "raw": "{{base_url}}/users/students/details",
          "host": ["{{base_url}}"],
          "path": ["users", "students", "details"]
        }
      }
    },
    {
      "name": "Public Courses",
      "request": {
        "method": "GET",
        "url": {
          "raw": "{{base_url}}/courses/public/all?active_only=true&limit=50",
          "host": ["{{base_url}}"],
          "path": ["courses", "public", "all"],
          "query": [
            {"key": "active_only", "value": "true"},
            {"key": "limit", "value": "50"}
          ]
        }
      }
    }
  ],
  "variable": [
    {
      "key": "base_url",
      "value": "http://localhost:8003"
    },
    {
      "key": "token",
      "value": "your_jwt_token_here"
    }
  ]
}
```

---

## Security Considerations

1. **Input Validation**: All endpoints include comprehensive input validation
2. **SQL Injection Prevention**: Using MongoDB with proper query construction
3. **Rate Limiting**: Public endpoints are rate-limited to prevent abuse
4. **Authentication**: Proper JWT token validation for protected endpoints
5. **Authorization**: Role-based access control implemented
6. **Data Sanitization**: All user inputs are sanitized before processing

---

## Performance Optimizations

1. **Database Indexing**: Recommended indexes for optimal performance:
   ```javascript
   // Categories collection
   db.categories.createIndex({ "code": 1 }, { unique: true })
   db.categories.createIndex({ "parent_category_id": 1 })
   db.categories.createIndex({ "is_active": 1, "display_order": 1 })

   // Durations collection
   db.durations.createIndex({ "code": 1 }, { unique: true })
   db.durations.createIndex({ "is_active": 1, "display_order": 1 })

   // Locations collection
   db.locations.createIndex({ "code": 1 }, { unique: true })
   db.locations.createIndex({ "is_active": 1, "display_order": 1 })
   ```

2. **Caching**: Consider implementing Redis caching for frequently accessed public endpoints

3. **Pagination**: All list endpoints support pagination to handle large datasets efficiently

---

## Monitoring and Logging

All endpoints include proper logging for:
- Request/response tracking
- Error monitoring
- Performance metrics
- Security events

Use the existing logging infrastructure to monitor API usage and performance.
