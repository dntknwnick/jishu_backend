from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from .user import db

class ExamCategory(db.Model):
    """Model for exam categories/courses"""
    __tablename__ = 'exam_category'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    course_name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)

    # Pricing fields
    amount = db.Column(db.Numeric(10, 2), nullable=True, default=0.00)  # Regular price
    offer_amount = db.Column(db.Numeric(10, 2), nullable=True, default=0.00)  # Discounted price

    # AI Token limits
    max_tokens = db.Column(db.Integer, nullable=True, default=0)  # 0 means unlimited for full course

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship with subjects
    subjects = db.relationship('ExamCategorySubject', backref='exam_category', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self, include_subjects=False):
        """Convert exam category object to dictionary"""
        result = {
            'id': self.id,
            'course_name': self.course_name,
            'description': self.description,
            'amount': float(self.amount) if self.amount else 0.00,
            'offer_amount': float(self.offer_amount) if self.offer_amount else 0.00,
            'max_tokens': self.max_tokens or 0,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'subjects_count': len(self.subjects) if self.subjects else 0
        }
        
        if include_subjects:
            result['subjects'] = [subject.to_dict() for subject in self.subjects]
            
        return result
    
    def __repr__(self):
        return f'<ExamCategory {self.course_name}>'


class ExamCategorySubject(db.Model):
    """Model for subjects within exam categories"""
    __tablename__ = 'exam_category_subjects'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    exam_category_id = db.Column(db.Integer, db.ForeignKey('exam_category.id'), nullable=False)
    subject_name = db.Column(db.String(100), nullable=False)

    # Pricing fields for individual subjects
    amount = db.Column(db.Numeric(10, 2), nullable=True, default=0.00)  # Regular price
    offer_amount = db.Column(db.Numeric(10, 2), nullable=True, default=0.00)  # Discounted price

    # AI Token limits for subject-specific purchases
    max_tokens = db.Column(db.Integer, nullable=True, default=100)  # Default tokens for subject purchase

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Add unique constraint to prevent duplicate subjects in same category
    __table_args__ = (db.UniqueConstraint('exam_category_id', 'subject_name', name='unique_subject_per_category'),)
    
    def to_dict(self):
        """Convert subject object to dictionary"""
        return {
            'id': self.id,
            'exam_category_id': self.exam_category_id,
            'subject_name': self.subject_name,
            'amount': float(self.amount) if self.amount else 0.00,
            'offer_amount': float(self.offer_amount) if self.offer_amount else 0.00,
            'max_tokens': self.max_tokens or 100,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def __repr__(self):
        return f'<ExamCategorySubject {self.subject_name}>'
