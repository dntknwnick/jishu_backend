from functools import wraps
from flask_jwt_extended import jwt_required, get_jwt_identity
from shared.models.user import User
from shared.utils.response_helper import error_response

def admin_required(f):
    """Decorator to require admin privileges"""
    @wraps(f)
    @jwt_required()
    def decorated_function(*args, **kwargs):
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        if not user:
            return error_response("User not found", 404)
        if not user.is_admin:
            return error_response("Admin access required", 403)
        if user.status != 'active':
            return error_response("Account is not active", 403)
        return f(*args, **kwargs)
    return decorated_function

def user_required(f):
    """Decorator to require active user account"""
    @wraps(f)
    @jwt_required()
    def decorated_function(*args, **kwargs):
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        if not user:
            return error_response("User not found", 404)
        if user.status != 'active':
            return error_response("Account is not active", 403)
        return f(*args, **kwargs)
    return decorated_function

def get_current_user():
    """Helper function to get current user from JWT token"""
    user_id = get_jwt_identity()
    return User.query.get(user_id) if user_id else None
