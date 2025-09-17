#!/usr/bin/env python3
"""
Complete Email Investigation - End-to-End Testing
"""

import requests
import json
import time
import smtplib
import ssl
import os
from dotenv import load_dotenv
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

class CompleteEmailInvestigation:
    def __init__(self):
        load_dotenv()
        self.backend_url = "http://31.97.224.169:8003"
        self.frontend_url = "http://localhost:3022"
        self.test_email = "pittisunilkumar@gmail.com"  # Correct email in database
        
        # SMTP Configuration
        self.smtp_host = os.getenv('SMTP_HOST', 'sveats.cyberdetox.in')
        self.smtp_port = int(os.getenv('SMTP_PORT', '587'))
        self.smtp_user = os.getenv('SMTP_USER', 'info@sveats.cyberdetox.in')
        self.smtp_pass = os.getenv('SMTP_PASS', 'Neelarani@10')
        self.smtp_from = os.getenv('SMTP_FROM', 'info@sveats.cyberdetox.in')

    def print_header(self, title):
        print(f"\n{'='*60}")
        print(f"🔍 {title}")
        print(f"{'='*60}")

    def test_backend_connectivity(self):
        """Test backend server connectivity"""
        self.print_header("BACKEND CONNECTIVITY TEST")
        
        try:
            response = requests.get(f"{self.backend_url}/docs", timeout=10)
            if response.status_code == 200:
                print("✅ Backend server is running and accessible")
                return True
            else:
                print(f"⚠️  Backend responding with status: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Backend connection failed: {e}")
            return False

    def test_frontend_connectivity(self):
        """Test frontend server connectivity"""
        self.print_header("FRONTEND CONNECTIVITY TEST")
        
        try:
            response = requests.get(self.frontend_url, timeout=10)
            if response.status_code == 200:
                print("✅ Frontend server is running and accessible")
                return True
            else:
                print(f"⚠️  Frontend responding with status: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Frontend connection failed: {e}")
            return False

    def test_direct_smtp(self):
        """Test direct SMTP connection and email sending"""
        self.print_header("DIRECT SMTP CONNECTION TEST")
        
        try:
            print(f"🔗 Connecting to {self.smtp_host}:{self.smtp_port}")
            
            # Create SMTP connection
            server = smtplib.SMTP(self.smtp_host, self.smtp_port, timeout=10)
            print("✅ SMTP connection established")
            
            # Start TLS
            server.starttls()
            print("✅ TLS encryption enabled")
            
            # Authenticate
            server.login(self.smtp_user, self.smtp_pass)
            print("✅ SMTP authentication successful")
            
            # Send test email
            message = MIMEMultipart("alternative")
            message["Subject"] = "🧪 Direct SMTP Test - Password Reset Investigation"
            message["From"] = self.smtp_from
            message["To"] = self.test_email
            
            text_content = f"""
Direct SMTP Test Email

This email was sent directly via SMTP to test email delivery.

Time: {time.strftime('%Y-%m-%d %H:%M:%S')}
From: Password Reset Investigation
SMTP Server: {self.smtp_host}:{self.smtp_port}

If you receive this email, direct SMTP delivery is working correctly.
            """.strip()
            
            html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        .header {{ background-color: #f8f9fa; padding: 20px; border-radius: 8px; }}
        .content {{ margin: 20px 0; }}
        .footer {{ color: #666; font-size: 12px; margin-top: 20px; }}
    </style>
</head>
<body>
    <div class="header">
        <h2>🧪 Direct SMTP Test Email</h2>
        <p>Password Reset Investigation</p>
    </div>
    
    <div class="content">
        <p>This email was sent directly via SMTP to test email delivery.</p>
        
        <p><strong>Test Details:</strong></p>
        <ul>
            <li>Time: {time.strftime('%Y-%m-%d %H:%M:%S')}</li>
            <li>SMTP Server: {self.smtp_host}:{self.smtp_port}</li>
            <li>From: {self.smtp_from}</li>
            <li>To: {self.test_email}</li>
        </ul>
        
        <p>If you receive this email, direct SMTP delivery is working correctly.</p>
    </div>
    
    <div class="footer">
        <p>This is a test email from the Password Reset Investigation.</p>
    </div>
</body>
</html>
            """.strip()
            
            # Add parts to message
            text_part = MIMEText(text_content, "plain")
            html_part = MIMEText(html_content, "html")
            
            message.attach(text_part)
            message.attach(html_part)
            
            # Send email
            server.sendmail(self.smtp_from, [self.test_email], message.as_string())
            print("✅ Direct SMTP email sent successfully")
            
            server.quit()
            print("✅ SMTP connection closed properly")
            return True
            
        except Exception as e:
            print(f"❌ Direct SMTP test failed: {e}")
            return False

    def test_backend_api(self):
        """Test backend forgot password API"""
        self.print_header("BACKEND API TEST")
        
        try:
            response = requests.post(
                f"{self.backend_url}/auth/forgot-password",
                json={'email': self.test_email},
                timeout=15
            )
            
            print(f"📊 Status Code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print("✅ API Response: Success")
                print(f"📧 Email Sent: {data.get('email_sent', 'NOT PRESENT')}")
                print(f"🔑 Reset Token: {'PRESENT' if 'reset_token' in data else 'NOT PRESENT'}")
                print(f"📄 Message: {data.get('message', 'No message')}")
                
                if data.get('email_sent'):
                    print("✅ Backend reports email was sent successfully")
                    return True, data.get('reset_token')
                else:
                    print("❌ Backend reports email sending failed")
                    return False, None
            else:
                print(f"❌ API Error: {response.status_code}")
                print(f"📄 Response: {response.text}")
                return False, None
                
        except Exception as e:
            print(f"❌ API Request Failed: {e}")
            return False, None

    def test_password_reset_workflow(self, reset_token):
        """Test complete password reset workflow"""
        if not reset_token:
            print("❌ No reset token available for workflow test")
            return False
            
        self.print_header("PASSWORD RESET WORKFLOW TEST")
        
        try:
            # Test password reset with token
            new_password = "NewTestPassword123!"
            
            response = requests.post(
                f"{self.backend_url}/auth/reset-password",
                json={'token': reset_token, 'new_password': new_password},
                timeout=15
            )
            
            if response.status_code == 200:
                print("✅ Password reset successful")
                
                # Test login with new password
                login_response = requests.post(
                    f"{self.backend_url}/auth/login",
                    json={'email': self.test_email, 'password': new_password},
                    timeout=15
                )
                
                if login_response.status_code == 200:
                    login_data = login_response.json()
                    print("✅ Login successful with new password")
                    print(f"🎫 Access token received: {len(login_data.get('access_token', ''))} characters")
                    return True
                else:
                    print(f"❌ Login failed: {login_response.status_code}")
                    return False
            else:
                print(f"❌ Password reset failed: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Workflow test failed: {e}")
            return False

    def run_complete_investigation(self):
        """Run complete email investigation"""
        print("🚀 COMPLETE EMAIL DELIVERY INVESTIGATION")
        print("="*60)
        print("Testing all components of the password reset email system")
        
        results = {}
        
        # Test 1: Backend connectivity
        results['backend'] = self.test_backend_connectivity()
        
        # Test 2: Frontend connectivity
        results['frontend'] = self.test_frontend_connectivity()
        
        # Test 3: Direct SMTP
        results['smtp'] = self.test_direct_smtp()
        
        # Test 4: Backend API
        api_success, reset_token = self.test_backend_api()
        results['api'] = api_success
        
        # Test 5: Complete workflow
        if reset_token:
            results['workflow'] = self.test_password_reset_workflow(reset_token)
        else:
            results['workflow'] = False
        
        # Summary
        self.print_header("INVESTIGATION SUMMARY")
        
        for test_name, result in results.items():
            status = '✅' if result else '❌'
            print(f'{status} {test_name.upper()}: {"PASS" if result else "FAIL"}')
        
        # Overall assessment
        all_passed = all(results.values())
        print(f'\n🎯 Overall Status: {"✅ ALL SYSTEMS OPERATIONAL" if all_passed else "❌ ISSUES DETECTED"}')
        
        # Recommendations
        if results['smtp'] and results['api']:
            print('\n📧 EMAIL DELIVERY ANALYSIS:')
            print('✅ SMTP server is working correctly')
            print('✅ Backend API is sending emails successfully')
            print('✅ Email service is functional')
            print('\n💡 LIKELY CAUSES OF EMAIL NOT BEING RECEIVED:')
            print('   1. 📧 Emails going to SPAM/JUNK folder')
            print('   2. 🔍 Email provider filtering (Gmail/Outlook blocking unknown senders)')
            print('   3. ⏰ Delivery delays (new domains can have 5-30 minute delays)')
            print('   4. 📱 Email client sync issues')
            print('\n🔧 RECOMMENDED ACTIONS:')
            print('   1. Check SPAM/JUNK folder thoroughly')
            print('   2. Add info@sveats.cyberdetox.in to safe senders list')
            print('   3. Wait 30 minutes and check again')
            print('   4. Try with a different email provider (Yahoo, Outlook)')
            print('   5. Consider using Gmail SMTP for better deliverability')
        
        return all_passed

if __name__ == "__main__":
    investigation = CompleteEmailInvestigation()
    investigation.run_complete_investigation()
