"""
Simple Chunked MCQ Generation Service
Uses existing exam_category_questions table only, no new tables needed.
"""

import uuid
import time
import logging
import threading
from typing import Dict, List, Optional
from datetime import datetime

from shared.models.user import db
from shared.models.purchase import (
    ExamCategoryQuestion, TestAttempt,
    TestAttemptSession, MockTestAttempt, ExamCategoryPurchase
)
from shared.models.course import ExamCategory, ExamCategorySubject
from shared.services.rag_service import get_rag_service

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# In-memory progress tracking
_generation_progress = {}


class SimpleChunkedMCQService:
    """Simple chunked MCQ generation using existing table structure only."""
    
    def __init__(self, batch_size: int = 5):
        self.batch_size = batch_size
        self.rag_service = get_rag_service()
        
    def start_chunked_generation(self, test_attempt_id=None, session_id=None, user_id=None):
        """Start chunked generation - generate first 5 questions immediately."""
        try:
            generation_id = str(uuid.uuid4())
            
            # Get context info
            context = self._get_generation_context(test_attempt_id, session_id)
            if not context['success']:
                return context
            
            # Generate first batch immediately
            logger.info(f"🔄 Generating first batch for {generation_id}")
            first_batch = self._generate_and_save_batch(
                generation_id=generation_id,
                batch_number=1,
                subject_name=context['subject_name'],
                context=context
            )
            
            if not first_batch['success']:
                return first_batch
            
            # Store progress info in memory
            total_needed = context['total_questions']
            _generation_progress[generation_id] = {
                'generation_id': generation_id,
                'total_questions_needed': total_needed,
                'questions_generated_count': len(first_batch['questions']),
                'generation_status': 'generating' if len(first_batch['questions']) < total_needed else 'completed',
                'started_at': datetime.utcnow(),
                'context': context
            }
            
            # Start background generation if more questions needed
            if len(first_batch['questions']) < total_needed:
                self._start_background_generation(generation_id, context)
            
            return {
                'success': True,
                'generation_id': generation_id,
                'initial_questions': first_batch['questions'],
                'progress': _generation_progress[generation_id],
                'background_generation_started': len(first_batch['questions']) < total_needed
            }
            
        except Exception as e:
            logger.error(f"❌ Error starting chunked generation: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def _get_generation_context(self, test_attempt_id, session_id):
        """Get context information for generation."""
        try:
            if session_id:
                # New test card flow
                logger.info(f"🔍 Getting context for session_id: {session_id}")
                session = TestAttemptSession.query.get(session_id)
                if not session:
                    logger.error(f"❌ Session {session_id} not found")
                    return {'success': False, 'error': 'Session not found'}

                logger.info(f"✅ Found session: {session.id}, mock_test_id: {session.mock_test_id}")

                # Get purchase through mock_test relationship
                mock_test = session.mock_test
                if not mock_test:
                    logger.error(f"❌ Mock test not found for session {session_id}")
                    return {'success': False, 'error': 'Mock test not found'}

                logger.info(f"✅ Found mock_test: {mock_test.id}")

                purchase = mock_test.purchase
                subject = mock_test.subject
                total_questions = 50  # Mock tests always have 50 questions

                logger.info(f"✅ Context: purchase_id={purchase.id}, subject={subject.subject_name}, total_questions={total_questions}")

                return {
                    'success': True,
                    'session_id': session_id,
                    'mock_test_id': mock_test.id,
                    'purchase_id': purchase.id,
                    'subject_id': subject.id,
                    'subject_name': subject.subject_name,
                    'exam_category_id': subject.exam_category_id,
                    'user_id': session.user_id,
                    'total_questions': total_questions
                }
            
            elif test_attempt_id:
                # Legacy flow
                attempt = TestAttempt.query.get(test_attempt_id)
                if not attempt:
                    return {'success': False, 'error': 'Test attempt not found'}
                
                purchase = attempt.purchase
                subject = purchase.subject
                total_questions = 50 if purchase.purchase_type == 'subject' else 150
                
                return {
                    'success': True,
                    'test_attempt_id': test_attempt_id,
                    'purchase_id': purchase.id,
                    'subject_id': subject.id,
                    'subject_name': subject.subject_name,
                    'exam_category_id': subject.exam_category_id,
                    'user_id': attempt.user_id,
                    'total_questions': total_questions
                }
            
            return {'success': False, 'error': 'No valid test identifier provided'}
            
        except Exception as e:
            logger.error(f"❌ Error getting generation context: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def _generate_and_save_batch(self, generation_id, batch_number, subject_name, context):
        """Generate a batch of questions and save to database."""
        try:
            # Generate questions using RAG service
            result = self.rag_service.generate_mcq_questions(
                subject=subject_name.lower(),
                num_questions=self.batch_size,
                difficulty='hard'
            )
            
            if not result['success']:
                return result
            
            # Save questions to database
            saved_questions = []
            for i, q in enumerate(result['questions']):
                question = ExamCategoryQuestion(
                    exam_category_id=context['exam_category_id'],
                    subject_id=context['subject_id'],
                    question=q['question'],
                    option_1=q['option_a'],
                    option_2=q['option_b'],
                    option_3=q['option_c'],
                    option_4=q['option_d'],
                    correct_answer=q['correct_answer'],
                    explanation=q.get('explanation', ''),
                    user_id=context['user_id'],
                    purchased_id=context['purchase_id'],
                    is_ai_generated=True,
                    ai_model_used=result.get('model_used', 'unknown'),
                    difficulty_level='hard',
                    generation_batch_id=generation_id,
                    batch_sequence=i + 1
                )

                # Link to mock test if this is for a test card
                if 'mock_test_id' in context:
                    question.mock_test_id = context['mock_test_id']
                
                db.session.add(question)
                saved_questions.append(question)
            
            db.session.commit()
            
            # Format questions for response
            formatted_questions = []
            for q in saved_questions:
                formatted_questions.append({
                    'id': q.id,
                    'question': q.question,
                    'options': {
                        'A': q.option_1,
                        'B': q.option_2,
                        'C': q.option_3,
                        'D': q.option_4
                    },
                    'correct_answer': q.correct_answer,
                    'explanation': q.explanation
                })
            
            logger.info(f"✅ Saved batch {batch_number} with {len(saved_questions)} questions")
            
            return {
                'success': True,
                'questions': formatted_questions,
                'batch_number': batch_number
            }
            
        except Exception as e:
            logger.error(f"❌ Error generating/saving batch {batch_number}: {str(e)}")
            db.session.rollback()
            return {'success': False, 'error': str(e)}
    
    def _start_background_generation(self, generation_id, context):
        """Start background thread to generate remaining questions."""
        def background_worker():
            try:
                progress = _generation_progress[generation_id]
                total_needed = progress['total_questions_needed']
                current_count = progress['questions_generated_count']
                batch_number = 2  # Start from batch 2
                
                while current_count < total_needed:
                    remaining = total_needed - current_count
                    batch_size = min(self.batch_size, remaining)
                    
                    logger.info(f"🔄 Background generating batch {batch_number} for {generation_id}")
                    
                    batch_result = self._generate_and_save_batch(
                        generation_id=generation_id,
                        batch_number=batch_number,
                        subject_name=context['subject_name'],
                        context=context
                    )
                    
                    if batch_result['success']:
                        current_count += len(batch_result['questions'])
                        progress['questions_generated_count'] = current_count
                        
                        if current_count >= total_needed:
                            progress['generation_status'] = 'completed'
                            progress['completed_at'] = datetime.utcnow()
                            logger.info(f"✅ Completed generation for {generation_id}")
                            break
                    else:
                        progress['generation_status'] = 'failed'
                        progress['error_message'] = batch_result['error']
                        logger.error(f"❌ Background generation failed for {generation_id}")
                        break
                    
                    batch_number += 1
                    time.sleep(1)  # Small delay between batches
                    
            except Exception as e:
                logger.error(f"❌ Background generation error for {generation_id}: {str(e)}")
                if generation_id in _generation_progress:
                    _generation_progress[generation_id]['generation_status'] = 'failed'
                    _generation_progress[generation_id]['error_message'] = str(e)
        
        # Start background thread
        thread = threading.Thread(target=background_worker, daemon=True)
        thread.start()
        logger.info(f"🚀 Started background generation for {generation_id}")
    
    def get_generation_progress(self, generation_id):
        """Get current progress of generation."""
        if generation_id not in _generation_progress:
            return {'success': False, 'error': 'Generation not found'}
        
        progress = _generation_progress[generation_id]
        
        # Get current questions from database
        questions = ExamCategoryQuestion.query.filter_by(
            generation_batch_id=generation_id
        ).order_by(ExamCategoryQuestion.batch_sequence).all()
        
        formatted_questions = []
        for q in questions:
            formatted_questions.append({
                'id': q.id,
                'question': q.question,
                'options': {
                    'A': q.option_1,
                    'B': q.option_2,
                    'C': q.option_3,
                    'D': q.option_4
                },
                'correct_answer': q.correct_answer,
                'explanation': q.explanation
            })
        
        return {
            'success': True,
            'progress': {
                'generation_id': progress['generation_id'],
                'total_questions_needed': progress['total_questions_needed'],
                'questions_generated_count': len(formatted_questions),
                'generation_status': progress['generation_status'],
                'progress_percentage': round((len(formatted_questions) / progress['total_questions_needed']) * 100, 1)
            },
            'questions': formatted_questions,
            'is_complete': progress['generation_status'] == 'completed',
            'has_error': progress['generation_status'] == 'failed'
        }


# Service instance
_chunked_service = None

def get_chunked_mcq_service(batch_size: int = 5) -> SimpleChunkedMCQService:
    """Get or create chunked MCQ service instance."""
    global _chunked_service
    if _chunked_service is None:
        _chunked_service = SimpleChunkedMCQService(batch_size)
    return _chunked_service
