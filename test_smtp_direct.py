#!/usr/bin/env python3
"""
Direct SMTP test to verify credentials and connection
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

def test_smtp_connection():
    """Test SMTP connection and authentication"""
    
    # Get SMTP settings
    smtp_host = os.getenv('SMTP_HOST', 'sveats.cyberdetox.in')
    smtp_port = int(os.getenv('SMTP_PORT', '465'))
    smtp_user = os.getenv('SMTP_USER', 'info@sveats.cyberdetox.in')
    smtp_pass = os.getenv('SMTP_PASS', 'Renangiyamini@143')
    smtp_from = os.getenv('SMTP_FROM', smtp_user)
    
    print(f"🔧 Testing SMTP Connection")
    print(f"Host: {smtp_host}")
    print(f"Port: {smtp_port}")
    print(f"User: {smtp_user}")
    print(f"From: {smtp_from}")
    print(f"Has Password: {bool(smtp_pass)}")
    print()
    
    try:
        print("📡 Attempting SMTP connection...")
        
        # Create SSL context
        context = ssl.create_default_context()
        
        if smtp_port == 465:
            print("🔒 Using SMTP_SSL for port 465...")
            server = smtplib.SMTP_SSL(smtp_host, smtp_port, context=context)
        else:
            print("🔒 Using SMTP with STARTTLS...")
            server = smtplib.SMTP(smtp_host, smtp_port)
            server.starttls(context=context)
        
        print("✅ Connection established")
        
        print("🔑 Attempting authentication...")
        server.login(smtp_user, smtp_pass)
        print("✅ Authentication successful!")
        
        # Create a test email
        test_email = "pittisunilkumar3@gmail.com"
        
        print(f"📧 Sending test email to {test_email}...")
        
        message = MIMEMultipart("alternative")
        message["Subject"] = "SMTP Test - Martial Arts Academy"
        message["From"] = smtp_from
        message["To"] = test_email
        
        # Plain text content
        text_content = """
Hello,

This is a test email to verify SMTP functionality for the Martial Arts Academy password reset system.

If you receive this email, the SMTP configuration is working correctly!

Best regards,
Martial Arts Academy Team
        """.strip()
        
        # HTML content
        html_content = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>SMTP Test</title>
</head>
<body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
    <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
        <h2 style="color: #333;">🥋 SMTP Test - Martial Arts Academy</h2>
        
        <p>Hello,</p>
        
        <p>This is a test email to verify SMTP functionality for the Martial Arts Academy password reset system.</p>
        
        <div style="background-color: #d4edda; border: 1px solid #c3e6cb; padding: 15px; border-radius: 5px; margin: 20px 0;">
            <strong>✅ Success!</strong> If you receive this email, the SMTP configuration is working correctly!
        </div>
        
        <p>Best regards,<br>
        Martial Arts Academy Team</p>
        
        <hr style="margin: 20px 0; border: none; border-top: 1px solid #eee;">
        <p style="font-size: 12px; color: #666;">
            This is an automated test message. Please do not reply to this email.
        </p>
    </div>
</body>
</html>
        """.strip()
        
        # Add text and HTML parts
        text_part = MIMEText(text_content, "plain")
        html_part = MIMEText(html_content, "html")
        
        message.attach(text_part)
        message.attach(html_part)
        
        # Send the email
        server.sendmail(smtp_from, test_email, message.as_string())
        print("✅ Test email sent successfully!")
        
        server.quit()
        print("✅ SMTP connection closed")
        
        return True
        
    except smtplib.SMTPAuthenticationError as e:
        print(f"❌ SMTP Authentication Error: {e}")
        print("   This usually means:")
        print("   - Incorrect username or password")
        print("   - Account may require app-specific password")
        print("   - Two-factor authentication may be enabled")
        return False
        
    except smtplib.SMTPConnectError as e:
        print(f"❌ SMTP Connection Error: {e}")
        print("   This usually means:")
        print("   - Incorrect host or port")
        print("   - Firewall blocking connection")
        print("   - Server may be down")
        return False
        
    except smtplib.SMTPException as e:
        print(f"❌ SMTP Error: {e}")
        return False
        
    except Exception as e:
        print(f"❌ Unexpected Error: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Starting Direct SMTP Test")
    print("=" * 50)
    
    success = test_smtp_connection()
    
    print()
    print("=" * 50)
    if success:
        print("🎉 SMTP test completed successfully!")
        print("The email service should now work properly.")
    else:
        print("💥 SMTP test failed!")
        print("Please check the SMTP credentials and server settings.")
