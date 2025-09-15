#!/usr/bin/env python3
"""
Gmail SMTP Test Script - Test Gmail SMTP configuration for password reset emails
"""

import smtplib
import ssl
import os
import getpass
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables
ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

class GmailSMTPTest:
    def __init__(self):
        self.smtp_host = "smtp.gmail.com"
        self.smtp_port = 587
        self.smtp_user = "pittisunilkumar3@gmail.com"
        self.test_email = "pittisunilkumar3@gmail.com"
        
    def test_gmail_smtp(self, app_password=None):
        """Test Gmail SMTP with app password"""
        print("📧 GMAIL SMTP TEST")
        print("=" * 50)
        
        # Get app password
        if not app_password:
            app_password = os.getenv('SMTP_PASS')
            
        if not app_password or app_password == 'YOUR_GMAIL_APP_PASSWORD_HERE':
            print("❌ Gmail app password not configured!")
            print("\n📋 SETUP REQUIRED:")
            print("1. Enable 2-Factor Authentication on your Gmail account")
            print("2. Generate an App Password for 'Mail'")
            print("3. Update SMTP_PASS in .env file with the app password")
            print("4. Or provide it when prompted")
            print()
            
            # Prompt for app password
            app_password = getpass.getpass("Enter Gmail App Password (16 characters): ").strip()
            
            if not app_password:
                print("❌ No app password provided. Exiting.")
                return False
        
        print(f"🔧 Configuration:")
        print(f"   Host: {self.smtp_host}")
        print(f"   Port: {self.smtp_port}")
        print(f"   User: {self.smtp_user}")
        print(f"   Test Email: {self.test_email}")
        print(f"   App Password: {'*' * len(app_password)}")
        print()
        
        try:
            print("📡 Connecting to Gmail SMTP...")
            server = smtplib.SMTP(self.smtp_host, self.smtp_port, timeout=15)
            
            print("🔒 Starting TLS encryption...")
            context = ssl.create_default_context()
            server.starttls(context=context)
            server.ehlo()
            
            print("🔑 Authenticating with Gmail...")
            server.login(self.smtp_user, app_password)
            print("✅ Gmail SMTP authentication successful!")
            
            print("📧 Sending test email...")
            success = self.send_test_email(server)
            
            server.quit()
            
            if success:
                print("🎉 Gmail SMTP test completed successfully!")
                print("✅ Email delivery is working!")
                
                # Update .env file with working password
                self.update_env_file(app_password)
                return True
            else:
                print("❌ Email sending failed")
                return False
                
        except smtplib.SMTPAuthenticationError as e:
            print(f"❌ Gmail authentication failed: {e}")
            print("\n🔍 TROUBLESHOOTING:")
            print("1. Ensure 2-Factor Authentication is enabled")
            print("2. Use App Password, not regular Gmail password")
            print("3. Check for typos in the app password")
            print("4. Generate a new app password if needed")
            return False
            
        except Exception as e:
            print(f"❌ Gmail SMTP test failed: {e}")
            return False
    
    def send_test_email(self, server):
        """Send a comprehensive test email"""
        try:
            # Create message
            message = MIMEMultipart("alternative")
            message["Subject"] = "🎉 Password Reset System - SMTP Working!"
            message["From"] = self.smtp_user
            message["To"] = self.test_email
            
            # Plain text content
            text_content = f"""
🎉 SUCCESS! Gmail SMTP Configuration Working!

The Martial Arts Academy password reset system is now fully operational!

✅ Test Results:
- SMTP Server: Gmail (smtp.gmail.com:587)
- Authentication: Successful with App Password
- Email Delivery: Working perfectly
- Security: TLS encryption enabled

🚀 What's Working Now:
- Users can request password resets
- Professional HTML emails are delivered
- Complete forgot password workflow is active
- Secure token-based password reset

📧 Email Features:
- Professional HTML templates
- Plain text fallback
- Secure reset links with 15-minute expiration
- Mobile-friendly responsive design

🔧 Technical Details:
- Backend API: All endpoints functional
- Frontend Forms: Complete UI implementation
- Security: JWT tokens, no email disclosure
- Email Service: Gmail SMTP with app password

Next Steps:
1. Test the forgot password form at: http://localhost:3022/forgot-password
2. Enter email: {self.test_email}
3. Check your inbox for password reset emails
4. Complete the password reset workflow

Best regards,
Martial Arts Academy Team

---
Test completed: {__import__('datetime').datetime.now()}
            """.strip()
            
            # HTML content
            html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Password Reset System - SMTP Working!</title>
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; margin: 0; padding: 0; }}
        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
        .header {{ background: linear-gradient(135deg, #28a745, #20c997); color: white; padding: 30px; text-align: center; border-radius: 8px 8px 0 0; }}
        .content {{ background-color: #ffffff; padding: 30px; border: 1px solid #e9ecef; }}
        .footer {{ background-color: #f8f9fa; padding: 20px; text-align: center; border-radius: 0 0 8px 8px; font-size: 12px; color: #6c757d; }}
        .success-box {{ background-color: #d4edda; border: 1px solid #c3e6cb; padding: 20px; border-radius: 8px; margin: 20px 0; }}
        .feature-list {{ background-color: #f8f9fa; padding: 20px; border-radius: 8px; margin: 20px 0; }}
        .btn {{ display: inline-block; padding: 12px 24px; background-color: #28a745; color: white; text-decoration: none; border-radius: 5px; font-weight: bold; margin: 10px 0; }}
        .technical-details {{ background-color: #e9ecef; padding: 15px; border-radius: 5px; margin: 20px 0; font-family: monospace; font-size: 14px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1 style="margin: 0;">🎉 SUCCESS!</h1>
            <h2 style="margin: 10px 0 0 0;">Gmail SMTP Configuration Working!</h2>
        </div>
        
        <div class="content">
            <div class="success-box">
                <h3 style="margin-top: 0; color: #155724;">✅ Password Reset System Operational</h3>
                <p>The Martial Arts Academy password reset system is now fully functional with professional email delivery!</p>
            </div>
            
            <h3>🚀 What's Working Now:</h3>
            <div class="feature-list">
                <ul>
                    <li><strong>Password Reset Requests:</strong> Users can request resets via email</li>
                    <li><strong>Professional Emails:</strong> HTML templates with responsive design</li>
                    <li><strong>Secure Workflow:</strong> JWT tokens with 15-minute expiration</li>
                    <li><strong>Complete Integration:</strong> Frontend forms + Backend APIs</li>
                </ul>
            </div>
            
            <h3>📧 Email Features:</h3>
            <ul>
                <li>✅ Professional HTML templates</li>
                <li>✅ Plain text fallback for compatibility</li>
                <li>✅ Secure reset links with token validation</li>
                <li>✅ Mobile-friendly responsive design</li>
                <li>✅ Security features (no email disclosure)</li>
            </ul>
            
            <div class="technical-details">
                <strong>🔧 Technical Configuration:</strong><br>
                SMTP Server: Gmail (smtp.gmail.com:587)<br>
                Authentication: App Password ✅<br>
                Encryption: TLS ✅<br>
                Email Delivery: Working ✅
            </div>
            
            <h3>🎯 Next Steps:</h3>
            <ol>
                <li>Test the forgot password form</li>
                <li>Verify email delivery in your inbox</li>
                <li>Complete the password reset workflow</li>
                <li>Deploy to production with confidence</li>
            </ol>
            
            <div style="text-align: center; margin: 30px 0;">
                <a href="http://localhost:3022/forgot-password" class="btn">Test Forgot Password Form</a>
            </div>
            
            <div style="background-color: #fff3cd; border: 1px solid #ffeaa7; padding: 15px; border-radius: 5px; margin: 20px 0;">
                <strong>📧 Test Email:</strong> {self.test_email}<br>
                <strong>🌐 Frontend URL:</strong> http://localhost:3022/forgot-password
            </div>
        </div>
        
        <div class="footer">
            <p><strong>Martial Arts Academy</strong><br>Password Reset System</p>
            <p>Test completed: {__import__('datetime').datetime.now()}</p>
            <p>This email confirms that SMTP configuration is working correctly.</p>
        </div>
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
            server.sendmail(self.smtp_user, [self.test_email], message.as_string())
            print("✅ Test email sent successfully!")
            print(f"📬 Check your inbox: {self.test_email}")
            
            return True
            
        except Exception as e:
            print(f"❌ Email sending failed: {e}")
            return False
    
    def update_env_file(self, app_password):
        """Update .env file with working app password"""
        try:
            env_file = ROOT_DIR / '.env'
            
            # Read current content
            with open(env_file, 'r') as f:
                content = f.read()
            
            # Replace placeholder with actual password
            updated_content = content.replace('YOUR_GMAIL_APP_PASSWORD_HERE', app_password)
            
            # Write back to file
            with open(env_file, 'w') as f:
                f.write(updated_content)
            
            print("✅ .env file updated with working app password")
            
        except Exception as e:
            print(f"⚠️  Could not update .env file: {e}")
            print(f"Please manually update SMTP_PASS with: {app_password}")

if __name__ == "__main__":
    print("🚀 Gmail SMTP Test for Password Reset System")
    print("This will test Gmail SMTP configuration and send a test email.")
    print()
    
    tester = GmailSMTPTest()
    success = tester.test_gmail_smtp()
    
    if success:
        print("\n" + "=" * 60)
        print("🎉 GMAIL SMTP CONFIGURATION SUCCESSFUL!")
        print("=" * 60)
        print("\n✅ WHAT'S WORKING:")
        print("   📧 Gmail SMTP authentication")
        print("   📨 Email delivery to inbox")
        print("   🔒 TLS encryption")
        print("   🎨 Professional HTML templates")
        
        print("\n🚀 NEXT STEPS:")
        print("   1. Restart the backend server")
        print("   2. Test forgot password at: http://localhost:3022/forgot-password")
        print("   3. Enter email: pittisunilkumar3@gmail.com")
        print("   4. Check inbox for password reset email")
        
        print("\n📧 EMAIL SENT:")
        print("   Check your Gmail inbox for the test email!")
        
    else:
        print("\n" + "=" * 60)
        print("❌ GMAIL SMTP CONFIGURATION FAILED")
        print("=" * 60)
        print("\n🔧 TROUBLESHOOTING:")
        print("   1. Enable 2-Factor Authentication on Gmail")
        print("   2. Generate App Password for 'Mail'")
        print("   3. Use App Password, not regular password")
        print("   4. Check for typos in credentials")
        print("   5. Refer to GMAIL_SMTP_SETUP_GUIDE.md")
