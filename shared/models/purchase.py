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
    total_marks = db.Column(db.Integer, nullable=True)
    marks_scored = db.Column(db.Integer, default=0)

    # Mock test tracking (legacy - kept for backward compatibility)
    total_mock_tests = db.Column(db.Integer, default=0)  # Total mock tests purchased
    mock_tests_used = db.Column(db.Integer, default=0)   # Mock tests already taken

    # New purchase type tracking
    purchase_type = db.Column(db.Enum('single_subject', 'multiple_subjects', 'full_bundle'), default='single_subject')
    subjects_included = db.Column(db.JSON, nullable=True)  # List of subject IDs for multiple subject purchases
    chatbot_tokens_unlimited = db.Column(db.Boolean, default=False)  # Whether user has unlimited chatbot tokens

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
            'total_marks': self.total_marks,
            'marks_scored': self.marks_scored,
            'total_mock_tests': self.total_mock_tests or 0,
            'mock_tests_used': self.mock_tests_used or 0,
            'available_mock_tests': (self.total_mock_tests or 0) - (self.mock_tests_used or 0),
            'purchase_type': self.purchase_type,
            'subjects_included': self.subjects_included,
            'chatbot_tokens_unlimited': self.chatbot_tokens_unlimited,
            'purchase_date': self.purchase_date.isoformat() if self.purchase_date else None,
            'last_attempt_date': self.last_attempt_date.isoformat() if self.last_attempt_date else None,
            'status': self.status,
            'exam_category_name': self.exam_category.course_name if self.exam_category else None,
            'subject_name': self.subject.subject_name if self.subject else None
        }

    @property
    def is_bundle_purchase(self):
        """Check if this is a full bundle purchase"""
        return self.purchase_type == 'full_bundle'

    @property
    def is_multiple_subjects(self):
        """Check if this is a multiple subjects purchase"""
        return self.purchase_type == 'multiple_subjects'

    def get_included_subjects(self):
        """Get list of subject IDs included in this purchase"""
        if self.purchase_type == 'single_subject':
            return [self.subject_id] if self.subject_id else []
        elif self.purchase_type == 'multiple_subjects':
            return self.subjects_included or []
        elif self.purchase_type == 'full_bundle':
            # Return all subjects for this course
            from .course import ExamCategorySubject
            subjects = ExamCategorySubject.query.filter_by(
                exam_category_id=self.exam_category_id,
                is_deleted=False
            ).all()
            return [s.id for s in subjects]
        return []
    
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

    # Link to specific mock test attempt (NEW)
    mock_test_id = db.Column(db.Integer, db.ForeignKey('mock_test_attempts.id'), nullable=True)

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
    mock_test = db.relationship('MockTestAttempt', backref='questions')
    
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


