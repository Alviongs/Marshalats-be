# Marshalats Learning Management System - API Documentation Overview

## Introduction
Welcome to the comprehensive API documentation for the Marshalats Learning Management System. This system provides a complete solution for managing martial arts schools, including student enrollment, course management, instructor coordination, branch operations, and administrative functions.

## System Architecture
The API is built using FastAPI with MongoDB as the database, providing a modern, scalable, and high-performance backend solution for martial arts school management.

### Technology Stack
- **Framework:** FastAPI (Python)
- **Database:** MongoDB with Motor (async driver)
- **Authentication:** JWT (JSON Web Tokens)
- **Authorization:** Role-based access control (RBAC)
- **Documentation:** OpenAPI/Swagger

## Base URLs
```
Development: http://31.97.224.169:8003/api
Production: https://edumanage-44.preview.dev.com/api
```

## Authentication Overview
The system implements dual authentication mechanisms:

### 1. Regular User Authentication (`/api/auth/`)
- **Purpose:** Authentication for students, coaches, coach admins, and regular super admins
- **Token Duration:** 24 hours
- **Roles:** `student`, `coach`, `coach_admin`, `super_admin`

### 2. Superadmin Authentication (`/api/superadmin/`)
- **Purpose:** Dedicated system for superadmin operations with enhanced privileges
- **Token Duration:** 24 hours
- **Role:** `superadmin`

### Authentication Header Format
```
Authorization: Bearer <jwt_token>
```

## User Roles and Permissions

### Role Hierarchy
1. **superadmin** - System administrator with full access across all resources
2. **super_admin** - Administrative user with comprehensive management capabilities
3. **coach_admin** - Branch-level manager with branch-specific administrative rights
4. **coach** - Instructor with course and student management capabilities
5. **student** - End user with personal account and enrollment capabilities

### Permission Matrix
| Resource | Superadmin | Super Admin | Coach Admin | Coach | Student |
|----------|------------|-------------|-------------|-------|---------|
| Users | Full | Full | Branch Only | View Only | Own Profile |
| Coaches | Full | Full | Create/Update | View Only | View Only |
| Branches | Full | Full | Own Branch | View Only | View Only |
| Courses | Full | Full | Instructor Only | View Only | View Active |
| Enrollments | Full | Full | Branch Only | View Only | Own Only |
| Payments | Full | View | View | View | Own Only |
| Events | Full | Full | Branch Only | View Only | View Public |
| Requests | Full | Full | Approve | View | Create Own |

## API Documentation Structure

### [01. Authentication API](./01_Authentication_API.md)
Complete authentication system documentation covering:
- User registration and login
- Superadmin authentication
- Token management and validation
- Password reset functionality
- Profile management

### [02. User Management API](./02_User_Management_API.md)
Comprehensive user management functionality:
- User creation and updates
- Role-based user retrieval
- User deactivation
- Force password reset
- Role-based access control

### [03. Course Management API](./03_Course_Management_API.md)
Course lifecycle management:
- Course creation with nested structures
- Course filtering and search
- Course updates and management
- Course statistics and analytics
- Student requirements and pricing

### [04. Branch Management API](./04_Branch_Management_API.md)
Branch operations and management:
- Branch creation with comprehensive details
- Operational details and timings
- Branch assignments and administration
- Holiday management
- Banking and financial information

### [05. Coach Management API](./05_Coach_Management_API.md)
Coach lifecycle and professional management:
- Coach registration and authentication
- Professional information management
- Areas of expertise tracking
- Coach statistics and analytics
- Performance monitoring

### [06. Superadmin API](./06_Superadmin_API.md)
System administration and oversight:
- Superadmin authentication
- System-wide coach management
- Administrative overrides
- System statistics and monitoring
- Enhanced security features

### [07. Additional APIs](./07_Additional_APIs.md)
Specialized functionality:
- **Enrollment Management:** Student course enrollment and management
- **Payment Processing:** Payment handling and tracking
- **Event Management:** Event creation and participant management
- **Request Management:** Student requests for transfers and course changes

## Quick Start Guide

### 1. Authentication
```bash
# Regular user login
curl -X POST "http://31.97.224.169:8003/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "password"}'

# Superadmin login
curl -X POST "http://31.97.224.169:8003/api/superadmin/login" \
  -H "Content-Type: application/json" \
  -d '{"email": "admin@example.com", "password": "password"}'
```

