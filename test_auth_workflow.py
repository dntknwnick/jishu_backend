#!/usr/bin/env python3
"""
Authentication Workflow Test Script
Tests the complete authentication flow including registration and login
"""

import requests
import json
import sys
from datetime import datetime

# Configuration
BASE_URL = 'http://localhost:5000'
TEST_USER_EMAIL = 'test@example.com'
TEST_USER_PASSWORD = 'TestPass@123'

class AuthTester:
    def __init__(self, base_url=BASE_URL):
        self.base_url = base_url
        self.session = requests.Session()
        self.access_token = None
        
    def print_result(self, test_name, success, message, data=None):
        """Print test result in a formatted way"""
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}: {message}")
        if data and isinstance(data, dict):
            print(f"   Data: {json.dumps(data, indent=2)}")
        print()
    
    def test_health_check(self):
        """Test if all services are running"""
        print("🔍 Testing Service Health...")
        
        services = [
            ('Gateway', f'{self.base_url}/health'),
            ('Auth Service', f'{self.base_url.replace("5000", "5001")}/health'),
            ('User Service', f'{self.base_url.replace("5000", "5002")}/health')
        ]
        
        all_healthy = True
        for service_name, url in services:
            try:
                response = requests.get(url, timeout=5)
                if response.status_code == 200:
                    self.print_result(f"{service_name} Health", True, "Service is running")
                else:
                    self.print_result(f"{service_name} Health", False, f"Status: {response.status_code}")
                    all_healthy = False
            except requests.exceptions.RequestException as e:
                self.print_result(f"{service_name} Health", False, f"Connection failed: {str(e)}")
                all_healthy = False
        
        return all_healthy
    
    def test_user_registration(self):
        """Test user registration with email/password"""
        print("📝 Testing User Registration...")
        
        registration_data = {
            "name": "Test User",
            "email_id": TEST_USER_EMAIL,
            "mobile_no": "9876543210",
            "password": TEST_USER_PASSWORD,
            "confirm_password": TEST_USER_PASSWORD
        }
        
        try:
            response = requests.post(
                f'{self.base_url}/api/auth/register',
                json=registration_data,
                headers={'Content-Type': 'application/json'}
            )
            
            if response.status_code == 201:
                data = response.json()
                if data.get('success') and data.get('data', {}).get('access_token'):
                    self.access_token = data['data']['access_token']
                    user_data = data['data']['user']
                    self.print_result(
                        "User Registration", 
                        True, 
                        f"User registered successfully: {user_data['name']} ({user_data['email_id']})",
                        {'user_id': user_data['id'], 'source': user_data['source']}
                    )
                    return True
                else:
                    self.print_result("User Registration", False, "No access token in response", data)
            elif response.status_code == 409:
                self.print_result("User Registration", True, "User already exists (expected for repeated tests)")
                return True
            else:
                data = response.json() if response.headers.get('content-type', '').startswith('application/json') else {}
                self.print_result("User Registration", False, f"Status: {response.status_code}", data)
                
        except requests.exceptions.RequestException as e:
            self.print_result("User Registration", False, f"Request failed: {str(e)}")
        
        return False
    
    def test_user_login(self):
        """Test user login with email/password"""
        print("🔑 Testing User Login...")
        
        login_data = {
            "email_id": TEST_USER_EMAIL,
            "password": TEST_USER_PASSWORD
        }
        
        try:
            response = requests.post(
                f'{self.base_url}/api/auth/login',
                json=login_data,
                headers={'Content-Type': 'application/json'}
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success') and data.get('data', {}).get('access_token'):
                    self.access_token = data['data']['access_token']
                    user_data = data['data']['user']
                    self.print_result(
                        "User Login", 
                        True, 
                        f"Login successful: {user_data['name']} ({user_data['email_id']})",
                        {'user_id': user_data['id'], 'last_login': user_data.get('last_login')}
                    )
                    return True
                else:
                    self.print_result("User Login", False, "No access token in response", data)
            else:
                data = response.json() if response.headers.get('content-type', '').startswith('application/json') else {}
                self.print_result("User Login", False, f"Status: {response.status_code}", data)
                
        except requests.exceptions.RequestException as e:
            self.print_result("User Login", False, f"Request failed: {str(e)}")
        
        return False
    
    def test_token_verification(self):
        """Test JWT token verification"""
        print("🛡️ Testing Token Verification...")
        
        if not self.access_token:
            self.print_result("Token Verification", False, "No access token available")
            return False
        
        try:
            response = requests.post(
                f'{self.base_url}/api/auth/verify-token',
                headers={
                    'Authorization': f'Bearer {self.access_token}',
                    'Content-Type': 'application/json'
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    user_data = data['data']['user']
                    self.print_result(
                        "Token Verification", 
                        True, 
                        f"Token is valid for user: {user_data['name']}",
                        {'user_id': user_data['id'], 'email': user_data['email_id']}
                    )
                    return True
                else:
                    self.print_result("Token Verification", False, "Token verification failed", data)
            else:
                data = response.json() if response.headers.get('content-type', '').startswith('application/json') else {}
                self.print_result("Token Verification", False, f"Status: {response.status_code}", data)
                
        except requests.exceptions.RequestException as e:
            self.print_result("Token Verification", False, f"Request failed: {str(e)}")
        
        return False
    
    def test_user_profile(self):
        """Test getting user profile"""
        print("👤 Testing User Profile...")
        
        if not self.access_token:
            self.print_result("User Profile", False, "No access token available")
            return False
        
        try:
            response = requests.get(
                f'{self.base_url}/api/user/profile',
                headers={
                    'Authorization': f'Bearer {self.access_token}',
                    'Content-Type': 'application/json'
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    user_data = data['data']['user']
                    self.print_result(
                        "User Profile", 
                        True, 
                        f"Profile retrieved: {user_data['name']}",
                        {
                            'email': user_data['email_id'],
                            'mobile': user_data['mobile_no'],
                            'source': user_data['source'],
                            'status': user_data['status']
                        }
                    )
                    return True
                else:
                    self.print_result("User Profile", False, "Failed to get profile", data)
            else:
                data = response.json() if response.headers.get('content-type', '').startswith('application/json') else {}
                self.print_result("User Profile", False, f"Status: {response.status_code}", data)
                
        except requests.exceptions.RequestException as e:
            self.print_result("User Profile", False, f"Request failed: {str(e)}")
        
        return False
    
    def run_all_tests(self):
        """Run all authentication tests"""
        print("🚀 Starting Authentication Workflow Tests")
        print("=" * 50)
        print(f"Base URL: {self.base_url}")
        print(f"Test Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 50)
        print()
        
        tests = [
            self.test_health_check,
            self.test_user_registration,
            self.test_user_login,
            self.test_token_verification,
            self.test_user_profile,
        ]
        
        passed = 0
        total = len(tests)
        
        for test in tests:
            if test():
                passed += 1
        
        print("=" * 50)
        print(f"📊 Test Results: {passed}/{total} tests passed")
        
        if passed == total:
            print("🎉 All tests passed! Authentication workflow is working correctly.")
            return True
        else:
            print("⚠️ Some tests failed. Please check the output above.")
            return False

def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Test authentication workflow')
    parser.add_argument('--url', default=BASE_URL, help='Base URL for the API')
    parser.add_argument('--email', default=TEST_USER_EMAIL, help='Test user email')
    parser.add_argument('--password', default=TEST_USER_PASSWORD, help='Test user password')
    
    args = parser.parse_args()
    
    global TEST_USER_EMAIL, TEST_USER_PASSWORD
    TEST_USER_EMAIL = args.email
    TEST_USER_PASSWORD = args.password
    
    tester = AuthTester(args.url)
    success = tester.run_all_tests()
    
    sys.exit(0 if success else 1)

if __name__ == '__main__':
    main()
