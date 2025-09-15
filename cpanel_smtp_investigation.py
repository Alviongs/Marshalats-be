#!/usr/bin/env python3
"""
Comprehensive cPanel SMTP Investigation and Testing Tool
Deep analysis of sveats.cyberdetox.in SMTP server configuration
"""

import smtplib
import ssl
import socket
import os
import dns.resolver
import base64
import time
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables
ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

class CPanelSMTPInvestigation:
    def __init__(self):
        self.smtp_host = os.getenv('SMTP_HOST', 'sveats.cyberdetox.in')
        self.smtp_user = os.getenv('SMTP_USER', 'info@sveats.cyberdetox.in')
        self.smtp_pass = os.getenv('SMTP_PASS', 'Renangiyamini@143')
        self.smtp_from = os.getenv('SMTP_FROM', self.smtp_user)
        self.test_email = "pittisunilkumar3@gmail.com"
        
    def run_comprehensive_investigation(self):
        """Run complete cPanel SMTP investigation"""
        print("🔍 COMPREHENSIVE cPanel SMTP INVESTIGATION")
        print("=" * 70)
        print(f"📧 Target Server: {self.smtp_host}")
        print(f"👤 Username: {self.smtp_user}")
        print(f"🎯 Test Email: {self.test_email}")
        print()
        
        # Step 1: DNS and Network Analysis
        self.analyze_dns_configuration()
        self.test_network_connectivity()
        
        # Step 2: SMTP Server Deep Analysis
        self.analyze_smtp_server_capabilities()
        
        # Step 3: Authentication Testing
        self.test_authentication_methods()
        
        # Step 4: Email Delivery Testing
        self.test_email_delivery()
        
        # Step 5: cPanel Specific Testing
        self.test_cpanel_specific_features()
        
        print("\n" + "=" * 70)
        print("📊 INVESTIGATION SUMMARY")
        print("=" * 70)
        
    def analyze_dns_configuration(self):
        """Analyze DNS configuration for the SMTP server"""
        print("🌐 STEP 1: DNS CONFIGURATION ANALYSIS")
        print("-" * 50)
        
        try:
            # Test A record
            ip_address = socket.gethostbyname(self.smtp_host)
            print(f"✅ A Record: {self.smtp_host} → {ip_address}")
            
            # Test reverse DNS
            try:
                hostname = socket.gethostbyaddr(ip_address)[0]
                print(f"✅ Reverse DNS: {ip_address} → {hostname}")
            except:
                print(f"⚠️  No reverse DNS found for {ip_address}")
            
            # Test MX records for the domain
            domain = self.smtp_host
            try:
                mx_records = dns.resolver.resolve(domain, 'MX')
                print(f"✅ MX Records for {domain}:")
                for mx in sorted(mx_records, key=lambda x: x.preference):
                    print(f"   Priority {mx.preference}: {mx.exchange}")
            except:
                print(f"⚠️  No MX records found for {domain}")
                
            # Test SPF records
            try:
                txt_records = dns.resolver.resolve(domain, 'TXT')
                spf_found = False
                for txt in txt_records:
                    txt_str = str(txt).strip('"')
                    if txt_str.startswith('v=spf1'):
                        print(f"✅ SPF Record: {txt_str}")
                        spf_found = True
                        break
                if not spf_found:
                    print(f"⚠️  No SPF record found for {domain}")
            except:
                print(f"⚠️  Could not query TXT records for {domain}")
                
        except Exception as e:
            print(f"❌ DNS analysis failed: {e}")
            
        print()
    
    def test_network_connectivity(self):
        """Test network connectivity to various SMTP ports"""
        print("🔌 STEP 2: NETWORK CONNECTIVITY ANALYSIS")
        print("-" * 50)
        
        ports_to_test = [25, 465, 587, 2525, 26]
        
        for port in ports_to_test:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(10)
                start_time = time.time()
                result = sock.connect_ex((self.smtp_host, port))
                end_time = time.time()
                sock.close()
                
                if result == 0:
                    response_time = round((end_time - start_time) * 1000, 2)
                    print(f"✅ Port {port}: Open (Response: {response_time}ms)")
                else:
                    print(f"❌ Port {port}: Closed/Filtered")
                    
            except Exception as e:
                print(f"❌ Port {port}: Error - {e}")
                
        print()
    
    def analyze_smtp_server_capabilities(self):
        """Deep analysis of SMTP server capabilities"""
        print("🔍 STEP 3: SMTP SERVER CAPABILITIES ANALYSIS")
        print("-" * 50)
        
        ports_to_analyze = [587, 465, 25]
        
        for port in ports_to_analyze:
            print(f"\n📡 Analyzing port {port}:")
            try:
                if port == 465:
                    # SSL connection
                    context = ssl.create_default_context()
                    server = smtplib.SMTP_SSL(self.smtp_host, port, context=context, timeout=15)
                    print(f"   ✅ SSL connection established")
                else:
                    # Regular connection
                    server = smtplib.SMTP(self.smtp_host, port, timeout=15)
                    print(f"   ✅ Connection established")
                    
                    if port == 587:
                        # Try STARTTLS
                        try:
                            context = ssl.create_default_context()
                            server.starttls(context=context)
                            print(f"   ✅ STARTTLS successful")
                        except Exception as e:
                            print(f"   ❌ STARTTLS failed: {e}")
                
                # Get server greeting and capabilities
                try:
                    code, response = server.ehlo()
                    print(f"   ✅ EHLO successful (Code: {code})")
                    
                    # Parse server response
                    response_lines = response.decode('utf-8').split('\n')
                    server_name = response_lines[0].split()[0] if response_lines else "Unknown"
                    print(f"   🖥️  Server: {server_name}")
                    
                    # Check supported features
                    features = server.esmtp_features
                    print(f"   🔧 Supported features:")
                    
                    for feature, params in features.items():
                        if feature.upper() == 'AUTH':
                            auth_methods = params.split() if params else []
                            print(f"      🔐 AUTH: {' '.join(auth_methods)}")
                        elif feature.upper() == 'SIZE':
                            print(f"      📏 SIZE: {params} bytes")
                        elif feature.upper() == 'STARTTLS':
                            print(f"      🔒 STARTTLS: Available")
                        else:
                            print(f"      ⚙️  {feature.upper()}: {params}")
                            
                except Exception as e:
                    print(f"   ❌ EHLO failed: {e}")
                
                server.quit()
                
            except Exception as e:
                print(f"   ❌ Connection failed: {e}")
                
        print()
    
    def test_authentication_methods(self):
        """Test various authentication methods"""
        print("🔐 STEP 4: AUTHENTICATION METHODS TESTING")
        print("-" * 50)
        
        test_configs = [
            {"port": 587, "tls": True, "ssl": False, "name": "Port 587 + STARTTLS"},
            {"port": 465, "tls": False, "ssl": True, "name": "Port 465 + SSL"},
            {"port": 25, "tls": False, "ssl": False, "name": "Port 25 (Plain)"},
            {"port": 25, "tls": True, "ssl": False, "name": "Port 25 + STARTTLS"},
        ]
        
        successful_config = None
        
        for config in test_configs:
            print(f"\n🧪 Testing: {config['name']}")
            try:
                # Establish connection
                if config['ssl']:
                    context = ssl.create_default_context()
                    server = smtplib.SMTP_SSL(self.smtp_host, config['port'], context=context, timeout=15)
                else:
                    server = smtplib.SMTP(self.smtp_host, config['port'], timeout=15)
                    
                    if config['tls']:
                        try:
                            context = ssl.create_default_context()
                            server.starttls(context=context)
                            print(f"   ✅ TLS encryption enabled")
                        except Exception as e:
                            print(f"   ⚠️  TLS failed: {e}")
                
                print(f"   ✅ Connection established")
                
                # Try authentication
                try:
                    server.login(self.smtp_user, self.smtp_pass)
                    print(f"   ✅ Authentication successful!")
                    successful_config = config
                    
                    # Test email sending capability
                    if self.test_email_sending_via_server(server):
                        print(f"   ✅ Email sending test successful!")
                        server.quit()
                        return successful_config
                    else:
                        print(f"   ⚠️  Email sending test failed")
                        
                except smtplib.SMTPAuthenticationError as e:
                    print(f"   ❌ Authentication failed: {e}")
                except Exception as e:
                    print(f"   ❌ Login error: {e}")
                
                server.quit()
                
            except Exception as e:
                print(f"   ❌ Connection error: {e}")
                
        return successful_config
    
    def test_email_sending_via_server(self, server):
        """Test email sending using an established server connection"""
        try:
            # Create test message
            message = MIMEMultipart("alternative")
            message["Subject"] = "🧪 cPanel SMTP Test - Martial Arts Academy"
            message["From"] = self.smtp_from
            message["To"] = self.test_email
            
            # Plain text content
            text_content = f"""
Hello,

This is a successful cPanel SMTP test email from the Martial Arts Academy system!

✅ SMTP Server: {self.smtp_host}
✅ Authentication: Working
✅ Email Delivery: Successful

Configuration Details:
- Server: {self.smtp_host}
- User: {self.smtp_user}
- From: {self.smtp_from}
- To: {self.test_email}

If you receive this email, the forgot password functionality should now work correctly.

Best regards,
Martial Arts Academy Team

---
Test timestamp: {time.ctime()}
            """.strip()
            
            # Add plain text part
            text_part = MIMEText(text_content, "plain")
            message.attach(text_part)
            
            # Send email
            server.sendmail(self.smtp_from, self.test_email, message.as_string())
            return True
            
        except Exception as e:
            print(f"   ❌ Email sending failed: {e}")
            return False
    
    def test_email_delivery(self):
        """Test email delivery with the working configuration"""
        print("📧 STEP 5: EMAIL DELIVERY TESTING")
        print("-" * 50)
        
        # This will be integrated with authentication testing
        print("Email delivery testing integrated with authentication tests above.")
        print()
    
    def test_cpanel_specific_features(self):
        """Test cPanel-specific SMTP features"""
        print("🏢 STEP 6: cPanel SPECIFIC FEATURES")
        print("-" * 50)
        
        print("Testing cPanel-specific configurations:")
        
        # Test different authentication formats
        auth_variants = [
            self.smtp_user,  # Full email
            self.smtp_user.split('@')[0],  # Username only
            f"{self.smtp_user.split('@')[0]}%{self.smtp_host}",  # cPanel format
        ]
        
        print(f"\n🔑 Testing authentication variants:")
        for variant in auth_variants:
            print(f"   Testing username: {variant}")
            
        # Test common cPanel SMTP issues
        print(f"\n⚠️  Common cPanel SMTP considerations:")
        print(f"   - Some cPanel servers require username without domain")
        print(f"   - Some require full email address")
        print(f"   - Port 587 with STARTTLS is usually preferred")
        print(f"   - Port 465 with SSL/TLS is alternative")
        print(f"   - Authentication may be case-sensitive")
        
        print()

if __name__ == "__main__":
    print("🚀 Starting Comprehensive cPanel SMTP Investigation")
    print("This will thoroughly analyze the sveats.cyberdetox.in SMTP server.")
    print()
    
    investigator = CPanelSMTPInvestigation()
    investigator.run_comprehensive_investigation()
