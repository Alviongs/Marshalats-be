from fastapi import HTTPException
from typing import Optional
from datetime import datetime, timedelta
from utils.database import get_db
from utils.helpers import serialize_doc
from models.user_models import UserRole

class DashboardController:
    @staticmethod
    async def get_dashboard_stats(
        current_user: dict,
        branch_id: Optional[str] = None
    ):
        """Get comprehensive dashboard statistics"""
        if not current_user:
            raise HTTPException(status_code=401, detail="Authentication required")

        db = get_db()
        stats = {}
        
        # Filter by role and branch
        filter_query = {}
        if current_user["role"] == "coach_admin" and current_user.get("branch_id"):
            filter_query["branch_id"] = current_user["branch_id"]
        elif current_user["role"] == "branch_manager":
            # Branch managers can only see data from their managed branches
            branch_manager_id = current_user.get("id")
            if not branch_manager_id:
                raise HTTPException(status_code=403, detail="Branch manager ID not found")

            # Find all branches managed by this branch manager
            managed_branches = await db.branches.find({"manager_id": branch_manager_id, "is_active": True}).to_list(length=None)

            if not managed_branches:
                # Return empty stats if no branches are managed
                return {"dashboard_stats": {
                    "active_students": 0,
                    "total_users": 0,
                    "active_courses": 0,
                    "monthly_active_users": 0,
                    "active_enrollments": 0,
                    "total_revenue": 0,
                    "monthly_revenue": 0,
                    "pending_payments": 0,
                    "today_attendance": 0,
                    "total_coaches": 0,
                    "active_coaches": 0
                }}

            # Get all branch IDs managed by this branch manager
            managed_branch_ids = [branch["id"] for branch in managed_branches]
            print(f"Branch manager {branch_manager_id} manages branches for dashboard stats: {managed_branch_ids}")

            # Filter by multiple branches
            filter_query["branch_id"] = {"$in": managed_branch_ids}
        elif branch_id:
            filter_query["branch_id"] = branch_id
        
        try:
            # Active students count - Handle branch manager filtering correctly
            if current_user["role"] == "branch_manager":
                managed_branch_ids = filter_query.get("branch_id", {}).get("$in", [])
                if managed_branch_ids:
                    # Count students in managed branches
                    active_students = await db.users.count_documents({
                        "role": "student",
                        "is_active": True,
                        "branch_id": {"$in": managed_branch_ids}
                    })

                    # Also count students from enrollments if users don't have branch_id
                    enrollment_students = await db.enrollments.find({
                        "is_active": True,
                        "branch_id": {"$in": managed_branch_ids}
                    }).distinct("student_id")

                    # Get unique student count from enrollments
                    enrollment_student_count = len(set(enrollment_students)) if enrollment_students else 0

                    # Use the higher count (some students might not have branch_id in users collection)
                    active_students = max(active_students, enrollment_student_count)

                    # Total users count for branch manager
                    total_users = await db.users.count_documents({
                        "is_active": True,
                        "branch_id": {"$in": managed_branch_ids}
                    })
                else:
                    active_students = 0
                    total_users = 0
            else:
                # For other roles, use existing logic
                active_students = await db.users.count_documents({
                    "role": "student",
                    "is_active": True,
                    **filter_query
                })

                total_users = await db.users.count_documents({
                    "is_active": True,
                    **filter_query
                })

            stats["active_students"] = active_students
            stats["total_users"] = total_users
            
            # Active courses count
            if current_user["role"] == "branch_manager":
                # For branch managers, count courses assigned to their managed branches
                managed_branch_ids = filter_query.get("branch_id", {}).get("$in", [])
                if managed_branch_ids:
                    # Get all course IDs from the managed branches
                    course_ids_set = set()
                    for branch in managed_branches:
                        branch_course_ids = branch.get("assignments", {}).get("courses", [])
                        course_ids_set.update(branch_course_ids)

                    if course_ids_set:
                        active_courses = await db.courses.count_documents({
                            "settings.active": True,
                            "id": {"$in": list(course_ids_set)}
                        })
                        total_courses = await db.courses.count_documents({
                            "id": {"$in": list(course_ids_set)}
                        })
                    else:
                        active_courses = 0
                        total_courses = 0
                else:
                    active_courses = 0
                    total_courses = 0
            else:
                # For other roles, count all active courses
                active_courses = await db.courses.count_documents({
                    "settings.active": True,
                    **filter_query
                })
                total_courses = await db.courses.count_documents(filter_query)

            stats["active_courses"] = active_courses
            stats["total_courses"] = total_courses

            # Active coaches count (for branch managers, filter by branch)
            if current_user["role"] == "branch_manager":
                # For branch managers, count coaches assigned to their managed branches
                managed_branch_ids = filter_query.get("branch_id", {}).get("$in", [])
                if managed_branch_ids:
                    active_coaches = await db.coaches.count_documents({
                        "is_active": True,
                        "branch_id": {"$in": managed_branch_ids}
                    })
                    total_coaches = await db.coaches.count_documents({
                        "branch_id": {"$in": managed_branch_ids}
                    })
                else:
                    active_coaches = 0
                    total_coaches = 0
            else:
                # For other roles, use existing logic
                active_coaches = await db.coaches.count_documents({
                    "is_active": True,
                    **filter_query
                })
                total_coaches = await db.coaches.count_documents(filter_query)

            stats["active_coaches"] = active_coaches
            stats["total_coaches"] = total_coaches

            # Monthly active users (users who logged in within last 30 days)
            thirty_days_ago = datetime.utcnow() - timedelta(days=30)
            monthly_active_users = await db.users.count_documents({
                "is_active": True,
                "last_login": {"$gte": thirty_days_ago},
                **filter_query
            })
            stats["monthly_active_users"] = monthly_active_users
            
            # Active enrollments - Handle branch manager filtering correctly
            if current_user["role"] == "branch_manager":
                managed_branch_ids = filter_query.get("branch_id", {}).get("$in", [])
                if managed_branch_ids:
                    active_enrollments = await db.enrollments.count_documents({
                        "is_active": True,
                        "branch_id": {"$in": managed_branch_ids}
                    })
                else:
                    active_enrollments = 0
            else:
                active_enrollments = await db.enrollments.count_documents({
                    "is_active": True,
                    **filter_query
                })
            stats["active_enrollments"] = active_enrollments
            
            # Revenue calculation (from payments) - Handle both "completed" and "paid" status
            # For branch managers, we need to get students from enrollments since payments don't have branch_id
            if current_user["role"] == "branch_manager":
                managed_branch_ids = filter_query.get("branch_id", {}).get("$in", [])

                if managed_branch_ids:
                    # Get students from enrollments in managed branches
                    enrollment_students = await db.enrollments.find({
                        "is_active": True,
                        "branch_id": {"$in": managed_branch_ids}
                    }).distinct("student_id")

                    # Also get students directly assigned to branches
                    branch_students = await db.users.find({
                        "role": "student",
                        "is_active": True,
                        "branch_id": {"$in": managed_branch_ids}
                    }).to_list(length=None)

                    direct_student_ids = [student["id"] for student in branch_students]
                    all_student_ids = list(set(enrollment_students + direct_student_ids))

                    if all_student_ids:
                        # Calculate total revenue
                        revenue_pipeline = [
                            {"$match": {
                                "payment_status": {"$in": ["completed", "paid"]},
                                "student_id": {"$in": all_student_ids}
                            }},
                            {"$group": {"_id": None, "total": {"$sum": "$amount"}}}
                        ]
                        revenue_result = await db.payments.aggregate(revenue_pipeline).to_list(length=1)
                        total_revenue = revenue_result[0]["total"] if revenue_result else 0

                        # Calculate monthly revenue
                        current_month_start = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
                        monthly_revenue_pipeline = [
                            {
                                "$match": {
                                    "payment_status": {"$in": ["completed", "paid"]},
                                    "payment_date": {"$gte": current_month_start},
                                    "student_id": {"$in": all_student_ids}
                                }
                            },
                            {"$group": {"_id": None, "total": {"$sum": "$amount"}}}
                        ]
                        monthly_revenue_result = await db.payments.aggregate(monthly_revenue_pipeline).to_list(length=1)
                        monthly_revenue = monthly_revenue_result[0]["total"] if monthly_revenue_result else 0

                        # Count pending payments
                        pending_payments = await db.payments.count_documents({
                            "payment_status": "pending",
                            "student_id": {"$in": all_student_ids}
                        })
                    else:
                        total_revenue = 0
                        monthly_revenue = 0
                        pending_payments = 0
                else:
                    total_revenue = 0
                    monthly_revenue = 0
                    pending_payments = 0
            else:
                # For other roles (super_admin, coach_admin), use branch_id filtering
                revenue_pipeline = [
                    {"$match": {"payment_status": {"$in": ["completed", "paid"]}, **filter_query}},
                    {"$group": {"_id": None, "total": {"$sum": "$amount"}}}
                ]
                revenue_result = await db.payments.aggregate(revenue_pipeline).to_list(length=1)
                total_revenue = revenue_result[0]["total"] if revenue_result else 0

                # Monthly revenue
                current_month_start = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
                monthly_revenue_pipeline = [
                    {
                        "$match": {
                            "payment_status": {"$in": ["completed", "paid"]},
                            "payment_date": {"$gte": current_month_start},
                            **filter_query
                        }
                    },
                    {"$group": {"_id": None, "total": {"$sum": "$amount"}}}
                ]
                monthly_revenue_result = await db.payments.aggregate(monthly_revenue_pipeline).to_list(length=1)
                monthly_revenue = monthly_revenue_result[0]["total"] if monthly_revenue_result else 0

                # Pending payments
                pending_payments = await db.payments.count_documents({
                    "payment_status": "pending",
                    **filter_query
                })

            stats["total_revenue"] = total_revenue
            stats["monthly_revenue"] = monthly_revenue
            stats["pending_payments"] = pending_payments
            
            # Today's attendance - Handle branch manager filtering correctly
            today = datetime.utcnow().date()
            if current_user["role"] == "branch_manager":
                managed_branch_ids = filter_query.get("branch_id", {}).get("$in", [])
                if managed_branch_ids:
                    today_attendance = await db.attendance.count_documents({
                        "attendance_date": {
                            "$gte": datetime.combine(today, datetime.min.time()),
                            "$lt": datetime.combine(today + timedelta(days=1), datetime.min.time())
                        },
                        "branch_id": {"$in": managed_branch_ids}
                    })
                else:
                    today_attendance = 0
            else:
                today_attendance = await db.attendance.count_documents({
                    "attendance_date": {
                        "$gte": datetime.combine(today, datetime.min.time()),
                        "$lt": datetime.combine(today + timedelta(days=1), datetime.min.time())
                    },
                    **filter_query
                })
            stats["today_attendance"] = today_attendance
            
            return {"dashboard_stats": stats}
            
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error fetching dashboard statistics: {str(e)}"
            )

    @staticmethod
    async def get_recent_activities(
        current_user: dict,
        limit: int = 10
    ):
        """Get recent activities for dashboard"""
        if not current_user:
            raise HTTPException(status_code=401, detail="Authentication required")

        db = get_db()
        
        try:
            # Get recent enrollments
            recent_enrollments = await db.enrollments.find({
                "is_active": True
            }).sort("created_at", -1).limit(limit).to_list(length=limit)
            
            # Get recent payments
            recent_payments = await db.payments.find({
                "payment_status": "completed"
            }).sort("payment_date", -1).limit(limit).to_list(length=limit)
            
            return {
                "recent_enrollments": serialize_doc(recent_enrollments),
                "recent_payments": serialize_doc(recent_payments)
            }
            
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error fetching recent activities: {str(e)}"
            )
