"""
Google OAuth 2.0 service for user authentication
"""

import os
import requests
from google.auth.transport import requests as google_requests
from google.oauth2 import id_token
from google_auth_oauthlib.flow import Flow
import json

class GoogleOAuthService:
    def __init__(self, client_id, client_secret, redirect_uri):
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri
        self.scopes = [
            'https://www.googleapis.com/auth/userinfo.email',
            'https://www.googleapis.com/auth/userinfo.profile',
            'openid'
        ]

        print(f"🔧 GoogleOAuthService initialized with redirect_uri: {redirect_uri}")
        
        # Create OAuth flow
        self.flow = Flow.from_client_config(
            {
                "web": {
                    "client_id": client_id,
                    "client_secret": client_secret,
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                    "redirect_uris": [redirect_uri]
                }
            },
            scopes=self.scopes
        )
        self.flow.redirect_uri = redirect_uri
    
    def get_authorization_url(self):
        """Generate Google OAuth authorization URL"""
        try:
            authorization_url, state = self.flow.authorization_url(
                access_type='offline',
                include_granted_scopes='false',  # Changed to false to avoid scope conflicts
                prompt='consent'  # Force consent screen to ensure fresh tokens
            )
            return authorization_url, state
        except Exception as e:
            print(f"❌ Error generating authorization URL: {str(e)}")
            return None, None
    
    def exchange_code_for_token(self, authorization_code):
        """Exchange authorization code for access token and user info"""
        try:
            print(f"🔄 Exchanging authorization code for token...")

            # Fetch token
            self.flow.fetch_token(code=authorization_code)

            # Get credentials
            credentials = self.flow.credentials
            print(f"✅ Successfully obtained credentials")

            # Get user info from Google
            user_info_response = requests.get(
                'https://www.googleapis.com/oauth2/v2/userinfo',
                headers={'Authorization': f'Bearer {credentials.token}'}
            )

            if user_info_response.status_code == 200:
                user_info = user_info_response.json()
                print(f"✅ Successfully fetched user info: {user_info.get('email', 'No email')}")
                return True, user_info
            else:
                error_msg = f"Failed to fetch user information from Google. Status: {user_info_response.status_code}, Response: {user_info_response.text}"
                print(f"❌ {error_msg}")
                return False, error_msg

        except Exception as e:
            error_msg = f"Error exchanging code for token: {str(e)}"
            print(f"❌ {error_msg}")
            return False, error_msg
    
    def verify_id_token(self, token):
        """Verify Google ID token (alternative method)"""
        try:
            idinfo = id_token.verify_oauth2_token(
                token, google_requests.Request(), self.client_id
            )
            
            if idinfo['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
                raise ValueError('Wrong issuer.')
            
            return True, idinfo
        except ValueError as e:
            return False, str(e)

# Global Google OAuth service instance
def create_google_oauth_service(app_config):
    """Create Google OAuth service from app config"""
    client_id = app_config.get('GOOGLE_CLIENT_ID')
    client_secret = app_config.get('GOOGLE_CLIENT_SECRET')
    redirect_uri = app_config.get('GOOGLE_REDIRECT_URI')

    print(f"🔧 Creating Google OAuth service with redirect URI: {redirect_uri}")

    if not all([client_id, client_secret, redirect_uri]):
        print("⚠️  Google OAuth not configured - missing credentials")
        return None

    return GoogleOAuthService(client_id, client_secret, redirect_uri)
