from fastapi import HTTPException, status
from typing import List, Optional, Dict, Any
from datetime import datetime
import uuid

from models.message_models import (
    Message, MessageThread, MessageCreate, MessageUpdate, MessageResponse,
    ConversationResponse, MessageStats, BulkMessageCreate, MessageSearchQuery,
    MessageStatus, MessagePriority, UserType, MessageParticipant
)
from models.user_models import UserRole
from models.notification_models import MessageNotification, MessageNotificationCreate
from utils.database import get_db
from utils.helpers import serialize_doc, log_activity

class MessageController:
    
    @staticmethod
    async def send_message(message_data: MessageCreate, current_user: dict) -> dict:
        """Send a new message with role-based access control"""
        db = get_db()

        try:
            # Get sender information
            sender_id = current_user["id"]
            sender_role = current_user["role"]
            sender_name = current_user.get("full_name", f"{current_user.get('first_name', '')} {current_user.get('last_name', '')}")
            sender_email = current_user.get("email", "")
            sender_branch_id = current_user.get("branch_id")
            
            # Map user roles to message user types
            role_mapping = {
                "student": UserType.STUDENT,
                "coach": UserType.COACH,
                "branch_manager": UserType.BRANCH_MANAGER,
                "super_admin": UserType.SUPERADMIN,
                "superadmin": UserType.SUPERADMIN
            }
            
            sender_type = role_mapping.get(sender_role, UserType.STUDENT)
            
            # Determine if this is a reply (has reply_to_message_id or thread_id)
            is_reply = bool(message_data.reply_to_message_id or message_data.thread_id)

            # Get recipient information and validate access
            recipient = await MessageController._get_and_validate_recipient(
                message_data.recipient_id, message_data.recipient_type, current_user, is_reply
            )
            
            # Find existing thread or create new one
            thread_id = message_data.thread_id  # Use provided thread_id if available

            # If no thread_id provided, check if this is a reply to an existing message
            if not thread_id and message_data.reply_to_message_id:
                original_message = await db.messages.find_one({"id": message_data.reply_to_message_id})
                if original_message:
                    thread_id = original_message.get("thread_id")

            # If no thread_id from reply, check for existing conversation between same participants
            if not thread_id:
                # Normalize subject by removing "Re:" prefixes for thread matching
                base_subject = message_data.subject
                if base_subject.startswith("Re: "):
                    base_subject = base_subject[4:]

                # Look for existing thread between these participants with same base subject
                existing_thread = await db.message_threads.find_one({
                    "$and": [
                        {
                            "participants.user_id": {"$all": [sender_id, message_data.recipient_id]}
                        },
                        {
                            "participants": {"$size": 2}  # Ensure exactly 2 participants
                        },
                        {
                            "$or": [
                                {"subject": base_subject},
                                {"subject": f"Re: {base_subject}"}
                            ]
                        },
                        {
                            "is_archived": {"$ne": True}
                        }
                    ]
                })

                if existing_thread:
                    thread_id = existing_thread["id"]

            if not thread_id:
                # Create new thread with normalized subject
                thread_subject = base_subject if 'base_subject' in locals() else message_data.subject
                thread = MessageThread(
                    subject=thread_subject,
                    participants=[
                        MessageParticipant(
                            user_id=sender_id,
                            user_type=sender_type,
                            user_name=sender_name,
                            user_email=sender_email,
                            branch_id=sender_branch_id
                        ),
                        MessageParticipant(
                            user_id=recipient["id"],
                            user_type=message_data.recipient_type,
                            user_name=recipient["name"],
                            user_email=recipient["email"],
                            branch_id=recipient.get("branch_id")
                        )
                    ],
                    allowed_branches=MessageController._get_allowed_branches(current_user, recipient)
                )
                
                thread_dict = thread.dict()
                await db.message_threads.insert_one(thread_dict)
                thread_id = thread.id
            
            # Create the message
            message = Message(
                thread_id=thread_id,
                sender_id=sender_id,
                sender_type=sender_type,
                sender_name=sender_name,
                sender_email=sender_email,
                sender_branch_id=sender_branch_id,
                recipient_id=message_data.recipient_id,
                recipient_type=message_data.recipient_type,
                recipient_name=recipient["name"],
                recipient_email=recipient["email"],
                recipient_branch_id=recipient.get("branch_id"),
                subject=message_data.subject,
                content=message_data.content,
                priority=message_data.priority,
                reply_to_message_id=message_data.reply_to_message_id,
                is_reply=bool(message_data.reply_to_message_id),
                allowed_branches=MessageController._get_allowed_branches(current_user, recipient)
            )
            
            message_dict = message.dict()
            await db.messages.insert_one(message_dict)
            
            # Update thread with latest message info
            await db.message_threads.update_one(
                {"id": thread_id},
                {
                    "$set": {
                        "last_message_id": message.id,
                        "last_message_at": message.created_at,
                        "last_sender_id": sender_id,
                        "updated_at": datetime.utcnow()
                    },
                    "$inc": {"message_count": 1}
                }
            )

            # Create notification for recipient
            await MessageController._create_message_notification(
                message=message,
                thread_id=thread_id,
                recipient=recipient,
                sender_data=current_user
            )

            # Log activity (skip for now since we don't have request object)
            # TODO: Add proper activity logging with request context
            # await log_activity(
            #     request, "message_sent", "success", sender_id, current_user.get("full_name"),
            #     {"message_id": message.id, "recipient_id": message_data.recipient_id}
            # )
            
            return {
                "message": "Message sent successfully",
                "message_id": message.id,
                "thread_id": thread_id
            }
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to send message: {str(e)}"
            )
    
    @staticmethod
    async def get_conversations(current_user: dict, skip: int = 0, limit: int = 50) -> dict:
        """Get user's conversations with role-based filtering"""
        db = get_db()
        
        try:
            user_id = current_user["id"]
            user_role = current_user["role"]
            user_branch_id = current_user.get("branch_id")
            
            # Build query to find conversations where user is a participant
            query = {
                "participants.user_id": user_id,
                "is_archived": {"$ne": True}  # Exclude archived conversations
            }

            # Add branch filtering for non-superadmin users
            if user_role != "super_admin" and user_role != "superadmin":
                if user_branch_id:
                    query["$or"] = [
                        {"allowed_branches": {"$in": [user_branch_id]}},
                        {"allowed_branches": {"$size": 0}},
                        {"allowed_branches": {"$exists": False}}
                    ]
            
            # Get conversations
            conversations_cursor = db.message_threads.find(query).sort("last_message_at", -1).skip(skip).limit(limit)
            conversations = await conversations_cursor.to_list(length=limit)
            
            # Get unread counts for each conversation
            conversation_responses = []
            for conv in conversations:
                # Get unread count for this user
                unread_count = await db.messages.count_documents({
                    "thread_id": conv["id"],
                    "recipient_id": user_id,
                    "is_read": False,
                    "is_deleted": False
                })
                
                # Get last message
                last_message = None
                if conv.get("last_message_id"):
                    last_msg_doc = await db.messages.find_one({"id": conv["last_message_id"]})
                    if last_msg_doc:
                        last_message = MessageResponse(**serialize_doc(last_msg_doc))
                
                conversation_responses.append(ConversationResponse(
                    thread_id=conv["id"],
                    subject=conv["subject"],
                    participants=[MessageParticipant(**p) for p in conv["participants"]],
                    message_count=conv.get("message_count", 0),
                    last_message=last_message,
                    last_message_at=conv.get("last_message_at"),
                    unread_count=unread_count,
                    is_archived=conv.get("is_archived", False),
                    created_at=conv["created_at"],
                    updated_at=conv["updated_at"]
                ))
            
            # Get total count
            total_count = await db.message_threads.count_documents(query)
            
            return {
                "conversations": [conv.dict() for conv in conversation_responses],
                "total_count": total_count,
                "skip": skip,
                "limit": limit
            }
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to get conversations: {str(e)}"
            )
    
    @staticmethod
    async def get_thread_messages(thread_id: str, current_user: dict, skip: int = 0, limit: int = 50) -> dict:
        """Get messages in a specific thread"""
        db = get_db()
        
        try:
            user_id = current_user["id"]
            
            # Verify user has access to this thread
            thread = await db.message_threads.find_one({"id": thread_id})
            if not thread:
                raise HTTPException(status_code=404, detail="Thread not found")
            
            # Check if user is a participant
            user_is_participant = any(p["user_id"] == user_id for p in thread["participants"])
            if not user_is_participant and current_user["role"] not in ["super_admin", "superadmin"]:
                raise HTTPException(status_code=403, detail="Access denied to this conversation")
            
            # Get messages in thread
            messages_cursor = db.messages.find({
                "thread_id": thread_id,
                "is_deleted": False
            }).sort("created_at", 1).skip(skip).limit(limit)
            
            messages = await messages_cursor.to_list(length=limit)
            
            # Mark messages as read if user is recipient
            message_ids_to_mark_read = []
            for msg in messages:
                if msg["recipient_id"] == user_id and not msg["is_read"]:
                    message_ids_to_mark_read.append(msg["id"])
            
            if message_ids_to_mark_read:
                await db.messages.update_many(
                    {"id": {"$in": message_ids_to_mark_read}},
                    {
                        "$set": {
                            "is_read": True,
                            "read_at": datetime.utcnow(),
                            "status": MessageStatus.READ,
                            "updated_at": datetime.utcnow()
                        }
                    }
                )
            
            # Convert to response format
            message_responses = [MessageResponse(**serialize_doc(msg)) for msg in messages]
            
            # Get total count
            total_count = await db.messages.count_documents({
                "thread_id": thread_id,
                "is_deleted": False
            })
            
            return {
                "messages": [msg.dict() for msg in message_responses],
                "thread": serialize_doc(thread),
                "total_count": total_count,
                "skip": skip,
                "limit": limit
            }
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to get thread messages: {str(e)}"
            )

    @staticmethod
    async def update_message(message_id: str, update_data: MessageUpdate, current_user: dict) -> dict:
        """Update message status (mark as read, archive, delete)"""
        db = get_db()

        try:
            user_id = current_user["id"]

            # Get the message
            message = await db.messages.find_one({"id": message_id})
            if not message:
                raise HTTPException(status_code=404, detail="Message not found")

            # Check if user has permission to update this message
            if message["recipient_id"] != user_id and current_user["role"] not in ["super_admin", "superadmin"]:
                raise HTTPException(status_code=403, detail="Access denied")

            # Prepare update data
            update_fields = {"updated_at": datetime.utcnow()}

            if update_data.is_read is not None:
                update_fields["is_read"] = update_data.is_read
                if update_data.is_read:
                    update_fields["read_at"] = datetime.utcnow()
                    update_fields["status"] = MessageStatus.READ

            if update_data.is_archived is not None:
                update_fields["is_archived"] = update_data.is_archived
                if update_data.is_archived:
                    update_fields["status"] = MessageStatus.ARCHIVED

            if update_data.is_deleted is not None:
                update_fields["is_deleted"] = update_data.is_deleted
                if update_data.is_deleted:
                    update_fields["status"] = MessageStatus.DELETED

            if update_data.status is not None:
                update_fields["status"] = update_data.status

            # Update the message
            await db.messages.update_one(
                {"id": message_id},
                {"$set": update_fields}
            )

            return {"message": "Message updated successfully"}

        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to update message: {str(e)}"
            )

    @staticmethod
    async def get_message_stats(current_user: dict) -> MessageStats:
        """Get message statistics for the current user"""
        db = get_db()

        try:
            user_id = current_user["id"]

            # Get various message counts
            total_messages = await db.messages.count_documents({
                "$or": [
                    {"sender_id": user_id},
                    {"recipient_id": user_id}
                ],
                "is_deleted": False
            })

            unread_messages = await db.messages.count_documents({
                "recipient_id": user_id,
                "is_read": False,
                "is_deleted": False
            })

            sent_messages = await db.messages.count_documents({
                "sender_id": user_id,
                "is_deleted": False
            })

            received_messages = await db.messages.count_documents({
                "recipient_id": user_id,
                "is_deleted": False
            })

            archived_messages = await db.messages.count_documents({
                "recipient_id": user_id,
                "is_archived": True,
                "is_deleted": False
            })

            deleted_messages = await db.messages.count_documents({
                "$or": [
                    {"sender_id": user_id},
                    {"recipient_id": user_id}
                ],
                "is_deleted": True
            })

            active_conversations = await db.message_threads.count_documents({
                "participants.user_id": user_id,
                "is_active": True
            })

            return MessageStats(
                total_messages=total_messages,
                unread_messages=unread_messages,
                sent_messages=sent_messages,
                received_messages=received_messages,
                archived_messages=archived_messages,
                deleted_messages=deleted_messages,
                active_conversations=active_conversations
            )

        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to get message stats: {str(e)}"
            )

    @staticmethod
    async def get_available_recipients(current_user: dict) -> dict:
        """Get list of users that current user can message based on role"""
        db = get_db()

        try:
            user_role = current_user["role"]
            user_branch_id = current_user.get("branch_id")
            recipients = []

            if user_role == "student":
                # Students can message coaches in their branch, branch manager, and superadmin
                print(f"🔍 DEBUG: Student user_branch_id: {user_branch_id}")
                print(f"🔍 DEBUG: Current user data: {current_user}")

                # For students, get branch_id from their enrollments if not directly available
                student_branch_ids = []
                if user_branch_id:
                    student_branch_ids.append(user_branch_id)
                else:
                    # Get branch IDs from student's active enrollments
                    user_id = current_user.get("id")
                    enrollments = await db.enrollments.find({
                        "student_id": user_id,
                        "is_active": True
                    }).to_list(length=None)
                    print(f"🔍 DEBUG: Found {len(enrollments)} active enrollments for student")

                    for enrollment in enrollments:
                        branch_id = enrollment.get("branch_id")
                        if branch_id and branch_id not in student_branch_ids:
                            student_branch_ids.append(branch_id)

                    print(f"🔍 DEBUG: Student branch IDs from enrollments: {student_branch_ids}")

                # If no branch IDs found, this might be a legacy student or data issue
                # In this case, we'll allow them to message any branch manager (fallback)
                if not student_branch_ids:
                    print("⚠️  WARNING: Student has no branch assignments. Using fallback to show all branch managers.")
                    # Get all active branch managers as fallback
                    all_branch_managers = await db.branch_managers.find({"is_active": True}).to_list(length=None)
                    for bm in all_branch_managers:
                        recipients.append({
                            "id": bm["id"],
                            "name": bm["full_name"],
                            "email": bm["email"],
                            "type": "branch_manager",
                            "branch_id": bm.get("branch_id")
                        })

                    # Also check users collection for branch managers
                    all_users_branch_managers = await db.users.find({"role": "branch_manager", "is_active": True}).to_list(length=None)
                    for bm in all_users_branch_managers:
                        if not any(r["id"] == bm["id"] for r in recipients):
                            recipients.append({
                                "id": bm["id"],
                                "name": bm["full_name"],
                                "email": bm["email"],
                                "type": "branch_manager",
                                "branch_id": bm.get("branch_id")
                            })

                # Get coaches and branch managers for all student's branches
                for branch_id in student_branch_ids:
                    # Get coaches in this branch
                    coaches = await db.coaches.find({
                        "branch_id": branch_id,
                        "is_active": True
                    }).to_list(length=None)
                    print(f"🔍 DEBUG: Found {len(coaches)} coaches in branch {branch_id}")

                    for coach in coaches:
                        # Avoid duplicates
                        if not any(r["id"] == coach["id"] for r in recipients):
                            recipients.append({
                                "id": coach["id"],
                                "name": coach["full_name"],
                                "email": coach["email"],
                                "type": "coach",
                                "branch_id": coach.get("branch_id")
                            })

                    # Get branch manager for this branch
                    branch = await db.branches.find_one({"id": branch_id})
                    if branch and branch.get("manager_id"):
                        branch_manager = await db.branch_managers.find_one({
                            "id": branch["manager_id"],
                            "is_active": True
                        })
                        if branch_manager:
                            # Avoid duplicates
                            if not any(r["id"] == branch_manager["id"] for r in recipients):
                                recipients.append({
                                    "id": branch_manager["id"],
                                    "name": branch_manager["full_name"],
                                    "email": branch_manager["email"],
                                    "type": "branch_manager",
                                    "branch_id": branch_id
                                })

                    # Also check if there are any branch managers for this branch in the users collection
                    branch_managers_in_users = await db.users.find({
                        "role": "branch_manager",
                        "branch_id": branch_id,
                        "is_active": True
                    }).to_list(length=None)

                    for bm in branch_managers_in_users:
                        if not any(r["id"] == bm["id"] for r in recipients):
                            recipients.append({
                                "id": bm["id"],
                                "name": bm["full_name"],
                                "email": bm["email"],
                                "type": "branch_manager",
                                "branch_id": branch_id
                            })

                # Add superadmins
                superadmins = await db.superadmins.find({"is_active": True}).to_list(length=None)
                print(f"🔍 DEBUG: Found {len(superadmins)} superadmins")
                for admin in superadmins:
                    recipients.append({
                        "id": admin["id"],
                        "name": admin["full_name"],
                        "email": admin["email"],
                        "type": "superadmin",
                        "branch_id": None
                    })

                print(f"🔍 DEBUG: Final recipients count for student: {len(recipients)}")
                for i, recipient in enumerate(recipients):
                    print(f"🔍 DEBUG: Recipient {i+1}: {recipient['name']} ({recipient['type']}) - Branch: {recipient.get('branch_id', 'None')}")

                # Additional debug: Check if we have any branch managers at all
                all_branch_managers = await db.branch_managers.find({"is_active": True}).to_list(length=None)
                print(f"🔍 DEBUG: Total active branch managers in system: {len(all_branch_managers)}")

                all_users_branch_managers = await db.users.find({"role": "branch_manager", "is_active": True}).to_list(length=None)
                print(f"🔍 DEBUG: Total active branch managers in users collection: {len(all_users_branch_managers)}")

                # Check branches table
                all_branches = await db.branches.find({}).to_list(length=None)
                print(f"🔍 DEBUG: Total branches in system: {len(all_branches)}")
                for branch in all_branches:
                    print(f"🔍 DEBUG: Branch {branch.get('name', 'Unknown')} (ID: {branch.get('id')}) - Manager ID: {branch.get('manager_id', 'None')}")

            elif user_role == "coach":
                # Coaches can message students in their branch, branch manager, and superadmin
                print(f"🔍 DEBUG: Coach recipients - User branch ID: {user_branch_id}")
                print(f"🔍 DEBUG: Coach full data: {current_user}")

                if user_branch_id:
                    # Get students in the same branch
                    students = await db.users.find({
                        "role": "student",
                        "branch_id": user_branch_id,
                        "is_active": True
                    }).to_list(length=None)

                    print(f"🔍 DEBUG: Found {len(students)} students in coach's branch ({user_branch_id})")
                    for student in students:
                        recipients.append({
                            "id": student["id"],
                            "name": student["full_name"],
                            "email": student["email"],
                            "type": "student",
                            "branch_id": student.get("branch_id")
                        })
                        print(f"🔍 DEBUG: Added student: {student['full_name']} (Branch: {student.get('branch_id')})")

                    # Get branch manager
                    branch = await db.branches.find_one({"id": user_branch_id})
                    if branch and branch.get("manager_id"):
                        branch_manager = await db.branch_managers.find_one({
                            "id": branch["manager_id"],
                            "is_active": True
                        })
                        if branch_manager:
                            recipients.append({
                                "id": branch_manager["id"],
                                "name": branch_manager["full_name"],
                                "email": branch_manager["email"],
                                "type": "branch_manager",
                                "branch_id": user_branch_id
                            })
                            print(f"🔍 DEBUG: Added branch manager: {branch_manager['full_name']}")
                        else:
                            print(f"🔍 DEBUG: No branch manager found for branch {user_branch_id}")
                    else:
                        print(f"🔍 DEBUG: Branch not found or no manager_id for branch {user_branch_id}")
                else:
                    print(f"⚠️ DEBUG: Coach has no branch_id assigned")
                    # Fallback: If coach has no branch_id, try to find it from coach record
                    coach_id = current_user.get("id")
                    if coach_id:
                        coach_record = await db.coaches.find_one({"id": coach_id})
                        if coach_record and coach_record.get("branch_id"):
                            fallback_branch_id = coach_record["branch_id"]
                            print(f"🔍 DEBUG: Found fallback branch_id from coach record: {fallback_branch_id}")

                            # Get students in the fallback branch
                            students = await db.users.find({
                                "role": "student",
                                "branch_id": fallback_branch_id,
                                "is_active": True
                            }).to_list(length=None)

                            print(f"🔍 DEBUG: Found {len(students)} students in coach's fallback branch ({fallback_branch_id})")
                            for student in students:
                                recipients.append({
                                    "id": student["id"],
                                    "name": student["full_name"],
                                    "email": student["email"],
                                    "type": "student",
                                    "branch_id": student.get("branch_id")
                                })
                                print(f"🔍 DEBUG: Added student (fallback): {student['full_name']} (Branch: {student.get('branch_id')})")

                            # Get branch manager for fallback branch
                            branch = await db.branches.find_one({"id": fallback_branch_id})
                            if branch and branch.get("manager_id"):
                                branch_manager = await db.branch_managers.find_one({
                                    "id": branch["manager_id"],
                                    "is_active": True
                                })
                                if branch_manager:
                                    recipients.append({
                                        "id": branch_manager["id"],
                                        "name": branch_manager["full_name"],
                                        "email": branch_manager["email"],
                                        "type": "branch_manager",
                                        "branch_id": fallback_branch_id
                                    })
                                    print(f"🔍 DEBUG: Added branch manager (fallback): {branch_manager['full_name']}")
                        else:
                            print(f"⚠️ DEBUG: No branch_id found in coach record either")

                # Add superadmins
                superadmins = await db.superadmins.find({"is_active": True}).to_list(length=None)
                print(f"🔍 DEBUG: Found {len(superadmins)} superadmins for coach")
                for admin in superadmins:
                    recipients.append({
                        "id": admin["id"],
                        "name": admin["full_name"],
                        "email": admin["email"],
                        "type": "superadmin",
                        "branch_id": None
                    })
                    print(f"🔍 DEBUG: Added superadmin: {admin['full_name']}")

                print(f"🔍 DEBUG: Total recipients for coach: {len(recipients)}")
                by_type = {}
                for r in recipients:
                    r_type = r["type"]
                    if r_type not in by_type:
                        by_type[r_type] = 0
                    by_type[r_type] += 1
                print(f"🔍 DEBUG: Coach recipients by type: {by_type}")

            elif user_role == "branch_manager":
                # Branch managers can message students and coaches in their branch, and superadmin
                managed_branches = await db.branches.find({
                    "manager_id": current_user["id"],
                    "is_active": True
                }).to_list(length=None)

                branch_ids = [branch["id"] for branch in managed_branches]

                if branch_ids:
                    # Get students in managed branches through enrollments
                    enrollments = await db.enrollments.find({
                        "branch_id": {"$in": branch_ids},
                        "is_active": True
                    }).to_list(length=None)

                    student_ids = list(set([enrollment["student_id"] for enrollment in enrollments]))

                    if student_ids:
                        students = await db.users.find({
                            "id": {"$in": student_ids},
                            "role": "student",
                            "is_active": True
                        }).to_list(length=None)

                        for student in students:
                            # Find the branch for this student from enrollments
                            student_enrollment = next((e for e in enrollments if e["student_id"] == student["id"]), None)
                            branch_id = student_enrollment["branch_id"] if student_enrollment else None

                            recipients.append({
                                "id": student["id"],
                                "name": student["full_name"],
                                "email": student["email"],
                                "type": "student",
                                "branch_id": branch_id
                            })

                    # Get coaches in managed branches
                    coaches = await db.coaches.find({
                        "branch_id": {"$in": branch_ids},
                        "is_active": True
                    }).to_list(length=None)

                    for coach in coaches:
                        recipients.append({
                            "id": coach["id"],
                            "name": coach["full_name"],
                            "email": coach["email"],
                            "type": "coach",
                            "branch_id": coach.get("branch_id")
                        })

                # Add superadmins
                superadmins = await db.superadmins.find({"is_active": True}).to_list(length=None)
                for admin in superadmins:
                    recipients.append({
                        "id": admin["id"],
                        "name": admin["full_name"],
                        "email": admin["email"],
                        "type": "superadmin",
                        "branch_id": None
                    })

            elif user_role in ["super_admin", "superadmin"]:
                # Superadmins can message anyone
                # Get all students
                students = await db.users.find({
                    "role": "student",
                    "is_active": True
                }).to_list(length=None)

                for student in students:
                    recipients.append({
                        "id": student["id"],
                        "name": student["full_name"],
                        "email": student["email"],
                        "type": "student",
                        "branch_id": student.get("branch_id")
                    })

                # Get all coaches
                coaches = await db.coaches.find({"is_active": True}).to_list(length=None)
                for coach in coaches:
                    recipients.append({
                        "id": coach["id"],
                        "name": coach["full_name"],
                        "email": coach["email"],
                        "type": "coach",
                        "branch_id": coach.get("branch_id")
                    })

                # Get all branch managers
                branch_managers = await db.branch_managers.find({"is_active": True}).to_list(length=None)
                print(f"🔍 DEBUG: Found {len(branch_managers)} branch managers for superadmin")
                for bm in branch_managers:
                    # Try multiple ways to get branch_id
                    branch_id = bm.get("branch_id") or bm.get("branch_assignment", {}).get("branch_id")
                    recipients.append({
                        "id": bm["id"],
                        "name": bm["full_name"],
                        "email": bm["email"],
                        "type": "branch_manager",
                        "branch_id": branch_id
                    })
                    print(f"🔍 DEBUG: Added branch manager: {bm['full_name']} (Branch ID: {branch_id})")

                # Also check users collection for branch managers
                users_branch_managers = await db.users.find({"role": "branch_manager", "is_active": True}).to_list(length=None)
                print(f"🔍 DEBUG: Found {len(users_branch_managers)} branch managers in users collection")
                for bm in users_branch_managers:
                    # Avoid duplicates
                    if not any(r["id"] == bm["id"] for r in recipients):
                        recipients.append({
                            "id": bm["id"],
                            "name": bm["full_name"],
                            "email": bm["email"],
                            "type": "branch_manager",
                            "branch_id": bm.get("branch_id")
                        })
                        print(f"🔍 DEBUG: Added branch manager from users: {bm['full_name']} (Branch ID: {bm.get('branch_id')})")

                print(f"🔍 DEBUG: Total recipients for superadmin: {len(recipients)}")
                by_type = {}
                for r in recipients:
                    r_type = r["type"]
                    if r_type not in by_type:
                        by_type[r_type] = 0
                    by_type[r_type] += 1
                print(f"🔍 DEBUG: Recipients by type: {by_type}")

            return {
                "recipients": recipients,
                "total_count": len(recipients)
            }

        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to get available recipients: {str(e)}"
            )

    @staticmethod
    async def _get_and_validate_recipient(recipient_id: str, recipient_type: UserType, current_user: dict, is_reply: bool = False) -> dict:
        """Get recipient information and validate if current user can message them"""
        db = get_db()

        user_role = current_user["role"]
        user_branch_id = current_user.get("branch_id")

        print(f"🔍 DEBUG: Validating recipient - User: {current_user.get('id')}, Role: {user_role}, Branch: {user_branch_id}")
        print(f"🔍 DEBUG: Recipient: {recipient_id}, Type: {recipient_type}, Is Reply: {is_reply}")
        print(f"🔍 DEBUG: Current user full data: {current_user}")

        # Get recipient based on type
        if recipient_type == UserType.STUDENT:
            recipient = await db.users.find_one({"id": recipient_id, "role": "student", "is_active": True})
            collection_name = "users"
        elif recipient_type == UserType.COACH:
            recipient = await db.coaches.find_one({"id": recipient_id, "is_active": True})
            collection_name = "coaches"
        elif recipient_type == UserType.BRANCH_MANAGER:
            recipient = await db.branch_managers.find_one({"id": recipient_id, "is_active": True})
            collection_name = "branch_managers"
        elif recipient_type == UserType.SUPERADMIN:
            recipient = await db.superadmins.find_one({"id": recipient_id, "is_active": True})
            collection_name = "superadmins"
        else:
            raise HTTPException(status_code=400, detail="Invalid recipient type")

        if not recipient:
            raise HTTPException(status_code=404, detail="Recipient not found")

        print(f"🔍 DEBUG: Found recipient: {recipient.get('full_name', 'Unknown')} (Branch: {recipient.get('branch_id', 'None')})")

        # Validate access based on user role
        if user_role == "student":
            # For students, get their branch IDs from enrollments
            student_branch_ids = []
            if user_branch_id:
                student_branch_ids.append(user_branch_id)
            else:
                # Get branch IDs from student's active enrollments
                user_id = current_user.get("id")
                enrollments = await db.enrollments.find({
                    "student_id": user_id,
                    "is_active": True
                }).to_list(length=None)

                for enrollment in enrollments:
                    branch_id = enrollment.get("branch_id")
                    if branch_id and branch_id not in student_branch_ids:
                        student_branch_ids.append(branch_id)

            # Students can only message coaches in their branch, their branch manager, or superadmin
            if recipient_type == UserType.COACH:
                recipient_branch_id = recipient.get("branch_id")
                if recipient_branch_id not in student_branch_ids:
                    raise HTTPException(status_code=403, detail="Cannot message coaches from other branches")
            elif recipient_type == UserType.BRANCH_MANAGER:
                # Check if this branch manager manages any of the student's branches
                valid_branch_manager = False
                for branch_id in student_branch_ids:
                    branch = await db.branches.find_one({"id": branch_id})
                    if branch and branch.get("manager_id") == recipient_id:
                        valid_branch_manager = True
                        break

                if not valid_branch_manager:
                    raise HTTPException(status_code=403, detail="Cannot message this branch manager")
            elif recipient_type == UserType.STUDENT:
                raise HTTPException(status_code=403, detail="Students cannot message other students")

        elif user_role == "coach":
            # Coaches can message students in their branch, their branch manager, or superadmin
            if recipient_type == UserType.STUDENT:
                # For replies, be more lenient with branch validation
                if is_reply:
                    print(f"🔍 DEBUG: This is a reply - allowing more lenient validation")
                    # For replies, we allow messaging if:
                    # 1. Coach has same branch as student, OR
                    # 2. Coach has no branch assignment (legacy data), OR
                    # 3. Student has no branch assignment (legacy data)
                    coach_branch = user_branch_id
                    student_branch = recipient.get("branch_id")

                    # Try to get coach branch from record if not in current_user
                    if not coach_branch:
                        coach_id = current_user.get("id")
                        if coach_id:
                            coach_record = await db.coaches.find_one({"id": coach_id})
                            if coach_record:
                                coach_branch = coach_record.get("branch_id")

                    print(f"🔍 DEBUG: Reply validation - Coach branch: {coach_branch}, Student branch: {student_branch}")

                    # Allow reply if either has no branch assignment or they match
                    if not coach_branch or not student_branch or coach_branch == student_branch:
                        print(f"✅ DEBUG: Reply allowed - branch validation passed")
                    else:
                        # For replies, check if there's an existing conversation between these users
                        # This allows replying to existing conversations even if branch assignments changed
                        print(f"🔍 DEBUG: Branch mismatch for reply, checking for existing conversation...")
                        existing_conversation = await db.message_threads.find_one({
                            "participants.user_id": {"$all": [current_user.get("id"), recipient_id]}
                        })

                        if existing_conversation:
                            print(f"✅ DEBUG: Found existing conversation, allowing reply despite branch mismatch")
                        else:
                            print(f"❌ DEBUG: No existing conversation found, blocking reply")
                            raise HTTPException(status_code=403, detail="Cannot reply to students from other branches")
                else:
                    # For new messages, enforce strict branch validation
                    print(f"🔍 DEBUG: This is a new message - enforcing strict validation")
                    if user_branch_id:
                        if recipient.get("branch_id") != user_branch_id:
                            raise HTTPException(status_code=403, detail="Cannot message students from other branches")
                    else:
                        # If coach has no branch_id, try to get it from coach record
                        coach_id = current_user.get("id")
                        if coach_id:
                            coach_record = await db.coaches.find_one({"id": coach_id})
                            if coach_record and coach_record.get("branch_id"):
                                coach_branch_id = coach_record["branch_id"]
                                if recipient.get("branch_id") != coach_branch_id:
                                    raise HTTPException(status_code=403, detail="Cannot message students from other branches")
                            else:
                                # If no branch assignment found, allow messaging (for legacy data)
                                print(f"⚠️ DEBUG: Coach {coach_id} has no branch assignment, allowing new message")
                        else:
                            raise HTTPException(status_code=403, detail="Coach authentication error")
            elif recipient_type == UserType.BRANCH_MANAGER:
                # Check if this branch manager manages the coach's branch
                effective_branch_id = user_branch_id
                if not effective_branch_id:
                    # Try to get branch_id from coach record
                    coach_id = current_user.get("id")
                    if coach_id:
                        coach_record = await db.coaches.find_one({"id": coach_id})
                        if coach_record and coach_record.get("branch_id"):
                            effective_branch_id = coach_record["branch_id"]

                if effective_branch_id:
                    branch = await db.branches.find_one({"id": effective_branch_id})
                    if not branch or branch.get("manager_id") != recipient_id:
                        raise HTTPException(status_code=403, detail="Cannot message this branch manager")
                else:
                    # If no branch assignment, allow messaging superadmin-level branch managers
                    print(f"⚠️ DEBUG: Coach has no branch assignment, allowing branch manager message for reply")
            elif recipient_type == UserType.COACH:
                raise HTTPException(status_code=403, detail="Coaches cannot message other coaches")

        elif user_role == "branch_manager":
            # Branch managers can message students and coaches in their managed branches, or superadmin
            if recipient_type in [UserType.STUDENT, UserType.COACH]:
                # Check if recipient is in a branch managed by this branch manager
                managed_branches = await db.branches.find({
                    "manager_id": current_user["id"],
                    "is_active": True
                }).to_list(length=None)

                managed_branch_ids = [branch["id"] for branch in managed_branches]
                recipient_branch_id = recipient.get("branch_id")

                if recipient_branch_id not in managed_branch_ids:
                    raise HTTPException(status_code=403, detail="Cannot message users from branches you don't manage")
            elif recipient_type == UserType.BRANCH_MANAGER:
                raise HTTPException(status_code=403, detail="Branch managers cannot message other branch managers")

        # Superadmins can message anyone (no restrictions)

        # Return recipient info
        return {
            "id": recipient["id"],
            "name": recipient.get("full_name", "Unknown"),
            "email": recipient.get("email", ""),
            "type": recipient_type.value,  # Add the type field
            "branch_id": recipient.get("branch_id") or recipient.get("branch_assignment", {}).get("branch_id")
        }

    @staticmethod
    def _get_allowed_branches(sender: dict, recipient: dict) -> List[str]:
        """Determine which branches should have access to this message thread"""
        branches = []

        # Add sender's branch
        if sender.get("branch_id"):
            branches.append(sender["branch_id"])

        # Add recipient's branch
        if recipient.get("branch_id"):
            branches.append(recipient["branch_id"])

        # Remove duplicates
        return list(set(branches))

    @staticmethod
    async def _create_message_notification(message: Message, thread_id: str, recipient: dict, sender_data: dict):
        """Create a notification for the message recipient"""
        try:
            db = get_db()

            # Determine notification type
            notification_type = "message_reply" if message.reply_to_message_id else "new_message"

            # Create notification title
            if notification_type == "new_message":
                title = f"New message from {sender_data.get('full_name', 'Unknown')}"
            else:
                title = f"Reply from {sender_data.get('full_name', 'Unknown')}"

            # Create notification
            notification = MessageNotification(
                message_id=message.id,
                thread_id=thread_id,
                recipient_id=recipient["id"],
                recipient_type=recipient["type"],
                sender_id=message.sender_id,
                sender_name=sender_data.get("full_name", "Unknown"),
                sender_type=message.sender_type.value,
                notification_type=notification_type,
                title=title,
                message=message.content[:200] + "..." if len(message.content) > 200 else message.content,
                subject=message.subject,
                priority=message.priority.value
            )

            # Insert notification into database
            await db.message_notifications.insert_one(notification.dict())

        except Exception as e:
            # Don't fail the message sending if notification creation fails
            print(f"Warning: Failed to create message notification: {str(e)}")

    @staticmethod
    async def get_message_notifications(current_user: dict, skip: int = 0, limit: int = 50) -> dict:
        """Get message notifications for the current user"""
        try:
            db = get_db()

            # Build query based on user type and ID
            query = {"recipient_id": current_user["id"]}

            # Get notifications with pagination
            notifications_cursor = db.message_notifications.find(query).sort("created_at", -1).skip(skip).limit(limit)
            notifications = await notifications_cursor.to_list(length=limit)

            # Get total count
            total_count = await db.message_notifications.count_documents(query)

            # Get unread count
            unread_count = await db.message_notifications.count_documents({**query, "is_read": False})

            # Serialize notifications
            serialized_notifications = [serialize_doc(notification) for notification in notifications]

            return {
                "notifications": serialized_notifications,
                "total": total_count,
                "unread_count": unread_count
            }

        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to get message notifications: {str(e)}"
            )

    @staticmethod
    async def mark_message_notification_as_read(notification_id: str, current_user: dict) -> dict:
        """Mark a message notification as read"""
        try:
            db = get_db()

            # Update notification
            result = await db.message_notifications.update_one(
                {"id": notification_id, "recipient_id": current_user["id"]},
                {
                    "$set": {
                        "is_read": True,
                        "read_at": datetime.utcnow()
                    }
                }
            )

            if result.matched_count == 0:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Notification not found"
                )

            return {"message": "Notification marked as read"}

        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to mark notification as read: {str(e)}"
            )
