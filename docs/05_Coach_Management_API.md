# Coach Management API Documentation

## Overview
The Coach Management API provides comprehensive functionality for managing martial arts instructors in the Marshalats Learning Management System. It supports complex nested data structures for personal information, professional details, contact information, and authentication.

## Base URL
```
Development: http://localhost:8003/api/coaches
Production: https://edumanage-44.preview.dev.com/api/coaches
```

## Authentication
Most endpoints require authentication via Bearer token in the Authorization header:
```
Authorization: Bearer <jwt_token>
```

### Getting Authentication Token
For coach management operations, you can use either coach login or superadmin login:

#### Option 1: Coach Login
```bash
curl -X POST "http://localhost:8003/api/coaches/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "coach@example.com",
    "password": "password123"
  }'
```

#### Option 2: Superadmin Login (Full Access)
```bash
curl -X POST "http://localhost:8003/api/superadmin/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "superadmin@example.com",
    "password": "StrongPassword@123"
  }'
```

## User Roles and Permissions

### Coach Management Permissions
- **super_admin** - Full coach management access (create, read, update, delete, statistics)
- **coach_admin** - Can create and update coaches, view all coaches
- **coach** - Can view own profile and other coaches, limited update access
- **student** - No coach management access

---

## Endpoints

### POST /api/coaches/login
Authenticate coach and receive JWT token.

**Authentication:** Not required
**Permissions:** Public endpoint

**Request Body:**
```json
{
  "email": "coach@example.com",
  "password": "securePassword123"
}
```

