# Branch Manager API Documentation

## Overview
The Branch Manager API provides comprehensive functionality for managing branch managers in the Marshalats Learning Management System. It supports complete CRUD operations with nested data structures for personal information, professional details, branch assignments, and emergency contacts.

## Base URL
```
Development: http://localhost:8003/api/branch-managers
Production: https://edumanage-44.preview.dev.com/api/branch-managers
```

## Authentication
Most endpoints require authentication via Bearer token in the Authorization header:
```
Authorization: Bearer <jwt_token>
```

### Getting Authentication Token
To get a superadmin token for branch manager management:
```bash
curl -X POST "http://localhost:8003/api/superadmin/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "pittisunilkumar3@gmail.com",
    "password": "StrongPassword@123"
  }'
```

## Data Models

### BranchManagerCreate
```json
{
  "personal_info": {
    "first_name": "string",
    "last_name": "string", 
    "gender": "male|female|other",
    "date_of_birth": "YYYY-MM-DD"
  },
  "contact_info": {
    "email": "user@example.com",
    "country_code": "+91",
    "phone": "string",
    "password": "string"
  },
  "address_info": {
    "address": "string",
    "area": "string", 
    "city": "string",
    "state": "string",
    "zip_code": "string",
    "country": "India"
  },
  "professional_info": {
    "designation": "string",
    "education_qualification": "string",
    "professional_experience": "string",
    "certifications": ["string"]
  },
  "branch_id": "string",
  "emergency_contact": {
    "name": "string",
    "phone": "string", 
    "relationship": "string"
  },
  "notes": "string"
}
```

### BranchManagerResponse
```json
{
  "id": "string",
  "personal_info": { /* PersonalInfo */ },
  "contact_info": { /* ContactInfo without password */ },
  "address_info": { /* AddressInfo */ },
  "professional_info": { /* ProfessionalInfo */ },
  "branch_assignment": {
    "branch_id": "string",
    "branch_name": "string",
    "branch_location": "string"
  },
  "emergency_contact": { /* EmergencyContact */ },
  "full_name": "string",
  "is_active": true,
  "notes": "string",
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

## API Endpoints

### 1. Create Branch Manager
**POST** `/api/branch-managers`

Creates a new branch manager with comprehensive nested structure.

**Authentication:** Super Admin required

**Request Body:** BranchManagerCreate

**Example:**
```bash
curl -X POST "http://localhost:8003/api/branch-managers" \
  -H "Authorization: Bearer <super_admin_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "personal_info": {
      "first_name": "John",
      "last_name": "Smith",
      "gender": "male",
      "date_of_birth": "1985-06-15"
    },
    "contact_info": {
      "email": "john.smith@example.com",
      "country_code": "+91",
      "phone": "9876543210",
      "password": "SecurePass@123"
    },
    "address_info": {
      "address": "123 Main Street",
      "area": "Downtown",
      "city": "Mumbai",
      "state": "Maharashtra", 
      "zip_code": "400001",
      "country": "India"
    },
    "professional_info": {
      "designation": "Branch Manager",
      "education_qualification": "MBA in Operations",
      "professional_experience": "5-10 years",
      "certifications": ["Operations Management", "Leadership"]
    },
    "branch_id": "branch-uuid-here",
    "emergency_contact": {
      "name": "Jane Smith",
      "phone": "9876543211",
      "relationship": "spouse"
    },
    "notes": "Experienced manager with strong leadership skills"
  }'
```

**Response:**
```json
{
  "message": "Branch manager created successfully",
  "branch_manager": {
    "id": "manager-uuid",
    "full_name": "John Smith",
    "email": "john.smith@example.com",
    "branch_assignment": {
      "branch_id": "branch-uuid",
      "branch_name": "Downtown Branch",
      "branch_location": "Mumbai, Maharashtra"
    }
  }
}
```

### 2. Get All Branch Managers
**GET** `/api/branch-managers`

Retrieves a paginated list of branch managers.

**Authentication:** Super Admin required

**Query Parameters:**
- `skip` (int, default: 0): Number of records to skip
- `limit` (int, default: 50, max: 100): Number of records to return
- `active_only` (bool, default: true): Filter only active managers

**Example:**
```bash
curl -X GET "http://localhost:8003/api/branch-managers?skip=0&limit=10&active_only=true" \
  -H "Authorization: Bearer <super_admin_token>"
```

**Response:**
```json
{
  "branch_managers": [
    {
      "id": "manager-uuid",
      "personal_info": { /* PersonalInfo */ },
      "contact_info": { /* ContactInfo */ },
      "address_info": { /* AddressInfo */ },
      "professional_info": { /* ProfessionalInfo */ },
      "branch_assignment": { /* BranchAssignment */ },
      "emergency_contact": { /* EmergencyContact */ },
      "full_name": "John Smith",
      "is_active": true,
      "notes": "string",
      "created_at": "2024-01-01T00:00:00Z",
      "updated_at": "2024-01-01T00:00:00Z"
    }
  ],
  "total_count": 25,
  "skip": 0,
  "limit": 10
}
```

### 3. Get Branch Manager by ID
**GET** `/api/branch-managers/{manager_id}`

Retrieves a specific branch manager by ID.

**Authentication:** Super Admin or Branch Manager required

**Example:**
```bash
curl -X GET "http://localhost:8003/api/branch-managers/manager-uuid" \
  -H "Authorization: Bearer <token>"
