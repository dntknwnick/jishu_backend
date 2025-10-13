#!/usr/bin/env python3
"""
Get the current OTP for a user from the database
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'shared'))

from shared.models.user import db, User
from flask import Flask
from config import config

# Create Flask app
app = Flask(__name__)
app.config.from_object(config['development'])

# Initialize database
db.init_app(app)

def get_user_otp(email):
    """Get the current OTP for a user"""
    with app.app_context():
        user = User.query.filter_by(email_id=email).first()
        
        if user:
            print(f"📧 User: {user.email_id}")
            print(f"🔑 Current OTP: {user.otp}")
            print(f"⏰ OTP Expires: {user.otp_expires_at}")
            print(f"✅ OTP Verified: {user.otp_verified}")
            return user.otp
        else:
            print(f"❌ User not found with email: {email}")
            return None

if __name__ == "__main__":
    email = "anupshiremath@gmail.com"
    otp = get_user_otp(email)
    if otp:
        print(f"\n🎯 Use this OTP for testing: {otp}")
