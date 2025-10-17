# Models package initialization
from .user import User, db
from .course import ExamCategory, ExamCategorySubject
from .purchase import ExamCategoryPurchase, ExamCategoryQuestion, TestAttempt, TestAnswer, MockTestAttempt, TestAttemptSession
from .community import BlogPost, BlogLike, BlogComment, AIChatHistory, UserAIStats, PasswordResetToken
from .profile import UserStats, UserAcademics, UserPurchaseHistory

__all__ = [
    'User', 'db',
    'ExamCategory', 'ExamCategorySubject',
    'ExamCategoryPurchase', 'ExamCategoryQuestion', 'TestAttempt', 'TestAnswer', 'MockTestAttempt', 'TestAttemptSession',
    'BlogPost', 'BlogLike', 'BlogComment', 'AIChatHistory', 'UserAIStats', 'PasswordResetToken',
    'UserStats', 'UserAcademics', 'UserPurchaseHistory'
]
