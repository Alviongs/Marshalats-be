# Additional APIs Documentation

## Overview
This document covers the remaining specialized APIs in the Marshalats Learning Management System: Enrollments, Payments, Events, and Requests. These APIs provide essential functionality for student enrollment management, payment processing, event management, and student request handling.

## Base URLs
```
Development: http://localhost:8003/api
Production: https://edumanage-44.preview.dev.com/api
```

## Authentication
All endpoints require authentication via Bearer token in the Authorization header:
```
Authorization: Bearer <jwt_token>
```

---

## Enrollment Management API

### Base URL: `/api/enrollments`

### POST /api/enrollments
Create a new student enrollment (Admin only).

**Authentication:** Required
**Permissions:** Super Admin, Coach Admin

**Request Body:**
```json
{
  "student_id": "student-uuid-here",
  "course_id": "course-uuid-here",
  "branch_id": "branch-uuid-here",
  "start_date": "2024-02-01T00:00:00Z",
  "fee_amount": 299.99,
  "admission_fee": 500.0
}
```

**Response (201 Created):**
```json
{
  "message": "Enrollment created successfully",
  "enrollment": {
    "id": "enrollment-uuid-here",
    "student_id": "student-uuid-here",
    "course_id": "course-uuid-here",
    "branch_id": "branch-uuid-here",
    "enrollment_date": "2024-01-20T10:30:00Z",
    "start_date": "2024-02-01T00:00:00Z",
    "end_date": "2024-08-01T00:00:00Z",
    "fee_amount": 299.99,
    "admission_fee": 500.0,
    "payment_status": "pending",
    "is_active": true
  }
}
```

### GET /api/enrollments
Retrieve enrollments with filtering options.

**Authentication:** Required
**Permissions:** All authenticated users

**Query Parameters:**
- `student_id` (optional): Filter by student ID
- `course_id` (optional): Filter by course ID
- `branch_id` (optional): Filter by branch ID
- `skip` (optional, default: 0): Pagination offset
- `limit` (optional, default: 50): Number of results

**Response (200 OK):**
```json
{
  "enrollments": [
    {
      "id": "enrollment-uuid-here",
      "student_id": "student-uuid-here",
      "course_id": "course-uuid-here",
      "branch_id": "branch-uuid-here",
      "enrollment_date": "2024-01-20T10:30:00Z",
      "start_date": "2024-02-01T00:00:00Z",
      "end_date": "2024-08-01T00:00:00Z",
      "fee_amount": 299.99,
      "admission_fee": 500.0,
      "payment_status": "pending",
      "next_due_date": "2024-03-01T00:00:00Z",
      "is_active": true
    }
  ]
}
```

### GET /api/enrollments/students/{student_id}/courses
Get all courses for a specific student.

**Authentication:** Required
**Permissions:** All authenticated users

**Response (200 OK):**
```json
{
  "student_courses": [
    {
      "enrollment_id": "enrollment-uuid-here",
      "course": {
        "id": "course-uuid-here",
        "title": "Advanced Karate",
        "code": "KAR-ADV-001",
        "difficulty_level": "Advanced"
      },
      "branch": {
        "id": "branch-uuid-here",
        "name": "Downtown Dojo"
      },
      "enrollment_date": "2024-01-20T10:30:00Z",
      "start_date": "2024-02-01T00:00:00Z",
      "payment_status": "pending",
      "is_active": true
    }
  ]
}
```

### POST /api/enrollments/students/enroll
Allow students to self-enroll in courses.

**Authentication:** Required
**Permissions:** Student only

**Request Body:**
```json
{
  "course_id": "course-uuid-here",
  "branch_id": "branch-uuid-here",
  "start_date": "2024-02-01T00:00:00Z"
}
```

**Response (201 Created):**
```json
{
  "message": "Successfully enrolled in course",
  "enrollment": {
    "id": "enrollment-uuid-here",
    "course_id": "course-uuid-here",
    "branch_id": "branch-uuid-here",
    "start_date": "2024-02-01T00:00:00Z",
    "fee_amount": 299.99,
    "admission_fee": 500.0,
    "payment_status": "pending"
  }
}
```

---

## Payment Management API

### Base URL: `/api/payments`

### POST /api/payments/students/payments
Process student payment.

**Authentication:** Required
**Permissions:** Student only

**Request Body:**
```json
{
  "enrollment_id": "enrollment-uuid-here",
  "amount": 299.99,
  "payment_method": "credit_card",
  "payment_type": "monthly_fee",
  "transaction_id": "txn_1234567890"
}
```

**Response (201 Created):**
```json
{
  "message": "Payment processed successfully",
  "payment": {
    "id": "payment-uuid-here",
    "student_id": "student-uuid-here",
    "enrollment_id": "enrollment-uuid-here",
    "amount": 299.99,
    "payment_type": "monthly_fee",
    "payment_method": "credit_card",
    "payment_status": "paid",
    "transaction_id": "txn_1234567890",
    "payment_date": "2024-01-20T10:30:00Z"
  }
}
```

