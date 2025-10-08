#!/usr/bin/env python3
"""
Create admin user and test course endpoints
"""

from app import app
from shared.models.user import db, User
from shared.models.course import ExamCategory, ExamCategorySubject
from flask_jwt_extended import create_access_token
import requests
import json

def create_admin_user():
    """Create admin user and return JWT token"""
    with app.app_context():
        # Check if admin user exists
        admin = User.query.filter_by(email_id='admin@test.com').first()
        if not admin:
            # Create admin user
            admin = User(
                email_id='admin@test.com',
                name='Test Admin',
                mobile_no='9876543210',
                is_admin=True,
                otp_verified=True,
                status='active'
            )
            db.session.add(admin)
            db.session.commit()
            print('✅ Admin user created: admin@test.com')
        else:
            # Update existing user to be admin
            admin.is_admin = True
            admin.otp_verified = True
            admin.status = 'active'
            db.session.commit()
            print('✅ Admin user updated: admin@test.com')
        
        # Create JWT token
        token = create_access_token(identity=admin.id)
        print(f'✅ JWT token created for admin user')
        return token, admin.id

def test_course_endpoints(token):
    """Test course endpoints"""
    BASE_URL = "http://localhost:5000"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    print("\n📚 Testing Course Endpoints")
    print("-" * 40)
    
    # Test 1: Add course
    print("1. Adding new course...")
    course_data = {
        "course_name": "UPSC Civil Services",
        "description": "Comprehensive course for UPSC Civil Services examination preparation"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/courses", json=course_data, headers=headers)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            course_id = response.json()["data"]["course"]["id"]
            print(f"   ✅ Course created with ID: {course_id}")
        else:
            print(f"   ❌ Error: {response.json()}")
            return None
    except Exception as e:
        print(f"   ❌ Request failed: {e}")
        return None
    
    # Test 2: Get all courses
    print("\n2. Getting all courses...")
    try:
        response = requests.get(f"{BASE_URL}/courses", headers=headers)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            courses = response.json()["data"]["courses"]
            print(f"   ✅ Found {len(courses)} courses")
        else:
            print(f"   ❌ Error: {response.json()}")
    except Exception as e:
        print(f"   ❌ Request failed: {e}")
    
    # Test 3: Get course by ID
    print(f"\n3. Getting course by ID: {course_id}")
    try:
        response = requests.get(f"{BASE_URL}/courses/{course_id}", headers=headers)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            course = response.json()["data"]["course"]
            print(f"   ✅ Course: {course['course_name']}")
        else:
            print(f"   ❌ Error: {response.json()}")
    except Exception as e:
        print(f"   ❌ Request failed: {e}")
    
    return course_id

def test_subject_endpoints(token, course_id):
    """Test subject endpoints"""
    BASE_URL = "http://localhost:5000"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    print("\n📖 Testing Subject Endpoints")
    print("-" * 40)
    
    # Test 1: Add subject
    print("1. Adding new subject...")
    subject_data = {
        "subject_name": "General Studies Paper 1"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/courses/{course_id}/subjects", json=subject_data, headers=headers)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            subject_id = response.json()["data"]["subject"]["id"]
            print(f"   ✅ Subject created with ID: {subject_id}")
        else:
            print(f"   ❌ Error: {response.json()}")
            return None
    except Exception as e:
        print(f"   ❌ Request failed: {e}")
        return None
    
    # Test 2: Get course subjects
    print(f"\n2. Getting subjects for course {course_id}...")
    try:
        response = requests.get(f"{BASE_URL}/courses/{course_id}/subjects", headers=headers)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            subjects = response.json()["data"]["subjects"]
            print(f"   ✅ Found {len(subjects)} subjects")
        else:
            print(f"   ❌ Error: {response.json()}")
    except Exception as e:
        print(f"   ❌ Request failed: {e}")
    
    # Test 3: Get subject by ID
    print(f"\n3. Getting subject by ID: {subject_id}")
    try:
        response = requests.get(f"{BASE_URL}/subjects/{subject_id}", headers=headers)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            subject = response.json()["data"]["subject"]
            print(f"   ✅ Subject: {subject['subject_name']}")
        else:
            print(f"   ❌ Error: {response.json()}")
    except Exception as e:
        print(f"   ❌ Request failed: {e}")
    
    return subject_id

def test_non_admin_access():
    """Test non-admin access restrictions"""
    BASE_URL = "http://localhost:5000"
    
    print("\n🚫 Testing Non-Admin Access Restrictions")
    print("-" * 40)
    
    with app.app_context():
        # Create regular user
        regular_user = User.query.filter_by(email_id='user@test.com').first()
        if not regular_user:
            regular_user = User(
                email_id='user@test.com',
                name='Test User',
                mobile_no='9876543211',
                is_admin=False,
                otp_verified=True,
                status='active'
            )
            db.session.add(regular_user)
            db.session.commit()
            print('✅ Regular user created: user@test.com')
        
        # Create JWT token for regular user
        user_token = create_access_token(identity=regular_user.id)
    
    headers = {
        "Authorization": f"Bearer {user_token}",
        "Content-Type": "application/json"
    }
    
    # Test adding course (should fail)
    print("1. Testing course addition with regular user (should fail)...")
    course_data = {
        "course_name": "Unauthorized Course",
        "description": "This should not be created"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/courses", json=course_data, headers=headers)
        print(f"   Status: {response.status_code}")
        if response.status_code == 403:
            print("   ✅ Correctly blocked non-admin from adding course")
        else:
            print(f"   ❌ Non-admin was able to add course! Response: {response.json()}")
    except Exception as e:
        print(f"   ❌ Request failed: {e}")

def main():
    """Main test function"""
    print("🧪 Course and Subject Management API Tests")
    print("=" * 50)
    
    # Create admin user and get token
    try:
        token, admin_id = create_admin_user()
        print(f"Admin user ID: {admin_id}")
    except Exception as e:
        print(f"❌ Failed to create admin user: {e}")
        return
    
    # Test course endpoints
    course_id = test_course_endpoints(token)
    if not course_id:
        print("❌ Course tests failed")
        return
    
    # Test subject endpoints
    subject_id = test_subject_endpoints(token, course_id)
    if not subject_id:
        print("❌ Subject tests failed")
        return
    
    # Test non-admin access
    test_non_admin_access()
    
    print("\n🎉 All tests completed successfully!")
    print("=" * 50)

if __name__ == "__main__":
    main()
