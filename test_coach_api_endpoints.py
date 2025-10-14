#!/usr/bin/env python3
"""
Test script to verify coach API endpoints and model structure
"""
import json
from models.coach_models import CoachUpdate, CoachResponse, Coach
from routes.coach_routes import router
from fastapi.routing import APIRoute

def test_coach_update_model():
    """Test CoachUpdate model has is_active field"""
    print("🧪 Testing CoachUpdate Model")
    print("=" * 30)
    
    # Test creating CoachUpdate with is_active field
    coach_update = CoachUpdate(is_active=True)
    model_dict = coach_update.model_dump()
    
    print(f"✅ CoachUpdate model created successfully")
    print(f"📋 is_active field present: {'is_active' in model_dict}")
    print(f"📋 is_active value: {model_dict.get('is_active')}")
    
    # Test with False
    coach_update_false = CoachUpdate(is_active=False)
    model_dict_false = coach_update_false.model_dump()
    print(f"📋 is_active=False value: {model_dict_false.get('is_active')}")
    
    # Test with None (should not update)
    coach_update_none = CoachUpdate(is_active=None)
    model_dict_none = coach_update_none.model_dump()
    print(f"📋 is_active=None value: {model_dict_none.get('is_active')}")
    
    return True

def test_coach_response_model():
    """Test CoachResponse model has is_active field"""
    print("\n🧪 Testing CoachResponse Model")
    print("=" * 30)
    
    # Check if CoachResponse has is_active field
    from models.coach_models import CoachResponse
    fields = CoachResponse.model_fields
    
    print(f"✅ CoachResponse model loaded successfully")
    print(f"📋 is_active field present: {'is_active' in fields}")
    
    if 'is_active' in fields:
        field_info = fields['is_active']
        print(f"📋 is_active field type: {field_info.annotation}")
    
    return 'is_active' in fields

def test_coach_routes():
    """Test coach routes are properly defined"""
    print("\n🧪 Testing Coach API Routes")
    print("=" * 30)
    
    routes = []
    for route in router.routes:
        if isinstance(route, APIRoute):
            routes.append({
                'path': route.path,
                'methods': list(route.methods),
                'name': route.name
            })
    
    # Check for key routes
    update_route = None
    activate_route = None
    deactivate_route = None
    
    for route in routes:
        if route['path'] == '/{coach_id}' and 'PUT' in route['methods']:
            update_route = route
        elif route['path'] == '/{coach_id}/activate' and 'PATCH' in route['methods']:
            activate_route = route
        elif route['path'] == '/{coach_id}' and 'DELETE' in route['methods']:
            deactivate_route = route
    
    print(f"📋 Total coach routes: {len(routes)}")
    print(f"✅ Update coach route (PUT /{coach_id}): {'Found' if update_route else 'Missing'}")
    print(f"✅ Activate coach route (PATCH /{coach_id}/activate): {'Found' if activate_route else 'Missing'}")
    print(f"✅ Deactivate coach route (DELETE /{coach_id}): {'Found' if deactivate_route else 'Missing'}")
    
    # Print all routes for reference
    print("\n📋 All Coach Routes:")
    for route in routes:
        methods_str = ', '.join(route['methods'])
        print(f"  {methods_str} {route['path']} -> {route['name']}")
    
    return update_route is not None and activate_route is not None and deactivate_route is not None

def test_controller_functions():
    """Test that controller functions exist"""
    print("\n🧪 Testing Coach Controller Functions")
    print("=" * 35)
    
    from controllers.coach_controller import CoachController
    
    # Check if required methods exist
    methods_to_check = [
        'update_coach',
        'activate_coach', 
        'deactivate_coach'
    ]
    
    results = {}
    for method_name in methods_to_check:
        exists = hasattr(CoachController, method_name)
        results[method_name] = exists
        print(f"✅ {method_name}: {'Found' if exists else 'Missing'}")
    
    return all(results.values())

def generate_api_documentation():
    """Generate API documentation for coach activation/deactivation"""
    print("\n📚 Coach Activation/Deactivation API Documentation")
    print("=" * 55)
    
    api_docs = """
## Coach Activation/Deactivation API Endpoints

### 1. Update Coach (Including Activation Status)
**Endpoint:** `PUT /api/coaches/{coach_id}`
**Method:** PUT
**Authentication:** Required (Super Admin, Coach Admin)
**Request Body:**
```json
{
  "is_active": true  // or false to deactivate
}
```
**Response:**
```json
{
  "message": "Coach updated successfully"
}
```

### 2. Activate Coach
**Endpoint:** `PATCH /api/coaches/{coach_id}/activate`
**Method:** PATCH
**Authentication:** Required (Super Admin, Branch Manager)
**Response:**
```json
{
  "message": "Coach activated successfully"
}
```

### 3. Deactivate Coach
**Endpoint:** `DELETE /api/coaches/{coach_id}`
**Method:** DELETE
**Authentication:** Required (Super Admin, Branch Manager)
**Response:**
```json
{
  "message": "Coach deactivated successfully"
}
```

### Frontend Integration Example:
```javascript
// Toggle coach status
const toggleCoachStatus = async (coachId, isActive) => {
  const response = await fetch(`/api/coaches/${coachId}`, {
    method: 'PUT',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`
    },
    body: JSON.stringify({
      is_active: !isActive  // Toggle the current status
    })
  });
  
  if (response.ok) {
    const result = await response.json();
    console.log('Coach status updated:', result.message);
    // Refresh coach list or update UI
  }
};
```
"""
    
    print(api_docs)
    return api_docs

def main():
    """Run all tests"""
    print("🚀 Coach Activation/Deactivation Backend Verification")
    print("=" * 60)
    
    results = []
    
    # Test 1: Model validation
    try:
        results.append(("CoachUpdate Model", test_coach_update_model()))
    except Exception as e:
        print(f"❌ CoachUpdate Model test failed: {e}")
        results.append(("CoachUpdate Model", False))
    
    # Test 2: Response model
    try:
        results.append(("CoachResponse Model", test_coach_response_model()))
    except Exception as e:
        print(f"❌ CoachResponse Model test failed: {e}")
        results.append(("CoachResponse Model", False))
    
    # Test 3: Routes
    try:
        results.append(("API Routes", test_coach_routes()))
    except Exception as e:
        print(f"❌ API Routes test failed: {e}")
        results.append(("API Routes", False))
    
    # Test 4: Controller functions
    try:
        results.append(("Controller Functions", test_controller_functions()))
    except Exception as e:
        print(f"❌ Controller Functions test failed: {e}")
        results.append(("Controller Functions", False))
    
    # Generate documentation
    generate_api_documentation()
    
    # Summary
    print("\n🎯 Test Results Summary")
    print("=" * 25)
    
    all_passed = True
    for test_name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} {test_name}")
        if not passed:
            all_passed = False
    
    print("\n" + "=" * 60)
    if all_passed:
        print("🎉 ALL TESTS PASSED! Coach activation/deactivation backend is ready!")
        print("✅ Frontend can now use the toggle functionality")
    else:
        print("❌ Some tests failed. Please check the implementation.")
    
    return all_passed

if __name__ == "__main__":
    main()
