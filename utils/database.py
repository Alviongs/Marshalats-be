from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId
from fastapi import Request
from datetime import date, datetime

# Global database instance
db: AsyncIOMotorDatabase = None

def init_db(database: AsyncIOMotorDatabase):
    """Initialize the global database instance"""
    global db
    db = database

def get_db():
    """Get the database instance"""
    return db

def get_database_from_request(request: Request) -> AsyncIOMotorDatabase:
    """Get database instance from FastAPI request object"""
    return request.app.mongodb

def serialize_doc(doc):
    """Convert MongoDB document to JSON serializable format"""
    if doc is None:
        return None
    if isinstance(doc, list):
        return [serialize_doc(item) for item in doc]
    if isinstance(doc, dict):
        serialized = {}
        for key, value in doc.items():
            if key == "_id" and isinstance(value, ObjectId):
                serialized["id"] = str(value)
            elif isinstance(value, ObjectId):
                serialized[key] = str(value)
            elif isinstance(value, date) and not isinstance(value, datetime):
                # Convert date objects to ISO format string for BSON compatibility
                serialized[key] = value.isoformat()
            elif isinstance(value, datetime):
                # Keep datetime objects as-is (BSON can handle them)
                serialized[key] = value
            elif isinstance(value, dict):
                serialized[key] = serialize_doc(value)
            elif isinstance(value, list):
                serialized[key] = [serialize_doc(item) for item in value]
            else:
                serialized[key] = value
        return serialized
    elif isinstance(doc, date) and not isinstance(doc, datetime):
        # Convert standalone date objects to ISO format string
        return doc.isoformat()
    elif isinstance(doc, datetime):
        # Keep datetime objects as-is
        return doc
    return doc
