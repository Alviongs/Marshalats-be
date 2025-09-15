# Student Management System API Documentation

## Overview
This is a comprehensive Student Management System API built with FastAPI, supporting role-based access for Super Admin, Staff (Coach Admin), Coaches, and Students. The API features nested data structures, comprehensive branch management, and JWT-based authentication.

## Base URL
```
Production: https://edumanage-44.preview.dev.com/api
Development: http://localhost:8003/api
```

## HTTP Status Codes
The API uses standard HTTP status codes to indicate success or failure:

### Success Codes
- **200 OK**: Request successful, data returned
- **201 Created**: Resource created successfully
- **204 No Content**: Request successful, no content to return

### Client Error Codes
- **400 Bad Request**: Invalid request data or validation errors
- **401 Unauthorized**: Authentication required or invalid credentials
- **403 Forbidden**: Valid authentication but insufficient permissions
- **404 Not Found**: Requested resource not found
- **409 Conflict**: Resource already exists (e.g., duplicate email)
- **422 Unprocessable Entity**: Request data validation failed
- **429 Too Many Requests**: Rate limit exceeded

### Server Error Codes
- **500 Internal Server Error**: Server-side error occurred
- **503 Service Unavailable**: Server temporarily unavailable

## Response Format
All API responses follow a consistent JSON structure:

### Success Response Format
```json
{
  "message": "Operation completed successfully",
  "data": {
    // Actual response data
  },
  "timestamp": "2025-01-07T12:00:00Z"
}
```

### Error Response Format
```json
{
  "detail": "Error description",
  "error_code": "VALIDATION_ERROR",
  "timestamp": "2025-01-07T12:00:00Z",
  "path": "/api/coaches",
  "method": "POST"
}
```

### Validation Error Format (422)
```json
{
  "detail": [
    {
      "type": "missing",
      "loc": ["body", "field_name"],
      "msg": "Field required",
      "input": {}
    }
  ]
}
```

## Authentication
The API uses JWT (JSON Web Token) for authentication with **two separate authentication systems**:

### 1. Super Admin Authentication System
- **Endpoint Prefix**: `/api/superadmin/`
- **Purpose**: Dedicated auth system for super admin management
- **Token Duration**: 24 hours
- **Access**: Super admin registration, login, profile management
- **Isolation**: Completely separate from regular user authentication

### 2. Regular User Authentication System  
- **Endpoint Prefix**: `/api/auth/`
- **Purpose**: Authentication for students, coaches, coach admins, and regular super admins
- **Token Duration**: Variable (configured in system)
- **Access**: User registration, login, profile management, role-based operations
- **Roles**: `student`, `coach`, `coach_admin`, `super_admin`

### Authentication Header Format
Both systems use the same header format:
```
Authorization: Bearer <your_jwt_token>
```

### Getting Authentication Tokens

#### For Super Admin Operations:
1. **Register**: POST `/api/superadmin/register` (first time setup)
2. **Login**: POST `/api/superadmin/login` with email and password
3. **Extract Token**: Copy the `token` from the response
4. **Use Token**: Include in Authorization header for super admin operations

#### For Coach Operations:
1. **Login**: POST `/api/coaches/login` with email and password
2. **Extract Token**: Copy the `access_token` from the response
3. **Use Token**: Include in Authorization header for coach operations
4. **Access**: Can view own profile, limited permissions

#### For Regular User Operations:
1. **Login**: POST `/api/auth/login` with email and password
2. **Extract Token**: Copy the `access_token` from the response  
3. **Use Token**: Include in Authorization header for user operations

### Authentication Header Format
```
Authorization: Bearer <your_jwt_token>
```

## Quick Start Guide

### 1. Testing Coach Creation (Complete Example)

**Step 1: Start the server**
```bash
cd /path/to/backend
python server.py
```

**Step 2: Test Coach Creation (Without Auth - Will Fail)**
```bash
curl -X POST "http://localhost:8003/api/coaches" \
  -H "Content-Type: application/json" \
  -d '{
    "personal_info": {
      "first_name": "Test",
      "last_name": "Coach",
      "gender": "Male",
      "date_of_birth": "1990-01-01"
    },
    "contact_info": {
      "email": "testcoach@example.com",
      "country_code": "+91",
      "phone": "9876543210",
      "password": "TestPassword123!"
    },
    "address_info": {
      "address": "123 Test Street",
      "area": "Test Area",
      "city": "Test City",
      "state": "Test State",
      "zip_code": "123456",
      "country": "India"
    },
    "professional_info": {
      "education_qualification": "Bachelor's Degree",
      "professional_experience": "3+ years",
      "designation_id": "test-designation-001",
      "certifications": ["Test Certification"]
    },
    "areas_of_expertise": ["Karate", "Self Defense"]
  }'
```

**Expected Response (401 Unauthorized)**:
```json
{
  "detail": "Could not validate credentials"
}
```

**Step 3: Get Authentication Token (Login with existing user)**
```bash
curl -X POST "http://localhost:8003/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@example.com",
    "password": "your_password"
  }'
```

**Step 4: Use Token for Coach Creation**
```bash
# Replace YOUR_TOKEN_HERE with actual token from login response
curl -X POST "http://localhost:8003/api/coaches" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{
    "personal_info": {
      "first_name": "Test",
      "last_name": "Coach",
      "gender": "Male", 
      "date_of_birth": "1990-01-01"
    },
    "contact_info": {
      "email": "testcoach@example.com",
      "country_code": "+91",
      "phone": "9876543210",
      "password": "TestPassword123!"
    },
    "address_info": {
      "address": "123 Test Street",
      "area": "Test Area",
      "city": "Test City",
      "state": "Test State",
      "zip_code": "123456",
      "country": "India"
    },
    "professional_info": {
      "education_qualification": "Bachelor's Degree",
      "professional_experience": "3+ years",
      "designation_id": "test-designation-001",
      "certifications": ["Test Certification"]
    },
    "areas_of_expertise": ["Karate", "Self Defense"]
  }'
```

### 2. API Documentation Access
```bash
# Interactive API Documentation (Swagger UI)
http://localhost:8003/docs

# Alternative API Documentation (ReDoc)
http://localhost:8003/redoc

# OpenAPI JSON Schema
http://localhost:8003/openapi.json
```

### 3. Common Test Commands

**Coach Login**:
```bash
curl -X POST "http://localhost:8003/api/coaches/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "coach@example.com",
    "password": "CoachPassword123!"
  }'
```

**Get Coach Profile** (after login):
```bash
curl -X GET "http://localhost:8003/api/coaches/me" \
  -H "Authorization: Bearer COACH_TOKEN_HERE"
```

**Get All Coaches** (Admin only):
```bash
curl -X GET "http://localhost:8003/api/coaches" \
  -H "Authorization: Bearer ADMIN_TOKEN_HERE"
```

**Get Coach Statistics** (Admin only):
```bash
curl -X GET "http://localhost:8003/api/coaches/stats/overview" \
  -H "Authorization: Bearer ADMIN_TOKEN_HERE"
```

**Update Coach** (Admin only):
```bash
curl -X PUT "http://localhost:8003/api/coaches/COACH_ID_HERE" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{
    "personal_info": {
      "first_name": "Updated Name"
    }
  }'
```

## API Features

### Rate Limiting
- **Login Endpoints**: 5 attempts per minute per IP
- **Registration Endpoints**: 3 attempts per minute per IP  
- **General API Endpoints**: 100 requests per minute per authenticated user
- **Public Endpoints**: 50 requests per minute per IP

### Pagination
Most list endpoints support pagination:
- **Query Parameters**: `skip` (offset), `limit` (page size)
- **Default Limit**: 50 items
- **Maximum Limit**: 100 items
- **Response Fields**: `total`, `page`, `limit`, `has_next`, `has_previous`

### Filtering
Many endpoints support filtering:
- **Example**: `/api/coaches?active_only=true&area_of_expertise=Karate`
- **Boolean Filters**: `active_only`, `is_verified`
- **Text Filters**: `search`, `area_of_expertise`
- **Date Filters**: `created_after`, `created_before`

### CORS Support
- **Enabled**: For all origins in development
- **Production**: Configured for specific domains
- **Methods**: GET, POST, PUT, DELETE, OPTIONS
- **Headers**: Authorization, Content-Type, Accept

### Data Validation
- **Pydantic Models**: All request/response data validated
- **Email Validation**: RFC compliant email addresses
- **Phone Validation**: International phone number format
- **Date Validation**: ISO 8601 date format (YYYY-MM-DD)
- **Password Validation**: Minimum complexity requirements

### Database
- **MongoDB**: Document-based storage
- **Collections**: Separate collections for users, coaches, branches, courses
- **Indexing**: Optimized queries with proper indexing
- **Relationships**: Embedded documents and references

## Common Error Scenarios

