from fastapi import HTTPException, Depends
from typing import Optional, List
from datetime import datetime, timedelta
import uuid
import csv
import io

from models.attendance_models import AttendanceCreate, BiometricAttendance, Attendance, AttendanceMethod
from models.user_models import UserRole
from utils.database import get_db
from utils.helpers import serialize_doc

class AttendanceController:
    @staticmethod
    async def get_attendance_reports(
        student_id: Optional[str] = None,
        coach_id: Optional[str] = None,
        course_id: Optional[str] = None,
        branch_id: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        current_user: dict = None
    ):
        """Get attendance reports with filtering and role-based access control"""
        try:
            db = get_db()
            if db is None:
                raise HTTPException(status_code=500, detail="Database connection not available")

            # Build filter query
            filter_query = {}
            
            # Apply role-based filtering for branch managers
            if current_user and current_user.get("role") == "branch_manager":
                branch_manager_id = current_user.get("id")
                if not branch_manager_id:
                    raise HTTPException(status_code=403, detail="Branch manager ID not found")

                # Find all branches managed by this branch manager
                managed_branches = await db.branches.find({"manager_id": branch_manager_id, "is_active": True}).to_list(length=None)
                if not managed_branches:
                    return {"attendance_records": [], "total": 0}

                managed_branch_ids = [branch["id"] for branch in managed_branches]
                filter_query["branch_id"] = {"$in": managed_branch_ids}

            # Apply additional filters
            if student_id:
                filter_query["student_id"] = student_id
            if coach_id:
                filter_query["coach_id"] = coach_id
            if course_id:
                filter_query["course_id"] = course_id
            if branch_id and current_user.get("role") != "branch_manager":
                filter_query["branch_id"] = branch_id

            # Date range filtering
            if start_date and end_date:
                try:
                    start_dt = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
                    end_dt = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
                    filter_query["attendance_date"] = {"$gte": start_dt, "$lte": end_dt}
                except ValueError:
                    raise HTTPException(status_code=400, detail="Invalid date format")

            # Get attendance records with student and course information
            pipeline = [
                {"$match": filter_query},
                {
                    "$lookup": {
                        "from": "users",
                        "localField": "student_id",
                        "foreignField": "id",
                        "as": "student_info"
                    }
                },
                {"$unwind": {"path": "$student_info", "preserveNullAndEmptyArrays": True}},
                {
                    "$lookup": {
                        "from": "courses",
                        "localField": "course_id",
                        "foreignField": "id",
                        "as": "course_info"
                    }
                },
                {"$unwind": {"path": "$course_info", "preserveNullAndEmptyArrays": True}},
                {
                    "$lookup": {
                        "from": "branches",
                        "localField": "branch_id",
                        "foreignField": "id",
                        "as": "branch_info"
                    }
                },
                {"$unwind": {"path": "$branch_info", "preserveNullAndEmptyArrays": True}},
                {
                    "$project": {
                        "id": 1,
                        "student_id": 1,
                        "student_name": {"$ifNull": ["$student_info.full_name", {"$concat": ["$student_info.first_name", " ", "$student_info.last_name"]}]},
                        "course_id": 1,
                        "course_name": {"$ifNull": ["$course_info.title", "$course_info.name"]},
                        "branch_id": 1,
                        "branch_name": {"$ifNull": ["$branch_info.branch.name", "$branch_info.name"]},
                        "attendance_date": 1,
                        "check_in_time": 1,
                        "check_out_time": 1,
                        "is_present": 1,
                        "method": 1,
                        "notes": 1,
                        "created_at": 1
                    }
                },
                {"$sort": {"attendance_date": -1}}
            ]

            attendance_records = await db.attendance.aggregate(pipeline).to_list(length=1000)

            # Convert to serializable format
            serialized_records = []
            for record in attendance_records:
                serialized_record = {}
                for key, value in record.items():
                    if key == "_id":
                        continue
                    elif hasattr(value, 'isoformat'):
                        serialized_record[key] = value.isoformat()
                    else:
                        serialized_record[key] = value
                serialized_records.append(serialized_record)

            return {
                "attendance_records": serialized_records,
                "total": len(serialized_records)
            }

        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to get attendance reports: {str(e)}")

    @staticmethod
    async def get_student_attendance(
        branch_id: Optional[str] = None,
        course_id: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        current_user: dict = None
    ):
        """Get student attendance data with aggregated statistics"""
        try:
            db = get_db()
            if db is None:
                raise HTTPException(status_code=500, detail="Database connection not available")

            # Build base filter for attendance records
            filter_query = {}
            
            # Apply role-based filtering for branch managers
            managed_branch_ids = None
            if current_user and current_user.get("role") == "branch_manager":
                branch_manager_id = current_user.get("id")
                if not branch_manager_id:
                    raise HTTPException(status_code=403, detail="Branch manager ID not found")

                managed_branches = await db.branches.find({"manager_id": branch_manager_id, "is_active": True}).to_list(length=None)
                if not managed_branches:
                    return {"students": [], "total": 0}

                managed_branch_ids = [branch["id"] for branch in managed_branches]
                filter_query["branch_id"] = {"$in": managed_branch_ids}

            # Apply additional filters
            if branch_id and current_user.get("role") != "branch_manager":
                filter_query["branch_id"] = branch_id
            if course_id:
                filter_query["course_id"] = course_id

            # Date range filtering
            if start_date and end_date:
                try:
                    start_dt = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
                    end_dt = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
                    filter_query["attendance_date"] = {"$gte": start_dt, "$lte": end_dt}
                except ValueError:
                    raise HTTPException(status_code=400, detail="Invalid date format")

            # Get students with attendance statistics
            pipeline = [
                {"$match": filter_query},
                {
                    "$group": {
                        "_id": "$student_id",
                        "total_sessions": {"$sum": 1},
                        "present_sessions": {"$sum": {"$cond": ["$is_present", 1, 0]}},
                        "last_attendance": {"$max": "$attendance_date"},
                        "branch_ids": {"$addToSet": "$branch_id"},
                        "course_ids": {"$addToSet": "$course_id"}
                    }
                },
                {
                    "$lookup": {
                        "from": "users",
                        "localField": "_id",
                        "foreignField": "id",
                        "as": "student_info"
                    }
                },
                {"$unwind": {"path": "$student_info", "preserveNullAndEmptyArrays": True}},
                {
                    "$project": {
                        "student_id": "$_id",
                        "student_name": {"$ifNull": ["$student_info.full_name", {"$concat": ["$student_info.first_name", " ", "$student_info.last_name"]}]},
                        "email": "$student_info.email",
                        "phone": "$student_info.phone",
                        "total_sessions": 1,
                        "present_sessions": 1,
                        "attendance_percentage": {
                            "$multiply": [
                                {"$divide": ["$present_sessions", "$total_sessions"]},
                                100
                            ]
                        },
                        "last_attendance": 1,
                        "branch_count": {"$size": "$branch_ids"},
                        "course_count": {"$size": "$course_ids"}
                    }
                },
                {"$sort": {"attendance_percentage": -1}}
            ]

            student_attendance = await db.attendance.aggregate(pipeline).to_list(length=1000)

            # Convert to serializable format
            serialized_students = []
            for student in student_attendance:
                serialized_student = {}
                for key, value in student.items():
                    if key == "_id":
                        continue
                    elif hasattr(value, 'isoformat'):
                        serialized_student[key] = value.isoformat()
                    else:
                        serialized_student[key] = value
                serialized_students.append(serialized_student)

            return {
                "students": serialized_students,
                "total": len(serialized_students)
            }

        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to get student attendance: {str(e)}")

    @staticmethod
    async def get_coach_attendance(
        branch_id: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        current_user: dict = None
    ):
        """Get coach attendance data"""
        try:
            db = get_db()
            if db is None:
                raise HTTPException(status_code=500, detail="Database connection not available")

            # Build filter query for coaches
            filter_query = {"role": "coach", "is_active": True}

            # Apply role-based filtering for branch managers
            if current_user and current_user.get("role") == "branch_manager":
                branch_manager_id = current_user.get("id")
                if not branch_manager_id:
                    raise HTTPException(status_code=403, detail="Branch manager ID not found")

                managed_branches = await db.branches.find({"manager_id": branch_manager_id, "is_active": True}).to_list(length=None)
                if not managed_branches:
                    return {"coaches": [], "total": 0}

                managed_branch_ids = [branch["id"] for branch in managed_branches]
                filter_query["branch_id"] = {"$in": managed_branch_ids}

            if branch_id and current_user.get("role") != "branch_manager":
                filter_query["branch_id"] = branch_id

            # Get coaches from the specified branches
            coaches = await db.users.find(filter_query).to_list(length=1000)

            # For each coach, get their attendance data
            coach_attendance_data = []
            for coach in coaches:
                coach_id = coach.get("id")

                # Build attendance filter
                attendance_filter = {"coach_id": coach_id}

                if start_date and end_date:
                    try:
                        start_dt = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
                        end_dt = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
                        attendance_filter["attendance_date"] = {"$gte": start_dt, "$lte": end_dt}
                    except ValueError:
                        raise HTTPException(status_code=400, detail="Invalid date format")

                # Get coach attendance records
                attendance_records = await db.coach_attendance.find(attendance_filter).to_list(length=1000)

                # Calculate statistics
                total_days = len(attendance_records)
                present_days = sum(1 for record in attendance_records if record.get("is_present", False))
                attendance_percentage = (present_days / total_days * 100) if total_days > 0 else 0

                # Get latest attendance
                latest_attendance = None
                if attendance_records:
                    latest_record = max(attendance_records, key=lambda x: x.get("attendance_date", datetime.min))
                    latest_attendance = latest_record.get("attendance_date")

                coach_data = {
                    "coach_id": coach_id,
                    "coach_name": coach.get("full_name") or f"{coach.get('first_name', '')} {coach.get('last_name', '')}".strip(),
                    "email": coach.get("email"),
                    "phone": coach.get("phone"),
                    "branch_id": coach.get("branch_id"),
                    "expertise": coach.get("expertise", []),
                    "total_days": total_days,
                    "present_days": present_days,
                    "attendance_percentage": round(attendance_percentage, 2),
                    "last_attendance": latest_attendance.isoformat() if latest_attendance else None
                }

                coach_attendance_data.append(coach_data)

            return {
                "coaches": coach_attendance_data,
                "total": len(coach_attendance_data)
            }

        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to get coach attendance: {str(e)}")

    @staticmethod
    async def get_attendance_stats(branch_id: Optional[str] = None, current_user: dict = None):
        """Get attendance statistics"""
        try:
            db = get_db()
            if db is None:
                raise HTTPException(status_code=500, detail="Database connection not available")

            # Build filter query
            filter_query = {}

            # Apply role-based filtering for branch managers
            if current_user and current_user.get("role") == "branch_manager":
                branch_manager_id = current_user.get("id")
                if not branch_manager_id:
                    raise HTTPException(status_code=403, detail="Branch manager ID not found")

                managed_branches = await db.branches.find({"manager_id": branch_manager_id, "is_active": True}).to_list(length=None)
                if not managed_branches:
                    return {
                        "total_students": 0,
                        "total_coaches": 0,
                        "average_student_attendance": 0,
                        "average_coach_attendance": 0,
                        "today_present_students": 0,
                        "today_present_coaches": 0
                    }

                managed_branch_ids = [branch["id"] for branch in managed_branches]
                filter_query["branch_id"] = {"$in": managed_branch_ids}

            if branch_id and current_user.get("role") != "branch_manager":
                filter_query["branch_id"] = branch_id

            # Get today's date
            today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            tomorrow = today + timedelta(days=1)

            # Student statistics
            student_pipeline = [
                {"$match": filter_query},
                {
                    "$group": {
                        "_id": "$student_id",
                        "total_sessions": {"$sum": 1},
                        "present_sessions": {"$sum": {"$cond": ["$is_present", 1, 0]}}
                    }
                },
                {
                    "$group": {
                        "_id": None,
                        "total_students": {"$sum": 1},
                        "avg_attendance": {
                            "$avg": {
                                "$multiply": [
                                    {"$divide": ["$present_sessions", "$total_sessions"]},
                                    100
                                ]
                            }
                        }
                    }
                }
            ]

            student_stats = await db.attendance.aggregate(student_pipeline).to_list(length=1)

            # Today's student attendance
            today_filter = {**filter_query, "attendance_date": {"$gte": today, "$lt": tomorrow}}
            today_students = await db.attendance.count_documents({**today_filter, "is_present": True})

            # Coach statistics (if coach_attendance collection exists)
            coach_filter = filter_query.copy()
            if "branch_id" in coach_filter:
                # For coaches, we need to filter by their assigned branch
                coach_user_filter = {"role": "coach", "is_active": True}
                if isinstance(coach_filter["branch_id"], dict) and "$in" in coach_filter["branch_id"]:
                    coach_user_filter["branch_id"] = coach_filter["branch_id"]
                else:
                    coach_user_filter["branch_id"] = coach_filter["branch_id"]

                coaches = await db.users.find(coach_user_filter).to_list(length=1000)
                total_coaches = len(coaches)

                # Today's coach attendance (mock data for now)
                today_coaches = int(total_coaches * 0.85)  # Assume 85% attendance
                avg_coach_attendance = 85.0
            else:
                total_coaches = 0
                today_coaches = 0
                avg_coach_attendance = 0

            return {
                "total_students": student_stats[0]["total_students"] if student_stats else 0,
                "total_coaches": total_coaches,
                "average_student_attendance": round(student_stats[0]["avg_attendance"] if student_stats else 0, 2),
                "average_coach_attendance": avg_coach_attendance,
                "today_present_students": today_students,
                "today_present_coaches": today_coaches
            }

        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to get attendance stats: {str(e)}")

    @staticmethod
    async def mark_manual_attendance(attendance_data: AttendanceCreate, current_user: dict):
        """Manually mark attendance"""
        try:
            db = get_db()
            if db is None:
                raise HTTPException(status_code=500, detail="Database connection not available")

            # Create attendance record
            attendance = Attendance(
                **attendance_data.dict(),
                check_in_time=datetime.utcnow(),
                marked_by=current_user["id"]
            )

            await db.attendance.insert_one(attendance.dict())
            return {"message": "Attendance marked successfully", "attendance_id": attendance.id}

        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to mark attendance: {str(e)}")

    @staticmethod
    async def biometric_attendance(attendance_data: BiometricAttendance):
        """Record attendance from biometric device"""
        try:
            db = get_db()
            if db is None:
                raise HTTPException(status_code=500, detail="Database connection not available")

            # Find user by biometric ID
            user = await db.users.find_one({"biometric_id": attendance_data.biometric_id, "is_active": True})
            if not user:
                raise HTTPException(status_code=404, detail="User with this biometric ID not found")

            # Create attendance record
            attendance = Attendance(
                student_id=user["id"],
                course_id="",  # Will be filled based on enrollment
                branch_id=user.get("branch_id", ""),
                attendance_date=attendance_data.timestamp,
                check_in_time=attendance_data.timestamp,
                method=AttendanceMethod.BIOMETRIC,
                notes=f"Biometric check-in from device {attendance_data.device_id}"
            )

            await db.attendance.insert_one(attendance.dict())
            return {"message": "Attendance marked successfully", "attendance_id": attendance.id}

        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to record biometric attendance: {str(e)}")

    @staticmethod
    async def export_attendance_reports(
        student_id: Optional[str] = None,
        coach_id: Optional[str] = None,
        course_id: Optional[str] = None,
        branch_id: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        format: str = "csv",
        current_user: dict = None
    ):
        """Export attendance reports"""
        try:
            # Get attendance data
            attendance_data = await AttendanceController.get_attendance_reports(
                student_id, coach_id, course_id, branch_id, start_date, end_date, current_user
            )

            if format == "csv":
                # Create CSV content
                output = io.StringIO()
                writer = csv.DictWriter(output, fieldnames=[
                    'student_name', 'course_name', 'branch_name', 'attendance_date',
                    'check_in_time', 'check_out_time', 'is_present', 'method', 'notes'
                ])
                writer.writeheader()
                writer.writerows(attendance_data["attendance_records"])

                return {
                    "content": output.getvalue(),
                    "filename": f"attendance_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    "content_type": "text/csv"
                }
            else:
                raise HTTPException(status_code=400, detail="Unsupported export format")

        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to export attendance reports: {str(e)}")
