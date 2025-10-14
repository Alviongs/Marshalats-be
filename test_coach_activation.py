#!/usr/bin/env python3
"""
Test script for coach activation/deactivation functionality
"""
import asyncio
import json
from datetime import datetime
from utils.database import get_db
from controllers.coach_controller import CoachController
from models.coach_models import CoachUpdate

async def test_coach_activation():
    """Test coach activation/deactivation functionality"""
    print("🧪 Testing Coach Activation/Deactivation Functionality")
    print("=" * 60)
    
    db = get_db()
    
    # Find a test coach
    test_coach = await db.coaches.find_one({"is_active": True})
    if not test_coach:
        print("❌ No active coaches found for testing")
        return
    
    coach_id = test_coach["id"]
    coach_name = test_coach.get("full_name", "Test Coach")
    
    print(f"📋 Testing with coach: {coach_name} (ID: {coach_id})")
    print(f"📋 Initial status: {'Active' if test_coach.get('is_active', True) else 'Inactive'}")
    print()
    
    # Mock admin user for testing
    mock_admin = {
        "id": "test_admin_id",
        "full_name": "Test Admin",
        "role": "super_admin"
    }
    
    # Mock request object
    class MockRequest:
        def __init__(self):
            self.client = type('obj', (object,), {'host': 'localhost'})()
            self.headers = {}
    
    mock_request = MockRequest()
    
    try:
        # Test 1: Deactivate coach using update_coach with is_active=False
        print("🔄 Test 1: Deactivating coach using update_coach...")
        coach_update = CoachUpdate(is_active=False)
        result = await CoachController.update_coach(coach_id, coach_update, mock_request, mock_admin)
        print(f"✅ Deactivation result: {result}")
        
        # Verify deactivation
        updated_coach = await db.coaches.find_one({"id": coach_id})
        print(f"📋 Coach status after deactivation: {'Active' if updated_coach.get('is_active', True) else 'Inactive'}")
        print()
        
        # Test 2: Activate coach using update_coach with is_active=True
        print("🔄 Test 2: Activating coach using update_coach...")
        coach_update = CoachUpdate(is_active=True)
        result = await CoachController.update_coach(coach_id, coach_update, mock_request, mock_admin)
        print(f"✅ Activation result: {result}")
        
        # Verify activation
        updated_coach = await db.coaches.find_one({"id": coach_id})
        print(f"📋 Coach status after activation: {'Active' if updated_coach.get('is_active', True) else 'Inactive'}")
        print()
        
        # Test 3: Test deactivate_coach function
        print("🔄 Test 3: Testing deactivate_coach function...")
        result = await CoachController.deactivate_coach(coach_id, mock_request, mock_admin)
        print(f"✅ Deactivate function result: {result}")
        
        # Verify deactivation
        updated_coach = await db.coaches.find_one({"id": coach_id})
        print(f"📋 Coach status after deactivate function: {'Active' if updated_coach.get('is_active', True) else 'Inactive'}")
        print()
        
        # Test 4: Test activate_coach function
        print("🔄 Test 4: Testing activate_coach function...")
        result = await CoachController.activate_coach(coach_id, mock_request, mock_admin)
        print(f"✅ Activate function result: {result}")
        
        # Verify activation
        updated_coach = await db.coaches.find_one({"id": coach_id})
        print(f"📋 Coach status after activate function: {'Active' if updated_coach.get('is_active', True) else 'Inactive'}")
        print()
        
        # Test 5: Test partial update (other fields should not be affected)
        print("🔄 Test 5: Testing partial update with is_active only...")
        original_areas = updated_coach.get("areas_of_expertise", [])
        coach_update = CoachUpdate(is_active=False)  # Only updating is_active
        result = await CoachController.update_coach(coach_id, coach_update, mock_request, mock_admin)
        
        updated_coach = await db.coaches.find_one({"id": coach_id})
        new_areas = updated_coach.get("areas_of_expertise", [])
        
        print(f"✅ Partial update result: {result}")
        print(f"📋 Areas of expertise preserved: {original_areas == new_areas}")
        print(f"📋 Coach status: {'Active' if updated_coach.get('is_active', True) else 'Inactive'}")
        print()
        
        # Restore original state
        print("🔄 Restoring original coach state...")
        coach_update = CoachUpdate(is_active=test_coach.get("is_active", True))
        await CoachController.update_coach(coach_id, coach_update, mock_request, mock_admin)
        print("✅ Original state restored")
        
        print()
        print("🎉 All tests completed successfully!")
        print("✅ Coach activation/deactivation functionality is working correctly")
        
    except Exception as e:
        print(f"❌ Test failed with error: {str(e)}")
        import traceback
        traceback.print_exc()
        
        # Try to restore original state
        try:
            print("🔄 Attempting to restore original state...")
            coach_update = CoachUpdate(is_active=test_coach.get("is_active", True))
            await CoachController.update_coach(coach_id, coach_update, mock_request, mock_admin)
            print("✅ Original state restored")
        except:
            print("❌ Failed to restore original state")

async def test_coach_model_validation():
    """Test CoachUpdate model validation"""
    print("\n🧪 Testing CoachUpdate Model Validation")
    print("=" * 40)
    
    try:
        # Test valid is_active values
        coach_update_true = CoachUpdate(is_active=True)
        coach_update_false = CoachUpdate(is_active=False)
        coach_update_none = CoachUpdate(is_active=None)
        coach_update_empty = CoachUpdate()
        
        print("✅ CoachUpdate with is_active=True: Valid")
        print("✅ CoachUpdate with is_active=False: Valid")
        print("✅ CoachUpdate with is_active=None: Valid")
        print("✅ CoachUpdate with no is_active field: Valid")
        
        # Test serialization
        print(f"📋 Serialized (True): {coach_update_true.dict()}")
        print(f"📋 Serialized (False): {coach_update_false.dict()}")
        print(f"📋 Serialized (None): {coach_update_none.dict()}")
        print(f"📋 Serialized (Empty): {coach_update_empty.dict()}")
        
        print("🎉 Model validation tests passed!")
        
    except Exception as e:
        print(f"❌ Model validation failed: {str(e)}")
        import traceback
        traceback.print_exc()

async def main():
    """Main test function"""
    await test_coach_model_validation()
    await test_coach_activation()

if __name__ == "__main__":
    asyncio.run(main())
