import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from flask import Flask, request, jsonify, session, redirect, url_for
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from flask_cors import CORS
import requests
from google.auth.transport import requests as google_requests
from google.oauth2 import id_token
import json
from datetime import datetime, timedelta

from shared.models.user import db, User
from shared.utils.validators import validate_email_format, validate_mobile_number, validate_password_strength, validate_name
from shared.utils.response_helper import success_response, error_response, validation_error_response
from config import config

def create_app(config_name='development'):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    # Initialize extensions
    db.init_app(app)
    jwt = JWTManager(app)
    CORS(app, origins=app.config['CORS_ORIGINS'])
    
    @app.route('/health', methods=['GET'])
    def health_check():
        return success_response(message="Auth service is running")
    
    @app.route('/register', methods=['POST'])
    def register():
        try:
            data = request.get_json()
            
            # Validate required fields
            required_fields = ['email_id', 'password', 'confirm_password', 'name', 'mobile_no']
            errors = {}
            
            for field in required_fields:
                if not data.get(field):
                    errors[field] = f"{field.replace('_', ' ').title()} is required"
            
            if errors:
                return validation_error_response(errors)
            
            # Validate email format
            if not validate_email_format(data['email_id']):
                errors['email_id'] = "Invalid email format"
            
            # Validate mobile number
            if not validate_mobile_number(data['mobile_no']):
                errors['mobile_no'] = "Invalid mobile number format"
            
            # Validate name
            is_valid_name, name_message = validate_name(data['name'])
            if not is_valid_name:
                errors['name'] = name_message
            
            # Validate password
            is_strong_password, password_message = validate_password_strength(data['password'])
            if not is_strong_password:
                errors['password'] = password_message
            
            # Check password confirmation
            if data['password'] != data['confirm_password']:
                errors['confirm_password'] = "Passwords do not match"
            
            if errors:
                return validation_error_response(errors)
            
            # Check if user already exists
            existing_user = User.query.filter_by(email_id=data['email_id']).first()
            if existing_user:
                return error_response("User with this email already exists", 409)
            
            # Create new user
            user = User(
                email_id=data['email_id'],
                name=data['name'].strip(),
                mobile_no=data['mobile_no'],
                source='email'
            )
            user.set_password(data['password'])
            
            db.session.add(user)
            db.session.commit()
            
            # Create access token
            access_token = create_access_token(identity=user.id)
            
            return success_response({
                'user': user.to_dict(),
                'access_token': access_token
            }, "User registered successfully", 201)
            
        except Exception as e:
            db.session.rollback()
            return error_response(f"Registration failed: {str(e)}", 500)
    
    @app.route('/login', methods=['POST'])
    def login():
        try:
            data = request.get_json()
            
            # Validate required fields
            if not data.get('email_id') or not data.get('password'):
                return error_response("Email and password are required", 400)
            
            # Find user
            user = User.query.filter_by(email_id=data['email_id']).first()
            if not user:
                return error_response("Invalid email or password", 401)
            
            # Check password
            if not user.check_password(data['password']):
                return error_response("Invalid email or password", 401)
            
            # Check user status
            if user.status != 'active':
                return error_response("Account is not active", 403)
            
            # Update last login
            user.last_login = datetime.utcnow()
            db.session.commit()
            
            # Create access token
            access_token = create_access_token(identity=user.id)
            
            return success_response({
                'user': user.to_dict(),
                'access_token': access_token
            }, "Login successful")
            
        except Exception as e:
            return error_response(f"Login failed: {str(e)}", 500)
    
    @app.route('/google-auth', methods=['POST'])
    def google_auth():
        try:
            data = request.get_json()
            token = data.get('token')

            if not token:
                return error_response("Google token is required", 400)

            # Verify Google token
            try:
                idinfo = id_token.verify_oauth2_token(
                    token, google_requests.Request(), app.config['GOOGLE_CLIENT_ID']
                )

                if idinfo['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
                    raise ValueError('Wrong issuer.')

                # Extract user info from Google
                google_id = idinfo['sub']
                email = idinfo['email']
                name = idinfo['name']

            except ValueError as e:
                return error_response("Invalid Google token", 401)

            # Check if user exists
            user = User.query.filter_by(email_id=email).first()

            if user:
                # Existing user - login
                user.last_login = datetime.utcnow()
                if not user.source:
                    user.source = 'google'
                message = "Google login successful"
            else:
                # New user - register
                user = User(
                    email_id=email,
                    name=name,
                    mobile_no='',  # Will be updated later in profile
                    source='google',
                    otp_verified=True  # Google users are pre-verified
                )
                message = "Google registration and login successful"

            db.session.add(user)
            db.session.commit()

            # Create access token
            access_token = create_access_token(identity=user.id)

            return success_response({
                'user': user.to_dict(),
                'access_token': access_token,
                'is_new_user': user.created_at == user.updated_at  # Check if just created
            }, message)

        except Exception as e:
            db.session.rollback()
            return error_response(f"Google authentication failed: {str(e)}", 500)

    @app.route('/auth/google/callback', methods=['GET'])
    def google_callback():
        """
        Google OAuth callback endpoint
        This handles the redirect from Google after user authorization
        """
        try:
            # Get authorization code from query parameters
            code = request.args.get('code')
            error = request.args.get('error')

            if error:
                return error_response(f"Google OAuth error: {error}", 400)

            if not code:
                return error_response("Authorization code not provided", 400)

            # Exchange code for token (this would typically be done on frontend)
            # For now, return a simple response indicating the callback was received
            return success_response({
                'code': code,
                'message': 'Authorization code received. Exchange this for token on frontend.'
            }, "Google OAuth callback received")

        except Exception as e:
            return error_response(f"Google OAuth callback failed: {str(e)}", 500)
    
    @app.route('/verify-token', methods=['POST'])
    @jwt_required()
    def verify_token():
        try:
            user_id = get_jwt_identity()
            user = User.query.get(user_id)
            
            if not user:
                return error_response("User not found", 404)
            
            return success_response({
                'user': user.to_dict()
            }, "Token is valid")
            
        except Exception as e:
            return error_response(f"Token verification failed: {str(e)}", 500)
    
    return app

if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        db.create_all()
    # Bind to 127.0.0.1 so it's only accessible internally
    app.run(host='127.0.0.1', port=5001, debug=True)
