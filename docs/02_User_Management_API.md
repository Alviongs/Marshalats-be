# User Management API Documentation

## Overview
The User Management API provides comprehensive functionality for managing users across the Marshalats Learning Management System. It supports role-based access control and allows different user types to perform operations based on their permissions.

## Base URL
```
Development: http://localhost:8003/api/users
Production: https://edumanage-44.preview.dev.com/api/users
```

## Authentication
All endpoints require authentication via Bearer token in the Authorization header:
```
Authorization: Bearer <jwt_token>
```

## User Roles and Permissions

### Role Hierarchy
1. **super_admin** - Full system access, can manage all users across all branches
2. **coach_admin** - Branch-level management, can manage users within their assigned branch
3. **coach** - Limited access, can view students in their assigned branch
4. **student** - Personal account access only

---

## Endpoints

### POST /api/users
Create a new user in the system.

**Authentication:** Required
**Permissions:** Super Admin, Coach Admin

**Request Body:**
```json
{
  "full_name": "Jane Smith",
  "email": "jane.smith@example.com",
  "password": "securePassword123",
  "phone": "+1234567890",
  "role": "student",
  "branch_id": "branch-uuid-here",
  "date_of_birth": "1995-03-20",
  "address": {
    "line1": "789 Oak Avenue",
    "area": "Midtown",
    "city": "Los Angeles",
    "state": "CA",
    "pincode": "90210",
    "country": "USA"
  },
  "emergency_contact": {
    "name": "John Smith",
    "relationship": "Father",
    "phone": "+1234567891"
  }
}
```

**Role Restrictions:**
- **Coach Admin:** Can only create users for their own branch
- **Coach Admin:** Cannot create other admin roles (super_admin, coach_admin)

**Response (201 Created):**
```json
{
  "message": "User created successfully",
  "user": {
    "id": "user-uuid-here",
    "full_name": "Jane Smith",
    "email": "jane.smith@example.com",
    "role": "student",
    "branch_id": "branch-uuid-here",
    "phone": "+1234567890",
    "is_active": true,
    "created_at": "2024-01-20T10:30:00Z",
    "created_by": "admin-uuid-here"
  }
}
```

### GET /api/users
Retrieve users with filtering options.

**Authentication:** Required
**Permissions:** Super Admin, Coach Admin, Coach

**Query Parameters:**
- `role` (optional): Filter by user role (student, coach, coach_admin, super_admin)
- `branch_id` (optional): Filter by branch ID
- `skip` (optional, default: 0): Number of users to skip for pagination
- `limit` (optional, default: 50, max: 100): Number of users to return

**Access Control:**
- **Super Admin:** Can view ALL users across ALL branches
- **Coach Admin:** Can view users in THEIR assigned branch only
- **Coach:** Can view ONLY STUDENTS in their assigned branch

**Example Request:**
```
GET /api/users?role=student&branch_id=branch-123&skip=0&limit=20
```

**Response (200 OK):**
```json
{
  "users": [
    {
      "id": "user-uuid-1",
      "full_name": "Jane Smith",
      "email": "jane.smith@example.com",
      "role": "student",
      "branch_id": "branch-uuid-here",
      "phone": "+1234567890",
      "is_active": true,
      "created_at": "2024-01-20T10:30:00Z",
      "last_login": "2024-01-22T14:15:00Z"
    },
    {
      "id": "user-uuid-2",
      "full_name": "Bob Johnson",
      "email": "bob.johnson@example.com",
      "role": "student",
      "branch_id": "branch-uuid-here",
      "phone": "+1234567892",
      "is_active": true,
      "created_at": "2024-01-21T09:15:00Z",
      "last_login": "2024-01-22T16:30:00Z"
    }
  ],
  "total": 2,
  "skip": 0,
  "limit": 20,
  "has_more": false
}
```

### PUT /api/users/{user_id}
Update an existing user's information.

**Authentication:** Required
**Permissions:** Super Admin, Coach Admin

**Path Parameters:**
- `user_id`: UUID of the user to update

**Request Body:**
```json
{
  "full_name": "Jane Updated Smith",
  "phone": "+1234567893",
  "address": {
    "line1": "456 New Street",
    "area": "Downtown",
    "city": "Los Angeles",
    "state": "CA",
    "pincode": "90211",
    "country": "USA"
  },
  "emergency_contact": {
    "name": "Mary Smith",
    "relationship": "Mother",
    "phone": "+1234567894"
  },
  "is_active": true
}
```

