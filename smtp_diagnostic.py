#!/usr/bin/env python3
"""
Comprehensive SMTP diagnostic tool to investigate email delivery issues
"""

import smtplib
import ssl
import socket
import os
import dns.resolver
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv
from pathlib import Path
import base64

# Load environment variables
ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

class SMTPDiagnostic:
    def __init__(self):
        self.smtp_host = os.getenv('SMTP_HOST', 'sveats.cyberdetox.in')
        self.smtp_user = os.getenv('SMTP_USER', 'info@sveats.cyberdetox.in')
        self.smtp_pass = os.getenv('SMTP_PASS', 'Renangiyamini@143')
        self.smtp_from = os.getenv('SMTP_FROM', self.smtp_user)
        self.test_email = "pittisunilkumar3@gmail.com"
        
    def run_full_diagnostic(self):
        """Run comprehensive SMTP diagnostic"""
        print("🔍 COMPREHENSIVE SMTP DIAGNOSTIC")
        print("=" * 60)
        
        print(f"📧 Target SMTP Server: {self.smtp_host}")
        print(f"👤 Username: {self.smtp_user}")
        print(f"📨 From Address: {self.smtp_from}")
        print(f"🎯 Test Email: {self.test_email}")
        print()
        
        # Step 1: DNS and Network Tests
        self.test_dns_resolution()
        self.test_network_connectivity()
        
        # Step 2: SMTP Server Discovery
        self.discover_smtp_capabilities()
        
        # Step 3: Authentication Tests
        self.test_authentication_methods()
        
        # Step 4: Email Sending Tests
        self.test_email_sending()
        
        print("\n" + "=" * 60)
        print("📊 DIAGNOSTIC SUMMARY")
        print("=" * 60)
        
    def test_dns_resolution(self):
        """Test DNS resolution for the SMTP server"""
        print("🌐 STEP 1: DNS Resolution Test")
        print("-" * 40)
        
        try:
            # Test A record
            result = socket.gethostbyname(self.smtp_host)
            print(f"✅ DNS A Record: {self.smtp_host} → {result}")
            
            # Test MX record
            try:
                mx_records = dns.resolver.resolve(self.smtp_host.split('@')[-1] if '@' in self.smtp_host else self.smtp_host, 'MX')
                print(f"✅ MX Records found:")
                for mx in mx_records:
                    print(f"   Priority {mx.preference}: {mx.exchange}")
            except:
                print("⚠️  No MX records found (not necessarily an issue for direct SMTP)")
                
        except Exception as e:
            print(f"❌ DNS Resolution failed: {e}")
            
        print()
    
    def test_network_connectivity(self):
        """Test network connectivity to SMTP ports"""
        print("🔌 STEP 2: Network Connectivity Test")
        print("-" * 40)
        
        ports_to_test = [25, 465, 587, 2525]
        
        for port in ports_to_test:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(5)
                result = sock.connect_ex((self.smtp_host, port))
                sock.close()
                
                if result == 0:
                    print(f"✅ Port {port}: Open")
                else:
                    print(f"❌ Port {port}: Closed/Filtered")
                    
            except Exception as e:
                print(f"❌ Port {port}: Error - {e}")
                
        print()
    
    def discover_smtp_capabilities(self):
        """Discover SMTP server capabilities"""
        print("🔍 STEP 3: SMTP Server Capabilities")
        print("-" * 40)
        
        ports_to_test = [587, 465, 25]
        
        for port in ports_to_test:
            print(f"\n📡 Testing port {port}:")
            try:
                if port == 465:
                    # SSL connection
                    context = ssl.create_default_context()
                    server = smtplib.SMTP_SSL(self.smtp_host, port, context=context, timeout=10)
                    print(f"   ✅ SSL connection established")
                else:
                    # Regular connection
                    server = smtplib.SMTP(self.smtp_host, port, timeout=10)
                    print(f"   ✅ Connection established")
                    
                    if port == 587:
                        # Try STARTTLS
                        try:
                            context = ssl.create_default_context()
                            server.starttls(context=context)
                            print(f"   ✅ STARTTLS successful")
                        except Exception as e:
                            print(f"   ❌ STARTTLS failed: {e}")
                
                # Get server capabilities
                try:
                    server.ehlo()
                    print(f"   ✅ EHLO successful")
                    
                    # Check supported features
                    if server.has_extn('AUTH'):
                        auth_methods = server.esmtp_features.get('auth', '').split()
                        print(f"   🔐 AUTH methods: {' '.join(auth_methods)}")
                    else:
                        print(f"   ⚠️  No AUTH extension found")
                        
                    if server.has_extn('STARTTLS'):
                        print(f"   🔒 STARTTLS supported")
                        
                except Exception as e:
                    print(f"   ❌ EHLO failed: {e}")
                
                server.quit()
                
            except Exception as e:
                print(f"   ❌ Connection failed: {e}")
                
        print()
    
    def test_authentication_methods(self):
        """Test different authentication methods"""
        print("🔐 STEP 4: Authentication Tests")
        print("-" * 40)
        
        test_configs = [
            {"port": 587, "tls": True, "ssl": False, "name": "Port 587 + STARTTLS"},
            {"port": 465, "tls": False, "ssl": True, "name": "Port 465 + SSL"},
            {"port": 25, "tls": False, "ssl": False, "name": "Port 25 (Plain)"},
        ]
        
        for config in test_configs:
            print(f"\n🧪 Testing: {config['name']}")
            try:
                # Establish connection
                if config['ssl']:
                    context = ssl.create_default_context()
                    server = smtplib.SMTP_SSL(self.smtp_host, config['port'], context=context, timeout=10)
                else:
                    server = smtplib.SMTP(self.smtp_host, config['port'], timeout=10)
                    
                    if config['tls']:
                        context = ssl.create_default_context()
                        server.starttls(context=context)
                
                print(f"   ✅ Connection established")
                
                # Try authentication
                try:
                    server.login(self.smtp_user, self.smtp_pass)
                    print(f"   ✅ Authentication successful!")
                    
                    # If auth successful, try sending a test email
                    success = self.send_test_email_via_server(server)
                    if success:
                        print(f"   ✅ Test email sent successfully!")
                        return True
                    else:
                        print(f"   ❌ Test email failed to send")
                        
                except smtplib.SMTPAuthenticationError as e:
                    print(f"   ❌ Authentication failed: {e}")
                except Exception as e:
                    print(f"   ❌ Login error: {e}")
                
                server.quit()
                
            except Exception as e:
                print(f"   ❌ Connection error: {e}")
                
        return False
    
    def send_test_email_via_server(self, server):
        """Send a test email using an established server connection"""
        try:
            # Create test message
            message = MIMEMultipart("alternative")
            message["Subject"] = "🧪 SMTP Test - Martial Arts Academy"
            message["From"] = self.smtp_from
            message["To"] = self.test_email
            
            # Plain text content
            text_content = f"""
Hello,

This is a successful SMTP test email from the Martial Arts Academy system!

✅ SMTP Server: {self.smtp_host}
✅ Authentication: Working
✅ Email Delivery: Successful

If you receive this email, the forgot password functionality should now work correctly.

Best regards,
Martial Arts Academy Team

---
Test timestamp: {__import__('datetime').datetime.now()}
            """.strip()
            
            # HTML content
            html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>SMTP Test Success</title>
