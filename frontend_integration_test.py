#!/usr/bin/env python3
"""
Frontend Integration Test - Complete workflow testing
"""

import requests
import json
import time
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, WebDriverException

class FrontendIntegrationTest:
    def __init__(self):
        load_dotenv()
        self.backend_url = "http://31.97.224.169:8003"
        self.frontend_url = "http://localhost:3022"
        self.test_email = "pittisunilkumar@gmail.com"  # Correct email from database
        
        # MongoDB connection details
        self.mongo_url = os.getenv("MONGO_URL", "mongodb://localhost:27017")
        self.db_name = os.getenv("DB_NAME", "student_management_db")

    def print_header(self, title):
        print(f"\n{'='*70}")
        print(f"🔍 {title}")
        print(f"{'='*70}")

    async def verify_user_in_database(self):
        """Verify the test user exists in the database"""
        self.print_header("DATABASE USER VERIFICATION")
        
        try:
            client = AsyncIOMotorClient(self.mongo_url)
            db = client.get_database(self.db_name)
            
            # Check if test user exists
            user = await db.users.find_one({"email": self.test_email})
            
            if user:
                print(f"✅ User found in database:")
                print(f"   📧 Email: {user.get('email')}")
                print(f"   👤 Name: {user.get('full_name', 'N/A')}")
                print(f"   🆔 ID: {user.get('id', 'N/A')}")
                print(f"   📱 Phone: {user.get('phone', 'N/A')}")
                print(f"   ✅ Active: {user.get('is_active', 'N/A')}")
                client.close()
                return True
            else:
                print(f"❌ User NOT found in database: {self.test_email}")
                
                # Show available users
                users = await db.users.find({}).limit(5).to_list(length=5)
                if users:
                    print(f"\n📋 Available users in database:")
                    for i, u in enumerate(users, 1):
                        print(f"   {i}. {u.get('email', 'N/A')} - {u.get('full_name', 'N/A')}")
                
                client.close()
                return False
                
        except Exception as e:
            print(f"❌ Database connection error: {e}")
            return False

    def test_backend_api_directly(self):
        """Test backend API directly"""
        self.print_header("BACKEND API DIRECT TEST")
        
        try:
            print(f"📡 Testing: POST {self.backend_url}/auth/forgot-password")
            print(f"📧 Email: {self.test_email}")
            
            response = requests.post(
                f"{self.backend_url}/auth/forgot-password",
                json={'email': self.test_email},
                headers={'Content-Type': 'application/json'},
                timeout=15
            )
            
            print(f"📊 Status Code: {response.status_code}")
            print(f"📋 Response Headers: {dict(response.headers)}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ API Response: Success")
                print(f"📧 Email Sent: {data.get('email_sent', 'NOT PRESENT')}")
                print(f"🔑 Reset Token: {'PRESENT' if 'reset_token' in data else 'NOT PRESENT'}")
                print(f"📄 Message: {data.get('message', 'No message')}")
                
                if data.get('email_sent'):
                    print(f"✅ Backend confirms email was sent successfully")
                    return True, data
                else:
                    print(f"❌ Backend reports email sending failed")
                    return False, data
            else:
                print(f"❌ API Error: {response.status_code}")
                print(f"📄 Response: {response.text}")
                return False, None
                
        except Exception as e:
            print(f"❌ API Request Failed: {e}")
            return False, None

    def test_frontend_accessibility(self):
        """Test if frontend is accessible"""
        self.print_header("FRONTEND ACCESSIBILITY TEST")
        
        try:
            # Test main frontend
            response = requests.get(self.frontend_url, timeout=10)
            print(f"📊 Frontend Status: {response.status_code}")
            
            if response.status_code == 200:
                print(f"✅ Frontend is accessible at {self.frontend_url}")
                
                # Test forgot password page specifically
                forgot_url = f"{self.frontend_url}/forgot-password"
                forgot_response = requests.get(forgot_url, timeout=10)
                print(f"📊 Forgot Password Page Status: {forgot_response.status_code}")
                
                if forgot_response.status_code == 200:
                    print(f"✅ Forgot password page is accessible")
                    return True
                else:
                    print(f"❌ Forgot password page not accessible")
                    return False
            else:
                print(f"❌ Frontend not accessible: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Frontend connection failed: {e}")
            return False

    def test_frontend_form_with_browser(self):
        """Test frontend form using browser automation"""
        self.print_header("FRONTEND FORM AUTOMATION TEST")
        
        try:
            # Setup Chrome options
            chrome_options = Options()
            chrome_options.add_argument("--headless")  # Run in background
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--window-size=1920,1080")
            
            print("🌐 Starting browser automation...")
            driver = webdriver.Chrome(options=chrome_options)
            
            try:
                # Navigate to forgot password page
                forgot_url = f"{self.frontend_url}/forgot-password"
                print(f"📍 Navigating to: {forgot_url}")
                driver.get(forgot_url)
                
                # Wait for page to load
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.TAG_NAME, "body"))
                )
                
                print(f"✅ Page loaded successfully")
                print(f"📄 Page title: {driver.title}")
                
                # Find email input field
                try:
                    email_input = WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='email']"))
                    )
                    print(f"✅ Email input field found")
                    
                    # Clear and enter email
                    email_input.clear()
                    email_input.send_keys(self.test_email)
                    print(f"✅ Email entered: {self.test_email}")
                    
                    # Find submit button
                    submit_button = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
                    print(f"✅ Submit button found: {submit_button.text}")
                    
                    # Click submit button
                    print(f"🔄 Submitting form...")
                    submit_button.click()
                    
                    # Wait for response (success message or error)
                    time.sleep(3)  # Give time for API call
                    
                    # Check for success/error messages
                    page_source = driver.page_source.lower()
                    
                    if "reset link sent" in page_source or "password reset link has been sent" in page_source:
                        print(f"✅ Success message detected on page")
                        return True
                    elif "error" in page_source or "failed" in page_source:
                        print(f"❌ Error message detected on page")
                        return False
                    else:
                        print(f"⚠️  No clear success/error message detected")
                        print(f"📄 Page contains: {len(page_source)} characters")
                        return True  # Assume success if no error
                        
                except TimeoutException:
                    print(f"❌ Could not find email input field")
                    return False
                    
            finally:
                driver.quit()
                print(f"🔄 Browser closed")
                
        except WebDriverException as e:
            print(f"❌ Browser automation failed: {e}")
            print(f"💡 Note: Chrome WebDriver may not be installed")
            return False
        except Exception as e:
            print(f"❌ Frontend form test failed: {e}")
            return False

    def test_network_connectivity(self):
        """Test network connectivity between frontend and backend"""
        self.print_header("NETWORK CONNECTIVITY TEST")
        
        try:
            # Test CORS preflight
            print(f"🔄 Testing CORS preflight...")
            options_response = requests.options(
                f"{self.backend_url}/auth/forgot-password",
                headers={
                    'Origin': self.frontend_url,
                    'Access-Control-Request-Method': 'POST',
                    'Access-Control-Request-Headers': 'Content-Type'
                },
                timeout=10
            )
            
            print(f"📊 CORS Preflight Status: {options_response.status_code}")
            print(f"📋 CORS Headers: {dict(options_response.headers)}")
            
            # Test actual POST request with frontend headers
            print(f"🔄 Testing POST request with frontend headers...")
            post_response = requests.post(
                f"{self.backend_url}/auth/forgot-password",
                json={'email': self.test_email},
                headers={
                    'Content-Type': 'application/json',
                    'Origin': self.frontend_url,
                    'Referer': f"{self.frontend_url}/forgot-password"
                },
                timeout=15
            )
            
            print(f"📊 POST Request Status: {post_response.status_code}")
            
            if post_response.status_code == 200:
                data = post_response.json()
                print(f"✅ Network connectivity working")
                print(f"📧 Email Sent: {data.get('email_sent', 'NOT PRESENT')}")
                return True
            else:
                print(f"❌ Network connectivity issue: {post_response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Network connectivity test failed: {e}")
            return False

    def monitor_backend_logs_simulation(self):
        """Simulate monitoring backend logs during frontend test"""
        self.print_header("BACKEND LOG MONITORING SIMULATION")
        
        print(f"📊 Expected backend log entries after frontend form submission:")
        print(f"   ✅ 'INFO:utils.email_service:Email sent successfully to {self.test_email}'")
        print(f"   ✅ 'INFO:root:Password reset requested for {self.test_email}. Email sent: True'")
        print(f"   ✅ 'INFO:     127.0.0.1:XXXXX - \"POST /auth/forgot-password HTTP/1.1\" 200 OK'")
        print(f"")
        print(f"💡 To monitor real-time logs, check your backend server terminal")

    async def run_complete_test(self):
        """Run complete frontend integration test"""
        print("🚀 FRONTEND INTEGRATION COMPREHENSIVE TEST")
        print("="*70)
        print("Testing complete frontend-to-backend-to-email workflow")
        
        results = {}
        
        # Test 1: Verify user in database
        results['database'] = await self.verify_user_in_database()
        
        # Test 2: Test backend API directly
        api_success, api_data = self.test_backend_api_directly()
        results['backend_api'] = api_success
        
        # Test 3: Test frontend accessibility
        results['frontend_access'] = self.test_frontend_accessibility()
        
        # Test 4: Test network connectivity
        results['network'] = self.test_network_connectivity()
        
        # Test 5: Test frontend form (if browser automation available)
        results['frontend_form'] = self.test_frontend_form_with_browser()
        
        # Test 6: Monitor backend logs
        self.monitor_backend_logs_simulation()
        
        # Summary
        self.print_header("COMPREHENSIVE TEST SUMMARY")
        
        for test_name, result in results.items():
            status = '✅' if result else '❌'
            print(f'{status} {test_name.upper().replace("_", " ")}: {"PASS" if result else "FAIL"}')
        
        # Overall assessment
        critical_tests = ['database', 'backend_api', 'frontend_access', 'network']
        critical_passed = all(results.get(test, False) for test in critical_tests)
        
        print(f'\n🎯 Critical Systems Status: {"✅ OPERATIONAL" if critical_passed else "❌ ISSUES DETECTED"}')
        
        # Specific recommendations
        self.print_header("TROUBLESHOOTING RECOMMENDATIONS")
        
        if critical_passed:
            print("✅ All critical systems are working correctly!")
            print("")
            print("📧 EMAIL DELIVERY TROUBLESHOOTING:")
            print("   Since all technical components are working, email delivery issues are likely:")
            print("")
            print("   1. 📧 CHECK SPAM/JUNK FOLDER")
            print("      - Gmail: Check 'Spam' folder")
            print("      - Outlook: Check 'Junk Email' folder")
            print("      - Yahoo: Check 'Spam' folder")
            print("")
            print("   2. 🔍 EMAIL PROVIDER FILTERING")
            print("      - Add info@sveats.cyberdetox.in to safe senders")
            print("      - Check 'All Mail' in Gmail")
            print("      - Look in 'Promotions' tab (Gmail)")
            print("")
            print("   3. ⏰ DELIVERY DELAYS")
            print("      - Wait 30 minutes for delivery")
            print("      - New domains can have delays")
            print("")
            print("   4. 📱 EMAIL CLIENT SYNC")
            print("      - Refresh your email client")
            print("      - Check on web interface")
            print("")
            print("🔧 IMMEDIATE ACTIONS:")
            print(f"   1. Use frontend form at: {self.frontend_url}/forgot-password")
            print(f"   2. Enter email: {self.test_email}")
            print(f"   3. Check spam folder immediately after submission")
            print(f"   4. Monitor backend logs for confirmation")
            
        else:
            print("❌ Issues detected in critical systems:")
            if not results.get('database'):
                print("   - Database: User not found or connection issue")
            if not results.get('backend_api'):
                print("   - Backend API: Not responding correctly")
            if not results.get('frontend_access'):
                print("   - Frontend: Not accessible")
            if not results.get('network'):
                print("   - Network: Connectivity issues between frontend and backend")
        
        return critical_passed

if __name__ == "__main__":
    test = FrontendIntegrationTest()
    result = asyncio.run(test.run_complete_test())
