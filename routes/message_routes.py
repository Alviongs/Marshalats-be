from fastapi import APIRouter, Depends, Query, Path
from typing import Optional
from controllers.message_controller import MessageController
from models.message_models import MessageCreate, MessageUpdate, UserType
from models.user_models import UserRole
from utils.unified_auth import require_role_unified, get_current_user_or_superadmin

router = APIRouter()

@router.post("/send")
async def send_message(
    message_data: MessageCreate,
    current_user: dict = Depends(require_role_unified([UserRole.STUDENT, UserRole.COACH, UserRole.BRANCH_MANAGER, UserRole.SUPER_ADMIN]))
):
    """Send a new message - accessible by all authenticated users"""
    return await MessageController.send_message(message_data, current_user)

@router.get("/conversations")
async def get_conversations(
    skip: int = Query(0, ge=0, description="Number of conversations to skip"),
    limit: int = Query(50, ge=1, le=100, description="Number of conversations to return"),
    current_user: dict = Depends(require_role_unified([UserRole.STUDENT, UserRole.COACH, UserRole.BRANCH_MANAGER, UserRole.SUPER_ADMIN]))
):
    """Get user's conversations - accessible by all authenticated users"""
    return await MessageController.get_conversations(current_user, skip, limit)

@router.get("/thread/{thread_id}/messages")
async def get_thread_messages(
    thread_id: str = Path(..., description="Thread ID"),
    skip: int = Query(0, ge=0, description="Number of messages to skip"),
    limit: int = Query(50, ge=1, le=100, description="Number of messages to return"),
    current_user: dict = Depends(require_role_unified([UserRole.STUDENT, UserRole.COACH, UserRole.BRANCH_MANAGER, UserRole.SUPER_ADMIN]))
):
    """Get messages in a specific thread - accessible by all authenticated users"""
    return await MessageController.get_thread_messages(thread_id, current_user, skip, limit)

@router.patch("/message/{message_id}")
async def update_message(
    message_id: str = Path(..., description="Message ID"),
    update_data: MessageUpdate = ...,
    current_user: dict = Depends(require_role_unified([UserRole.STUDENT, UserRole.COACH, UserRole.BRANCH_MANAGER, UserRole.SUPER_ADMIN]))
):
    """Update message status (mark as read, archive, delete) - accessible by all authenticated users"""
    return await MessageController.update_message(message_id, update_data, current_user)

@router.get("/stats")
async def get_message_stats(
    current_user: dict = Depends(require_role_unified([UserRole.STUDENT, UserRole.COACH, UserRole.BRANCH_MANAGER, UserRole.SUPER_ADMIN]))
):
    """Get message statistics for current user - accessible by all authenticated users"""
    stats = await MessageController.get_message_stats(current_user)
    return {"stats": stats.dict()}

@router.get("/recipients")
async def get_available_recipients(
    current_user: dict = Depends(require_role_unified([UserRole.STUDENT, UserRole.COACH, UserRole.BRANCH_MANAGER, UserRole.SUPER_ADMIN]))
):
    """Get list of users that current user can message - accessible by all authenticated users"""
    return await MessageController.get_available_recipients(current_user)

# Additional endpoints for specific message operations

@router.post("/message/{message_id}/mark-read")
async def mark_message_as_read(
    message_id: str = Path(..., description="Message ID"),
    current_user: dict = Depends(require_role_unified([UserRole.STUDENT, UserRole.COACH, UserRole.BRANCH_MANAGER, UserRole.SUPER_ADMIN]))
):
    """Mark a specific message as read - accessible by all authenticated users"""
    update_data = MessageUpdate(is_read=True)
    return await MessageController.update_message(message_id, update_data, current_user)

@router.post("/message/{message_id}/archive")
async def archive_message(
    message_id: str = Path(..., description="Message ID"),
    current_user: dict = Depends(require_role_unified([UserRole.STUDENT, UserRole.COACH, UserRole.BRANCH_MANAGER, UserRole.SUPER_ADMIN]))
):
    """Archive a specific message - accessible by all authenticated users"""
    update_data = MessageUpdate(is_archived=True)
    return await MessageController.update_message(message_id, update_data, current_user)

