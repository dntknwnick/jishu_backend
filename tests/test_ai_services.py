"""
Unit tests for AI services endpoints and functionality
"""

import pytest
import json
from unittest.mock import patch, MagicMock

from shared.models.community import AIChatHistory, UserAIStats
from shared.models.purchase import ExamCategoryQuestion
from tests.conftest import assert_success_response, assert_error_response


class TestAIChatEndpoints:
    """Test AI chat functionality"""
    
    def test_ai_chat_authenticated(self, client, auth_headers, mock_ollama_service):
        """Test AI chat with authenticated user"""
        chat_data = {
            'message': 'Explain photosynthesis',
            'session_id': 'test_session_123',
            'is_academic': True
        }
        
        response = client.post('/api/ai/chat', 
                             headers=auth_headers, json=chat_data)
        
        data = assert_success_response(response)
        assert 'response' in data['data']
        assert 'session_id' in data['data']
        assert 'token_info' in data['data']
        assert data['data']['session_id'] == chat_data['session_id']
    
    def test_ai_chat_unauthenticated(self, client):
        """Test AI chat without authentication"""
        chat_data = {
            'message': 'Test message',
            'session_id': 'test_session',
            'is_academic': True
        }
        
        response = client.post('/api/ai/chat', json=chat_data)
        
        assert_error_response(response, 401)
    
    def test_ai_chat_missing_message(self, client, auth_headers):
        """Test AI chat with missing message"""
        chat_data = {
            'session_id': 'test_session',
            'is_academic': True
        }
        
        response = client.post('/api/ai/chat', 
                             headers=auth_headers, json=chat_data)
        
        assert_error_response(response, 400)
    
    def test_ai_chat_empty_message(self, client, auth_headers):
        """Test AI chat with empty message"""
        chat_data = {
            'message': '',
            'session_id': 'test_session',
            'is_academic': True
        }
        
        response = client.post('/api/ai/chat', 
                             headers=auth_headers, json=chat_data)
        
        assert_error_response(response, 400)
    
    def test_ai_chat_token_tracking(self, client, auth_headers, mock_ollama_service, db_session):
        """Test that AI chat tracks token usage"""
        chat_data = {
            'message': 'Test message for token tracking',
            'session_id': 'token_test_session',
            'is_academic': True
        }
        
        response = client.post('/api/ai/chat', 
                             headers=auth_headers, json=chat_data)
        
        data = assert_success_response(response)
        token_info = data['data']['token_info']
        assert 'tokens_used_today' in token_info
        assert 'daily_limit' in token_info
        assert 'remaining_tokens' in token_info
        assert token_info['tokens_used_today'] > 0
    
    @patch('shared.services.ai_service.generate_ai_response')
    def test_ai_chat_service_error(self, mock_ai, client, auth_headers):
        """Test AI chat when service is unavailable"""
        mock_ai.side_effect = Exception("AI service unavailable")
        
        chat_data = {
            'message': 'Test message',
            'session_id': 'error_test',
            'is_academic': True
        }
        
        response = client.post('/api/ai/chat', 
                             headers=auth_headers, json=chat_data)
        
        assert_error_response(response, 500)


class TestTokenStatusEndpoint:
    """Test AI token status functionality"""
    
    def test_token_status_authenticated(self, client, auth_headers):
        """Test getting token status with authenticated user"""
        response = client.get('/api/ai/token-status', headers=auth_headers)
        
        data = assert_success_response(response)
        token_info = data['data']
        assert 'tokens_used_today' in token_info
        assert 'daily_limit' in token_info
        assert 'remaining_tokens' in token_info
        assert 'reset_time' in token_info
    
    def test_token_status_unauthenticated(self, client):
        """Test getting token status without authentication"""
        response = client.get('/api/ai/token-status')
        
        assert_error_response(response, 401)


