"""
Integration tests for complete user flows and system interactions
"""

import pytest
import json
import time
from unittest.mock import patch

from shared.models.user import User
from shared.models.course import ExamCategory, ExamCategorySubject
from shared.models.purchase import ExamCategoryPurchase, TestAttempt
from tests.conftest import assert_success_response, assert_error_response


class TestCompleteUserFlow:
    """Test complete user registration to course purchase flow"""
    
    def test_complete_registration_to_purchase_flow(self, client, db_session, mock_email_service, sample_course, sample_subject):
        """Test complete flow from registration to course purchase"""
        
        # Step 1: Request OTP
        email = 'integration@example.com'
        response = client.post('/api/auth/otp/request', json={'email': email})
        assert_success_response(response)
        
        # Step 2: Register user
        user_data = {
            'email': email,
            'otp': '123456',
            'password': 'testpassword123',
            'name': 'Integration Test User',
            'mobile_no': '9876543210'
        }
        response = client.post('/api/auth/register', json=user_data)
        data = assert_success_response(response, 201)
        access_token = data['data']['access_token']
        user_id = data['data']['user']['id']
        
        # Step 3: Get user profile
        headers = {'Authorization': f'Bearer {access_token}'}
        response = client.get('/api/auth/profile', headers=headers)
        data = assert_success_response(response)
        assert data['data']['user']['email_id'] == email
        
        # Step 4: Browse courses
        response = client.get('/api/courses')
        data = assert_success_response(response)
        assert len(data['data']['courses']) >= 1
        
        # Step 5: Get course subjects
        response = client.get(f'/api/subjects?course_id={sample_course.id}')
        data = assert_success_response(response)
        assert len(data['data']['subjects']) >= 1
        
        # Step 6: Purchase subject
        purchase_data = {
            'courseId': str(sample_course.id),
            'subjectId': str(sample_subject.id),
            'paymentMethod': 'local_dev'
        }
        response = client.post('/api/purchases', headers=headers, json=purchase_data)
        data = assert_success_response(response, 201)
        assert data['data']['instant_access'] is True
        
        # Step 7: Verify purchase in database
        purchase = db_session.query(ExamCategoryPurchase).filter_by(
            user_id=user_id,
            subject_id=sample_subject.id
        ).first()
        assert purchase is not None
        assert purchase.status == 'active'
    
    def test_admin_course_management_flow(self, client, db_session, mock_email_service):
        """Test complete admin course management flow"""
        
        # Step 1: Create admin user
        response = client.post('/api/create-test-user', json={'suffix': 'admin'})
        data = assert_success_response(response)
        admin_token = data['data']['access_token']
        admin_headers = {'Authorization': f'Bearer {admin_token}'}
        
        # Step 2: Create course
        course_data = {
            'course_name': 'Integration Test Course',
            'description': 'Course created during integration testing',
            'amount': 1299.00,
            'offer_amount': 999.00,
            'max_tokens': 1500
        }
        response = client.post('/api/admin/courses', headers=admin_headers, json=course_data)
        data = assert_success_response(response, 201)
        course_id = data['data']['course']['id']
        
        # Step 3: Create subjects for the course
        subject_data = {
            'course_id': course_id,
            'subject_name': 'Integration Test Subject',
            'amount': 399.00,
            'offer_amount': 299.00,
            'max_tokens': 300,
            'total_mock': 30,
            'is_bundle': False
        }
        response = client.post('/api/admin/subjects', headers=admin_headers, json=subject_data)
        data = assert_success_response(response, 201)
        subject_id = data['data']['subject']['id']
        
        # Step 4: Create bundle
        bundle_data = {
            'course_id': course_id,
            'subject_name': 'Complete Integration Bundle',
            'amount': 1299.00,
            'offer_amount': 999.00,
            'max_tokens': 1500,
            'total_mock': 100,
            'is_bundle': True
        }
        response = client.post('/api/admin/subjects', headers=admin_headers, json=bundle_data)
        data = assert_success_response(response, 201)
        bundle_id = data['data']['subject']['id']
        
        # Step 5: Verify course structure
        response = client.get(f'/api/courses/{course_id}?include_subjects=true')
        data = assert_success_response(response)
        course = data['data']['course']
        assert len(course['subjects']) == 2  # Regular subject + bundle
        
        # Step 6: Get bundles separately
        response = client.get(f'/api/bundles?course_id={course_id}')
        data = assert_success_response(response)
        bundles = data['data']['bundles']
        assert len(bundles) == 1
        assert bundles[0]['is_bundle'] is True
        
        # Step 7: Update course
        update_data = {
            'course_name': 'Updated Integration Course',
            'offer_amount': 799.00
        }
        response = client.put(f'/api/admin/courses/{course_id}', 
                            headers=admin_headers, json=update_data)
        data = assert_success_response(response)
        assert data['data']['course']['course_name'] == update_data['course_name']
        
        # Step 8: Soft delete subject
        response = client.put(f'/api/admin/subjects/{subject_id}', 
                            headers=admin_headers, json={'is_deleted': True})
        data = assert_success_response(response)
        assert data['data']['subject']['is_deleted'] is True
        
        # Step 9: Verify deleted subject is hidden
        response = client.get(f'/api/subjects?course_id={course_id}')
        data = assert_success_response(response)
        subjects = data['data']['subjects']
        # Should only show bundle (non-deleted)
        assert len(subjects) == 1
        assert subjects[0]['is_bundle'] is True


