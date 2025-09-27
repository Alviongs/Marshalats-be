#!/usr/bin/env python3
"""
Debug script to check coach access issue for branch managers
"""
import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

async def debug_coach_access():
    """Debug coach access for branch manager"""
    
    # Database connection
    MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
    DB_NAME = os.environ.get('DB_NAME', 'marshalats')
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]

    print(f"🔍 Debugging coach access issue")
    print(f"Connecting to: {MONGO_URL}")
    print(f"Database: {DB_NAME}")
    print("=" * 60)
    
    try:
        # 1. Find the branch manager
        print("1. Checking branch manager data...")
        manager = await db.branch_managers.find_one({"email": "pittisunilkumar3@gmail.com"})
        
        if not manager:
            print("❌ Branch manager not found!")
            return
            
        print(f"✅ Found branch manager: {manager.get('full_name', 'No name')}")
        print(f"   Manager ID: {manager.get('id')}")
        print(f"   Branch assignment: {manager.get('branch_assignment')}")
        
        # 2. Check what branches this manager manages
        manager_id = manager.get('id')
        managed_branches = await db.branches.find({"manager_id": manager_id, "is_active": True}).to_list(100)
        
        print(f"\n2. Checking managed branches...")
        print(f"   Branches where manager_id = {manager_id}:")
        managed_branch_ids = []
        for branch in managed_branches:
            branch_id = branch.get('id')
            managed_branch_ids.append(branch_id)
            print(f"   ✅ Branch: {branch.get('branch', {}).get('name', 'No name')} (ID: {branch_id})")
        
        # Also check branch_assignment approach
        branch_assignment = manager.get('branch_assignment', {})
        if branch_assignment and branch_assignment.get('branch_id'):
            assignment_branch_id = branch_assignment.get('branch_id')
            if assignment_branch_id not in managed_branch_ids:
                managed_branch_ids.append(assignment_branch_id)
            print(f"   ✅ Branch from assignment: {assignment_branch_id}")
        
        print(f"   Total managed branch IDs: {managed_branch_ids}")
        
        # 3. Check the specific coach
        coach_id = "b6c5cc5f-be8d-47b2-aa95-3c1cdcb72a0d"
        print(f"\n3. Checking coach {coach_id}...")
        coach = await db.coaches.find_one({"id": coach_id})
        
        if not coach:
            print("❌ Coach not found!")
            return
            
        print(f"✅ Found coach: {coach.get('full_name', 'No name')}")
        print(f"   Coach branch_id: {coach.get('branch_id')}")
        print(f"   Coach is_active: {coach.get('is_active')}")
        
        # 4. Check if coach's branch matches managed branches
        coach_branch_id = coach.get('branch_id')
        print(f"\n4. Access check...")
        print(f"   Coach branch ID: {coach_branch_id}")
        print(f"   Managed branch IDs: {managed_branch_ids}")
        
        if coach_branch_id in managed_branch_ids:
            print("✅ ACCESS SHOULD BE ALLOWED - Coach is in a managed branch")
        else:
            print("❌ ACCESS DENIED - Coach is not in any managed branch")
            
        # 5. Check all coaches in managed branches
        print(f"\n5. All coaches in managed branches...")
        if managed_branch_ids:
            coaches_in_managed_branches = await db.coaches.find({
                "branch_id": {"$in": managed_branch_ids},
                "is_active": True
            }).to_list(100)
            
            print(f"   Found {len(coaches_in_managed_branches)} coaches in managed branches:")
            for coach in coaches_in_managed_branches:
                print(f"   - {coach.get('full_name', 'No name')} (ID: {coach.get('id')}) in branch {coach.get('branch_id')}")
        else:
            print("   No managed branches found!")
            
        # 6. Check all coaches in database
        print(f"\n6. All coaches in database...")
        all_coaches = await db.coaches.find({"is_active": True}).to_list(100)
        print(f"   Total active coaches: {len(all_coaches)}")
        for coach in all_coaches:
            print(f"   - {coach.get('full_name', 'No name')} (ID: {coach.get('id')}) in branch {coach.get('branch_id')}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    asyncio.run(debug_coach_access())