### Authentication Errors
```bash
# Missing token
curl -X GET "http://localhost:8003/api/coaches"
# Response: 401 {"detail": "Not authenticated"}

# Invalid token
curl -X GET "http://localhost:8003/api/coaches" \
  -H "Authorization: Bearer invalid_token"
# Response: 401 {"detail": "Could not validate credentials"}

# Expired token
curl -X GET "http://localhost:8003/api/coaches" \
  -H "Authorization: Bearer expired_token"
# Response: 401 {"detail": "Token has expired"}
```

### Validation Errors
```bash
# Missing required fields
curl -X POST "http://localhost:8003/api/coaches" \
  -H "Authorization: Bearer valid_token" \
  -H "Content-Type: application/json" \
  -d '{}'
# Response: 422 with detailed validation errors

# Invalid email format
curl -X POST "http://localhost:8003/api/coaches" \
  -H "Authorization: Bearer valid_token" \
  -H "Content-Type: application/json" \
  -d '{"contact_info": {"email": "invalid-email"}}'
# Response: 422 {"detail": [{"loc": ["contact_info", "email"], "msg": "value is not a valid email address"}]}
```

### Permission Errors
```bash
# Insufficient permissions (non-admin trying to create coach)
curl -X POST "http://localhost:8003/api/coaches" \
  -H "Authorization: Bearer student_token" \
  -H "Content-Type: application/json" \
  -d '{...}'
# Response: 403 {"detail": "Not enough permissions to access this resource"}
```

### Example Authentication Flow
```bash
# Step 1: Login to get token
curl -X POST http://localhost:8003/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "password123"}'

# Step 2: Use token in protected requests
curl -X GET http://localhost:8003/api/auth/me \
  -H "Authorization: Bearer your_token_here" \
  -H "Content-Type: application/json"
```

### Postman Setup
1. Login request → Tests tab → Add: `pm.globals.set("token", pm.response.json().access_token);`
2. Use `{{token}}` in Authorization header: `Bearer {{token}}`

## Error Responses
All endpoints may return the following error formats:

**400 Bad Request**:
```json
{
  "detail": "Error message describing what went wrong"
}
```

**401 Unauthorized**:
```json
{
  "detail": "Invalid authentication credentials"
}
```

**403 Forbidden**:
```json
{
  "detail": "Insufficient permissions"
}
```

**404 Not Found**:
```json
{
  "detail": "Resource not found"
}
```

**422 Validation Error**:
```json
{
  "detail": [
    {
      "loc": ["field_name"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

**500 Internal Server Error**:
```json
{
  "detail": "Internal server error"
}
```

## User Roles & Permissions
- **super_admin**: Full system access, manages branches, courses, users, and system settings
- **coach_admin**: Branch-level management, student enrollment, course scheduling, branch operations
- **coach**: Limited access to assigned courses and students, attendance tracking
- **student**: Personal profile, course enrollment, attendance viewing, payment history

## Available User Role Values
When creating or updating users, use these exact role values:
- `"super_admin"` - System administrator with full access
- `"coach_admin"` - Branch manager with branch-level permissions  
- `"coach"` - Instructor with course-specific access
- `"student"` - End user with personal account access

## Data Structure Overview
The API uses nested JSON structures for complex entities:
- **Users**: Include nested `course` and `branch` objects
- **Branches**: Comprehensive nested structure with address, operational details, assignments, and bank details
- **Consistent Storage**: Data is stored and returned in the same nested format

## Testing & Development Tools

### Available Test Scripts
- `test_auth_bearer.py` - Comprehensive authentication testing
- `simple_auth_test.py` - Step-by-step authentication guide
- `Student_Management_API_Bearer_Auth.postman_collection.json` - Postman collection

### Quick Test Commands
```bash
# Test authentication
python test_auth_bearer.py

# Show step-by-step auth flow
python simple_auth_test.py

# Test specific endpoints
curl -X POST http://localhost:8003/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "superadmin@test.com", "password": "SuperAdmin123!"}'
```

### Demo Users
- **Super Admin**: `superadmin@test.com` / `SuperAdmin123!`
- **Student**: Available after registration

---

# API Endpoints

## 0. Super Admin Authentication

### POST /api/superadmin/register
**Description**: Register a new super admin (isolated auth system for super admin management)

**Access**: Public (no authentication required)

**Request Body**:
```json
{
  "full_name": "John Doe",
  "email": "superadmin@example.com",
  "password": "StrongPassword@123",
  "phone": "+919876543210"
}
```

**Required Fields**: `full_name`, `email`, `password`, `phone`

**Field Specifications**:
- `full_name`: Complete name of the super admin
- `email`: Must be a valid email address (unique)
- `password`: Strong password (recommend 8+ characters with special characters)
- `phone`: Contact phone number with country code

**Response**:
```json
{
  "status": "success",
  "message": "Super admin registered successfully",
  "data": {
    "id": "superadmin-uuid-1234",
    "full_name": "John Doe",
    "email": "superadmin@example.com",
    "phone": "+919876543210",
    "is_active": true,
    "created_at": "2025-09-05T12:00:00Z",
    "updated_at": "2025-09-05T12:00:00Z"
  }
}
```

**cURL Example**:
```bash
curl -X POST http://localhost:8003/api/superadmin/register \
  -H "Content-Type: application/json" \
  -d '{
    "full_name": "Super Admin",
    "email": "admin@company.com",
    "password": "SecurePass@2025",
    "phone": "+919123456789"
  }'
```

**Error Responses**:
- `400`: Email already exists
- `422`: Validation errors (invalid email format, missing fields)

### POST /api/superadmin/login
**Description**: Super admin login - authenticate and receive JWT token (24-hour expiry)

**Access**: Public (no authentication required)

**Request Body**:
```json
{
  "email": "superadmin@example.com",
  "password": "StrongPassword@123"
}
```

**Required Fields**: `email`, `password`

**Response**:
```json
{
  "status": "success",
  "message": "Login successful",
  "data": {
    "id": "superadmin-uuid-1234",
    "full_name": "John Doe",
    "email": "superadmin@example.com",
    "phone": "+919876543210",
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "bearer",
    "expires_in": 86400
  }
}
```

**cURL Example**:
```bash
curl -X POST http://localhost:8003/api/superadmin/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@company.com",
    "password": "SecurePass@2025"
  }'
```

**Response Fields**:
- `token`: JWT token for super admin authentication
- `token_type`: Always "bearer"
- `expires_in`: Token expiry time in seconds (86400 = 24 hours)

**Usage**: Save the `token` and use as `Authorization: Bearer <token>` for all super admin protected endpoints.

**Error Responses**:
- `401`: Invalid email or password
- `401`: Account is disabled

### GET /api/superadmin/me
**Description**: Get current super admin profile information

**Access**: Super Admin only

**Headers**: 
```
Authorization: Bearer <super_admin_jwt_token>
```

**Response**:
```json
{
  "status": "success",
  "data": {
    "id": "superadmin-uuid-1234",
    "full_name": "John Doe",
    "email": "superadmin@example.com",
    "phone": "+919876543210",
    "is_active": true,
    "created_at": "2025-09-05T12:00:00Z",
    "updated_at": "2025-09-05T12:00:00Z"
  }
}
```

**cURL Example**:
```bash
curl -X GET http://localhost:8003/api/superadmin/me \
  -H "Authorization: Bearer your_superadmin_token_here" \
  -H "Content-Type: application/json"
```

### GET /api/superadmin/verify-token
**Description**: Verify if the super admin token is valid and not expired

**Access**: Super Admin only

**Headers**: 
```
Authorization: Bearer <super_admin_jwt_token>
```

**Response**:
```json
{
  "status": "success",
  "message": "Token is valid",
  "data": {
    "id": "superadmin-uuid-1234",
    "email": "superadmin@example.com",
    "full_name": "John Doe"
  }
}
```

**cURL Example**:
```bash
curl -X GET http://localhost:8003/api/superadmin/verify-token \
  -H "Authorization: Bearer your_superadmin_token_here" \
  -H "Content-Type: application/json"
