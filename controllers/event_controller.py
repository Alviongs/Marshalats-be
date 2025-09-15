from fastapi import HTTPException, Depends, status

from models.event_models import EventCreate, Event
from models.user_models import UserRole
from utils.auth import require_role, get_current_active_user
from utils.database import db
from utils.helpers import serialize_doc

class EventController:
    @staticmethod
    async def create_event(
        event_data: EventCreate,
        current_user: dict = Depends(require_role([UserRole.SUPER_ADMIN, UserRole.COACH_ADMIN]))
    ):
        """Create a new branch event."""
        if not current_user.get("branch_id"):
            raise HTTPException(status_code=400, detail="User is not assigned to a branch.")

        event = Event(
            **event_data.dict(),
            branch_id=current_user["branch_id"],
            created_by=current_user["id"]
        )
        await db.events.insert_one(event.dict())
        return event

    @staticmethod
    async def get_events(
        branch_id: str,
        current_user: dict = Depends(get_current_active_user)
    ):
        """Get events for a specific branch."""
        events = await db.events.find({"branch_id": branch_id}).to_list(1000)
        return {"events": serialize_doc(events)}

    @staticmethod
    async def update_event(
        event_id: str,
        event_data: EventCreate,
        current_user: dict = Depends(require_role([UserRole.SUPER_ADMIN, UserRole.COACH_ADMIN]))
    ):
        """Update a branch event."""
        event = await db.events.find_one({"id": event_id})
        if not event:
            raise HTTPException(status_code=404, detail="Event not found")

        if event["branch_id"] != current_user.get("branch_id"):
            raise HTTPException(status_code=403, detail="You can only manage events for your own branch.")

        await db.events.update_one(
            {"id": event_id},
            {"$set": event_data.dict()}
        )
        return {"message": "Event updated successfully"}

    @staticmethod
    async def delete_event(
        event_id: str,
        current_user: dict = Depends(require_role([UserRole.SUPER_ADMIN, UserRole.COACH_ADMIN]))
    ):
        """Delete a branch event."""
        event = await db.events.find_one({"id": event_id})
        if not event:
            raise HTTPException(status_code=404, detail="Event not found")

        if event["branch_id"] != current_user.get("branch_id"):
            raise HTTPException(status_code=403, detail="You can only manage events for your own branch.")

        await db.events.delete_one({"id": event_id})
        return
