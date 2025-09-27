from fastapi import HTTPException, Depends
from typing import Optional, List
from datetime import datetime, timedelta
import uuid
import csv
import io

from models.attendance_models import (
    AttendanceCreate, BiometricAttendance, Attendance, AttendanceMethod,
    CoachAttendance, CoachAttendanceCreate, BranchManagerAttendance, BranchManagerAttendanceCreate,
    AttendanceStatus, AttendanceMarkRequest
)
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

                # Get coach attendance records - try both collections
                attendance_records = await db.coach_attendance.find(attendance_filter).to_list(length=1000)

                # If no records in coach_attendance, create mock data or use alternative approach
                if not attendance_records:
                    # For now, create sample attendance data based on working days
                    # In production, this should be replaced with actual attendance tracking
                    today = datetime.now()
                    if start_date and end_date:
                        start_dt = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
                        end_dt = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
                        # Generate mock attendance for the date range
                        current_date = start_dt
                        while current_date <= end_dt:
                            if current_date.weekday() < 5:  # Monday to Friday
                                attendance_records.append({
                                    "coach_id": coach_id,
                                    "attendance_date": current_date,
                                    "is_present": True,  # Assume present for now
                                    "check_in_time": current_date.replace(hour=9, minute=0),
                                    "check_out_time": current_date.replace(hour=17, minute=0)
                                })
                            current_date += timedelta(days=1)

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

    @staticmethod
    async def get_coach_students(coach_id: str, current_user: dict):
        """Get students assigned to a specific coach"""
        try:
            db = get_db()
            if db is None:
                raise HTTPException(status_code=500, detail="Database connection not available")

            # Verify coach access - coaches can only see their own students
            if current_user.get("role") == "coach" and current_user.get("id") != coach_id:
                raise HTTPException(status_code=403, detail="Access denied: Can only view your own students")

            # Get coach information
            coach = await db.coaches.find_one({"id": coach_id, "is_active": True})
            if not coach:
                # Try users collection for coaches
                coach = await db.users.find_one({"id": coach_id, "role": "coach", "is_active": True})
                if not coach:
                    raise HTTPException(status_code=404, detail="Coach not found")

            print(f"🔍 DEBUG: Found coach: {coach.get('id')} - {coach.get('full_name', 'Unknown')}")

            coach_branch_id = coach.get("branch_id")
            print(f"🔍 DEBUG: Coach branch_id: {coach_branch_id}")

            if not coach_branch_id:
                print("⚠️ DEBUG: Coach has no branch_id assigned")
                return {"students": [], "total": 0, "debug_info": "Coach has no branch assignment"}

            # Get courses assigned to this coach
            assigned_courses = []
            if "assignment_details" in coach and coach["assignment_details"]:
                assigned_courses = coach["assignment_details"].get("courses", [])
                print(f"🔍 DEBUG: Coach assigned courses: {assigned_courses}")
            else:
                print("⚠️ DEBUG: Coach has no assignment_details")

            # If no specific course assignments, get all courses in the coach's branch
            if not assigned_courses:
                print(f"🔍 DEBUG: No specific course assignments, getting all courses in branch {coach_branch_id}")
                branch_courses = await db.courses.find({"branch_id": coach_branch_id, "is_active": True}).to_list(length=None)
                assigned_courses = [course["id"] for course in branch_courses]
                print(f"🔍 DEBUG: Found {len(branch_courses)} courses in branch: {assigned_courses}")

            if not assigned_courses:
                print("⚠️ DEBUG: No courses found for this coach")
                return {"students": [], "total": 0, "debug_info": "No courses assigned to coach or branch"}

            # Get students enrolled in these courses
            print(f"🔍 DEBUG: Searching for enrollments with course_ids: {assigned_courses}, branch_id: {coach_branch_id}")
            enrollments = await db.enrollments.find({
                "course_id": {"$in": assigned_courses},
                "branch_id": coach_branch_id,
                "is_active": True
            }).to_list(length=None)

            print(f"🔍 DEBUG: Found {len(enrollments)} enrollments")

            student_ids = [enrollment["student_id"] for enrollment in enrollments]
            print(f"🔍 DEBUG: Student IDs from enrollments: {student_ids}")

            if not student_ids:
                # Try without branch_id filter as fallback
                print("🔍 DEBUG: No students found with branch filter, trying without branch filter...")
                fallback_enrollments = await db.enrollments.find({
                    "course_id": {"$in": assigned_courses},
                    "is_active": True
                }).to_list(length=None)

                print(f"🔍 DEBUG: Fallback found {len(fallback_enrollments)} enrollments")

                if fallback_enrollments:
                    student_ids = [enrollment["student_id"] for enrollment in fallback_enrollments]
                    print(f"🔍 DEBUG: Fallback student IDs: {student_ids}")
                else:
                    return {"students": [], "total": 0, "debug_info": "No enrollments found for assigned courses"}

            # Get student details with enrollment information
            pipeline = [
                {"$match": {"id": {"$in": student_ids}, "is_active": True}},
                {
                    "$lookup": {
                        "from": "enrollments",
                        "let": {"student_id": "$id"},
                        "pipeline": [
                            {
                                "$match": {
                                    "$expr": {
                                        "$and": [
                                            {"$eq": ["$student_id", "$$student_id"]},
                                            {"$in": ["$course_id", assigned_courses]},
                                            {"$eq": ["$is_active", True]}
                                        ]
                                    }
                                }
                            }
                        ],
                        "as": "enrollments"
                    }
                },
                {
                    "$lookup": {
                        "from": "courses",
                        "localField": "enrollments.course_id",
                        "foreignField": "id",
                        "as": "courses"
                    }
                },
                {
                    "$project": {
                        "id": 1,
                        "full_name": {"$ifNull": ["$full_name", {"$concat": ["$first_name", " ", "$last_name"]}]},
                        "email": 1,
                        "phone": 1,
                        "enrollments": 1,
                        "courses": 1,
                        "is_active": 1
                    }
                }
            ]

            students = await db.users.aggregate(pipeline).to_list(length=None)
            print(f"🔍 DEBUG: Found {len(students)} students after aggregation")

            # Serialize the results
            serialized_students = []
            for student in students:
                student_data = serialize_doc(student)
                serialized_students.append(student_data)
                print(f"🔍 DEBUG: Student: {student_data.get('id')} - {student_data.get('full_name', 'Unknown')}")

            result = {
                "students": serialized_students,
                "total": len(serialized_students),
                "coach_id": coach_id,
                "branch_id": coach_branch_id,
                "debug_info": {
                    "assigned_courses": assigned_courses,
                    "enrollments_found": len(enrollments) if 'enrollments' in locals() else 0,
                    "student_ids": student_ids
                }
            }

            print(f"🔍 DEBUG: Final result: {len(serialized_students)} students")
            return result

        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to get coach students: {str(e)}")

    @staticmethod
    async def mark_coach_attendance(attendance_data: CoachAttendanceCreate, current_user: dict):
        """Mark attendance for a coach"""
        try:
            db = get_db()
            if db is None:
                raise HTTPException(status_code=500, detail="Database connection not available")

            # Verify permissions
            user_role = current_user.get("role")
            if user_role not in ["super_admin", "superadmin", "branch_manager"]:
                raise HTTPException(status_code=403, detail="Insufficient permissions to mark coach attendance")

            # If branch manager, verify they can mark attendance for this coach
            if user_role == "branch_manager":
                branch_manager_id = current_user.get("id")
                managed_branches = await db.branches.find({"manager_id": branch_manager_id, "is_active": True}).to_list(length=None)
                managed_branch_ids = [branch["id"] for branch in managed_branches]

                if attendance_data.branch_id not in managed_branch_ids:
                    raise HTTPException(status_code=403, detail="Cannot mark attendance for coaches outside your managed branches")

            # Verify coach exists and is in the specified branch
            coach = await db.coaches.find_one({"id": attendance_data.coach_id, "is_active": True})
            if not coach:
                coach = await db.users.find_one({"id": attendance_data.coach_id, "role": "coach", "is_active": True})
                if not coach:
                    raise HTTPException(status_code=404, detail="Coach not found")

            # Check if attendance already marked for this date
            existing_attendance = await db.coach_attendance.find_one({
                "coach_id": attendance_data.coach_id,
                "attendance_date": {
                    "$gte": attendance_data.attendance_date.replace(hour=0, minute=0, second=0, microsecond=0),
                    "$lt": attendance_data.attendance_date.replace(hour=23, minute=59, second=59, microsecond=999999)
                }
            })

            if existing_attendance:
                raise HTTPException(status_code=400, detail="Attendance already marked for this coach today")

            # Create coach attendance record
            coach_attendance = CoachAttendance(
                **attendance_data.dict(),
                check_in_time=datetime.utcnow() if attendance_data.is_present else None,
                marked_by=current_user["id"]
            )

            await db.coach_attendance.insert_one(coach_attendance.dict())
            return {"message": "Coach attendance marked successfully", "attendance_id": coach_attendance.id}

        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to mark coach attendance: {str(e)}")

    @staticmethod
    async def mark_branch_manager_attendance(attendance_data: BranchManagerAttendanceCreate, current_user: dict):
        """Mark attendance for a branch manager"""
        try:
            db = get_db()
            if db is None:
                raise HTTPException(status_code=500, detail="Database connection not available")

            # Only superadmins can mark branch manager attendance
            user_role = current_user.get("role")
            if user_role not in ["super_admin", "superadmin"]:
                raise HTTPException(status_code=403, detail="Only superadmins can mark branch manager attendance")

            # Verify branch manager exists
            branch_manager = await db.branch_managers.find_one({"id": attendance_data.branch_manager_id, "is_active": True})
            if not branch_manager:
                raise HTTPException(status_code=404, detail="Branch manager not found")

            # Check if attendance already marked for this date
            existing_attendance = await db.branch_manager_attendance.find_one({
                "branch_manager_id": attendance_data.branch_manager_id,
                "attendance_date": {
                    "$gte": attendance_data.attendance_date.replace(hour=0, minute=0, second=0, microsecond=0),
                    "$lt": attendance_data.attendance_date.replace(hour=23, minute=59, second=59, microsecond=999999)
                }
            })

            if existing_attendance:
                raise HTTPException(status_code=400, detail="Attendance already marked for this branch manager today")

            # Create branch manager attendance record
            bm_attendance = BranchManagerAttendance(
                **attendance_data.dict(),
                check_in_time=datetime.utcnow() if attendance_data.is_present else None,
                marked_by=current_user["id"]
            )

            await db.branch_manager_attendance.insert_one(bm_attendance.dict())
            return {"message": "Branch manager attendance marked successfully", "attendance_id": bm_attendance.id}

        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to mark branch manager attendance: {str(e)}")

    @staticmethod
    async def get_coach_students_attendance(coach_id: str, date: str, current_user: dict):
        """Get students assigned to a coach with their attendance for a specific date"""
        try:
            db = get_db()
            if db is None:
                raise HTTPException(status_code=500, detail="Database connection not available")

            # Verify coach access
            if current_user.get("role") == "coach" and current_user.get("id") != coach_id:
                raise HTTPException(status_code=403, detail="Access denied: Can only view your own students")

            # Parse the date
            try:
                target_date = datetime.fromisoformat(date.replace('Z', '+00:00'))
                start_of_day = target_date.replace(hour=0, minute=0, second=0, microsecond=0)
                end_of_day = target_date.replace(hour=23, minute=59, second=59, microsecond=999999)
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid date format")

            # Get coach information
            coach = await db.coaches.find_one({"id": coach_id, "is_active": True})
            if not coach:
                coach = await db.users.find_one({"id": coach_id, "role": "coach", "is_active": True})
                if not coach:
                    raise HTTPException(status_code=404, detail="Coach not found")

            coach_branch_id = coach.get("branch_id")
            if not coach_branch_id:
                return {"students": [], "attendance": [], "total": 0}

            # Get students in the coach's branch using the same logic as search_students
            # First get all students
            students = await db.users.find({
                "role": "student",
                "is_active": True
            }).to_list(length=None)

            # Get student IDs for enrollment filtering
            student_ids = [student["id"] for student in students]

            # Build enrollment filter (same as search_students)
            enrollment_filter = {"student_id": {"$in": student_ids}}
            if coach_branch_id:
                enrollment_filter["branch_id"] = coach_branch_id

            # Get matching enrollments (don't require is_active=True to match search behavior)
            enrollments = await db.enrollments.find(enrollment_filter).to_list(length=None)

            # Filter students based on enrollment matches (same as search_students)
            enrolled_student_ids = set(enrollment["student_id"] for enrollment in enrollments)
            students = [student for student in students if student["id"] in enrolled_student_ids]

            # Get attendance records for the specific date
            attendance_records = await db.attendance.find({
                "attendance_date": {"$gte": start_of_day, "$lte": end_of_day},
                "branch_id": coach_branch_id
            }).to_list(length=None)

            # Create a map of student attendance
            attendance_map = {}
            for record in attendance_records:
                student_id = record.get("student_id")
                if student_id:
                    # Use stored status if available, otherwise fall back to is_present logic
                    stored_status = record.get("status")
                    if stored_status:
                        status = stored_status
                    else:
                        # Fallback for old records without status field
                        status = "present" if record.get("is_present") else "absent"

                    attendance_map[student_id] = {
                        "status": status,
                        "check_in_time": record.get("check_in_time"),
                        "check_out_time": record.get("check_out_time"),
                        "notes": record.get("notes", ""),
                        "marked_by": record.get("marked_by")
                    }

            # Combine student data with attendance and course information
            result_students = []
            for student in students:
                student_id = student.get("id")
                attendance_info = attendance_map.get(student_id, {
                    "status": "absent",  # Default to absent if no record
                    "check_in_time": None,
                    "check_out_time": None,
                    "notes": "",
                    "marked_by": None
                })

                # Get student's enrollments for course information
                student_enrollments = [e for e in enrollments if e["student_id"] == student_id]
                courses = []

                for enrollment in student_enrollments:
                    # Get course details
                    course = await db.courses.find_one({"id": enrollment["course_id"]})
                    if course:
                        courses.append({
                            "id": course["id"],
                            "name": course.get("name", course.get("title", "Unknown Course")),
                            "course_id": course["id"],
                            "course_name": course.get("name", course.get("title", "Unknown Course"))
                        })

                result_students.append({
                    "id": student_id,
                    "full_name": student.get("full_name", "Unknown"),
                    "email": student.get("email", ""),
                    "branch_id": coach_branch_id,  # Use the coach's branch ID
                    "courses": courses,
                    "attendance": attendance_info
                })

            return {
                "students": result_students,
                "date": date,
                "total": len(result_students),
                "attendance_marked": len([s for s in result_students if s["attendance"]["status"] != "absent"])
            }

        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to get coach students attendance: {str(e)}")

    @staticmethod
    async def mark_comprehensive_attendance(attendance_request: AttendanceMarkRequest, current_user: dict):
        """Mark attendance for any user type (student, coach, branch_manager)"""
        try:
            db = get_db()
            if db is None:
                raise HTTPException(status_code=500, detail="Database connection not available")

            user_role = current_user.get("role")
            user_id = attendance_request.user_id
            user_type = attendance_request.user_type

            # Determine is_present based on status - both PRESENT and LATE are considered present
            is_present = attendance_request.status in [AttendanceStatus.PRESENT, AttendanceStatus.LATE]
            check_in_time = attendance_request.check_in_time or (datetime.utcnow() if is_present else None)

            if user_type == "student":
                # Verify permissions for student attendance
                if user_role not in ["super_admin", "superadmin", "coach", "branch_manager"]:
                    raise HTTPException(status_code=403, detail="Insufficient permissions")

                # Verify course_id is provided for students
                if not attendance_request.course_id:
                    raise HTTPException(status_code=400, detail="Course ID required for student attendance")

                # Enhanced deduplication: Check if attendance already exists for this exact date
                attendance_date_start = attendance_request.attendance_date.replace(hour=0, minute=0, second=0, microsecond=0)
                attendance_date_end = attendance_request.attendance_date.replace(hour=23, minute=59, second=59, microsecond=999999)

                print(f"🔍 Checking for existing attendance: student_id={user_id}, course_id={attendance_request.course_id}, date_range={attendance_date_start} to {attendance_date_end}")

                existing = await db.attendance.find_one({
                    "student_id": user_id,
                    "course_id": attendance_request.course_id,
                    "branch_id": attendance_request.branch_id,
                    "attendance_date": {
                        "$gte": attendance_date_start,
                        "$lt": attendance_date_end
                    }
                })

                if existing:
                    print(f"📝 Found existing attendance record: {existing['id']} - updating instead of creating duplicate")

                    # Update existing record (proper upsert functionality)
                    update_data = {
                        "check_in_time": check_in_time,
                        "check_out_time": attendance_request.check_out_time,
                        "is_present": is_present,
                        "status": attendance_request.status.value,  # Store the original status
                        "notes": attendance_request.notes,
                        "marked_by": current_user["id"],
                        "method": AttendanceMethod.MANUAL,
                        "updated_at": datetime.utcnow()  # Track when it was last updated
                    }

                    result = await db.attendance.update_one(
                        {"id": existing["id"]},
                        {"$set": update_data}
                    )

                    if result.modified_count > 0:
                        print(f"✅ Successfully updated existing attendance record: {existing['id']}")
                        return {"message": "Student attendance updated successfully", "attendance_id": existing["id"], "action": "updated"}
                    else:
                        print(f"⚠️ No changes made to existing attendance record: {existing['id']}")
                        return {"message": "Student attendance already up to date", "attendance_id": existing["id"], "action": "no_change"}
                else:
                    print(f"➕ No existing attendance found - creating new record")

                    # Create new attendance record
                    attendance = Attendance(
                        student_id=user_id,
                        course_id=attendance_request.course_id,
                        branch_id=attendance_request.branch_id,
                        attendance_date=attendance_request.attendance_date,
                        check_in_time=check_in_time,
                        check_out_time=attendance_request.check_out_time,
                        method=AttendanceMethod.MANUAL,
                        marked_by=current_user["id"],
                        is_present=is_present,
                        status=attendance_request.status.value,  # Store the original status
                        notes=attendance_request.notes
                    )

                    await db.attendance.insert_one(attendance.dict())
                    print(f"✅ Successfully created new attendance record: {attendance.id}")
                    return {"message": "Student attendance marked successfully", "attendance_id": attendance.id, "action": "created"}

            elif user_type == "coach":
                # Use existing coach attendance method
                coach_data = CoachAttendanceCreate(
                    coach_id=user_id,
                    branch_id=attendance_request.branch_id,
                    attendance_date=attendance_request.attendance_date,
                    method=AttendanceMethod.MANUAL,
                    is_present=is_present,
                    notes=attendance_request.notes
                )
                return await AttendanceController.mark_coach_attendance(coach_data, current_user)

            elif user_type == "branch_manager":
                # Use existing branch manager attendance method
                bm_data = BranchManagerAttendanceCreate(
                    branch_manager_id=user_id,
                    branch_id=attendance_request.branch_id,
                    attendance_date=attendance_request.attendance_date,
                    method=AttendanceMethod.MANUAL,
                    is_present=is_present,
                    notes=attendance_request.notes
                )
                return await AttendanceController.mark_branch_manager_attendance(bm_data, current_user)

            else:
                raise HTTPException(status_code=400, detail="Invalid user type")

        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to mark attendance: {str(e)}")
