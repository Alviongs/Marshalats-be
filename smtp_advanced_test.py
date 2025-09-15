#!/usr/bin/env python3
"""
Advanced SMTP testing with different authentication methods and debugging
"""

import smtplib
import ssl
import os
import base64
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables
ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

class AdvancedSMTPTest:
    def __init__(self):
        self.smtp_host = os.getenv('SMTP_HOST', 'sveats.cyberdetox.in')
        self.smtp_user = os.getenv('SMTP_USER', 'info@sveats.cyberdetox.in')
        self.smtp_pass = os.getenv('SMTP_PASS', 'Renangiyamini@143')
        self.smtp_from = os.getenv('SMTP_FROM', self.smtp_user)
        self.test_email = "pittisunilkumar3@gmail.com"
        
    def test_manual_auth_commands(self):
        """Test manual authentication commands"""
        print("🔐 MANUAL AUTHENTICATION TEST")
        print("=" * 50)
        
        try:
            # Test with port 587 + STARTTLS
            print("📡 Connecting to port 587 with STARTTLS...")
            server = smtplib.SMTP(self.smtp_host, 587, timeout=15)
            server.set_debuglevel(1)  # Enable debug output
            
            print("\n🤝 Sending EHLO...")
            server.ehlo()
            
            print("\n🔒 Starting TLS...")
            context = ssl.create_default_context()
            server.starttls(context=context)
            server.ehlo()  # EHLO again after STARTTLS
            
            print(f"\n🔑 Attempting login with username: {self.smtp_user}")
            
            # Try different authentication methods
            auth_methods = [
                ("Standard LOGIN", lambda: server.login(self.smtp_user, self.smtp_pass)),
                ("Manual AUTH PLAIN", lambda: self.manual_auth_plain(server)),
                ("Manual AUTH LOGIN", lambda: self.manual_auth_login(server)),
            ]
            
            for method_name, auth_func in auth_methods:
                print(f"\n🧪 Trying {method_name}...")
                try:
                    auth_func()
                    print(f"✅ {method_name} successful!")
                    
                    # Try sending email
                    if self.send_test_email_via_server(server):
                        print("✅ Test email sent successfully!")
                        server.quit()
                        return True
                    else:
                        print("❌ Test email failed")
                        
                except Exception as e:
                    print(f"❌ {method_name} failed: {e}")
            
            server.quit()
            
        except Exception as e:
            print(f"❌ Connection error: {e}")
            
        return False
    
    def manual_auth_plain(self, server):
        """Manual AUTH PLAIN implementation"""
        # AUTH PLAIN format: \0username\0password
        auth_string = f"\0{self.smtp_user}\0{self.smtp_pass}"
        auth_bytes = auth_string.encode('utf-8')
        auth_b64 = base64.b64encode(auth_bytes).decode('ascii')
        
        # Send AUTH PLAIN command
        server.docmd("AUTH PLAIN", auth_b64)
    
    def manual_auth_login(self, server):
        """Manual AUTH LOGIN implementation"""
        # AUTH LOGIN is interactive
        server.docmd("AUTH LOGIN")
        
        # Send username
        username_b64 = base64.b64encode(self.smtp_user.encode('utf-8')).decode('ascii')
        server.docmd(username_b64)
        
        # Send password
        password_b64 = base64.b64encode(self.smtp_pass.encode('utf-8')).decode('ascii')
        server.docmd(password_b64)
    
    def test_alternative_credentials(self):
        """Test with alternative credential formats"""
        print("\n🔄 ALTERNATIVE CREDENTIAL FORMATS")
        print("=" * 50)
        
        # Test different username formats
        username_variants = [
            self.smtp_user,  # Original: info@sveats.cyberdetox.in
            self.smtp_user.split('@')[0],  # Just: info
            f"{self.smtp_user.split('@')[0]}@{self.smtp_host}",  # info@sveats.cyberdetox.in
        ]
        
        for username in username_variants:
            print(f"\n🧪 Testing username: {username}")
            try:
                server = smtplib.SMTP(self.smtp_host, 587, timeout=10)
                context = ssl.create_default_context()
                server.starttls(context=context)
                server.ehlo()
                
                server.login(username, self.smtp_pass)
                print(f"✅ Authentication successful with username: {username}")
                
                if self.send_test_email_via_server(server):
                    print("✅ Test email sent successfully!")
                    server.quit()
                    return True
                    
                server.quit()
                
            except Exception as e:
                print(f"❌ Failed with username {username}: {e}")
        
        return False
    
    def test_without_auth(self):
        """Test sending email without authentication (open relay)"""
        print("\n📮 TESTING WITHOUT AUTHENTICATION")
        print("=" * 50)
        
        try:
            server = smtplib.SMTP(self.smtp_host, 25, timeout=10)
            server.ehlo()
            
            print("🧪 Attempting to send email without authentication...")
            if self.send_test_email_via_server(server):
                print("✅ Email sent without authentication (open relay)!")
                server.quit()
                return True
            else:
                print("❌ Email sending failed without authentication")
                
            server.quit()
            
        except Exception as e:
            print(f"❌ Error testing without auth: {e}")
            
        return False
    
    def send_test_email_via_server(self, server):
        """Send a test email using an established server connection"""
        try:
            # Create simple test message
            message = MIMEText("🧪 SMTP Test - This email confirms SMTP is working!")
            message["Subject"] = "SMTP Test Success - Martial Arts Academy"
            message["From"] = self.smtp_from
            message["To"] = self.test_email
            
            # Send email
            server.sendmail(self.smtp_from, [self.test_email], message.as_string())
            return True
            
        except Exception as e:
            print(f"❌ Email sending failed: {e}")
            return False
    
    def test_server_info(self):
        """Get detailed server information"""
        print("\n📊 SERVER INFORMATION")
        print("=" * 50)
        
        try:
            server = smtplib.SMTP(self.smtp_host, 587, timeout=10)
            server.set_debuglevel(1)
            
            print("🔍 Server response to EHLO:")
            code, response = server.ehlo()
            print(f"Response code: {code}")
            print(f"Response: {response.decode('utf-8')}")
            
            print(f"\n🔧 ESMTP Features:")
            for feature, params in server.esmtp_features.items():
                print(f"  {feature}: {params}")
            
            server.quit()
            
        except Exception as e:
            print(f"❌ Error getting server info: {e}")
    
    def run_all_tests(self):
        """Run all advanced tests"""
        print("🚀 ADVANCED SMTP TESTING")
        print("=" * 60)
        
        # Get server information first
        self.test_server_info()
        
        # Test manual authentication
        if self.test_manual_auth_commands():
            return True
            
        # Test alternative credential formats
        if self.test_alternative_credentials():
            return True
            
        # Test without authentication
        if self.test_without_auth():
            return True
            
        print("\n💥 All authentication methods failed!")
        print("\n🔍 POSSIBLE ISSUES:")
        print("1. ❌ Incorrect username or password")
        print("2. 🔐 Account may require app-specific password")
        print("3. 🛡️  Two-factor authentication enabled")
        print("4. 🚫 SMTP access disabled for this account")
        print("5. 🌐 IP address may be blocked")
        print("6. ⏰ Account may be temporarily locked")
        
        return False

if __name__ == "__main__":
    print("🔬 Starting Advanced SMTP Testing")
    print("This will test various authentication methods and configurations.")
    print()
    
    tester = AdvancedSMTPTest()
    success = tester.run_all_tests()
    
    if success:
        print("\n🎉 SMTP configuration is working!")
        print("The forgot password functionality should now work correctly.")
    else:
        print("\n💔 SMTP configuration still not working.")
        print("Please check with the email provider for correct settings.")
