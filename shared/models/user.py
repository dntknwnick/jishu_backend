from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

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
    otp_verified = db.Column(db.Boolean, default=False)
    last_login = db.Column(db.DateTime, nullable=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.Enum('active', 'inactive', 'blocked'), default='active')
    source = db.Column(db.String(100), nullable=True)  # 'google', 'email', etc.
    
    def set_password(self, password):
        """Hash and set password"""
        self.password = generate_password_hash(password)
    
    def check_password(self, password):
        """Check if provided password matches hash"""
        if not self.password:
            return False
        return check_password_hash(self.password, password)
    
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
            'source': self.source
        }
    
    def __repr__(self):
        return f'<User {self.email_id}>'
