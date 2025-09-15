import asyncio
import os
from dotenv import load_dotenv
import sys

# Add project root to the Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

from utils.email_service import EmailService

# Load environment variables from .env file
load_dotenv()

async def main():
    """
    Test function to send a simple email.
    """
    print("Attempting to send a test email...")
    
    # Initialize the email service
    email_service = EmailService()

    # Check if the service is enabled
    if not email_service.enabled:
        print("Email service is not enabled. Check your .env file for SMTP credentials.")
        return

    # Recipient email address
    to_email = "pittisunilkumar4@gmail.com"
    subject = "Test Email from Martial Arts Academy"
    body = """
    This is a test email to verify the SMTP configuration.
    
    If you're receiving this email, the email service is working correctly!
    
    Best regards,
    Martial Arts Academy Team
    """
    html_body = """
    <h1>Test Email from Martial Arts Academy</h1>
    <p>This is a test email to verify the <strong>SMTP configuration</strong>.</p>
    <p>If you're receiving this email, the email service is working correctly!</p>
    <p>Best regards,<br>Martial Arts Academy Team</p>
    """

    print(f"Sending email to: {to_email}")
    print(f"Using SMTP host: {email_service.smtp_host}:{email_service.smtp_port}")
    print(f"Using SMTP user: {email_service.smtp_user}")

    # Send the email
    success = await email_service.send_email(
        to_email=to_email,
        subject=subject,
        body=body,
        html_body=html_body
    )

    if success:
        print("✅ Test email sent successfully!")
    else:
        print("❌ Failed to send test email. Please check the logs for errors.")

if __name__ == "__main__":
    # Ensure the event loop is managed correctly
    try:
        asyncio.run(main())
    except Exception as e:
        print(f"An error occurred: {e}")
