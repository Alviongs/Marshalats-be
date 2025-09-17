#!/usr/bin/env python3
"""
Test full API response
"""

import requests
import json

def test_full_response():
    response = requests.post(
        'http://31.97.224.169:8003/auth/forgot-password',
        json={'email': 'pittisunilkumar3@gmail.com'},
        timeout=15
    )

    print('📊 Full API Response:')
    print(f'Status: {response.status_code}')
    print(f'Headers: {dict(response.headers)}')
    print(f'Body: {response.text}')

    if response.status_code == 200:
        data = response.json()
        print(f'\n📧 Email Sent Field: {data.get("email_sent", "NOT PRESENT")}')
        print(f'🔑 Reset Token Field: {"PRESENT" if "reset_token" in data else "NOT PRESENT"}')
        
        if data.get("email_sent"):
            print('✅ Email was sent successfully according to API response')
        else:
            print('❌ Email sending failed or not reported')

if __name__ == "__main__":
    test_full_response()