class TestAIIntegrationFlow:
    """Test AI services integration flow"""
    
    def test_ai_chat_to_mcq_generation_flow(self, client, auth_headers, mock_ollama_service):
        """Test flow from AI chat to MCQ generation"""
        
        # Step 1: Start AI chat session
        chat_data = {
            'message': 'Explain the concept of photosynthesis in plants',
            'session_id': 'integration_chat_session',
            'is_academic': True
        }
        response = client.post('/api/ai/chat', headers=auth_headers, json=chat_data)
        data = assert_success_response(response)
        assert 'response' in data['data']
        
        # Step 2: Check token usage
        response = client.get('/api/ai/token-status', headers=auth_headers)
        data = assert_success_response(response)
        initial_tokens = data['data']['tokens_used_today']
        assert initial_tokens > 0
        
        # Step 3: Generate MCQ questions
        mcq_data = {
            'num_questions': 3,
            'subject_name': 'Biology',
            'difficulty': 'hard',
            'save_to_database': True
        }
        response = client.post('/api/ai/generate-mcq-from-pdfs', 
                             headers=auth_headers, json=mcq_data)
        data = assert_success_response(response)
        assert len(data['data']['questions']) == 3
        assert data['data']['saved_to_database'] is True
        
        # Step 4: Continue chat in same session
        follow_up_data = {
            'message': 'Can you explain the Calvin cycle in more detail?',
            'session_id': 'integration_chat_session',
            'is_academic': True
        }
        response = client.post('/api/ai/chat', headers=auth_headers, json=follow_up_data)
        data = assert_success_response(response)
        assert data['data']['session_id'] == 'integration_chat_session'
        
        # Step 5: Check updated token usage
        response = client.get('/api/ai/token-status', headers=auth_headers)
        data = assert_success_response(response)
        final_tokens = data['data']['tokens_used_today']
        assert final_tokens > initial_tokens
    
    def test_rag_status_and_dependencies(self, client):
        """Test RAG system status and dependency checking"""
        
        # Step 1: Check RAG status
        response = client.get('/api/ai/rag/status')
        data = assert_success_response(response)
        status_info = data['data']
        
        # Step 2: Verify status structure
        assert 'status' in status_info
        assert 'dependencies' in status_info
        assert 'pdf_count' in status_info
        assert 'last_updated' in status_info
        
        # Step 3: Check dependencies
        dependencies = status_info['dependencies']
        expected_deps = ['ollama', 'embeddings', 'pdf_storage']
        for dep in expected_deps:
            if dep in dependencies:
                assert isinstance(dependencies[dep], bool)


