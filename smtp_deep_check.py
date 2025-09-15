import smtplib
import ssl
import os
from dotenv import load_dotenv

# Load environment
load_dotenv()

def test_smtp():
    print("🔍 SMTP Credentials Deep Check")
    print(f"Host: {os.getenv('SMTP_HOST')}")
    print(f"Port: {os.getenv('SMTP_PORT')}")
    print(f"User: {os.getenv('SMTP_USER')}")
    
    try:
        # Test connection
        with smtplib.SMTP(os.getenv('SMTP_HOST'), int(os.getenv('SMTP_PORT'))) as server:
            print("\n1. Connection successful")
            
            # Start TLS
            context = ssl.create_default_context()
            server.starttls(context=context)
            print("2. TLS encryption enabled")
            
            # Test authentication
            try:
                server.login(os.getenv('SMTP_USER'), os.getenv('SMTP_PASS'))
                print("3. ✅ Authentication successful")
                
                # Test email sending
                test_msg = "Subject: SMTP Test\n\nThis is a test email from direct SMTP check."
                server.sendmail(os.getenv('SMTP_FROM'), "pittisunilkumar4@gmail.com", test_msg)
                print("4. ✅ Test email sent to SMTP server")
                print("   Note: This confirms server acceptance, not delivery")
                
                # Get server capabilities
                print("\nSMTP Server Capabilities:")
                print(server.ehlo())
                
            except smtplib.SMTPAuthenticationError:
                print("3. ❌ Authentication failed - check credentials")
                print("   Common issues:")
                print("   - Incorrect username/password")
                print("   - SMTP auth disabled in cPanel")
                print("   - Account suspended")
                
    except Exception as e:
        print(f"\n❌ Connection failed: {str(e)}")
        print("   Check:")
        print("   - Server is online")
        print("   - Port is open")
        print("   - Firewall settings")

if __name__ == "__main__":
    test_smtp()
