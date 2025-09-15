#!/usr/bin/env python3
"""
Quick Email Fix - Temporary solution to demonstrate working email functionality
"""

import os
import asyncio
from pathlib import Path
from dotenv import load_dotenv
from utils.email_service import get_email_service

# Load environment variables
ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

class QuickEmailFix:
    def __init__(self):
        self.test_email = "pittisunilkumar3@gmail.com"
        
    def show_current_issue(self):
        """Show the current issue and solutions"""
        print("🚨 CURRENT EMAIL ISSUE")
        print("=" * 50)
        print()
        print("❌ Error: (535, b'Username and Password not accepted')")
        print("📧 Gmail Account: pittisunilkumar3@gmail.com")
        print("🔑 Issue: App password not configured")
        print()
        
    def show_immediate_solutions(self):
        """Show immediate solutions"""
        print("🔧 IMMEDIATE SOLUTIONS")
        print("=" * 50)
        print()
        
        print("✅ SOLUTION 1: Set up Gmail App Password (5 minutes)")
        print("   1. Run: python setup_gmail_smtp.py")
        print("   2. Follow the interactive setup guide")
        print("   3. Test email functionality")
        print()
        
        print("✅ SOLUTION 2: Use Alternative Email Account")
        print("   1. Create a new Gmail account for the app")
        print("   2. Enable 2FA on the new account")
        print("   3. Generate app password")
        print("   4. Update .env with new credentials")
        print()
        
        print("✅ SOLUTION 3: Use Different SMTP Provider")
        print("   1. Outlook SMTP (may work with regular password)")
        print("   2. SendGrid (professional service)")
        print("   3. Mailgun (developer-friendly)")
        print()
        
    def test_current_config(self):
        """Test current email configuration"""
        print("🧪 TESTING CURRENT CONFIGURATION")
        print("=" * 50)
        
        smtp_host = os.getenv('SMTP_HOST')
        smtp_user = os.getenv('SMTP_USER')
        smtp_pass = os.getenv('SMTP_PASS')
        
        print(f"📧 SMTP Host: {smtp_host}")
        print(f"👤 SMTP User: {smtp_user}")
        print(f"🔑 SMTP Pass: {smtp_pass}")
        print()
        
        if smtp_pass == 'YOUR_GMAIL_APP_PASSWORD_HERE':
            print("❌ App password not configured!")
            print("   The .env file still has the placeholder password.")
            print("   You need to replace it with a real Gmail app password.")
            return False
        else:
            print("✅ App password appears to be configured")
            return True
    
    async def test_email_service(self):
        """Test the email service"""
        print("\n📧 TESTING EMAIL SERVICE")
        print("-" * 30)
        
        try:
            email_service = get_email_service()
            
            if not email_service.enabled:
                print("❌ Email service is disabled")
                print("   Check SMTP configuration in .env file")
                return False
            
            print("✅ Email service is enabled")
            print(f"   Host: {email_service.smtp_host}")
            print(f"   Port: {email_service.smtp_port}")
            print(f"   User: {email_service.smtp_user}")
            
            return True
            
        except Exception as e:
            print(f"❌ Email service error: {e}")
            return False
    
    def create_temp_env_backup(self):
        """Create backup of current .env file"""
        try:
            env_file = ROOT_DIR / '.env'
            backup_file = ROOT_DIR / '.env.backup'
            
            with open(env_file, 'r') as f:
                content = f.read()
            
            with open(backup_file, 'w') as f:
                f.write(content)
            
            print("✅ Created .env backup file")
            return True
            
        except Exception as e:
            print(f"❌ Could not create backup: {e}")
            return False
    
    def show_manual_setup_steps(self):
        """Show manual setup steps"""
        print("\n📋 MANUAL SETUP STEPS")
        print("=" * 50)
        print()
        print("🔐 Step 1: Enable 2-Factor Authentication")
        print("   1. Go to: https://myaccount.google.com/security")
        print("   2. Sign in with: pittisunilkumar3@gmail.com")
        print("   3. Click '2-Step Verification'")
        print("   4. Follow the setup process")
        print()
        
        print("🔑 Step 2: Generate App Password")
        print("   1. Go to: https://myaccount.google.com/apppasswords")
        print("   2. Select 'Mail' as the app")
        print("   3. Select 'Other (Custom name)' as device")
        print("   4. Enter 'Martial Arts Academy'")
        print("   5. Click 'Generate'")
        print("   6. Copy the 16-character password")
        print()
        
        print("📝 Step 3: Update .env File")
        print("   1. Open Marshalats-be/.env file")
        print("   2. Find line: SMTP_PASS=YOUR_GMAIL_APP_PASSWORD_HERE")
        print("   3. Replace with: SMTP_PASS=your_actual_app_password")
        print("   4. Save the file")
        print()
        
        print("🔄 Step 4: Restart Backend Server")
        print("   1. Stop current server (Ctrl+C)")
        print("   2. Start again: python -m uvicorn server:app --host 0.0.0.0 --port 8003 --reload")
        print()
        
        print("🧪 Step 5: Test Email Functionality")
        print("   1. Go to: http://localhost:3022/forgot-password")
        print("   2. Enter: pittisunilkumar3@gmail.com")
        print("   3. Check inbox for password reset email")
        print()
    
    def show_alternative_quick_fix(self):
        """Show alternative quick fix using different email"""
        print("\n⚡ ALTERNATIVE QUICK FIX")
        print("=" * 50)
        print()
        print("If you don't want to set up 2FA on pittisunilkumar3@gmail.com:")
        print()
        print("1. 📧 Create a new Gmail account (e.g., martialarts.academy.app@gmail.com)")
        print("2. 🔐 Enable 2FA on the new account")
        print("3. 🔑 Generate app password for the new account")
        print("4. 📝 Update .env file:")
        print("   SMTP_USER=martialarts.academy.app@gmail.com")
        print("   SMTP_PASS=new_account_app_password")
        print("   SMTP_FROM=martialarts.academy.app@gmail.com")
        print("5. 🔄 Restart backend server")
        print("6. 🧪 Test functionality")
        print()
        print("✅ This approach keeps your personal Gmail account unchanged")
        print("✅ Provides dedicated email account for the application")
        print()
    
    async def run_diagnosis(self):
        """Run complete diagnosis"""
        print("🔍 EMAIL FUNCTIONALITY DIAGNOSIS")
        print("This will help identify and fix the email sending issue.")
        print()
        
        # Show current issue
        self.show_current_issue()
        
        # Test current configuration
        config_ok = self.test_current_config()
        
        # Test email service
        service_ok = await self.test_email_service()
        
        # Show solutions
        self.show_immediate_solutions()
        
        # Show manual setup steps
        self.show_manual_setup_steps()
        
        # Show alternative fix
        self.show_alternative_quick_fix()
        
        # Final recommendations
        print("\n" + "=" * 60)
        print("🎯 RECOMMENDED ACTION")
        print("=" * 60)
        
        if not config_ok:
            print("\n🚀 QUICKEST SOLUTION:")
            print("   Run: python setup_gmail_smtp.py")
            print("   This interactive script will guide you through the setup.")
            
        print("\n📧 EXPECTED RESULT:")
        print("   After setup, you should see:")
        print("   ✅ Email sent successfully to pittisunilkumar3@gmail.com")
        print("   ✅ Password reset email in inbox")
        print("   ✅ Complete forgot password workflow functional")
        
        print("\n⏱️  ESTIMATED TIME: 5-10 minutes")
        print("💡 TIP: The interactive setup script will do most of the work for you!")

async def main():
    """Main function"""
    fix = QuickEmailFix()
    await fix.run_diagnosis()

if __name__ == "__main__":
    asyncio.run(main())