```

**Error Responses**:
- `401`: Token has expired
- `401`: Invalid authentication credentials
- `401`: Super admin not found

---

## 1. Authentication & User Management

### POST /api/auth/register
**Description**: Register a new student (public endpoint). Creates user with nested course and branch information. Upon successful registration, an SMS containing login credentials will be sent to the registered phone number.

**Access**: Public (no authentication required)

**Request Body**:
```json
{
  "email": "pittisunilkumar3@gmail.com",
  "phone": "+9876543210",
  "first_name": "John",
  "last_name": "Doe",
  "role": "student",
  "password": "Neelarani@10",
  "date_of_birth": "2005-08-15",
  "gender": "male",
  "biometric_id": "optional-fingerprint-id",
  "course": {
    "category_id": "category-uuid",
    "course_id": "course-uuid",
    "duration": "6-months"
  },
  "branch": {
    "location_id": "location-uuid",
    "branch_id": "branch-uuid"
  }
}
```

**Required Fields**: `email`, `phone`, `first_name`, `last_name`, `role`

**Optional Fields**: `password`, `date_of_birth`, `gender`, `biometric_id`, `course`, `branch`

**Field Specifications**:
- `date_of_birth`: YYYY-MM-DD format (e.g., "2005-08-15")
- `gender`: Any string value (e.g., "male", "female", "other")
- `course`: If provided, all nested fields are required
- `branch`: If provided, all nested fields are required
- `password`: Auto-generated if not provided

**Response**:
```json
{
  "message": "User registered successfully",
  "user_id": "0b44cebf-f0e1-4716-b521-0e3ba290e5c4"
}
```

**cURL Example**:
```bash
curl -X POST http://localhost:8003/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "newuser@example.com",
    "phone": "+1234567890",
    "first_name": "New",
    "last_name": "User",
    "role": "student",
    "password": "UserPass123!",
    "date_of_birth": "1995-01-01",
    "gender": "male",
    "course": {
      "category_id": "cat-123",
      "course_id": "course-456", 
      "duration": "3-months"
    },
    "branch": {
      "location_id": "loc-789",
      "branch_id": "branch-101"
    }
  }'
```

**Notes**: 
- SMS with login credentials sent to provided phone number
- If `password` not provided, random password generated
- User data stored with nested structure intact
- `full_name` auto-generated from `first_name` + `last_name`



### POST /api/auth/login
**Description**: User login - authenticate user and receive JWT bearer token

**Access**: Public (no authentication required)

**Request Body**:
```json
{
  "email": "user@example.com",
  "password": "password123"
}
```

**Required Fields**: `email`, `password`

**Success Response (200 OK)**:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIwYjQ0Y2ViZi1mMGUxLTQ3MTYtYjUyMS0wZTNiYTI5MGU1YzQiLCJleHAiOjE3NTcxMzY3MDZ9.TzV1jpaRxAh0jRUPwZ5o8fAPuaBMNQsNgUAHhVKWZkI",
  "token_type": "bearer",
  "user": {
    "id": "1e22ab99-b6ab-4cf1-9bc5-95cd3d62da21",
    "email": "user@example.com",
    "role": "student",
    "first_name": "John",
    "last_name": "Doe",
    "full_name": "John Doe",
    "date_of_birth": "2005-08-15",
    "gender": "male",
    "course": {
      "category_id": "category-uuid",
      "course_id": "course-uuid",
      "duration": "6-months"
    },
    "branch": {
      "location_id": "location-uuid", 
      "branch_id": "branch-uuid"
    },
    "is_active": true,
    "created_at": "2025-01-07T10:30:00Z",
    "updated_at": "2025-01-07T10:30:00Z"
  }
}
```

**Error Responses**:

**401 Unauthorized** - Invalid Credentials:
```json
{
  "detail": "Incorrect email or password"
}
```

**422 Unprocessable Entity** - Validation Error:
```json
{
  "detail": [
    {
      "type": "missing",
      "loc": ["body", "email"],
      "msg": "Field required",
      "input": {}
    },
    {
      "type": "string_type",
      "loc": ["body", "password"],
      "msg": "Input should be a valid string",
      "input": null
    }
  ]
}
```

**403 Forbidden** - Account Inactive:
```json
{
  "detail": "Account is inactive. Please contact administrator."
}
```

**429 Too Many Requests** - Rate Limiting:
```json
{
  "detail": "Too many login attempts. Please try again later."
}
```

**cURL Example**:
```bash
curl -X POST http://localhost:8003/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "superadmin@test.com",
    "password": "SuperAdmin123!"
  }'
```

**Response Fields**:
- `access_token`: JWT token for authentication (use in Authorization header)
- `token_type`: Always "bearer"
- `user`: Complete user profile with nested objects
- Nested `course` and `branch` objects (null if not set during registration)

**Usage**: Save the `access_token` and use as `Authorization: Bearer <token>` for all protected endpoints.

### GET /api/auth/me
**Description**: Get current authenticated user information

**Access**: All authenticated users

**Headers**: 
```
Authorization: Bearer <your_jwt_token>
```

**Response**:
```json
{
  "id": "0b44cebf-f0e1-4716-b521-0e3ba290e5c4",
  "email": "user@example.com",
  "phone": "+1234567890",
  "first_name": "John",
  "last_name": "Doe",
  "full_name": "John Doe",
  "role": "student",
  "biometric_id": "fingerprint_123",
  "is_active": true,
  "date_of_birth": "2005-08-15",
  "gender": "male",
  "created_at": "2025-01-07T12:00:00Z",
  "updated_at": "2025-01-07T12:00:00Z"
}
```

**cURL Example**:
```bash
curl -X GET http://localhost:8003/api/auth/me \
  -H "Authorization: Bearer your_token_here" \
  -H "Content-Type: application/json"
```

**Notes**: 
- Returns complete user profile for current authenticated user
- `date_of_birth`, `gender`, `biometric_id` may be `null` if not set
- Timestamps in ISO 8601 format

### PUT /api/auth/profile
**Description**: Update user profile
**Access**: Authenticated users
**Headers**: 
```
Authorization: Bearer <your_jwt_token>
```
**Request Body** (all fields are optional):
```json
{
  "email": "newemail@example.com",
  "phone": "+0987654321",
  "first_name": "Jane",
  "last_name": "Smith",
  "biometric_id": "fingerprint_456",
  "date_of_birth": "1990-01-01",
  "gender": "female"
}
```
**Optional Fields**: All fields in the request body are optional
**Response**:
```json
{
  "message": "Profile updated successfully"
}
```

### POST /api/auth/forgot-password
**Description**: Initiate password reset. If an account with the provided email exists, a password reset token will be sent via SMS.
**Access**: Public
**Request Body**:
```json
{
  "email": "user@example.com"
}
```
**Required Fields**: `email`
**Response**:
```json
{
  "message": "If an account with that email exists, a password reset link has been sent."
}
```
**Note**: In testing mode (`TESTING=True` in .env), the response will also include the reset token for testing purposes.

### POST /api/auth/reset-password
**Description**: Reset password with a valid token
**Access**: Public
**Request Body**:
```json
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "new_password": "YourNewPassword123!"
}
```
**Required Fields**: `token`, `new_password`
**Response**:
```json
{
  "message": "Password has been reset successfully."
}
```

---

## 2. User Management

### POST /api/coaches/login
**Description**: Coach login endpoint to authenticate coaches and receive JWT token

**Access**: Public (no authentication required)

**Request Body**:
```json
{
  "email": "coach@example.com",
  "password": "CoachPassword123!"
}
```

**Required Fields**: `email`, `password`

**Success Response (200 OK)**:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "coach": {
    "id": "67836f2a5b8e4c2f9a1d3e56",
    "personal_info": {
      "first_name": "Ravi",
      "last_name": "Kumar",
      "gender": "Male",
      "date_of_birth": "1985-06-15"
    },
    "contact_info": {
      "email": "coach@example.com",
      "country_code": "+91",
      "phone": "9876543210"
    },
    "address_info": {
      "address": "123 MG Road",
      "area": "Indiranagar",
      "city": "Bengaluru",
      "state": "Karnataka",
      "zip_code": "560038",
      "country": "India"
    },
    "professional_info": {
      "education_qualification": "Bachelor's Degree",
      "professional_experience": "5+ years",
      "designation_id": "designation-uuid-1234",
      "certifications": [
        "Black Belt in Karate",
        "Certified Fitness Trainer"
      ]
    },
    "areas_of_expertise": [
      "Taekwondo",
      "Karate",
      "Kung Fu",
      "Mixed Martial Arts"
    ],
    "full_name": "Ravi Kumar",
    "is_active": true,
    "created_at": "2025-01-07T12:00:00Z",
    "updated_at": "2025-01-07T12:00:00Z"
  },
  "expires_in": 86400,
  "message": "Login successful"
}
```

**Error Responses**:

**401 Unauthorized** - Invalid Credentials:
```json
{
  "detail": "Invalid email or password"
}
```

**401 Unauthorized** - Account Inactive:
```json
{
  "detail": "Account is inactive. Please contact administrator."
}
```

**422 Unprocessable Entity** - Validation Error:
```json
{
  "detail": [
    {
      "type": "missing",
      "loc": ["body", "email"],
      "msg": "Field required",
      "input": {}
    }
  ]
}
```

**cURL Example**:
```bash
curl -X POST "http://localhost:8003/api/coaches/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "coach@example.com",
    "password": "CoachPassword123!"
  }'