**Response (200 OK):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 86400,
  "message": "Login successful",
  "coach": {
    "id": "coach-uuid-here",
    "personal_info": {
      "first_name": "John",
      "last_name": "Smith",
      "gender": "Male",
      "date_of_birth": "1985-03-15"
    },
    "contact_info": {
      "email": "coach@example.com",
      "country_code": "+1",
      "phone": "5551234567"
    },
    "address_info": {
      "address": "123 Main Street",
      "area": "Downtown",
      "city": "New York",
      "state": "NY",
      "zip_code": "10001",
      "country": "USA"
    },
    "professional_info": {
      "education_qualification": "Bachelor's in Sports Science",
      "professional_experience": "10 years martial arts instruction",
      "designation_id": "senior-instructor",
      "certifications": ["Black Belt Karate", "First Aid Certified"]
    },
    "areas_of_expertise": ["Karate", "Self-Defense", "Youth Training"],
    "full_name": "John Smith",
    "role": "coach",
    "is_active": true,
    "created_at": "2024-01-20T10:30:00Z"
  }
}
```

### GET /api/coaches/me
Get current authenticated coach's profile.

**Authentication:** Required (Coach token)
**Permissions:** Coach only

**Response (200 OK):**
```json
{
  "coach": {
    "id": "coach-uuid-here",
    "personal_info": {
      "first_name": "John",
      "last_name": "Smith",
      "gender": "Male",
      "date_of_birth": "1985-03-15"
    },
    "contact_info": {
      "email": "coach@example.com",
      "country_code": "+1",
      "phone": "5551234567"
    },
    "address_info": {
      "address": "123 Main Street",
      "area": "Downtown",
      "city": "New York",
      "state": "NY",
      "zip_code": "10001",
      "country": "USA"
    },
    "professional_info": {
      "education_qualification": "Bachelor's in Sports Science",
      "professional_experience": "10 years martial arts instruction",
      "designation_id": "senior-instructor",
      "certifications": ["Black Belt Karate", "First Aid Certified"]
    },
    "areas_of_expertise": ["Karate", "Self-Defense", "Youth Training"],
    "full_name": "John Smith",
    "role": "coach",
    "is_active": true
  }
}
```

### POST /api/coaches
Create a new coach with comprehensive nested structure.

**Authentication:** Required
**Permissions:** Super Admin, Coach Admin

**Request Body:**
```json
{
  "personal_info": {
    "first_name": "Jane",
    "last_name": "Doe",
    "gender": "Female",
    "date_of_birth": "1990-07-22"
  },
  "contact_info": {
    "email": "jane.doe@example.com",
    "country_code": "+1",
    "phone": "5559876543",
    "password": "temporaryPassword123"
  },
  "address_info": {
    "address": "456 Oak Avenue",
    "area": "Midtown",
    "city": "Los Angeles",
    "state": "CA",
    "zip_code": "90210",
    "country": "USA"
  },
  "professional_info": {
    "education_qualification": "Master's in Kinesiology",
    "professional_experience": "8 years teaching martial arts, 5 years competitive fighting",
    "designation_id": "instructor",
    "certifications": ["Black Belt Taekwondo", "CPR Certified", "Youth Coaching Certificate"]
  },
  "areas_of_expertise": ["Taekwondo", "Kickboxing", "Competition Training"]
}
```

**Response (201 Created):**
```json
{
  "message": "Coach created successfully",
  "coach_id": "coach-uuid-here"
}
```

### GET /api/coaches
Retrieve coaches with filtering and pagination options.

**Authentication:** Required
**Permissions:** Super Admin, Coach Admin, Coach

**Query Parameters:**
- `skip` (optional, default: 0): Number of coaches to skip for pagination
- `limit` (optional, default: 50, max: 100): Number of coaches to return
- `active_only` (optional, default: true): Show only active coaches
- `area_of_expertise` (optional): Filter by specific area of expertise

**Example Request:**
```
GET /api/coaches?area_of_expertise=Karate&active_only=true&skip=0&limit=10
```

**Response (200 OK):**
```json
{
  "coaches": [
    {
      "id": "coach-uuid-1",
      "personal_info": {
        "first_name": "John",
        "last_name": "Smith",
        "gender": "Male",
        "date_of_birth": "1985-03-15"
      },
      "contact_info": {
        "email": "john.smith@example.com",
        "country_code": "+1",
        "phone": "5551234567"
      },
      "address_info": {
        "address": "123 Main Street",
        "area": "Downtown",
        "city": "New York",
        "state": "NY",
        "zip_code": "10001",
        "country": "USA"
      },
      "professional_info": {
        "education_qualification": "Bachelor's in Sports Science",
        "professional_experience": "10 years martial arts instruction",
        "designation_id": "senior-instructor",
        "certifications": ["Black Belt Karate", "First Aid Certified"]
      },
      "areas_of_expertise": ["Karate", "Self-Defense", "Youth Training"],
      "full_name": "John Smith",
      "is_active": true,
      "created_at": "2024-01-20T10:30:00Z",
      "updated_at": "2024-01-20T10:30:00Z"
    }
  ]
}
```

### GET /api/coaches/{coach_id}
Retrieve a specific coach by ID.

**Authentication:** Required
**Permissions:** Super Admin, Coach Admin, Coach

**Path Parameters:**
- `coach_id`: UUID of the coach

**Response (200 OK):**
```json
{
  "coach": {
    "id": "coach-uuid-here",
    "personal_info": {
      "first_name": "John",
      "last_name": "Smith",
      "gender": "Male",
      "date_of_birth": "1985-03-15"
    },
    "contact_info": {
      "email": "john.smith@example.com",
      "country_code": "+1",
      "phone": "5551234567"
    },
    "address_info": {
      "address": "123 Main Street",
      "area": "Downtown",
      "city": "New York",
      "state": "NY",
      "zip_code": "10001",
      "country": "USA"
    },
    "professional_info": {
      "education_qualification": "Bachelor's in Sports Science",
      "professional_experience": "10 years martial arts instruction",
      "designation_id": "senior-instructor",
      "certifications": ["Black Belt Karate", "First Aid Certified"]
    },
    "areas_of_expertise": ["Karate", "Self-Defense", "Youth Training"],
    "full_name": "John Smith",
    "is_active": true,
    "created_at": "2024-01-20T10:30:00Z",
    "updated_at": "2024-01-20T10:30:00Z"
  }
}
```

### PUT /api/coaches/{coach_id}
Update an existing coach's information.

**Authentication:** Required
**Permissions:** Super Admin, Coach Admin

**Path Parameters:**
- `coach_id`: UUID of the coach to update

**Request Body (all fields optional):**
```json
{
  "personal_info": {
    "first_name": "John Updated",
    "last_name": "Smith"
  },
  "contact_info": {
    "phone": "5551234568"
  },
  "address_info": {
    "address": "789 New Street",
    "city": "Boston"
  },
  "professional_info": {
    "certifications": ["Black Belt Karate", "First Aid Certified", "Advanced Instructor Certificate"]
  },
  "areas_of_expertise": ["Karate", "Self-Defense", "Youth Training", "Competition Coaching"]
}
```

**Response (200 OK):**
```json
{
  "message": "Coach updated successfully",
  "coach": {
    "id": "coach-uuid-here",
    "full_name": "John Updated Smith",
    "updated_at": "2024-01-22T14:30:00Z"
  }
}
```

### DELETE /api/coaches/{coach_id}
Deactivate a coach (soft delete).

**Authentication:** Required
**Permissions:** Super Admin only

**Path Parameters:**
- `coach_id`: UUID of the coach to deactivate

**Response (200 OK):**
```json
{
  "message": "Coach deactivated successfully",
  "coach": {
    "id": "coach-uuid-here",
    "full_name": "John Smith",
    "is_active": false,
    "deactivated_at": "2024-01-22T15:00:00Z"
  }
}
```

### GET /api/coaches/stats/overview
Get coach statistics and analytics.

**Authentication:** Required
**Permissions:** Super Admin, Coach Admin

**Response (200 OK):**
```json
{
  "total_coaches": 25,
  "active_coaches": 23,
  "inactive_coaches": 2,
  "expertise_distribution": [
    {"_id": "Karate", "count": 8},
    {"_id": "Taekwondo", "count": 6},
    {"_id": "Kung Fu", "count": 5},
    {"_id": "Self-Defense", "count": 12},
    {"_id": "Youth Training", "count": 15},
    {"_id": "Competition Training", "count": 4}
  ]
}
```

---

## Data Models

### Coach Object Structure
```json
{
  "id": "string (UUID)",
  "personal_info": {
    "first_name": "string",
    "last_name": "string",
    "gender": "string (Male|Female|Other)",
    "date_of_birth": "string (YYYY-MM-DD)"
  },
  "contact_info": {
    "email": "string (email format)",
    "country_code": "string (+1, +44, etc.)",
    "phone": "string"
  },
  "address_info": {
    "address": "string",
    "area": "string",
    "city": "string",
    "state": "string",
    "zip_code": "string",
    "country": "string"
  },
  "professional_info": {
    "education_qualification": "string",
    "professional_experience": "string",
    "designation_id": "string",
    "certifications": ["string array"]
  },
  "areas_of_expertise": ["string array"],
  "full_name": "string (auto-generated)",
  "role": "string (always 'coach')",
  "is_active": "boolean",
  "created_at": "string (ISO 8601)",
  "updated_at": "string (ISO 8601)"
}
```

### Common Areas of Expertise
- Karate
- Taekwondo
- Kung Fu
- Jiu-Jitsu
- Kickboxing
- Self-Defense
- Youth Training
- Competition Training
- Weapons Training
- Meditation & Philosophy

### Designation IDs
- `"instructor"` - Basic instructor level
- `"senior-instructor"` - Senior instructor with advanced experience
- `"head-instructor"` - Department or branch head instructor
- `"master-instructor"` - Master level with extensive credentials

---

## Error Responses

### 400 Bad Request
```json
{
  "detail": "Coach with this email or phone already exists"
}
```

### 401 Unauthorized
```json
{
  "detail": "Invalid email or password"
}
```

### 403 Forbidden
```json
{
  "detail": "Insufficient permissions to access this resource"
}
```

### 404 Not Found
```json
{
  "detail": "Coach not found"
}
```

---

## Usage Examples

### Coach Login
```bash
curl -X POST "http://localhost:8003/api/coaches/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "coach@example.com",
    "password": "password123"
  }'
