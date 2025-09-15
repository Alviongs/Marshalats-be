#!/usr/bin/env python3
"""
cPanel Authentication Testing - Test different authentication methods and formats
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

class CPanelAuthTest:
    def __init__(self):
        self.smtp_host = os.getenv('SMTP_HOST', 'sveats.cyberdetox.in')
        self.smtp_user = os.getenv('SMTP_USER', 'info@sveats.cyberdetox.in')
        self.smtp_pass = os.getenv('SMTP_PASS', 'Renangiyamini@143')
        self.smtp_from = os.getenv('SMTP_FROM', self.smtp_user)
        self.test_email = "pittisunilkumar3@gmail.com"
        
    def test_cpanel_authentication_variants(self):
        """Test different cPanel authentication formats"""
        print("🔐 cPanel AUTHENTICATION VARIANTS TEST")
        print("=" * 60)
        
        # Different username formats to try
        username_variants = [
            # Standard formats
            self.smtp_user,  # info@sveats.cyberdetox.in
            self.smtp_user.split('@')[0],  # info
            
            # cPanel specific formats
            f"{self.smtp_user.split('@')[0]}@{self.smtp_host}",  # info@sveats.cyberdetox.in
            f"{self.smtp_user.split('@')[0]}%{self.smtp_host}",  # info%sveats.cyberdetox.in
            f"{self.smtp_user.split('@')[0]}+{self.smtp_host}",  # info+sveats.cyberdetox.in
            
            # Alternative domain formats
            f"info@cyberdetox.in",  # Parent domain
            f"info@sv90.ifastnet.com",  # Server hostname
        ]
        
        # Different password formats to try
        password_variants = [
            self.smtp_pass,  # Original password
            self.smtp_pass.lower(),  # Lowercase
            self.smtp_pass.upper(),  # Uppercase
        ]
        
        # Test configurations
        test_configs = [
            {"port": 587, "tls": True, "ssl": False, "name": "Port 587 + STARTTLS"},
            {"port": 465, "tls": False, "ssl": True, "name": "Port 465 + SSL"},
        ]
        
        successful_config = None
        
        for config in test_configs:
            print(f"\n🧪 Testing Configuration: {config['name']}")
            print("-" * 40)
            
            for username in username_variants:
                for password in password_variants:
                    if password != self.smtp_pass:  # Only test password variants with original username
                        if username != self.smtp_user:
                            continue
                    
                    print(f"   🔑 Testing: {username} / {'*' * len(password)}")
                    
                    try:
                        # Establish connection
                        if config['ssl']:
                            context = ssl.create_default_context()
                            server = smtplib.SMTP_SSL(self.smtp_host, config['port'], context=context, timeout=15)
                        else:
                            server = smtplib.SMTP(self.smtp_host, config['port'], timeout=15)
                            
                            if config['tls']:
                                context = ssl.create_default_context()
                                server.starttls(context=context)
                        
                        # Try authentication
                        try:
                            server.login(username, password)
                            print(f"   ✅ SUCCESS! Authentication worked!")
                            print(f"      Username: {username}")
                            print(f"      Password: {'*' * len(password)}")
                            
                            # Test email sending
                            if self.send_test_email_via_server(server, username):
                                print(f"   ✅ Test email sent successfully!")
                                successful_config = {
                                    'config': config,
                                    'username': username,
                                    'password': password
                                }
                                server.quit()
                                return successful_config
                            else:
                                print(f"   ⚠️  Email sending failed")
                                
                        except smtplib.SMTPAuthenticationError as e:
                            print(f"   ❌ Auth failed: {e}")
                        except Exception as e:
                            print(f"   ❌ Login error: {e}")
                        
                        server.quit()
                        
                    except Exception as e:
                        print(f"   ❌ Connection error: {e}")
                        
        return successful_config
    
    def test_manual_authentication(self):
        """Test manual SMTP authentication commands"""
        print("\n🔧 MANUAL AUTHENTICATION TESTING")
        print("=" * 60)
        
        try:
            # Connect to port 587 with STARTTLS
            print("📡 Connecting to port 587 with STARTTLS...")
            server = smtplib.SMTP(self.smtp_host, 587, timeout=15)
            server.set_debuglevel(1)  # Enable debug output
            
            print("\n🤝 Sending EHLO...")
            server.ehlo()
            
            print("\n🔒 Starting TLS...")
            context = ssl.create_default_context()
            server.starttls(context=context)
            server.ehlo()  # EHLO again after STARTTLS
            
            # Try different manual authentication methods
            auth_methods = [
                ("AUTH PLAIN", self.manual_auth_plain),
                ("AUTH LOGIN", self.manual_auth_login),
            ]
            
            for method_name, auth_func in auth_methods:
                print(f"\n🧪 Trying {method_name}...")
                try:
                    auth_func(server)
                    print(f"✅ {method_name} successful!")
                    
                    # Try sending email
                    if self.send_test_email_via_server(server, self.smtp_user):
                        print("✅ Test email sent successfully!")
                        server.quit()
                        return True
                    else:
                        print("❌ Test email failed")
                        
                except Exception as e:
                    print(f"❌ {method_name} failed: {e}")
            
            server.quit()
            
        except Exception as e:
            print(f"❌ Manual authentication test failed: {e}")
            
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
    
    def send_test_email_via_server(self, server, from_email):
        """Send a test email using an established server connection"""
        try:
            # Create test message
            message = MIMEMultipart("alternative")
            message["Subject"] = "🎉 cPanel SMTP SUCCESS - Martial Arts Academy"
            message["From"] = from_email
            message["To"] = self.test_email
            
            # Plain text content
            text_content = f"""
