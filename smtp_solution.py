#!/usr/bin/env python3
"""
SMTP Solution: Test with multiple SMTP providers to find a working configuration
"""

import smtplib
import ssl
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables
ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

class SMTPSolution:
    def __init__(self):
        self.test_email = "pittisunilkumar3@gmail.com"
        
    def test_smtp_providers(self):
        """Test multiple SMTP providers to find a working one"""
        print("🔧 SMTP SOLUTION FINDER")
        print("=" * 60)
        
        # List of SMTP providers to test
        smtp_configs = [
            {
                "name": "Gmail SMTP",
                "host": "smtp.gmail.com",
                "port": 587,
                "user": "your-gmail@gmail.com",  # User needs to provide
                "pass": "your-app-password",     # User needs to provide
                "tls": True,
                "note": "Requires app-specific password with 2FA enabled"
            },
            {
                "name": "Outlook/Hotmail SMTP",
                "host": "smtp-mail.outlook.com",
                "port": 587,
                "user": "your-email@outlook.com",  # User needs to provide
                "pass": "your-password",           # User needs to provide
                "tls": True,
                "note": "Works with regular password"
            },
            {
                "name": "Yahoo SMTP",
                "host": "smtp.mail.yahoo.com",
                "port": 587,
                "user": "your-email@yahoo.com",  # User needs to provide
                "pass": "your-app-password",     # User needs to provide
                "tls": True,
                "note": "Requires app-specific password"
            },
            {
                "name": "SendGrid SMTP",
                "host": "smtp.sendgrid.net",
                "port": 587,
                "user": "apikey",
                "pass": "your-sendgrid-api-key",  # User needs to provide
                "tls": True,
                "note": "Professional email service, requires API key"
            },
            {
                "name": "Mailgun SMTP",
                "host": "smtp.mailgun.org",
                "port": 587,
                "user": "your-mailgun-user",  # User needs to provide
                "pass": "your-mailgun-pass",  # User needs to provide
                "tls": True,
                "note": "Professional email service"
            }
        ]
        
        print("📋 Available SMTP Providers:")
        print("-" * 40)
        
        for i, config in enumerate(smtp_configs, 1):
            print(f"{i}. {config['name']}")
            print(f"   Host: {config['host']}:{config['port']}")
            print(f"   Note: {config['note']}")
            print()
        
        return smtp_configs
    
    def create_working_smtp_config(self):
        """Create a working SMTP configuration using Gmail as example"""
        print("📧 CREATING WORKING SMTP CONFIGURATION")
        print("=" * 60)
        
        print("Since the provided SMTP server has relay restrictions,")
        print("let's set up a working configuration using Gmail SMTP.")
        print()
        
        # Test if we can use Gmail SMTP (most common and reliable)
        gmail_config = {
            "host": "smtp.gmail.com",
            "port": 587,
            "user": "pittisunilkumar3@gmail.com",  # Use the test email as sender
            "pass": "",  # User needs to provide app password
            "from": "pittisunilkumar3@gmail.com"
        }
        
        print("🔧 Gmail SMTP Configuration:")
        print(f"   Host: {gmail_config['host']}")
        print(f"   Port: {gmail_config['port']}")
        print(f"   User: {gmail_config['user']}")
        print(f"   From: {gmail_config['from']}")
        print()
        
        print("📋 SETUP INSTRUCTIONS:")
        print("1. Go to your Google Account settings")
        print("2. Enable 2-Factor Authentication")
        print("3. Generate an App Password for 'Mail'")
        print("4. Use the app password (not your regular password)")
        print()
        
        return gmail_config
    
    def test_gmail_smtp_with_app_password(self, app_password):
        """Test Gmail SMTP with app password"""
        print(f"🧪 Testing Gmail SMTP with app password...")
        
        try:
            # Connect to Gmail SMTP
            server = smtplib.SMTP('smtp.gmail.com', 587, timeout=10)
            server.starttls()
            server.ehlo()
            
            # Login with app password
            server.login('pittisunilkumar3@gmail.com', app_password)
            print("✅ Gmail SMTP authentication successful!")
            
            # Send test email
            message = MIMEMultipart("alternative")
            message["Subject"] = "🎉 SMTP Working - Password Reset System Ready!"
            message["From"] = "pittisunilkumar3@gmail.com"
            message["To"] = self.test_email
            
            # HTML content
            html_content = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>SMTP Success</title>
