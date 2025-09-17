# PowerShell script to test the courses API
Write-Host "🧪 Testing Enhanced Courses API" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green

try {
    $response = Invoke-WebRequest -Uri "http://31.97.224.169:8003/api/courses/public/all" -Method GET
    
    if ($response.StatusCode -eq 200) {
        Write-Host "✅ API call successful!" -ForegroundColor Green
        
        $data = $response.Content | ConvertFrom-Json
        $courses = $data.courses
        
        Write-Host "   Found $($courses.Count) courses" -ForegroundColor White
        
        if ($courses.Count -gt 0) {
            $course = $courses[0]
            Write-Host ""
            Write-Host "📋 Sample course data:" -ForegroundColor Yellow
            Write-Host "   Title: $($course.title)" -ForegroundColor White
            Write-Host "   Name: $($course.name)" -ForegroundColor White
            Write-Host "   Branches: $($course.branches)" -ForegroundColor White
            Write-Host "   Masters: $($course.masters)" -ForegroundColor White
            Write-Host "   Students: $($course.students)" -ForegroundColor White
            Write-Host "   Icon: $($course.icon)" -ForegroundColor White
            Write-Host "   Enabled: $($course.enabled)" -ForegroundColor White
            Write-Host "   Branch assignments: $($course.branch_assignments.Count)" -ForegroundColor White
            Write-Host "   Instructor assignments: $($course.instructor_assignments.Count)" -ForegroundColor White
            Write-Host "   Student enrollment count: $($course.student_enrollment_count)" -ForegroundColor White
            
            if ($course.instructor_assignments.Count -gt 0) {
                Write-Host "   Assigned instructors:" -ForegroundColor Cyan
                foreach ($instructor in $course.instructor_assignments) {
                    Write-Host "     - $($instructor.instructor_name) ($($instructor.email))" -ForegroundColor White
                }
            }
        }
    } else {
        Write-Host "❌ API call failed: $($response.StatusCode)" -ForegroundColor Red
    }
} catch {
    Write-Host "❌ Error testing API: $($_.Exception.Message)" -ForegroundColor Red
}
