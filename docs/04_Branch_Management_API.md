# Branch Management API Documentation

## Overview
The Branch Management API provides comprehensive functionality for managing martial arts school branches in the Marshalats Learning Management System. It supports complex nested data structures for branch information, operational details, assignments, and banking information.

## Base URL
```
Development: http://31.97.224.169:8003/api/branches
Production: https://edumanage-44.preview.dev.com/api/branches
```

## Authentication
All endpoints require authentication via Bearer token in the Authorization header:
```
Authorization: Bearer <jwt_token>
```

### Getting Authentication Token
To get a superadmin token for branch management:

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

### Branch Management Permissions
- **super_admin** - Full branch management access (create, read, update, delete)
- **coach_admin** - Can update their own branch, view all branches
- **coach** - Can view branches only
- **student** - Can view branches only

---

## Endpoints

### POST /api/branches
Create a new branch with comprehensive nested structure.

**Authentication:** Required
**Permissions:** Super Admin only

**Request Body:**
```json
{
  "branch": {
    "name": "Rock Martial Arts",
    "code": "RMA01",
    "email": "contact@rockmartialarts.com",
    "phone": "+1234567890",
    "address": {
      "line1": "123 Main Street",
      "area": "Downtown",
      "city": "New York",
      "state": "NY",
      "pincode": "10001",
      "country": "USA"
    }
  },
  "manager_id": "manager-uuid-here",
  "operational_details": {
    "courses_offered": ["Karate", "Kung Fu", "Taekwondo"],
    "timings": [
      {"day": "Monday", "open": "07:00", "close": "19:00"},
      {"day": "Tuesday", "open": "07:00", "close": "19:00"},
      {"day": "Wednesday", "open": "07:00", "close": "19:00"},
      {"day": "Thursday", "open": "07:00", "close": "19:00"},
      {"day": "Friday", "open": "07:00", "close": "19:00"},
      {"day": "Saturday", "open": "08:00", "close": "16:00"}
    ],
    "holidays": ["2024-12-25", "2024-01-01", "2024-07-04"]
  },
  "assignments": {
    "accessories_available": true,
    "courses": ["course-uuid-1", "course-uuid-2", "course-uuid-3"],
    "branch_admins": ["admin-uuid-1", "admin-uuid-2"]
  },
  "bank_details": {
    "bank_name": "First National Bank",
    "account_number": "1234567890",
    "upi_id": "rockmartialarts@bank"
  }
}
```

**Response (201 Created):**
```json
{
  "message": "Branch created successfully",
  "branch_id": "branch-uuid-here"
}
```

### GET /api/branches
Retrieve all active branches with pagination.

**Authentication:** Required
**Permissions:** All authenticated users

**Query Parameters:**
- `skip` (optional, default: 0): Number of branches to skip for pagination
- `limit` (optional, default: 50, max: 100): Number of branches to return

**Example Request:**
```
GET /api/branches?skip=0&limit=10
```

**Response (200 OK):**
```json
{
  "branches": [
    {
      "id": "branch-uuid-here",
      "branch": {
        "name": "Rock Martial Arts",
        "code": "RMA01",
        "email": "contact@rockmartialarts.com",
        "phone": "+1234567890",
        "address": {
          "line1": "123 Main Street",
          "area": "Downtown",
          "city": "New York",
          "state": "NY",
          "pincode": "10001",
          "country": "USA"
        }
      },
      "manager_id": "manager-uuid-here",
      "operational_details": {
        "courses_offered": ["Karate", "Kung Fu", "Taekwondo"],
        "timings": [
          {"day": "Monday", "open": "07:00", "close": "19:00"},
          {"day": "Tuesday", "open": "07:00", "close": "19:00"}
        ],
        "holidays": ["2024-12-25", "2024-01-01"]
      },
      "assignments": {
        "accessories_available": true,
        "courses": ["course-uuid-1", "course-uuid-2"],
        "branch_admins": ["admin-uuid-1"]
      },
      "bank_details": {
        "bank_name": "First National Bank",
        "account_number": "1234567890",
        "upi_id": "rockmartialarts@bank"
      },
      "is_active": true,
      "created_at": "2024-01-20T10:30:00Z",
      "updated_at": "2024-01-20T10:30:00Z"
    }
  ]
}
```

