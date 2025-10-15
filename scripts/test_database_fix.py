#!/usr/bin/env python3
"""
Test the database fix for test_answers table
"""

import os
import sys
import requests
import json

# Add the parent directory to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

BASE_URL = "http://localhost:5000"

def test_database_connection():
    """Test if the database connection works"""
    try:
        from shared.models.user import db
        from shared.models.purchase import TestAnswer, TestAttemptSession
        
        print("Testing database models...")
        
        # Try to query the TestAnswer model
        count = TestAnswer.query.count()
        print(f"TestAnswer records: {count}")
        
        # Try to query TestAttemptSession model
        session_count = TestAttemptSession.query.count()
        print(f"TestAttemptSession records: {session_count}")
        
        print("Database models work correctly!")
        return True
        
    except Exception as e:
        print(f"Database model test failed: {str(e)}")
        return False

def test_api_endpoints():
    """Test if the API endpoints are working"""
    try:
        # Test basic health check
        response = requests.get(f"{BASE_URL}/api/health")
        if response.status_code == 200:
            print("API server is running")
            return True
        else:
            print(f"API server returned status: {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("API server is not running")
        return False
    except Exception as e:
        print(f"API test failed: {str(e)}")
        return False

def create_test_user():
    """Create a test user for testing"""
    try:
        response = requests.post(f"{BASE_URL}/api/create-test-user")
        if response.status_code == 200:
            data = response.json()
            if data['success']:
                print("Test user created successfully")
                return data['data']['access_token']
            else:
                print(f"Test user creation failed: {data.get('message', 'Unknown error')}")
                return None
        else:
            print(f"Test user creation request failed: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"Error creating test user: {str(e)}")
        return None

def test_test_answer_creation():
    """Test creating a TestAnswer record directly"""
    try:
        from shared.models.user import db
        from shared.models.purchase import TestAnswer, TestAttemptSession
        from shared.models.course import ExamCategoryQuestion
        
        print("Testing TestAnswer creation...")
        
        # Create a test session first
        test_session = TestAttemptSession(
            mock_test_id=None,
            user_id=1,  # Assuming user ID 1 exists
            attempt_number=1,
            status='in_progress'
        )
        
        db.session.add(test_session)
        db.session.flush()  # Get the session ID
        
        # Create a test answer
        test_answer = TestAnswer(
            session_id=test_session.id,
            question_id=1,  # Assuming question ID 1 exists
            selected_answer='A',
            is_correct=True,
            time_taken=30
        )
        
        db.session.add(test_answer)
        db.session.commit()
        
        print(f"TestAnswer created successfully with ID: {test_answer.id}")
        
        # Clean up
        db.session.delete(test_answer)
        db.session.delete(test_session)
        db.session.commit()
        
        print("Test cleanup completed")
        return True
        
    except Exception as e:
        print(f"TestAnswer creation failed: {str(e)}")
        try:
            db.session.rollback()
        except:
            pass
        return False

def main():
    """Main test function"""
    print("Database Fix Test")
    print("=" * 30)
    
    # Test 1: Database connection and models
    print("\nTest 1: Database Models")
    if not test_database_connection():
        print("FAILED: Database models test")
        return False
    
    # Test 2: API server
    print("\nTest 2: API Server")
    if not test_api_endpoints():
        print("FAILED: API server test")
        return False
    
    # Test 3: TestAnswer creation
    print("\nTest 3: TestAnswer Creation")
    if not test_test_answer_creation():
        print("FAILED: TestAnswer creation test")
        return False
    
    print("\n" + "=" * 30)
    print("ALL TESTS PASSED!")
    print("The database fix is working correctly.")
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
