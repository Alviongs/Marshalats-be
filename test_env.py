#!/usr/bin/env python3
"""
Test script to verify environment variables are loaded correctly
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
ROOT_DIR = Path(__file__).parent
env_file = ROOT_DIR / '.env'

print(f"🔍 Testing Environment Variables")
print(f"Root directory: {ROOT_DIR}")
print(f"Env file path: {env_file}")
print(f"Env file exists: {env_file.exists()}")

if env_file.exists():
    print(f"\n📄 Contents of .env file:")
    with open(env_file, 'r') as f:
        content = f.read()
        print(content)

print(f"\n🔧 Loading environment variables...")
load_dotenv(env_file)

print(f"\n📊 Environment Variables:")
print(f"MONGO_URL: {os.getenv('MONGO_URL', 'NOT SET')}")
print(f"DB_NAME: {os.getenv('DB_NAME', 'NOT SET')}")
print(f"SECRET_KEY: {os.getenv('SECRET_KEY', 'NOT SET')}")
print(f"TESTING: {os.getenv('TESTING', 'NOT SET')}")
print(f"SMTP_HOST: {os.getenv('SMTP_HOST', 'NOT SET')}")
print(f"SMTP_PORT: {os.getenv('SMTP_PORT', 'NOT SET')}")
print(f"SMTP_USER: {os.getenv('SMTP_USER', 'NOT SET')}")
print(f"SMTP_PASS: {os.getenv('SMTP_PASS', 'NOT SET')}")
print(f"SMTP_FROM: {os.getenv('SMTP_FROM', 'NOT SET')}")
print(f"FRONTEND_URL: {os.getenv('FRONTEND_URL', 'NOT SET')}")

# Test email service initialization
print(f"\n📧 Testing Email Service:")
from utils.email_service import EmailService

email_service = EmailService()
print(f"Email service enabled: {email_service.enabled}")
print(f"SMTP Host: {email_service.smtp_host}")
print(f"SMTP Port: {email_service.smtp_port}")
print(f"SMTP User: {email_service.smtp_user}")
print(f"Has SMTP Password: {bool(email_service.smtp_pass)}")
