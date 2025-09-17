#!/usr/bin/env python3
"""
Test with correct email address
"""

import requests
import json

def test_correct_email():
    print('🧪 TESTING WITH CORRECT EMAIL ADDRESS')
    print('='*60)

    # Test with the actual email in database
    correct_email = 'pittisunilkumar@gmail.com'

    response = requests.post(
        'http://31.97.224.169:8003/auth/forgot-password',
        json={'email': correct_email},
        timeout=15
    )

    print(f'📊 Status Code: {response.status_code}')
    print(f'📧 Testing with: {correct_email}')

    if response.status_code == 200:
        data = response.json()
        print('✅ API Response: Success')
        print(f'📧 Email Sent: {data.get("email_sent", "NOT PRESENT")}')
        print(f'🔑 Reset Token: {"PRESENT" if "reset_token" in data else "NOT PRESENT"}')
        print(f'📄 Message: {data.get("message", "No message")}')
        
        if data.get('email_sent'):
            print('\n🎉 SUCCESS! Email was sent successfully!')
            return True
        else:
            print('\n❌ Email sending failed')
            return False
    else:
        print(f'❌ API Error: {response.status_code}')
        print(f'📄 Response: {response.text}')
        return False

if __name__ == "__main__":
    result = test_correct_email()
    print(f'\n🎯 Test result: {"SUCCESS" if result else "FAILED"}')
