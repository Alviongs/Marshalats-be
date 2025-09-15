#!/usr/bin/env python3

import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv

async def fix_existing_branch():
    """Fix the existing branch by adding proper location_id"""
    
    print('🔧 FIXING EXISTING BRANCH WITH LOCATION_ID')
    print('=' * 50)
    
    load_dotenv()
    
    mongo_url = os.getenv('MONGO_URL', 'mongodb://localhost:27017')
    db_name = os.getenv('DB_NAME', 'student_management_db')
    
    client = AsyncIOMotorClient(mongo_url)
    db = client[db_name]
    
    try:
        # Get locations
        locations_collection = db.locations
        locations = await locations_collection.find().to_list(None)
        
        print(f'Found {len(locations)} locations:')
        for loc in locations:
            name = loc.get('name', 'N/A')
            loc_id = loc.get('id', 'N/A')
            state = loc.get('state', 'N/A')
            print(f'  - {name} (ID: {loc_id}) in {state}')
        
        if not locations:
            print('❌ No locations found. Cannot fix branch.')
            return
        
        # Get the existing branch
        branches_collection = db.branches
        branch = await branches_collection.find_one()
        
        if not branch:
            print('❌ No branch found to fix.')
            return
        
        branch_name = branch.get('branch', {}).get('name', 'N/A')
        branch_id = branch.get('id', 'N/A')
        current_location_id = branch.get('location_id', 'MISSING')
        
        print(f'\\nFound branch: {branch_name} (ID: {branch_id})')
        print(f'Current location_id: {current_location_id}')
        
        # Choose a location to associate with (let's use the first one - Hyderabad)
        target_location = locations[0]
        target_location_id = target_location.get('id')
        target_location_name = target_location.get('name')
        
        print(f'\\nAssociating branch with location: {target_location_name} (ID: {target_location_id})')
        
        # Update the branch document
        update_result = await branches_collection.update_one(
            {'id': branch_id},
            {'$set': {'location_id': target_location_id}}
        )
        
        if update_result.modified_count > 0:
            print('✅ Branch updated successfully!')
            
            # Verify the update
            updated_branch = await branches_collection.find_one({'id': branch_id})
            if updated_branch:
                new_location_id = updated_branch.get('location_id', 'STILL MISSING')
                print(f'Verified: Branch now has location_id = {new_location_id}')
            
        else:
            print('❌ Failed to update branch.')
            
    except Exception as e:
        print(f'❌ Error: {e}')
    finally:
        client.close()

async def test_filtering_after_fix():
    """Test the filtering after fixing the branch"""
    
    print('\\n🧪 TESTING FILTERING AFTER FIX')
    print('=' * 50)
    
    import requests
    
    # Test the API endpoints
    try:
        # Test all branches
        response = requests.get('http://localhost:8003/api/branches/public/all?active_only=true')
        if response.status_code == 200:
            data = response.json()
            branches = data.get('branches', [])
            print(f'\\nAll branches: {len(branches)}')
            for branch in branches:
                name = branch.get('name', 'N/A')
                location_id = branch.get('location_id', 'MISSING')
                print(f'  - {name}: location_id = {location_id}')
        
        # Test filtering by location
        location_id = '07a19e09-0ef3-49ef-ba1d-4278af845685'  # Hyderabad
        response = requests.get(f'http://localhost:8003/api/branches/public/by-location/{location_id}?active_only=true')
        if response.status_code == 200:
            data = response.json()
            filtered_branches = data.get('branches', [])
            print(f'\\nBranches in Hyderabad: {len(filtered_branches)}')
            for branch in filtered_branches:
                name = branch.get('name', 'N/A')
                print(f'  - {name}')
                
            if len(filtered_branches) > 0:
                print('\\n🎉 SUCCESS! Location-based filtering is now working!')
            else:
                print('\\n❌ Still no branches found for location.')
        
    except Exception as e:
        print(f'❌ API test error: {e}')

async def main():
    await fix_existing_branch()
    await test_filtering_after_fix()

if __name__ == '__main__':
    asyncio.run(main())
