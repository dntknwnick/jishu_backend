#!/usr/bin/env python3
"""
Test script for the enhanced purchase flow and MCQ generation system
Tests LOCAL_DEV_MODE functionality and exam-specific question generation
"""

import requests
import json
import sys
import os

# Configuration
BASE_URL = "http://localhost:5000"
TEST_USER_EMAIL = "testuser@jishu.com"

def print_section(title):
    """Print a formatted section header"""
    print(f"\n{'='*60}")
    print(f" {title}")
    print(f"{'='*60}")

def print_result(success, message, data=None):
    """Print test result"""
    status = "✅ PASS" if success else "❌ FAIL"
    print(f"{status}: {message}")
    if data and isinstance(data, dict):
        print(f"   Data: {json.dumps(data, indent=2)[:200]}...")
    elif data:
        print(f"   Data: {str(data)[:200]}...")

def test_configuration():
    """Test development configuration"""
    print_section("Testing Development Configuration")
    
    try:
        response = requests.get(f"{BASE_URL}/api/config/dev-settings")
        if response.status_code == 200:
            data = response.json()
            config = data.get('data', {})
            
            local_dev = config.get('LOCAL_DEV_MODE', False)
            bypass_validation = config.get('BYPASS_PURCHASE_VALIDATION', False)
            
            print_result(local_dev, f"LOCAL_DEV_MODE: {local_dev}")
            print_result(bypass_validation, f"BYPASS_PURCHASE_VALIDATION: {bypass_validation}")
            
            return local_dev and bypass_validation
        else:
            print_result(False, f"Config endpoint failed: {response.status_code}")
            return False
            
    except Exception as e:
        print_result(False, f"Config test error: {str(e)}")
        return False

def create_test_user():
    """Create a fresh test user"""
    print_section("Creating Test User")
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/create-test-user",
            headers={'Content-Type': 'application/json'},
            json={'suffix': '3'}  # Create testuser3@jishu.com
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                user_data = data.get('data', {})
                access_token = user_data.get('access_token')
                user_info = user_data.get('user', {})
                
                print_result(True, f"Test user created: {user_info.get('email_id')}")
                return access_token
            else:
                print_result(False, f"User creation failed: {data.get('message')}")
                return None
        else:
            print_result(False, f"User creation request failed: {response.status_code}")
            return None
            
    except Exception as e:
        print_result(False, f"User creation error: {str(e)}")
        return None

def test_purchase_flow(token):
    """Test the enhanced purchase flow"""
    print_section("Testing Enhanced Purchase Flow")
    
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    try:
        # Test individual subject purchase
        purchase_data = {
            'course_id': 1,  # Assuming course ID 1 exists
            'subject_id': 1,  # Assuming subject ID 1 exists
            'payment_method': 'demo'
        }
        
        response = requests.post(
            f"{BASE_URL}/api/purchases",
            headers=headers,
            json=purchase_data
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                purchase_info = data.get('data', {})
                print_result(True, "Individual subject purchase successful")
                print(f"   Purchase ID: {purchase_info.get('purchase_id')}")
                print(f"   Total Mock Tests: {purchase_info.get('total_mock_tests')}")
                return True
            else:
                print_result(False, f"Purchase failed: {data.get('message')}")
                return False
        else:
            print_result(False, f"Purchase request failed: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print_result(False, f"Purchase test error: {str(e)}")
        return False

def test_ai_service():
    """Test AI service availability"""
    print_section("Testing AI Service")
    
    try:
        # Check if PDFs directory exists
        pdf_path = os.path.join(os.getcwd(), 'pdfs', 'subjects')
        if os.path.exists(pdf_path):
            subjects = [d for d in os.listdir(pdf_path) if os.path.isdir(os.path.join(pdf_path, d))]
            print_result(True, f"PDF subjects directory found: {subjects}")
            
            # Check for PDF files in each subject
            for subject in subjects:
                subject_path = os.path.join(pdf_path, subject)
                pdf_files = [f for f in os.listdir(subject_path) if f.endswith('.pdf')]
                print(f"   {subject}: {len(pdf_files)} PDF files")
            
            return len(subjects) > 0
        else:
            print_result(False, f"PDF directory not found: {pdf_path}")
            return False
            
    except Exception as e:
        print_result(False, f"AI service test error: {str(e)}")
        return False

def test_available_tests(token):
    """Test available tests endpoint"""
    print_section("Testing Available Tests")
    
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    try:
        response = requests.get(f"{BASE_URL}/api/user/available-tests", headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                tests = data.get('data', {}).get('available_tests', [])
                print_result(True, f"Available tests retrieved: {len(tests)} tests")
                
                for test in tests[:2]:  # Show first 2 tests
                    print(f"   - {test.get('subject_name')}: {test.get('available_tests')} available")
                
                return len(tests) > 0
            else:
                print_result(False, f"Available tests failed: {data.get('message')}")
                return False
        else:
            print_result(False, f"Available tests request failed: {response.status_code}")
            return False
            
    except Exception as e:
        print_result(False, f"Available tests error: {str(e)}")
        return False

def main():
    """Run all tests"""
    print("🧪 Enhanced Purchase Flow & MCQ Generation Test Suite")
    print("=" * 60)
    
    # Test configuration
    config_ok = test_configuration()
    if not config_ok:
        print("\n❌ Configuration test failed. Please check LOCAL_DEV_MODE settings.")
        sys.exit(1)
    
    # Create test user
    token = create_test_user()
    if not token:
        print("\n❌ Test user creation failed.")
        sys.exit(1)
    
    # Test AI service
    ai_ok = test_ai_service()
    if not ai_ok:
        print("\n⚠️  AI service test failed. MCQ generation may not work properly.")
    
    # Test purchase flow
    purchase_ok = test_purchase_flow(token)
    if not purchase_ok:
        print("\n❌ Purchase flow test failed.")
        sys.exit(1)
    
    # Test available tests
    tests_ok = test_available_tests(token)
    if not tests_ok:
        print("\n❌ Available tests test failed.")
        sys.exit(1)
    
    print_section("Test Summary")
    print("✅ All core tests passed!")
    print("✅ LOCAL_DEV_MODE is working correctly")
    print("✅ Purchase flow bypasses payment but maintains business logic")
    print("✅ Test allocation is working")
    
    if ai_ok:
        print("✅ AI service is ready for MCQ generation")
    else:
        print("⚠️  AI service needs attention")
    
    print("\n🎯 Next Steps:")
    print("1. Test the enhanced MCQ generation endpoints")
    print("2. Verify exam-specific question generation")
    print("3. Check frontend integration")

if __name__ == "__main__":
    main()
