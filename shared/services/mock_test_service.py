"""
Mock Test Service - Handles test card creation and management
"""
from datetime import datetime
from typing import List, Dict, Optional, Tuple
from sqlalchemy.exc import IntegrityError
from ..models.user import db
from ..models.purchase import ExamCategoryPurchase, MockTestAttempt, TestAttemptSession, ExamCategoryQuestion
from ..models.course import ExamCategory, ExamCategorySubject


class MockTestService:
    """Service class for managing mock test cards and attempts"""
    
    @staticmethod
    def create_test_cards_for_purchase(purchase_id: int) -> Dict:
        """
        Create 50 test cards for each subject in a purchase
        
        Args:
            purchase_id: ID of the purchase
            
        Returns:
            Dict with creation results
        """
        try:
            purchase = ExamCategoryPurchase.query.get(purchase_id)
            if not purchase:
                return {'success': False, 'error': 'Purchase not found'}

            # Check if test cards already exist for this purchase
            existing_cards = MockTestAttempt.query.filter_by(purchase_id=purchase_id).first()
            if existing_cards:
                # Count existing cards
                total_existing = MockTestAttempt.query.filter_by(purchase_id=purchase_id).count()
                return {
                    'success': True,
                    'cards_created': total_existing,
                    'subjects_count': len(set(card.subject_id for card in MockTestAttempt.query.filter_by(purchase_id=purchase_id).all())),
                    'cards_per_subject': 50,
                    'message': 'Test cards already exist for this purchase'
                }

            # Get subjects included in this purchase
            subject_ids = purchase.get_included_subjects()

            if not subject_ids:
                return {'success': False, 'error': 'No subjects found for purchase'}

            created_cards = []
            
            for subject_id in subject_ids:
                # Create 50 test cards for this subject
                for test_number in range(1, 51):
                    mock_test = MockTestAttempt(
                        purchase_id=purchase.id,
                        user_id=purchase.user_id,
                        course_id=purchase.exam_category_id,
                        subject_id=subject_id,
                        test_number=test_number,
                        max_attempts=3,
                        attempts_used=0,
                        questions_generated=False,
                        total_questions=50,
                        status='available'
                    )
                    
                    db.session.add(mock_test)
                    created_cards.append({
                        'subject_id': subject_id,
                        'test_number': test_number
                    })
            
            db.session.commit()
            
            return {
                'success': True,
                'cards_created': len(created_cards),
                'subjects_count': len(subject_ids),
                'cards_per_subject': 50,
                'details': created_cards
            }
            
        except IntegrityError as e:
            db.session.rollback()
            return {'success': False, 'error': f'Database integrity error: {str(e)}'}
        except Exception as e:
            db.session.rollback()
            return {'success': False, 'error': f'Failed to create test cards: {str(e)}'}
    
    @staticmethod
    def get_user_test_cards(user_id: int, subject_id: Optional[int] = None) -> List[Dict]:
        """
        Get all test cards for a user, optionally filtered by subject
        
        Args:
            user_id: ID of the user
            subject_id: Optional subject ID to filter by
            
        Returns:
            List of test card dictionaries
        """
        query = MockTestAttempt.query.filter_by(user_id=user_id)
        
        if subject_id:
            query = query.filter_by(subject_id=subject_id)
        
        # Join with purchase to ensure only active purchases
        query = query.join(ExamCategoryPurchase).filter(
            ExamCategoryPurchase.status == 'active'
        )
        
        test_cards = query.order_by(
            MockTestAttempt.subject_id,
            MockTestAttempt.test_number
        ).all()
        
        return [card.to_dict() for card in test_cards]
    
    @staticmethod
    def start_test_attempt(mock_test_id: int, user_id: int) -> Dict:
        """
        Start a new test attempt for a mock test card
        
        Args:
            mock_test_id: ID of the mock test card
            user_id: ID of the user
            
        Returns:
            Dict with attempt details or error
        """
        try:
            mock_test = MockTestAttempt.query.filter_by(
                id=mock_test_id,
                user_id=user_id
            ).first()
            
            if not mock_test:
                return {'success': False, 'error': 'Mock test not found'}
            
            if not mock_test.is_available:
                return {
                    'success': False, 
                    'error': f'Test card not available. Attempts used: {mock_test.attempts_used}/{mock_test.max_attempts}'
                }
            
            # Create new test session
            attempt_number = mock_test.attempts_used + 1
            session = TestAttemptSession(
                mock_test_id=mock_test.id,
                user_id=user_id,
                attempt_number=attempt_number,
                status='in_progress'
            )
            
            db.session.add(session)
            
            # Update mock test status
            mock_test.status = 'in_progress'
            
            db.session.commit()
            
            return {
                'success': True,
                'session_id': session.id,
                'mock_test_id': mock_test.id,
                'attempt_number': attempt_number,
                'remaining_attempts': mock_test.remaining_attempts - 1,
                'questions_generated': mock_test.questions_generated
            }
            
        except Exception as e:
            db.session.rollback()
            return {'success': False, 'error': f'Failed to start test attempt: {str(e)}'}
    
    @staticmethod
    def complete_test_attempt(session_id: int, score: int, time_taken: int, 
                            correct_answers: int, wrong_answers: int, unanswered: int) -> Dict:
        """
        Complete a test attempt and update scores
        
        Args:
            session_id: ID of the test session
            score: Final score
            time_taken: Time taken in seconds
            correct_answers: Number of correct answers
            wrong_answers: Number of wrong answers
            unanswered: Number of unanswered questions
            
        Returns:
            Dict with completion results
        """
        try:
            session = TestAttemptSession.query.get(session_id)
            if not session:
                return {'success': False, 'error': 'Test session not found'}
            
            mock_test = session.mock_test
            
            # Calculate percentage
            percentage = (score / mock_test.total_questions) * 100 if mock_test.total_questions > 0 else 0
            
            # Update session
            session.score = score
            session.percentage = percentage
            session.time_taken = time_taken
            session.correct_answers = correct_answers
            session.wrong_answers = wrong_answers
            session.unanswered = unanswered
            session.status = 'completed'
            session.completed_at = datetime.utcnow()
            
            # Update mock test with latest attempt results
            mock_test.latest_score = score
            mock_test.latest_percentage = percentage
            mock_test.latest_time_taken = time_taken
            mock_test.latest_attempt_date = datetime.utcnow()
            mock_test.attempts_used += 1
            
            # Set first attempt data if this is the first attempt
            if session.attempt_number == 1:
                mock_test.first_attempt_score = score
                mock_test.first_attempt_date = datetime.utcnow()
            
            # Update status based on remaining attempts
            if mock_test.attempts_used >= mock_test.max_attempts:
                mock_test.status = 'disabled'
            else:
                mock_test.status = 'completed'
            
            db.session.commit()
            
            return {
                'success': True,
                'session_id': session.id,
                'mock_test_id': mock_test.id,
                'score': score,
                'percentage': percentage,
                'attempt_number': session.attempt_number,
                'remaining_attempts': mock_test.remaining_attempts,
                'is_final_attempt': mock_test.attempts_used >= mock_test.max_attempts
            }
            
        except Exception as e:
            db.session.rollback()
            return {'success': False, 'error': f'Failed to complete test attempt: {str(e)}'}
    
    @staticmethod
    def get_test_analytics(user_id: int, subject_id: Optional[int] = None) -> Dict:
        """
        Get analytics for user's test performance (based on latest attempts only)
        
        Args:
            user_id: ID of the user
            subject_id: Optional subject ID to filter by
            
        Returns:
            Dict with analytics data
        """
        query = MockTestAttempt.query.filter_by(user_id=user_id)
        
        if subject_id:
            query = query.filter_by(subject_id=subject_id)
        
        # Only include tests that have been attempted
        query = query.filter(MockTestAttempt.attempts_used > 0)
        
        test_cards = query.all()
        
        if not test_cards:
            return {
                'total_tests_taken': 0,
                'average_score': 0,
                'average_percentage': 0,
                'best_score': 0,
                'worst_score': 0,
                'total_time_spent': 0
            }
        
        # Calculate analytics based on latest attempts only
        scores = [card.latest_score for card in test_cards]
        percentages = [float(card.latest_percentage) for card in test_cards]
        times = [card.latest_time_taken for card in test_cards]
        
        return {
            'total_tests_taken': len(test_cards),
            'average_score': sum(scores) / len(scores),
            'average_percentage': sum(percentages) / len(percentages),
            'best_score': max(scores),
            'worst_score': min(scores),
            'total_time_spent': sum(times),
            'improvement_data': MockTestService._calculate_improvement(test_cards)
        }
    
    @staticmethod
    def _calculate_improvement(test_cards: List[MockTestAttempt]) -> Dict:
        """Calculate improvement metrics comparing first vs latest attempts"""
        first_attempts = [card for card in test_cards if card.first_attempt_score > 0]
        
        if not first_attempts:
            return {'improvement_available': False}
        
        first_avg = sum(card.first_attempt_score for card in first_attempts) / len(first_attempts)
        latest_avg = sum(card.latest_score for card in first_attempts) / len(first_attempts)
        
        return {
            'improvement_available': True,
            'first_attempt_average': first_avg,
            'latest_attempt_average': latest_avg,
            'improvement_points': latest_avg - first_avg,
            'improvement_percentage': ((latest_avg - first_avg) / first_avg * 100) if first_avg > 0 else 0
        }
