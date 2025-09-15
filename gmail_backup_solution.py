#!/usr/bin/env python3
"""
Gmail SMTP Backup Solution
Alternative email configuration using Gmail SMTP for guaranteed delivery
"""

import smtplib
import ssl
import os
import asyncio
import sys
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

# Add current directory to path
sys.path.append('.')

class GmailBackupSolution:
    def __init__(self):
        load_dotenv()
        self.test_email = 'pittisunilkumar3@gmail.com'
        
    def print_header(self, title):
        """Print a formatted header"""
        print(f"\n{'='*60}")
        print(f"📧 {title}")
        print(f"{'='*60}")
        
    def setup_gmail_smtp(self):
        """Setup Gmail SMTP configuration"""
        self.print_header("GMAIL SMTP BACKUP SOLUTION")
        
        print("🔧 Setting up Gmail SMTP as backup email solution...")
        print("\n📋 Gmail SMTP Configuration:")
        print("   Host: smtp.gmail.com")
        print("   Port: 587")
        print("   Security: STARTTLS")
        print("   Authentication: App Password Required")
        
        print("\n⚠️  IMPORTANT: You need a Gmail App Password")
        print("   1. Go to Google Account settings")
        print("   2. Enable 2-Factor Authentication")
        print("   3. Generate App Password for 'Mail'")
        print("   4. Use the 16-character app password")
        
        # Get Gmail credentials
        gmail_user = input("\n📧 Enter your Gmail address: ").strip()
        if not gmail_user:
            gmail_user = self.test_email
            
        gmail_pass = input("🔑 Enter your Gmail App Password (16 chars): ").strip()
        
        return gmail_user, gmail_pass
        
    def test_gmail_smtp(self, gmail_user, gmail_pass):
        """Test Gmail SMTP connection"""
        print(f"\n🧪 Testing Gmail SMTP connection...")
        
        try:
            # Test connection
            print("🔌 Connecting to Gmail SMTP...")
            server = smtplib.SMTP('smtp.gmail.com', 587, timeout=10)
            
            print("🔒 Starting TLS encryption...")
            context = ssl.create_default_context()
            server.starttls(context=context)
            
            print("🔑 Authenticating with Gmail...")
            server.login(gmail_user, gmail_pass)
            print("✅ Gmail SMTP authentication successful!")
            
            # Send test email
            success = self.send_test_email(server, gmail_user)
            server.quit()
            
            return success
            
        except smtplib.SMTPAuthenticationError as e:
            print(f"❌ Gmail authentication failed: {e}")
            print("💡 Make sure you're using an App Password, not your regular password")
            return False
            
        except Exception as e:
            print(f"❌ Gmail SMTP test failed: {e}")
            return False
            
    def send_test_email(self, server, gmail_user):
        """Send test email via Gmail"""
        try:
            print("📧 Sending test email via Gmail...")
            
            # Create message
            message = MIMEMultipart("alternative")
            message["Subject"] = "🎉 Gmail SMTP Working - Password Reset System Ready!"
            message["From"] = gmail_user
            message["To"] = self.test_email
            
            # HTML content
            html_content = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Gmail SMTP Success</title>
    <style>
        body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
        .container { max-width: 600px; margin: 0 auto; padding: 20px; }
        .header { background: linear-gradient(135deg, #4285f4 0%, #34a853 100%); color: white; padding: 20px; text-align: center; border-radius: 8px 8px 0 0; }
        .content { background: #f8f9fa; padding: 20px; border: 1px solid #e9ecef; }
        .success { background: #d4edda; border: 1px solid #c3e6cb; padding: 15px; border-radius: 5px; margin: 20px 0; }
        .footer { background: #6c757d; color: white; padding: 15px; text-align: center; border-radius: 0 0 8px 8px; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎉 Gmail SMTP Success!</h1>
            <p>Martial Arts Academy Email System</p>
        </div>
        
        <div class="content">
            <div class="success">
                <strong>✅ Gmail SMTP Configuration Successful!</strong>
            </div>
            
            <p>The Martial Arts Academy password reset system is now fully functional using Gmail SMTP!</p>
            
            <h3>✅ Configuration Details:</h3>
            <ul>
                <li><strong>SMTP Provider:</strong> Gmail</li>
                <li><strong>Authentication:</strong> Working</li>
                <li><strong>Email Delivery:</strong> Successful</li>
                <li><strong>Security:</strong> App Password Used</li>
            </ul>
            
            <h3>🚀 Next Steps:</h3>
            <ul>
                <li>Users can now request password resets</li>
                <li>Professional emails will be delivered reliably</li>
                <li>Complete forgot password workflow is active</li>
            </ul>
        </div>
        
        <div class="footer">
            <p>Best regards,<br>
            <strong>Martial Arts Academy Team</strong></p>
        </div>
    </div>
</body>
</html>
            """.strip()
            
            # Plain text content
            text_content = """
🎉 Gmail SMTP Configuration Successful!

The Martial Arts Academy password reset system is now fully functional!

✅ Configuration Details:
- SMTP Provider: Gmail
- Authentication: Working
- Email Delivery: Successful
- Security: App Password Used

🚀 Next Steps:
- Users can now request password resets
- Professional emails will be delivered reliably
- Complete forgot password workflow is active

Best regards,
Martial Arts Academy Team
            """.strip()
            
            # Add parts
            text_part = MIMEText(text_content, "plain")
            html_part = MIMEText(html_content, "html")
            message.attach(text_part)
            message.attach(html_part)
            
            # Send email
            server.sendmail(gmail_user, self.test_email, message.as_string())
            print("✅ Test email sent successfully via Gmail!")
            
            return True
            
        except Exception as e:
            print(f"❌ Failed to send test email: {e}")
            return False
            
    def update_env_file(self, gmail_user, gmail_pass):
        """Update .env file with Gmail configuration"""
        print(f"\n📝 Updating .env file with Gmail SMTP configuration...")
        
        # Read current .env file
        env_file = '.env'
        with open(env_file, 'r') as f:
            lines = f.readlines()
            
        # Update SMTP settings
        updated_lines = []
        smtp_settings = {
            'SMTP_HOST': 'smtp.gmail.com',
            'SMTP_PORT': '587',
            'SMTP_USER': gmail_user,
            'SMTP_PASS': gmail_pass,
            'SMTP_FROM': gmail_user
        }
        
        for line in lines:
            updated = False
            for key, value in smtp_settings.items():
                if line.startswith(f'{key}='):
                    updated_lines.append(f'{key}={value}\n')
                    updated = True
                    break
            if not updated:
                updated_lines.append(line)
                
        # Write updated .env file
        with open(env_file, 'w') as f:
            f.writelines(updated_lines)
            
        print("✅ .env file updated successfully!")
        print("\n📋 New SMTP Configuration:")
        for key, value in smtp_settings.items():
            if key == 'SMTP_PASS':
                print(f"   {key}=***hidden***")
            else:
                print(f"   {key}={value}")
                
    async def test_updated_system(self):
        """Test the system with updated Gmail configuration"""
        print(f"\n🧪 Testing updated system with Gmail SMTP...")
        
        try:
            from utils.email_service import send_password_reset_email
            
            # Reload email service to pick up new config
            import importlib
            import utils.email_service
            importlib.reload(utils.email_service)
            
            result = await send_password_reset_email(
                to_email=self.test_email,
                reset_token="gmail_test_token_123",
                user_name="Gmail Test User"
            )
            
            if result:
                print("✅ Updated system working with Gmail SMTP!")
                return True
            else:
                print("❌ Updated system test failed")
                return False
                
        except Exception as e:
            print(f"❌ System test error: {e}")
            return False

if __name__ == "__main__":
    print("🚀 Gmail SMTP Backup Solution")
    print("Setting up reliable email delivery using Gmail SMTP...")
    
    solution = GmailBackupSolution()
    print("\n📧 This solution requires a Gmail App Password")
    print("Visit: https://support.google.com/accounts/answer/185833")
    print("Or run: python gmail_backup_solution.py (interactive setup)")
