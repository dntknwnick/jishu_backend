"""
Pytest configuration and fixtures for Jishu Backend tests
"""

import pytest
import os
import sys
from datetime import datetime, timedelta

# Add the parent directory to the path so we can import our app
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app
from shared.models.user import db, User
from shared.models.course import ExamCategory, ExamCategorySubject
from shared.models.purchase import ExamCategoryPurchase, ExamCategoryQuestion
from shared.models.community import BlogPost, AIChatHistory, UserAIStats

@pytest.fixture(scope='session')
def test_app():
    """Create and configure a test Flask application"""
    # Set test configuration
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'  # In-memory database for tests
    app.config['JWT_SECRET_KEY'] = 'test-jwt-secret-key'
    app.config['SECRET_KEY'] = 'test-secret-key'
    app.config['WTF_CSRF_ENABLED'] = False
    
    # Create application context
    with app.app_context():
        # Create all tables
        db.create_all()
        yield app
        # Clean up
        db.drop_all()

@pytest.fixture(scope='function')
def client(test_app):
    """Create a test client for the Flask application"""
    return test_app.test_client()

@pytest.fixture(scope='function')
def app_context(test_app):
    """Create an application context for tests"""
    with test_app.app_context():
        yield test_app

@pytest.fixture(scope='function')
def db_session(app_context):
    """Create a database session for tests"""
    # Create fresh tables for each test
    db.create_all()
    yield db.session
    # Clean up after each test
    db.session.rollback()
    db.drop_all()

@pytest.fixture
def sample_user(db_session):
    """Create a sample user for testing"""
    user = User(
        mobile_no='9876543210',
        email_id='test@example.com',
        name='Test User',
        is_premium=False,
        is_admin=False,
        color_theme='light',
        otp_verified=True,
        status='active',
        source='manual',
        auth_provider='manual'
    )
    user.set_password('testpassword123')
    db_session.add(user)
    db_session.commit()
    return user

@pytest.fixture
def admin_user(db_session):
    """Create an admin user for testing"""
    user = User(
        mobile_no='9999999999',
        email_id='admin@example.com',
        name='Admin User',
        is_premium=True,
        is_admin=True,
        color_theme='dark',
        otp_verified=True,
        status='active',
        source='manual',
        auth_provider='manual'
    )
    user.set_password('adminpassword123')
    db_session.add(user)
    db_session.commit()
    return user

@pytest.fixture
def sample_course(db_session):
    """Create a sample course for testing"""
    course = ExamCategory(
        course_name='Test Physics Course',
        description='A comprehensive physics course for testing',
        amount=999.00,
        offer_amount=799.00,
        max_tokens=1000
    )
    db_session.add(course)
    db_session.commit()
    return course

@pytest.fixture
def sample_subject(db_session, sample_course):
    """Create a sample subject for testing"""
    subject = ExamCategorySubject(
        exam_category_id=sample_course.id,
        subject_name='Mechanics',
        amount=299.00,
        offer_amount=199.00,
        max_tokens=200,
        total_mock=25,
        is_deleted=False,
        is_bundle=False
    )
    db_session.add(subject)
    db_session.commit()
    return subject

@pytest.fixture
def sample_bundle(db_session, sample_course):
    """Create a sample bundle for testing"""
    bundle = ExamCategorySubject(
        exam_category_id=sample_course.id,
        subject_name='Complete Physics Bundle',
        amount=999.00,
        offer_amount=799.00,
        max_tokens=1000,
        total_mock=100,
        is_deleted=False,
        is_bundle=True
    )
    db_session.add(bundle)
    db_session.commit()
    return bundle

@pytest.fixture
def sample_purchase(db_session, sample_user, sample_course, sample_subject):
    """Create a sample purchase for testing"""
    purchase = ExamCategoryPurchase(
        user_id=sample_user.id,
        exam_category_id=sample_course.id,
        subject_id=sample_subject.id,
        cost=199.00,
        total_mock_tests=25,
        mock_tests_used=0,
        status='active'
    )
    db_session.add(purchase)
    db_session.commit()
    return purchase

@pytest.fixture
def sample_question(db_session, sample_course, sample_subject):
    """Create a sample question for testing"""
    question = ExamCategoryQuestion(
        exam_category_id=sample_course.id,
        subject_id=sample_subject.id,
        question='What is Newton\'s first law of motion?',
        option_a='Force equals mass times acceleration',
        option_b='An object at rest stays at rest unless acted upon by a force',
        option_c='For every action there is an equal and opposite reaction',
        option_d='Energy cannot be created or destroyed',
        correct_answer='B',
        explanation='Newton\'s first law states that an object at rest stays at rest...',
        difficulty_level='medium',
        is_ai_generated=False
    )
    db_session.add(question)
    db_session.commit()
    return question

