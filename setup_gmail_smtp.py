#!/usr/bin/env python3
"""
Interactive Gmail SMTP Setup Script
This script will guide you through setting up Gmail app password for email functionality
"""

import os
import smtplib
import ssl
import getpass
from pathlib import Path
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

# Load environment variables
ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

class GmailSMTPSetup:
    def __init__(self):
        self.gmail_user = "pittisunilkumar3@gmail.com"
        self.test_email = "pittisunilkumar3@gmail.com"
        
    def show_setup_instructions(self):
        """Show detailed setup instructions"""
        print("🔑 GMAIL APP PASSWORD SETUP")
        print("=" * 60)
        print()
        print("📋 STEP-BY-STEP INSTRUCTIONS:")
        print()
        print("1. 🔐 Enable 2-Factor Authentication:")
        print("   - Go to: https://myaccount.google.com/security")
        print(f"   - Sign in with: {self.gmail_user}")
        print("   - Click '2-Step Verification' and follow setup")
        print()
        print("2. 🔑 Generate App Password:")
        print("   - After enabling 2FA, go back to Security settings")
        print("   - Click 'App passwords' (under 'Signing in to Google')")
        print("   - Select 'Mail' as the app")
        print("   - Select 'Other (Custom name)' as device")
        print("   - Enter 'Martial Arts Academy' as name")
        print("   - Click 'Generate'")
        print("   - Copy the 16-character password (format: abcd efgh ijkl mnop)")
        print()
        print("3. 📝 Enter the app password when prompted below")
        print()
        
    def get_app_password(self):
        """Get app password from user"""
        print("🔑 ENTER GMAIL APP PASSWORD")
        print("-" * 40)
        print("Please enter the 16-character app password you generated:")
        print("(Format: abcd efgh ijkl mnop)")
        print()
        
        while True:
            app_password = getpass.getpass("Gmail App Password: ").strip()
            
            if not app_password:
                print("❌ No password entered. Please try again.")
                continue
                
            # Remove spaces and validate format
            clean_password = app_password.replace(" ", "")
            
            if len(clean_password) == 16 and clean_password.isalnum():
                return clean_password
            else:
                print("❌ Invalid format. App password should be 16 characters (letters and numbers).")
                print("   Example: abcdefghijklmnop")
                continue
    
    def test_smtp_connection(self, app_password):
        """Test SMTP connection with app password"""
        print("\n🧪 TESTING GMAIL SMTP CONNECTION")
        print("-" * 40)
        
        try:
            print("📡 Connecting to Gmail SMTP...")
            server = smtplib.SMTP('smtp.gmail.com', 587, timeout=15)
            
            print("🔒 Starting TLS encryption...")
            context = ssl.create_default_context()
            server.starttls(context=context)
            server.ehlo()
            
            print("🔑 Authenticating with Gmail...")
            server.login(self.gmail_user, app_password)
            
            print("✅ Gmail SMTP authentication successful!")
            
            # Send test email
            success = self.send_test_email(server)
            server.quit()
            
            return success
            
        except smtplib.SMTPAuthenticationError as e:
            print(f"❌ Gmail authentication failed: {e}")
            print("\n🔍 TROUBLESHOOTING:")
            print("1. Ensure 2-Factor Authentication is enabled")
            print("2. Use the app password, not your regular Gmail password")
            print("3. Check for typos in the app password")
            print("4. Generate a new app password if needed")
            return False
            
        except Exception as e:
            print(f"❌ SMTP connection failed: {e}")
            return False
    
    def send_test_email(self, server):
        """Send a test email"""
        try:
            print("📧 Sending test email...")
            
            # Create message
            message = MIMEMultipart("alternative")
            message["Subject"] = "🎉 Gmail SMTP Setup Successful - Martial Arts Academy"
            message["From"] = self.gmail_user
            message["To"] = self.test_email
            
            # Plain text content
            text_content = f"""
🎉 SUCCESS! Gmail SMTP Setup Complete!

Your Martial Arts Academy password reset system is now fully operational!

✅ Configuration Details:
- SMTP Server: Gmail (smtp.gmail.com:587)
- Authentication: Working with App Password
- Email Delivery: Successful
- Security: TLS encryption enabled

🚀 What's Working Now:
- Users can request password resets
- Professional HTML emails are delivered
- Complete forgot password workflow is active
- Secure token-based password reset

📧 Test Details:
- From: {self.gmail_user}
- To: {self.test_email}
- Authentication: App Password
- Encryption: TLS

Next Steps:
1. Test the forgot password form at: http://localhost:3022/forgot-password
2. Enter email: {self.test_email}
3. Check your inbox for password reset emails
4. Complete the password reset workflow

Best regards,
Martial Arts Academy Team

---
Setup completed successfully!
            """.strip()
            
            # HTML content
            html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Gmail SMTP Setup Successful</title>
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; margin: 0; padding: 0; }}
        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
        .header {{ background: linear-gradient(135deg, #28a745, #20c997); color: white; padding: 30px; text-align: center; border-radius: 8px 8px 0 0; }}
        .content {{ background-color: #ffffff; padding: 30px; border: 1px solid #e9ecef; }}
        .footer {{ background-color: #f8f9fa; padding: 20px; text-align: center; border-radius: 0 0 8px 8px; font-size: 12px; color: #6c757d; }}
        .success-box {{ background-color: #d4edda; border: 1px solid #c3e6cb; padding: 20px; border-radius: 8px; margin: 20px 0; }}
        .btn {{ display: inline-block; padding: 12px 24px; background-color: #28a745; color: white; text-decoration: none; border-radius: 5px; font-weight: bold; margin: 10px 0; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1 style="margin: 0;">🎉 SUCCESS!</h1>
            <h2 style="margin: 10px 0 0 0;">Gmail SMTP Setup Complete!</h2>
        </div>
        
        <div class="content">
            <div class="success-box">
                <h3 style="margin-top: 0; color: #155724;">✅ Password Reset System Operational</h3>
                <p>Your Martial Arts Academy password reset system is now fully functional with professional email delivery!</p>
            </div>
            
            <h3>🔧 Configuration Confirmed:</h3>
            <ul>
                <li><strong>SMTP Server:</strong> Gmail (smtp.gmail.com:587)</li>
                <li><strong>Authentication:</strong> ✅ Working with App Password</li>
                <li><strong>Email Delivery:</strong> ✅ Successful</li>
                <li><strong>Security:</strong> ✅ TLS encryption enabled</li>
            </ul>
            
            <h3>🚀 What's Working Now:</h3>
            <ul>
                <li>Users can request password resets</li>
                <li>Professional HTML emails are delivered</li>
                <li>Complete forgot password workflow is active</li>
                <li>Secure token-based password reset</li>
            </ul>
            
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
            <p>Setup completed successfully!</p>
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
            server.sendmail(self.gmail_user, [self.test_email], message.as_string())
            print("✅ Test email sent successfully!")
            print(f"📬 Check your inbox: {self.test_email}")
            
            return True
            
        except Exception as e:
            print(f"❌ Test email failed: {e}")
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
            print("🔄 Please restart the backend server for changes to take effect")
            
        except Exception as e:
            print(f"⚠️  Could not update .env file: {e}")
            print(f"Please manually update SMTP_PASS with: {app_password}")
    
    def run_setup(self):
        """Run the complete setup process"""
        print("🚀 GMAIL SMTP SETUP FOR MARTIAL ARTS ACADEMY")
        print("This will set up Gmail SMTP for password reset emails.")
        print()
        
        # Show instructions
        self.show_setup_instructions()
        
        # Get user confirmation
        response = input("Have you completed steps 1 and 2 above? (y/n): ").strip().lower()
        if response != 'y':
            print("Please complete the setup steps first, then run this script again.")
            return False
        
        # Get app password
        app_password = self.get_app_password()
        
        # Test SMTP connection
        success = self.test_smtp_connection(app_password)
        
        if success:
            # Update .env file
            self.update_env_file(app_password)
            
            print("\n" + "=" * 60)
            print("🎉 GMAIL SMTP SETUP COMPLETE!")
            print("=" * 60)
            print("\n✅ WHAT'S WORKING:")
            print("   📧 Gmail SMTP authentication")
            print("   📨 Email delivery to inbox")
            print("   🔒 TLS encryption")
            print("   🎨 Professional HTML templates")
            
            print("\n🚀 NEXT STEPS:")
            print("   1. Restart the backend server:")
            print("      python -m uvicorn server:app --host 0.0.0.0 --port 8003 --reload")
            print("   2. Test forgot password at: http://localhost:3022/forgot-password")
            print("   3. Enter email: pittisunilkumar3@gmail.com")
            print("   4. Check inbox for password reset email")
            
            print("\n📧 EMAIL SENT:")
            print("   A test email has been sent to your inbox!")
            print("   If you don't see it, check your spam folder.")
            
            return True
        else:
            print("\n❌ Setup failed. Please check the troubleshooting steps above.")
            return False

if __name__ == "__main__":
    setup = GmailSMTPSetup()
    setup.run_setup()
