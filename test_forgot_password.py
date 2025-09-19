#!/usr/bin/env python3
"""
Test script for forgot password functionality
"""

import asyncio
import aiohttp
import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

API_BASE_URL = "http://localhost:8003"

async def test_forgot_password():
    """Test the forgot password functionality"""
    print("🧪 Testing Forgot Password Functionality")
    print("=" * 50)
    
    # Test email (should exist in database)
    test_email = "pittisunilkumar3@gmail.com"
    
    async with aiohttp.ClientSession() as session:
        # Test 1: Valid email
        print(f"📧 Testing forgot password with email: {test_email}")
        
        forgot_password_data = {
            "email": test_email
        }
        
        try:
            async with session.post(
                f"{API_BASE_URL}/auth/forgot-password",
                json=forgot_password_data,
                headers={"Content-Type": "application/json"}
            ) as response:
                data = await response.json()
                
                if response.status == 200:
                    print("✅ Forgot password request successful!")
                    print(f"   Message: {data.get('message')}")
                    
                    # If testing mode, show the token
                    if data.get('reset_token'):
                        print(f"   Reset Token (testing): {data.get('reset_token')}")
                        print(f"   Email Sent: {data.get('email_sent', 'Unknown')}")
                        
                        # Test the reset password with the token
                        await test_reset_password(session, data.get('reset_token'))
                    else:
                        print("   Check your email for reset instructions!")
                        
                else:
                    print(f"❌ Request failed with status {response.status}")
                    print(f"   Error: {data}")
                    
        except Exception as e:
            print(f"❌ Error testing forgot password: {e}")
        
        print()
        
        # Test 2: Invalid email
        print("📧 Testing forgot password with invalid email")
        
        invalid_email_data = {
            "email": "nonexistent@example.com"
        }
        
        try:
            async with session.post(
                f"{API_BASE_URL}/auth/forgot-password",
                json=invalid_email_data,
                headers={"Content-Type": "application/json"}
            ) as response:
                data = await response.json()
                
                if response.status == 200:
                    print("✅ Request handled correctly (doesn't reveal if email exists)")
                    print(f"   Message: {data.get('message')}")
                else:
                    print(f"❌ Unexpected response: {response.status}")
                    print(f"   Error: {data}")
                    
        except Exception as e:
            print(f"❌ Error testing invalid email: {e}")

async def test_reset_password(session, reset_token):
    """Test the reset password functionality with a token"""
    print("\n🔐 Testing Reset Password with Token")
    print("-" * 30)
    
    new_password = "NewTestPassword123!"
    
    reset_data = {
        "token": reset_token,
        "new_password": new_password
    }
    
    try:
        async with session.post(
            f"{API_BASE_URL}/auth/reset-password",
            json=reset_data,
            headers={"Content-Type": "application/json"}
        ) as response:
            data = await response.json()
            
            if response.status == 200:
                print("✅ Password reset successful!")
                print(f"   Message: {data.get('message')}")
                
                # Test login with new password
                await test_login_with_new_password(session, "pittisunilkumar3@gmail.com", new_password)
                
            else:
                print(f"❌ Password reset failed with status {response.status}")
                print(f"   Error: {data}")
                
    except Exception as e:
        print(f"❌ Error testing reset password: {e}")

async def test_login_with_new_password(session, email, password):
    """Test login with the new password"""
    print("\n🔑 Testing Login with New Password")
    print("-" * 30)
    
    login_data = {
        "email": email,
        "password": password
    }
    
    try:
        async with session.post(
            f"{API_BASE_URL}/auth/login",
            json=login_data,
            headers={"Content-Type": "application/json"}
        ) as response:
            data = await response.json()
            
            if response.status == 200:
                print("✅ Login successful with new password!")
                print(f"   User: {data.get('user', {}).get('full_name', 'Unknown')}")
                print(f"   Token received: {'Yes' if data.get('access_token') else 'No'}")
            else:
                print(f"❌ Login failed with status {response.status}")
                print(f"   Error: {data}")
                
    except Exception as e:
        print(f"❌ Error testing login: {e}")

if __name__ == "__main__":
    # Set testing mode
    os.environ["TESTING"] = "True"
    
    print("🚀 Starting Forgot Password Tests")
    print("Make sure the backend server is running on http://localhost:8003")
    print()
    
    asyncio.run(test_forgot_password())
