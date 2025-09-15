import asyncio
import os
import logging
from dotenv import load_dotenv
from pathlib import Path

# Set up detailed logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('email_debug.log')
    ]
)
logger = logging.getLogger(__name__)

# Load environment variables
ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

async def test_email_service():
    """Test the email service with detailed logging"""
    from utils.email_service import EmailService
    
    logger.info("Starting email service test...")
    
    # Initialize the email service
    email_service = EmailService()
    
    # Log configuration
    logger.info(f"SMTP Configuration:")
    logger.info(f"  Host: {email_service.smtp_host}")
    logger.info(f"  Port: {email_service.smtp_port}")
    logger.info(f"  User: {email_service.smtp_user}")
    logger.info(f"  From: {email_service.smtp_from}")
    
    if not email_service.enabled:
        logger.error("Email service is not enabled. Check your .env file.")
        return
    
    # Test email details
    test_recipient = "pittisunilkumar4@gmail.com"
    test_subject = "Debug Test Email from LMS"
    test_body = """
    This is a detailed test email to verify the email service.
    
    If you receive this email, the SMTP configuration is working correctly.
    
    Best regards,
    LMS Support Team
    """
    
    test_html = """
    <h1>Debug Test Email</h1>
    <p>This is a detailed test email to verify the email service.</p>
    <p>If you receive this email, the SMTP configuration is working correctly.</p>
    <p>Best regards,<br><strong>LMS Support Team</strong></p>
    """
    
    try:
        logger.info(f"Sending test email to: {test_recipient}")
        
        # Send the email
        success = await email_service.send_email(
            to_email=test_recipient,
            subject=test_subject,
            body=test_body,
            html_body=test_html
        )
        
        if success:
            logger.info("✅ Email sent successfully!")
            print("\n✅ Test email was sent successfully!")
            print("Please check your inbox (and spam folder) for the test email.")
        else:
            logger.error("❌ Email sending failed (returned False)")
            print("\n❌ Email sending failed (returned False)")
            print("Check the email_debug.log file for more details.")
            
    except Exception as e:
        logger.exception("❌ Exception occurred while sending email")
        print(f"\n❌ An error occurred: {str(e)}")
        print("Check the email_debug.log file for the full traceback.")
    finally:
        logger.info("Email test completed.")

if __name__ == "__main__":
    print("Running email service test...")
    print("Detailed logs are being written to email_debug.log")
    asyncio.run(test_email_service())