### GET /api/branches/{branch_id}
Retrieve a specific branch by ID with complete nested structure.

**Authentication:** Required
**Permissions:** All authenticated users

**Path Parameters:**
- `branch_id`: UUID of the branch

**Response (200 OK):**
```json
{
  "id": "branch-uuid-here",
  "branch": {
    "name": "Rock Martial Arts",
    "code": "RMA01",
    "email": "contact@rockmartialarts.com",
    "phone": "+1234567890",
    "address": {
      "line1": "123 Main Street",
      "area": "Downtown",
      "city": "New York",
      "state": "NY",
      "pincode": "10001",
      "country": "USA"
    }
  },
  "manager_id": "manager-uuid-here",
  "operational_details": {
    "courses_offered": ["Karate", "Kung Fu", "Taekwondo"],
    "timings": [
      {"day": "Monday", "open": "07:00", "close": "19:00"},
      {"day": "Tuesday", "open": "07:00", "close": "19:00"},
      {"day": "Wednesday", "open": "07:00", "close": "19:00"},
      {"day": "Thursday", "open": "07:00", "close": "19:00"},
      {"day": "Friday", "open": "07:00", "close": "19:00"},
      {"day": "Saturday", "open": "08:00", "close": "16:00"}
    ],
    "holidays": ["2024-12-25", "2024-01-01", "2024-07-04"]
  },
  "assignments": {
    "accessories_available": true,
    "courses": ["course-uuid-1", "course-uuid-2", "course-uuid-3"],
    "branch_admins": ["admin-uuid-1", "admin-uuid-2"]
  },
  "bank_details": {
    "bank_name": "First National Bank",
    "account_number": "1234567890",
    "upi_id": "rockmartialarts@bank"
  },
  "is_active": true,
  "created_at": "2024-01-20T10:30:00Z",
  "updated_at": "2024-01-20T10:30:00Z"
}
```

### PUT /api/branches/{branch_id}
Update an existing branch with nested structure.

**Authentication:** Required
**Permissions:** Super Admin, Coach Admin (own branch only)

**Path Parameters:**
- `branch_id`: UUID of the branch to update

**Role Restrictions:**
- **Coach Admin:** Can only update branches where they are listed in `assignments.branch_admins`
- **Coach Admin:** Cannot update `manager_id`, `is_active`, `assignments`, or `bank_details`

**Request Body (all fields optional):**
```json
{
  "branch": {
    "name": "Updated Rock Martial Arts",
    "email": "updated@rockmartialarts.com",
    "phone": "+1234567891",
    "address": {
      "line1": "456 New Street",
      "area": "Uptown",
      "city": "New York",
      "state": "NY",
      "pincode": "10002",
      "country": "USA"
    }
  },
  "operational_details": {
    "courses_offered": ["Karate", "Kung Fu", "Taekwondo", "Jiu-Jitsu"],
    "timings": [
      {"day": "Monday", "open": "06:00", "close": "20:00"},
      {"day": "Tuesday", "open": "06:00", "close": "20:00"}
    ],
    "holidays": ["2024-12-25", "2024-01-01", "2024-07-04", "2024-11-28"]
  }
}
```

**Response (200 OK):**
```json
{
  "message": "Branch updated successfully",
  "branch": {
    "id": "branch-uuid-here",
    "branch": {
      "name": "Updated Rock Martial Arts",
      "code": "RMA01"
    },
    "updated_at": "2024-01-22T14:30:00Z"
  }
}
```

### POST /api/branches/{branch_id}/holidays
Create a holiday for a specific branch.

**Authentication:** Required
**Permissions:** Super Admin, Coach Admin

**Path Parameters:**
- `branch_id`: UUID of the branch

**Request Body:**
```json
{
  "name": "Independence Day",
  "date": "2024-07-04",
  "description": "National holiday - branch closed"
}
```

