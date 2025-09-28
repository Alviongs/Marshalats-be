# Superadmin API Documentation

## Overview
The Superadmin API provides dedicated endpoints for system administrators with enhanced privileges in the Marshalats Learning Management System. This API operates independently from the regular user authentication system and provides comprehensive administrative functionality.

## Base URL
```
Development: http://31.97.224.169:8003/api/superadmin
Production: https://edumanage-44.preview.dev.com/api/superadmin
```

## Authentication
All endpoints (except register and login) require authentication via Bearer token in the Authorization header:
```
Authorization: Bearer <superadmin_jwt_token>
```

## Superadmin Privileges
- **System-wide access** - Can manage all resources across all branches
- **User management** - Create, update, and deactivate all user types
- **Coach management** - Full coach lifecycle management
- **Branch management** - Create and manage all branches
- **System statistics** - Access to comprehensive analytics
- **Administrative operations** - System configuration and maintenance

---

## Authentication Endpoints

### POST /superadmin/register
Register a new superadmin (first-time setup or by existing superadmin).

**Authentication:** Not required for first superadmin, required for subsequent registrations
**Permissions:** Public for initial setup, Superadmin for additional registrations

**Request Body:**
```json
{
  "full_name": "System Administrator",
  "email": "admin@marshalats.com",
  "password": "superSecurePassword123"
}
```

**Response (201 Created):**
```json
{
  "message": "Super admin registered successfully",
  "admin": {
    "id": "admin-uuid-here",
    "full_name": "System Administrator",
    "email": "admin@marshalats.com",
    "created_at": "2024-01-20T10:30:00Z"
  }
}
```

### POST /api/superadmin/login
Authenticate superadmin and receive JWT token.

**Authentication:** Not required
**Permissions:** Public endpoint

**Request Body:**
```json
{
  "email": "admin@marshalats.com",
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
    "full_name": "System Administrator",
    "email": "admin@marshalats.com",
    "role": "superadmin"
  }
}
```

### GET /api/superadmin/me
Get current superadmin profile information.

**Authentication:** Required (Superadmin token)
**Permissions:** Superadmin only

**Response (200 OK):**
```json
{
  "status": "success",
  "data": {
    "id": "admin-uuid-here",
    "full_name": "System Administrator",
    "email": "admin@marshalats.com",
    "created_at": "2024-01-20T10:30:00Z"
  }
}
```

### GET /api/superadmin/verify-token
Verify if superadmin token is valid.

**Authentication:** Required (Superadmin token)
**Permissions:** Superadmin only

**Response (200 OK):**
```json
{
  "status": "success",
  "message": "Token is valid",
  "data": {
    "id": "admin-uuid-here",
    "email": "admin@marshalats.com",
    "full_name": "System Administrator"
  }
}
```

---

## Coach Management Endpoints

### POST /api/superadmin/coaches
Create a new coach with comprehensive nested structure.

**Authentication:** Required (Superadmin token)
**Permissions:** Superadmin only

**Request Body:**
```json
{
  "personal_info": {
    "first_name": "Sarah",
    "last_name": "Wilson",
    "gender": "Female",
    "date_of_birth": "1987-05-12"
  },
  "contact_info": {
    "email": "sarah.wilson@example.com",
    "country_code": "+1",
    "phone": "5551112233",
    "password": "temporaryPassword123"
  },
  "address_info": {
    "address": "321 Elm Street",
    "area": "Westside",
    "city": "Chicago",
    "state": "IL",
    "zip_code": "60601",
    "country": "USA"
  },
  "professional_info": {
    "education_qualification": "PhD in Sports Psychology",
    "professional_experience": "15 years martial arts instruction, former Olympic coach",
    "designation_id": "master-instructor",
    "certifications": ["Master Black Belt Taekwondo", "Sports Psychology Certification", "Olympic Coaching License"]
  },
  "areas_of_expertise": ["Taekwondo", "Competition Training", "Sports Psychology", "Elite Athlete Development"]
}
```

**Response (201 Created):**
```json
{
  "message": "Coach created successfully",
  "coach_id": "coach-uuid-here"
}
```

### GET /api/superadmin/coaches
Retrieve all coaches with filtering options.

**Authentication:** Required (Superadmin token)
**Permissions:** Superadmin only

