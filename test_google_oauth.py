#!/usr/bin/env python3
"""
Google OAuth Testing Script
This script helps debug Google OAuth issues by testing each step manually.
"""

import requests
import json
import sys
from urllib.parse import urlparse, parse_qs

def test_oauth_config():
    """Test OAuth configuration"""
    print("🔧 Testing Google OAuth Configuration...")
    
    try:
        response = requests.get('http://localhost:5000/api/debug/google-oauth')
        if response.status_code == 200:
            data = response.json()
            print("✅ OAuth Configuration:")
            for key, value in data['data'].items():
                print(f"   {key}: {value}")
            return True
        else:
            print(f"❌ Failed to get OAuth config: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error testing OAuth config: {e}")
        return False

def get_authorization_url():
    """Get Google authorization URL"""
    print("\n🔗 Getting Google Authorization URL...")
    
    try:
        response = requests.get('http://localhost:5000/auth/google')
        if response.status_code == 200:
            data = response.json()
            auth_url = data['data']['authorization_url']
            print(f"✅ Authorization URL generated")
            print(f"🔗 URL: {auth_url}")
            
            # Parse and display URL components
            parsed = urlparse(auth_url)
            params = parse_qs(parsed.query)
            print(f"📋 URL Components:")
            print(f"   client_id: {params.get('client_id', ['Not found'])[0]}")
            print(f"   redirect_uri: {params.get('redirect_uri', ['Not found'])[0]}")
            print(f"   scope: {params.get('scope', ['Not found'])[0]}")
            
            return auth_url
        else:
            print(f"❌ Failed to get authorization URL: {response.status_code}")
            print(f"Response: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Error getting authorization URL: {e}")
        return None

def test_code_verification(code):
    """Test authorization code verification"""
    print(f"\n🔐 Testing Authorization Code Verification...")
    print(f"Code: {code[:20]}...")
    
    try:
        response = requests.post(
            'http://localhost:5000/api/auth/google/verify',
            headers={'Content-Type': 'application/json'},
            json={'code': code}
        )
        
        print(f"📊 Response Status: {response.status_code}")
        print(f"📋 Response Body: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print("✅ OAuth verification successful!")
                user = data['data']['user']
                print(f"👤 User: {user.get('email', 'Unknown')}")
                print(f"🎫 Access Token: {data['data']['access_token'][:20]}...")
                return True
            else:
                print(f"❌ OAuth verification failed: {data.get('message', 'Unknown error')}")
                return False
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            try:
                error_data = response.json()
                print(f"Error: {error_data.get('message', 'Unknown error')}")
            except:
                print(f"Raw response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing code verification: {e}")
        return False

def main():
    """Main testing function"""
    print("🚀 Google OAuth Testing Script")
    print("=" * 50)
    
    # Test 1: OAuth Configuration
    if not test_oauth_config():
        print("\n❌ OAuth configuration test failed. Check backend setup.")
        return
    
    # Test 2: Authorization URL Generation
    auth_url = get_authorization_url()
    if not auth_url:
        print("\n❌ Authorization URL generation failed.")
        return
    
    print("\n" + "=" * 50)
    print("📋 MANUAL TESTING STEPS:")
    print("1. Copy the authorization URL above")
    print("2. Open it in your browser")
    print("3. Complete Google OAuth consent")
    print("4. Copy the 'code' parameter from the callback URL")
    print("5. Run this script again with the code:")
    print(f"   python {sys.argv[0]} YOUR_CODE_HERE")
    print("=" * 50)
    
    # Test 3: Code Verification (if code provided)
    if len(sys.argv) > 1:
        code = sys.argv[1]
        test_code_verification(code)
    else:
        print("\n💡 To test code verification, run:")
        print(f"   python {sys.argv[0]} YOUR_AUTHORIZATION_CODE")

if __name__ == "__main__":
    main()