---

## Event Management API

### Base URL: `/api/events`

### POST /api/events
Create a new event.

**Authentication:** Required
**Permissions:** Super Admin, Coach Admin

**Request Body:**
```json
{
  "title": "Annual Tournament",
  "description": "Annual martial arts tournament for all students",
  "event_type": "tournament",
  "branch_id": "branch-uuid-here",
  "start_date": "2024-06-15T09:00:00Z",
  "end_date": "2024-06-15T18:00:00Z",
  "location": "Main Arena",
  "max_participants": 100,
  "registration_fee": 50.0,
  "is_public": true
}
```

**Response (201 Created):**
```json
{
  "message": "Event created successfully",
  "event": {
    "id": "event-uuid-here",
    "title": "Annual Tournament",
    "description": "Annual martial arts tournament for all students",
    "event_type": "tournament",
    "branch_id": "branch-uuid-here",
    "start_date": "2024-06-15T09:00:00Z",
    "end_date": "2024-06-15T18:00:00Z",
    "location": "Main Arena",
    "max_participants": 100,
    "registration_fee": 50.0,
    "is_public": true,
    "is_active": true,
    "created_at": "2024-01-20T10:30:00Z"
  }
}
```

### GET /api/events
Retrieve events for a specific branch.

**Authentication:** Required
**Permissions:** All authenticated users

**Query Parameters:**
- `branch_id` (required): Branch ID to filter events

**Response (200 OK):**
```json
{
  "events": [
    {
      "id": "event-uuid-here",
      "title": "Annual Tournament",
      "description": "Annual martial arts tournament for all students",
      "event_type": "tournament",
      "branch_id": "branch-uuid-here",
      "start_date": "2024-06-15T09:00:00Z",
end_date": "2024-06-15T18:00:00Z",
      "location": "Main Arena",
      "max_participants": 100,
      "current_participants": 25,
      "registration_fee": 50.0,
      "is_public": true,
      "is_active": true
    }
  ]
}
```

---

## Request Management API

### Base URL: `/api/requests`

### POST /api/requests/transfer
Create a branch transfer request.

**Authentication:** Required
**Permissions:** Student only

**Request Body:**
```json
{
  "current_branch_id": "current-branch-uuid",
  "target_branch_id": "target-branch-uuid",
  "reason": "Moving to new location, need closer branch",
  "preferred_transfer_date": "2024-03-01T00:00:00Z"
}
```

**Response (201 Created):**
```json
{
  "message": "Transfer request created successfully",
  "request": {
    "id": "request-uuid-here",
    "student_id": "student-uuid-here",
    "current_branch_id": "current-branch-uuid",
    "target_branch_id": "target-branch-uuid",
    "reason": "Moving to new location, need closer branch",
    "status": "pending",
    "created_at": "2024-01-20T10:30:00Z"
  }
}
```

### GET /api/requests/transfer
Retrieve transfer request status.

**Authentication:** Required
**Permissions:** Super Admin, Coach Admin

**Query Parameters:**
- `status` (optional): Filter by request status (pending, approved, rejected)

**Response (200 OK):**
```json
{
  "transfer_requests": [
    {
      "id": "request-uuid-here",
      "student_id": "student-uuid-here",
      "student_name": "John Doe",
      "current_branch_id": "current-branch-uuid",
      "target_branch_id": "target-branch-uuid",
      "reason": "Moving to new location, need closer branch",
      "status": "pending",
      "created_at": "2024-01-20T10:30:00Z"
    }
  ]
}
```

### PUT /api/requests/transfer/{request_id}
Update transfer request status.

**Authentication:** Required
**Permissions:** Super Admin, Coach Admin

**Request Body:**
```json
{
  "status": "approved",
  "admin_notes": "Transfer approved. Student can start at new branch from March 1st."
}
```

**Response (200 OK):**
```json
{
  "message": "Transfer request updated successfully",
  "request": {
    "id": "request-uuid-here",
    "status": "approved",
    "admin_notes": "Transfer approved. Student can start at new branch from March 1st.",
    "updated_at": "2024-01-22T14:30:00Z"
  }
}
```

### POST /api/requests/course-change
Create a course change request.

**Authentication:** Required
**Permissions:** Student only

**Request Body:**
```json
{
  "current_enrollment_id": "enrollment-uuid-here",
  "new_course_id": "new-course-uuid-here",
  "reason": "Want to switch to advanced level course"
}
```

**Response (201 Created):**
```json
{
  "message": "Course change request created successfully",
  "request": {
dateTime": "request-uuid-here",
    "student_id": "student-uuid-here",
    "current_enrollment_id": "enrollment-uuid-atedhere",
    "new_course_id": "new-course-uuid-here",
    "reason": "Want to switch to advanced level course",
    "status": "pending",
    "created_at": "2024-01-20T10:30:00Z"
  }

  }
}
```

