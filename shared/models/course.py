from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from .user import db

class ExamCategory(db.Model):
    """Model for exam categories/courses"""
    __tablename__ = 'exam_category'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    course_name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
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
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def __repr__(self):
        return f'<ExamCategorySubject {self.subject_name}>'
