#!/usr/bin/env python3
"""
Manual test for user API
"""

def test_user_api():
    print("Testing User List API...")
    
    # Test with PowerShell
    import subprocess
    
    # First get superadmin token
    print("1. Getting superadmin token...")
    login_cmd = """
    $body = '{"email": "testsuperadmin@example.com", "password": "TestSuperAdmin123!"}'
    $response = Invoke-RestMethod -Uri "http://31.97.224.169:8003/api/superadmin/login" -Method POST -Body $body -ContentType "application/json"
    $response.data.token
    """
    
    try:
        result = subprocess.run(['powershell', '-Command', login_cmd], capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            token = result.stdout.strip()
            print(f"✅ Got token: {token[:20]}...")
            
            # Test user list
            print("2. Testing user list...")
            user_cmd = f"""
            $headers = @{{"Authorization" = "Bearer {token}"}}
            $response = Invoke-RestMethod -Uri "http://31.97.224.169:8003/api/users" -Method GET -Headers $headers
            $response | ConvertTo-Json
            """
            
            user_result = subprocess.run(['powershell', '-Command', user_cmd], capture_output=True, text=True, timeout=30)
            print(f"User list result: {user_result.returncode}")
            print(f"Output: {user_result.stdout}")
            if user_result.stderr:
                print(f"Error: {user_result.stderr}")
                
        else:
            print(f"❌ Login failed: {result.stderr}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_user_api()