### GET /api/requests/course-change
Retrieve course change requests.

**Authentication:** Required
**Permissions:** Super Admin, Coach Admin

**Query Parameters:**
- `status` (optional): Filter by request status

**Response (200 OK):**
```json
{
  "course_change_requests": [
    {
      "id": "request-uuid-here",
      "student_id": "student-uuid-here",
      "student_name": "Jane Smith",
      "current_course": "Beginner Karate",
      "new_course": "Intermediate Karate",
      "reason": "Want to switch to advanced level course",
      "status": "pending",
      "created_at": "2024-01-20T10:30:00Z"
    }
  ]
}
```

### PUT /api/requests/course-change/{request_id}
Update course change request status.

**Authentication:** Required
**Permissions:** Super Admin, Coach Admin

**Request Body:**
```json
{
  "status": "approved",
  "admin_notes": "Student has demonstrated proficiency. Course change approved."
}
```

**Response (200 OK):**
```json
{
  "message": "Course change request updated successfully",
  "request": {
    "id": "request-uuid-here",
    "status": "approved",
ateTime": "admin_notes": "Student has demonstrated proficiency. Course change approved.",
    "updated_at": "2024-01-22T14:30:00Z"
  }
}
```

---

## Data Models

### Enrollment Object
```json
{
  "id": "string (UUID)",
  "student_id": "string (UUID)",
  "course_id": "string (UUID)",
  "branch_id": "string (UUID)",
  "enrollment_date": "string (ISO 8601)",
  "start_date": "string (ISO 8601)",
  "end_date": "string ("string (ISO 8601)",
  "fee_amount": "float",
  "admission_fee": "float",
  "payment_status": "string (pending|paid|overdue|cancelled)",
  "next_due_date": "string (ISO 8601)",
  "is_active": "boolean"
}
```

### Payment Object
```json
{
  "id": "string (UUID)",
  "student_id": "string (UUID)",
  "enrollment_id": "string (UUID)",
  "amount": "float",
  "payment_type": "string",
  "payment_method": "string",
  "payment_status": "string (pending|paid|overdue|cancelled)",
  "transaction_id": "string (optional)",
  "payment_date": "string (ISO 8601, optional)",
  "due_date": "string (ISO 8601)",
  "notes": "string (optional)"
}
```

### Event Object
```json
{
  "id": "string (UUID)",
  "title": "string",
  "description": "string",
  "event_type": "string",
  "branch_id": "string (UUID)",
  "start_date": "string (ISO 8601)",
  "end_date": "string (ISO 8601)",
  "location": "string",
  "max_participants": "integer",
  "registration_fee": "float",
  "is_public": "boolean",
  "is_active": "boolean"
}
```

### Request Objects
```json
{
  "id": "string (UUID)",
  "student_id": "string (UUID)",
  "status": "string (pending|approved|rejected)",
  "reason": "string",
  "admin_notes": "string (optional)",
  "created_at": "string (ISO 8601)",
  "updated_at": "string (ISO 8601)"
}
```

---

## Usage Examples

### Enroll Student in Course
```bash
curl -X POST "http://localhost:8003/api/enrollments/students/enroll" \
  -H "Authorization: Bearer <student_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "course_id": "course-uuid-here",
    "branch_id": "branch-uuid-here",
    "start_date": "2024-02-01T00:00:00Z"
  }'
```

### Process Payment
```bash
curl -X POST "http://localhost:8003/api/payments/students/payments" \
  -H "Authorization: Bearer <student_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "enrollment_id": "enrollment-uuid-here",
    "amount": 299.99,
    "payment_method": "credit_card",
    "payment_type": "monthly_fee"
  }'
```

### Create Event
```bash
curl -X POST "http://localhost:8003/api/events" \
  -H "Authorization: Bearer <admin_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Belt Testing",
    "event_type": "examination",
    "branch_id": "branch-uuid-here",
    "start_date": "2024-05-15T10:00:00Z",
    "end_date": "2024-05-15T16:00:00Z"
  }'
```

### Submit Transfer Request
```bash
curl -X POST "http://localhost:8003/api/requests/transfer" \
  -H "Authorization: Bearer <student_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "current_branch_id": "current-branch-uuid",
    "target_branch_id": "target-branch-uuid",
    "reason": "Relocating to new area"
  }'
```

---

## Integration Notes

### Enrollment Integration
- Automatically creates payment records upon enrollment
- Calculates course end dates based on duration
- Validates student, course, and branch existence
- Supports both admin-created and self-enrollments

### Payment Integration
- Links to enrollment records
- Supports multiple payment methods
- Tracks payment status and due dates
- Handles payment proof submission

### Event Integration
- Branch-specific event management
- Participant registration and limits
- Public and private event types
- Integration with calendar systems

### Request Integration
- Student-initiated requests for changes
- Admin approval workflow
- Status tracking and notifications
- Audit trail for all request changes
