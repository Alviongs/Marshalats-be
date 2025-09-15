#!/usr/bin/env python3

import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv
import uuid
from datetime import datetime

load_dotenv()

async def create_test_branches():
    """Create test branches with proper location_id associations"""
    
    try:
        client = AsyncIOMotorClient(os.getenv('MONGODB_URL'))
        db = client[os.getenv('DATABASE_NAME')]
        
        print("🏗️  Creating test branches with location associations...")
        
        # First, get existing locations
        locations = await db.locations.find().to_list(10)
        if not locations:
            print("❌ No locations found. Please create locations first.")
            return
        
        print(f"📍 Found {len(locations)} locations:")
        for loc in locations:
            print(f"  - {loc.get('name')} (ID: {loc.get('id')}) in {loc.get('state')}")
        
        # Create test branches for each location
        test_branches = []
        
        for i, location in enumerate(locations):
            location_id = location.get('id')
            location_name = location.get('name')
            state = location.get('state')
            
            # Create 2 branches per location
            for j in range(1, 3):
                branch_id = str(uuid.uuid4())
                branch = {
                    "id": branch_id,
                    "location_id": location_id,  # Proper location association
                    "branch": {
                        "name": f"{location_name} Martial Arts Center {j}",
                        "code": f"{location_name[:3].upper()}{j:02d}",
                        "email": f"{location_name.lower().replace(' ', '')}{j}@martialarts.com",
                        "phone": f"+91-{9000000000 + i*100 + j}",
                        "address": {
                            "line1": f"{j*100} Main Street",
                            "area": f"Sector {j}",
                            "city": location_name,
                            "state": state,
                            "pincode": f"{500000 + i*10 + j}",
                            "country": "India"
                        }
                    },
                    "manager_id": f"manager-{branch_id}",
                    "operational_details": {
                        "courses_offered": ["Karate", "Taekwondo", "Kung Fu"],
                        "timings": [
                            {"day": "Monday", "open": "06:00", "close": "22:00"},
                            {"day": "Tuesday", "open": "06:00", "close": "22:00"},
                            {"day": "Wednesday", "open": "06:00", "close": "22:00"},
                            {"day": "Thursday", "open": "06:00", "close": "22:00"},
                            {"day": "Friday", "open": "06:00", "close": "22:00"},
                            {"day": "Saturday", "open": "08:00", "close": "20:00"},
                            {"day": "Sunday", "open": "08:00", "close": "18:00"}
                        ],
                        "holidays": ["2025-01-01", "2025-08-15", "2025-10-02", "2025-12-25"]
                    },
                    "assignments": {
                        "accessories_available": True,
                        "courses": [],  # Will be populated with actual course IDs
                        "branch_admins": []  # Will be populated with actual admin IDs
                    },
                    "bank_details": {
                        "bank_name": f"State Bank of {state}",
                        "account_number": f"1234567890{i}{j}",
                        "upi_id": f"{location_name.lower().replace(' ', '')}{j}@sbi"
                    },
                    "is_active": True,
                    "created_at": datetime.utcnow(),
                    "updated_at": datetime.utcnow()
                }
                test_branches.append(branch)
        
        # Insert test branches
        if test_branches:
            await db.branches.insert_many(test_branches)
            print(f"✅ Created {len(test_branches)} test branches")
            
            # Verify the creation
            for branch in test_branches:
                location_name = next(loc['name'] for loc in locations if loc['id'] == branch['location_id'])
                print(f"  - {branch['branch']['name']} (Location: {location_name})")
        
        print("\n🧪 Testing the location-based branch filtering...")
        
        # Test the filtering for each location
        for location in locations:
            location_id = location['id']
            location_name = location['name']
            
            # Count branches for this location
            branch_count = await db.branches.count_documents({
                "location_id": location_id,
                "is_active": True
            })
            
            print(f"📊 {location_name}: {branch_count} branches")
        
        client.close()
        print("\n🎉 Test data creation completed successfully!")
        
    except Exception as e:
        print(f"❌ Error creating test branches: {e}")

if __name__ == '__main__':
    asyncio.run(create_test_branches())