### 2. Using Tokens
```bash
# Include token in subsequent requests
curl -X GET "http://31.97.224.169:8003/api/users" \
  -H "Authorization: Bearer <your_token_here>"
```

### 3. Common Operations
```bash
# Create a user
curl -X POST "http://31.97.224.169:8003/api/users" \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"full_name": "John Doe", "email": "john@example.com", "role": "student"}'

# Get courses
curl -X GET "http://31.97.224.169:8003/api/courses?active_only=true" \
  -H "Authorization: Bearer <token>"

# Enroll in course
curl -X POST "http://31.97.224.169:8003/api/enrollments/students/enroll" \
  -H "Authorization: Bearer <student_token>" \
  -H "Content-Type: application/json" \
  -d '{"course_id": "course-uuid", "branch_id": "branch-uuid"}'
```

## API Features

### ✅ Comprehensive Functionality
- **JWT Bearer Token Authentication** with role-based access control
- **Nested Data Structures** for complex business entities
- **RESTful Design** with standard HTTP methods and status codes
- **Comprehensive Error Handling** with detailed error responses
- **Data Validation** using Pydantic models
- **Async Operations** for high performance
- **Audit Logging** for security and compliance

### ✅ Business Logic Support
- **Multi-branch Operations** with branch-specific permissions
- **Course Management** with prerequisites and capacity limits
- **Payment Processing** with multiple payment methods
- **Event Management** with registration and capacity tracking
- **Request Workflows** with approval processes
- **Notification Systems** via SMS and WhatsApp

### ✅ Security Features
- **Password Hashing** using bcrypt
- **Token Expiration** for security
- **Role-based Permissions** strictly enforced
- **Input Validation** and sanitization
- **CORS Configuration** for web security
- **Audit Trails** for all operations

## Error Handling

### Standard HTTP Status Codes
- **200 OK** - Request successful
- **201 Created** - Resource created successfully
- **400 Bad Request** - Invalid request data
- **401 Unauthorized** - Authentication required
- **403 Forbidden** - Insufficient permissions
- **404 Not Found** - Resource not found
- **422 Unprocessable Entity** - Validation error
- **500 Internal Server Error** - Server error

### Error Response Format
```json
{
  "detail": "Error description",
  "errors": [
    {
      "field": "field_name",
      "message": "Specific error message"
    }
  ]
}
```

## Rate Limiting and Performance

### Pagination
Most list endpoints support pagination:
- `skip` - Number of items to skip (default: 0)
- `limit` - Number of items to return (default: 50, max: 100)

### Filtering
Many endpoints support filtering by relevant fields:
- `role` - Filter by user role
- `branch_id` - Filter by branch
- `active_only` - Filter active items only
- `difficulty_level` - Filter courses by difficulty

## Development and Testing

### Interactive Documentation
- **Swagger UI:** `http://31.97.224.169:8003/docs`
- **ReDoc:** `http://31.97.224.169:8003/redoc`

### Health Check
```bash
curl -X GET "http://31.97.224.169:8003/health"
```

### Environment Setup
1. Install dependencies: `pip install -r requirements.txt`
2. Set environment variables (MongoDB URL, JWT secret)
3. Start server: `python server.py`
4. Access documentation: `http://31.97.224.169:8003/docs`

## Support and Maintenance

### Logging
All API operations are logged with:
- Request/response details
- User authentication information
- Error tracking and debugging
- Performance metrics

### Monitoring
- Health check endpoints
- Database connection monitoring
- Token validation tracking
- User activity analytics

### Backup and Recovery
- Database backup procedures
- Data migration tools
- System restore capabilities
- Disaster recovery planning

## Integration Guidelines

### Frontend Integration
- Use provided TypeScript interfaces
- Implement proper token storage
- Handle token expiration gracefully
- Follow authentication flows

### Third-party Integration
- Webhook support for external systems
- API key management for integrations
- Data export capabilities
- Real-time notifications

## Conclusion
This API documentation provides comprehensive coverage of all endpoints, data models, authentication mechanisms, and integration patterns for the Marshalats Learning Management System. Each section includes detailed examples, error handling, and best practices for implementation.

For specific implementation details, please refer to the individual API documentation files listed above.
