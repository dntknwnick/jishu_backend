from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
import random
import string

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    mobile_no = db.Column(db.String(20), nullable=False)
    email_id = db.Column(db.String(100), nullable=False, unique=True)
    name = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(255), nullable=True)  # Nullable for Google OAuth users
    is_premium = db.Column(db.Boolean, default=False)
    is_admin = db.Column(db.Boolean, default=False)
    color_theme = db.Column(db.Enum('light', 'dark'), default='light')
    otp = db.Column(db.String(10), nullable=True)
    otp_expires_at = db.Column(db.DateTime, nullable=True)
    otp_verified = db.Column(db.Boolean, default=False)
    last_login = db.Column(db.DateTime, nullable=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.Enum('active', 'inactive', 'blocked'), default='active')
    source = db.Column(db.String(100), nullable=True)  # 'google', 'email', etc.
    google_id = db.Column(db.String(255), nullable=True, unique=True)
    auth_provider = db.Column(db.Enum('manual', 'google'), default='manual')
    refresh_token = db.Column(db.Text, nullable=True)
    refresh_token_expires_at = db.Column(db.DateTime, nullable=True)
    
    def set_password(self, password):
        """Hash and set password"""
        self.password = generate_password_hash(password)
    
    def check_password(self, password):
        """Check if provided password matches hash"""
        if not self.password:
            return False
        return check_password_hash(self.password, password)

    def generate_otp(self):
        """Generate a 6-digit OTP and set expiry time"""
        self.otp = ''.join(random.choices(string.digits, k=6))
        self.otp_expires_at = datetime.utcnow() + timedelta(minutes=10)  # OTP expires in 10 minutes
        self.otp_verified = False
        return self.otp

    def verify_otp(self, provided_otp):
        """Verify the provided OTP"""
        if not self.otp or not self.otp_expires_at:
            return False, "No OTP generated"

        if datetime.utcnow() > self.otp_expires_at:
            return False, "OTP has expired"

        if self.otp != provided_otp:
            return False, "Invalid OTP"

        # OTP is valid
        self.otp_verified = True
        self.otp = None  # Clear OTP after successful verification
        self.otp_expires_at = None
        return True, "OTP verified successfully"

    def set_refresh_token(self, refresh_token, expires_at):
        """Set refresh token and its expiry time"""
        self.refresh_token = refresh_token
        self.refresh_token_expires_at = expires_at

    def is_refresh_token_valid(self, provided_token):
        """Check if the provided refresh token is valid and not expired"""
        if not self.refresh_token or not self.refresh_token_expires_at:
            return False, "No refresh token found"

        if datetime.utcnow() > self.refresh_token_expires_at:
            return False, "Refresh token has expired"

        if self.refresh_token != provided_token:
            return False, "Invalid refresh token"

        return True, "Refresh token is valid"

    def clear_refresh_token(self):
        """Clear refresh token and its expiry time"""
        self.refresh_token = None
        self.refresh_token_expires_at = None
    
    def to_dict(self):
        """Convert user object to dictionary"""
        return {
            'id': self.id,
            'mobile_no': self.mobile_no,
            'email_id': self.email_id,
            'name': self.name,
            'is_premium': self.is_premium,
            'is_admin': self.is_admin,
            'color_theme': self.color_theme,
            'otp_verified': self.otp_verified,
            'last_login': self.last_login.isoformat() if self.last_login else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'status': self.status,
            'source': self.source,
            'google_id': self.google_id,
            'auth_provider': self.auth_provider
        }
    
    def __repr__(self):
        return f'<User {self.email_id}>'
