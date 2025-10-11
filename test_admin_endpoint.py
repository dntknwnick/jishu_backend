#!/usr/bin/env python3
"""
Test the new admin courses GET endpoint
"""

import requests
import json
from app import app
from shared.models.user import User
from flask_jwt_extended import create_access_token

def test_admin_courses_endpoint():
    """Test the admin courses GET endpoint"""
    
    # Create a test token for admin user
    with app.app_context():
        admin = User.query.filter_by(email_id='admin@test.com').first()
        if not admin:
            print("❌ Admin user not found. Run create_admin_and_test.py first.")
            return
        
        token = create_access_token(identity=admin.id)
        print(f"✅ Created token for admin user: {admin.email_id}")
    
    # Test the endpoint
    url = "http://localhost:5000/api/admin/courses"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    try:
        print(f"\n🔍 Testing GET {url}")
        response = requests.get(url, headers=headers)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Success! Response:")
            print(json.dumps(data, indent=2))
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"Response: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection error. Make sure the Flask server is running on localhost:5000")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == '__main__':
    test_admin_courses_endpoint()