class TestMCQGeneration:
    """Test MCQ generation functionality"""
    
    def test_mcq_generation_from_pdfs(self, client, auth_headers, mock_ollama_service):
        """Test MCQ generation from PDFs"""
        mcq_data = {
            'num_questions': 2,
            'subject_name': 'Physics',
            'difficulty': 'hard',
            'save_to_database': False
        }
        
        response = client.post('/api/ai/generate-mcq-from-pdfs', 
                             headers=auth_headers, json=mcq_data)
        
        data = assert_success_response(response)
        assert 'questions' in data['data']
        assert 'total_generated' in data['data']
        assert 'subject_name' in data['data']
        assert 'difficulty' in data['data']
        assert data['data']['total_generated'] == mcq_data['num_questions']
        assert data['data']['difficulty'] == 'hard'  # Should be forced to hard
    
    def test_mcq_generation_save_to_database(self, client, auth_headers, mock_ollama_service, db_session):
        """Test MCQ generation with database saving"""
        mcq_data = {
            'num_questions': 1,
            'subject_name': 'Biology',
            'difficulty': 'medium',  # Should be overridden to hard
            'save_to_database': True
        }
        
        response = client.post('/api/ai/generate-mcq-from-pdfs', 
                             headers=auth_headers, json=mcq_data)
        
        data = assert_success_response(response)
        assert data['data']['saved_to_database'] is True
        
        # Verify questions were saved to database
        questions = db_session.query(ExamCategoryQuestion).filter_by(
            is_ai_generated=True
        ).all()
        assert len(questions) >= 1
    
    def test_mcq_generation_invalid_num_questions(self, client, auth_headers):
        """Test MCQ generation with invalid number of questions"""
        test_cases = [
            (0, 'Zero questions'),
            (-1, 'Negative questions'),
            (101, 'Too many questions'),
            ('invalid', 'Invalid type')
        ]
        
        for num_questions, description in test_cases:
            mcq_data = {
                'num_questions': num_questions,
                'subject_name': 'Physics',
                'difficulty': 'hard',
                'save_to_database': False
            }
            
            response = client.post('/api/ai/generate-mcq-from-pdfs', 
                                 headers=auth_headers, json=mcq_data)
            
            assert_error_response(response, 400)
    
    def test_mcq_generation_missing_subject(self, client, auth_headers):
        """Test MCQ generation without subject name"""
        mcq_data = {
            'num_questions': 2,
            'difficulty': 'hard',
            'save_to_database': False
        }
        
        response = client.post('/api/ai/generate-mcq-from-pdfs', 
                             headers=auth_headers, json=mcq_data)
        
        assert_error_response(response, 400)
    
    def test_mcq_generation_duplicate_protection(self, client, auth_headers, mock_ollama_service):
        """Test MCQ generation duplicate request protection"""
        mcq_data = {
            'num_questions': 1,
            'subject_name': 'Physics',
            'difficulty': 'hard',
            'save_to_database': False
        }
        
        # First request should succeed
        response1 = client.post('/api/ai/generate-mcq-from-pdfs', 
                              headers=auth_headers, json=mcq_data)
        assert_success_response(response1)
        
        # Second request immediately should be blocked
        response2 = client.post('/api/ai/generate-mcq-from-pdfs', 
                              headers=auth_headers, json=mcq_data)
        assert_error_response(response2, 429)
    
    def test_mcq_generation_unauthenticated(self, client):
        """Test MCQ generation without authentication"""
        mcq_data = {
            'num_questions': 2,
            'subject_name': 'Physics',
            'difficulty': 'hard',
            'save_to_database': False
        }
        
        response = client.post('/api/ai/generate-mcq-from-pdfs', json=mcq_data)
        
        assert_error_response(response, 401)
    
    @patch('shared.services.ai_service.generate_mcq_questions')
    def test_mcq_generation_service_error(self, mock_mcq, client, auth_headers):
        """Test MCQ generation when AI service fails"""
        mock_mcq.side_effect = Exception("MCQ generation failed")
        
        mcq_data = {
            'num_questions': 1,
            'subject_name': 'Physics',
            'difficulty': 'hard',
            'save_to_database': False
        }
        
        response = client.post('/api/ai/generate-mcq-from-pdfs', 
                             headers=auth_headers, json=mcq_data)
        
        assert_error_response(response, 500)


class TestRAGStatusEndpoint:
    """Test RAG system status functionality"""
    
    def test_rag_status_public(self, client):
        """Test RAG status endpoint (public access)"""
        response = client.get('/api/ai/rag/status')
        
        data = assert_success_response(response)
        status_info = data['data']
        assert 'status' in status_info
        assert 'dependencies' in status_info
        assert 'pdf_count' in status_info
        assert 'last_updated' in status_info
    
    @patch('shared.services.ai_service.check_rag_status')
    def test_rag_status_caching(self, mock_rag_status, client):
        """Test RAG status endpoint caching"""
        mock_rag_status.return_value = {
            'status': 'operational',
            'dependencies': {'ollama': True, 'embeddings': True},
            'pdf_count': 10,
            'last_updated': '2024-01-01T00:00:00Z'
        }
        
        # First request
        response1 = client.get('/api/ai/rag/status')
        assert_success_response(response1)
        
        # Second request should use cache
        response2 = client.get('/api/ai/rag/status')
        assert_success_response(response2)
        
        # Should only call the service once due to caching
        assert mock_rag_status.call_count == 1
    
    @patch('shared.services.ai_service.check_rag_status')
    def test_rag_status_service_error(self, mock_rag_status, client):
        """Test RAG status when service check fails"""
        mock_rag_status.side_effect = Exception("RAG service check failed")
        
        response = client.get('/api/ai/rag/status')
        
        # Should still return a response with error status
        data = assert_success_response(response)
        assert data['data']['status'] == 'error'


