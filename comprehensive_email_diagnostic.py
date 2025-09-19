#!/usr/bin/env python3
"""
Comprehensive Email Diagnostic Tool
Diagnoses email delivery issues and provides solutions
"""

import smtplib
import ssl
import os
import asyncio
import sys
import time
import socket
import requests
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv
from pathlib import Path

# Add current directory to path
sys.path.append('.')

class EmailDiagnostic:
    def __init__(self):
        self.load_config()
        self.issues_found = []
        self.recommendations = []
        
    def load_config(self):
        """Load configuration from .env file"""
        load_dotenv()
        self.smtp_host = os.getenv('SMTP_HOST', 'sveats.cyberdetox.in')
        self.smtp_port = int(os.getenv('SMTP_PORT', '587'))
        self.smtp_user = os.getenv('SMTP_USER', 'info@sveats.cyberdetox.in')
        self.smtp_pass = os.getenv('SMTP_PASS', 'Neelarani@10')
        self.smtp_from = os.getenv('SMTP_FROM', 'info@sveats.cyberdetox.in')
        self.test_email = 'pittisunilkumar3@gmail.com'
        
    def print_header(self, title):
        """Print a formatted header"""
        print(f"\n{'='*60}")
        print(f"🔍 {title}")
        print(f"{'='*60}")
        
    def print_section(self, title):
        """Print a formatted section"""
        print(f"\n📋 {title}")
        print("-" * 40)
        
    def test_dns_resolution(self):
        """Test DNS resolution for SMTP server"""
        self.print_section("DNS Resolution Test")
        
        try:
            # Test A record
            result = socket.gethostbyname(self.smtp_host)
            print(f"✅ DNS Resolution: {self.smtp_host} → {result}")
                
        except Exception as e:
            print(f"❌ DNS Resolution failed: {e}")
            self.issues_found.append("DNS resolution failed")
            
    def test_network_connectivity(self):
        """Test network connectivity to SMTP server"""
        self.print_section("Network Connectivity Test")
        
        ports_to_test = [25, 465, 587, 2525]
        
        for port in ports_to_test:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(5)
                result = sock.connect_ex((self.smtp_host, port))
                sock.close()
                
                if result == 0:
                    status = "✅ Open"
                    if port == self.smtp_port:
                        status += " (CONFIGURED)"
                else:
                    status = "❌ Closed"
                    
                print(f"   Port {port}: {status}")
                
            except Exception as e:
                print(f"   Port {port}: ❌ Error - {e}")
                
    def test_smtp_connection(self):
        """Test SMTP connection and authentication"""
        self.print_section("SMTP Connection Test")
        
        try:
            print(f"🔌 Connecting to {self.smtp_host}:{self.smtp_port}...")
            server = smtplib.SMTP(self.smtp_host, self.smtp_port, timeout=10)
            print("✅ Connection established")
            
            # Get server info
            print(f"📋 Server greeting: {server.getwelcome()}")
            
            # Test STARTTLS
            if self.smtp_port == 587:
                print("🔒 Starting TLS...")
                context = ssl.create_default_context()
                server.starttls(context=context)
                print("✅ TLS started successfully")
                
            # Test authentication
            print("🔑 Testing authentication...")
            server.login(self.smtp_user, self.smtp_pass)
            print("✅ Authentication successful")
            
            # Get server capabilities
            print("📋 Server capabilities:")
            for feature, params in server.esmtp_features.items():
                print(f"   - {feature}: {params}")
                
            server.quit()
            print("✅ SMTP connection test passed")
            
        except smtplib.SMTPAuthenticationError as e:
            print(f"❌ Authentication failed: {e}")
            self.issues_found.append("SMTP authentication failed")
            self.recommendations.append("Check SMTP username and password")
            
        except Exception as e:
            print(f"❌ SMTP connection failed: {e}")
            self.issues_found.append(f"SMTP connection failed: {e}")
            
    def send_test_email(self):
        """Send a test email"""
        self.print_section("Test Email Sending")
        
        try:
            # Create test message
            message = MIMEMultipart("alternative")
            message["Subject"] = "🧪 Email Diagnostic Test - " + time.strftime("%Y-%m-%d %H:%M:%S")
            message["From"] = self.smtp_from
            message["To"] = self.test_email
            
            # Plain text content
            text_content = f"""
Email Diagnostic Test

This is a test email sent from the Martial Arts Academy system.

Test Details:
- SMTP Server: {self.smtp_host}:{self.smtp_port}
- From: {self.smtp_from}
- To: {self.test_email}
- Time: {time.strftime("%Y-%m-%d %H:%M:%S")}

If you receive this email, the SMTP configuration is working correctly.

Best regards,
Email Diagnostic System
            """.strip()
            
            # HTML content
            html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Email Diagnostic Test</title>
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
        .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; text-align: center; border-radius: 8px 8px 0 0; }}
        .content {{ background: #f8f9fa; padding: 20px; border: 1px solid #e9ecef; }}
        .footer {{ background: #6c757d; color: white; padding: 15px; text-align: center; border-radius: 0 0 8px 8px; }}
        .success {{ background: #d4edda; border: 1px solid #c3e6cb; padding: 15px; border-radius: 5px; margin: 20px 0; }}
        .info {{ background: #d1ecf1; border: 1px solid #bee5eb; padding: 15px; border-radius: 5px; margin: 20px 0; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🧪 Email Diagnostic Test</h1>
            <p>Martial Arts Academy System</p>
        </div>
        
        <div class="content">
            <div class="success">
                <strong>✅ Success!</strong> This email was sent successfully from the system.
            </div>
            
            <h3>Test Details:</h3>
            <ul>
                <li><strong>SMTP Server:</strong> {self.smtp_host}:{self.smtp_port}</li>
                <li><strong>From:</strong> {self.smtp_from}</li>
                <li><strong>To:</strong> {self.test_email}</li>
                <li><strong>Time:</strong> {time.strftime("%Y-%m-%d %H:%M:%S")}</li>
            </ul>
            
            <div class="info">
                <strong>📧 Email Configuration Status:</strong><br>
                If you receive this email, the SMTP configuration is working correctly and emails should be delivered successfully.
            </div>
        </div>
        
        <div class="footer">
            <p>Email Diagnostic System<br>
            Martial Arts Academy</p>
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
            print(f"📧 Sending test email to {self.test_email}...")
            
            context = ssl.create_default_context()
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                if self.smtp_port == 587:
                    server.starttls(context=context)
                server.login(self.smtp_user, self.smtp_pass)
                server.sendmail(self.smtp_from, self.test_email, message.as_string())
                
            print("✅ Test email sent successfully!")
            print(f"📬 Check your inbox at {self.test_email}")
            
        except Exception as e:
            print(f"❌ Failed to send test email: {e}")
            self.issues_found.append(f"Test email sending failed: {e}")
            
    async def test_application_email_service(self):
        """Test the application's email service"""
        self.print_section("Application Email Service Test")
        
        try:
            from utils.email_service import send_password_reset_email
            
            print("🧪 Testing application email service...")
            result = await send_password_reset_email(
                to_email=self.test_email,
                reset_token="diagnostic_test_token_123",
                user_name="Diagnostic Test User"
            )
            
            if result:
                print("✅ Application email service working correctly")
            else:
                print("❌ Application email service failed")
                self.issues_found.append("Application email service failed")
                
        except Exception as e:
            print(f"❌ Application email service error: {e}")
            self.issues_found.append(f"Application email service error: {e}")
            
    def test_api_endpoint(self):
        """Test the forgot password API endpoint"""
        self.print_section("API Endpoint Test")
        
        try:
            url = 'http://localhost:8003/auth/forgot-password'
            data = {'email': self.test_email}
            
            print(f"🌐 Testing API endpoint: {url}")
            response = requests.post(url, json=data, timeout=10)
            
            print(f"📊 Response Status: {response.status_code}")
            
            if response.status_code == 200:
                response_data = response.json()
                email_sent = response_data.get('email_sent', False)
                
                if email_sent:
                    print("✅ API endpoint working correctly")
                    print(f"📧 Email sent status: {email_sent}")
                else:
                    print("⚠️  API responded but email_sent is False")
                    self.issues_found.append("API reports email not sent")
            else:
                print(f"❌ API endpoint failed with status {response.status_code}")
                self.issues_found.append(f"API endpoint failed: {response.status_code}")
                
        except requests.exceptions.ConnectionError:
            print("❌ Cannot connect to API server")
            self.issues_found.append("API server not running")
            self.recommendations.append("Start the backend server with: python server.py")
            
        except Exception as e:
            print(f"❌ API test failed: {e}")
            self.issues_found.append(f"API test failed: {e}")

    def check_email_deliverability_factors(self):
        """Check factors that might affect email deliverability"""
        self.print_section("Email Deliverability Analysis")

        print("📋 Checking factors that might affect email delivery:")

        # Check sender reputation
        print(f"📧 Sender domain: {self.smtp_from.split('@')[1]}")
        print(f"📧 SMTP server: {self.smtp_host}")

        # Common deliverability issues
        deliverability_tips = [
            "✉️  Check spam/junk folder in your email client",
            "🔍 Search for emails from 'info@sveats.cyberdetox.in'",
            "📱 Check if your email provider blocks emails from unknown domains",
            "⚡ Gmail/Outlook may delay emails from new senders",
            "🛡️  Some corporate firewalls block emails from certain domains",
            "📬 Check if your email quota is full",
            "🔄 Try requesting password reset multiple times (with delays)",
            "📧 Try with a different email address (Gmail, Yahoo, etc.)"
        ]

        for tip in deliverability_tips:
            print(f"   {tip}")

    def generate_report(self):
        """Generate final diagnostic report"""
        self.print_header("DIAGNOSTIC REPORT")

        if not self.issues_found:
            print("🎉 NO TECHNICAL ISSUES FOUND!")
            print("\n✅ All technical components are working correctly:")
            print("   - SMTP server connection: Working")
            print("   - Authentication: Successful")
            print("   - Email sending: Functional")
            print("   - API endpoint: Responsive")
            print("   - Application service: Operational")

            print("\n💡 LIKELY CAUSES FOR NOT RECEIVING EMAILS:")
            print("   1. 📧 Emails are going to spam/junk folder")
            print("   2. 🔍 Email provider is filtering/blocking the sender")
            print("   3. ⏰ Email delivery is delayed (can take minutes)")
            print("   4. 📱 Mobile email apps may not sync immediately")
            print("   5. 🛡️  Corporate/ISP firewall blocking emails")

        else:
            print("❌ ISSUES FOUND:")
            for i, issue in enumerate(self.issues_found, 1):
                print(f"   {i}. {issue}")

        if self.recommendations:
            print("\n🔧 RECOMMENDATIONS:")
            for i, rec in enumerate(self.recommendations, 1):
                print(f"   {i}. {rec}")

        print("\n📋 NEXT STEPS:")
        print("   1. Check spam/junk folder thoroughly")
        print("   2. Search for 'Martial Arts Academy' or 'info@sveats.cyberdetox.in'")
        print("   3. Try with a different email provider (Gmail, Yahoo)")
        print("   4. Wait 5-10 minutes and check again")
        print("   5. Contact your email provider if issues persist")

    async def run_full_diagnostic(self):
        """Run complete diagnostic suite"""
        self.print_header("EMAIL SYSTEM COMPREHENSIVE DIAGNOSTIC")

        print("🚀 Starting comprehensive email diagnostic...")
        print(f"📧 Test email address: {self.test_email}")
        print(f"🔧 SMTP configuration: {self.smtp_host}:{self.smtp_port}")

        # Run all tests
        self.test_dns_resolution()
        self.test_network_connectivity()
        self.test_smtp_connection()
        self.send_test_email()
        await self.test_application_email_service()
        self.test_api_endpoint()
        self.check_email_deliverability_factors()

        # Generate final report
        self.generate_report()

if __name__ == "__main__":
    diagnostic = EmailDiagnostic()
    asyncio.run(diagnostic.run_full_diagnostic())
