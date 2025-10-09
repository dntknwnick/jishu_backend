from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from .user import db

class BlogPost(db.Model):
    """Model for community blog posts"""
    __tablename__ = 'blog_posts'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    content = db.Column(db.Text, nullable=False)
    tags = db.Column(db.String(500), nullable=True)  # comma-separated tags
    likes_count = db.Column(db.Integer, default=0)
    comments_count = db.Column(db.Integer, default=0)
    is_featured = db.Column(db.Boolean, default=False)
    status = db.Column(db.Enum('draft', 'published', 'archived'), default='published')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', backref='blog_posts')
    
    def to_dict(self, include_user=True):
        """Convert blog post object to dictionary"""
        result = {
            'id': self.id,
            'user_id': self.user_id,
            'title': self.title,
            'content': self.content,
            'tags': self.tags.split(',') if self.tags else [],
            'likes_count': self.likes_count,
            'comments_count': self.comments_count,
            'is_featured': self.is_featured,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
        
        if include_user and self.user:
            result['user'] = {
                'id': self.user.id,
                'name': self.user.name,
                'email_id': self.user.email_id
            }
            
        return result
    
    def __repr__(self):
        return f'<BlogPost {self.title}>'


class BlogLike(db.Model):
    """Model for blog post likes"""
    __tablename__ = 'blog_likes'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('blog_posts.id', ondelete='CASCADE'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Unique constraint to prevent duplicate likes
    __table_args__ = (db.UniqueConstraint('user_id', 'post_id', name='unique_user_post_like'),)
    
    # Relationships
    user = db.relationship('User', backref='blog_likes')
    post = db.relationship('BlogPost', backref='likes')
    
    def to_dict(self):
        """Convert blog like object to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'post_id': self.post_id,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    def __repr__(self):
        return f'<BlogLike {self.id}>'


class BlogComment(db.Model):
    """Model for blog post comments"""
    __tablename__ = 'blog_comments'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('blog_posts.id', ondelete='CASCADE'), nullable=False)
    parent_comment_id = db.Column(db.Integer, db.ForeignKey('blog_comments.id', ondelete='CASCADE'), nullable=True)
    content = db.Column(db.Text, nullable=False)
    likes_count = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', backref='blog_comments')
    post = db.relationship('BlogPost', backref='comments')
    parent_comment = db.relationship('BlogComment', remote_side=[id], backref='replies')
    
    def to_dict(self, include_user=True, include_replies=False):
        """Convert blog comment object to dictionary"""
        result = {
            'id': self.id,
            'user_id': self.user_id,
            'post_id': self.post_id,
            'parent_comment_id': self.parent_comment_id,
            'content': self.content,
            'likes_count': self.likes_count,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
        
        if include_user and self.user:
            result['user'] = {
                'id': self.user.id,
                'name': self.user.name,
                'email_id': self.user.email_id
            }
        
        if include_replies:
            result['replies'] = [reply.to_dict(include_user=include_user, include_replies=False) 
                               for reply in self.replies]
            
        return result
    
    def __repr__(self):
        return f'<BlogComment {self.id}>'


class AIChatHistory(db.Model):
    """Model for AI chat history"""
    __tablename__ = 'ai_chat_history'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    session_id = db.Column(db.String(100), nullable=True)
    message = db.Column(db.Text, nullable=False)
    response = db.Column(db.Text, nullable=False)
    tokens_used = db.Column(db.Integer, default=0)
    response_time = db.Column(db.Numeric(8, 3), default=0.000)  # in seconds
    is_academic = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', backref='ai_chat_history')
    
    def to_dict(self):
        """Convert AI chat history object to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'session_id': self.session_id,
            'message': self.message,
            'response': self.response,
            'tokens_used': self.tokens_used,
            'response_time': float(self.response_time) if self.response_time else 0.0,
            'is_academic': self.is_academic,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    def __repr__(self):
        return f'<AIChatHistory {self.id}>'


class UserAIStats(db.Model):
    """Model for user AI usage statistics"""
    __tablename__ = 'user_ai_stats'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    total_queries = db.Column(db.Integer, default=0)
    total_tokens_used = db.Column(db.Integer, default=0)
    monthly_queries = db.Column(db.Integer, default=0)
    monthly_tokens_used = db.Column(db.Integer, default=0)
    last_query_date = db.Column(db.DateTime, nullable=True)
    month_year = db.Column(db.String(7), nullable=False)  # format: YYYY-MM
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Unique constraint to prevent duplicate monthly stats
    __table_args__ = (db.UniqueConstraint('user_id', 'month_year', name='unique_user_month'),)
    
    # Relationships
    user = db.relationship('User', backref='ai_stats')
    
    def to_dict(self):
        """Convert user AI stats object to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'total_queries': self.total_queries,
            'total_tokens_used': self.total_tokens_used,
            'monthly_queries': self.monthly_queries,
            'monthly_tokens_used': self.monthly_tokens_used,
            'last_query_date': self.last_query_date.isoformat() if self.last_query_date else None,
            'month_year': self.month_year,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def __repr__(self):
        return f'<UserAIStats {self.user_id}-{self.month_year}>'


class PasswordResetToken(db.Model):
    """Model for password reset tokens"""
    __tablename__ = 'password_reset_tokens'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    token = db.Column(db.String(255), nullable=False, unique=True)
    expires_at = db.Column(db.DateTime, nullable=False)
    used = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', backref='password_reset_tokens')
    
    def is_valid(self):
        """Check if token is valid and not expired"""
        return not self.used and datetime.utcnow() < self.expires_at
    
    def to_dict(self):
        """Convert password reset token object to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'token': self.token,
            'expires_at': self.expires_at.isoformat() if self.expires_at else None,
            'used': self.used,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    def __repr__(self):
        return f'<PasswordResetToken {self.id}>'