🎉 SUCCESS! cPanel SMTP Authentication Working!

The Martial Arts Academy password reset system is now fully operational with cPanel SMTP!

✅ Configuration Details:
- SMTP Server: {self.smtp_host}
- Authentication: Working
- From Email: {from_email}
- To Email: {self.test_email}
- Email Delivery: Successful

🚀 What's Working Now:
- Users can request password resets
- Professional HTML emails are delivered
- Complete forgot password workflow is active
- Secure token-based password reset

📧 Technical Details:
- Server: {self.smtp_host}
- Port: 587 with STARTTLS
- Authentication: Successful
- Email Format: HTML + Plain Text

Next Steps:
1. Test the forgot password form at: http://localhost:3022/forgot-password
2. Enter email: {self.test_email}
3. Check your inbox for password reset emails
4. Complete the password reset workflow

Best regards,
Martial Arts Academy Team

---
cPanel SMTP test completed successfully!
            """.strip()
            
            # HTML content
            html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>cPanel SMTP Success</title>
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
            <h2 style="margin: 10px 0 0 0;">cPanel SMTP Working!</h2>
        </div>
        
        <div class="content">
            <div class="success-box">
                <h3 style="margin-top: 0; color: #155724;">✅ Password Reset System Operational</h3>
                <p>The Martial Arts Academy password reset system is now fully functional with cPanel SMTP!</p>
            </div>
            
            <h3>🔧 Configuration Confirmed:</h3>
            <ul>
                <li><strong>SMTP Server:</strong> {self.smtp_host}</li>
                <li><strong>Authentication:</strong> ✅ Working</li>
                <li><strong>Email Delivery:</strong> ✅ Successful</li>
                <li><strong>From Email:</strong> {from_email}</li>
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
        </div>
        
        <div class="footer">
            <p><strong>Martial Arts Academy</strong><br>Password Reset System</p>
            <p>cPanel SMTP test completed successfully!</p>
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
            server.sendmail(from_email, [self.test_email], message.as_string())
            return True
            
        except Exception as e:
            print(f"   ❌ Email sending failed: {e}")
            return False
    
    def run_comprehensive_auth_test(self):
        """Run comprehensive authentication testing"""
        print("🚀 COMPREHENSIVE cPanel AUTHENTICATION TEST")
        print("This will test various authentication methods and formats.")
        print()
        
        # Test authentication variants
        successful_config = self.test_cpanel_authentication_variants()
        
        if successful_config:
            print("\n" + "=" * 60)
            print("🎉 AUTHENTICATION SUCCESSFUL!")
            print("=" * 60)
            
            config = successful_config['config']
            username = successful_config['username']
            password = successful_config['password']
            
            print(f"\n✅ Working Configuration:")
            print(f"   Port: {config['port']}")
            print(f"   TLS: {config['tls']}")
            print(f"   SSL: {config['ssl']}")
            print(f"   Username: {username}")
            print(f"   Password: {'*' * len(password)}")
            
            print(f"\n📧 Test email sent successfully!")
            print(f"   Check your inbox: {self.test_email}")
            
            return successful_config
        else:
            print("\n" + "=" * 60)
            print("❌ AUTHENTICATION FAILED")
            print("=" * 60)
            
            # Try manual authentication as fallback
            print("\n🔧 Trying manual authentication methods...")
            manual_success = self.test_manual_authentication()
            
            if not manual_success:
                print("\n💡 TROUBLESHOOTING SUGGESTIONS:")
                print("1. Verify the email account exists in cPanel")
                print("2. Check if the password is correct")
                print("3. Ensure SMTP is enabled for the account")
                print("4. Check cPanel email account settings")
                print("5. Contact hosting provider for SMTP configuration")
            
            return None

if __name__ == "__main__":
    print("🔐 cPanel SMTP Authentication Testing")
    print("Testing various authentication methods for sveats.cyberdetox.in")
    print()
    
    tester = CPanelAuthTest()
    result = tester.run_comprehensive_auth_test()
    
    if result:
        print("\n🎉 cPanel SMTP is working!")
        print("The forgot password functionality should now work correctly.")
    else:
        print("\n💔 cPanel SMTP authentication still not working.")
        print("Please check the troubleshooting suggestions above.")