```

### GET /api/coaches/me
**Description**: Get current authenticated coach's profile

**Access**: Coach only

**Headers**:
```
Authorization: Bearer <coach_jwt_token>
```

**Success Response (200 OK)**:
```json
{
  "coach": {
    "id": "67836f2a5b8e4c2f9a1d3e56",
    "personal_info": {
      "first_name": "Ravi",
      "last_name": "Kumar",
      "gender": "Male",
      "date_of_birth": "1985-06-15"
    },
    "contact_info": {
      "email": "coach@example.com",
      "country_code": "+91",
      "phone": "9876543210"
    },
    "address_info": {
      "address": "123 MG Road",
      "area": "Indiranagar",
      "city": "Bengaluru",
      "state": "Karnataka",
      "zip_code": "560038",
      "country": "India"
    },
    "professional_info": {
      "education_qualification": "Bachelor's Degree",
      "professional_experience": "5+ years",
      "designation_id": "designation-uuid-1234",
      "certifications": [
        "Black Belt in Karate",
        "Certified Fitness Trainer"
      ]
    },
    "areas_of_expertise": [
      "Taekwondo",
      "Karate",
      "Kung Fu",
      "Mixed Martial Arts"
    ],
    "full_name": "Ravi Kumar",
    "is_active": true,
    "created_at": "2025-01-07T12:00:00Z",
    "updated_at": "2025-01-07T12:00:00Z"
  }
}
```

**Error Responses**:

**401 Unauthorized**:
```json
{
  "detail": "Invalid authentication credentials"
}
```

**403 Forbidden** - Not a Coach:
```json
{
  "detail": "Insufficient permissions"
}
```

### POST /api/coaches
**Description**: Create new coach with comprehensive nested structure. This endpoint stores coach information in a structured format with personal, contact, address, and professional details in a dedicated coaches collection.

**Access**: Super Admin, Coach Admin

**Headers**:
```
Authorization: Bearer <your_jwt_token>
Content-Type: application/json
```

**Request Body**:
```json
{
  "personal_info": {
    "first_name": "Ravi",
    "last_name": "Kumar",
    "gender": "Male",
    "date_of_birth": "1985-06-15"
  },
  "contact_info": {
    "email": "coach@example.com",
    "country_code": "+91",
    "phone": "9876543210",
    "password": "SecurePassword@123"
  },
  "address_info": {
    "address": "123 MG Road",
    "area": "Indiranagar",
    "city": "Bengaluru",
    "state": "Karnataka",
    "zip_code": "560038",
    "country": "India"
  },
  "professional_info": {
    "education_qualification": "Bachelor's Degree",
    "professional_experience": "5+ years",
    "designation_id": "designation-uuid-1234",
    "certifications": [
      "Black Belt in Karate",
      "Certified Fitness Trainer"
    ]
  },
  "areas_of_expertise": [
    "Taekwondo",
    "Karate",
    "Kung Fu",
    "Mixed Martial Arts"
  ]
}
```

**Required Fields**: All nested objects and their fields are required

**Field Specifications**:
- `personal_info.date_of_birth`: YYYY-MM-DD format (e.g., "1985-06-15")
- `personal_info.gender`: Any string value (e.g., "Male", "Female", "Other")
- `contact_info.email`: Must be a valid email address (unique)
- `contact_info.country_code`: Phone country code (e.g., "+91", "+1")
- `contact_info.phone`: Phone number without country code
- `contact_info.password`: Auto-generated if not provided
- `professional_info.certifications`: Array of certification strings
- `areas_of_expertise`: Array of expertise area strings

**Success Response (201 Created)**:
```json
{
    "message": "Coach created successfully",
    "coach_id": "4896e1fb-10c4-4a87-be0d-cf6733d7ee0b"
}
```

**Error Responses**:

**400 Bad Request** - Validation Error:
```json
{
  "detail": [
    {
      "type": "missing",
      "loc": ["body", "personal_info", "first_name"],
      "msg": "Field required",
      "input": {}
    },
    {
      "type": "string_type",
      "loc": ["body", "contact_info", "email"],
      "msg": "Input should be a valid string",
      "input": null
    }
  ]
}
```

**409 Conflict** - Email Already Exists:
```json
{
  "detail": "Coach with email coach@example.com already exists"
}
```

**401 Unauthorized** - Invalid/Missing Token:
```json
{
  "detail": "Could not validate credentials"
}
```

**403 Forbidden** - Insufficient Permissions:
```json
{
  "detail": "Not enough permissions to access this resource"
}
```

**500 Internal Server Error** - Database Error:
```json
{
  "detail": "Internal server error occurred while creating coach"
}
```

**Database Storage**: Coaches are stored in a dedicated `coaches` collection separate from the general `users` collection.

### GET /api/coaches
**Description**: Get coaches with filtering options

**Access**: Super Admin, Coach Admin

**Query Parameters**:
- `skip`: Number of coaches to skip (default: 0)
- `limit`: Number of coaches to return (default: 50, max: 100)
- `active_only`: Filter only active coaches (default: true)
- `area_of_expertise`: Filter by specific area of expertise

**Success Response (200 OK)**:
```json
{
  "coaches": [
    {
      "id": "67836f2a5b8e4c2f9a1d3e56",
      "personal_info": {
        "first_name": "Ravi",
        "last_name": "Kumar",
        "gender": "Male",
        "date_of_birth": "1985-06-15"
      },
      "contact_info": {
        "email": "coach@example.com",
        "country_code": "+91",
        "phone": "9876543210"
      },
      "address_info": {
        "address": "123 MG Road",
        "area": "Indiranagar",
        "city": "Bengaluru",
        "state": "Karnataka",
        "zip_code": "560038",
        "country": "India"
      },
      "professional_info": {
        "education_qualification": "Bachelor's Degree",
        "professional_experience": "5+ years",
        "designation_id": "designation-uuid-1234",
        "certifications": [
          "Black Belt in Karate",
          "Certified Fitness Trainer"
        ]
      },
      "areas_of_expertise": [
        "Taekwondo",
        "Karate",
        "Kung Fu",
        "Mixed Martial Arts"
      ],
      "full_name": "Ravi Kumar",
      "is_active": true,
      "created_at": "2025-01-07T12:00:00Z",
      "updated_at": "2025-01-07T12:00:00Z"
    },
    {
      "id": "67836f2a5b8e4c2f9a1d3e57",
      "personal_info": {
        "first_name": "Priya",
        "last_name": "Sharma",
        "gender": "Female",
        "date_of_birth": "1990-03-22"
      },
      "contact_info": {
        "email": "priya.sharma@martialarts.com",
        "country_code": "+91",
        "phone": "9876543211"
      },
      "address_info": {
        "address": "456 Brigade Road",
        "area": "MG Road",
        "city": "Bengaluru",
        "state": "Karnataka",
        "zip_code": "560001",
        "country": "India"
      },
      "professional_info": {
        "education_qualification": "Masters in Sports Science",
        "professional_experience": "7+ years",
        "designation_id": "senior-coach-002",
        "certifications": [
          "Black Belt in Taekwondo",
          "Certified Self Defense Instructor"
        ]
      },
      "areas_of_expertise": [
        "Taekwondo",
        "Self Defense",
        "Women's Self Defense"
      ],
      "full_name": "Priya Sharma",
      "is_active": true,
      "created_at": "2025-01-06T10:30:00Z",
      "updated_at": "2025-01-06T10:30:00Z"
    }
  ],
  "total": 15,
  "page": 1,
  "limit": 50,
  "has_next": false,
  "has_previous": false
}
```

**Empty Result Response (200 OK)**:
```json
{
  "coaches": [],
  "total": 0,
  "page": 1,
  "limit": 50,
  "has_next": false,
  "has_previous": false
}
```

**Error Responses**:

**401 Unauthorized**:
```json
{
  "detail": "Could not validate credentials"
}
```

**403 Forbidden**:
```json
{
  "detail": "Not enough permissions to access this resource"
}
```

**422 Unprocessable Entity** - Invalid Query Parameters:
```json
{
  "detail": [
    {
      "type": "int_parsing",
      "loc": ["query", "limit"],
      "msg": "Input should be a valid integer",
      "input": "invalid"
    }
  ]
}
```

### GET /api/coaches/{coach_id}
**Description**: Get coach by ID with complete information

**Access**: Super Admin, Coach Admin

**Path Parameters**:
- `coach_id`: UUID of the coach

**Success Response (200 OK)**:
```json
{
  "id": "67836f2a5b8e4c2f9a1d3e56",
  "personal_info": {
    "first_name": "Ravi",
    "last_name": "Kumar",
    "gender": "Male",
    "date_of_birth": "1985-06-15"
  },
  "contact_info": {
    "email": "coach@example.com",
    "country_code": "+91",
    "phone": "9876543210"
  },
  "address_info": {
    "address": "123 MG Road",
    "area": "Indiranagar",
    "city": "Bengaluru",
    "state": "Karnataka",
    "zip_code": "560038",
    "country": "India"
  },
  "professional_info": {
    "education_qualification": "Bachelor's Degree",
    "professional_experience": "5+ years",
    "designation_id": "designation-uuid-1234",
    "certifications": [
      "Black Belt in Karate",
      "Certified Fitness Trainer"
    ]
  },
  "areas_of_expertise": [
    "Taekwondo",
    "Karate",
    "Kung Fu",
    "Mixed Martial Arts"
  ],
  "full_name": "Ravi Kumar",
  "is_active": true,
  "created_at": "2025-01-07T12:00:00Z",
  "updated_at": "2025-01-07T12:00:00Z"
}
```

**Error Responses**:

**404 Not Found**:
```json
{
  "detail": "Coach not found"
}
```

**401 Unauthorized**:
```json
{
  "detail": "Could not validate credentials"
}
```

**403 Forbidden**:
```json
{
  "detail": "Not enough permissions to access this resource"
}
```

**422 Unprocessable Entity** - Invalid Coach ID:
```json
{
  "detail": [
    {
      "type": "string_type",
      "loc": ["path", "coach_id"],
      "msg": "Input should be a valid string",
      "input": null
    }
  ]
}
```

### PUT /api/coaches/{coach_id}
**Description**: Update coach information with nested structure

**Access**: Super Admin, Coach Admin

**Path Parameters**:
- `coach_id`: UUID of the coach to update

**Request Body** (all fields are optional):
```json
{
  "personal_info": {
    "first_name": "Updated Name",
    "last_name": "Updated Lastname",
    "gender": "Male",
    "date_of_birth": "1985-06-15"
  },
  "contact_info": {
    "email": "newemail@example.com",
    "country_code": "+91",
    "phone": "9876543211",
    "password": "NewPassword@123"
  },
  "areas_of_expertise": [
    "Taekwondo",
    "Karate",
    "Self Defense"
  ]
}
```

**Success Response (200 OK)**:
```json
{
  "message": "Coach updated successfully",
  "coach": {
    "id": "67836f2a5b8e4c2f9a1d3e56",
    "personal_info": {
      "first_name": "Updated Name",
      "last_name": "Updated Lastname",
      "gender": "Male",
      "date_of_birth": "1985-06-15"
    },
    "contact_info": {
      "email": "newemail@example.com",
      "country_code": "+91",
      "phone": "9876543211"
    },
    "address_info": {
      "address": "123 MG Road",
      "area": "Indiranagar",
      "city": "Bengaluru",
      "state": "Karnataka",
      "zip_code": "560038",
      "country": "India"
    },
    "professional_info": {
      "education_qualification": "Bachelor's Degree",
      "professional_experience": "5+ years",
      "designation_id": "designation-uuid-1234",
      "certifications": [
        "Black Belt in Karate",
        "Certified Fitness Trainer"
      ]
    },
    "areas_of_expertise": [
      "Taekwondo",
      "Karate",
      "Self Defense"
    ],
    "full_name": "Updated Name Updated Lastname",
    "is_active": true,
    "created_at": "2025-01-07T12:00:00Z",
    "updated_at": "2025-01-07T15:30:00Z"
  }
}
```

**Error Responses**:

**404 Not Found**:
```json
{
  "detail": "Coach not found"
}
```

**409 Conflict** - Email Already Exists:
```json
{
  "detail": "Coach with email newemail@example.com already exists"
}
```

**400 Bad Request** - Validation Error:
```json
{
  "detail": [
    {
      "type": "value_error",
      "loc": ["body", "contact_info", "email"],
      "msg": "value is not a valid email address",
      "input": "invalid-email"
    }
  ]
}
```

**401 Unauthorized**:
```json
{
  "detail": "Could not validate credentials"
}
```

**403 Forbidden**:
```json
{
  "detail": "Not enough permissions to access this resource"
}
```

### DELETE /api/coaches/{coach_id}
**Description**: Deactivate coach (sets is_active to false)

**Access**: Super Admin only

**Path Parameters**:
- `coach_id`: UUID of the coach to deactivate

**Success Response (200 OK)**:
```json
{
  "message": "Coach deactivated successfully",
  "coach_id": "67836f2a5b8e4c2f9a1d3e56",
  "status": "deactivated"
}
```

**Error Responses**:

**404 Not Found**:
```json
{
  "detail": "Coach not found"
}
```

**400 Bad Request** - Coach Already Inactive:
```json
{
  "detail": "Coach is already inactive"
}
```

**401 Unauthorized**:
```json
{
  "detail": "Could not validate credentials"
}
```

**403 Forbidden**:
```json
{
  "detail": "Not enough permissions to access this resource. Super Admin access required."
}
```

### GET /api/coaches/stats/overview
**Description**: Get coach statistics and analytics

**Access**: Super Admin, Coach Admin

**Success Response (200 OK)**:
```json
{
  "total_coaches": 25,
  "active_coaches": 22,
  "inactive_coaches": 3,
  "expertise_distribution": [
    {
      "_id": "Karate",
      "count": 15,
      "percentage": 60.0
    },
    {
      "_id": "Taekwondo",
      "count": 12,
      "percentage": 48.0
    },
    {
      "_id": "Mixed Martial Arts",
      "count": 8,
      "percentage": 32.0
    },
    {
      "_id": "Self Defense",
      "count": 6,
      "percentage": 24.0
    },
    {
      "_id": "Kung Fu",
      "count": 4,
      "percentage": 16.0
    }
  ],
  "recent_additions": [
    {
      "id": "67836f2a5b8e4c2f9a1d3e56",
      "full_name": "Ravi Kumar",
      "areas_of_expertise": ["Karate", "Taekwondo"],
      "created_at": "2025-01-07T12:00:00Z"
    },
    {
      "id": "67836f2a5b8e4c2f9a1d3e57",
      "full_name": "Priya Sharma",
      "areas_of_expertise": ["Taekwondo", "Self Defense"],
      "created_at": "2025-01-06T10:30:00Z"
    }
  ],
  "statistics_generated_at": "2025-01-07T16:45:00Z"
}
```

**Error Responses**:

**401 Unauthorized**:
```json
{
  "detail": "Could not validate credentials"
}
```

**403 Forbidden**:
```json
{
  "detail": "Not enough permissions to access this resource"
}
```

**500 Internal Server Error**:
```json
{
  "detail": "Error generating coach statistics"
}
```

## Super Admin Coach Management

### POST /api/superadmin/coaches
**Description**: Create coach using super admin authentication

**Access**: Super Admin only (uses superadmin token)

**Headers**:
```
Authorization: Bearer <super_admin_jwt_token>
Content-Type: application/json
```

**Request Body**: Same format as regular coach creation above.

**Success Response (201 Created)**: Same format as regular coach creation above.

**Error Responses**: Same as regular coach creation, plus:

**403 Forbidden** - Super Admin Required:
```json
{
  "detail": "Super Admin access required"
}
```

### GET /api/superadmin/coaches
**Description**: Get coaches using super admin authentication

**Access**: Super Admin only

**Query Parameters**: Same as regular coaches endpoint

**Success Response (200 OK)**: Same format as regular coaches list above.

**Error Responses**: Same as regular coaches list, plus super admin access restrictions.

### GET /api/superadmin/coaches/{coach_id}
**Description**: Get coach by ID using super admin authentication

**Access**: Super Admin only

**Success Response (200 OK)**: Same format as regular coach details above.

**Error Responses**: Same as regular coach details, plus super admin access restrictions.

### PUT /api/superadmin/coaches/{coach_id}
**Description**: Update coach using super admin authentication

**Access**: Super Admin only

**Success Response (200 OK)**: Same format as regular coach update above.

**Error Responses**: Same as regular coach update, plus super admin access restrictions.

### DELETE /api/superadmin/coaches/{coach_id}
**Description**: Deactivate coach using super admin authentication

**Access**: Super Admin only

**Success Response (200 OK)**: Same format as regular coach deactivation above.

**Error Responses**: Same as regular coach deactivation, plus super admin access restrictions.

### GET /api/superadmin/coaches/stats/overview
**Description**: Get coach statistics using super admin authentication

**Access**: Super Admin only

**Success Response (200 OK)**: Same format as regular coach statistics above.

**Error Responses**: Same as regular coach statistics, plus super admin access restrictions.

### POST /api/users
**Description**: Create new user. Coach Admins can only create users for their own branch and cannot create other admin users (Super Admin or Coach Admin roles).
**Access**: Super Admin, Coach Admin
**Request Body**:
```json
{
  "email": "newuser@example.com",
  "phone": "+1234567890",
  "full_name": "New User",
  "role": "coach_admin",
  "branch_id": "branch-uuid",
  "date_of_birth": "1990-01-01",
  "gender": "female"
}
```
**Response**:
```json
{
  "message": "User created successfully",
  "user_id": "user-uuid"
}
```

### GET /api/users
**Description**: Get users with filtering and role-based access control
**Access**: Super Admin, Coach Admin, Coach
**Authentication**: Bearer Token (Superadmin, Coach Admin, or Coach)

**Access Rules**:
- **Super Admin**: Can view all users across all branches
- **Coach Admin**: Can view all users within their assigned branch only
- **Coach**: Can view only students within their assigned branch

**Query Parameters**:
- `role`: Filter by user role (optional)
  - Values: `student`, `coach`, `coach_admin`, `super_admin`
  - Note: Coaches can only filter by `student` role
- `branch_id`: Filter by branch (optional)
  - Coach Admin/Coach: Must match their assigned branch
- `skip`: Skip records for pagination (default: 0)
- `limit`: Limit records per page (default: 50, max: 100)

**Headers**:
```
Authorization: Bearer <superadmin_token|coach_admin_token|coach_token>
Content-Type: application/json
```

**Example Request**:
```bash
GET /api/users?role=student&branch_id=branch-123&skip=0&limit=10
```

**Response**:
```json
{
  "users": [
    {
      "id": "user-uuid",
      "email": "student@example.com",
      "full_name": "John Student",
      "role": "student",
      "branch_id": "branch-123",
      "is_active": true,
      "date_of_birth": "2000-01-01",
      "gender": "male",
      "phone": "+1234567890",
      "biometric_id": "fingerprint_123",
      "created_at": "2025-01-01T10:00:00Z",
      "updated_at": "2025-01-01T10:00:00Z"
    }
  ],
  "total": 1,
  "skip": 0,
  "limit": 10,
  "message": "Retrieved 1 users"
}
```

**Error Responses**:
- **401 Unauthorized**: Invalid or missing token
- **403 Forbidden**: Insufficient permissions for requested data
- **400 Bad Request**: Invalid query parameters

### PUT /api/users/{user_id}
**Description**: Update user. Coach Admins can only update students in their own branch.
**Access**: Super Admin, Coach Admin
**Request Body**:
```json
{
  "email": "newemail@example.com",
  "phone": "+0987654321",
  "full_name": "Jane Doe",
  "biometric_id": "fingerprint_456",
  "date_of_birth": "1990-01-01",
  "gender": "female",
  "is_active": true
}

