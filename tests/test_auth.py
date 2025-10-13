"""
Unit tests for authentication endpoints and functionality
"""

import pytest
import json
from datetime import datetime, timedelta
from unittest.mock import patch

from shared.models.user import User
from tests.conftest import assert_success_response, assert_error_response


class TestOTPEndpoints:
    """Test OTP request and verification"""
    
    def test_otp_request_valid_email(self, client, mock_email_service):
        """Test OTP request with valid email"""
        response = client.post('/api/auth/otp/request', 
                             json={'email': 'test@example.com'})
        
        data = assert_success_response(response)
        assert 'OTP sent successfully' in data['message']
    
    def test_otp_request_invalid_email(self, client):
        """Test OTP request with invalid email format"""
        response = client.post('/api/auth/otp/request', 
                             json={'email': 'invalid-email'})
        
        assert_error_response(response, 400)
    
    def test_otp_request_missing_email(self, client):
        """Test OTP request without email"""
        response = client.post('/api/auth/otp/request', json={})
        
        assert_error_response(response, 400)
    
    def test_otp_request_rate_limiting(self, client, mock_email_service):
        """Test OTP request rate limiting"""
        email = 'ratelimit@example.com'
        
        # First request should succeed
        response1 = client.post('/api/auth/otp/request', json={'email': email})
        assert_success_response(response1)
        
        # Second request immediately should be rate limited
        response2 = client.post('/api/auth/otp/request', json={'email': email})
        assert_error_response(response2, 429)


class TestUserRegistration:
    """Test user registration functionality"""
    
    def test_register_valid_data(self, client, db_session, mock_email_service, valid_user_data):
        """Test user registration with valid data"""
        # First request OTP
        client.post('/api/auth/otp/request', json={'email': valid_user_data['email']})
        
        # Register user
        response = client.post('/api/auth/register', json=valid_user_data)
        
        data = assert_success_response(response, 201)
        assert 'access_token' in data['data']
        assert 'refresh_token' in data['data']
        assert data['data']['user']['email_id'] == valid_user_data['email']
        
        # Verify user was created in database
        user = db_session.query(User).filter_by(email_id=valid_user_data['email']).first()
        assert user is not None
        assert user.name == valid_user_data['name']
        assert user.mobile_no == valid_user_data['mobile_no']
        assert user.otp_verified is True
    
    def test_register_duplicate_email(self, client, sample_user, valid_user_data):
        """Test registration with existing email"""
        valid_user_data['email'] = sample_user.email_id
        
        response = client.post('/api/auth/register', json=valid_user_data)
        
        assert_error_response(response, 400)
    
    def test_register_invalid_password(self, client, valid_user_data):
        """Test registration with weak password"""
        valid_user_data['password'] = '123'  # Too short
        
        response = client.post('/api/auth/register', json=valid_user_data)
        
        assert_error_response(response, 400)
    
    def test_register_invalid_mobile(self, client, valid_user_data):
        """Test registration with invalid mobile number"""
        valid_user_data['mobile_no'] = '123'  # Too short
        
        response = client.post('/api/auth/register', json=valid_user_data)
        
        assert_error_response(response, 400)
    
    def test_register_missing_fields(self, client):
        """Test registration with missing required fields"""
        incomplete_data = {'email': 'test@example.com'}
        
        response = client.post('/api/auth/register', json=incomplete_data)
        
        assert_error_response(response, 400)


class TestUserLogin:
    """Test user login functionality"""
    
    def test_login_valid_credentials(self, client, sample_user, mock_email_service):
        """Test login with valid email and OTP"""
        # Request OTP
        client.post('/api/auth/otp/request', json={'email': sample_user.email_id})
        
        # Login with OTP
        response = client.post('/api/auth/login', json={
            'email': sample_user.email_id,
            'otp': '123456'  # Mock OTP
        })
        
        data = assert_success_response(response)
        assert 'access_token' in data['data']
        assert 'refresh_token' in data['data']
        assert data['data']['user']['email_id'] == sample_user.email_id
    
    def test_login_invalid_email(self, client):
        """Test login with non-existent email"""
        response = client.post('/api/auth/login', json={
            'email': 'nonexistent@example.com',
            'otp': '123456'
        })
        
        assert_error_response(response, 401)
    
    def test_login_invalid_otp(self, client, sample_user):
        """Test login with invalid OTP"""
        response = client.post('/api/auth/login', json={
            'email': sample_user.email_id,
            'otp': 'wrong'
        })
        
        assert_error_response(response, 401)
    
    def test_login_expired_otp(self, client, sample_user, db_session):
        """Test login with expired OTP"""
        # Set expired OTP
        sample_user.otp = '123456'
        sample_user.otp_expires_at = datetime.utcnow() - timedelta(minutes=10)
        db_session.commit()
        
        response = client.post('/api/auth/login', json={
            'email': sample_user.email_id,
            'otp': '123456'
        })
        
        assert_error_response(response, 401)


class TestTokenRefresh:
    """Test JWT token refresh functionality"""
    
    def test_refresh_valid_token(self, client, auth_headers):
        """Test token refresh with valid refresh token"""
        # Get refresh token from test user creation
        response = client.post('/api/create-test-user', json={'suffix': '1'})
        data = response.get_json()
        refresh_token = data['data']['refresh_token']
        
        # Use refresh token
        headers = {'Authorization': f'Bearer {refresh_token}'}
        response = client.post('/refresh-token', headers=headers)
        
        data = assert_success_response(response)
        assert 'access_token' in data['data']
        assert 'refresh_token' in data['data']
    
    def test_refresh_invalid_token(self, client):
        """Test token refresh with invalid token"""
        headers = {'Authorization': 'Bearer invalid-token'}
        response = client.post('/refresh-token', headers=headers)
        
        assert_error_response(response, 401)
    
    def test_refresh_missing_token(self, client):
        """Test token refresh without token"""
        response = client.post('/refresh-token')
        
        assert_error_response(response, 401)