class TestPurchaseAndTestFlow:
    """Test purchase to test taking flow"""
    
    def test_purchase_to_test_attempt_flow(self, client, auth_headers, sample_course, sample_subject, sample_question, db_session):
        """Test complete flow from purchase to test attempt"""
        
        # Step 1: Purchase subject
        purchase_data = {
            'courseId': str(sample_course.id),
            'subjectId': str(sample_subject.id),
            'paymentMethod': 'local_dev'
        }
        response = client.post('/api/purchases', headers=auth_headers, json=purchase_data)
        data = assert_success_response(response, 201)
        purchase_id = data['data']['purchase']['id']
        
        # Step 2: Get available tests
        response = client.get('/api/user/available-tests', headers=auth_headers)
        data = assert_success_response(response)
        available_tests = data['data']['available_tests']
        assert len(available_tests) >= 1
        
        # Step 3: Start test attempt
        test_data = {
            'purchase_id': purchase_id,
            'subject_id': sample_subject.id,
            'num_questions': 1
        }
        response = client.post('/api/user/start-test', headers=auth_headers, json=test_data)
        data = assert_success_response(response, 201)
        attempt_id = data['data']['test_attempt']['id']
        
        # Step 4: Submit test answers
        answer_data = {
            'test_attempt_id': attempt_id,
            'answers': [
                {
                    'question_id': sample_question.id,
                    'user_answer': 'B',
                    'time_taken': 30
                }
            ]
        }
        response = client.post('/api/user/submit-test', headers=auth_headers, json=answer_data)
        data = assert_success_response(response)
        
        # Step 5: Get test results
        response = client.get(f'/api/user/test-results/{attempt_id}', headers=auth_headers)
        data = assert_success_response(response)
        results = data['data']['results']
        assert 'total_questions' in results
        assert 'correct_answers' in results
        assert 'percentage' in results
        
        # Step 6: Verify test attempt in database
        attempt = db_session.query(TestAttempt).filter_by(id=attempt_id).first()
        assert attempt is not None
        assert attempt.status == 'completed'


class TestCommunityIntegrationFlow:
    """Test community features integration"""
    
    def test_blog_post_creation_and_interaction_flow(self, client, auth_headers, db_session):
        """Test complete blog post creation and interaction flow"""
        
        # Step 1: Create blog post
        post_data = {
            'title': 'Integration Test: Study Tips for Physics',
            'content': 'Here are some effective study tips for physics that I have learned...',
            'tags': ['physics', 'study-tips', 'education']
        }
        response = client.post('/api/community/posts', headers=auth_headers, json=post_data)
        data = assert_success_response(response, 201)
        post_id = data['data']['post']['id']
        
        # Step 2: Get all blog posts
        response = client.get('/api/community/posts')
        data = assert_success_response(response)
        posts = data['data']['posts']
        assert len(posts) >= 1
        
        # Step 3: Like the post
        response = client.post(f'/api/community/posts/{post_id}/like', headers=auth_headers)
        data = assert_success_response(response)
        assert 'liked successfully' in data['message'].lower()
        
        # Step 4: Add comment
        comment_data = {
            'content': 'Great tips! Thanks for sharing this valuable information.'
        }
        response = client.post(f'/api/community/posts/{post_id}/comment', 
                             headers=auth_headers, json=comment_data)
        data = assert_success_response(response, 201)
        
        # Step 5: Get post with interactions
        response = client.get(f'/api/community/posts/{post_id}')
        data = assert_success_response(response)
        post = data['data']['post']
        assert post['likes_count'] >= 1
        assert post['comments_count'] >= 1
        
        # Step 6: Unlike the post
        response = client.delete(f'/api/community/posts/{post_id}/like', headers=auth_headers)
        data = assert_success_response(response)
        assert 'unliked successfully' in data['message'].lower()