```
**Response**:
```json
{
  "message": "User updated successfully"
}
```

### DELETE /api/users/{user_id}
**Description**: Deactivate user
**Access**: Super Admin
**Response**:
```json
{
  "message": "User deactivated successfully"
}
```

### POST /api/users/{user_id}/force-password-reset
**Description**: Force a password reset for a user. A new temporary password will be generated and sent to the user via SMS and WhatsApp.
**Access**: Super Admin, Coach Admin
**Details**:
- Super Admins can reset the password for any user.
- Coach Admins can only reset passwords for Students and Coaches within their own branch.
**Response**:
```json
{
  "message": "Password for user [User's Full Name] has been reset and sent to them."
}
```

---

## 3. Branch Management

### POST /api/branches
**Description**: Create new branch with comprehensive nested structure

**Access**: Super Admin only
**Authentication**: Bearer Token (Superadmin token from either `/api/superadmin/login` or regular admin login)

**Headers**:
```
Authorization: Bearer <superadmin_token>
Content-Type: application/json
```

**Request Body**:
```json
{
  "branch": {
    "name": "Rock martial arts",
    "code": "RMA01",
    "email": "yourname@email.com",
    "phone": "+13455672356",
    "address": {
      "line1": "928#123",
      "area": "Madhapur",
      "city": "Hyderabad",
      "state": "Telangana",
      "pincode": "500089",
      "country": "India"
    }
  },
  "manager_id": "manager-uuid-1234",
  "operational_details": {
    "courses_offered": ["Rock martial arts"],
    "timings": [
      { "day": "Monday", "open": "07:00", "close": "19:00" },
      { "day": "Tuesday", "open": "07:00", "close": "19:00" }
    ],
    "holidays": ["2025-10-02", "2025-12-25"]
  },
  "assignments": {
    "accessories_available": true,
    "courses": ["course-uuid-1", "course-uuid-2", "course-uuid-3"],
    "branch_admins": ["coach-uuid-1", "coach-uuid-2"]
  },
  "bank_details": {
    "bank_name": "State Bank of India",
    "account_number": "XXXXXXXXXXXX",
    "upi_id": "name@ybl"
  }
}
```

**Required Fields**: All nested objects and their fields are required

**Field Specifications**:
- `assignments.courses`: Array of course IDs (UUIDs) for database relationships
- `assignments.branch_admins`: Array of user IDs (UUIDs) for coaches who can manage this branch
- `operational_details.courses_offered`: Array of course names for display purposes
- `operational_details.holidays`: Array of date strings in YYYY-MM-DD format
- `operational_details.timings`: Array with day, open/close times in HH:MM format

**Response**:
```json
{
  "message": "Branch created successfully",
  "branch_id": "branch-uuid"
}
```

**cURL Example**:
```bash
curl -X POST http://localhost:8003/api/branches \
  -H "Authorization: Bearer your_token_here" \
  -H "Content-Type: application/json" \
  -d '{
    "branch": {
      "name": "Test Branch",
      "code": "TB01",
      "email": "test@branch.com",
      "phone": "+1234567890",
      "address": {
        "line1": "123 Test St",
        "area": "Test Area",
        "city": "Test City",
        "state": "Test State",
        "pincode": "123456",
        "country": "India"
      }
    },
    "manager_id": "manager-uuid",
    "operational_details": {
      "courses_offered": ["Martial Arts"],
      "timings": [
        {"day": "Monday", "open": "09:00", "close": "18:00"}
      ],
      "holidays": ["2025-12-25"]
    },
    "assignments": {
      "accessories_available": true,
      "courses": ["course-uuid-1"],
      "branch_admins": ["admin-uuid-1"]
    },
    "bank_details": {
      "bank_name": "Test Bank",
      "account_number": "1234567890",
      "upi_id": "test@upi"
    }
  }'
