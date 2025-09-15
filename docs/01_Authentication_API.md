# Authentication API Documentation

## Overview
The Marshalats Learning Management System provides multiple authentication systems to support different user types and access patterns. The system uses JWT (JSON Web Tokens) for secure authentication and role-based access control.

## Base URL
```
Development: http://localhost:8003/api
Production: https://edumanage-44.preview.dev.com/api
```

## Authentication Systems

### 1. Regular User Authentication (`/api/auth/`)
For students, coaches, coach admins, and regular super admins.

### 2. Superadmin Authentication (`/api/superadmin/`)
Dedicated system for superadmin operations with enhanced privileges.

## Authentication Header Format
All authenticated requests require the following header:
```
Authorization: Bearer <jwt_token>
```

---

## Regular User Authentication Endpoints

### POST /api/auth/register
Register a new user in the system.

**Request Body:**
```json
{
  "full_name": "John Doe",
  "email": "john.doe@example.com",
  "password": "securePassword123",
  "phone": "+1234567890",
  "role": "student",
  "branch_id": "branch-uuid-here",
  "date_of_birth": "1990-01-15",
  "address": {
    "line1": "123 Main Street",
    "area": "Downtown",
    "city": "New York",
    "state": "NY",
    "pincode": "10001",
    "country": "USA"
  }
}
```

**Available Roles:**
- `"student"` - End user with personal account access
- `"coach"` - Instructor with course-specific access
- `"coach_admin"` - Branch manager with branch-level permissions
- `"super_admin"` - System administrator with full access

**Response (201 Created):**
```json
{
  "message": "User registered successfully",
  "user": {
    "id": "user-uuid-here",
    "full_name": "John Doe",
    "email": "john.doe@example.com",
    "role": "student",
    "branch_id": "branch-uuid-here",
    "is_active": true,
    "created_at": "2024-01-15T10:30:00Z"
  }
}
```

### POST /api/auth/login
Authenticate user and receive JWT token.

**Request Body:**
```json
{
  "email": "john.doe@example.com",
  "password": "securePassword123"
}
```

**Response (200 OK):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 86400,
  "user": {
    "id": "user-uuid-here",
    "full_name": "John Doe",
    "email": "john.doe@example.com",
    "role": "student",
d    "branch_id": "branch-uuid-here",
    "is_active": true
  }
}
```

### POST /api/auth/forgot-password
Initiate password reset process.

**Request Body:**
```json
{
  "email": "john.doe@example.com"
}
```

**Response (200 OK):**
```json
{
  "message": "Password reset instructions sent to email"
}
```

### POST /api/auth/reset-password
Reset password using reset token.

**Request Body:**
```json
{
  "token": "reset-token-here",
  "new_password": "newSecurePassword123"
}
```

**Response (200 OK):**
```json
{
  "message": "Password reset successfully"
}
```

### GET /api/auth/me
Get current authenticated user information.

**Authentication:** Required (Bearer token)

**Response (200 OK):**
```json
{
  "id": "user-uuid-here",
  "full_name": "John Doe",
  "email": "john.doe@example.com",
  "role": "student",
  "branch_id": "branch-uuid-here",
  "phone": "+1234567890",
  "is_active": true,
  "created_at": "2024-01-15T10:30:00Z",
  "last_login": "2024-01-20T14:30:00Z"
}
```

### PUT /api/auth/profile
Update current user's profile information.

**Authentication:** Required (Bearer token)

**Request Body:**
```json
{
  "full_name": "John Updated Doe",
  "phone": "+1234567891",
  "address": {
    "line1": "456 New Street",
    "area": "Uptown",
    "city": "New York",
    "state": "NY",
    "pincode": "10002",
    "country": "USA"
  }
}
```

**Response (200 OK):**
```json
{
  "message": "Profile updated successfully",
  "user": {
    "id": "user-uuid-here",
    "full_name": "John Updated Doe",
    "email": "john.doe@example.com",
    "phone": "+1234567891",
    "role": "student",
    "updated_at": "2024-01-20T15:00:00Z"
  }
}
```

---

## Superadmin Authentication Endpoints

### POST /api/superadmin/register
Register a new superadmin (first-time setup).

**Request Body:**
```json
{
  "full_name": "Super Admin",
  "email": "admin@example.com",
  "password": "superSecurePassword123"
}
```

**Response (201 Created):**
```json
{
  "message": "Super admin registered successfully",
  "admin": {
    "id": "admin-uuid-here",
    "full_name": "Super Admin",
    "email": "admin@example.com",
    "created_at": "2024-01-15T10:30:00Z"
  }
}
```

### POST /api/superadmin/login
Authenticate superadmin and receive JWT token.

**Request Body:**
```json
{
  "email": "admin@example.com",
  "password": "superSecurePassword123"
}
```

**Response (200 OK):**
```json
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 86400,
  "admin": {
    "id": "admin-uuid-here",
_name": "Super Admin",
    "email": "admin@example.com",
    "role": "superadmin"
  }
}
```

### GET /api/superadmin/me
Get current superadmin profile information.

**Authentication:** Required (Superadmin Bearer token)

**Response (200 OK):**
```json
{
  "status": "success",
  "data": {
    "id": "admin-uuid-here",
    "full_name": "Super Admin",
    ""admin@example.com",
    "created_at": "2024-01-15T10:30:00Z"
  }
}
```

### GET /api/superadmin/verify-token
Verify if superadmin token is valid.

**Authentication:** Required (Superadmin Bearer token)

**Response (200 OK):**
```json
{
  "status": "success",
  "message": "Token is valid",
  "data": {
    "id": "admin-uuid-here",
    "email": "admin@example.com",
    "full_name": "Super Admin"
  }
}
```

---

## Error Responses

### 400 Bad Request
```json
{
  "detail": "Invalid request data",
  "errors": [
    {
      "field": "email",
      "message": "Invalid email format"
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
  "detail": "Insufficient permissions"
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

## Token Information

### Token Expiration
- **Regular User Tokens:** 24 hours (1440 minutes)
- **Superadmin Tokens:** 24 hours (1440 minutes)

### Token Payload Structure
Regular user token payload:
```json
{
  "sub": "user-uuid-here",
  "role": "student",
  "branch_id": "branch-uuid-here",
  "exp": 1705834800
}
```

Superadmin token payload:
```json
{
  "sub": "admin-uuid-here",
  "role": "superadmin",
  "exp": 1705834800
}
```

### Security Notes
- All passwords are hashed using bcrypt
- JWT tokens are signed with HS256 algorithm
- Tokens include expiration time for security
- Failed login attempts should be monitored
- Use HTTPS in production environments