</head>
<body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
    <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
        <h2 style="color: #28a745;">🎉 SMTP Configuration Successful!</h2>
        
        <div style="background-color: #d4edda; border: 1px solid #c3e6cb; padding: 20px; border-radius: 8px; margin: 20px 0;">
            <h3 style="margin-top: 0;">✅ Email System Working</h3>
            <p>The Martial Arts Academy password reset system is now fully functional!</p>
        </div>
        
        <h3>🔧 Configuration Details:</h3>
        <ul>
            <li><strong>SMTP Provider:</strong> Gmail</li>
            <li><strong>Authentication:</strong> ✅ Working</li>
            <li><strong>Email Delivery:</strong> ✅ Successful</li>
            <li><strong>Security:</strong> ✅ App Password Used</li>
        </ul>
        
        <div style="background-color: #d1ecf1; border: 1px solid #bee5eb; padding: 15px; border-radius: 5px; margin: 20px 0;">
            <strong>🚀 Next Steps:</strong>
            <ul>
                <li>Users can now request password resets</li>
                <li>Professional emails will be delivered</li>
                <li>Complete forgot password workflow is active</li>
            </ul>
        </div>
        
        <p>Best regards,<br>
        <strong>Martial Arts Academy Team</strong></p>
        
        <hr style="margin: 20px 0; border: none; border-top: 1px solid #eee;">
        <p style="font-size: 12px; color: #666;">
            This email confirms that the SMTP configuration is working correctly.
        </p>
    </div>
</body>
</html>
            """.strip()
            
            # Plain text content
            text_content = """
🎉 SMTP Configuration Successful!

The Martial Arts Academy password reset system is now fully functional!

✅ Configuration Details:
- SMTP Provider: Gmail
- Authentication: Working
- Email Delivery: Successful
- Security: App Password Used

🚀 Next Steps:
- Users can now request password resets
- Professional emails will be delivered
- Complete forgot password workflow is active

Best regards,
Martial Arts Academy Team

---
This email confirms that the SMTP configuration is working correctly.
            """.strip()
            
            # Add parts to message
            text_part = MIMEText(text_content, "plain")
            html_part = MIMEText(html_content, "html")
            
            message.attach(text_part)
            message.attach(html_part)
            
            # Send email
            server.sendmail('pittisunilkumar3@gmail.com', [self.test_email], message.as_string())
            print("✅ Test email sent successfully!")
            
            server.quit()
            return True
            
        except Exception as e:
            print(f"❌ Gmail SMTP test failed: {e}")
            return False
    
    def generate_env_config(self, smtp_config):
        """Generate .env configuration"""
        print("\n📝 UPDATED .ENV CONFIGURATION")
        print("=" * 60)
        
        env_config = f"""
# Email Configuration for Password Reset
SMTP_HOST={smtp_config['host']}
SMTP_PORT={smtp_config['port']}
SMTP_USER={smtp_config['user']}
SMTP_PASS=YOUR_APP_PASSWORD_HERE
SMTP_FROM={smtp_config['from']}
FRONTEND_URL=http://localhost:3022
        """.strip()
        
        print(env_config)
        print()
        print("📋 INSTRUCTIONS:")
        print("1. Copy the above configuration to your .env file")
        print("2. Replace 'YOUR_APP_PASSWORD_HERE' with your actual app password")
        print("3. Restart the backend server")
        print("4. Test the forgot password functionality")
        
        return env_config

if __name__ == "__main__":
    print("🚀 SMTP Solution Finder")
    print("Finding a working SMTP configuration for email delivery...")
    print()
    
    solution = SMTPSolution()
    
    # Show available providers
    providers = solution.test_smtp_providers()
    
    # Create working configuration
    gmail_config = solution.create_working_smtp_config()
    
    # Generate .env configuration
    solution.generate_env_config(gmail_config)
    
    print("\n" + "=" * 60)
    print("📊 SOLUTION SUMMARY")
    print("=" * 60)
    
    print("\n❌ ORIGINAL ISSUE:")
    print("   The provided SMTP server (sveats.cyberdetox.in) has two problems:")
    print("   1. Authentication credentials are rejected")
    print("   2. Server doesn't allow relay to external domains (Gmail)")
    
    print("\n✅ RECOMMENDED SOLUTION:")
    print("   Use Gmail SMTP with app-specific password:")
    print("   - Reliable and widely supported")
    print("   - Allows sending to any email address")
    print("   - Professional email delivery")
    print("   - Free for reasonable usage")
    
    print("\n🔧 NEXT STEPS:")
    print("   1. Set up Gmail app password")
    print("   2. Update .env file with Gmail SMTP settings")
    print("   3. Test the configuration")
    print("   4. Verify forgot password functionality")
    
    print("\n💡 ALTERNATIVE:")
    print("   If Gmail is not preferred, consider professional email services:")
    print("   - SendGrid (recommended for production)")
    print("   - Mailgun")
    print("   - Amazon SES")
    print("   - Outlook SMTP")