```

### GET /api/branches
**Description**: Get all branches with comprehensive nested structure
**Access**: All authenticated users
**Query Parameters**:
- `skip`: Skip records (pagination)
- `limit`: Limit records (default: 50)
**Response**:
```json
{
  "branches": [
    {
      "id": "branch-uuid",
      "branch": {
        "name": "Rock martial arts",
        "code": "RMA01",
        "email": "yourname@email.com",
        "phone": "+13455672356",
        "address": {
          "line1": "928#123",
          "area": "Madhapur",
          "city": "Hyderabad",
          "state": "Telangana",
          "pincode": "500089",
          "country": "India"
        }
      },
      "manager_id": "manager-uuid-1234",
      "operational_details": {
        "courses_offered": ["Rock martial arts"],
        "timings": [
          { "day": "Monday", "open": "07:00", "close": "19:00" },
          { "day": "Tuesday", "open": "07:00", "close": "19:00" }
        ],
        "holidays": ["2025-10-02", "2025-12-25"]
      },
      "assignments": {
        "accessories_available": true,
        "courses": ["course-uuid-1", "course-uuid-2", "course-uuid-3"],
        "branch_admins": ["coach-uuid-1", "coach-uuid-2"]
      },
      "bank_details": {
        "bank_name": "State Bank of India",
        "account_number": "XXXXXXXXXXXX",
        "upi_id": "name@ybl"
      },
      "is_active": true,
      "created_at": "2025-01-07T12:00:00Z",
      "updated_at": "2025-01-07T12:00:00Z"
    }
  ]
}
```

### GET /api/branches/{branch_id}
**Description**: Get branch by ID with comprehensive nested structure
**Access**: All authenticated users
**Response**:
```json
{
  "id": "branch-uuid",
  "branch": {
    "name": "Rock martial arts",
    "code": "RMA01",
    "email": "yourname@email.com",
    "phone": "+13455672356",
    "address": {
      "line1": "928#123",
      "area": "Madhapur",
      "city": "Hyderabad",
      "state": "Telangana",
      "pincode": "500089",
      "country": "India"
    }
  },
  "manager_id": "manager-uuid-1234",
  "operational_details": {
    "courses_offered": ["Rock martial arts"],
    "timings": [
      { "day": "Monday", "open": "07:00", "close": "19:00" },
      { "day": "Tuesday", "open": "07:00", "close": "19:00" }
    ],
    "holidays": ["2025-10-02", "2025-12-25"]
  },
  "assignments": {
    "accessories_available": true,
    "courses": ["course-uuid-1", "course-uuid-2", "course-uuid-3"],
    "branch_admins": ["coach-uuid-1", "coach-uuid-2"]
  },
  "bank_details": {
    "bank_name": "State Bank of India",
    "account_number": "XXXXXXXXXXXX",
    "upi_id": "name@ybl"
  },
  "is_active": true,
  "created_at": "2025-01-07T12:00:00Z",
  "updated_at": "2025-01-07T12:00:00Z"
}
```

### PUT /api/branches/{branch_id}
**Description**: Update branch with comprehensive nested structure.
**Access**: Super Admin, Coach Admin (own branch only)
**Details**: Coach Admins can only update branches where they are listed in the `assignments.branch_admins` array and cannot update certain fields (manager_id, is_active, assignments, bank_details).
**Request Body** (all fields are optional):
```json
{
  "branch": {
    "name": "Updated Branch Name",
    "code": "UBN01",
    "email": "updated@email.com",
    "phone": "+1234567890",
    "address": {
      "line1": "456 New St",
      "area": "New Area",
      "city": "New City",
      "state": "New State", 
      "pincode": "123456",
      "country": "India"
    }
  },
  "operational_details": {
    "courses_offered": ["Updated Course"],
    "timings": [
      { "day": "Monday", "open": "08:00", "close": "18:00" }
    ],
    "holidays": ["2025-12-25"]
  }
}
```
**Response**:
```json
{
  "message": "Branch updated successfully"
}
```

### POST /api/branches/{branch_id}/holidays
**Description**: Create a new holiday for a branch.
**Access**: Super Admin, Coach Admin (own branch only)
**Request Body**:
```json
{
  "date": "2025-12-25",
  "description": "Christmas Day"
}
```
**Response**:
```json
{
  "id": "holiday-uuid",
  "branch_id": "branch-uuid",
  "date": "2025-12-25",
  "description": "Christmas Day",
  "created_at": "2025-01-07T12:00:00Z"
}
```

### GET /api/branches/{branch_id}/holidays
**Description**: Get all holidays for a specific branch.
**Access**: All authenticated users
**Response**:
```json
{
  "holidays": [
    {
      "id": "holiday-uuid",
      "branch_id": "branch-uuid",
      "date": "2025-12-25",
      "description": "Christmas Day",
      "created_at": "2025-01-07T12:00:00Z"
    }
  ]
}
```

### DELETE /api/branches/{branch_id}/holidays/{holiday_id}
**Description**: Delete a holiday for a branch.
**Access**: Super Admin, Coach Admin (own branch only)
**Response**: (No content) `204 No Content`

---

## 4. Course Management

### POST /api/courses
**Description**: Create new course with comprehensive nested structure

**Access**: Super Admin only

**Headers**:
```
Authorization: Bearer <your_jwt_token>
Content-Type: application/json
```

**Request Body**:
```json
{
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
}
```

**Required Fields**: All nested objects and their fields are required

**Field Specifications**:
- `title`: Course display name
- `code`: Unique course identifier/code
- `martial_art_style_id`: UUID reference to martial art style
- `difficulty_level`: Skill level (e.g., "Beginner", "Intermediate", "Advanced")
- `category_id`: UUID reference to course category
- `instructor_id`: UUID reference to instructor/coach
- `student_requirements.prerequisites`: Array of requirement strings
- `course_content.equipment_required`: Array of required equipment items
- `media_resources`: Optional URLs for course image and promotional video
- `pricing.amount`: Course fee amount as number
- `settings.active`: Boolean to enable/disable course

**Response**:
```json
{
  "message": "Course created successfully",
  "course_id": "course-uuid"
}
```

**cURL Example**:
```bash
curl -X POST http://localhost:8003/api/courses \
  -H "Authorization: Bearer your_token_here" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Beginner Karate Training",
    "code": "KAR-BEG-001",
    "description": "Introduction to Karate fundamentals and basic techniques.",
    "martial_art_style_id": "style-karate-001",
    "difficulty_level": "Beginner",
    "category_id": "cat-martial-arts",
    "instructor_id": "instructor-john-doe",
    "student_requirements": {
      "max_students": 15,
      "min_age": 5,
      "max_age": 70,
      "prerequisites": ["Basic physical fitness"]
    },
    "course_content": {
      "syllabus": "Week 1: Basic stances, Week 2: Blocking techniques, Week 3: Basic kicks, Week 4: Kata practice",
      "equipment_required": ["Karate uniform", "Belt", "Protective gear"]
    },
    "media_resources": {
      "course_image_url": "https://example.com/karate-course.jpg",
      "promo_video_url": "https://youtube.com/watch?v=xyz123"
    },
    "pricing": {
      "currency": "INR",
      "amount": 5000,
      "branch_specific_pricing": false
    },
    "settings": {
      "offers_certification": true,
      "active": true
    }
  }'
