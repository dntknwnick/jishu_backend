#!/usr/bin/env python3
"""
Make a specific user an admin
"""

from app import app
from shared.models.user import db, User

def make_user_admin(email):
    """Make a user admin by email"""
    with app.app_context():
        user = User.query.filter_by(email_id=email).first()
        if user:
            user.is_admin = True
            user.status = 'active'
            user.otp_verified = True
            db.session.commit()
            print(f'✅ User {email} is now an admin')
            print(f'User ID: {user.id}')
            print(f'Name: {user.name}')
            print(f'Status: {user.status}')
            print(f'Is Admin: {user.is_admin}')
        else:
            print(f'❌ User {email} not found')

if __name__ == '__main__':
    # Replace with your email
    email = input("Enter email to make admin: ")
    make_user_admin(email)