```

**Response:** BranchManagerResponse object

### 4. Update Branch Manager
**PUT** `/api/branch-managers/{manager_id}`

Updates an existing branch manager.

**Authentication:** Super Admin required

**Request Body:** BranchManagerUpdate (all fields optional)

**Example:**
```bash
curl -X PUT "http://localhost:8003/api/branch-managers/manager-uuid" \
  -H "Authorization: Bearer <super_admin_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "personal_info": {
      "first_name": "John",
      "last_name": "Smith Updated"
    },
    "professional_info": {
      "designation": "Senior Branch Manager"
    }
  }'
```

**Response:**
```json
{
  "message": "Branch manager updated successfully",
  "branch_manager": { /* Updated BranchManagerResponse */ }
}
```

### 5. Delete Branch Manager
**DELETE** `/api/branch-managers/{manager_id}`

Deletes a branch manager.

**Authentication:** Super Admin required

**Example:**
```bash
curl -X DELETE "http://localhost:8003/api/branch-managers/manager-uuid" \
  -H "Authorization: Bearer <super_admin_token>"
```

**Response:**
```json
{
  "message": "Branch manager deleted successfully"
}
```

### 6. Send Credentials Email
**POST** `/api/branch-managers/{manager_id}/send-credentials`

Sends login credentials to branch manager via email with secure password reset token.

**Authentication:** Super Admin required

**Example:**
```bash
curl -X POST "http://localhost:8003/api/branch-managers/manager-uuid/send-credentials" \
  -H "Authorization: Bearer <super_admin_token>"
```

**Response:**
```json
{
  "message": "Login credentials sent successfully to branch manager's email",
  "email": "john.smith@example.com"
}
```

### 7. Get Current Branch Manager Profile
**GET** `/api/branch-managers/me`

Gets the current authenticated branch manager's profile.

**Authentication:** Branch Manager required

**Example:**
```bash
curl -X GET "http://localhost:8003/api/branch-managers/me" \
  -H "Authorization: Bearer <branch_manager_token>"
