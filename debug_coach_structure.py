#!/usr/bin/env python3
"""
Debug script to check coach document structure in database
"""

import asyncio
from utils.database import get_db

async def check_coach_structure():
    """Check the structure of coach documents in the database"""
    
    print("🔍 Checking coach document structure...")
    
    try:
        db = get_db()
        
        # Find a coach document to see its structure
        coach = await db.coaches.find_one({"contact_info.email": "testlogincoach@example.com"})
        
        if coach:
            print("✅ Found test coach document")
            print("\nDocument structure:")
            for key, value in coach.items():
                if key == "password_hash":
                    print(f"  {key}: [HASHED PASSWORD]")
                elif key == "hashed_password":
                    print(f"  {key}: [HASHED PASSWORD]")
                elif isinstance(value, dict):
                    print(f"  {key}: {{nested object}}")
                elif isinstance(value, list):
                    print(f"  {key}: [list with {len(value)} items]")
                else:
                    print(f"  {key}: {type(value).__name__}")
            
            # Check specifically for password fields
            password_fields = []
            if "password_hash" in coach:
                password_fields.append("password_hash")
            if "hashed_password" in coach:
                password_fields.append("hashed_password")
            if "password" in coach:
                password_fields.append("password")
                
            print(f"\nPassword fields found: {password_fields}")
            
        else:
            print("❌ No test coach found")
            
            # List all coaches to see what's available
            all_coaches = await db.coaches.find({}).to_list(length=5)
            print(f"Found {len(all_coaches)} coaches in database")
            
            if all_coaches:
                sample_coach = all_coaches[0]
                print(f"\nSample coach structure:")
                for key in sample_coach.keys():
                    print(f"  {key}: {type(sample_coach[key]).__name__}")
                
                # Check for password fields in any coach
                password_fields = []
                for coach in all_coaches:
                    for key in coach.keys():
                        if "password" in key.lower():
                            if key not in password_fields:
                                password_fields.append(key)
                                
                print(f"\nPassword fields across all coaches: {password_fields}")
                
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(check_coach_structure())
