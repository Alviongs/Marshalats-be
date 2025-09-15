from fastapi import HTTPException
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
from utils.database import get_db
from utils.helpers import serialize_doc
from models.user_models import UserRole

class ReportsController:
    @staticmethod
    async def get_financial_reports(
        current_user: dict,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        branch_id: Optional[str] = None,
        session: Optional[str] = None,
        class_filter: Optional[str] = None,
        section: Optional[str] = None,
        fees_type: Optional[str] = None
    ):
        """Get comprehensive financial reports"""
        if not current_user:
            raise HTTPException(status_code=401, detail="Authentication required")

        db = get_db()
        
        # Build filter query based on user role and parameters
        filter_query = {}
        if current_user["role"] == "coach_admin" and current_user.get("branch_id"):
            filter_query["branch_id"] = current_user["branch_id"]
        elif branch_id:
            filter_query["branch_id"] = branch_id
        
        # Add date range filter
        if start_date and end_date:
            filter_query["payment_date"] = {"$gte": start_date, "$lte": end_date}
        elif not start_date and not end_date:
            # Default to current month if no dates provided
            now = datetime.utcnow()
            start_of_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            filter_query["payment_date"] = {"$gte": start_of_month}

        try:
            # Total Balance Fees Statement
            total_balance_pipeline = [
                {"$match": {**filter_query, "payment_status": {"$in": ["paid", "completed"]}}},
                {"$group": {"_id": None, "total": {"$sum": "$amount"}, "count": {"$sum": 1}}}
            ]
            total_balance_result = await db.payments.aggregate(total_balance_pipeline).to_list(1)
            total_balance = total_balance_result[0] if total_balance_result else {"total": 0, "count": 0}

            # Balance Fees Statement (Pending)
            balance_fees_pipeline = [
                {"$match": {**filter_query, "payment_status": "pending"}},
                {"$group": {"_id": None, "total": {"$sum": "$amount"}, "count": {"$sum": 1}}}
            ]
            balance_fees_result = await db.payments.aggregate(balance_fees_pipeline).to_list(1)
            balance_fees = balance_fees_result[0] if balance_fees_result else {"total": 0, "count": 0}

            # Daily Collection Report
            daily_collection_pipeline = [
                {"$match": {**filter_query, "payment_status": {"$in": ["paid", "completed"]}}},
                {"$group": {
                    "_id": {"$dateToString": {"format": "%Y-%m-%d", "date": "$payment_date"}},
                    "total": {"$sum": "$amount"},
                    "count": {"$sum": 1}
                }},
                {"$sort": {"_id": -1}},
                {"$limit": 30}
            ]
            daily_collection = await db.payments.aggregate(daily_collection_pipeline).to_list(30)

            # Type Wise Balance Report (by payment type)
            type_wise_pipeline = [
                {"$match": filter_query},
                {"$group": {
                    "_id": "$payment_type",
                    "total": {"$sum": "$amount"},
                    "count": {"$sum": 1}
                }}
            ]
            type_wise_balance = await db.payments.aggregate(type_wise_pipeline).to_list(10)

            # Fees Statement
            fees_statement_pipeline = [
                {"$match": {**filter_query, "payment_status": {"$in": ["paid", "completed"]}}},
                {"$lookup": {
                    "from": "users",
                    "localField": "student_id",
                    "foreignField": "id",
                    "as": "student_info"
                }},
                {"$unwind": "$student_info"},
                {"$group": {
                    "_id": "$student_info.branch_id",
                    "total": {"$sum": "$amount"},
                    "count": {"$sum": 1}
                }},
                {"$lookup": {
                    "from": "branches",
                    "localField": "_id",
                    "foreignField": "id",
                    "as": "branch_info"
                }},
                {"$unwind": "$branch_info"}
            ]
            fees_statement = await db.payments.aggregate(fees_statement_pipeline).to_list(20)

            # Total Fee Collection Report
            total_fee_collection_pipeline = [
                {"$match": {**filter_query, "payment_status": {"$in": ["paid", "completed"]}}},
                {"$group": {
                    "_id": {"$dateToString": {"format": "%Y-%m", "date": "$payment_date"}},
                    "total": {"$sum": "$amount"},
                    "count": {"$sum": 1}
                }},
                {"$sort": {"_id": -1}},
                {"$limit": 12}
            ]
            total_fee_collection = await db.payments.aggregate(total_fee_collection_pipeline).to_list(12)

            # Other Fees Collection Report
            other_fees_pipeline = [
                {"$match": {**filter_query, "payment_type": {"$ne": "tuition"}}},
                {"$group": {
                    "_id": "$payment_type",
                    "total": {"$sum": "$amount"},
                    "count": {"$sum": 1}
                }}
            ]
            other_fees_collection = await db.payments.aggregate(other_fees_pipeline).to_list(10)

            # Online Fees Collection Report
            online_fees_pipeline = [
                {"$match": {**filter_query, "payment_method": "online"}},
                {"$group": {
                    "_id": {"$dateToString": {"format": "%Y-%m-%d", "date": "$payment_date"}},
                    "total": {"$sum": "$amount"},
                    "count": {"$sum": 1}
                }},
                {"$sort": {"_id": -1}},
                {"$limit": 30}
            ]
            online_fees_collection = await db.payments.aggregate(online_fees_pipeline).to_list(30)

            # Balance Fees Report With Remark
            balance_fees_remark_pipeline = [
                {"$match": {**filter_query, "payment_status": "pending"}},
                {"$lookup": {
                    "from": "users",
                    "localField": "student_id",
                    "foreignField": "id",
                    "as": "student_info"
                }},
                {"$unwind": "$student_info"},
                {"$project": {
                    "amount": 1,
                    "due_date": 1,
                    "notes": 1,
                    "student_name": "$student_info.full_name",
                    "student_email": "$student_info.email"
                }},
                {"$limit": 100}
            ]
            balance_fees_remark = await db.payments.aggregate(balance_fees_remark_pipeline).to_list(100)

            return {
                "financial_reports": {
                    "total_balance_fees_statement": {
                        "total_amount": total_balance["total"],
                        "total_transactions": total_balance["count"]
                    },
                    "balance_fees_statement": {
                        "pending_amount": balance_fees["total"],
                        "pending_transactions": balance_fees["count"]
                    },
                    "daily_collection_report": serialize_doc(daily_collection),
                    "type_wise_balance_report": serialize_doc(type_wise_balance),
                    "fees_statement": serialize_doc(fees_statement),
                    "total_fee_collection_report": serialize_doc(total_fee_collection),
                    "other_fees_collection_report": serialize_doc(other_fees_collection),
                    "online_fees_collection_report": serialize_doc(online_fees_collection),
                    "balance_fees_report_with_remark": serialize_doc(balance_fees_remark)
                },
                "filters_applied": {
                    "start_date": start_date,
                    "end_date": end_date,
                    "branch_id": branch_id,
                    "session": session,
                    "class": class_filter,
                    "section": section,
                    "fees_type": fees_type
                },
                "generated_at": datetime.utcnow()
            }

        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error generating financial reports: {str(e)}")

    @staticmethod
    async def get_student_reports(
        current_user: dict,
        branch_id: Optional[str] = None,
        course_id: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ):
        """Get comprehensive student reports"""
        if not current_user:
            raise HTTPException(status_code=401, detail="Authentication required")

        db = get_db()
        
        # Build filter query
        filter_query = {"role": "student", "is_active": True}
        if current_user["role"] == "coach_admin" and current_user.get("branch_id"):
            filter_query["branch_id"] = current_user["branch_id"]
        elif branch_id:
            filter_query["branch_id"] = branch_id

        try:
            # Student enrollment statistics
            enrollment_stats = await db.enrollments.aggregate([
                {"$match": {"is_active": True}},
                {"$group": {
                    "_id": "$course_id",
                    "total_students": {"$sum": 1}
                }},
                {"$lookup": {
                    "from": "courses",
                    "localField": "_id",
                    "foreignField": "id",
                    "as": "course_info"
                }},
                {"$unwind": "$course_info"}
            ]).to_list(50)

            # Student attendance statistics
            attendance_filter = {}
            if start_date and end_date:
                attendance_filter["attendance_date"] = {"$gte": start_date, "$lte": end_date}
            
            attendance_stats = await db.attendance.aggregate([
                {"$match": attendance_filter},
                {"$group": {
                    "_id": "$student_id",
                    "total_classes": {"$sum": 1},
                    "present_classes": {"$sum": {"$cond": [{"$eq": ["$status", "present"]}, 1, 0]}}
                }},
                {"$project": {
                    "attendance_percentage": {
                        "$multiply": [
                            {"$divide": ["$present_classes", "$total_classes"]},
                            100
                        ]
                    }
                }}
            ]).to_list(1000)

            # Active students by branch
            students_by_branch = await db.users.aggregate([
                {"$match": filter_query},
                {"$group": {
                    "_id": "$branch_id",
                    "total_students": {"$sum": 1}
                }},
                {"$lookup": {
                    "from": "branches",
                    "localField": "_id",
                    "foreignField": "id",
                    "as": "branch_info"
                }},
                {"$unwind": "$branch_info"}
            ]).to_list(20)

            return {
                "student_reports": {
                    "enrollment_statistics": serialize_doc(enrollment_stats),
                    "attendance_statistics": serialize_doc(attendance_stats),
                    "students_by_branch": serialize_doc(students_by_branch)
                },
                "generated_at": datetime.utcnow()
            }

        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error generating student reports: {str(e)}")

    @staticmethod
    async def get_coach_reports(
        current_user: dict,
        branch_id: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ):
        """Get comprehensive coach reports"""
        if not current_user:
            raise HTTPException(status_code=401, detail="Authentication required")

        db = get_db()

        # Build filter query
        filter_query = {"role": "coach", "is_active": True}
        if current_user["role"] == "coach_admin" and current_user.get("branch_id"):
            filter_query["branch_id"] = current_user["branch_id"]
        elif branch_id:
            filter_query["branch_id"] = branch_id

        try:
            # Coach performance statistics
            coach_stats = await db.users.aggregate([
                {"$match": filter_query},
                {"$lookup": {
                    "from": "courses",
                    "localField": "id",
                    "foreignField": "instructor_id",
                    "as": "assigned_courses"
                }},
                {"$project": {
                    "full_name": 1,
                    "email": 1,
                    "branch_id": 1,
                    "total_courses": {"$size": "$assigned_courses"}
                }}
            ]).to_list(100)

            # Coach ratings if available
            coach_ratings = await db.coach_ratings.aggregate([
                {"$group": {
                    "_id": "$coach_id",
                    "average_rating": {"$avg": "$rating"},
                    "total_ratings": {"$sum": 1}
                }},
                {"$lookup": {
                    "from": "users",
                    "localField": "_id",
                    "foreignField": "id",
                    "as": "coach_info"
                }},
                {"$unwind": "$coach_info"}
            ]).to_list(100)

            # Coaches by branch
            coaches_by_branch = await db.users.aggregate([
                {"$match": filter_query},
                {"$group": {
                    "_id": "$branch_id",
                    "total_coaches": {"$sum": 1}
                }},
                {"$lookup": {
                    "from": "branches",
                    "localField": "_id",
                    "foreignField": "id",
                    "as": "branch_info"
                }},
                {"$unwind": "$branch_info"}
            ]).to_list(20)

            return {
                "coach_reports": {
                    "coach_statistics": serialize_doc(coach_stats),
                    "coach_ratings": serialize_doc(coach_ratings),
                    "coaches_by_branch": serialize_doc(coaches_by_branch)
                },
                "generated_at": datetime.utcnow()
            }

        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error generating coach reports: {str(e)}")

    @staticmethod
    async def get_branch_reports(
        current_user: dict,
        branch_id: Optional[str] = None
    ):
        """Get comprehensive branch reports"""
        if not current_user:
            raise HTTPException(status_code=401, detail="Authentication required")

        db = get_db()

        # Build filter query
        filter_query = {}
        if current_user["role"] == "coach_admin" and current_user.get("branch_id"):
            filter_query["id"] = current_user["branch_id"]
        elif branch_id:
            filter_query["id"] = branch_id

        try:
            # Branch performance statistics
            branch_stats = await db.branches.aggregate([
                {"$match": filter_query if filter_query else {}},
                {"$lookup": {
                    "from": "users",
                    "localField": "id",
                    "foreignField": "branch_id",
                    "as": "branch_users"
                }},
                {"$lookup": {
                    "from": "courses",
                    "localField": "id",
                    "foreignField": "branch_id",
                    "as": "branch_courses"
                }},
                {"$project": {
                    "name": 1,
                    "location": 1,
                    "state": 1,
                    "total_students": {
                        "$size": {
                            "$filter": {
                                "input": "$branch_users",
                                "cond": {"$eq": ["$$this.role", "student"]}
                            }
                        }
                    },
                    "total_coaches": {
                        "$size": {
                            "$filter": {
                                "input": "$branch_users",
                                "cond": {"$eq": ["$$this.role", "coach"]}
                            }
                        }
                    },
                    "total_courses": {"$size": "$branch_courses"}
                }}
            ]).to_list(50)

            # Revenue by branch
            revenue_by_branch = await db.payments.aggregate([
                {"$match": {"payment_status": {"$in": ["paid", "completed"]}}},
                {"$lookup": {
                    "from": "users",
                    "localField": "student_id",
                    "foreignField": "id",
                    "as": "student_info"
                }},
                {"$unwind": "$student_info"},
                {"$group": {
                    "_id": "$student_info.branch_id",
                    "total_revenue": {"$sum": "$amount"},
                    "total_transactions": {"$sum": 1}
                }},
                {"$lookup": {
                    "from": "branches",
                    "localField": "_id",
                    "foreignField": "id",
                    "as": "branch_info"
                }},
                {"$unwind": "$branch_info"}
            ]).to_list(50)

            return {
                "branch_reports": {
                    "branch_statistics": serialize_doc(branch_stats),
                    "revenue_by_branch": serialize_doc(revenue_by_branch)
                },
                "generated_at": datetime.utcnow()
            }

        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error generating branch reports: {str(e)}")

    @staticmethod
    async def get_course_reports(
        current_user: dict,
        branch_id: Optional[str] = None,
        category_id: Optional[str] = None
    ):
        """Get comprehensive course reports"""
        if not current_user:
            raise HTTPException(status_code=401, detail="Authentication required")

        db = get_db()

        # Build filter query
        filter_query = {"settings.active": True}
        if current_user["role"] == "coach_admin" and current_user.get("branch_id"):
            filter_query["branch_id"] = current_user["branch_id"]
        elif branch_id:
            filter_query["branch_id"] = branch_id

        if category_id:
            filter_query["category_id"] = category_id

        try:
            # Course enrollment statistics
            course_enrollment_stats = await db.courses.aggregate([
                {"$match": filter_query},
                {"$lookup": {
                    "from": "enrollments",
                    "localField": "id",
                    "foreignField": "course_id",
                    "as": "enrollments"
                }},
                {"$lookup": {
                    "from": "categories",
                    "localField": "category_id",
                    "foreignField": "id",
                    "as": "category_info"
                }},
                {"$unwind": {"path": "$category_info", "preserveNullAndEmptyArrays": True}},
                {"$project": {
                    "title": 1,
                    "code": 1,
                    "category_name": "$category_info.name",
                    "total_enrollments": {"$size": "$enrollments"},
                    "active_enrollments": {
                        "$size": {
                            "$filter": {
                                "input": "$enrollments",
                                "cond": {"$eq": ["$$this.is_active", True]}
                            }
                        }
                    }
                }}
            ]).to_list(100)

            # Course completion rates
            course_completion_stats = await db.enrollments.aggregate([
                {"$match": {"is_active": True}},
                {"$group": {
                    "_id": "$course_id",
                    "total_enrollments": {"$sum": 1},
                    "completed_enrollments": {
                        "$sum": {"$cond": [{"$eq": ["$status", "completed"]}, 1, 0]}
                    }
                }},
                {"$project": {
                    "completion_rate": {
                        "$multiply": [
                            {"$divide": ["$completed_enrollments", "$total_enrollments"]},
                            100
                        ]
                    }
                }},
                {"$lookup": {
                    "from": "courses",
                    "localField": "_id",
                    "foreignField": "id",
                    "as": "course_info"
                }},
                {"$unwind": "$course_info"}
            ]).to_list(100)

            return {
                "course_reports": {
                    "course_enrollment_statistics": serialize_doc(course_enrollment_stats),
                    "course_completion_statistics": serialize_doc(course_completion_stats)
                },
                "generated_at": datetime.utcnow()
            }

        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error generating course reports: {str(e)}")

    @staticmethod
    async def get_report_categories():
        """Get available report categories"""
        return {
            "categories": [
                {
                    "id": "student",
                    "name": "Student Reports",
                    "description": "Student enrollment, attendance, and performance reports",
                    "reports_count": 8
                },
                {
                    "id": "master",
                    "name": "Master Reports",
                    "description": "Comprehensive system-wide reports and administrative summaries",
                    "reports_count": 8
                },
                {
                    "id": "course",
                    "name": "Course Reports",
                    "description": "Course enrollment, completion rates, and performance analytics",
                    "reports_count": 8
                },
                {
                    "id": "coach",
                    "name": "Coach Reports",
                    "description": "Coach performance, assignments, ratings, and analytics",
                    "reports_count": 8
                },
                {
                    "id": "branch",
                    "name": "Branch Reports",
                    "description": "Branch-wise analytics, performance, and operational reports",
                    "reports_count": 8
                },
                {
                    "id": "financial",
                    "name": "Financial Reports",
                    "description": "Payment, revenue, and financial analytics reports",
                    "reports_count": 8
                }
            ]
        }

    @staticmethod
    async def get_category_reports(category_id: str):
        """Get reports available for a specific category"""
        category_reports = {
            "student": [
                {"id": "student-enrollment-summary", "name": "Student Enrollment Summary"},
                {"id": "student-attendance-report", "name": "Student Attendance Report"},
                {"id": "student-performance-analysis", "name": "Student Performance Analysis"},
                {"id": "student-payment-history", "name": "Student Payment History"},
                {"id": "student-transfer-requests", "name": "Student Transfer Requests"},
                {"id": "student-course-changes", "name": "Student Course Changes"},
                {"id": "student-complaints-report", "name": "Student Complaints Report"},
                {"id": "student-demographics", "name": "Student Demographics"}
            ],
            "master": [
                {"id": "system-overview-dashboard", "name": "System Overview Dashboard"},
                {"id": "master-enrollment-report", "name": "Master Enrollment Report"},
                {"id": "master-attendance-summary", "name": "Master Attendance Summary"},
                {"id": "master-financial-summary", "name": "Master Financial Summary"},
                {"id": "activity-log-report", "name": "Activity Log Report"},
                {"id": "system-usage-analytics", "name": "System Usage Analytics"},
                {"id": "master-user-report", "name": "Master User Report"},
                {"id": "notification-delivery-report", "name": "Notification Delivery Report"}
            ],
            "course": [
                {"id": "course-enrollment-statistics", "name": "Course Enrollment Statistics"},
                {"id": "course-completion-rates", "name": "Course Completion Rates"},
                {"id": "course-popularity-analysis", "name": "Course Popularity Analysis"},
                {"id": "course-revenue-report", "name": "Course Revenue Report"},
                {"id": "course-category-analysis", "name": "Course Category Analysis"},
                {"id": "course-duration-effectiveness", "name": "Course Duration Effectiveness"},
                {"id": "course-feedback-summary", "name": "Course Feedback Summary"},
                {"id": "course-capacity-utilization", "name": "Course Capacity Utilization"}
            ],
            "coach": [
                {"id": "coach-performance-summary", "name": "Coach Performance Summary"},
                {"id": "coach-student-assignments", "name": "Coach Student Assignments"},
                {"id": "coach-ratings-analysis", "name": "Coach Ratings Analysis"},
                {"id": "coach-attendance-tracking", "name": "Coach Attendance Tracking"},
                {"id": "coach-course-load", "name": "Coach Course Load"},
                {"id": "coach-feedback-report", "name": "Coach Feedback Report"},
                {"id": "coach-productivity-metrics", "name": "Coach Productivity Metrics"},
                {"id": "coach-branch-distribution", "name": "Coach Branch Distribution"}
            ],
            "branch": [
                {"id": "branch-performance-overview", "name": "Branch Performance Overview"},
                {"id": "branch-enrollment-statistics", "name": "Branch Enrollment Statistics"},
                {"id": "branch-revenue-analysis", "name": "Branch Revenue Analysis"},
                {"id": "branch-capacity-utilization", "name": "Branch Capacity Utilization"},
                {"id": "branch-staff-allocation", "name": "Branch Staff Allocation"},
                {"id": "branch-operational-hours", "name": "Branch Operational Hours"},
                {"id": "branch-comparison-report", "name": "Branch Comparison Report"},
                {"id": "branch-growth-trends", "name": "Branch Growth Trends"}
            ],
            "financial": [
                {"id": "revenue-summary-report", "name": "Revenue Summary Report"},
                {"id": "payment-collection-analysis", "name": "Payment Collection Analysis"},
                {"id": "outstanding-dues-report", "name": "Outstanding Dues Report"},
                {"id": "payment-method-analysis", "name": "Payment Method Analysis"},
                {"id": "monthly-financial-summary", "name": "Monthly Financial Summary"},
                {"id": "admission-fee-collection", "name": "Admission Fee Collection"},
                {"id": "course-fee-breakdown", "name": "Course Fee Breakdown"},
                {"id": "refund-and-adjustments", "name": "Refund and Adjustments"}
            ]
        }

        if category_id not in category_reports:
            raise HTTPException(status_code=404, detail="Category not found")

        return {
            "category_id": category_id,
            "reports": category_reports[category_id]
        }

    @staticmethod
    async def get_report_filters(current_user: dict):
        """Get available filter options for reports"""
        if not current_user:
            raise HTTPException(status_code=401, detail="Authentication required")

        db = get_db()

        try:
            # Get available branches
            branch_filter = {"is_active": True}  # Only get active branches
            if current_user["role"] == "coach_admin" and current_user.get("branch_id"):
                branch_filter["id"] = current_user["branch_id"]

            branches_raw = await db.branches.find(branch_filter, {"id": 1, "branch.name": 1}).to_list(100)

            # Format branches for frontend consumption and filter out invalid entries
            branches = []
            for branch in branches_raw:
                if branch.get("id") and branch.get("branch", {}).get("name"):
                    branches.append({
                        "id": branch["id"],
                        "name": branch["branch"]["name"]
                    })

            # Get available courses
            courses_raw = await db.courses.find(
                {"settings.active": True},
                {"id": 1, "title": 1, "code": 1}
            ).to_list(100)

            # Format courses and filter out invalid entries
            courses = []
            for course in courses_raw:
                if course.get("id") and course.get("title"):
                    courses.append({
                        "id": course["id"],
                        "title": course["title"],
                        "code": course.get("code", "")
                    })

            # Get available categories
            categories_raw = await db.categories.find({}, {"id": 1, "name": 1}).to_list(50)

            # Format categories and filter out invalid entries
            categories = []
            for category in categories_raw:
                if category.get("id") and category.get("name"):
                    categories.append({
                        "id": category["id"],
                        "name": category["name"]
                    })

            # Get available payment types
            payment_types = await db.payments.distinct("payment_type")
            # Filter out None/empty payment types
            payment_types = [pt for pt in payment_types if pt and pt.strip()]

            return {
                "filter_options": {
                    "branches": branches,
                    "courses": courses,
                    "categories": categories,
                    "payment_types": payment_types,
                    "date_ranges": [
                        {"id": "current-month", "name": "Current Month"},
                        {"id": "last-month", "name": "Last Month"},
                        {"id": "current-quarter", "name": "Current Quarter"},
                        {"id": "last-quarter", "name": "Last Quarter"},
                        {"id": "current-year", "name": "Current Year"},
                        {"id": "custom", "name": "Custom Range"}
                    ]
                }
            }

        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error getting report filters: {str(e)}")

    @staticmethod
    async def get_master_reports(
        current_user: dict,
        branch_id: Optional[str] = None,
        course_id: Optional[str] = None,
        area_of_expertise: Optional[str] = None,
        professional_experience: Optional[str] = None,
        designation_id: Optional[str] = None,
        active_only: bool = True,
        search: Optional[str] = None,
        skip: int = 0,
        limit: int = 50
    ):
        """Get comprehensive master (coach) reports with filtering and search"""
        if not current_user:
            raise HTTPException(status_code=401, detail="Authentication required")

        db = get_db()

        try:
            # Build filter query
            filter_query = {"role": "coach"}

            # Apply role-based filtering
            if current_user["role"] == "coach_admin" and current_user.get("branch_id"):
                filter_query["branch_id"] = current_user["branch_id"]
            elif branch_id:
                filter_query["branch_id"] = branch_id

            # Apply filters
            if active_only:
                filter_query["is_active"] = True

            if area_of_expertise:
                filter_query["areas_of_expertise"] = {"$in": [area_of_expertise]}

            if professional_experience:
                filter_query["professional_info.professional_experience"] = professional_experience

            if designation_id:
                filter_query["professional_info.designation_id"] = designation_id

            if course_id:
                filter_query["assignment_details.courses"] = {"$in": [course_id]}

            # Apply search filter
            if search and len(search.strip()) >= 2:
                search_pattern = {"$regex": search.strip(), "$options": "i"}
                filter_query["$or"] = [
                    {"full_name": search_pattern},
                    {"contact_info.email": search_pattern},
                    {"contact_info.phone": search_pattern},
                    {"personal_info.first_name": search_pattern},
                    {"personal_info.last_name": search_pattern}
                ]

            # Get total count for pagination
            total_count = await db.users.count_documents(filter_query)

            # Get coaches with pagination
            coaches_cursor = db.users.find(filter_query).skip(skip).limit(limit)
            coaches = await coaches_cursor.to_list(length=limit)

            # Process coaches data and join with related information
            processed_coaches = []
            for coach in coaches:
                # Get branch information
                branch_info = None
                if coach.get("branch_id"):
                    branch_doc = await db.branches.find_one({"id": coach["branch_id"]})
                    if branch_doc:
                        branch_info = {
                            "id": branch_doc["id"],
                            "name": branch_doc["branch"]["name"],
                            "code": branch_doc["branch"]["code"]
                        }

                # Get course information
                course_details = []
                assigned_courses = coach.get("assignment_details", {}).get("courses", [])
                if assigned_courses:
                    courses_cursor = db.courses.find({"id": {"$in": assigned_courses}})
                    courses = await courses_cursor.to_list(length=100)
                    course_details = [
                        {
                            "id": course["id"],
                            "title": course["title"],
                            "code": course.get("code", ""),
                            "difficulty_level": course.get("difficulty_level", "")
                        }
                        for course in courses
                    ]

                # Build processed coach data
                processed_coach = {
                    "id": coach["id"],
                    "full_name": coach.get("full_name", ""),
                    "first_name": coach.get("personal_info", {}).get("first_name", ""),
                    "last_name": coach.get("personal_info", {}).get("last_name", ""),
                    "email": coach.get("contact_info", {}).get("email", ""),
                    "phone": coach.get("contact_info", {}).get("phone", ""),
                    "branch": branch_info,
                    "assigned_courses": course_details,
                    "areas_of_expertise": coach.get("areas_of_expertise", []),
                    "professional_experience": coach.get("professional_info", {}).get("professional_experience", ""),
                    "designation": coach.get("professional_info", {}).get("designation_id", ""),
                    "is_active": coach.get("is_active", False),
                    "join_date": coach.get("assignment_details", {}).get("join_date"),
                    "created_at": coach.get("created_at"),
                    "updated_at": coach.get("updated_at")
                }
                processed_coaches.append(processed_coach)

            return {
                "masters": serialize_doc(processed_coaches),
                "pagination": {
                    "total": total_count,
                    "skip": skip,
                    "limit": limit,
                    "has_more": skip + limit < total_count
                },
                "filters_applied": {
                    "branch_id": branch_id,
                    "course_id": course_id,
                    "area_of_expertise": area_of_expertise,
                    "professional_experience": professional_experience,
                    "designation_id": designation_id,
                    "active_only": active_only,
                    "search": search
                },
                "generated_at": datetime.utcnow()
            }

        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error getting master reports: {str(e)}")

    @staticmethod
    async def get_master_report_filters(current_user: dict):
        """Get available filter options for master reports"""
        if not current_user:
            raise HTTPException(status_code=401, detail="Authentication required")

        db = get_db()

        try:
            # Get branches (filtered by user role)
            branch_filter = {}
            if current_user["role"] == "coach_admin" and current_user.get("branch_id"):
                branch_filter["id"] = current_user["branch_id"]

            branches_cursor = db.branches.find(branch_filter)
            branches = await branches_cursor.to_list(length=100)
            branch_options = []
            for branch in branches:
                # Handle both nested and direct branch structures
                if 'branch' in branch and isinstance(branch['branch'], dict):
                    name = branch['branch'].get('name', 'Unknown')
                    code = branch['branch'].get('code', '')
                else:
                    name = branch.get('name', 'Unknown')
                    code = branch.get('code', '')

                display_name = f"{name} ({code})" if code else name
                branch_options.append({"id": branch["id"], "name": display_name})

            # Get courses
            courses_cursor = db.courses.find({"settings.active": True}, {"id": 1, "title": 1, "code": 1})
            courses = await courses_cursor.to_list(length=200)
            course_options = [
                {"id": course["id"], "name": f"{course['title']} ({course.get('code', '')})"}
                for course in courses
            ]

            # Get unique areas of expertise from coaches
            areas_pipeline = [
                {"$match": {"role": "coach", "areas_of_expertise": {"$exists": True, "$ne": []}}},
                {"$unwind": "$areas_of_expertise"},
                {"$group": {"_id": "$areas_of_expertise"}},
                {"$sort": {"_id": 1}}
            ]
            areas_result = await db.users.aggregate(areas_pipeline).to_list(100)
            area_options = [{"id": area["_id"], "name": area["_id"]} for area in areas_result]

            # Get unique professional experience levels
            experience_pipeline = [
                {"$match": {"role": "coach", "professional_info.professional_experience": {"$exists": True, "$ne": None}}},
                {"$group": {"_id": "$professional_info.professional_experience"}},
                {"$sort": {"_id": 1}}
            ]
            experience_result = await db.users.aggregate(experience_pipeline).to_list(20)
            experience_options = [{"id": exp["_id"], "name": exp["_id"]} for exp in experience_result]

            # Get unique designations
            designation_pipeline = [
                {"$match": {"role": "coach", "professional_info.designation_id": {"$exists": True, "$ne": None}}},
                {"$group": {"_id": "$professional_info.designation_id"}},
                {"$sort": {"_id": 1}}
            ]
            designation_result = await db.users.aggregate(designation_pipeline).to_list(20)
            designation_options = [{"id": des["_id"], "name": des["_id"]} for des in designation_result]

            return {
                "filters": {
                    "branches": branch_options,
                    "courses": course_options,
                    "areas_of_expertise": area_options,
                    "professional_experience": experience_options,
                    "designations": designation_options,
                    "active_status": [
                        {"id": "true", "name": "Active Only"},
                        {"id": "false", "name": "Include Inactive"}
                    ]
                },
                "generated_at": datetime.utcnow()
            }

        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error getting master report filters: {str(e)}")