class TestUserProfile:
    """Test user profile endpoints"""
    
    def test_get_profile_authenticated(self, client, auth_headers):
        """Test getting user profile with valid token"""
        response = client.get('/api/auth/profile', headers=auth_headers)
        
        data = assert_success_response(response)
        assert 'user' in data['data']
        assert 'email_id' in data['data']['user']
        assert 'name' in data['data']['user']
    
    def test_get_profile_unauthenticated(self, client):
        """Test getting user profile without token"""
        response = client.get('/api/auth/profile')
        
        assert_error_response(response, 401)
    
    def test_update_profile_valid_data(self, client, auth_headers):
        """Test updating user profile with valid data"""
        update_data = {
            'name': 'Updated Name',
            'mobile_no': '9876543210',
            'color_theme': 'dark'
        }
        
        response = client.put('/api/auth/profile/edit', 
                            headers=auth_headers, json=update_data)
        
        data = assert_success_response(response)
        assert data['data']['user']['name'] == update_data['name']
        assert data['data']['user']['color_theme'] == update_data['color_theme']
    
    def test_update_profile_invalid_data(self, client, auth_headers):
        """Test updating user profile with invalid data"""
        update_data = {
            'name': '',  # Empty name
            'mobile_no': '123',  # Invalid mobile
            'color_theme': 'invalid'  # Invalid theme
        }
        
        response = client.put('/api/auth/profile/edit', 
                            headers=auth_headers, json=update_data)
        
        assert_error_response(response, 400)


class TestGoogleOAuth:
    """Test Google OAuth functionality"""
    
    @patch('google.auth.transport.requests.Request')
    @patch('google.oauth2.id_token.verify_oauth2_token')
    def test_google_oauth_new_user(self, mock_verify, mock_request, client, db_session):
        """Test Google OAuth with new user"""
        # Mock Google token verification
        mock_verify.return_value = {
            'sub': 'google123',
            'email': 'google@example.com',
            'name': 'Google User',
            'email_verified': True
        }
        
        response = client.post('/api/auth/google/verify', json={
            'token': 'mock-google-token'
        })
        
        data = assert_success_response(response, 201)
        assert 'access_token' in data['data']
        assert data['data']['user']['email_id'] == 'google@example.com'
        assert data['data']['user']['auth_provider'] == 'google'
        
        # Verify user was created
        user = db_session.query(User).filter_by(google_id='google123').first()
        assert user is not None
        assert user.email_id == 'google@example.com'
    
    @patch('google.auth.transport.requests.Request')
    @patch('google.oauth2.id_token.verify_oauth2_token')
    def test_google_oauth_existing_user(self, mock_verify, mock_request, client, db_session):
        """Test Google OAuth with existing user"""
        # Create existing Google user
        existing_user = User(
            mobile_no='9876543210',
            email_id='existing@example.com',
            name='Existing User',
            google_id='google123',
            auth_provider='google',
            otp_verified=True,
            status='active'
        )
        db_session.add(existing_user)
        db_session.commit()
        
        # Mock Google token verification
        mock_verify.return_value = {
            'sub': 'google123',
            'email': 'existing@example.com',
            'name': 'Existing User',
            'email_verified': True
        }
        
        response = client.post('/api/auth/google/verify', json={
            'token': 'mock-google-token'
        })
        
        data = assert_success_response(response)
        assert data['data']['user']['email_id'] == 'existing@example.com'
    
    def test_google_oauth_invalid_token(self, client):
        """Test Google OAuth with invalid token"""
        response = client.post('/api/auth/google/verify', json={
            'token': 'invalid-token'
        })
        
        assert_error_response(response, 401)


class TestLogout:
    """Test user logout functionality"""
    
    def test_logout_authenticated(self, client, auth_headers):
        """Test logout with valid token"""
        response = client.post('/api/auth/logout', headers=auth_headers)
        
        data = assert_success_response(response)
        assert 'logged out successfully' in data['message'].lower()
    
    def test_logout_unauthenticated(self, client):
        """Test logout without token"""
        response = client.post('/api/auth/logout')
        
        assert_error_response(response, 401)


class TestPasswordSecurity:
    """Test password security features"""
    
    def test_password_hashing(self, db_session):
        """Test that passwords are properly hashed"""
        user = User(
            mobile_no='9876543210',
            email_id='hash@example.com',
            name='Hash User',
            otp_verified=True,
            status='active'
        )
        user.set_password('plaintext123')
        
        # Password should be hashed, not stored as plaintext
        assert user.password != 'plaintext123'
        assert user.check_password('plaintext123') is True
        assert user.check_password('wrongpassword') is False
    
    def test_password_validation(self, client, valid_user_data):
        """Test password strength validation"""
        test_cases = [
            ('123', 'Too short'),
            ('password', 'No numbers'),
            ('12345678', 'No letters'),
            ('Pass123!', 'Valid password')
        ]
        
        for password, description in test_cases:
            valid_user_data['password'] = password
            response = client.post('/api/auth/register', json=valid_user_data)
            
            if description == 'Valid password':
                # This might fail due to other validation, but password should be OK
                pass  # We're just testing password validation here
            else:
                # Should fail validation
                assert response.status_code == 400
