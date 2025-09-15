#!/usr/bin/env python3
"""
Backend API Investigation - Comprehensive testing of email functionality
"""

import requests
import json
import time
import os
from dotenv import load_dotenv

def test_backend_connectivity():
    """Test if backend server is running and accessible"""
    print('📡 BACKEND CONNECTIVITY TEST')
    print('-'*40)
    
    try:
        response = requests.get('http://localhost:8003/docs', timeout=10)
        if response.status_code == 200:
            print('✅ Backend server is running on port 8003')
            print('✅ FastAPI docs accessible')
            return True
        else:
            print(f'⚠️  Backend responding with status: {response.status_code}')
            return False
    except Exception as e:
        print(f'❌ Backend connection failed: {e}')
        print('❌ Backend may not be running')
        return False

def test_forgot_password_api():
    """Test the forgot password API endpoint"""
    print('\n📧 FORGOT PASSWORD API TEST')
    print('-'*40)
    
    test_email = 'pittisunilkumar3@gmail.com'
    
    try:
        response = requests.post(
            'http://localhost:8003/auth/forgot-password',
            json={'email': test_email},
            timeout=15
        )
        
        print(f'📊 Status Code: {response.status_code}')
        
        if response.status_code == 200:
            data = response.json()
            print('✅ API Response: Success')
            print(f'📧 Email Sent: {data.get("email_sent", "Not specified")}')
            print(f'📄 Message: {data.get("message", "No message")}')
            
            # Check if reset token is included (for testing)
            if 'reset_token' in data:
                print(f'🔑 Reset Token: {len(data["reset_token"])} characters')
            else:
                print('🔑 Reset Token: Not included in response (security)')
                
            return True
        else:
            print(f'❌ API Error: {response.status_code}')
            print(f'📄 Response: {response.text}')
            return False
            
    except Exception as e:
        print(f'❌ API Request Failed: {e}')
        return False

def check_environment_config():
    """Check environment variable configuration"""
    print('\n🔧 ENVIRONMENT CONFIGURATION CHECK')
    print('-'*40)
    
    load_dotenv()
    
    smtp_vars = {
        'SMTP_HOST': os.getenv('SMTP_HOST'),
        'SMTP_PORT': os.getenv('SMTP_PORT'),
        'SMTP_USER': os.getenv('SMTP_USER'),
        'SMTP_PASS': '***' if os.getenv('SMTP_PASS') else None,
        'SMTP_FROM': os.getenv('SMTP_FROM'),
        'FRONTEND_URL': os.getenv('FRONTEND_URL')
    }
    
    all_configured = True
    for key, value in smtp_vars.items():
        status = '✅' if value else '❌'
        print(f'{status} {key}: {value or "Not set"}')
        if not value:
            all_configured = False
    
    return all_configured

def test_direct_smtp_connection():
    """Test direct SMTP connection"""
    print('\n🔌 DIRECT SMTP CONNECTION TEST')
    print('-'*40)
    
    import smtplib
    import ssl
    
    load_dotenv()
    
    smtp_host = os.getenv('SMTP_HOST', 'sveats.cyberdetox.in')
    smtp_port = int(os.getenv('SMTP_PORT', '587'))
    smtp_user = os.getenv('SMTP_USER', 'info@sveats.cyberdetox.in')
    smtp_pass = os.getenv('SMTP_PASS', 'Neelarani@10')
    
    try:
        print(f'🔗 Connecting to {smtp_host}:{smtp_port}')
        
        # Create SMTP connection
        server = smtplib.SMTP(smtp_host, smtp_port, timeout=10)
        print('✅ SMTP connection established')
        
        # Start TLS
        server.starttls()
        print('✅ TLS encryption enabled')
        
        # Authenticate
        server.login(smtp_user, smtp_pass)
        print('✅ SMTP authentication successful')
        
        server.quit()
        print('✅ SMTP connection closed properly')
        return True
        
    except Exception as e:
        print(f'❌ SMTP connection failed: {e}')
        return False

def test_email_service_directly():
    """Test the email service directly"""
    print('\n📧 DIRECT EMAIL SERVICE TEST')
    print('-'*40)
    
    try:
        import sys
        import os
        sys.path.append(os.path.dirname(os.path.abspath(__file__)))
        
        from utils.email_service import get_email_service
        import asyncio
        
        async def test_email():
            email_service = get_email_service()
            
            print(f'📧 Email service enabled: {email_service.enabled}')
            print(f'🔧 SMTP Host: {email_service.smtp_host}:{email_service.smtp_port}')
            print(f'👤 SMTP User: {email_service.smtp_user}')
            
            # Test sending email
            result = await email_service.send_password_reset_email(
                to_email='pittisunilkumar3@gmail.com',
                reset_token='test_token_123',
                user_name='Test User'
            )
            
            print(f'📧 Email sending result: {result}')
            return result
        
        result = asyncio.run(test_email())
        return result
        
    except Exception as e:
        print(f'❌ Email service test failed: {e}')
        return False

def main():
    """Run comprehensive backend investigation"""
    print('🔍 COMPREHENSIVE BACKEND API INVESTIGATION')
    print('='*60)
    
    results = {}
    
    # Test 1: Backend connectivity
    results['backend_running'] = test_backend_connectivity()
    
    # Test 2: Environment configuration
    results['env_configured'] = check_environment_config()
    
    # Test 3: Direct SMTP connection
    results['smtp_connection'] = test_direct_smtp_connection()
    
    # Test 4: Forgot password API
    results['api_working'] = test_forgot_password_api()
    
    # Test 5: Direct email service
    results['email_service'] = test_email_service_directly()
    
    # Summary
    print('\n📊 INVESTIGATION SUMMARY')
    print('='*60)
    
    for test_name, result in results.items():
        status = '✅' if result else '❌'
        print(f'{status} {test_name.replace("_", " ").title()}: {"PASS" if result else "FAIL"}')
    
    # Overall status
    all_passed = all(results.values())
    print(f'\n🎯 Overall Status: {"✅ ALL SYSTEMS OPERATIONAL" if all_passed else "❌ ISSUES DETECTED"}')
    
    if not all_passed:
        print('\n🔧 RECOMMENDED ACTIONS:')
        if not results['backend_running']:
            print('   - Start the backend server: python server.py')
        if not results['env_configured']:
            print('   - Check .env file configuration')
        if not results['smtp_connection']:
            print('   - Verify SMTP credentials and server settings')
        if not results['api_working']:
            print('   - Check API endpoint implementation')
        if not results['email_service']:
            print('   - Review email service configuration')

if __name__ == "__main__":
    main()
