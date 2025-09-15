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
        elif branch_id:
            filter_query["branch_id"] = branch_id
        
        try:
            # Active students count
            active_students = await db.users.count_documents({
                "role": "student", 
                "is_active": True,
                **filter_query
            })
            stats["active_students"] = active_students
            
            # Total users count
            total_users = await db.users.count_documents({
                "is_active": True,
                **filter_query
            })
            stats["total_users"] = total_users
            
            # Active courses count
            active_courses = await db.courses.count_documents({
                "settings.active": True,
                **filter_query
            })
            stats["active_courses"] = active_courses
            
            # Monthly active users (users who logged in within last 30 days)
            thirty_days_ago = datetime.utcnow() - timedelta(days=30)
            monthly_active_users = await db.users.count_documents({
                "is_active": True,
                "last_login": {"$gte": thirty_days_ago},
                **filter_query
            })
            stats["monthly_active_users"] = monthly_active_users
            
            # Active enrollments
            active_enrollments = await db.enrollments.count_documents({
                "is_active": True,
                **filter_query
            })
            stats["active_enrollments"] = active_enrollments
            
            # Revenue calculation (from payments)
            revenue_pipeline = [
                {"$match": {"payment_status": "completed", **filter_query}},
                {"$group": {"_id": None, "total": {"$sum": "$amount"}}}
            ]
            revenue_result = await db.payments.aggregate(revenue_pipeline).to_list(length=1)
            total_revenue = revenue_result[0]["total"] if revenue_result else 0
            stats["total_revenue"] = total_revenue
            
            # Monthly revenue (current month)
            current_month_start = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            monthly_revenue_pipeline = [
                {
                    "$match": {
                        "payment_status": "completed",
                        "payment_date": {"$gte": current_month_start},
                        **filter_query
                    }
                },
                {"$group": {"_id": None, "total": {"$sum": "$amount"}}}
            ]
            monthly_revenue_result = await db.payments.aggregate(monthly_revenue_pipeline).to_list(length=1)
            monthly_revenue = monthly_revenue_result[0]["total"] if monthly_revenue_result else 0
            stats["monthly_revenue"] = monthly_revenue
            
            # Pending payments
            pending_payments = await db.payments.count_documents({
                "payment_status": "pending",
                **filter_query
            })
            stats["pending_payments"] = pending_payments
            
            # Today's attendance
            today = datetime.utcnow().date()
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