**Response (201 Created):**
```json
{
  "id": "holiday-uuid-here",
  "branch_id": "branch-uuid-here",
  "name": "Independence Day",
  "date": "2024-07-04",
  "description": "National holiday - branch closed",
  "created_at": "2024-01-20T10:30:00Z"
}
```

### GET /api/branches/{branch_id}/holidays
Retrieve all holidays for a specific branch.

**Authentication:** Required
**Permissions:** All authenticated users

**Path Parameters:**
- `branch_id`: UUID of the branch

**Response (200 OK):**
```json
{
  "holidays": [
    {
      "id": "holiday-uuid-1",
      "branch_id": "branch-uuid-here",
      "name": "Christmas Day",
      "date": "2024-12-25",
      "description": "Christmas holiday - branch closed",
      "created_at": "2024-01-20T10:30:00Z"
    },
    {
      "id": "holiday-uuid-2",
      "branch_id": "branch-uuid-here",
      "name": "New Year's Day",
      "date": "2024-01-01",
      "description": "New Year holiday - branch closed",
      "created_at": "2024-01-20T10:30:00Z"
    }
  ]
}
```

---

## Data Models

### Branch Object Structure
```json
{
  "id": "string (UUID)",
  "branch": {
    "name": "string",
    "code": "string (unique branch code)",
    "email": "string (email format)",
    "phone": "string",
    "address": {
      "line1": "string",
      "area": "string",
      "city": "string",
      "state": "string",
      "pincode": "string",
      "country": "string"
    }
  },
  "manager_id": "string (UUID)",
  "operational_details": {
    "courses_offered": ["string array"],
    "timings": [
      {
        "day": "string (Monday-Sunday)",
        "open": "string (HH:MM format)",
        "close": "string (HH:MM format)"
      }
    ],
    "holidays": ["string array (YYYY-MM-DD format)"]
  },
  "assignments": {
    "accessories_available": "boolean",
    "courses": ["string array (course UUIDs)"],
    "branch_admins": ["string array (user UUIDs)"]
  },
  "bank_details": {
    "bank_name": "string",
    "account_number": "string",
    "upi_id": "string"
  },
  "is_active": "boolean",
  "created_at": "string (ISO 8601)",
  "updated_at": "string (ISO 8601)"
}
```

### Holiday Object Structure
```json
{
  "id": "string (UUID)",
  "branch_id": "string (UUID)",
  "name": "string",
  "date": "string (YYYY-MM-DD format)",
  "description": "string (optional)",
  "created_at": "string (ISO 8601)"
}
```

---

## Error Responses

### 400 Bad Request
```json
{
  "detail": "Invalid branch data",
  "errors": [
    {
      "field": "branch.code",
      "message": "Branch code already exists"
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
  "detail": "Coach Admins can only update branches where they are listed as branch admins"
}
```

### 404 Not Found
```json
{
  "detail": "Branch not found"
}
```

---

## Usage Examples

### Create a New Branch (Super Admin)
```bash
curl -X POST "http://31.97.224.169:8003/api/branches" \
  -H "Authorization: Bearer <super_admin_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "branch": {
      "name": "Downtown Dojo",
      "code": "DD01",
      "email": "info@downtowndojo.com",
      "phone": "+1555123456",
      "address": {
        "line1": "789 Center St",
        "area": "Business District",
        "city": "Chicago",
        "state": "IL",
        "pincode": "60601",
        "country": "USA"
      }
    },
    "manager_id": "manager-uuid-here",
    "operational_details": {
      "courses_offered": ["Karate", "Judo"],
      "timings": [
        {"day": "Monday", "open": "09:00", "close": "21:00"}
      ],
      "holidays": ["2024-12-25"]
    },
    "assignments": {
      "accessories_available": true,
      "courses": ["course-uuid-1"],
      "branch_admins": ["admin-uuid-1"]
    },
    "bank_details": {
      "bank_name": "Chicago Bank",
      "account_number": "9876543210",
      "upi_id": "downtowndojo@bank"
    }
  }'
```

