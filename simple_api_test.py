import requests
import json

# Test configuration
BASE_URL = 'http://localhost:8003'
token = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1MGY3YzdhYy0yNTkyLTQ0N2YtYmQzNy0zYzBkYWQ1ZDMzMGMiLCJlbWFpbCI6ImFkbWluQHRlc3QuY29tIiwicm9sZSI6InN1cGVyYWRtaW4iLCJleHAiOjE3NTczMTQ5NDh9.ZnhHstNDQVNNqYqHZtKw1sVSZ9PIHSuXZFK3aDZ3hn8'
headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}

# Test data IDs
category_ids = ['7b656efc-65bf-463d-8aad-0e1cf28117e4', '5de1c515-dc37-4b08-bb8b-1d4412539f76']
location_ids = ['a60c5165-60f4-4f65-b66c-433ebdcd9f73', 'e5bacaa2-54b5-4730-9451-1881048730cb']

def test_endpoint(name, url, expected_status=200):
    print(f"\n{'='*50}")
    print(f"Testing: {name}")
    print(f"URL: {url}")
    
    try:
        response = requests.get(url)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == expected_status:
            print("✅ SUCCESS")
            try:
                data = response.json()
                print(f"Response keys: {list(data.keys())}")
                if 'message' in data:
                    print(f"Message: {data['message']}")
                if 'total' in data:
                    print(f"Total items: {data['total']}")
                return True
            except:
                print(f"Response: {response.text[:200]}...")
                return True
        else:
            print("❌ FAILED")
            print(f"Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ EXCEPTION: {e}")
        return False

print("🚀 TESTING NEW API ENDPOINTS")
print("="*50)

results = []

# Test 1: Categories public details
success = test_endpoint(
    "Categories Public Details",
    f"{BASE_URL}/categories/public/details?include_courses=true"
)
results.append(("Categories Public Details", success))

# Test 2: Categories with courses and durations
success = test_endpoint(
    "Categories with Courses and Durations",
    f"{BASE_URL}/categories/public/with-courses-and-durations"
)
results.append(("Categories with Courses and Durations", success))

# Test 3: Category location hierarchy
if category_ids:
    success = test_endpoint(
        "Category Location Hierarchy",
        f"{BASE_URL}/categories/public/location-hierarchy?category_id={category_ids[0]}"
    )
    results.append(("Category Location Hierarchy", success))

# Test 4: Courses by category
if category_ids:
    success = test_endpoint(
        "Courses by Category",
        f"{BASE_URL}/courses/public/by-category/{category_ids[0]}"
    )
    results.append(("Courses by Category", success))

# Test 5: Durations public all
success = test_endpoint(
    "Durations Public All",
    f"{BASE_URL}/durations/public/all"
)
results.append(("Durations Public All", success))

# Test 6: Locations public details
success = test_endpoint(
    "Locations Public Details",
    f"{BASE_URL}/locations/public/details"
)
results.append(("Locations Public Details", success))

# Test 7: Locations with branches
success = test_endpoint(
    "Locations with Branches",
    f"{BASE_URL}/locations/public/with-branches"
)
results.append(("Locations with Branches", success))

# Test 8: Branches by location
if location_ids:
    success = test_endpoint(
        "Branches by Location",
        f"{BASE_URL}/branches/public/by-location/{location_ids[0]}"
    )
    results.append(("Branches by Location", success))

# Test 9: Error handling - invalid ID
success = test_endpoint(
    "Invalid Category ID (Error Test)",
    f"{BASE_URL}/categories/public/location-hierarchy?category_id=invalid-uuid",
    expected_status=404
)
results.append(("Error Handling", success))

# Summary
print(f"\n{'='*50}")
print("📊 TEST RESULTS SUMMARY")
print("="*50)

passed = sum(1 for _, success in results if success)
failed = len(results) - passed

for test_name, success in results:
    status = "✅ PASS" if success else "❌ FAIL"
    print(f"{test_name:<35} {status}")

print(f"\nTotal Tests: {len(results)}")
print(f"Passed: {passed}")
print(f"Failed: {failed}")
print(f"Success Rate: {(passed/len(results)*100):.1f}%")

if failed == 0:
    print("\n🎉 ALL TESTS PASSED!")
else:
    print(f"\n⚠️  {failed} tests failed.")
