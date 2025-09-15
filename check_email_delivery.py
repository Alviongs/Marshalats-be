import os
import time
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def check_email_status():
    """Check email delivery status and logs"""
    email_logs_dir = Path("email_logs")
    
    print("🔍 Checking email delivery status...")
    print(f"SMTP Server: {os.getenv('SMTP_HOST')}:{os.getenv('SMTP_PORT')}")
    print(f"Sender: {os.getenv('SMTP_FROM')}")
    
    # Check email logs directory
    if email_logs_dir.exists():
        print("\n📄 Found email logs:")
        for log_file in email_logs_dir.glob("*.log"):
            print(f"- {log_file.name} (last modified: {time.ctime(log_file.stat().st_mtime)})")
            
            # Show last 5 lines of each log file
            try:
                with open(log_file, 'r') as f:
                    lines = f.readlines()[-5:]
                    print("  Recent log entries:")
                    for line in lines:
                        print(f"  {line.strip()}")
            except Exception as e:
                print(f"  Could not read log file: {str(e)}")
    else:
        print("\n⚠️ No email logs directory found")
    
    print("\nNext steps:")
    print("1. Check your spam/junk folder")
    print("2. Verify the recipient email address")
    print("3. Contact your SMTP provider to check email delivery")
    print("4. Try sending to a different email provider (Gmail, Outlook, etc.)")

if __name__ == "__main__":
    check_email_status()
