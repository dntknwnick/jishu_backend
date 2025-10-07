import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from flask import Flask, request, jsonify
from flask_jwt_extended import JWTManager, jwt_required, get_jwt_identity
from flask_cors import CORS
from datetime import datetime

from shared.models.user import db, User
from shared.utils.validators import validate_email_format, validate_mobile_number, validate_name
from shared.utils.response_helper import success_response, error_response, validation_error_response
from config import config

def create_app(config_name='development'):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    # Initialize extensions
    db.init_app(app)
    jwt = JWTManager(app)
    CORS(app, origins=app.config['CORS_ORIGINS'])
    
    @app.route('/health', methods=['GET'])
    def health_check():
        return success_response(message="User service is running")
    
    @app.route('/profile', methods=['GET'])
    @jwt_required()
    def get_profile():
        try:
            user_id = get_jwt_identity()
            user = User.query.get(user_id)
            
            if not user:
                return error_response("User not found", 404)
            
            return success_response({
                'user': user.to_dict()
            }, "Profile retrieved successfully")
            
        except Exception as e:
            return error_response(f"Failed to get profile: {str(e)}", 500)
    
    @app.route('/profile', methods=['PUT'])
    @jwt_required()
    def update_profile():
        try:
            user_id = get_jwt_identity()
            user = User.query.get(user_id)
            
            if not user:
                return error_response("User not found", 404)
            
            data = request.get_json()
            errors = {}
            
            # Validate and update name
            if 'name' in data:
                is_valid_name, name_message = validate_name(data['name'])
                if not is_valid_name:
                    errors['name'] = name_message
                else:
                    user.name = data['name'].strip()
            
            # Validate and update mobile number
            if 'mobile_no' in data:
                if not validate_mobile_number(data['mobile_no']):
                    errors['mobile_no'] = "Invalid mobile number format"
                else:
                    user.mobile_no = data['mobile_no']
            
            # Update color theme
            if 'color_theme' in data:
                if data['color_theme'] in ['light', 'dark']:
                    user.color_theme = data['color_theme']
                else:
                    errors['color_theme'] = "Color theme must be 'light' or 'dark'"
            
            if errors:
                return validation_error_response(errors)
            
            user.updated_at = datetime.utcnow()
            db.session.commit()
            
            return success_response({
                'user': user.to_dict()
            }, "Profile updated successfully")
            
        except Exception as e:
            db.session.rollback()
            return error_response(f"Failed to update profile: {str(e)}", 500)
    
    @app.route('/change-password', methods=['POST'])
    @jwt_required()
    def change_password():
        try:
            user_id = get_jwt_identity()
            user = User.query.get(user_id)
            
            if not user:
                return error_response("User not found", 404)
            
            # Check if user has a password (not Google OAuth user)
            if not user.password:
                return error_response("Cannot change password for Google OAuth users", 400)
            
            data = request.get_json()
            
            # Validate required fields
            required_fields = ['current_password', 'new_password', 'confirm_password']
            errors = {}
            
            for field in required_fields:
                if not data.get(field):
                    errors[field] = f"{field.replace('_', ' ').title()} is required"
            
            if errors:
                return validation_error_response(errors)
            
            # Check current password
            if not user.check_password(data['current_password']):
                return error_response("Current password is incorrect", 401)
            
            # Validate new password
            from shared.utils.validators import validate_password_strength
            is_strong_password, password_message = validate_password_strength(data['new_password'])
            if not is_strong_password:
                errors['new_password'] = password_message
            
            # Check password confirmation
            if data['new_password'] != data['confirm_password']:
                errors['confirm_password'] = "Passwords do not match"
            
            if errors:
                return validation_error_response(errors)
            
            # Update password
            user.set_password(data['new_password'])
            user.updated_at = datetime.utcnow()
            db.session.commit()
            
            return success_response(message="Password changed successfully")
            
        except Exception as e:
            db.session.rollback()
            return error_response(f"Failed to change password: {str(e)}", 500)
    
    @app.route('/users', methods=['GET'])
    @jwt_required()
    def get_users():
        try:
            user_id = get_jwt_identity()
            current_user = User.query.get(user_id)
            
            if not current_user or not current_user.is_admin:
                return error_response("Admin access required", 403)
            
            # Get pagination parameters
            page = request.args.get('page', 1, type=int)
            per_page = request.args.get('per_page', 10, type=int)
            
            # Get filter parameters
            status = request.args.get('status')
            source = request.args.get('source')
            
            # Build query
            query = User.query
            
            if status:
                query = query.filter(User.status == status)
            if source:
                query = query.filter(User.source == source)
            
            # Paginate results
            users = query.paginate(
                page=page, 
                per_page=per_page, 
                error_out=False
            )
            
            return success_response({
                'users': [user.to_dict() for user in users.items],
                'pagination': {
                    'page': users.page,
                    'pages': users.pages,
                    'per_page': users.per_page,
                    'total': users.total
                }
            }, "Users retrieved successfully")
            
        except Exception as e:
            return error_response(f"Failed to get users: {str(e)}", 500)
    
    @app.route('/users/<int:user_id>/status', methods=['PUT'])
    @jwt_required()
    def update_user_status():
        try:
            current_user_id = get_jwt_identity()
            current_user = User.query.get(current_user_id)
            
            if not current_user or not current_user.is_admin:
                return error_response("Admin access required", 403)
            
            user_id = request.view_args['user_id']
            user = User.query.get(user_id)
            
            if not user:
                return error_response("User not found", 404)
            
            data = request.get_json()
            new_status = data.get('status')
            
            if new_status not in ['active', 'inactive', 'blocked']:
                return error_response("Invalid status. Must be 'active', 'inactive', or 'blocked'", 400)
            
            user.status = new_status
            user.updated_at = datetime.utcnow()
            db.session.commit()
            
            return success_response({
                'user': user.to_dict()
            }, f"User status updated to {new_status}")
            
        except Exception as e:
            db.session.rollback()
            return error_response(f"Failed to update user status: {str(e)}", 500)
    
    return app

if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        db.create_all()
    # Bind to 127.0.0.1 so it's only accessible internally
    app.run(host='127.0.0.1', port=5002, debug=True)