```

### Create New Coach (Super Admin)
```bash
curl -X POST "http://localhost:8003/api/coaches" \
  -H "Authorization: Bearer <super_admin_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "personal_info": {
      "first_name": "Mike",
      "last_name": "Johnson",
      "gender": "Male",
      "date_of_birth": "1988-12-10"
    },
    "contact_info": {
      "email": "mike.johnson@example.com",
      "country_code": "+1",
      "phone": "5555551234"
    },
    "areas_of_expertise": ["Jiu-Jitsu", "Self-Defense"]
  }'
```

### Get Coaches by Expertise
```bash
curl -X GET "http://localhost:8003/api/coaches?area_of_expertise=Karate&limit=20" \
  -H "Authorization: Bearer <token>"
```

### Update Coach Information
```bash
curl -X PUT "http://localhost:8003/api/coaches/coach-uuid-here" \
  -H "Authorization: Bearer <admin_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "professional_info": {
      "certifications": ["Black Belt Karate", "Master Instructor Certificate"]
    }
  }'
```

---

## Integration Notes

### Authentication Integration
- Coach login generates JWT tokens with "coach" role
- Tokens are valid for 24 hours by default
- Password reset functionality available through admin endpoints

### Course Integration
- Coaches can be assigned as instructors to courses
- `instructor_id` in courses references coach IDs
- Coach expertise areas should align with course categories

### Branch Integration
- Coaches can be assigned to specific branches
- Branch assignments affect coach permissions and access
- Multiple coaches can be assigned to the same branch

### User Management Integration
- Coaches are stored in a separate `coaches` collection
- Different from regular users in the `users` collection
- Unified authentication system supports both coach and user tokens

### Notification Integration
- SMS and WhatsApp notifications sent on coach creation
- Temporary passwords communicated securely
- Activity logging for all coach management operations

---

## Working Example - Complete Coach Management Flow

### Step 1: Get Superadmin Token
```bash
curl -X POST "http://localhost:8003/api/superadmin/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "superadmin@example.com",
    "password": "StrongPassword@123"
  }'
```

### Step 2: Retrieve All Coaches
```bash
curl -X GET "http://localhost:8003/api/coaches" \
  -H "Authorization: Bearer <token_from_step_1>"
```

### Step 3: Get Specific Coach
```bash
curl -X GET "http://localhost:8003/api/coaches/<coach_id>" \
  -H "Authorization: Bearer <token_from_step_1>"
```

### Step 4: Get Coach Statistics
```bash
curl -X GET "http://localhost:8003/api/coaches/stats/overview" \
  -H "Authorization: Bearer <token_from_step_1>"
```

### Step 5: Coach Login (Alternative Authentication)
```bash
curl -X POST "http://localhost:8003/api/coaches/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "coach@example.com",
    "password": "password123"
  }'
```

**Status:** ✅ All coach APIs are fully functional and tested (Updated: 2025-09-06)
