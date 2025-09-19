import requests
import json
import time

def test_forgot_password():
    """Test the forgot password API endpoint"""
    
    # Test the forgot password endpoint
    url = 'http://localhost:8003/auth/forgot-password'
    data = {'email': 'pittisunilkumar3@gmail.com'}
    
    print(f'🧪 Testing forgot password endpoint: {url}')
    print(f'📧 Request data: {data}')
    print('-' * 50)
    
    try:
        response = requests.post(url, json=data, timeout=10)
        
        print(f'📊 Response Status: {response.status_code}')
        print(f'📋 Response Headers: {dict(response.headers)}')
        print(f'📄 Response Body: {response.text}')
        print('-' * 50)
        
        if response.status_code == 200:
            print('✅ Forgot password request successful!')
            
            # Parse response
            try:
                response_data = response.json()
                print(f'📝 Response Message: {response_data.get("message", "No message")}')
            except:
                print('⚠️  Could not parse JSON response')
                
        else:
            print('❌ Forgot password request failed!')
            
    except requests.exceptions.ConnectionError:
        print('❌ Cannot connect to server. Is the backend running on port 8003?')
        return False
    except Exception as e:
        print(f'❌ Request failed: {e}')
        return False
    
    return True

def check_server_status():
    """Check if the server is running"""
    try:
        response = requests.get('http://localhost:8003/docs', timeout=5)
        if response.status_code == 200:
            print('✅ Server is running on port 8003')
            return True
        else:
            print(f'⚠️  Server responded with status {response.status_code}')
            return False
    except:
        print('❌ Server is not running on port 8003')
        return False

if __name__ == "__main__":
    print('🚀 Testing Forgot Password API')
    print('=' * 50)
    
    # Check server status first
    if not check_server_status():
        print('\n💡 Please start the server with: python server.py')
        exit(1)
    
    print()
    
    # Test the forgot password functionality
    success = test_forgot_password()
    
    print('\n' + '=' * 50)
    if success:
        print('🎉 Test completed! Check your email for the password reset link.')
    else:
        print('💥 Test failed! Please check the server logs for errors.')