**Query Parameters:**
- `skip` (optional, default: 0): Number of coaches to skip
- `limit` (optional, default: 50): Number of coaches to return
- `active_only` (optional, default: true): Filter active coaches only
- `area_of_expertise` (optional): Filter by expertise area

**Response (200 OK):**
```json
{
  "coaches": [
    {
      "id": "coach-uuid-1",
      "personal_info": {
        "first_name": "Sarah",
        "last_name": "Wilson",
        "gender": "Female",
        "date_of_birth": "1987-05-12"
      },
      "contact_info": {
        "email": "sarah.wilson@example.com",
        "country_code": "+1",
        "phone": "5551112233"
      },
      "professional_info": {
        "education_qualification": "PhD in Sports Psychology",
        "designation_id": "master-instructor",
        "certifications": ["Master Black Belt Taekwondo", "Sports Psychology Certification"]
      },
      "areas_of_expertise": ["Taekwondo", "Competition Training", "Sports Psychology"],
      "full_name": "Sarah Wilson",
      "is_active": true,
      "created_at": "2024-01-20T10:30:00Z"
    }
  ]
}
```

### GET /api/superadmin/coaches/{coach_id}
Retrieve a specific coach by ID.

**Authentication:** Required (Superadmin token)
**Permissions:** Superadmin only

**Path Parameters:**
- `coach_id`: UUID of the coach

**Response (200 OK):**
```json
{
  "coach": {
    "id": "coach-uuid-here",
    "personal_info": {
      "first_name": "Sarah",
      "last_name": "Wilson",
      "gender": "Female",
      "date_of_birth": "1987-05-12"
    },
    "contact_info": {
      "email": "sarah.wilson@example.com",
      "country_code": "+1",
      "phone": "5551112233"
    },
    "address_info": {
      "address": "321 Elm Street",
      "area": "Westside",
      "city": "Chicago",
      "state": "IL",
      "zip_code": "60601",
      "country": "USA"
    },
    "professional_info": {
      "education_qualification": "PhD in Sports Psychology",
      "professional_experience": "15 years martial arts instruction",
      "designation_id": "master-instructor",
      "certifications": ["Master Black Belt Taekwondo", "Sports Psychology Certification"]
    },
    "areas_of_expertise": ["Taekwondo", "Competition Training", "Sports Psychology"],
    "full_name": "Sarah Wilson",
    "is_active": true,
    "created_at": "2024-01-20T10:30:00Z",
    "updated_at": "2024-01-20T10:30:00Z"
  }
}
```

### PUT /api/superadmin/coaches/{coach_id}
Update an existing coach's information.

**Authentication:** Required (Superadmin token)
**Permissions:** Superadmin only

**Path Parameters:**
- `coach_id`: UUID of the coach to update

**Request Body (all fields optional):**
```json
{
  "personal_info": {
    "first_name": "Sarah Updated"
  },
  "professional_info": {
    "certifications": ["Master Black Belt Taekwondo", "Sports Psychology Certification", "Advanced Competition Coaching"]
  },
  "areas_of_expertise": ["Taekwondo", "Competition Training", "Sports Psychology", "Youth Development"]
}
```

**Response (200 OK):**
```json
{
  "message": "Coach updated successfully",
  "coach": {
    "id": "coach-uuid-here",
    "full_name": "Sarah Updated Wilson",
    "updated_at": "2024-01-22T14:30:00Z"
  }
}
```

### DELETE /api/superadmin/coaches/{coach_id}
Deactivate a coach (superadmin override).

**Authentication:** Required (Superadmin token)
**Permissions:** Superadmin only

**Path Parameters:**
- `coach_id`: UUID of the coach to deactivate

**Response (200 OK):**
```json
{
  "message": "Coach deactivated successfully",
  "coach": {
    "id": "coach-uuid-here",
    "full_name": "Sarah Wilson",
    "is_active": false,
    "deactivated_at": "2024-01-22T15:00:00Z",
    "deactivated_by": "admin-uuid-here"
  }
}
```

### GET /api/superadmin/coaches/stats/overview
Get comprehensive coach statistics and analytics.

**Authentication:** Required (Superadmin token)
**Permissions:** Superadmin only