class MockTestAttempt(db.Model):
    """Model for individual mock test cards with re-attempt logic"""
    __tablename__ = 'mock_test_attempts'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    purchase_id = db.Column(db.Integer, db.ForeignKey('exam_category_purchase.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('exam_category.id'), nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey('exam_category_subjects.id'), nullable=False)

    # Test card identification
    test_number = db.Column(db.Integer, nullable=False)  # 1-50 for each subject

    # Re-attempt tracking
    max_attempts = db.Column(db.Integer, default=3)  # Maximum allowed attempts
    attempts_used = db.Column(db.Integer, default=0)  # Number of attempts used

    # Question management
    questions_generated = db.Column(db.Boolean, default=False)  # Whether MCQs have been generated
    total_questions = db.Column(db.Integer, default=50)  # Always 50 MCQs per test

    # Latest attempt results (only these count for analytics)
    latest_score = db.Column(db.Integer, default=0)
    latest_percentage = db.Column(db.Numeric(5, 2), default=0.00)
    latest_time_taken = db.Column(db.Integer, default=0)  # in seconds
    latest_attempt_date = db.Column(db.DateTime, nullable=True)

    # First attempt results (for comparison)
    first_attempt_score = db.Column(db.Integer, default=0)
    first_attempt_date = db.Column(db.DateTime, nullable=True)

    # Status tracking
    status = db.Column(db.Enum('available', 'in_progress', 'completed', 'disabled'), default='available')

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    purchase = db.relationship('ExamCategoryPurchase', backref='mock_tests')
    user = db.relationship('User', backref='mock_test_attempts')
    course = db.relationship('ExamCategory', backref='mock_test_attempts')
    subject = db.relationship('ExamCategorySubject', backref='mock_test_attempts')

    # Unique constraint: one test card per test number per purchase
    __table_args__ = (db.UniqueConstraint('purchase_id', 'test_number', name='unique_test_per_purchase'),)

    @property
    def is_available(self):
        """Check if test card is available for attempt"""
        return self.attempts_used < self.max_attempts and self.status != 'disabled'

    @property
    def remaining_attempts(self):
        """Get remaining attempts for this test card"""
        return max(0, self.max_attempts - self.attempts_used)

    def to_dict(self):
        """Convert mock test attempt object to dictionary"""
        return {
            'id': self.id,
            'purchase_id': self.purchase_id,
            'user_id': self.user_id,
            'course_id': self.course_id,
            'subject_id': self.subject_id,
            'test_number': self.test_number,
            'max_attempts': self.max_attempts,
            'attempts_used': self.attempts_used,
            'remaining_attempts': self.remaining_attempts,
            'questions_generated': self.questions_generated,
            'total_questions': self.total_questions,
            'latest_score': self.latest_score,
            'latest_percentage': float(self.latest_percentage) if self.latest_percentage else 0.0,
            'latest_time_taken': self.latest_time_taken,
            'latest_attempt_date': self.latest_attempt_date.isoformat() if self.latest_attempt_date else None,
            'first_attempt_score': self.first_attempt_score,
            'first_attempt_date': self.first_attempt_date.isoformat() if self.first_attempt_date else None,
            'status': self.status,
            'is_available': self.is_available,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'course_name': self.course.course_name if self.course else None,
            'subject_name': self.subject.subject_name if self.subject else None
        }

    def __repr__(self):
        return f'<MockTestAttempt {self.id}: Test {self.test_number} for Purchase {self.purchase_id}>'


class TestAttemptSession(db.Model):
    """Model for individual test sessions within a mock test attempt"""
    __tablename__ = 'test_attempt_sessions'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    mock_test_id = db.Column(db.Integer, db.ForeignKey('mock_test_attempts.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    # Session details
    attempt_number = db.Column(db.Integer, nullable=False)  # 1, 2, or 3
    score = db.Column(db.Integer, default=0)
    percentage = db.Column(db.Numeric(5, 2), default=0.00)
    time_taken = db.Column(db.Integer, default=0)  # in seconds

    # Question tracking
    correct_answers = db.Column(db.Integer, default=0)
    wrong_answers = db.Column(db.Integer, default=0)
    unanswered = db.Column(db.Integer, default=0)

    # Session status
    status = db.Column(db.Enum('in_progress', 'completed', 'abandoned'), default='in_progress')
    started_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime, nullable=True)

    # Relationships
    mock_test = db.relationship('MockTestAttempt', backref='sessions')
    user = db.relationship('User', backref='test_sessions')

    def to_dict(self):
        """Convert test session object to dictionary"""
        return {
            'id': self.id,
            'mock_test_id': self.mock_test_id,
            'user_id': self.user_id,
            'attempt_number': self.attempt_number,
            'score': self.score,
            'percentage': float(self.percentage) if self.percentage else 0.0,
            'time_taken': self.time_taken,
            'correct_answers': self.correct_answers,
            'wrong_answers': self.wrong_answers,
            'unanswered': self.unanswered,
            'status': self.status,
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None
        }

    def __repr__(self):
        return f'<TestAttemptSession {self.id}: Attempt {self.attempt_number} for MockTest {self.mock_test_id}>'


class TestAnswer(db.Model):
    """Model for test answers"""
    __tablename__ = 'test_answers'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    session_id = db.Column(db.Integer, db.ForeignKey('test_attempt_sessions.id', ondelete='CASCADE'), nullable=False)
    question_id = db.Column(db.Integer, db.ForeignKey('exam_category_questions.id'), nullable=False)
    selected_answer = db.Column(db.String(255), nullable=True)
    is_correct = db.Column(db.Boolean, default=False)
    time_taken = db.Column(db.Integer, default=0)  # in seconds for this question
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    session = db.relationship('TestAttemptSession', backref='answers')
    question = db.relationship('ExamCategoryQuestion', backref='user_answers')

    def to_dict(self):
        """Convert test answer object to dictionary"""
        return {
            'id': self.id,
            'session_id': self.session_id,
            'question_id': self.question_id,
            'selected_answer': self.selected_answer,
            'is_correct': self.is_correct,
            'time_taken': self.time_taken,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

    def __repr__(self):
        return f'<TestAnswer {self.id}>'
