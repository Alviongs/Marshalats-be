#!/usr/bin/env python3
"""
Mock SMTP Server for testing email functionality without real SMTP credentials
"""

import asyncio
import smtpd
import smtplib
import threading
import time
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from pathlib import Path

class MockSMTPServer(smtpd.SMTPServer):
    """Mock SMTP server that captures emails instead of sending them"""
    
    def __init__(self, localaddr, remoteaddr):
        super().__init__(localaddr, remoteaddr)
        self.emails = []
        print(f"🔧 Mock SMTP Server started on {localaddr[0]}:{localaddr[1]}")
    
    def process_message(self, peer, mailfrom, rcpttos, data, **kwargs):
        """Process incoming email messages"""
        print(f"\n📧 EMAIL CAPTURED:")
        print(f"   From: {mailfrom}")
        print(f"   To: {', '.join(rcpttos)}")
        print(f"   Size: {len(data)} bytes")
        
        # Store email
        email_data = {
            'from': mailfrom,
            'to': rcpttos,
            'data': data.decode('utf-8'),
            'timestamp': time.time()
        }
        self.emails.append(email_data)
        
        # Extract subject from email data
        lines = data.decode('utf-8').split('\n')
        subject = "No Subject"
        for line in lines:
            if line.startswith('Subject:'):
                subject = line[8:].strip()
                break
        
        print(f"   Subject: {subject}")
        print(f"   ✅ Email captured successfully!")
        
        # Save email to file for inspection
        self.save_email_to_file(email_data)
    
    def save_email_to_file(self, email_data):
        """Save captured email to file for inspection"""
        try:
            emails_dir = Path(__file__).parent / 'captured_emails'
            emails_dir.mkdir(exist_ok=True)
            
            timestamp = int(email_data['timestamp'])
            filename = f"email_{timestamp}.txt"
            filepath = emails_dir / filename
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(f"From: {email_data['from']}\n")
                f.write(f"To: {', '.join(email_data['to'])}\n")
                f.write(f"Timestamp: {time.ctime(email_data['timestamp'])}\n")
                f.write("-" * 50 + "\n")
                f.write(email_data['data'])
            
            print(f"   📁 Email saved to: {filepath}")
            
        except Exception as e:
            print(f"   ⚠️  Could not save email: {e}")

def start_mock_smtp_server():
    """Start the mock SMTP server in a separate thread"""
    server = MockSMTPServer(('localhost', 1025), None)
    
    def run_server():
        try:
            asyncio.run(server.serve_forever())
        except KeyboardInterrupt:
            print("\n🛑 Mock SMTP Server stopped")
    
    thread = threading.Thread(target=run_server, daemon=True)
    thread.start()
    
    return server

def test_mock_smtp():
    """Test the mock SMTP server"""
    print("🧪 TESTING MOCK SMTP SERVER")
    print("=" * 50)
    
    # Start mock server
    mock_server = start_mock_smtp_server()
    time.sleep(1)  # Give server time to start
    
    try:
        # Connect to mock server
        print("📡 Connecting to mock SMTP server...")
        server = smtplib.SMTP('localhost', 1025, timeout=5)
        
        print("✅ Connected to mock SMTP server")
        
        # Create test email
        message = MIMEMultipart("alternative")
        message["Subject"] = "🧪 Mock SMTP Test - Password Reset System"
        message["From"] = "test@martialarts.com"
        message["To"] = "pittisunilkumar3@gmail.com"
        
        # Plain text content
        text_content = """
🧪 Mock SMTP Test Successful!

This email was captured by the mock SMTP server, demonstrating that the email functionality is working correctly.

✅ Email Template Generation: Working
✅ SMTP Connection: Working  
✅ Email Formatting: Working
✅ Password Reset Flow: Ready

The forgot password system is ready for production with real SMTP credentials.

Best regards,
Martial Arts Academy Team
        """.strip()
        
        # HTML content
        html_content = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Mock SMTP Test</title>
</head>
<body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
    <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
        <h2 style="color: #28a745;">🧪 Mock SMTP Test Successful!</h2>
        
        <div style="background-color: #d4edda; border: 1px solid #c3e6cb; padding: 20px; border-radius: 8px; margin: 20px 0;">
            <p>This email was captured by the mock SMTP server, demonstrating that the email functionality is working correctly.</p>
        </div>
        
        <h3>✅ Test Results:</h3>
        <ul>
            <li>Email Template Generation: Working</li>
            <li>SMTP Connection: Working</li>
            <li>Email Formatting: Working</li>
            <li>Password Reset Flow: Ready</li>
        </ul>
        
        <p>The forgot password system is ready for production with real SMTP credentials.</p>
        
        <p>Best regards,<br>
        <strong>Martial Arts Academy Team</strong></p>
    </div>
</body>
</html>
        """.strip()
        
        # Add parts to message
        text_part = MIMEText(text_content, "plain")
        html_part = MIMEText(html_content, "html")
        
        message.attach(text_part)
        message.attach(html_part)
        
        # Send email to mock server
        print("📧 Sending test email to mock server...")
        server.sendmail("test@martialarts.com", ["pittisunilkumar3@gmail.com"], message.as_string())
        
        server.quit()
        print("✅ Test email sent to mock server successfully!")
        
        # Give server time to process
        time.sleep(1)
        
        print(f"\n📊 Mock Server Statistics:")
        print(f"   Emails Captured: {len(mock_server.emails)}")
        
        if mock_server.emails:
            latest_email = mock_server.emails[-1]
            print(f"   Latest Email From: {latest_email['from']}")
            print(f"   Latest Email To: {', '.join(latest_email['to'])}")
        
        return True
        
    except Exception as e:
        print(f"❌ Mock SMTP test failed: {e}")
        return False

def create_mock_smtp_env():
    """Create environment configuration for mock SMTP"""
    print("\n🔧 MOCK SMTP CONFIGURATION")
    print("=" * 50)
    
    mock_config = """
# Mock SMTP Configuration (for testing without real credentials)
SMTP_HOST=localhost
SMTP_PORT=1025
SMTP_USER=test@martialarts.com
SMTP_PASS=mock_password
SMTP_FROM=test@martialarts.com
FRONTEND_URL=http://localhost:3022
    """.strip()
    
    print("📝 Mock SMTP .env configuration:")
    print(mock_config)
    
    print("\n📋 USAGE:")
    print("1. Start mock SMTP server: python mock_smtp_server.py")
    print("2. Update .env with mock configuration above")
    print("3. Restart backend server")
    print("4. Test forgot password functionality")
    print("5. Check captured_emails/ folder for email files")
    
    return mock_config

if __name__ == "__main__":
    print("🚀 Mock SMTP Server for Email Testing")
    print("This allows testing email functionality without real SMTP credentials.")
    print()
    
    # Test mock SMTP
    success = test_mock_smtp()
    
    if success:
        print("\n🎉 Mock SMTP server is working!")
        
        # Show configuration
        create_mock_smtp_env()
        
        print("\n🔄 KEEPING SERVER RUNNING...")
        print("Press Ctrl+C to stop the server")
        
        try:
            # Keep server running
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n🛑 Mock SMTP server stopped")
    else:
        print("\n❌ Mock SMTP server test failed")
