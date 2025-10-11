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
        print(f"DEBUG admin_required: user_id={user_id}, type={type(user_id)}")
        # Handle both string and integer identities for backward compatibility
        try:
            user_id_int = int(user_id) if isinstance(user_id, (str, int)) else user_id
            user = User.query.get(user_id_int)
            print(f"DEBUG admin_required: found user={user.email_id if user else None}")
        except (ValueError, TypeError) as e:
            print(f"DEBUG admin_required: conversion error={e}")
            return error_response("Invalid user identity", 401)
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
        # Handle both string and integer identities for backward compatibility
        try:
            user_id_int = int(user_id) if isinstance(user_id, (str, int)) else user_id
            user = User.query.get(user_id_int)
        except (ValueError, TypeError):
            return error_response("Invalid user identity", 401)
        if not user:
            return error_response("User not found", 404)
        if user.status != 'active':
            return error_response("Account is not active", 403)
        return f(*args, **kwargs)
    return decorated_function

def get_current_user():
    """Helper function to get current user from JWT token"""
    user_id = get_jwt_identity()
    if not user_id:
        return None
    try:
        user_id_int = int(user_id) if isinstance(user_id, (str, int)) else user_id
        return User.query.get(user_id_int)
    except (ValueError, TypeError):
        return None
