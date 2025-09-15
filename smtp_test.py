import smtplib
import ssl
import os
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables
ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

def test_smtp_connection():
    """Test SMTP connection and authentication"""
    smtp_host = os.getenv('SMTP_HOST')
    smtp_port = int(os.getenv('SMTP_PORT', '587'))
    smtp_user = os.getenv('SMTP_USER')
    smtp_pass = os.getenv('SMTP_PASS')

    print("\n" + "="*50)
    print("SMTP Connection Test")
    print("="*50)
    print(f"Host: {smtp_host}")
    print(f"Port: {smtp_port}")
    print(f"Username: {smtp_user}")
    print("Password: [HIDDEN]" if smtp_pass else "Password: [NOT SET]")

    try:
        # Create a secure SSL context
        context = ssl.create_default_context()

        # Try to log in to server and send email
        with smtplib.SMTP(smtp_host, smtp_port) as server:
            print("\n1. Connecting to SMTP server...")
            server.ehlo()
            
            print("2. Starting TLS encryption...")
            server.starttls(context=context)
            server.ehlo()
            
            print("3. Authenticating...")
            server.login(smtp_user, smtp_pass)
            
            print("\n✅ SMTP Connection Successful!")
            print("   The SMTP server is reachable and credentials are valid.")
            
            # Test sending a simple email
            test_recipient = "pittisunilkumar4@gmail.com"
            test_subject = "SMTP Test Email"
            test_message = "This is a test email to verify SMTP functionality."
            
            msg = f"Subject: {test_subject}\n\n{test_message}"
            
            print(f"\nSending test email to: {test_recipient}")
            server.sendmail(smtp_user, test_recipient, msg)
            print("✅ Test email sent successfully!")
            
    except Exception as e:
        print(f"\n❌ SMTP Connection Failed!")
        print(f"Error: {str(e)}")
        
        if "authentication failed" in str(e).lower():
            print("\nPossible issues:")
            print("- Incorrect username or password")
            print("- SMTP authentication is not enabled for this user")
            print("- App password might be required instead of regular password")
        elif "connection refused" in str(e).lower():
            print("\nPossible issues:")
            print("- SMTP server is not running")
            print("- Firewall is blocking the connection")
            print("- Incorrect port number")
        elif "timed out" in str(e).lower():
            print("\nPossible issues:")
            print("- Network connectivity issues")
            print("- SMTP server is not reachable")
            print("- DNS resolution failed")

if __name__ == "__main__":
    test_smtp_connection()