```

**Response:**
```json
{
  "branch_manager": { /* BranchManagerResponse without sensitive data */ }
}
```

## Error Responses

### 400 Bad Request
```json
{
  "detail": "Branch manager with this email or phone already exists"
}
```

### 401 Unauthorized
```json
{
  "detail": "Not authenticated"
}
```

### 403 Forbidden
```json
{
  "detail": "Not enough permissions"
}
```

### 404 Not Found
```json
{
  "detail": "Branch manager not found"
}
```

### 422 Validation Error
```json
{
  "detail": [
    {
      "loc": ["body", "personal_info", "first_name"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

## Features

### Security Features
- Password hashing using bcrypt
- JWT token-based authentication
- Role-based access control
- Secure password reset tokens with expiry
- Email/phone uniqueness validation

### Data Management
- Comprehensive nested data structures
- Automatic full name generation
- Branch assignment with location details
- Emergency contact management
- Professional information tracking
- Activity logging for audit trails

### Email Integration
- Automated credential sending via email
- HTML and plain text email templates
- Secure password reset links
- 24-hour token expiry for security

### Validation
- Email format validation
- Phone number validation
- Date format validation (YYYY-MM-DD)
- Password strength requirements
- Required field validation

## Testing

### Test Branch Manager Creation
```bash
# 1. Get superadmin token
TOKEN=$(curl -s -X POST "http://localhost:8003/api/superadmin/login" \
  -H "Content-Type: application/json" \
  -d '{"email": "pittisunilkumar3@gmail.com", "password": "StrongPassword@123"}' \
  | jq -r '.access_token')

# 2. Create branch manager
curl -X POST "http://localhost:8003/api/branch-managers" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "personal_info": {
      "first_name": "Test",
      "last_name": "Manager",
      "gender": "male"
    },
    "contact_info": {
      "email": "test.manager@example.com",
      "phone": "9876543210",
      "password": "TestPass@123"
    },
    "professional_info": {
      "designation": "Branch Manager",
      "education_qualification": "MBA"
    }
  }'
```

### Test Branch Manager Login
```bash
# Test login with created branch manager
curl -X POST "http://localhost:8003/api/branch-managers/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test.manager@example.com",
    "password": "TestPass@123"
  }'
```

**Expected Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer",
  "branch_manager": {
    "id": "uuid",
    "full_name": "Test Manager",
    "email": "test.manager@example.com",
    "is_active": true
  },
  "expires_in": 86400,
  "message": "Login successful"
}
```

### Frontend Testing
1. Navigate to `http://localhost:3022/branch-manager/login`
2. Enter credentials: `test.manager@example.com` / `TestPass@123`
3. Verify successful login and redirect to dashboard

### Known Issues & Solutions
- **bcrypt Compatibility:** If you encounter bcrypt `__about__` attribute errors, downgrade bcrypt:
  ```bash
  pip install bcrypt==4.0.1
  ```

## Authentication Endpoints

### 8. Branch Manager Login
**POST** `/api/branch-managers/login`

Authenticates a branch manager and returns a JWT token.

**Authentication:** None required (public endpoint)

**Request Body:** BranchManagerLogin
```json
{
  "email": "manager@example.com",
  "password": "password123"
}
```

**Example:**
```bash
curl -X POST "http://localhost:8003/api/branch-managers/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test.manager@example.com",
    "password": "TestPass@123"
  }'
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "branch_manager": {
    "id": "manager-uuid",
    "personal_info": {
      "first_name": "John",
      "last_name": "Smith",
      "gender": "male",
      "date_of_birth": "1985-06-15"
    },
    "contact_info": {
      "email": "test.manager@example.com",
      "country_code": "+91",
      "phone": "9876543210"
    },
    "address_info": { /* AddressInfo */ },
    "professional_info": { /* ProfessionalInfo */ },
    "branch_assignment": {
      "branch_id": "branch-uuid",
      "branch_name": "Downtown Branch",
      "branch_location": "Mumbai, Maharashtra"
    },
    "emergency_contact": { /* EmergencyContact */ },
    "full_name": "John Smith",
    "is_active": true,
    "notes": "string",
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-01-01T00:00:00Z"
  },
  "expires_in": 86400,
  "message": "Login successful"
}
```

### Additional Authentication Endpoints (Planned)

The following authentication endpoints are planned for future implementation:

- **POST** `/api/branch-managers/forgot-password` - Initiate password reset
- **POST** `/api/branch-managers/reset-password` - Reset password with token

## Implementation Status

### ✅ Fully Implemented and Tested
- **POST** `/api/branch-managers` - Create branch manager
- **GET** `/api/branch-managers` - Get all branch managers with pagination
- **GET** `/api/branch-managers/{manager_id}` - Get specific branch manager
- **PUT** `/api/branch-managers/{manager_id}` - Update branch manager
- **DELETE** `/api/branch-managers/{manager_id}` - Delete branch manager
- **POST** `/api/branch-managers/{manager_id}/send-credentials` - Send credentials email
- **GET** `/api/branch-managers/me` - Get current manager profile
- **POST** `/api/branch-managers/login` - Branch manager authentication

### 🔄 Planned for Future Implementation
- Password reset functionality (forgot password flow)
- Enhanced branch manager dashboard features

## Frontend Integration

### Branch Manager Creation
The branch manager creation form is fully integrated with the backend API:
- **Frontend Path:** `/dashboard/branch-managers/create`
- **Form Validation:** Client-side validation with error handling
- **API Integration:** Complete form data mapping to backend models
- **Success Handling:** Success popup with credential sending option
- **Error Handling:** Comprehensive error messages and user feedback

### Branch Manager Login
The branch manager login system is fully implemented:
- **Frontend Path:** `/branch-manager/login`
- **Authentication:** JWT token-based authentication
- **API Integration:** Real-time login with backend validation
- **Session Management:** Secure token storage and expiration handling
- **Error Handling:** Comprehensive validation and user feedback
- **Redirect Logic:** Automatic redirect to dashboard upon successful login

## Database Schema

Branch managers are stored in the `branch_managers` collection with the following structure:

```json
{
  "_id": "ObjectId",
  "id": "uuid-string",
  "personal_info": {
    "first_name": "string",
    "last_name": "string",
    "gender": "string",
    "date_of_birth": "YYYY-MM-DD"
  },
  "contact_info": {
    "email": "string",
    "country_code": "string",
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
    "designation": "string",
    "education_qualification": "string",
    "professional_experience": "string",
    "certifications": ["string"]
  },
  "branch_assignment": {
    "branch_id": "string",
    "branch_name": "string",
    "branch_location": "string"
  },
  "emergency_contact": {
    "name": "string",
    "phone": "string",
    "relationship": "string"
  },
  "email": "string",
  "phone": "string",
  "first_name": "string",
  "last_name": "string",
  "full_name": "string",
  "password_hash": "string",
  "is_active": true,
  "notes": "string",
  "created_at": "ISODate",
  "updated_at": "ISODate",
  "reset_token": "string",
  "reset_token_expiry": "ISODate"
}
```

## Notes

- All timestamps are in UTC format
- Password fields are never returned in API responses
- Branch assignment automatically populates branch name and location
- Emergency contact information is optional but recommended
- Activity logging tracks all create/update/delete operations
- Email service integration requires proper webhook configuration
- All APIs are fully tested and working in development environment
- Frontend form is completely integrated and functional