```

### GET /api/courses
**Description**: Get all courses with comprehensive nested structure
**Access**: All authenticated users
**Query Parameters**:
- `category_id`: Filter by category ID
- `difficulty_level`: Filter by difficulty level
- `instructor_id`: Filter by instructor ID
- `active_only`: Filter active courses only (default: true)
- `skip`: Skip records (pagination)
- `limit`: Limit records (default: 50)

**Response**:
```json
{
  "courses": [
    {
      "id": "course-uuid",
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
        "amount": 8500.0,
        "branch_specific_pricing": false
      },
      "settings": {
        "offers_certification": true,
        "active": true
      },
      "created_at": "2025-01-07T12:00:00Z",
      "updated_at": "2025-01-07T12:00:00Z"
    }
  ]
}
```

### GET /api/courses/{course_id}
**Description**: Get course by ID with comprehensive nested structure
**Access**: All authenticated users
**Response**:
```json
{
  "id": "course-uuid",
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
    "amount": 8500.0,
    "branch_specific_pricing": false
  },
  "settings": {
    "offers_certification": true,
    "active": true
  },
  "created_at": "2025-01-07T12:00:00Z",
  "updated_at": "2025-01-07T12:00:00Z"
}
```

### PUT /api/courses/{course_id}
**Description**: Update course with comprehensive nested structure.
**Access**: Super Admin, Coach Admin (instructor only)
**Details**: Coach Admins can only update courses where they are listed as the instructor.
**Request Body** (all fields are optional):
```json
{
  "title": "Updated Course Title",
  "description": "Updated course description",
  "student_requirements": {
    "max_students": 25,
    "min_age": 8,
    "max_age": 60,
    "prerequisites": ["Updated prerequisites"]
  },
  "course_content": {
    "syllabus": "Updated syllabus content",
    "equipment_required": ["Updated equipment list"]
  },
  "pricing": {
    "currency": "INR",
    "amount": 9000,
    "branch_specific_pricing": false
  },
  "settings": {
    "offers_certification": true,
    "active": true
  }
}
```
**Response**:
```json
{
  "message": "Course updated successfully"
}
```

### GET /api/courses/{course_id}/stats
**Description**: Get statistics for a specific course.
**Access**: Super Admin, Coach Admin
**Response**:
```json
{
  "course_details": {
    "id": "course-uuid",
    "title": "Advanced Kung Fu Training",
    "instructor_id": "instructor-uuid-91011",
    "settings": {
      "offers_certification": true,
      "active": true
    }
  },
  "active_enrollments": 15
}
```

---

# Complete API Usage Examples

## Super Admin Authentication Flow

### 1. Super Admin Registration (First Time Setup)
```bash
curl -X POST http://localhost:8003/api/superadmin/register \
  -H "Content-Type: application/json" \
  -d '{
    "full_name": "System Administrator",
    "email": "admin@company.com",
    "password": "SecurePass@2025",
    "phone": "+919123456789"
  }'
```

### 2. Super Admin Login
```bash
curl -X POST http://localhost:8003/api/superadmin/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@company.com",
    "password": "SecurePass@2025"
  }'
```
**Extract the `token` from response for subsequent super admin operations.**

### 3. Verify Super Admin Token
```bash
curl -X GET http://localhost:8003/api/superadmin/verify-token \
  -H "Authorization: Bearer YOUR_SUPERADMIN_TOKEN" \
  -H "Content-Type: application/json"
```

### 4. Get Super Admin Profile
```bash
curl -X GET http://localhost:8003/api/superadmin/me \
  -H "Authorization: Bearer YOUR_SUPERADMIN_TOKEN" \
  -H "Content-Type: application/json"
```

## Regular User Authentication Flow

## Regular User Authentication Flow

### 1. User Registration (Public)
```bash
curl -X POST http://localhost:8003/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "newstudent@example.com",
    "phone": "+1234567890",
    "first_name": "New",
    "last_name": "Student",
    "role": "student",
    "password": "StudentPass123!",
    "date_of_birth": "2000-01-01",
    "gender": "male",
    "course": {
      "category_id": "cat-martial-arts",
      "course_id": "course-karate-101",
      "duration": "6-months"
    },
    "branch": {
      "location_id": "loc-downtown",
      "branch_id": "branch-main"
    }
  }'
```

### 2. User Login
```bash
curl -X POST http://localhost:8003/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "newstudent@example.com",
    "password": "StudentPass123!"
  }'