### Get All Branches
```bash
curl -X GET "http://31.97.224.169:8003/api/branches?skip=0&limit=20" \
  -H "Authorization: Bearer <token>"
```

### Update Branch Information (Coach Admin)
```bash
curl -X PUT "http://31.97.224.169:8003/api/branches/branch-uuid-here" \
  -H "Authorization: Bearer <coach_admin_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "branch": {
      "phone": "+1555123457"
    },
    "operational_details": {
      "timings": [
        {"day": "Monday", "open": "08:00", "close": "22:00"}
      ]
    }
  }'
```

### Add Holiday to Branch
```bash
curl -X POST "http://31.97.224.169:8003/api/branches/branch-uuid-here/holidays" \
  -H "Authorization: Bearer <admin_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Labor Day",
    "date": "2024-09-02",
    "description": "Labor Day holiday - branch closed"
  }'
```

---

## Integration Notes

### User Integration
- `manager_id` references a user with "coach_admin" or "super_admin" role
- `assignments.branch_admins` contains user IDs with administrative privileges
- Branch assignments affect user permissions and access control

### Course Integration
- `assignments.courses` contains course IDs available at this branch
- Course enrollment is restricted to assigned branches
- Branch-specific pricing can be configured per course

### Operational Management
- `operational_details.timings` defines branch operating hours
- `operational_details.holidays` lists branch closure dates
- Holiday management supports recurring and one-time closures

### Financial Integration
- `bank_details` supports payment processing and financial reporting
- UPI integration for digital payments
- Branch-specific financial tracking and reporting

---

## Working Example - Complete Branch Management Flow

### Step 1: Get Superadmin Token
```bash
curl -X POST "http://31.97.224.169:8003/api/superadmin/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "superadmin@example.com",
    "password": "StrongPassword@123"
  }'
```

### Step 2: Create a Branch
```bash
curl -X POST "http://31.97.224.169:8003/api/branches" \
  -H "Authorization: Bearer <token_from_step_1>" \
  -H "Content-Type: application/json" \
  -d '{
    "branch": {
      "name": "Downtown Martial Arts Center",
      "code": "DMAC-001",
      "email": "downtown@martialarts.com",
      "phone": "+1-555-0123",
      "address": {
        "line1": "123 Main Street",
        "area": "Downtown District",
        "city": "Downtown",
        "state": "CA",
        "pincode": "90210",
        "country": "USA"
      }
    },
    "manager_id": "manager-uuid-12345",
    "operational_details": {
      "courses_offered": ["Kung Fu", "Karate", "Taekwondo"],
      "timings": [
        {"day": "Monday", "open": "06:00", "close": "22:00"},
        {"day": "Tuesday", "open": "06:00", "close": "22:00"}
      ],
      "holidays": ["2025-01-01", "2025-12-25"]
    },
    "assignments": {
      "accessories_available": true,
      "courses": ["course-uuid-1", "course-uuid-2"],
      "branch_admins": ["admin-uuid-1"]
    },
    "bank_details": {
      "bank_name": "First National Bank",
      "account_number": "1234567890",
      "upi_id": "downtown@paytm"
    }
  }'
```

### Step 3: Retrieve All Branches
```bash
curl -X GET "http://31.97.224.169:8003/api/branches" \
  -H "Authorization: Bearer <token_from_step_1>"
```

### Step 4: Get Specific Branch
```bash
curl -X GET "http://31.97.224.169:8003/api/branches/<branch_id_from_step_2>" \
  -H "Authorization: Bearer <token_from_step_1>"
```

### Step 5: Create Holiday for Branch
```bash
curl -X POST "http://31.97.224.169:8003/api/branches/<branch_id>/holidays" \
  -H "Authorization: Bearer <token_from_step_1>" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "New Year Day",
    "date": "2025-01-01",
    "description": "Branch closed for New Year celebration",
    "is_recurring": true
  }'
```

**Status:** ✅ All branch APIs are fully functional and tested (Updated: 2025-09-06)
