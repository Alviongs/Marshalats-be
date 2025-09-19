#!/usr/bin/env python3
"""
Test API now that server is running
"""

import requests
import json

def test_api():
    print('🧪 TESTING BACKEND API NOW THAT SERVER IS RUNNING')
    print('='*60)

    # Test forgot password API
    try:
        response = requests.post(
            'http://localhost:8003/auth/forgot-password',
            json={'email': 'pittisunilkumar3@gmail.com'},
            timeout=15
        )
        
        print(f'📊 Status Code: {response.status_code}')
        
        if response.status_code == 200:
            data = response.json()
            print('✅ API Response: Success')
            print(f'📧 Email Sent: {data.get("email_sent", "Not specified")}')
            print(f'📄 Message: {data.get("message", "No message")}')
            print('✅ Backend API is working correctly!')
            return True
        else:
            print(f'❌ API Error: {response.status_code}')
            print(f'📄 Response: {response.text}')
            return False
            
    except Exception as e:
        print(f'❌ API Request Failed: {e}')
        return False

if __name__ == "__main__":
    result = test_api()
    print(f'\n🎯 Backend API test complete: {"SUCCESS" if result else "FAILED"}')