class TestErrorHandlingIntegration:
    """Test error handling across integrated flows"""
    
    def test_authentication_error_propagation(self, client, sample_course):
        """Test that authentication errors are properly handled across endpoints"""
        
        # Test various endpoints without authentication
        endpoints_to_test = [
            ('GET', '/api/auth/profile'),
            ('POST', '/api/ai/chat'),
            ('GET', '/api/ai/token-status'),
            ('POST', '/api/purchases'),
            ('POST', '/api/community/posts'),
            ('POST', '/api/admin/courses')
        ]
        
        for method, endpoint in endpoints_to_test:
            if method == 'GET':
                response = client.get(endpoint)
            else:
                response = client.post(endpoint, json={})
            
            assert response.status_code == 401
            data = response.get_json()
            assert data['success'] is False
    
    def test_authorization_error_propagation(self, client, auth_headers):
        """Test that authorization errors are properly handled"""
        
        # Test admin endpoints with regular user
        admin_endpoints = [
            ('POST', '/api/admin/courses'),
            ('PUT', '/api/admin/courses/1'),
            ('DELETE', '/api/admin/courses/1'),
            ('POST', '/api/admin/subjects'),
            ('PUT', '/api/admin/subjects/1')
        ]
        
        for method, endpoint in admin_endpoints:
            if method == 'POST':
                response = client.post(endpoint, headers=auth_headers, json={})
            elif method == 'PUT':
                response = client.put(endpoint, headers=auth_headers, json={})
            else:
                response = client.delete(endpoint, headers=auth_headers)
            
            assert response.status_code == 403
            data = response.get_json()
            assert data['success'] is False
    
    def test_validation_error_consistency(self, client, auth_headers, admin_auth_headers):
        """Test that validation errors are consistent across endpoints"""
        
        # Test various endpoints with invalid data
        test_cases = [
            ('POST', '/api/auth/register', {'email': 'invalid-email'}),
            ('POST', '/api/admin/courses', {'course_name': ''}, admin_auth_headers),
            ('POST', '/api/admin/subjects', {'subject_name': ''}, admin_auth_headers),
            ('POST', '/api/ai/chat', {'message': ''}, auth_headers),
            ('POST', '/api/community/posts', {'title': ''}, auth_headers)
        ]
        
        for method, endpoint, invalid_data, *headers in test_cases:
            headers = headers[0] if headers else {}
            response = client.post(endpoint, headers=headers, json=invalid_data)
            
            assert response.status_code == 400
            data = response.get_json()
            assert data['success'] is False
            assert 'error' in data or 'message' in data


class TestPerformanceIntegration:
    """Test performance aspects of integrated flows"""
    
    def test_concurrent_user_simulation(self, client, mock_email_service, mock_ollama_service):
        """Simulate multiple users performing actions concurrently"""
        
        # Create multiple test users
        users = []
        for i in range(3):
            response = client.post('/api/create-test-user', json={'suffix': str(i)})
            if response.status_code == 200:
                data = response.get_json()
                users.append({
                    'token': data['data']['access_token'],
                    'user_id': data['data']['user']['id']
                })
        
        assert len(users) >= 2  # At least 2 users created successfully
        
        # Each user performs AI chat
        for i, user in enumerate(users):
            headers = {'Authorization': f'Bearer {user["token"]}'}
            chat_data = {
                'message': f'User {i} asking about physics concepts',
                'session_id': f'concurrent_session_{i}',
                'is_academic': True
            }
            response = client.post('/api/ai/chat', headers=headers, json=chat_data)
            assert_success_response(response)
    
    def test_database_transaction_integrity(self, client, auth_headers, sample_course, sample_subject):
        """Test database transaction integrity during complex operations"""
        
        # Perform multiple related operations
        purchase_data = {
            'courseId': str(sample_course.id),
            'subjectId': str(sample_subject.id),
            'paymentMethod': 'local_dev'
        }
        
        # Multiple purchase attempts (should handle duplicates gracefully)
        responses = []
        for _ in range(3):
            response = client.post('/api/purchases', headers=auth_headers, json=purchase_data)
            responses.append(response)
        
        # First should succeed, others should handle gracefully
        success_count = sum(1 for r in responses if r.status_code in [200, 201])
        assert success_count >= 1  # At least one should succeed