</head>
<body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
    <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
        <h2 style="color: #28a745;">🎉 SMTP Test Successful!</h2>
        
        <div style="background-color: #d4edda; border: 1px solid #c3e6cb; padding: 20px; border-radius: 8px; margin: 20px 0;">
            <h3 style="margin-top: 0;">✅ Email Delivery Working</h3>
            <p>This test email confirms that the SMTP configuration is working correctly for the Martial Arts Academy password reset system.</p>
        </div>
        
        <h3>📊 Test Details:</h3>
        <ul>
            <li><strong>SMTP Server:</strong> {self.smtp_host}</li>
            <li><strong>Authentication:</strong> ✅ Working</li>
            <li><strong>Email Delivery:</strong> ✅ Successful</li>
            <li><strong>Test Email:</strong> {self.test_email}</li>
        </ul>
        
        <div style="background-color: #fff3cd; border: 1px solid #ffeaa7; padding: 15px; border-radius: 5px; margin: 20px 0;">
            <strong>🔔 Next Steps:</strong> The forgot password functionality should now work correctly. Users can request password resets and receive professional email notifications.
        </div>
        
        <p>Best regards,<br>
        <strong>Martial Arts Academy Team</strong></p>
        
        <hr style="margin: 20px 0; border: none; border-top: 1px solid #eee;">
        <p style="font-size: 12px; color: #666;">
            Test timestamp: {__import__('datetime').datetime.now()}<br>
            This is an automated test message.
        </p>
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
            server.sendmail(self.smtp_from, self.test_email, message.as_string())
            return True
            
        except Exception as e:
            print(f"   ❌ Email sending failed: {e}")
            return False
    
    def test_email_sending(self):
        """Test email sending with various configurations"""
        print("📧 STEP 5: Email Sending Test")
        print("-" * 40)
        
        # This will be called from authentication tests
        print("Email sending tests integrated with authentication tests above.")
        print()

if __name__ == "__main__":
    print("🚀 Starting SMTP Diagnostic Tool")
    print("This will thoroughly test the SMTP configuration and attempt to send a test email.")
    print()
    
    diagnostic = SMTPDiagnostic()
    diagnostic.run_full_diagnostic()