```
**Extract the `access_token` from response for subsequent requests.**

### 3. Get Current User Info
```bash
curl -X GET http://localhost:8003/api/auth/me \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json"
```

## Branch Management Examples

### 1. Create Comprehensive Branch (Super Admin Only)
```bash
curl -X POST http://localhost:8003/api/branches \
  -H "Authorization: Bearer YOUR_SUPER_ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "branch": {
      "name": "Elite Martial Arts Academy",
      "code": "EMAA01",
      "email": "elite@martialarts.com",
      "phone": "+1555123456",
      "address": {
        "line1": "789 Warrior Way",
        "area": "Dojo District",
        "city": "Martial City",
        "state": "Combat State",
        "pincode": "54321",
        "country": "India"
      }
    },
    "manager_id": "mgr-john-doe-uuid",
    "operational_details": {
      "courses_offered": ["Karate", "Taekwondo", "Jiu-Jitsu", "Kickboxing"],
      "timings": [
        {"day": "Monday", "open": "06:00", "close": "22:00"},
        {"day": "Tuesday", "open": "06:00", "close": "22:00"},
        {"day": "Wednesday", "open": "06:00", "close": "22:00"},
        {"day": "Thursday", "open": "06:00", "close": "22:00"},
        {"day": "Friday", "open": "06:00", "close": "22:00"},
        {"day": "Saturday", "open": "08:00", "close": "20:00"},
        {"day": "Sunday", "open": "08:00", "close": "18:00"}
      ],
      "holidays": ["2025-01-01", "2025-08-15", "2025-10-02", "2025-12-25"]
    },
    "assignments": {
      "accessories_available": true,
      "courses": [
        "course-karate-uuid",
        "course-taekwondo-uuid", 
        "course-jiujitsu-uuid",
        "course-kickboxing-uuid"
      ],
      "branch_admins": [
        "admin-sarah-uuid",
        "admin-mike-uuid"
      ]
    },
    "bank_details": {
      "bank_name": "First National Bank",
      "account_number": "9876543210",
      "upi_id": "elite@okaxis"
    }
  }'
```

### 2. Get All Branches
```bash
curl -X GET http://localhost:8003/api/branches \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json"
```

### 3. Get Specific Branch
```bash
curl -X GET http://localhost:8003/api/branches/BRANCH_ID \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json"
```

## Course Management Examples

### 1. Create Comprehensive Course (Super Admin Only)
```bash
curl -X POST http://localhost:8003/api/courses \
  -H "Authorization: Bearer YOUR_SUPER_ADMIN_TOKEN" \
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

### 2. Get All Courses
```bash
curl -X GET http://localhost:8003/api/courses \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json"
```

### 3. Get Specific Course
```bash
curl -X GET http://localhost:8003/api/courses/COURSE_ID \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json"
```

### 4. Filter Courses
```bash
# Filter by difficulty level
curl -X GET "http://localhost:8003/api/courses?difficulty_level=Advanced" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json"

# Filter by category and instructor
curl -X GET "http://localhost:8003/api/courses?category_id=cat-uuid&instructor_id=instructor-uuid" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json"
```

## User Management Examples

### 1. Create New Coach with Nested Structure (Admin Only)
```bash
curl -X POST http://localhost:8003/api/users/coaches \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "personal_info": {
      "first_name": "Ravi",
      "last_name": "Kumar",
      "gender": "Male",
      "date_of_birth": "1985-06-15"
    },
    "contact_info": {
      "email": "ravi.kumar@martialarts.com",
      "country_code": "+91",
      "phone": "9876543210",
      "password": "SecurePassword@123"
    },
    "address_info": {
      "address": "123 MG Road",
      "area": "Indiranagar",
      "city": "Bengaluru",
      "state": "Karnataka",
      "zip_code": "560038",
      "country": "India"
    },
    "professional_info": {
      "education_qualification": "Bachelor of Physical Education",
      "professional_experience": "5+ years in martial arts training",
      "designation_id": "senior-instructor-001",
      "certifications": [
        "Black Belt in Karate",
        "Certified Fitness Trainer",
        "Sports Injury Prevention Certificate"
      ]
    },
    "areas_of_expertise": [
      "Taekwondo",
      "Karate",
      "Kung Fu",
      "Mixed Martial Arts",
      "Self Defense"
    ]
  }'
```

### 2. Get All Users (Admin Only)
```bash
curl -X GET http://localhost:8003/api/users \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN" \
  -H "Content-Type: application/json"
```

### 3. Create New User (Admin Only)
```bash
curl -X POST http://localhost:8003/api/users \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "newcoach@example.com",
    "phone": "+1234567890",
    "first_name": "New",
    "last_name": "Coach",
    "role": "coach",
    "date_of_birth": "1985-05-15",
    "gender": "female"
  }'
```

## Common Response Patterns

### Success Response Format
```json
{
  "message": "Operation completed successfully",
  "data": { /* relevant data */ }
}
```

### Error Response Format
```json
{
  "detail": "Error description or validation errors array"
}
```

### Nested Data Structure Example
```json
{
  "user": {
    "id": "user-uuid",
    "email": "user@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "course": {
      "category_id": "cat-uuid",
      "course_id": "course-uuid", 
      "duration": "6-months"
    },
    "branch": {
      "location_id": "loc-uuid",
      "branch_id": "branch-uuid"
    }
  }
}
```

## Testing Tools & Resources

### Python Test Scripts
```bash
# Super Admin authentication testing
python test_superadmin_api.py

# Comprehensive authentication testing
python test_auth_bearer.py

# Step-by-step authentication guide
python simple_auth_test.py

# Test complete branch API functionality
python test_complete_branch_api.py

# Test comprehensive course API functionality
python test_course_creation.py
```

### Postman Collection
Import `Student_Management_API_Bearer_Auth.postman_collection.json` into Postman for GUI testing with automatic token management.

### Demo Credentials
- **Super Admin**: `superadmin@example.com` / `StrongPassword@123` (via Super Admin API)
- **Regular Super Admin**: `superadmin@test.com` / `SuperAdmin123!` (via regular auth API)
- **Test Users**: Created via registration endpoint

### API Features Summary
- ✅ **JWT Bearer Token Authentication**
- ✅ **Role-Based Access Control** (Super Admin, Coach Admin, Coach, Student)
- ✅ **Nested Data Structures** (User courses/branches, Branch comprehensive details)
- ✅ **Comprehensive Branch Management** (Address, Operations, Assignments, Banking)
- ✅ **Secure Endpoints** (All protected routes require authentication)
- ✅ **Consistent Data Storage** (Nested structures preserved in database)
- ✅ **RESTful Design** (Standard HTTP methods and status codes)
- ✅ **Separate Coach Management** (Dedicated coaches collection and endpoints)
- ✅ **Comprehensive Error Handling** (Detailed error responses and status codes)
- ✅ **Data Validation** (Pydantic models with comprehensive validation)
- ✅ **Rate Limiting** (Protection against abuse)
- ✅ **CORS Support** (Cross-origin resource sharing)

## Troubleshooting

### Common Issues

**1. Server Won't Start**
```bash
# Check Python version (requires 3.7+)
python --version

# Install dependencies
pip install -r requirements.txt

# Check port availability
netstat -an | findstr :8001  # Windows
lsof -i :8001  # Linux/macOS
```

**2. Authentication Issues**
```bash
# Test token validity
curl -X GET "http://localhost:8003/api/auth/me" \
  -H "Authorization: Bearer YOUR_TOKEN"

# Expected response: User profile (200 OK)
# If 401: Token expired or invalid
```

**3. Database Connection Issues**
```bash
# Check MongoDB connection
# Verify database configuration in utils/database.py
# Ensure MongoDB is running locally or connection string is correct
```

**4. CORS Issues**
```javascript
// Frontend JavaScript example
fetch('http://localhost:8003/api/coaches', {
  method: 'GET',
  headers: {
    'Authorization': 'Bearer ' + token,
    'Content-Type': 'application/json',
  },
})
.then(response => response.json())
.then(data => console.log(data));
```

**5. Validation Errors**
- **Check Required Fields**: All nested objects must have required fields
- **Email Format**: Must be valid email address
- **Date Format**: Use YYYY-MM-DD format
- **Phone Format**: Country code + phone number

### Support
- **API Documentation**: `http://localhost:8003/docs` (Swagger UI)
- **Alternative Docs**: `http://localhost:8003/redoc` (ReDoc)
- **OpenAPI Schema**: `http://localhost:8003/openapi.json`

### Version Information
- **API Version**: 1.0
- **FastAPI Version**: Latest
- **Python Version**: 3.7+
- **Database**: MongoDB
- **Authentication**: JWT Bearer Tokens

---

**Last Updated**: January 2025  
**Documentation Version**: 2.0  
**API Status**: ✅ Active and Stable

