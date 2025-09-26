from fastapi import HTTPException, Depends, status
from datetime import datetime, timedelta
import uuid
import secrets
import csv
import io
from typing import Optional

from models.payment_models import PaymentStatus, PaymentType, PaymentMethod, Payment, RegistrationPaymentCreate, RegistrationPaymentResponse
from models.student_models import StudentPaymentCreate, CoursePaymentInfo
from models.user_models import UserRole, UserCreate
from models.notification_models import PaymentNotification, PaymentNotificationCreate
from utils.auth import require_role
from utils.database import get_db
from utils.helpers import send_whatsapp

class PaymentController:
    @staticmethod
    async def student_process_payment(
        payment_data: StudentPaymentCreate,
        current_user: dict = Depends(require_role([UserRole.STUDENT]))
    ):
        """Allow a student to process a payment for their enrollment."""
        student_id = current_user["id"]

        # Validate enrollment and payment
        enrollment = await db.enrollments.find_one({"id": payment_data.enrollment_id, "student_id": student_id})
        if not enrollment:
            raise HTTPException(status_code=404, detail="Enrollment not found or does not belong to you.")

        # Find the pending payment for this enrollment
        # This assumes there's a specific pending payment the student is trying to clear
        # In a real system, you might have a more complex payment reconciliation logic
        pending_payment = await db.payments.find_one({
            "enrollment_id": payment_data.enrollment_id,
            "student_id": student_id,
            "payment_status": PaymentStatus.PENDING.value,
            "amount": payment_data.amount  # Ensure the amount matches
        })

        if not pending_payment:
            raise HTTPException(status_code=400, detail="No matching pending payment found for this enrollment and amount.")

        # Simulate payment gateway interaction (update payment status)
        update_data = {
            "payment_status": PaymentStatus.PAID,
            "payment_method": payment_data.payment_method,
            "transaction_id": payment_data.transaction_id,
            "payment_date": datetime.utcnow(),
            "notes": payment_data.notes,
            "updated_at": datetime.utcnow()
        }

        result = await db.payments.update_one(
            {"id": pending_payment["id"]},
            {"$set": update_data}
        )

        if result.matched_count == 0:
            raise HTTPException(status_code=500, detail="Failed to update payment status.")

        # Update enrollment payment status if needed (e.g., if all payments are cleared)
        # This logic might need to be more sophisticated in a real app
        await db.enrollments.update_one(
            {"id": enrollment["id"]},
            {"$set": {"payment_status": PaymentStatus.PAID}}  # Simplified: mark enrollment paid if this payment clears it
        )

        # Send payment confirmation
        await send_whatsapp(current_user["phone"], f"Payment of ₹{payment_data.amount} received for enrollment {payment_data.enrollment_id}. Thank you!")

        return {"message": "Payment processed successfully", "payment_id": pending_payment["id"]}

    @staticmethod
    async def get_course_payment_info(course_id: str, branch_id: str, duration: str):
        """Get payment information for a course"""
        try:
            db = get_db()

            if db is None:
                raise HTTPException(status_code=500, detail="Database connection not available")

            # Get course details
            course = await db.courses.find_one({"id": course_id})
            if not course:
                raise HTTPException(status_code=404, detail="Course not found")

            # Get branch details
            branch = await db.branches.find_one({"id": branch_id})
            if not branch:
                raise HTTPException(status_code=404, detail="Branch not found")

            # Get category details
            category = await db.categories.find_one({"id": course.get("category_id")}) if course.get("category_id") else None

            # Get duration details for pricing multiplier
            # Try to find by ID first, then by code
            duration_info = await db.durations.find_one({"id": duration})
            if not duration_info:
                duration_info = await db.durations.find_one({"code": duration})

            pricing_multiplier = duration_info.get("pricing_multiplier", 1.0) if duration_info else 1.0
            duration_name = duration_info.get("name", duration) if duration_info else duration

            # Calculate pricing - handle different pricing structures
            base_price = 15000  # Default base price
            if course.get("pricing"):
                if isinstance(course["pricing"], dict):
                    base_price = course["pricing"].get("amount", base_price)
                elif isinstance(course["pricing"], (int, float)):
                    base_price = course["pricing"]
            elif course.get("price"):
                base_price = course["price"]
            elif course.get("fee"):
                base_price = course["fee"]

            course_fee = float(base_price) * pricing_multiplier
            admission_fee = 500.0  # Fixed admission fee
            total_amount = course_fee + admission_fee

            # Import PaymentCalculation
            from models.student_models import PaymentCalculation

            # Create pricing calculation
            pricing = PaymentCalculation(
                course_fee=course_fee,
                admission_fee=admission_fee,
                total_amount=total_amount,
                currency="INR",
                duration_multiplier=pricing_multiplier
            )

            return CoursePaymentInfo(
                course_id=course_id,
                course_name=course.get("title", course.get("name", "Course")),
                category_name=category.get("name", "Category") if category else "Category",
                branch_name=branch.get("name", branch.get("branch", {}).get("name", "Branch")),
                duration=duration_name,
                pricing=pricing
            )

        except HTTPException:
            raise
        except Exception as e:
            print(f"Error in get_course_payment_info: {e}")
            raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

    @staticmethod
    async def process_registration_payment(payment_data: RegistrationPaymentCreate):
        """Process payment for student registration"""
        db = get_db()

        try:
            # Get payment information
            payment_info = await PaymentController.get_course_payment_info(
                payment_data.course_id,
                payment_data.branch_id,
                payment_data.duration
            )

            # Generate transaction ID
            transaction_id = f"TXN{datetime.utcnow().strftime('%Y%m%d')}{secrets.token_hex(4).upper()}"

            # Create user first
            from controllers.auth_controller import AuthController

            # Generate password if not provided
            if not payment_data.student_data.get("password"):
                payment_data.student_data["password"] = secrets.token_urlsafe(8)

            # Create user account
            user_create_data = UserCreate(**payment_data.student_data)
            user_result = await AuthController.register_user(user_create_data, None)
            student_id = user_result["user_id"]

            # Create enrollment record first to get enrollment_id
            enrollment_id = user_result.get("enrollment_id")
            if not enrollment_id:
                from models.enrollment_models import Enrollment

                enrollment = Enrollment(
                    student_id=student_id,
                    course_id=payment_data.course_id,
                    branch_id=payment_data.branch_id,
                    start_date=datetime.utcnow(),
                    end_date=datetime.utcnow() + timedelta(days=365),  # Default 1 year
                    fee_amount=payment_info.pricing.course_fee,
                    admission_fee=payment_info.pricing.admission_fee,
                    payment_status="paid",
                    enrollment_date=datetime.utcnow(),
                    is_active=True
                )

                await db.enrollments.insert_one(enrollment.dict())
                enrollment_id = enrollment.id

            # Create payment record with proper enrollment linking
            payment = Payment(
                student_id=student_id,
                enrollment_id=enrollment_id,  # Link payment to enrollment
                amount=payment_info.pricing.total_amount,
                payment_type=PaymentType.REGISTRATION_FEE,
                payment_method=payment_data.payment_method,
                payment_status=PaymentStatus.PAID,  # Simulate successful payment
                transaction_id=transaction_id,
                payment_date=datetime.utcnow(),
                due_date=datetime.utcnow() + timedelta(days=7),
                registration_data=payment_data.student_data,
                course_details={
                    "course_id": payment_data.course_id,
                    "course_name": payment_info.course_name,
                    "category_id": payment_data.category_id,
                    "duration": payment_data.duration
                },
                branch_details={
                    "branch_id": payment_data.branch_id,
                    "branch_name": payment_info.branch_name
                }
            )

            await db.payments.insert_one(payment.dict())

            # Create notification for superadmin
            student_data = {
                "id": student_id,
                "full_name": payment_data.student_data.get("full_name", ""),
                "email": payment_data.student_data.get("email", ""),
                "phone": payment_data.student_data.get("phone", "")
            }
            await PaymentController.create_payment_notification(
                payment.id, student_id, payment_info, student_data
            )

            # Send confirmation message
            phone = payment_data.student_data.get("phone", "")
            if phone:
                message = f"Welcome! Your registration is complete. Payment of ₹{payment_info.pricing.total_amount} received. Transaction ID: {transaction_id}"
                await send_whatsapp(phone, message)

            return RegistrationPaymentResponse(
                payment_id=payment.id,
                student_id=student_id,
                transaction_id=transaction_id,
                amount=payment_info.pricing.total_amount,
                status=PaymentStatus.PAID,
                message="Registration and payment completed successfully"
            )

        except Exception as e:
            # Handle payment failure
            raise HTTPException(
                status_code=400,
                detail=f"Payment processing failed: {str(e)}"
            )

    @staticmethod
    async def create_payment_notification(payment_id: str, student_id: str, payment_info: CoursePaymentInfo, student_data: dict):
        """Create notification for superadmin about new payment"""
        db = get_db()

        notification = PaymentNotification(
            payment_id=payment_id,
            student_id=student_id,
            notification_type="registration_payment",
            title="New Student Registration",
            message=f"New student {student_data.get('full_name', 'Unknown')} registered for {payment_info.course_name} with payment of ₹{payment_info.pricing.total_amount}",
            amount=payment_info.pricing.total_amount,
            course_name=payment_info.course_name,
            branch_name=payment_info.branch_name,
            priority="high"
        )

        await db.payment_notifications.insert_one(notification.dict())
        return notification

    @staticmethod
    async def get_payment_notifications(skip: int = 0, limit: int = 50):
        """Get payment notifications for superadmin dashboard"""
        try:
            db = get_db()

            if db is None:
                raise HTTPException(status_code=500, detail="Database connection not available")

            # Get notifications with proper error handling
            notifications = await db.payment_notifications.find(
                {},
                sort=[("created_at", -1)]
            ).skip(skip).limit(limit).to_list(limit)

            # Convert MongoDB documents to JSON-serializable format
            serialized_notifications = []
            for notification in notifications:
                # Convert ObjectId and datetime objects to strings
                serialized_notif = {}
                for key, value in notification.items():
                    if key == "_id":
                        continue  # Skip MongoDB ObjectId
                    elif hasattr(value, 'isoformat'):  # datetime objects
                        serialized_notif[key] = value.isoformat()
                    else:
                        serialized_notif[key] = value
                serialized_notifications.append(serialized_notif)

            return serialized_notifications

        except Exception as e:
            print(f"Error in get_payment_notifications: {e}")
            import traceback
            traceback.print_exc()
            # Return empty list instead of raising error for better UX
            return []

    @staticmethod
    async def mark_notification_read(notification_id: str):
        """Mark a notification as read"""
        db = get_db()

        result = await db.payment_notifications.update_one(
            {"id": notification_id},
            {
                "$set": {
                    "is_read": True,
                    "read_at": datetime.utcnow()
                }
            }
        )

        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Notification not found")

        return {"message": "Notification marked as read"}

    @staticmethod
    async def get_payment_stats(current_user: dict = None):
        """Get payment statistics for dashboard"""
        db = get_db()

        # Build base filter for role-based access
        base_filter = {}
        if current_user:
            current_role = current_user.get("role")
            if current_role == "student":
                # Students can only see their own payment stats
                student_id = current_user.get("id")
                if not student_id:
                    raise HTTPException(status_code=403, detail="Student ID not found")
                base_filter["student_id"] = student_id
            elif current_role == "branch_manager":
                # Branch managers can only see stats from their managed branches
                branch_manager_id = current_user.get("id")
                if not branch_manager_id:
                    raise HTTPException(status_code=403, detail="Branch manager ID not found")

                # Find all branches managed by this branch manager
                managed_branches = await db.branches.find({"manager_id": branch_manager_id, "is_active": True}).to_list(length=None)

                if not managed_branches:
                    return {
                        "total_collected": 0,
                        "pending_payments": 0,
                        "this_month_collection": 0,
                        "total_students": 0
                    }

                # Get all branch IDs managed by this branch manager
                managed_branch_ids = [branch["id"] for branch in managed_branches]
                print(f"Branch manager {branch_manager_id} manages branches for payment stats: {managed_branch_ids}")

                # Filter by branch_id in branch_details
                base_filter["branch_details.branch_id"] = {"$in": managed_branch_ids}

        # Get total collected (paid payments)
        total_collected_pipeline = [
            {"$match": {**base_filter, "payment_status": PaymentStatus.PAID.value}},
            {"$group": {"_id": None, "total": {"$sum": "$amount"}}}
        ]
        total_collected_result = await db.payments.aggregate(total_collected_pipeline).to_list(1)
        total_collected = total_collected_result[0]["total"] if total_collected_result else 0

        # Get pending payments
        pending_payments_pipeline = [
            {"$match": {**base_filter, "payment_status": PaymentStatus.PENDING.value}},
            {"$group": {"_id": None, "total": {"$sum": "$amount"}}}
        ]
        pending_payments_result = await db.payments.aggregate(pending_payments_pipeline).to_list(1)
        pending_payments = pending_payments_result[0]["total"] if pending_payments_result else 0

        # Get this month's collection
        from datetime import datetime
        current_month_start = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        this_month_pipeline = [
            {
                "$match": {
                    **base_filter,
                    "payment_status": PaymentStatus.PAID.value,
                    "payment_date": {"$gte": current_month_start}
                }
            },
            {"$group": {"_id": None, "total": {"$sum": "$amount"}}}
        ]
        this_month_result = await db.payments.aggregate(this_month_pipeline).to_list(1)
        this_month_collection = this_month_result[0]["total"] if this_month_result else 0

        # Get total students count (for branch managers, count students in their branches)
        if current_user and current_user.get("role") == "branch_manager":
            # Count students enrolled in courses at managed branches
            managed_branch_ids = base_filter.get("branch_details.branch_id", {}).get("$in", [])
            if managed_branch_ids:
                student_count = await db.enrollments.distinct("student_id", {"branch_id": {"$in": managed_branch_ids}, "is_active": True})
                total_students = len(student_count)
            else:
                total_students = 0
        else:
            total_students = await db.users.count_documents({"role": "student"})

        return {
            "total_collected": total_collected,
            "pending_payments": pending_payments,
            "this_month_collection": this_month_collection,
            "total_students": total_students
        }

    @staticmethod
    async def get_payments(skip: int = 0, limit: int = 50, status: str = None, payment_type: str = None, current_user: dict = None):
        """Get payments with filtering and student information"""
        try:
            db = get_db()

            if db is None:
                raise HTTPException(status_code=500, detail="Database connection not available")

            # Build filter query
            filter_query = {}
            if status and status != "all":
                filter_query["payment_status"] = status
            if payment_type and payment_type != "all":
                filter_query["payment_type"] = payment_type

            # Apply role-based filtering
            managed_branch_ids = None
            if current_user:
                current_role = current_user.get("role")
                if current_role == "student":
                    # Students can only see their own payments
                    student_id = current_user.get("id")
                    if not student_id:
                        raise HTTPException(status_code=403, detail="Student ID not found")
                    filter_query["student_id"] = student_id
                elif current_role == "branch_manager":
                    # Branch managers can only see payments from their managed branches
                    branch_manager_id = current_user.get("id")
                    if not branch_manager_id:
                        raise HTTPException(status_code=403, detail="Branch manager ID not found")

                    # Find all branches managed by this branch manager
                    managed_branches = await db.branches.find({"manager_id": branch_manager_id, "is_active": True}).to_list(length=None)

                    if not managed_branches:
                        return {"payments": []}

                    # Get all branch IDs managed by this branch manager
                    managed_branch_ids = [branch["id"] for branch in managed_branches]
                    print(f"Branch manager {branch_manager_id} manages branches for payments: {managed_branch_ids}")

                    # Filter payments by branch_id in branch_details
                    filter_query["branch_details.branch_id"] = {"$in": managed_branch_ids}

            # Get payments with student information
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
                    "$project": {
                        "id": 1,
                        "student_id": 1,
                        "student_name": {"$ifNull": ["$student_info.full_name", {"$concat": ["$student_info.first_name", " ", "$student_info.last_name"]}]},
                        "amount": 1,
                        "payment_type": 1,
                        "payment_method": 1,
                        "payment_status": 1,
                        "transaction_id": 1,
                        "payment_date": 1,
                        "course_name": {"$ifNull": ["$course_details.course_name", None]},
                        "branch_name": {"$ifNull": ["$branch_details.branch_name", None]},
                        "created_at": 1
                    }
                },
                {"$sort": {"created_at": -1}},
                {"$skip": skip},
                {"$limit": limit}
            ]

            payments = await db.payments.aggregate(pipeline).to_list(limit)

            # Convert MongoDB documents to JSON-serializable format
            serialized_payments = []
            for payment in payments:
                # Convert ObjectId and datetime objects to strings
                serialized_payment = {}
                for key, value in payment.items():
                    if key == "_id":
                        continue  # Skip MongoDB ObjectId
                    elif hasattr(value, 'isoformat'):  # datetime objects
                        serialized_payment[key] = value.isoformat()
                    else:
                        serialized_payment[key] = value
                serialized_payments.append(serialized_payment)

            return {"payments": serialized_payments}

        except Exception as e:
            print(f"Error in get_payments: {e}")
            import traceback
            traceback.print_exc()
            raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

    @staticmethod
    async def export_payments(
        status: Optional[str] = None,
        payment_type: Optional[str] = None,
        branch_id: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        format: str = "csv",
        current_user: dict = None
    ):
        """Export payment reports"""
        try:
            # Build filter query
            filter_query = {}
            if status and status != "all":
                filter_query["payment_status"] = status
            if payment_type and payment_type != "all":
                filter_query["payment_type"] = payment_type

            # Add date range filter if provided
            if start_date or end_date:
                date_filter = {}
                if start_date:
                    try:
                        start_dt = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
                        date_filter["$gte"] = start_dt
                    except ValueError:
                        raise HTTPException(status_code=400, detail="Invalid start_date format")
                if end_date:
                    try:
                        end_dt = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
                        date_filter["$lte"] = end_dt
                    except ValueError:
                        raise HTTPException(status_code=400, detail="Invalid end_date format")
                filter_query["payment_date"] = date_filter

            # Store role-based filtering info for pipeline
            role_based_branches = None
            additional_branch_filter = None

            if current_user:
                user_role = current_user.get("role")
                if user_role == UserRole.BRANCH_MANAGER.value:
                    # Branch managers can only see payments from their managed branches
                    managed_branches = current_user.get("managed_branches", [])
                    if managed_branches:
                        role_based_branches = managed_branches
                    else:
                        # If no managed branches, return empty result
                        filter_query["_id"] = {"$exists": False}
                elif user_role == UserRole.COACH_ADMIN.value:
                    # Coach admins can see payments from their assigned branches
                    assigned_branches = current_user.get("assigned_branches", [])
                    if assigned_branches:
                        role_based_branches = assigned_branches
                    else:
                        # If no assigned branches, return empty result
                        filter_query["_id"] = {"$exists": False}
                elif user_role == UserRole.STUDENT.value:
                    # Students can only see their own payments
                    filter_query["student_id"] = current_user.get("user_id")

            # Additional branch filter if specified
            if branch_id and branch_id != "all":
                additional_branch_filter = branch_id

            db = get_db()
            if db is None:
                raise HTTPException(status_code=500, detail="Database connection not available")

            # Get payments with student information for export
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
                        "from": "enrollments",
                        "localField": "enrollment_id",
                        "foreignField": "id",
                        "as": "enrollment_info"
                    }
                },
                {"$unwind": {"path": "$enrollment_info", "preserveNullAndEmptyArrays": True}},
                {
                    "$lookup": {
                        "from": "courses",
                        "localField": "enrollment_info.course_id",
                        "foreignField": "id",
                        "as": "course_info"
                    }
                },
                {"$unwind": {"path": "$course_info", "preserveNullAndEmptyArrays": True}},
                {
                    "$lookup": {
                        "from": "branches",
                        "localField": "enrollment_info.branch_id",
                        "foreignField": "id",
                        "as": "branch_info"
                    }
                },
                {"$unwind": {"path": "$branch_info", "preserveNullAndEmptyArrays": True}},
            ]

            # Add branch filtering after lookups if needed
            branch_filter_conditions = []
            if role_based_branches:
                branch_filter_conditions.extend([
                    {"branch_details.branch_id": {"$in": role_based_branches}},
                    {"enrollment_info.branch_id": {"$in": role_based_branches}}
                ])
            if additional_branch_filter:
                branch_filter_conditions.extend([
                    {"branch_details.branch_id": additional_branch_filter},
                    {"enrollment_info.branch_id": additional_branch_filter}
                ])

            if branch_filter_conditions:
                pipeline.append({"$match": {"$or": branch_filter_conditions}})

            # Add projection stage
            pipeline.extend([
                {
                    "$project": {
                        "student_name": {"$ifNull": ["$student_info.full_name", {"$concat": ["$student_info.first_name", " ", "$student_info.last_name"]}]},
                        "student_email": "$student_info.email",
                        "student_phone": "$student_info.phone",
                        "amount": 1,
                        "payment_type": 1,
                        "payment_method": 1,
                        "payment_status": 1,
                        "transaction_id": 1,
                        "payment_date": {"$dateToString": {"format": "%Y-%m-%d %H:%M:%S", "date": "$payment_date"}},
                        "due_date": {"$dateToString": {"format": "%Y-%m-%d", "date": "$due_date"}},
                        "course_name": {
                            "$ifNull": [
                                "$course_details.course_name",
                                {"$ifNull": ["$course_info.name", "N/A"]}
                            ]
                        },
                        "branch_name": {
                            "$ifNull": [
                                "$branch_details.branch_name",
                                {"$ifNull": ["$branch_info.branch.name", "N/A"]}
                            ]
                        },
                        "notes": {"$ifNull": ["$notes", ""]},
                        "created_at": {"$dateToString": {"format": "%Y-%m-%d %H:%M:%S", "date": "$created_at"}}
                    }
                },
                {"$sort": {"payment_date": -1, "created_at": -1}}
            ])

            payments = await db.payments.aggregate(pipeline).to_list(None)  # Get all matching records

            if format == "csv":
                # Create CSV content
                output = io.StringIO()
                fieldnames = [
                    'student_name', 'student_email', 'student_phone', 'amount', 'payment_type',
                    'payment_method', 'payment_status', 'transaction_id', 'payment_date',
                    'due_date', 'course_name', 'branch_name', 'notes', 'created_at'
                ]
                writer = csv.DictWriter(output, fieldnames=fieldnames)
                writer.writeheader()

                # Convert payments to CSV-friendly format
                for payment in payments:
                    csv_row = {}
                    for field in fieldnames:
                        value = payment.get(field, '')
                        # Handle None values and convert to string
                        csv_row[field] = str(value) if value is not None else ''
                    writer.writerow(csv_row)

                return {
                    "content": output.getvalue(),
                    "filename": f"payment_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    "content_type": "text/csv"
                }
            else:
                raise HTTPException(status_code=400, detail="Unsupported export format")

        except HTTPException:
            raise
        except Exception as e:
            print(f"Error in export_payments: {e}")
            import traceback
            traceback.print_exc()
            raise HTTPException(status_code=500, detail=f"Failed to export payment reports: {str(e)}")