**Role Restrictions:**
- **Coach Admin:** Can only update users in their own branch
- **Coach Admin:** Cannot update admin roles

**Response (200 OK):**
```json
{
  "message": "User updated successfully",
  "user": {
    "id": "user-uuid-here",
    "full_name": "Jane Updated Smith",
    "email": "jane.smith@example.com",
    "role": "student",
    "branch_id": "branch-uuid-here",
    "phone": "+1234567893",
    "is_active": true,
    "updated_at": "2024-01-22T11:45:00Z",
    "updated_by": "admin-uuid-here"
  }
}
```

### POST /api/users/{user_id}/force-password-reset
Force a password reset for a specific user.

**Authentication:** Required
**Permissions:** Super Admin, Coach Admin

**Path Parameters:**
- `user_id`: UUID of the user

**Role Restrictions:**
- **Coach Admin:** Can only reset passwords for users in their own branch

**Response (200 OK):**
```json
{
  "message": "Password reset initiated successfully",
  "reset_token": "temp-reset-token-here",
  "expires_at": "2024-01-22T23:59:59Z"
}
```

### DELETE /api/users/{user_id}
Deactivate a user (soft delete).

**Authentication:** Required
**Permissions:** Super Admin only

**Path Parameters:**
- `user_id`: UUID of the user to deactivate

**Response (200 OK):**
```json
{
  "message": "User deactivated successfully",
  "user": {
    "id": "user-uuid-here",
    "full_name": "Jane Smith",
    "email": "jane.smith@example.com",
    "is_active": false,
    "deactivated_at": "2024-01-22T12:00:00Z",
    "deactivated_by": "admin-uuid-here"
  }
}
```

---

## Data Models

### User Object Structure
```json
{
  "id": "string (UUID)",
  "full_name": "string",
  "email": "string (email format)",
  "role": "string (student|coach|coach_admin|super_admin)",
  "branch_id": "string (UUID)",
  "phone": "string",
  "date_of_birth": "string (YYYY-MM-DD)",
  "address": {
    "line1": "string",
    "area": "string",
    "city": "string",
    "state": "string",
    "pincode": "string",
    "country": "string"
  },
  "emergency_contact": {
    "name": "string",
    "relationship": "string",
    "phone": "string"
  },
  "is_active": "boolean",
  "created_at": "string (ISO 8601)",
  "updated_at": "string (ISO 8601)",
  "last_login": "string (ISO 8601)",
  "created_by": "string (UUID)",
  "updated_by": "string (UUID)"
}
```

### Available User Roles
- `"student"` - End user with personal account access
- `"coach"` - Instructor with course-specific access
- `"coach_admin"` - Branch manager with branch-level permissions
- `"super_admin"` - System administrator with full access

---

## Error Responses

### 400 Bad Request
```json
{
  "detail": "Invalid request data",
  "errors": [
    {
      "field": "email",
      "message": "Email already exists"
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
  "detail": "Coach Admins can only create users for their own branch"
}
```

### 404 Not Found
```json
{
  "detail": "User not found"
}
```

### 422 Validation Error
```json
{
  "detail": [
    {
      "loc": ["body", "email"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

---

## Usage Examples

### Create a Student User (Coach Admin)
```bash
curl -X POST "http://localhost:8003/api/users" \
  -H "Authorization: Bearer <coach_admin_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "full_name": "New Student",
    "email": "student@example.com",
    "password": "password123",
    "role": "student",
    "branch_id": "branch-uuid-here",
    "phone": "+1234567890"
  }'
```

### Get All Students in Branch (Coach)
```bash
curl -X GET "http://localhost:8003/api/users?role=student&branch_id=branch-123" \
  -H "Authorization: Bearer <coach_token>"
```

### Update User Information (Super Admin)
```bash
curl -X PUT "http://localhost:8003/api/users/user-uuid-here" \
  -H "Authorization: Bearer <super_admin_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "full_name": "Updated Name",
    "phone": "+9876543210"
  }'
```

---

## Security Notes

- All user passwords are automatically hashed using bcrypt
- Email addresses must be unique across the system
- Soft delete is used for user deactivation (preserves data integrity)
- Role-based access control is strictly enforced
- All user operations are logged for audit purposes
- Personal data is protected according to privacy regulations
