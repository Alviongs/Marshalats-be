#!/usr/bin/env python3
"""
Test script to verify MongoDB connection
"""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv

async def test_mongodb_connection():
    """Test MongoDB connection"""
    # Load environment variables
    load_dotenv()
    
    mongo_url = os.getenv("MONGO_URL", "mongodb://localhost:27017")
    db_name = os.getenv("DB_NAME", "student_management_db")
    
    print(f"Testing connection to: {mongo_url}")
    print(f"Database name: {db_name}")
    
    try:
        # Create MongoDB client
        client = AsyncIOMotorClient(mongo_url)
        
        # Test connection by accessing admin database
        db = client.get_database(db_name)
        
        # Try to perform a simple operation
        result = await db.list_collection_names()
        print(f"✅ Successfully connected to MongoDB!")
        print(f"Collections in database: {result}")
        
        # Test a simple insert and delete
        test_collection = db.test_connection
        test_doc = {"test": "connection", "timestamp": "2025-01-01"}
        
        insert_result = await test_collection.insert_one(test_doc)
        print(f"✅ Test document inserted with ID: {insert_result.inserted_id}")
        
        # Clean up test document
        await test_collection.delete_one({"_id": insert_result.inserted_id})
        print("✅ Test document cleaned up")
        
        # Close connection
        client.close()
        
        print("\n🎉 MongoDB is properly configured and working!")
        return True
        
    except Exception as e:
        print(f"❌ Error connecting to MongoDB: {e}")
        print("\n📋 To fix this issue:")
        print("1. Install MongoDB Community Server from: https://www.mongodb.com/try/download/community")
        print("2. Start MongoDB service")
        print("3. Or use MongoDB Atlas (cloud): https://www.mongodb.com/atlas")
        print("4. Update MONGO_URL in .env file if using different connection string")
        return False

if __name__ == "__main__":
    asyncio.run(test_mongodb_connection())
