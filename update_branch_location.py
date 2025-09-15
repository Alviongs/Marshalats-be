#!/usr/bin/env python3

import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv

load_dotenv()

async def update_branch_with_location():
    """Update the existing branch to have a proper location_id"""
    
    try:
        client = AsyncIOMotorClient(os.getenv('MONGODB_URL'))
        db = client[os.getenv('DATABASE_NAME')]
        
        print("🔧 Updating existing branch with location association...")
        
        # Get existing locations
        locations = await db.locations.find().to_list(10)
        if not locations:
            print("❌ No locations found. Please create locations first.")
            return
        
        print(f"📍 Found {len(locations)} locations:")
        for loc in locations:
            print(f"  - {loc.get('name')} (ID: {loc.get('id')}) in {loc.get('state')}")
        
        # Get existing branches without location_id
        branches_without_location = await db.branches.find({
            "$or": [
                {"location_id": {"$exists": False}},
                {"location_id": None}
            ]
        }).to_list(10)
        
        if not branches_without_location:
            print("✅ All branches already have location associations.")
            return
        
        print(f"🏢 Found {len(branches_without_location)} branches without location:")
        for branch in branches_without_location:
            print(f"  - {branch.get('branch', {}).get('name', branch.get('name', 'N/A'))} (ID: {branch.get('id')})")
        
        # Update the first branch to be associated with the first location (Hyderabad)
        if branches_without_location and locations:
            branch_to_update = branches_without_location[0]
            location_to_assign = locations[0]  # Hyderabad
            
            branch_id = branch_to_update['id']
            location_id = location_to_assign['id']
            location_name = location_to_assign['name']
            
            # Update the branch
            result = await db.branches.update_one(
                {"id": branch_id},
                {"$set": {"location_id": location_id}}
            )
            
            if result.modified_count > 0:
                print(f"✅ Successfully updated branch '{branch_to_update.get('branch', {}).get('name', branch_to_update.get('name', 'N/A'))}' to be associated with location '{location_name}'")
            else:
                print(f"❌ Failed to update branch")
        
        # Verify the update
        print("\n🧪 Verifying the update...")
        updated_branch = await db.branches.find_one({"id": branch_id})
        if updated_branch and updated_branch.get('location_id'):
            print(f"✅ Branch now has location_id: {updated_branch['location_id']}")
            
            # Test the filtering
            branches_for_location = await db.branches.find({
                "location_id": location_id,
                "is_active": True
            }).to_list(10)
            
            print(f"📊 Found {len(branches_for_location)} branches for location '{location_name}'")
        
        client.close()
        print("\n🎉 Branch location update completed successfully!")
        
    except Exception as e:
        print(f"❌ Error updating branch location: {e}")

if __name__ == '__main__':
    asyncio.run(update_branch_with_location())