@pytest.fixture
def sample_blog_post(db_session, sample_user):
    """Create a sample blog post for testing"""
    post = BlogPost(
        user_id=sample_user.id,
        title='Understanding Physics Concepts',
        content='This post explains fundamental physics concepts...',
        tags='physics,education,science',
        likes_count=0,
        comments_count=0,
        is_featured=False,
        is_deleted=False,
        status='published'
    )
    db_session.add(post)
    db_session.commit()
    return post

@pytest.fixture
def auth_headers(client, sample_user):
    """Get authentication headers for API requests"""
    # Login to get JWT token
    response = client.post('/api/create-test-user', json={'suffix': '1'})
    if response.status_code == 200:
        data = response.get_json()
        access_token = data['data']['access_token']
        return {'Authorization': f'Bearer {access_token}'}
    return {}

@pytest.fixture
def admin_auth_headers(client, admin_user):
    """Get admin authentication headers for API requests"""
    # Create admin test user
    response = client.post('/api/create-test-user', json={'suffix': 'admin'})
    if response.status_code == 200:
        data = response.get_json()
        access_token = data['data']['access_token']
        return {'Authorization': f'Bearer {access_token}'}
    return {}

# Test data generators
@pytest.fixture
def valid_user_data():
    """Valid user registration data"""
    return {
        'email': 'newuser@example.com',
        'otp': '123456',
        'password': 'securepassword123',
        'name': 'New User',
        'mobile_no': '9876543210'
    }

@pytest.fixture
def valid_course_data():
    """Valid course creation data"""
    return {
        'course_name': 'Advanced Mathematics',
        'description': 'Comprehensive mathematics course',
        'amount': 1299.00,
        'offer_amount': 999.00,
        'max_tokens': 1500
    }

@pytest.fixture
def valid_subject_data():
    """Valid subject creation data"""
    return {
        'subject_name': 'Calculus',
        'amount': 399.00,
        'offer_amount': 299.00,
        'max_tokens': 300,
        'total_mock': 30,
        'is_bundle': False
    }

@pytest.fixture
def valid_blog_post_data():
    """Valid blog post creation data"""
    return {
        'title': 'Study Tips for Physics',
        'content': 'Here are some effective study tips for physics...',
        'tags': ['physics', 'study-tips', 'education']
    }

@pytest.fixture
def valid_mcq_data():
    """Valid MCQ generation data"""
    return {
        'content': 'Photosynthesis is the process by which plants convert light energy into chemical energy.',
        'num_questions': 2,
        'subject_name': 'Biology',
        'difficulty': 'medium',
        'save_to_database': False
    }

# Mock external services
@pytest.fixture
def mock_ollama_service(monkeypatch):
    """Mock Ollama AI service for testing"""
    def mock_generate_response(*args, **kwargs):
        return {
            'response': 'This is a mock AI response for testing purposes.',
            'tokens_used': 10,
            'response_time': 0.5
        }
    
    def mock_generate_mcq(*args, **kwargs):
        return [
            {
                'question': 'What is photosynthesis?',
                'options': {
                    'A': 'Respiration in plants',
                    'B': 'Conversion of light to chemical energy',
                    'C': 'Water absorption',
                    'D': 'Root growth'
                },
                'correct_answer': 'B',
                'explanation': 'Photosynthesis converts light energy to chemical energy.'
            }
        ]
    
    monkeypatch.setattr('shared.services.ai_service.generate_ai_response', mock_generate_response)
    monkeypatch.setattr('shared.services.ai_service.generate_mcq_questions', mock_generate_mcq)

@pytest.fixture
def mock_email_service(monkeypatch):
    """Mock email service for testing"""
    def mock_send_otp(*args, **kwargs):
        return True
    
    monkeypatch.setattr('shared.services.email_service.send_otp_email', mock_send_otp)

# Test utilities
def assert_success_response(response, expected_status=200):
    """Assert that response is successful"""
    assert response.status_code == expected_status
    data = response.get_json()
    assert data is not None
    assert data.get('success') is True
    return data

def assert_error_response(response, expected_status=400):
    """Assert that response is an error"""
    assert response.status_code == expected_status
    data = response.get_json()
    assert data is not None
    assert data.get('success') is False
    return data
