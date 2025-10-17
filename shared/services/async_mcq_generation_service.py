"""
Asynchronous MCQ Generation Service
Handles background MCQ generation with immediate return of initial questions
"""

import threading
import logging
import time
from typing import Dict, List, Optional
from datetime import datetime
from dataclasses import dataclass, asdict
import json

logger = logging.getLogger(__name__)


@dataclass
class GenerationSession:
    """Represents an MCQ generation session"""
    session_id: str
    mock_test_id: int
    user_id: int
    subject_id: int
    total_questions: int = 50
    initial_questions_count: int = 5
    
    # Progress tracking
    questions_generated: int = 0
    is_complete: bool = False
    has_error: bool = False
    error_message: str = ""
    
    # Questions storage
    questions: List[Dict] = None
    
    # Timestamps
    created_at: datetime = None
    started_at: datetime = None
    completed_at: datetime = None
    
    def __post_init__(self):
        if self.questions is None:
            self.questions = []
        if self.created_at is None:
            self.created_at = datetime.utcnow()
    
    def to_dict(self):
        """Convert to dictionary"""
        data = asdict(self)
        data['created_at'] = self.created_at.isoformat() if self.created_at else None
        data['started_at'] = self.started_at.isoformat() if self.started_at else None
        data['completed_at'] = self.completed_at.isoformat() if self.completed_at else None
        return data


class AsyncMCQGenerationService:
    """Service for asynchronous MCQ generation"""
    
    def __init__(self):
        """Initialize the service"""
        self.sessions: Dict[str, GenerationSession] = {}
        self.lock = threading.Lock()
        logger.info("✅ AsyncMCQGenerationService initialized")
    
    def create_session(
        self,
        mock_test_id: int,
        user_id: int,
        subject_id: int,
        total_questions: int = 50,
        initial_questions_count: int = 5
    ) -> GenerationSession:
        """
        Create a new generation session
        
        Args:
            mock_test_id: ID of the mock test
            user_id: ID of the user
            subject_id: ID of the subject
            total_questions: Total questions to generate
            initial_questions_count: Number of initial questions to return immediately
            
        Returns:
            GenerationSession: The created session
        """
        session_id = f"gen_{mock_test_id}_{user_id}_{int(time.time() * 1000)}"
        
        session = GenerationSession(
            session_id=session_id,
            mock_test_id=mock_test_id,
            user_id=user_id,
            subject_id=subject_id,
            total_questions=total_questions,
            initial_questions_count=initial_questions_count
        )
        
        with self.lock:
            self.sessions[session_id] = session
        
        logger.info(f"✅ Created generation session: {session_id}")
        return session
    
    def get_session(self, session_id: str) -> Optional[GenerationSession]:
        """Get a generation session by ID"""
        with self.lock:
            return self.sessions.get(session_id)
    
    def start_background_generation(
        self,
        session_id: str,
        generation_func,
        *args,
        **kwargs
    ) -> bool:
        """
        Start background MCQ generation in a separate thread
        
        Args:
            session_id: ID of the generation session
            generation_func: Function to call for MCQ generation
            *args: Positional arguments for generation_func
            **kwargs: Keyword arguments for generation_func
            
        Returns:
            bool: True if thread started successfully
        """
        session = self.get_session(session_id)
        if not session:
            logger.error(f"❌ Session not found: {session_id}")
            return False
        
        def _generate():
            """Background generation worker"""
            try:
                session.started_at = datetime.utcnow()
                logger.info(f"🔄 Starting background MCQ generation for session: {session_id}")
                
                # Call the generation function
                result = generation_func(*args, **kwargs)
                
                if result.get('success'):
                    questions = result.get('questions', [])
                    with self.lock:
                        session.questions = questions
                        session.questions_generated = len(questions)
                        session.is_complete = True
                        session.completed_at = datetime.utcnow()
                    
                    logger.info(f"✅ Background generation complete: {len(questions)} questions")
                else:
                    with self.lock:
                        session.has_error = True
                        session.error_message = result.get('error', 'Unknown error')
                        session.completed_at = datetime.utcnow()
                    
                    logger.error(f"❌ Generation failed: {session.error_message}")
                    
            except Exception as e:
                logger.error(f"❌ Background generation error: {str(e)}")
                with self.lock:
                    session.has_error = True
                    session.error_message = str(e)
                    session.completed_at = datetime.utcnow()
        
        # Start background thread
        thread = threading.Thread(target=_generate, daemon=True)
        thread.start()
        
        logger.info(f"✅ Background generation thread started for session: {session_id}")
        return True
    
    def get_progress(self, session_id: str) -> Dict:
        """
        Get generation progress for a session
        
        Returns:
            Dict with progress information
        """
        session = self.get_session(session_id)
        if not session:
            return {
                'success': False,
                'error': 'Session not found'
            }
        
        progress_percent = (session.questions_generated / session.total_questions) * 100 if session.total_questions > 0 else 0
        
        return {
            'success': True,
            'session_id': session_id,
            'progress': progress_percent,
            'questions_generated': session.questions_generated,
            'total_questions': session.total_questions,
            'is_complete': session.is_complete,
            'has_error': session.has_error,
            'error_message': session.error_message if session.has_error else None,
            'questions': session.questions[:session.initial_questions_count] if session.questions else [],
            'can_use_partial': session.questions_generated >= session.initial_questions_count,
            'timestamp': datetime.utcnow().isoformat()
        }
    
    def cleanup_session(self, session_id: str) -> bool:
        """
        Clean up a generation session
        
        Args:
            session_id: ID of the session to clean up
            
        Returns:
            bool: True if cleaned up successfully
        """
        with self.lock:
            if session_id in self.sessions:
                del self.sessions[session_id]
                logger.info(f"✅ Cleaned up session: {session_id}")
                return True
        
        return False
    
    def get_all_sessions(self) -> List[Dict]:
        """Get all active sessions"""
        with self.lock:
            return [session.to_dict() for session in self.sessions.values()]


# Singleton instance
_async_mcq_service = None


def get_async_mcq_generation_service() -> AsyncMCQGenerationService:
    """Get or create singleton instance"""
    global _async_mcq_service
    if _async_mcq_service is None:
        _async_mcq_service = AsyncMCQGenerationService()
    return _async_mcq_service

