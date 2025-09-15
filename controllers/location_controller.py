from fastapi import HTTPException, Depends
from typing import Optional, List
from datetime import datetime

from models.location_models import LocationCreate, LocationUpdate, Location, LocationWithBranches, LocationResponse
from models.user_models import UserRole
from utils.auth import require_role, get_current_active_user
from utils.unified_auth import require_role_unified, get_current_user_or_superadmin
from utils.database import get_db
from utils.helpers import serialize_doc

class LocationController:
    @staticmethod
    async def create_location(
        location_data: LocationCreate,
        current_user: dict = None
    ):
        """Create new location (Super Admin only)"""
        if not current_user:
            raise HTTPException(status_code=401, detail="Authentication required")
        
        db = get_db()
        
        # Check if location code already exists
        existing_location = await db.locations.find_one({"code": location_data.code})
        if existing_location:
            raise HTTPException(status_code=400, detail="Location code already exists")
        
        location = Location(**location_data.dict())
        location_dict = location.dict()
        
        await db.locations.insert_one(location_dict)
        return {"message": "Location created successfully", "location_id": location.id}

    @staticmethod
    async def get_locations(
        active_only: bool = True,
        skip: int = 0,
        limit: int = 50,
        current_user: dict = None
    ):
        """Get locations with optional filtering"""
        db = get_db()
        
        # Build query
        query = {}
        if active_only:
            query["is_active"] = True
        
        # Get locations with sorting
        locations_cursor = db.locations.find(query).sort("display_order", 1).skip(skip).limit(limit)
        locations = await locations_cursor.to_list(limit)
        
        # Get total count
        total = await db.locations.count_documents(query)
        
        # Enrich locations with branch count
        enriched_locations = []
        for location in locations:
            # Count branches in this location
            branch_count = await db.branches.count_documents({
                "branch.address.city": {"$regex": location["name"], "$options": "i"}
            })
            
            location_response = {
                "id": location["id"],
                "name": location["name"],
                "code": location["code"],
                "state": location["state"],
                "country": location["country"],
                "timezone": location["timezone"],
                "is_active": location["is_active"],
                "display_order": location["display_order"],
                "description": location.get("description"),
                "branch_count": branch_count,
                "created_at": location["created_at"],
                "updated_at": location["updated_at"]
            }
            
            enriched_locations.append(location_response)
        
        return {
            "message": f"Retrieved {len(enriched_locations)} locations successfully",
            "locations": enriched_locations,
            "total": total,
            "skip": skip,
            "limit": limit
        }

    @staticmethod
    async def get_states(
        active_only: bool = True
    ):
        """Get unique states from locations - Public endpoint (no authentication required)"""
        db = get_db()

        # Build query
        query = {}
        if active_only:
            query["is_active"] = True

        # Get unique states using aggregation
        pipeline = [
            {"$match": query},
            {"$group": {"_id": "$state", "count": {"$sum": 1}}},
            {"$sort": {"_id": 1}}
        ]

        states_cursor = db.locations.aggregate(pipeline)
        states_data = await states_cursor.to_list(100)

        # Format states for frontend consumption
        states = [{"state": state_doc["_id"], "location_count": state_doc["count"]} for state_doc in states_data]

        return {
            "message": f"Retrieved {len(states)} states successfully",
            "states": states,
            "total": len(states)
        }

    @staticmethod
    async def get_locations_with_branches(
        active_only: bool = True,
        skip: int = 0,
        limit: int = 100
    ):
        """Get locations with their associated branches - Public endpoint (no authentication required)"""
        db = get_db()
        
        # Build query for locations
        location_query = {}
        if active_only:
            location_query["is_active"] = True
        
        # Apply pagination
        if limit > 100:
            limit = 100  # Cap at 100 for public endpoint
        
        # Get locations with sorting
        locations_cursor = db.locations.find(location_query).sort("display_order", 1).skip(skip).limit(limit)
        locations = await locations_cursor.to_list(limit)
        
        # Get total count
        total = await db.locations.count_documents(location_query)
        
        # Get branches for each location
        locations_with_branches = []
        for location in locations:
            # Find branches in this location (matching by city name)
            branch_query = {
                "branch.address.city": {"$regex": location["name"], "$options": "i"}
            }
            if active_only:
                branch_query["is_active"] = True
            
            branches = await db.branches.find(branch_query).to_list(100)
            
            # Format branches for public consumption
            formatted_branches = []
            for branch in branches:
                formatted_branch = {
                    "id": branch["id"],
                    "name": branch["branch"]["name"],
                    "code": branch["branch"]["code"],
                    "email": branch["branch"]["email"],
                    "phone": branch["branch"]["phone"],
                    "address": {
                        "line1": branch["branch"]["address"]["line1"],
                        "area": branch["branch"]["address"]["area"],
                        "city": branch["branch"]["address"]["city"],
                        "state": branch["branch"]["address"]["state"],
                        "pincode": branch["branch"]["address"]["pincode"],
                        "country": branch["branch"]["address"]["country"]
                    },
                    "courses_offered": branch["operational_details"]["courses_offered"],
                    "timings": branch["operational_details"]["timings"]
                }
                formatted_branches.append(formatted_branch)
            
            location_with_branches = {
                "id": location["id"],
                "name": location["name"],
                "code": location["code"],
                "state": location["state"],
                "country": location["country"],
                "timezone": location["timezone"],
                "is_active": location["is_active"],
                "display_order": location["display_order"],
                "description": location.get("description"),
                "branch_count": len(formatted_branches),
                "branches": formatted_branches,
                "created_at": location["created_at"],
                "updated_at": location["updated_at"]
            }
            
            locations_with_branches.append(location_with_branches)
        
        return {
            "message": f"Retrieved {len(locations_with_branches)} locations with branches successfully",
            "locations": locations_with_branches,
            "total": total,
            "skip": skip,
            "limit": limit
        }

    @staticmethod
    async def get_location(
        location_id: str,
        current_user: dict = None
    ):
        """Get single location by ID"""
        db = get_db()
        
        location = await db.locations.find_one({"id": location_id})
        if not location:
            raise HTTPException(status_code=404, detail="Location not found")
        
        # Count branches in this location
        branch_count = await db.branches.count_documents({
            "branch.address.city": {"$regex": location["name"], "$options": "i"}
        })
        
        location_response = {
            "id": location["id"],
            "name": location["name"],
            "code": location["code"],
            "state": location["state"],
            "country": location["country"],
            "timezone": location["timezone"],
            "is_active": location["is_active"],
            "display_order": location["display_order"],
            "description": location.get("description"),
            "branch_count": branch_count,
            "created_at": location["created_at"],
            "updated_at": location["updated_at"]
        }
        
        return location_response

    @staticmethod
    async def update_location(
        location_id: str,
        location_update: LocationUpdate,
        current_user: dict = None
    ):
        """Update location (Super Admin only)"""
        if not current_user:
            raise HTTPException(status_code=401, detail="Authentication required")
        
        db = get_db()
        
        # Check if location exists
        existing_location = await db.locations.find_one({"id": location_id})
        if not existing_location:
            raise HTTPException(status_code=404, detail="Location not found")
        
        # Check if new code conflicts with existing locations
        if location_update.code and location_update.code != existing_location["code"]:
            code_conflict = await db.locations.find_one({
                "code": location_update.code,
                "id": {"$ne": location_id}
            })
            if code_conflict:
                raise HTTPException(status_code=400, detail="Location code already exists")
        
        # Prepare update data
        update_data = {k: v for k, v in location_update.dict().items() if v is not None}
        update_data["updated_at"] = datetime.utcnow()
        
        # Update location
        result = await db.locations.update_one(
            {"id": location_id},
            {"$set": update_data}
        )
        
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Location not found")
        
        return {"message": "Location updated successfully"}

    @staticmethod
    async def delete_location(
        location_id: str,
        current_user: dict = None
    ):
        """Delete location (Super Admin only)"""
        if not current_user:
            raise HTTPException(status_code=401, detail="Authentication required")
        
        db = get_db()
        
        # Check if location exists
        location = await db.locations.find_one({"id": location_id})
        if not location:
            raise HTTPException(status_code=404, detail="Location not found")
        
        # Check if location has branches
        branch_count = await db.branches.count_documents({
            "branch.address.city": {"$regex": location["name"], "$options": "i"}
        })
        if branch_count > 0:
            raise HTTPException(
                status_code=400, 
                detail=f"Cannot delete location. It has {branch_count} associated branches."
            )
        
        # Delete location
        result = await db.locations.delete_one({"id": location_id})
        
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Location not found")
        
        return {"message": "Location deleted successfully"}

    @staticmethod
    async def get_locations_with_details(
        location_id: Optional[str] = None,
        include_branches: bool = True,
        include_courses: bool = False,
        active_only: bool = True,
        skip: int = 0,
        limit: int = 50
    ):
        """Get location details with associated branches - Public endpoint"""
        db = get_db()

        # Build query
        query = {}
        if location_id:
            query["id"] = location_id
        if active_only:
            query["is_active"] = True

        # Apply pagination
        if limit > 100:
            limit = 100

        # Get locations
        locations_cursor = db.locations.find(query).sort("display_order", 1).skip(skip).limit(limit)
        locations = await locations_cursor.to_list(limit)

        # Get total count
        total = await db.locations.count_documents(query)

        # Enrich locations with branch and course data
        enriched_locations = []
        for location in locations:
            # Get branches in this location using location_id
            branch_query = {
                "location_id": location["id"]
            }
            if active_only:
                branch_query["is_active"] = True

            branches = await db.branches.find(branch_query).to_list(100)

            # Format branches
            formatted_branches = []
            all_course_ids = set()

            for branch in branches:
                branch_courses = branch.get("assignments", {}).get("courses", [])
                all_course_ids.update(branch_courses)

                branch_data = {
                    "id": branch["id"],
                    "name": branch["branch"]["name"],
                    "code": branch["branch"]["code"],
                    "email": branch["branch"]["email"],
                    "phone": branch["branch"]["phone"],
                    "address": {
                        "line1": branch["branch"]["address"]["line1"],
                        "area": branch["branch"]["address"]["area"],
                        "city": branch["branch"]["address"]["city"],
                        "state": branch["branch"]["address"]["state"],
                        "pincode": branch["branch"]["address"]["pincode"],
                        "country": branch["branch"]["address"]["country"]
                    },
                    "courses_offered": branch["operational_details"]["courses_offered"],
                    "course_count": len(branch_courses),
                    "timings": branch["operational_details"]["timings"]
                }

                if include_branches:
                    formatted_branches.append(branch_data)

            # Get total courses available at this location
            total_courses_available = len(all_course_ids)

            location_data = {
                "id": location["id"],
                "name": location["name"],
                "code": location["code"],
                "state": location["state"],
                "country": location["country"],
                "timezone": location["timezone"],
                "branch_count": len(branches),
                "branches": formatted_branches,
                "total_courses_available": total_courses_available
            }

            enriched_locations.append(location_data)

        return {
            "message": f"Retrieved {len(enriched_locations)} locations with details successfully",
            "locations": enriched_locations,
            "total": total
        }

    @staticmethod
    async def get_branches_by_location(
        location_id: str,
        include_courses: bool = True,
        include_timings: bool = True,
        active_only: bool = True,
        skip: int = 0,
        limit: int = 50
    ):
        """Get branches filtered by location - Public endpoint"""
        db = get_db()

        # Verify location exists
        location = await db.locations.find_one({"id": location_id})
        if not location:
            raise HTTPException(status_code=404, detail="Location not found")

        # Find branches in this location using location_id
        branch_query = {
            "location_id": location_id
        }
        if active_only:
            branch_query["is_active"] = True

        # Apply pagination
        if limit > 100:
            limit = 100

        # Get branches
        branches_cursor = db.branches.find(branch_query).skip(skip).limit(limit)
        branches = await branches_cursor.to_list(limit)

        # Get total count
        total = await db.branches.count_documents(branch_query)

        # Enrich branches with course data
        enriched_branches = []
        for branch in branches:
            # Get available courses if requested
            available_courses = []
            if include_courses:
                course_ids = branch.get("assignments", {}).get("courses", [])
                if course_ids:
                    courses = await db.courses.find({
                        "id": {"$in": course_ids},
                        "settings.active": True
                    }).to_list(100)

                    for course in courses:
                        # Get category info
                        category = await db.categories.find_one({"id": course["category_id"]})

                        course_data = {
                            "id": course["id"],
                            "title": course["title"],
                            "code": course["code"],
                            "category": category["name"] if category else "Unknown",
                            "difficulty_level": course["difficulty_level"],
                            "pricing": {
                                "currency": course.get("pricing", {}).get("currency", "INR"),
                                "amount": course.get("pricing", {}).get("amount", 0)
                            }
                        }
                        available_courses.append(course_data)

            # Get timings if requested
            timings = []
            if include_timings:
                timings = branch["operational_details"]["timings"]

            branch_data = {
                "id": branch["id"],
                "name": branch["branch"]["name"],
                "code": branch["branch"]["code"],
                "email": branch["branch"]["email"],
                "phone": branch["branch"]["phone"],
                "address": {
                    "line1": branch["branch"]["address"]["line1"],
                    "area": branch["branch"]["address"]["area"],
                    "city": branch["branch"]["address"]["city"],
                    "state": branch["branch"]["address"]["state"],
                    "pincode": branch["branch"]["address"]["pincode"],
                    "country": branch["branch"]["address"]["country"]
                },
                "available_courses": available_courses,
                "timings": timings,
                "course_count": len(available_courses)
            }

            enriched_branches.append(branch_data)

        return {
            "message": f"Retrieved {len(enriched_branches)} branches for location successfully",
            "location": {
                "id": location["id"],
                "name": location["name"],
                "code": location["code"],
                "state": location["state"]
            },
            "branches": enriched_branches,
            "total": total
        }
