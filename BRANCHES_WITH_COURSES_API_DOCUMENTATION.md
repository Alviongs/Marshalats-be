# Branches with Courses API Documentation

## Overview

The `/api/branches-with-courses` endpoint provides comprehensive branch and course data for the reports system. This endpoint replaces the frontend mock API with real database integration.

## Endpoint Details

**URL:** `GET /api/branches-with-courses`  
**Authentication:** Bearer token required  
**Content-Type:** `application/json`

## Query Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `branch_id` | string | No | "all" | Filter by specific branch ID, or "all" for all branches |
| `status` | string | No | - | Filter by branch status ("active" or "inactive") |
| `include_inactive` | boolean | No | false | Include inactive branches when no status filter is applied |

## Response Format

```json
{
  "message": "Branches with courses retrieved successfully",
  "branches": [
    {
      "id": "c9ed7bb7-c31e-4b0f-9edf-760b41de9628",
      "branch": {
        "name": "Rock martial arts",
        "code": "RMA01",
        "email": "rma@email.com",
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
      "is_active": true,
      "operational_details": {
        "courses_offered": ["course-id-1", "course-id-2"],
        "timings": [
          {"day": "Monday", "open": "07:00", "close": "19:00"}
        ],
        "holidays": ["2025-10-02", "2025-12-25"]
      },
      "assignments": {
        "accessories_available": true,
        "courses": ["course-uuid-1", "course-uuid-2"],
        "branch_admins": ["coach-uuid-1", "coach-uuid-2"]
      },
      "bank_details": {
        "bank_name": "State Bank of India",
        "account_number": "XXXXXXXXXXXX",
        "upi_id": "name@ybl"
      },
      "statistics": {
        "coach_count": 3,
        "student_count": 45,
        "course_count": 2,
        "active_courses": 2
      },
      "courses": [
        {
          "id": "course-123456",
          "title": "Advanced Kung Fu Training",
          "name": "Advanced Kung Fu Training",
          "code": "KF-ADV-001",
          "description": "A comprehensive course covering advanced Kung Fu techniques.",
          "difficulty_level": "Advanced",
          "pricing": {
            "currency": "INR",
            "amount": 8500,
            "branch_specific_pricing": false
          },
          "student_requirements": {
            "max_students": 20,
            "min_age": 16,
            "max_age": 50,
            "prerequisites": ["Basic Kung Fu"]
          },
          "settings": {
            "active": true,
            "offers_certification": true
          },
          "created_at": "2025-09-14T20:05:32.791Z",
          "updated_at": "2025-09-14T20:05:32.791Z"
        }
      ],
      "created_at": "2025-09-14T20:05:32.791Z",
      "updated_at": "2025-09-14T20:05:32.791Z"
    }
  ],
  "total": 1,
  "summary": {
    "total_branches": 1,
    "total_courses": 2,
    "total_students": 45,
    "total_coaches": 3
  },
  "filters_applied": {
    "branch_id": "all",
    "status": "active",
    "include_inactive": false
  }
}
```

## Error Responses

### 401 Unauthorized
```json
{
  "detail": "Authentication required"
}
```

### 404 Not Found
```json
{
  "detail": "Branch not found with ID: invalid-branch-id"
}
```

### 500 Internal Server Error
```json
{
  "detail": "Internal server error"
}
```

## Usage Examples

### Get All Active Branches
```bash
curl -X GET "http://localhost:8003/api/branches-with-courses" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json"
```

### Get Specific Branch
```bash
curl -X GET "http://localhost:8003/api/branches-with-courses?branch_id=c9ed7bb7-c31e-4b0f-9edf-760b41de9628" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json"
```

### Get All Branches (Including Inactive)
```bash
curl -X GET "http://localhost:8003/api/branches-with-courses?include_inactive=true" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json"
```

### Filter by Status
```bash
curl -X GET "http://localhost:8003/api/branches-with-courses?status=inactive" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json"
```

## Database Integration

### Collections Used
- **branches**: Main branch data
- **courses**: Course details
- **coaches**: Coach assignments and counts
- **enrollments**: Student enrollment data

### Query Optimization
- Efficient filtering at database level
- Aggregated statistics calculation
- Proper indexing on branch IDs and status fields

## Frontend Integration

### TypeScript Interface
```typescript
interface BranchWithCourses {
  id: string
  branch: {
    name: string
    code: string
    email: string
    phone: string
    address: Address
  }
  manager_id: string
  is_active: boolean
  operational_details: OperationalDetails
  assignments: Assignments
  bank_details: BankDetails
  statistics: {
    coach_count: number
    student_count: number
    course_count: number
    active_courses: number
  }
  courses: Course[]
  created_at: string
  updated_at: string
}
```

### Usage in Reports
```typescript
import { fetchBranchesWithCourses } from '@/lib/branchesWithCoursesAPI'

// Get all active branches with courses
const data = await fetchBranchesWithCourses()

// Get specific branch
const branchData = await fetchBranchesWithCourses({ branch_id: 'branch-1' })

// Extract for dropdowns
const branches = extractBranchesForDropdown(data)
const courses = extractCoursesForDropdown(data)
```

## Implementation Files

### Backend Files
- `controllers/branches_with_courses_controller.py` - Main controller logic
- `routes/branches_with_courses_routes.py` - API route definition
- `server.py` - Router registration

### Frontend Files
- `lib/branchesWithCoursesAPI.ts` - Frontend API client
- `app/api/branches-with-courses/route.ts` - Frontend mock API (deprecated)

## Testing

Run the comprehensive test suite:
```bash
cd Marshalats-be
python test_branches_with_courses_api.py
```

### Test Coverage
- ✅ Basic endpoint functionality
- ✅ Branch ID filtering
- ✅ Status filtering
- ✅ Authentication requirement
- ✅ Response structure validation
- ✅ Error handling for invalid inputs

## Performance Considerations

- Database queries are optimized with proper filtering
- Statistics are calculated efficiently using aggregation
- Response size is managed through pagination (can be added if needed)
- Caching can be implemented for frequently accessed data

## Security

- Bearer token authentication required
- Input validation and sanitization
- Proper error handling without exposing sensitive information
- Role-based access control through unified authentication

## Migration Notes

The frontend reports pages have been updated to use this real backend API instead of the mock data. The response structure is identical to ensure seamless integration.

## Future Enhancements

- Add pagination support for large datasets
- Implement caching for improved performance
- Add more granular filtering options
- Support for bulk operations
- Real-time updates via WebSocket connections