**Response (200 OK):**
```json
{
  "total_coaches": 45,
  "active_coaches": 42,
  "inactive_coaches": 3,
  "expertise_distribution": [
    {"_id": "Karate", "count": 12},
    {"_id": "Taekwondo", "count": 10},
    {"_id": "Kung Fu", "count": 8},
    {"_id": "Self-Defense", "count": 18},
    {"_id": "Youth Training", "count": 25},
    {"_id": "Competition Training", "count": 7},
    {"_id": "Weapons Training", "count": 5}
  ],
  "coaches_by_designation": [
    {"designation": "instructor", "count": 20},
    {"designation": "senior-instructor", "count": 15},
    {"designation": "head-instructor", "count": 8},
    {"designation": "master-instructor", "count": 2}
  ],
  "recent_additions": 5,
  "performance_metrics": {
    "average_experience_years": 8.5,
    "certification_completion_rate": 92.3,
    "student_satisfaction_average": 4.6
  }
}
```

---

## Data Models

### Superadmin Object Structure
```json
{
  "id": "string (UUID)",
  "full_name": "string",
  "email": "string (email format)",
  "role": "string (always 'superadmin')",
  "created_at": "string (ISO 8601)",
  "updated_at": "string (ISO 8601)"
}
```

### Token Payload Structure
```json
{
  "sub": "admin-uuid-here",
  "role": "superadmin",
  "email": "admin@example.com",
  "exp": 1705834800
}
```

---

## Error Responses

### 400 Bad Request
```json
{
  "detail": "Invalid superadmin data",
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
  "detail": "Invalid superadmin credentials"
}
```

### 403 Forbidden
```json
{
  "detail": "Superadmin access required"
}
```

### 404 Not Found
```json
{
  "detail": "Resource not found"
}
```

---

## Usage Examples

### Superadmin Login
```bash
curl -X POST "http://31.97.224.169:8003/api/superadmin/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@marshalats.com",
    "password": "superSecurePassword123"
  }'
```

### Create Coach as Superadmin
```bash
curl -X POST "http://31.97.224.169:8003/api/superadmin/coaches" \
  -H "Authorization: Bearer <superadmin_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "personal_info": {
      "first_name": "Master",
      "last_name": "Chen",
      "gender": "Male",
      "date_of_birth": "1975-08-30"
    },
    "contact_info": {
      "email": "master.chen@example.com",
      "country_code": "+1",
      "phone": "5559998888"
    },
    "areas_of_expertise": ["Kung Fu", "Traditional Weapons", "Philosophy"]
  }'
```

### Get System Statistics
```bash
curl -X GET "http://31.97.224.169:8003/api/superadmin/coaches/stats/overview" \
  -H "Authorization: Bearer <superadmin_token>"
```

### Verify Token
```bash
curl -X GET "http://31.97.224.169:8003/api/superadmin/verify-token" \
  -H "Authorization: Bearer <superadmin_token>"
```

---

## Security Notes

### Enhanced Security Features
- **Separate authentication system** - Independent from regular user authentication
- **Extended token validity** - Longer session times for administrative work
- **Audit logging** - All superadmin actions are logged for security
- **IP restrictions** - Can be configured to limit access by IP address
- **Multi-factor authentication** - Can be enabled for additional security

### Access Control
- **System-wide privileges** - Override all role-based restrictions
- **Cross-branch access** - Can manage resources across all branches
- **Emergency access** - Can access system even during maintenance
- **User impersonation** - Can act on behalf of other users for support

### Best Practices
- **Strong passwords** - Enforce complex password requirements
- **Regular token rotation** - Implement token refresh mechanisms
- **Session monitoring** - Track and monitor all superadmin sessions
- **Backup access** - Maintain multiple superadmin accounts
- **Secure communication** - Always use HTTPS in production

---

## Integration Notes

### Cross-System Integration
- **Unified authentication** - Superadmin tokens work across all API endpoints
- **Override permissions** - Can bypass normal role restrictions
- **System maintenance** - Access during system updates and maintenance
- **Data migration** - Tools for system upgrades and data transfers

### Monitoring and Analytics
- **System health** - Monitor overall system performance
- **User activity** - Track user engagement and system usage
- **Resource utilization** - Monitor system resource consumption
- **Security events** - Track authentication and authorization events
