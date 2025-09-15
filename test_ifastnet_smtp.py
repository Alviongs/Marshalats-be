import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_smtp_connection():
    # SMTP Configuration for ifastnet.in
    smtp_config = {
        'host': 'mail.ifastnet.com',  # ifastnet's mail server
        'port': 587,                  # Standard SMTP port with STARTTLS
        'username': os.getenv('SMTP_USER'),
        'password': os.getenv('SMTP_PASS'),
        'from_email': os.getenv('SMTP_FROM'),
        'to_email': 'pittisunilkumar4@gmail.com'
    }

    print("Testing SMTP Connection to ifastnet.in...")
    print(f"Host: {smtp_config['host']}")
    print(f"Port: {smtp_config['port']}")
    print(f"Username: {smtp_config['username']}")

    # Create message
    msg = MIMEMultipart()
    msg['From'] = smtp_config['from_email']
    msg['To'] = smtp_config['to_email']
    msg['Subject'] = "Test Email from ifastnet.in SMTP"
    
    body = """
    This is a test email sent using ifastnet.in's SMTP server.
    
    If you're receiving this, the SMTP configuration is correct!
    
    Best regards,
    LMS System
    """
    
    msg.attach(MIMEText(body, 'plain'))
    
    try:
        # Create secure connection
        context = ssl.create_default_context()
        
        # Connect to the SMTP server
        with smtplib.SMTP(smtp_config['host'], smtp_config['port']) as server:
            print("\n1. Connecting to SMTP server...")
            server.ehlo()
            
            print("2. Starting TLS encryption...")
            server.starttls(context=context)
            server.ehlo()
            
            print("3. Authenticating...")
            server.login(smtp_config['username'], smtp_config['password'])
            
            print("4. Sending test email...")
            server.send_message(msg)
            
            print("\n✅ Email sent successfully!")
            print(f"Check {smtp_config['to_email']} for the test email.")
            
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        print("\nTroubleshooting tips:")
        print("1. Verify your SMTP credentials in the .env file")
        print("2. Check if your ifastnet.in hosting allows remote SMTP access")
        print("3. Try using port 465 with SSL instead of 587 with STARTTLS")
        print("4. Contact ifastnet.in support to confirm SMTP settings")

if __name__ == "__main__":
    test_smtp_connection()
