from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from .user import db

class ExamCategoryPurchase(db.Model):
    """Model for exam category purchases"""
    __tablename__ = 'exam_category_purchase'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    exam_category_id = db.Column(db.Integer, db.ForeignKey('exam_category.id'), nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey('exam_category_subjects.id'), nullable=True)
    cost = db.Column(db.Numeric(10, 2), nullable=False)
    no_of_attempts = db.Column(db.Integer, default=3)
    attempts_used = db.Column(db.Integer, default=0)
    total_marks = db.Column(db.Integer, nullable=True)
    marks_scored = db.Column(db.Integer, default=0)
    purchase_date = db.Column(db.DateTime, default=datetime.utcnow)
    last_attempt_date = db.Column(db.DateTime, nullable=True)
    status = db.Column(db.Enum('active', 'completed', 'expired'), default='active')
    
    # Relationships
    user = db.relationship('User', backref='purchases')
    exam_category = db.relationship('ExamCategory', backref='purchases')
    subject = db.relationship('ExamCategorySubject', backref='purchases')
    
    def to_dict(self):
        """Convert purchase object to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'exam_category_id': self.exam_category_id,
            'subject_id': self.subject_id,
            'cost': float(self.cost) if self.cost else 0,
            'no_of_attempts': self.no_of_attempts,
            'attempts_used': self.attempts_used,
            'total_marks': self.total_marks,
            'marks_scored': self.marks_scored,
            'purchase_date': self.purchase_date.isoformat() if self.purchase_date else None,
            'last_attempt_date': self.last_attempt_date.isoformat() if self.last_attempt_date else None,
            'status': self.status,
            'exam_category_name': self.exam_category.course_name if self.exam_category else None,
            'subject_name': self.subject.subject_name if self.subject else None
        }
    
    def __repr__(self):
        return f'<ExamCategoryPurchase {self.id}>'


class ExamCategoryQuestion(db.Model):
    """Model for exam category questions"""
    __tablename__ = 'exam_category_questions'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    exam_category_id = db.Column(db.Integer, db.ForeignKey('exam_category.id'), nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey('exam_category_subjects.id'), nullable=False)
    question = db.Column(db.Text, nullable=False)
    option_1 = db.Column(db.String(255), nullable=False)
    option_2 = db.Column(db.String(255), nullable=False)
    option_3 = db.Column(db.String(255), nullable=False)
    option_4 = db.Column(db.String(255), nullable=False)
    correct_answer = db.Column(db.String(255), nullable=False)
    explanation = db.Column(db.Text, nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    purchased_id = db.Column(db.Integer, db.ForeignKey('exam_category_purchase.id'), nullable=True)

    # AI-related fields
    is_ai_generated = db.Column(db.Boolean, default=False)
    ai_model_used = db.Column(db.String(100), nullable=True)  # e.g., 'llama3.2:1b'
    difficulty_level = db.Column(db.Enum('easy', 'medium', 'hard'), default='medium')
    source_content = db.Column(db.Text, nullable=True)  # Original content used for generation

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    exam_category = db.relationship('ExamCategory', backref='questions')
    subject = db.relationship('ExamCategorySubject', backref='questions')
    user = db.relationship('User', backref='created_questions')
    purchase = db.relationship('ExamCategoryPurchase', backref='questions')
    
    def to_dict(self, include_answer=False):
        """Convert question object to dictionary"""
        result = {
            'id': self.id,
            'exam_category_id': self.exam_category_id,
            'subject_id': self.subject_id,
            'question': self.question,
            'option_1': self.option_1,
            'option_2': self.option_2,
            'option_3': self.option_3,
            'option_4': self.option_4,
            'explanation': self.explanation,
            'is_ai_generated': self.is_ai_generated,
            'ai_model_used': self.ai_model_used,
            'difficulty_level': self.difficulty_level,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

        if include_answer:
            result['correct_answer'] = self.correct_answer

        return result
    
    def __repr__(self):
        return f'<ExamCategoryQuestion {self.id}>'


class TestAttempt(db.Model):
    """Model for test attempts"""
    __tablename__ = 'test_attempts'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    purchase_id = db.Column(db.Integer, db.ForeignKey('exam_category_purchase.id'), nullable=False)
    exam_category_id = db.Column(db.Integer, db.ForeignKey('exam_category.id'), nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey('exam_category_subjects.id'), nullable=True)
    total_questions = db.Column(db.Integer, nullable=False)
    correct_answers = db.Column(db.Integer, default=0)
    wrong_answers = db.Column(db.Integer, default=0)
    unanswered = db.Column(db.Integer, default=0)
    total_marks = db.Column(db.Integer, nullable=False)
    marks_scored = db.Column(db.Integer, default=0)
    percentage = db.Column(db.Numeric(5, 2), default=0.00)
    time_taken = db.Column(db.Integer, default=0)  # in seconds
    started_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime, nullable=True)
    status = db.Column(db.Enum('in_progress', 'completed', 'abandoned'), default='in_progress')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', backref='test_attempts')
    purchase = db.relationship('ExamCategoryPurchase', backref='test_attempts')
    exam_category = db.relationship('ExamCategory', backref='test_attempts')
    subject = db.relationship('ExamCategorySubject', backref='test_attempts')
    
    def to_dict(self):
        """Convert test attempt object to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'purchase_id': self.purchase_id,
            'exam_category_id': self.exam_category_id,
            'subject_id': self.subject_id,
            'total_questions': self.total_questions,
            'correct_answers': self.correct_answers,
            'wrong_answers': self.wrong_answers,
            'unanswered': self.unanswered,
            'total_marks': self.total_marks,
            'marks_scored': self.marks_scored,
            'percentage': float(self.percentage) if self.percentage else 0.0,
            'time_taken': self.time_taken,
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'exam_category_name': self.exam_category.course_name if self.exam_category else None,
            'subject_name': self.subject.subject_name if self.subject else None
        }
    
    def __repr__(self):
        return f'<TestAttempt {self.id}>'


class TestAnswer(db.Model):
    """Model for test answers"""
    __tablename__ = 'test_answers'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    attempt_id = db.Column(db.Integer, db.ForeignKey('test_attempts.id', ondelete='CASCADE'), nullable=False)
    question_id = db.Column(db.Integer, db.ForeignKey('exam_category_questions.id'), nullable=False)
    selected_answer = db.Column(db.String(255), nullable=True)
    is_correct = db.Column(db.Boolean, default=False)
    time_taken = db.Column(db.Integer, default=0)  # in seconds for this question
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    attempt = db.relationship('TestAttempt', backref='answers')
    question = db.relationship('ExamCategoryQuestion', backref='user_answers')
    
    def to_dict(self):
        """Convert test answer object to dictionary"""
        return {
            'id': self.id,
            'attempt_id': self.attempt_id,
            'question_id': self.question_id,
            'selected_answer': self.selected_answer,
            'is_correct': self.is_correct,
            'time_taken': self.time_taken,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    def __repr__(self):
        return f'<TestAnswer {self.id}>'
