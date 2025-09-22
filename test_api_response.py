#!/usr/bin/env python3
"""
Test script to check the exact API response format
"""
import asyncio
import sys
import os
import json
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.database import get_db, init_db
from controllers.dashboard_controller import DashboardController
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

async def test_api_response():
    """Test the exact API response format"""
    
    # Load environment variables
    load_dotenv()
    
    # Connect to database
    mongo_url = os.getenv("MONGO_URL", "mongodb://localhost:27017")
    client = AsyncIOMotorClient(mongo_url)
    db_name = os.getenv("DB_NAME", "student_management_db")
    database = client.get_database(db_name)
    
    # Initialize database connection
    init_db(database)
    
    print("🔍 Testing API Response Format")
    print("=" * 50)
    
    # Find a branch manager in the database
    db = get_db()
    branch_manager = await db.branch_managers.find_one({"is_active": True})
    
    # Create mock current_user object
    current_user = {
        "id": branch_manager["id"],
        "email": branch_manager["email"],
        "role": "branch_manager"
    }
    
    print(f"🔍 Testing with branch manager: {branch_manager.get('full_name', 'Unknown')}")
    
    try:
        result = await DashboardController.get_dashboard_stats(current_user)
        
        print("\n📊 Raw API Response:")
        print(json.dumps(result, indent=2, default=str))
        
        print("\n🔍 Response Structure Analysis:")
        print(f"Type: {type(result)}")
        print(f"Keys: {list(result.keys()) if isinstance(result, dict) else 'Not a dict'}")
        
        if 'dashboard_stats' in result:
            stats = result['dashboard_stats']
            print(f"\nDashboard Stats Type: {type(stats)}")
            print(f"Dashboard Stats Keys: {list(stats.keys()) if isinstance(stats, dict) else 'Not a dict'}")
            
            print("\n📈 Individual Values:")
            for key, value in stats.items():
                print(f"  {key}: {value} (type: {type(value)})")
        
    except Exception as e:
        print(f"❌ API call failed: {str(e)}")
        import traceback
        traceback.print_exc()
    
    # Close database connection
    client.close()

if __name__ == "__main__":
    asyncio.run(test_api_response())
