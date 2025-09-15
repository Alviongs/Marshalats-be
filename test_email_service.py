import asyncio
import os
from dotenv import load_dotenv
from pathlib import Path
from utils.email_service import send_email

# Load environment variables
ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

async def test_send_email():
    try:
        to_email = input("Enter recipient email: ")
        subject = "Test Email from LMS System"
        message = "This is a test email sent from the LMS system."
        
        print(f"Sending test email to: {to_email}")
        print(f"Using SMTP server: {os.getenv('SMTP_HOST')}")
        
        result = await send_email(
            to_email=to_email,
            subject=subject,
            body=message,
            html_body=f"<p>{message}</p>"
        )
        
        if result:
            print("✅ Email sent successfully!")
            print("Please check your inbox (and spam folder) for the test email.")
        else:
            print("❌ Failed to send email. Check server logs for details.")
            
    except Exception as e:
        print(f"❌ An error occurred: {str(e)}")
    finally:
        # Give some time for the email to be sent before exiting
        await asyncio.sleep(2)

if __name__ == "__main__":
    asyncio.run(test_send_email())
