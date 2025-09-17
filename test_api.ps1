# PowerShell script to test the User List API

Write-Host "🔬 Testing User List API with PowerShell" -ForegroundColor Cyan
Write-Host "=" * 50

try {
    # Step 1: Get superadmin token
    Write-Host "1. Getting superadmin token..." -ForegroundColor Yellow
    
    $loginBody = @{
        email = "testsuperadmin@example.com"
        password = "TestSuperAdmin123!"
    } | ConvertTo-Json
    
    $loginResponse = Invoke-RestMethod -Uri "http://31.97.224.169:8003/api/superadmin/login" -Method POST -Body $loginBody -ContentType "application/json"
    
    if ($loginResponse.data.token) {
        Write-Host "   ✅ Login successful" -ForegroundColor Green
        $token = $loginResponse.data.token
        
        # Step 2: Test user list API
        Write-Host "2. Testing user list API..." -ForegroundColor Yellow
        
        $headers = @{
            "Authorization" = "Bearer $token"
        }
        
        $userResponse = Invoke-RestMethod -Uri "http://31.97.224.169:8003/api/users" -Method GET -Headers $headers
        
        Write-Host "   ✅ SUCCESS! User list API is working!" -ForegroundColor Green
        Write-Host "   📊 Total users: $($userResponse.total)" -ForegroundColor White
        Write-Host "   📋 Retrieved: $($userResponse.users.Count) users" -ForegroundColor White
        Write-Host "   💬 Message: $($userResponse.message)" -ForegroundColor White
        
        if ($userResponse.users.Count -gt 0) {
            Write-Host "   👥 Sample users:" -ForegroundColor White
            for ($i = 0; $i -lt [Math]::Min(3, $userResponse.users.Count); $i++) {
                $user = $userResponse.users[$i]
                Write-Host "      $($i+1). $($user.full_name) ($($user.role))" -ForegroundColor Gray
            }
        }
        
    } else {
        Write-Host "   ❌ Login failed" -ForegroundColor Red
    }
    
} catch {
    Write-Host "❌ Error: $($_.Exception.Message)" -ForegroundColor Red
    if ($_.Exception.Response) {
        Write-Host "   Status: $($_.Exception.Response.StatusCode)" -ForegroundColor Red
    }
}

Write-Host "`n🏁 Test completed!" -ForegroundColor Cyan
