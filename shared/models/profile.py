"""
Profile-related models for comprehensive user profile management
"""

from datetime import datetime
from .user import db


class UserStats(db.Model):
    """Model for user test statistics and performance metrics"""
    __tablename__ = 'user_stats'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, unique=True)
    total_tests_taken = db.Column(db.Integer, default=0)
    highest_score = db.Column(db.Integer, default=0)
    average_score = db.Column(db.Numeric(5, 2), default=0.00)
    current_streak = db.Column(db.Integer, default=0)
    total_attempts = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', backref='stats')
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'total_tests_taken': self.total_tests_taken,
            'highest_score': self.highest_score,
            'average_score': float(self.average_score) if self.average_score else 0.0,
            'current_streak': self.current_streak,
            'total_attempts': self.total_attempts,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def __repr__(self):
        return f'<UserStats {self.user_id}>'


class UserAcademics(db.Model):
    """Model for user academic information"""
    __tablename__ = 'user_academics'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, unique=True)
    school_college = db.Column(db.String(255), nullable=True)
    grade_year = db.Column(db.String(100), nullable=True)
    board_university = db.Column(db.String(255), nullable=True)
    current_exam_target = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', backref='academics')
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'school_college': self.school_college,
            'grade_year': self.grade_year,
            'board_university': self.board_university,
            'current_exam_target': self.current_exam_target,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def __repr__(self):
        return f'<UserAcademics {self.user_id}>'


class UserPurchaseHistory(db.Model):
    """Model for user purchase history tracking"""
    __tablename__ = 'user_purchase_history'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    purchase_id = db.Column(db.Integer, db.ForeignKey('exam_category_purchase.id', ondelete='CASCADE'), nullable=False)
    exam_category_id = db.Column(db.Integer, nullable=True)
    subject_id = db.Column(db.Integer, nullable=True)
    purchase_type = db.Column(db.String(50), default='single_subject')
    amount = db.Column(db.Numeric(10, 2), default=0.00)
    purchase_date = db.Column(db.DateTime, default=datetime.utcnow)
    expiry_date = db.Column(db.Date, nullable=True)
    status = db.Column(db.Enum('active', 'expired', 'cancelled'), default='active')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', backref='purchase_history')
    purchase = db.relationship('ExamCategoryPurchase', backref='history_records')
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'purchase_id': self.purchase_id,
            'exam_category_id': self.exam_category_id,
            'subject_id': self.subject_id,
            'purchase_type': self.purchase_type,
            'amount': float(self.amount) if self.amount else 0.0,
            'purchase_date': self.purchase_date.isoformat() if self.purchase_date else None,
            'expiry_date': self.expiry_date.isoformat() if self.expiry_date else None,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def __repr__(self):
        return f'<UserPurchaseHistory {self.user_id}-{self.purchase_id}>'