class TestAIServiceIntegration:
    """Test AI service integration and dependencies"""
    
    @patch('shared.services.ai_service.check_ollama_connection')
    def test_ollama_connection_check(self, mock_ollama, client):
        """Test Ollama connection checking"""
        mock_ollama.return_value = True
        
        response = client.get('/api/ai/rag/status')
        data = assert_success_response(response)
        
        # Should include Ollama status in dependencies
        dependencies = data['data']['dependencies']
        assert 'ollama' in dependencies
    
    @patch('shared.services.ai_service.check_pdf_availability')
    def test_pdf_availability_check(self, mock_pdf, client):
        """Test PDF availability checking"""
        mock_pdf.return_value = {'count': 5, 'subjects': ['Physics', 'Chemistry']}
        
        response = client.get('/api/ai/rag/status')
        data = assert_success_response(response)
        
        # Should include PDF information
        assert 'pdf_count' in data['data']
    
    def test_ai_model_configuration(self, client):
        """Test AI model configuration in responses"""
        response = client.get('/api/ai/rag/status')
        data = assert_success_response(response)
        
        # Should include model information
        status_info = data['data']
        if 'model_info' in status_info:
            assert 'model_name' in status_info['model_info']


class TestAIUsageTracking:
    """Test AI usage tracking and statistics"""
    
    def test_chat_history_storage(self, client, auth_headers, mock_ollama_service, db_session):
        """Test that chat history is properly stored"""
        chat_data = {
            'message': 'Test message for history',
            'session_id': 'history_test_session',
            'is_academic': True
        }
        
        response = client.post('/api/ai/chat', 
                             headers=auth_headers, json=chat_data)
        
        assert_success_response(response)
        
        # Verify chat history was stored
        chat_history = db_session.query(AIChatHistory).filter_by(
            session_id='history_test_session'
        ).first()
        assert chat_history is not None
        assert chat_history.message == chat_data['message']
        assert chat_history.is_academic is True
    
    def test_ai_stats_tracking(self, client, auth_headers, mock_ollama_service, db_session):
        """Test that AI usage statistics are tracked"""
        chat_data = {
            'message': 'Test message for stats',
            'session_id': 'stats_test_session',
            'is_academic': True
        }
        
        response = client.post('/api/ai/chat', 
                             headers=auth_headers, json=chat_data)
        
        assert_success_response(response)
        
        # Verify AI stats were updated
        # Note: This might require getting the user ID from the auth headers
        # For now, just check that the response includes token tracking
        token_info = response.get_json()['data']['token_info']
        assert token_info['tokens_used_today'] > 0
    
    def test_token_limit_enforcement(self, client, auth_headers, mock_ollama_service, sample_user, db_session):
        """Test that token limits are enforced"""
        # Set user's daily token usage to near limit
        # This would require modifying the user's AI stats
        # For now, test that token info is returned correctly
        
        chat_data = {
            'message': 'Test token limit',
            'session_id': 'limit_test',
            'is_academic': True
        }
        
        response = client.post('/api/ai/chat', 
                             headers=auth_headers, json=chat_data)
        
        data = assert_success_response(response)
        token_info = data['data']['token_info']
        
        # Should have reasonable token limits
        assert token_info['daily_limit'] > 0
        assert token_info['remaining_tokens'] >= 0
        assert token_info['tokens_used_today'] <= token_info['daily_limit']


class TestAIErrorHandling:
    """Test AI service error handling"""
    
    @patch('shared.services.ai_service.generate_ai_response')
    def test_ai_timeout_handling(self, mock_ai, client, auth_headers):
        """Test handling of AI service timeouts"""
        mock_ai.side_effect = TimeoutError("AI service timeout")
        
        chat_data = {
            'message': 'Test timeout',
            'session_id': 'timeout_test',
            'is_academic': True
        }
        
        response = client.post('/api/ai/chat', 
                             headers=auth_headers, json=chat_data)
        
        assert_error_response(response, 500)
        error_data = response.get_json()
        assert 'timeout' in error_data['error'].lower()
    
    @patch('shared.services.ai_service.generate_mcq_questions')
    def test_mcq_generation_partial_failure(self, mock_mcq, client, auth_headers):
        """Test handling of partial MCQ generation failures"""
        # Mock returning fewer questions than requested
        mock_mcq.return_value = [
            {
                'question': 'Test question',
                'options': {'A': 'Option A', 'B': 'Option B', 'C': 'Option C', 'D': 'Option D'},
                'correct_answer': 'A',
                'explanation': 'Test explanation'
            }
        ]
        
        mcq_data = {
            'num_questions': 5,  # Request 5 but only get 1
            'subject_name': 'Physics',
            'difficulty': 'hard',
            'save_to_database': False
        }
        
        response = client.post('/api/ai/generate-mcq-from-pdfs', 
                             headers=auth_headers, json=mcq_data)
        
        data = assert_success_response(response)
        # Should still succeed but with fewer questions
        assert len(data['data']['questions']) == 1
        assert data['data']['total_generated'] == 1
