#!/usr/bin/env python3
"""
Test script to verify authentication flow and token refresh
"""

import requests
import json
import time

BASE_URL = 'http://localhost:5000'

def test_auth_flow():
    print("🔧 Testing Authentication Flow")
    print("=" * 50)
    
    # Step 1: Create test user
    print("\n1. Creating test user...")
    try:
        response = requests.post(f'{BASE_URL}/api/dev/create-test-user')
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                access_token = data['data']['access_token']
                refresh_token = data['data']['refresh_token']
                user = data['data']['user']
                print(f"✅ Test user created: {user['email_id']}")
                print(f"   Access Token: {access_token[:20]}...")
                print(f"   Refresh Token: {refresh_token[:20]}...")
                return access_token, refresh_token, user
            else:
                print(f"❌ Failed to create test user: {data.get('message')}")
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"❌ Exception: {e}")
    
    return None, None, None

def test_protected_endpoint(access_token):
    print("\n2. Testing protected endpoint...")
    headers = {'Authorization': f'Bearer {access_token}'}
    
    try:
        response = requests.get(f'{BASE_URL}/api/user/available-tests', headers=headers)
        print(f"   Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Protected endpoint accessible")
            print(f"   Response: {json.dumps(data, indent=2)[:200]}...")
            return True
        elif response.status_code == 401:
            print(f"❌ Unauthorized - Token might be expired")
            return False
        else:
            print(f"❌ Unexpected status: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Exception: {e}")
        return False

def test_token_refresh(refresh_token):
    print("\n3. Testing token refresh...")
    headers = {'Authorization': f'Bearer {refresh_token}'}
    
    try:
        response = requests.post(f'{BASE_URL}/refresh-token', headers=headers)
        print(f"   Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                new_access_token = data['data']['access_token']
                new_refresh_token = data['data']['refresh_token']
                print(f"✅ Token refresh successful")
                print(f"   New Access Token: {new_access_token[:20]}...")
                print(f"   New Refresh Token: {new_refresh_token[:20]}...")
                return new_access_token, new_refresh_token
            else:
                print(f"❌ Refresh failed: {data.get('message')}")
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"❌ Exception: {e}")
    
    return None, None

def test_ai_status():
    print("\n4. Testing AI status endpoint (public)...")
    try:
        response = requests.get(f'{BASE_URL}/api/ai/rag/status')
        print(f"   Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ AI status endpoint accessible")
            print(f"   Status: {data.get('data', {}).get('status', 'unknown')}")
            print(f"   Dependencies: {data.get('data', {}).get('dependencies', {})}")
            return True
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Exception: {e}")
        return False

def test_mcq_generation(access_token):
    print("\n5. Testing MCQ generation (admin required)...")
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    
    payload = {
        'content': 'Photosynthesis is the process by which plants convert light energy into chemical energy. This process occurs in chloroplasts and involves two main stages: light-dependent reactions and the Calvin cycle.',
        'num_questions': 2,
        'subject_name': 'Biology',
        'difficulty': 'medium',
        'save_to_database': False
    }
    
    try:
        response = requests.post(f'{BASE_URL}/api/ai/generate-questions-from-text', 
                               headers=headers, json=payload)
        print(f"   Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                questions = data.get('questions', [])
                print(f"✅ MCQ generation successful")
                print(f"   Generated {len(questions)} questions")
                if questions:
                    print(f"   Sample question: {questions[0].get('question', '')[:100]}...")
                return True
            else:
                print(f"❌ Generation failed: {data.get('error')}")
        elif response.status_code == 403:
            print(f"❌ Forbidden - Admin access required")
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"❌ Exception: {e}")
    
    return False

def main():
    print("🚀 Starting Authentication and MCQ Generation Tests")
    
    # Test 1: Create test user and get tokens
    access_token, refresh_token, user = test_auth_flow()
    if not access_token:
        print("\n❌ Cannot proceed without valid tokens")
        return
    
    # Test 2: Test protected endpoint
    endpoint_works = test_protected_endpoint(access_token)
    
    # Test 3: Test token refresh
    if refresh_token:
        new_access_token, new_refresh_token = test_token_refresh(refresh_token)
        if new_access_token:
            access_token = new_access_token  # Use new token for subsequent tests
    
    # Test 4: Test AI status (public endpoint)
    test_ai_status()
    
    # Test 5: Test MCQ generation (admin required)
    if user and user.get('is_admin'):
        test_mcq_generation(access_token)
    else:
        print("\n5. Skipping MCQ generation test - user is not admin")
        print(f"   User admin status: {user.get('is_admin') if user else 'unknown'}")
    
    print("\n" + "=" * 50)
    print("🏁 Test completed!")

if __name__ == '__main__':
    main()