@router.delete("/message/{message_id}")
async def delete_message(
    message_id: str = Path(..., description="Message ID"),
    current_user: dict = Depends(require_role_unified([UserRole.STUDENT, UserRole.COACH, UserRole.BRANCH_MANAGER, UserRole.SUPER_ADMIN]))
):
    """Delete a specific message - accessible by all authenticated users"""
    update_data = MessageUpdate(is_deleted=True)
    return await MessageController.update_message(message_id, update_data, current_user)

@router.get("/unread-count")
async def get_unread_message_count(
    current_user: dict = Depends(require_role_unified([UserRole.STUDENT, UserRole.COACH, UserRole.BRANCH_MANAGER, UserRole.SUPER_ADMIN]))
):
    """Get count of unread messages for current user - accessible by all authenticated users"""
    stats = await MessageController.get_message_stats(current_user)
    return {"unread_count": stats.unread_messages}

# Role-specific endpoints for enhanced functionality

@router.get("/students")
async def get_messageable_students(
    branch_id: Optional[str] = Query(None, description="Filter by branch ID"),
    current_user: dict = Depends(require_role_unified([UserRole.COACH, UserRole.BRANCH_MANAGER, UserRole.SUPER_ADMIN]))
):
    """Get students that current user can message - accessible by coaches, branch managers, and superadmin"""
    recipients = await MessageController.get_available_recipients(current_user)
    students = [r for r in recipients["recipients"] if r["type"] == "student"]
    
    if branch_id:
        students = [s for s in students if s.get("branch_id") == branch_id]
    
    return {
        "students": students,
        "total_count": len(students)
    }

@router.get("/coaches")
async def get_messageable_coaches(
    branch_id: Optional[str] = Query(None, description="Filter by branch ID"),
    current_user: dict = Depends(require_role_unified([UserRole.STUDENT, UserRole.BRANCH_MANAGER, UserRole.SUPER_ADMIN]))
):
    """Get coaches that current user can message - accessible by students, branch managers, and superadmin"""
    recipients = await MessageController.get_available_recipients(current_user)
    coaches = [r for r in recipients["recipients"] if r["type"] == "coach"]
    
    if branch_id:
        coaches = [c for c in coaches if c.get("branch_id") == branch_id]
    
    return {
        "coaches": coaches,
        "total_count": len(coaches)
    }

@router.get("/branch-managers")
async def get_messageable_branch_managers(
    current_user: dict = Depends(require_role_unified([UserRole.STUDENT, UserRole.COACH, UserRole.SUPER_ADMIN]))
):
    """Get branch managers that current user can message - accessible by students, coaches, and superadmin"""
    recipients = await MessageController.get_available_recipients(current_user)
    branch_managers = [r for r in recipients["recipients"] if r["type"] == "branch_manager"]
    
    return {
        "branch_managers": branch_managers,
        "total_count": len(branch_managers)
    }

@router.get("/superadmins")
async def get_messageable_superadmins(
    current_user: dict = Depends(require_role_unified([UserRole.STUDENT, UserRole.COACH, UserRole.BRANCH_MANAGER]))
):
    """Get superadmins that current user can message - accessible by students, coaches, and branch managers"""
    recipients = await MessageController.get_available_recipients(current_user)
    superadmins = [r for r in recipients["recipients"] if r["type"] == "superadmin"]
    
    return {
        "superadmins": superadmins,
        "total_count": len(superadmins)
    }

@router.get("/notifications")
async def get_message_notifications(
    skip: int = 0,
    limit: int = 50,
    current_user: dict = Depends(require_role_unified([UserRole.STUDENT, UserRole.COACH, UserRole.BRANCH_MANAGER, UserRole.SUPER_ADMIN]))
):
    """Get message notifications for the current user"""
    try:
        result = await MessageController.get_message_notifications(current_user, skip, limit)
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get message notifications: {str(e)}"
        )

@router.put("/notifications/{notification_id}/read")
async def mark_message_notification_as_read(
    notification_id: str,
    current_user: dict = Depends(require_role_unified([UserRole.STUDENT, UserRole.COACH, UserRole.BRANCH_MANAGER, UserRole.SUPER_ADMIN]))
):
    """Mark a message notification as read"""
    try:
        result = await MessageController.mark_message_notification_as_read(notification_id, current_user)
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to mark notification as read: {str(e)}"
        )
