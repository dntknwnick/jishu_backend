# Entry point for monolithic architecture
# Jishu Backend - Flask RESTful API

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'shared'))

from flask import Flask, request, jsonify
from flask_jwt_extended import JWTManager, jwt_required, get_jwt_identity, create_access_token, create_refresh_token, get_jwt
from flask_cors import CORS
from datetime import datetime, timedelta
import time
import uuid

from shared.models.user import db, User
from shared.models.course import ExamCategory, ExamCategorySubject
from shared.models.purchase import ExamCategoryPurchase, ExamCategoryQuestion, TestAttempt, TestAnswer, MockTestAttempt, TestAttemptSession
from shared.models.community import BlogPost, BlogLike, BlogComment, AIChatHistory, UserAIStats
from shared.models.profile import UserStats, UserAcademics, UserPurchaseHistory
from shared.utils.validators import (
    validate_email_format, validate_mobile_number, validate_name, validate_otp,
    validate_subject_name, validate_course_name, validate_price, validate_token_count,
    validate_mock_test_count, validate_blog_title, validate_blog_content, validate_tags
)
from shared.utils.response_helper import success_response, error_response, validation_error_response
from shared.utils.email_service import email_service
from shared.utils.google_oauth import create_google_oauth_service
from shared.utils.decorators import admin_required, user_required, get_current_user
from config import config
import secrets
import uuid

def generate_fallback_questions(subject_name, num_questions=50):
    """Generate fallback questions when RAG service fails"""
    fallback_questions = []

    # Subject-specific question templates
    templates = {
        'physics': [
            {
                'question': 'What is the SI unit of force?',
                'option_a': 'Newton',
                'option_b': 'Joule',
                'option_c': 'Watt',
                'option_d': 'Pascal',
                'correct_answer': 'A',
                'explanation': 'The SI unit of force is Newton (N), named after Sir Isaac Newton.'
            },
            {
                'question': 'What is the speed of light in vacuum?',
                'option_a': '3 × 10⁸ m/s',
                'option_b': '3 × 10⁶ m/s',
                'option_c': '3 × 10¹⁰ m/s',
                'option_d': '3 × 10⁴ m/s',
                'correct_answer': 'A',
                'explanation': 'The speed of light in vacuum is approximately 3 × 10⁸ meters per second.'
            }
        ],
        'chemistry': [
            {
                'question': 'What is the atomic number of carbon?',
                'option_a': '6',
                'option_b': '12',
                'option_c': '14',
                'option_d': '8',
                'correct_answer': 'A',
                'explanation': 'Carbon has an atomic number of 6, meaning it has 6 protons in its nucleus.'
            }
        ],
        'biology': [
            {
                'question': 'What is the powerhouse of the cell?',
                'option_a': 'Mitochondria',
                'option_b': 'Nucleus',
                'option_c': 'Ribosome',
                'option_d': 'Endoplasmic reticulum',
                'correct_answer': 'A',
                'explanation': 'Mitochondria are called the powerhouse of the cell because they produce ATP energy.'
            }
        ],
        'mathematics': [
            {
                'question': 'What is the value of π (pi) approximately?',
                'option_a': '3.14159',
                'option_b': '2.71828',
                'option_c': '1.41421',
                'option_d': '2.30259',
                'correct_answer': 'A',
                'explanation': 'π (pi) is approximately 3.14159, representing the ratio of circumference to diameter of a circle.'
            }
        ]
    }

    # Get templates for the subject (default to physics if not found)
    subject_templates = templates.get(subject_name.lower(), templates['physics'])

    # Generate questions by cycling through templates
    for i in range(num_questions):
        template_index = i % len(subject_templates)
        base_question = subject_templates[template_index].copy()

        # Add variation to question numbers
        if i > 0:
            base_question['question'] = f"Question {i+1}: {base_question['question']}"

        fallback_questions.append(base_question)

    return fallback_questions

def create_app(config_name='development'):
    app = Flask(__name__)
    app.config.from_object(config[config_name])

    # Initialize extensions
    db.init_app(app)
    jwt = JWTManager(app)

    # JWT Configuration
    @jwt.user_identity_loader
    def user_identity_lookup(user):
        return str(user)

    @jwt.user_lookup_loader
    def user_lookup_callback(_jwt_header, jwt_data):
        identity = jwt_data["sub"]
        # Handle both string and integer identities for backward compatibility
        try:
            user_id = int(identity) if isinstance(identity, (str, int)) else identity
            return User.query.get(user_id)
        except (ValueError, TypeError):
            return None

    CORS(app,
         origins=app.config['CORS_ORIGINS'],
         methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
         allow_headers=['Content-Type', 'Authorization'],
         supports_credentials=True)

    # Initialize Google OAuth service
    google_oauth = create_google_oauth_service(app.config)

    # CORS preflight handler
    @app.before_request
    def handle_preflight():
        if request.method == "OPTIONS":
            response = jsonify({'status': 'OK'})
            response.headers.add("Access-Control-Allow-Origin", "*")
            response.headers.add('Access-Control-Allow-Headers', "Content-Type,Authorization")
            response.headers.add('Access-Control-Allow-Methods', "GET,PUT,POST,DELETE,OPTIONS")
            response.headers.add('Access-Control-Allow-Credentials', "true")
            return response

    # Health endpoint
    @app.route('/health', methods=['GET'])
    def health_check():
        return jsonify({
            'success': True,
            'message': 'Jishu Backend API is running',
            'version': '1.0.0',
            'architecture': 'monolithic'
        })

    @app.route('/api/config/dev-settings', methods=['GET'])
    def get_dev_settings():
        """Get development configuration settings (for debugging)"""
        return success_response({
            'LOCAL_DEV_MODE': app.config.get('LOCAL_DEV_MODE', False),
            'BYPASS_PURCHASE_VALIDATION': app.config.get('BYPASS_PURCHASE_VALIDATION', False),
            'DEBUG': app.config.get('DEBUG', False),
            'environment': 'development' if app.config.get('DEBUG') else 'production'
        }, "Development settings retrieved")

    # --- AUTH ENDPOINTS ---


    @app.route('/verify-token', methods=['POST'])
    @jwt_required()
    def verify_token():
        try:
            user_id = get_jwt_identity()
            # Handle both string and integer identities for backward compatibility
            try:
                user_id_int = int(user_id) if isinstance(user_id, (str, int)) else user_id
                user = User.query.get(user_id_int)
            except (ValueError, TypeError):
                return error_response("Invalid user identity", 401)
            if not user:
                return error_response("User not found", 404)
            return success_response({
                'user': user.to_dict()
            }, "Token is valid")
        except Exception as e:
            return error_response(f"Token verification failed: {str(e)}", 500)

    @app.route('/refresh-token', methods=['POST'])
    @jwt_required(refresh=True)
    def refresh_token():
        """Refresh access token using refresh token"""
        try:
            user_id = get_jwt_identity()
            user = User.query.get(int(user_id))
            if not user:
                return error_response("User not found", 404)

            if user.status != 'active':
                return error_response("Account is not active", 403)

            # Get the refresh token from the JWT
            current_token = get_jwt()
            jti = current_token.get('jti')  # JWT ID

            # Verify the refresh token is still valid in database
            # Note: For enhanced security, you might want to store JTI in database
            # For now, we'll just check if user has a valid refresh token
            if not user.refresh_token or not user.refresh_token_expires_at:
                return error_response("No valid refresh token found", 401)

            if datetime.utcnow() > user.refresh_token_expires_at:
                user.clear_refresh_token()
                db.session.commit()
                return error_response("Refresh token has expired", 401)

            # Generate new access token
            new_access_token = create_access_token(identity=str(user.id))

            # Optionally generate new refresh token (rotate refresh tokens)
            new_refresh_token = create_refresh_token(identity=str(user.id))
            refresh_expires_at = datetime.utcnow() + timedelta(seconds=app.config['JWT_REFRESH_TOKEN_EXPIRES'])
            user.set_refresh_token(new_refresh_token, refresh_expires_at)

            # Update last login time
            user.last_login = datetime.utcnow()
            db.session.commit()

            return success_response({
                'access_token': new_access_token,
                'refresh_token': new_refresh_token,
                'user': user.to_dict()
            }, "Tokens refreshed successfully")

        except Exception as e:
            db.session.rollback()
            return error_response(f"Token refresh failed: {str(e)}", 500)

    @app.route('/logout', methods=['POST'])
    @jwt_required()
    def logout():
        """Logout user and invalidate refresh token"""
        try:
            user_id = get_jwt_identity()
            user = User.query.get(int(user_id))
            if not user:
                return error_response("User not found", 404)

            # Clear refresh token from database
            user.clear_refresh_token()
            db.session.commit()

            return success_response({
                'message': 'Logged out successfully'
            }, "Logout successful")

        except Exception as e:
            db.session.rollback()
            return error_response(f"Logout failed: {str(e)}", 500)

    # --- NEW API ENDPOINTS AS PER SPECIFICATION ---

    # Authentication & User Flow Endpoints
    @app.route('/api/auth/register', methods=['POST'])
    def api_register():
        """Register with email + OTP (no password required)"""
        try:
            data = request.get_json()
            email_id = data.get('email')
            otp = data.get('otp')
            name = data.get('name', '').strip()
            mobile_no = data.get('mobile_no', '').strip()

            # Validation
            if not email_id or not otp:
                return error_response("Email and OTP are required", 400)

            if not name:
                return error_response("Name is required", 400)

            if not mobile_no:
                return error_response("Mobile number is required", 400)

            if not validate_email_format(email_id):
                return error_response("Invalid email format", 400)

            if not validate_mobile_number(mobile_no):
                return error_response("Invalid mobile number format", 400)

            is_valid_name, name_message = validate_name(name)
            if not is_valid_name:
                return error_response(name_message, 400)

            is_valid_otp, otp_message = validate_otp(otp)
            if not is_valid_otp:
                return error_response(otp_message, 400)

            # Check if user exists
            user = User.query.filter_by(email_id=email_id).first()
            if not user:
                return error_response("User not found. Please request OTP first.", 404)

            # Verify OTP
            is_valid, message = user.verify_otp(otp)
            if not is_valid:
                return error_response(message, 400)

            # Complete registration - no password needed for OTP-based auth
            user.name = name
            user.mobile_no = mobile_no
            user.status = 'active'
            user.otp_verified = True
            user.last_login = datetime.utcnow()
            user.auth_provider = 'manual'
            user.source = 'email'

            # Generate JWT tokens
            access_token = create_access_token(identity=str(user.id))
            refresh_token = create_refresh_token(identity=str(user.id))

            # Store refresh token
            refresh_expires_at = datetime.utcnow() + timedelta(seconds=app.config['JWT_REFRESH_TOKEN_EXPIRES'])
            user.set_refresh_token(refresh_token, refresh_expires_at)

            db.session.commit()

            # Send welcome email
            email_service.send_welcome_email(email_id, user.name)

            return success_response({
                'access_token': access_token,
                'refresh_token': refresh_token,
                'user': user.to_dict()
            }, "Registration completed successfully")

        except Exception as e:
            db.session.rollback()
            return error_response(f"Registration failed: {str(e)}", 500)

    @app.route('/api/auth/login', methods=['POST'])
    def api_login():
        """Login with email/OTP only - Enhanced for seamless auth transitions"""
        try:
            data = request.get_json()
            email_id = data.get('email')
            otp = data.get('otp')

            if not email_id or not otp:
                return error_response("Email and OTP are required", 400)

            if not validate_email_format(email_id):
                return error_response("Invalid email format", 400)

            user = User.query.filter_by(email_id=email_id).first()
            if not user:
                return error_response("User not found", 404)

            if user.status != 'active':
                return error_response("Account is not active", 403)

            # Enhanced: Allow OTP login regardless of original auth provider
            # This enables users to login with OTP even if they originally registered with Google
            # Removed the restriction: if user.auth_provider == 'google'

            # Verify OTP
            is_valid, message = user.verify_otp(otp)
            if not is_valid:
                return error_response(message, 400)

            # Update last login and ensure user can use both auth methods
            user.last_login = datetime.utcnow()

            # If this was a Google-only user, now they can use both methods
            if user.auth_provider == 'google' and not user.source:
                user.source = 'email'  # Enable email auth too

            # Generate JWT tokens
            access_token = create_access_token(identity=str(user.id))
            refresh_token = create_refresh_token(identity=str(user.id))

            # Store refresh token
            refresh_expires_at = datetime.utcnow() + timedelta(seconds=app.config['JWT_REFRESH_TOKEN_EXPIRES'])
            user.set_refresh_token(refresh_token, refresh_expires_at)

            db.session.commit()

            return success_response({
                'access_token': access_token,
                'refresh_token': refresh_token,
                'user': user.to_dict(),
                'auth_method_used': 'otp',
                'available_auth_methods': ['otp', 'google'] if user.google_id else ['otp']
            }, "Login successful")

        except Exception as e:
            db.session.rollback()
            return error_response(f"Login failed: {str(e)}", 500)

    @app.route('/api/auth/logout', methods=['POST'])
    @user_required
    def api_logout():
        """Logout and blacklist token"""
        try:
            user = get_current_user()
            if not user:
                return error_response("User not found", 404)

            # Clear refresh token
            user.clear_refresh_token()
            db.session.commit()

            return success_response({
                'message': 'Logged out successfully'
            }, "Logout successful")

        except Exception as e:
            db.session.rollback()
            return error_response(f"Logout failed: {str(e)}", 500)

    @app.route('/api/auth/otp/request', methods=['POST'])
    def api_request_otp():
        """Request email OTP - Enhanced for seamless auth transitions"""
        try:
            data = request.get_json()
            email_id = data.get('email')

            if not email_id:
                return error_response("Email is required", 400)

            if not validate_email_format(email_id):
                return error_response("Invalid email format", 400)

            # Check if user exists, if not create a new user
            user = User.query.filter_by(email_id=email_id).first()
            if not user:
                # Create new user for registration
                user = User(
                    email_id=email_id,
                    name='',  # Will be filled during registration
                    mobile_no='',  # Will be filled during registration
                    status='inactive',  # Will be activated after OTP verification
                    auth_provider='manual'  # Set as manual registration
                )
                db.session.add(user)
                user_action = 'registration'
            else:
                # Enhanced: Allow OTP login regardless of original auth provider
                # This enables seamless transitions between Google and OTP auth
                user_action = 'login'

                # If user was originally Google-only, we'll allow OTP login too
                # This provides flexibility for users who want to use either method

            # Generate and send OTP
            otp = user.generate_otp()
            db.session.commit()

            # Send OTP email with appropriate context
            success, message = email_service.send_otp_email(email_id, otp, user.name or 'User')
            if not success:
                return error_response(f"Failed to send OTP: {message}", 500)

            return success_response({
                'email': email_id,
                'otp_sent': True,
                'action': user_action,  # 'registration' or 'login'
                'user_exists': user_action == 'login',
                'message': f"OTP sent for {user_action}"
            }, f"OTP sent for {user_action}")

        except Exception as e:
            db.session.rollback()
            return error_response(f"Failed to send OTP: {str(e)}", 500)



    @app.route('/api/auth/profile', methods=['GET'])
    @user_required
    def api_get_profile():
        """Get user profile"""
        try:
            user = get_current_user()
            if not user:
                return error_response("User not found", 404)

            return success_response({
                'user': user.to_dict()
            }, "Profile retrieved successfully")

        except Exception as e:
            return error_response(f"Failed to get profile: {str(e)}", 500)

    @app.route('/api/auth/profile/edit', methods=['PUT'])
    @user_required
    def api_edit_profile():
        """Edit own profile"""
        try:
            user = get_current_user()
            if not user:
                return error_response("User not found", 404)

            data = request.get_json()
            errors = {}

            # Validate and update fields
            if 'name' in data:
                name = data['name'].strip()
                is_valid_name, name_message = validate_name(name)
                if not is_valid_name:
                    errors['name'] = name_message
                else:
                    user.name = name

            if 'mobile_no' in data:
                mobile_no = data['mobile_no'].strip()
                if mobile_no and not validate_mobile_number(mobile_no):
                    errors['mobile_no'] = 'Invalid mobile number format'
                else:
                    user.mobile_no = mobile_no

            if 'color_theme' in data:
                color_theme = data['color_theme']
                if color_theme not in ['light', 'dark']:
                    errors['color_theme'] = 'Color theme must be light or dark'
                else:
                    user.color_theme = color_theme

            if 'avatar' in data:
                user.avatar = data['avatar']

            if 'address' in data:
                user.address = data['address']

            if 'gender' in data:
                if data['gender'] in ['male', 'female', 'other', None]:
                    user.gender = data['gender']
                else:
                    errors['gender'] = "Gender must be 'male', 'female', or 'other'"

            if 'date_of_birth' in data:
                try:
                    if data['date_of_birth']:
                        user.date_of_birth = datetime.strptime(data['date_of_birth'], '%Y-%m-%d').date()
                except ValueError:
                    errors['date_of_birth'] = 'Invalid date format. Use YYYY-MM-DD'

            if 'city' in data:
                user.city = data['city']

            if 'state' in data:
                user.state = data['state']

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

    @app.route('/api/auth/soft_delete', methods=['DELETE'])
    @user_required
    def api_soft_delete_account():
        """Soft delete own account"""
        try:
            user = get_current_user()
            if not user:
                return error_response("User not found", 404)

            # Soft delete by setting status to inactive
            user.status = 'inactive'
            user.clear_refresh_token()  # Clear any active sessions

            db.session.commit()

            return success_response({
                'message': 'Account has been deactivated successfully'
            }, "Account deactivated")

        except Exception as e:
            db.session.rollback()
            return error_response(f"Failed to deactivate account: {str(e)}", 500)

    # Course & Subject Management Endpoints
    @app.route('/api/courses', methods=['GET'])
    def api_get_courses():
        """List all courses (public endpoint)"""
        try:
            page = request.args.get('page', 1, type=int)
            per_page = request.args.get('per_page', 10, type=int)
            search = request.args.get('search', '').strip()

            # Build query
            query = ExamCategory.query

            if search:
                query = query.filter(ExamCategory.course_name.ilike(f'%{search}%'))

            # Paginate results
            courses = query.paginate(page=page, per_page=per_page, error_out=False)

            return success_response({
                'courses': [course.to_dict(include_subjects=False) for course in courses.items],
                'pagination': {
                    'page': courses.page,
                    'pages': courses.pages,
                    'per_page': courses.per_page,
                    'total': courses.total,
                    'has_next': courses.has_next,
                    'has_prev': courses.has_prev
                }
            }, "Courses retrieved successfully")

        except Exception as e:
            return error_response(f"Failed to get courses: {str(e)}", 500)

    @app.route('/api/courses/<int:course_id>', methods=['GET'])
    def api_get_course_by_id(course_id):
        """View course by ID (public endpoint)"""
        try:
            course = ExamCategory.query.get(course_id)
            if not course:
                return error_response("Course not found", 404)

            include_subjects = request.args.get('include_subjects', 'true').lower() == 'true'

            return success_response({
                'course': course.to_dict(include_subjects=include_subjects)
            }, "Course retrieved successfully")

        except Exception as e:
            return error_response(f"Failed to get course: {str(e)}", 500)

    @app.route('/api/subjects', methods=['GET'])
    def api_get_subjects():
        """Get subjects for a specific course (public endpoint)"""
        try:
            course_id = request.args.get('course_id', type=int)
            include_deleted = request.args.get('include_deleted', 'false').lower() == 'true'

            if not course_id:
                return error_response("course_id parameter is required", 400)

            # Check if course exists
            course = ExamCategory.query.get(course_id)
            if not course:
                return error_response("Course not found", 404)

            page = request.args.get('page', 1, type=int)
            per_page = request.args.get('per_page', 10, type=int)

            # Get subjects for the course (exclude deleted and bundles by default)
            query = ExamCategorySubject.query.filter_by(exam_category_id=course_id)
            if not include_deleted:
                query = query.filter_by(is_deleted=False)

            # Exclude bundle subjects from regular subject listing
            query = query.filter_by(is_bundle=False)

            subjects = query.paginate(page=page, per_page=per_page, error_out=False)

            return success_response({
                'subjects': [subject.to_dict() for subject in subjects.items],
                'course': course.to_dict(include_subjects=False),
                'pagination': {
                    'page': subjects.page,
                    'pages': subjects.pages,
                    'per_page': subjects.per_page,
                    'total': subjects.total,
                    'has_next': subjects.has_next,
                    'has_prev': subjects.has_prev
                }
            }, "Subjects retrieved successfully")

        except Exception as e:
            return error_response(f"Failed to get subjects: {str(e)}", 500)

    @app.route('/api/bundles', methods=['GET'])
    def api_get_bundles():
        """Get bundles for a specific course (public endpoint)"""
        try:
            course_id = request.args.get('course_id', type=int)
            include_deleted = request.args.get('include_deleted', 'false').lower() == 'true'

            if not course_id:
                return error_response("course_id parameter is required", 400)

            # Check if course exists
            course = ExamCategory.query.get(course_id)
            if not course:
                return error_response("Course not found", 404)

            # Get bundle subjects for the course
            query = ExamCategorySubject.query.filter_by(exam_category_id=course_id, is_bundle=True)
            if not include_deleted:
                query = query.filter_by(is_deleted=False)

            bundles = query.all()

            return success_response({
                'bundles': [bundle.to_dict() for bundle in bundles],
                'course': course.to_dict(include_subjects=False)
            }, "Bundles retrieved successfully")

        except Exception as e:
            return error_response(f"Failed to get bundles: {str(e)}", 500)

    @app.route('/api/admin/courses', methods=['GET'])
    @admin_required
    def api_admin_get_courses():
        """Get all courses for admin management"""
        try:
            page = request.args.get('page', 1, type=int)
            per_page = request.args.get('per_page', 50, type=int)  # Higher limit for admin

            # Get all courses with pagination
            courses_query = ExamCategory.query.order_by(ExamCategory.created_at.desc())
            courses_paginated = courses_query.paginate(
                page=page,
                per_page=per_page,
                error_out=False
            )

            courses_list = []
            for course in courses_paginated.items:
                # Get subject count for each course
                subject_count = ExamCategorySubject.query.filter_by(exam_category_id=course.id).count()

                course_data = {
                    'id': course.id,
                    'course_name': course.course_name,
                    'description': course.description,
                    'amount': float(course.amount) if course.amount else 0,
                    'offer_amount': float(course.offer_amount) if course.offer_amount else 0,
                    'max_tokens': course.max_tokens or 100,
                    'status': 'active',  # Default status
                    'subjects_count': subject_count,
                    'created_at': course.created_at.isoformat() if course.created_at else None,
                    'updated_at': course.updated_at.isoformat() if course.updated_at else None
                }
                courses_list.append(course_data)

            return success_response({
                'courses': courses_list,
                'pagination': {
                    'page': page,
                    'per_page': per_page,
                    'total': courses_paginated.total,
                    'pages': courses_paginated.pages,
                    'has_next': courses_paginated.has_next,
                    'has_prev': courses_paginated.has_prev
                }
            }, "Courses retrieved successfully")

        except Exception as e:
            return error_response(f"Failed to get courses: {str(e)}", 500)

    @app.route('/api/admin/courses', methods=['POST'])
    @admin_required
    def api_admin_add_course():
        """Add new course (Admin only)"""
        try:
            data = request.get_json()
            course_name = data.get('course_name')
            description = data.get('description', '')
            amount = data.get('amount', 0.00)
            offer_amount = data.get('offer_amount', 0.00)
            max_tokens = data.get('max_tokens', 0)

            # Validation
            if not course_name:
                return error_response("Course name is required", 400)

            if len(course_name.strip()) < 2:
                return error_response("Course name must be at least 2 characters long", 400)

            # Validate pricing
            try:
                amount = float(amount) if amount else 0.00
                offer_amount = float(offer_amount) if offer_amount else 0.00
                max_tokens = int(max_tokens) if max_tokens else 0
            except (ValueError, TypeError):
                return error_response("Invalid pricing or token values", 400)

            if amount < 0 or offer_amount < 0 or max_tokens < 0:
                return error_response("Pricing and token values must be non-negative", 400)

            # Check if course already exists
            existing_course = ExamCategory.query.filter_by(course_name=course_name.strip()).first()
            if existing_course:
                return error_response("Course with this name already exists", 409)

            # Create new course
            new_course = ExamCategory(
                course_name=course_name.strip(),
                description=description.strip() if description else None,
                amount=amount,
                offer_amount=offer_amount,
                max_tokens=max_tokens
            )

            db.session.add(new_course)
            db.session.commit()

            return success_response({
                'course': new_course.to_dict()
            }, "Course added successfully")

        except Exception as e:
            db.session.rollback()
            return error_response(f"Failed to add course: {str(e)}", 500)

    @app.route('/api/admin/courses/<int:course_id>', methods=['PUT'])
    @admin_required
    def api_admin_edit_course(course_id):
        """Edit course (Admin only)"""
        try:
            course = ExamCategory.query.get(course_id)
            if not course:
                return error_response("Course not found", 404)

            data = request.get_json()
            course_name = data.get('course_name')
            description = data.get('description')
            amount = data.get('amount')
            offer_amount = data.get('offer_amount')
            max_tokens = data.get('max_tokens')

            # Validation
            if course_name:
                if len(course_name.strip()) < 2:
                    return error_response("Course name must be at least 2 characters long", 400)

                # Check if another course with same name exists
                existing_course = ExamCategory.query.filter(
                    ExamCategory.course_name == course_name.strip(),
                    ExamCategory.id != course_id
                ).first()
                if existing_course:
                    return error_response("Course with this name already exists", 409)

                course.course_name = course_name.strip()

            if description is not None:
                course.description = description.strip() if description else None

            # Update pricing fields if provided
            if amount is not None:
                try:
                    amount = float(amount)
                    if amount < 0:
                        return error_response("Amount must be non-negative", 400)
                    course.amount = amount
                except (ValueError, TypeError):
                    return error_response("Invalid amount value", 400)

            if offer_amount is not None:
                try:
                    offer_amount = float(offer_amount)
                    if offer_amount < 0:
                        return error_response("Offer amount must be non-negative", 400)
                    course.offer_amount = offer_amount
                except (ValueError, TypeError):
                    return error_response("Invalid offer amount value", 400)

            if max_tokens is not None:
                try:
                    max_tokens = int(max_tokens)
                    if max_tokens < 0:
                        return error_response("Max tokens must be non-negative", 400)
                    course.max_tokens = max_tokens
                except (ValueError, TypeError):
                    return error_response("Invalid max tokens value", 400)

            db.session.commit()

            return success_response({
                'course': course.to_dict()
            }, "Course updated successfully")

        except Exception as e:
            db.session.rollback()
            return error_response(f"Failed to update course: {str(e)}", 500)

    @app.route('/api/admin/courses/<int:course_id>', methods=['DELETE'])
    @admin_required
    def api_admin_delete_course(course_id):
        """Delete course (Admin only)"""
        try:
            course = ExamCategory.query.get(course_id)
            if not course:
                return error_response("Course not found", 404)

            # Check if course has any purchases
            purchases = ExamCategoryPurchase.query.filter_by(exam_category_id=course_id).first()
            if purchases:
                return error_response("Cannot delete course with existing purchases", 400)

            db.session.delete(course)
            db.session.commit()

            return success_response({
                'message': 'Course deleted successfully'
            }, "Course deleted successfully")

        except Exception as e:
            db.session.rollback()
            return error_response(f"Failed to delete course: {str(e)}", 500)

    @app.route('/api/admin/subjects', methods=['POST'])
    @admin_required
    def api_admin_add_subject():
        """Add new subject to course (Admin only)"""
        try:
            data = request.get_json()
            course_id = data.get('course_id')
            subject_name = data.get('subject_name')
            amount = data.get('amount', 0.00)
            offer_amount = data.get('offer_amount', 0.00)
            max_tokens = data.get('max_tokens', 100)
            total_mock = data.get('total_mock', 50)
            is_bundle = data.get('is_bundle', False)

            if not course_id or not subject_name:
                return error_response("course_id and subject_name are required", 400)

            # Check if course exists
            course = ExamCategory.query.get(course_id)
            if not course:
                return error_response("Course not found", 404)

            # Validation
            is_valid_subject, subject_message = validate_subject_name(subject_name)
            if not is_valid_subject:
                return error_response(subject_message, 400)

            is_valid_amount, amount_message = validate_price(amount)
            if not is_valid_amount:
                return error_response(f"Amount: {amount_message}", 400)

            is_valid_offer, offer_message = validate_price(offer_amount)
            if not is_valid_offer:
                return error_response(f"Offer amount: {offer_message}", 400)

            is_valid_tokens, tokens_message = validate_token_count(max_tokens)
            if not is_valid_tokens:
                return error_response(f"Max tokens: {tokens_message}", 400)

            is_valid_mock, mock_message = validate_mock_test_count(total_mock)
            if not is_valid_mock:
                return error_response(f"Total mock tests: {mock_message}", 400)

            # Convert to proper types
            amount = float(amount) if amount else 0.00
            offer_amount = float(offer_amount) if offer_amount else 0.00
            max_tokens = int(max_tokens) if max_tokens else 100
            total_mock = int(total_mock) if total_mock else 50

            # Check if subject already exists in this course
            existing_subject = ExamCategorySubject.query.filter_by(
                exam_category_id=course_id,
                subject_name=subject_name.strip()
            ).first()
            if existing_subject:
                return error_response("Subject already exists in this course", 409)

            # Create new subject
            new_subject = ExamCategorySubject(
                exam_category_id=course_id,
                subject_name=subject_name.strip(),
                amount=amount,
                offer_amount=offer_amount,
                max_tokens=max_tokens,
                total_mock=total_mock,
                is_bundle=is_bundle
            )

            db.session.add(new_subject)
            db.session.commit()

            return success_response({
                'subject': new_subject.to_dict()
            }, "Subject added successfully")

        except Exception as e:
            db.session.rollback()
            return error_response(f"Failed to add subject: {str(e)}", 500)

    @app.route('/api/admin/subjects/<int:subject_id>', methods=['PUT'])
    @admin_required
    def api_admin_edit_subject(subject_id):
        """Edit subject (Admin only)"""
        try:
            subject = ExamCategorySubject.query.get(subject_id)
            if not subject:
                return error_response("Subject not found", 404)

            data = request.get_json()
            subject_name = data.get('subject_name')
            amount = data.get('amount')
            offer_amount = data.get('offer_amount')
            max_tokens = data.get('max_tokens')
            total_mock = data.get('total_mock')
            is_bundle = data.get('is_bundle')
            is_deleted = data.get('is_deleted')

            # Validation for subject name
            if subject_name:
                if len(subject_name.strip()) < 2:
                    return error_response("Subject name must be at least 2 characters long", 400)

                # Check if another subject with same name exists in the same course
                existing_subject = ExamCategorySubject.query.filter(
                    ExamCategorySubject.exam_category_id == subject.exam_category_id,
                    ExamCategorySubject.subject_name == subject_name.strip(),
                    ExamCategorySubject.id != subject_id
                ).first()
                if existing_subject:
                    return error_response("Subject with this name already exists in this course", 409)

                subject.subject_name = subject_name.strip()

            # Update pricing fields if provided
            if amount is not None:
                try:
                    amount = float(amount)
                    if amount < 0:
                        return error_response("Amount must be non-negative", 400)
                    subject.amount = amount
                except (ValueError, TypeError):
                    return error_response("Invalid amount value", 400)

            if offer_amount is not None:
                try:
                    offer_amount = float(offer_amount)
                    if offer_amount < 0:
                        return error_response("Offer amount must be non-negative", 400)
                    subject.offer_amount = offer_amount
                except (ValueError, TypeError):
                    return error_response("Invalid offer amount value", 400)

            if max_tokens is not None:
                try:
                    max_tokens = int(max_tokens)
                    if max_tokens < 0:
                        return error_response("Max tokens must be non-negative", 400)
                    subject.max_tokens = max_tokens
                except (ValueError, TypeError):
                    return error_response("Invalid max tokens value", 400)

            if total_mock is not None:
                try:
                    total_mock = int(total_mock)
                    if total_mock < 0:
                        return error_response("Total mock tests must be non-negative", 400)
                    subject.total_mock = total_mock
                except (ValueError, TypeError):
                    return error_response("Invalid total mock tests value", 400)

            if is_bundle is not None:
                subject.is_bundle = bool(is_bundle)

            if is_deleted is not None:
                subject.is_deleted = bool(is_deleted)

            db.session.commit()

            return success_response({
                'subject': subject.to_dict()
            }, "Subject updated successfully")

        except Exception as e:
            db.session.rollback()
            return error_response(f"Failed to update subject: {str(e)}", 500)

    @app.route('/api/admin/subjects/<int:subject_id>', methods=['DELETE'])
    @admin_required
    def api_admin_delete_subject(subject_id):
        """Soft delete subject (Admin only)"""
        try:
            subject = ExamCategorySubject.query.get(subject_id)
            if not subject:
                return error_response("Subject not found", 404)

            # Soft delete the subject
            subject.is_deleted = True
            db.session.commit()

            return success_response({
                'message': 'Subject deleted successfully',
                'subject_id': subject_id,
                'subject_name': subject.subject_name
            }, "Subject deleted successfully")

        except Exception as e:
            db.session.rollback()
            return error_response(f"Failed to delete subject: {str(e)}", 500)

    # Community Blog Endpoints
    @app.route('/api/community/posts', methods=['GET'])
    def api_get_community_posts():
        """List all posts in community (public endpoint)"""
        try:
            page = request.args.get('page', 1, type=int)
            per_page = request.args.get('per_page', 10, type=int)
            search = request.args.get('search', '').strip()
            tags = request.args.get('tags', '').strip()
            featured = request.args.get('featured', '').lower()

            # Build query - exclude deleted posts
            query = BlogPost.query.filter_by(status='published', is_deleted=False)

            if search:
                query = query.filter(
                    db.or_(
                        BlogPost.title.ilike(f'%{search}%'),
                        BlogPost.content.ilike(f'%{search}%')
                    )
                )

            if tags:
                query = query.filter(BlogPost.tags.ilike(f'%{tags}%'))

            if featured == 'true':
                query = query.filter_by(is_featured=True)

            # Order by creation date (newest first)
            query = query.order_by(BlogPost.created_at.desc())

            # Paginate results
            posts = query.paginate(page=page, per_page=per_page, error_out=False)

            # Get current user for like status (if authenticated)
            current_user = None
            try:
                current_user = get_current_user()
            except:
                pass  # Not authenticated, that's fine

            # Add user-specific like status and inline comments to posts
            posts_data = []
            for post in posts.items:
                post_dict = post.to_dict(include_user=True)

                # Check if current user liked this post
                if current_user:
                    user_like = BlogLike.query.filter_by(
                        user_id=current_user.id,
                        post_id=post.id
                    ).first()
                    post_dict['is_liked'] = user_like is not None
                else:
                    post_dict['is_liked'] = False

                # Get recent comments for inline display (limit to 3 most recent)
                recent_comments = BlogComment.query.filter_by(
                    post_id=post.id,
                    is_deleted=False,
                    parent_comment_id=None  # Only top-level comments for now
                ).order_by(BlogComment.created_at.desc()).limit(3).all()

                post_dict['recent_comments'] = []
                for comment in recent_comments:
                    comment_dict = comment.to_dict(include_user=True)
                    post_dict['recent_comments'].append(comment_dict)

                posts_data.append(post_dict)

            return success_response({
                'posts': posts_data,
                'pagination': {
                    'page': posts.page,
                    'pages': posts.pages,
                    'per_page': posts.per_page,
                    'total': posts.total,
                    'has_next': posts.has_next,
                    'has_prev': posts.has_prev
                }
            }, "Posts retrieved successfully")

        except Exception as e:
            return error_response(f"Failed to get posts: {str(e)}", 500)

    @app.route('/api/community/posts/<int:post_id>/comments', methods=['GET'])
    def api_get_post_comments(post_id):
        """Get comments for a specific post (public endpoint)"""
        try:
            page = request.args.get('page', 1, type=int)
            per_page = request.args.get('per_page', 20, type=int)

            # Check if post exists and is not deleted
            post = BlogPost.query.filter_by(id=post_id, is_deleted=False).first()
            if not post:
                return error_response("Post not found", 404)

            # Get comments for the post, excluding deleted ones
            query = BlogComment.query.filter_by(post_id=post_id, is_deleted=False)
            query = query.order_by(BlogComment.created_at.asc())

            # Paginate results
            comments = query.paginate(page=page, per_page=per_page, error_out=False)

            return success_response({
                'comments': [comment.to_dict(include_user=True, include_replies=True) for comment in comments.items],
                'pagination': {
                    'page': comments.page,
                    'pages': comments.pages,
                    'per_page': comments.per_page,
                    'total': comments.total,
                    'has_next': comments.has_next,
                    'has_prev': comments.has_prev
                }
            }, "Comments retrieved successfully")

        except Exception as e:
            return error_response(f"Failed to get comments: {str(e)}", 500)

    @app.route('/api/community/posts', methods=['POST'])
    @user_required
    def api_create_community_post():
        """Create a new post with optional image upload"""
        import os
        import uuid
        from werkzeug.utils import secure_filename

        try:
            user = get_current_user()
            if not user:
                return error_response("User not found", 404)

            # Handle both JSON and form data
            if request.content_type and 'multipart/form-data' in request.content_type:
                # Form data with file upload
                title = request.form.get('title', '').strip()
                content = request.form.get('content', '').strip()
                tags_input = request.form.get('tags', '')
                image_file = request.files.get('image')
            else:
                # JSON data (no file upload)
                data = request.get_json()
                title = data.get('title', '').strip()
                content = data.get('content', '').strip()
                tags_input = data.get('tags', '')
                image_file = None

            # Handle tags - can be either string or array from frontend
            if isinstance(tags_input, list):
                # Frontend sends array of tags
                tags = ','.join([str(tag).strip() for tag in tags_input if str(tag).strip()])
            else:
                # Fallback for string input
                tags = str(tags_input).strip()

            # Validation
            is_valid_title, title_message = validate_blog_title(title)
            if not is_valid_title:
                return error_response(title_message, 400)

            is_valid_content, content_message = validate_blog_content(content)
            if not is_valid_content:
                return error_response(content_message, 400)

            is_valid_tags, tags_message = validate_tags(tags)
            if not is_valid_tags:
                return error_response(tags_message, 400)

            # Handle image upload
            image_url = None
            if image_file and image_file.filename:
                # Validate file type
                allowed_extensions = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
                file_extension = image_file.filename.rsplit('.', 1)[1].lower() if '.' in image_file.filename else ''

                if file_extension not in allowed_extensions:
                    return error_response("Invalid file type. Only PNG, JPG, JPEG, GIF, and WebP are allowed.", 400)

                # Generate unique filename
                filename = f"{uuid.uuid4().hex}.{file_extension}"

                # Ensure assets/images directory exists
                upload_dir = os.path.join(os.getcwd(), 'assets', 'images')
                os.makedirs(upload_dir, exist_ok=True)

                # Save file
                file_path = os.path.join(upload_dir, filename)
                image_file.save(file_path)

                # Store relative path for database
                image_url = f"/assets/images/{filename}"

            # Create new post
            new_post = BlogPost(
                user_id=user.id,
                title=title,
                content=content,
                tags=tags if tags else None,
                image_url=image_url,
                status='published'
            )

            db.session.add(new_post)
            db.session.commit()

            return success_response({
                'post': new_post.to_dict(include_user=True)
            }, "Post created successfully")

        except Exception as e:
            db.session.rollback()
            return error_response(f"Failed to create post: {str(e)}", 500)

    @app.route('/assets/images/<filename>')
    def serve_uploaded_image(filename):
        """Serve uploaded images"""
        import os
        from flask import send_from_directory

        upload_dir = os.path.join(os.getcwd(), 'assets', 'images')
        return send_from_directory(upload_dir, filename)

    @app.route('/api/community/posts/<int:post_id>/like', methods=['POST'])
    @user_required
    def api_like_post(post_id):
        """Like a post"""
        try:
            user = get_current_user()
            if not user:
                return error_response("User not found", 404)

            post = BlogPost.query.get(post_id)
            if not post:
                return error_response("Post not found", 404)

            # Check if user already liked this post
            existing_like = BlogLike.query.filter_by(user_id=user.id, post_id=post_id).first()

            if existing_like:
                # Unlike the post
                db.session.delete(existing_like)
                post.likes_count = max(0, post.likes_count - 1)
                liked = False
            else:
                # Like the post
                new_like = BlogLike(user_id=user.id, post_id=post_id)
                db.session.add(new_like)
                post.likes_count += 1
                liked = True

            db.session.commit()

            return success_response({
                'liked': liked,
                'likes_count': post.likes_count
            }, "Post like status updated")

        except Exception as e:
            db.session.rollback()
            return error_response(f"Failed to update like status: {str(e)}", 500)

    @app.route('/api/community/posts/<int:post_id>/comment', methods=['POST'])
    @user_required
    def api_add_comment(post_id):
        """Add a comment to a post"""
        try:
            user = get_current_user()
            if not user:
                return error_response("User not found", 404)

            post = BlogPost.query.get(post_id)
            if not post:
                return error_response("Post not found", 404)

            data = request.get_json()
            content = data.get('content', '').strip()
            parent_comment_id = data.get('parent_comment_id')

            # Validation
            if not content or not isinstance(content, str):
                return error_response("Comment content is required", 400)

            if len(content) < 3:
                return error_response("Comment must be at least 3 characters long", 400)

            if len(content) > 1000:
                return error_response("Comment must be less than 1000 characters", 400)

            # If replying to a comment, check if parent comment exists
            if parent_comment_id:
                parent_comment = BlogComment.query.get(parent_comment_id)
                if not parent_comment or parent_comment.post_id != post_id:
                    return error_response("Parent comment not found", 404)

            # Create new comment
            new_comment = BlogComment(
                user_id=user.id,
                post_id=post_id,
                parent_comment_id=parent_comment_id,
                content=content
            )

            db.session.add(new_comment)

            # Update post comments count
            post.comments_count += 1

            db.session.commit()

            return success_response({
                'comment': new_comment.to_dict(include_user=True)
            }, "Comment added successfully")

        except Exception as e:
            db.session.rollback()
            return error_response(f"Failed to add comment: {str(e)}", 500)

    @app.route('/api/community/comments/<int:comment_id>', methods=['DELETE'])
    @user_required
    def api_delete_comment(comment_id):
        """Delete own comment"""
        try:
            user = get_current_user()
            if not user:
                return error_response("User not found", 404)

            comment = BlogComment.query.get(comment_id)
            if not comment:
                return error_response("Comment not found", 404)

            # Check if user owns the comment
            if comment.user_id != user.id:
                return error_response("You can only delete your own comments", 403)

            # Soft delete the comment
            comment.is_deleted = True

            # Get the post to update comment count
            post = BlogPost.query.get(comment.post_id)
            if post:
                post.comments_count = max(0, post.comments_count - 1)

            db.session.commit()

            return success_response({
                'message': 'Comment deleted successfully'
            }, "Comment deleted successfully")

        except Exception as e:
            db.session.rollback()
            return error_response(f"Failed to delete comment: {str(e)}", 500)

    @app.route('/api/community/posts/<int:post_id>', methods=['DELETE'])
    @user_required
    def api_delete_post(post_id):
        """Delete own post"""
        try:
            user = get_current_user()
            if not user:
                return error_response("User not found", 404)

            post = BlogPost.query.get(post_id)
            if not post:
                return error_response("Post not found", 404)

            # Check if user owns the post
            if post.user_id != user.id:
                return error_response("You can only delete your own posts", 403)

            # Soft delete the post
            post.is_deleted = True
            db.session.commit()

            return success_response({
                'message': 'Post deleted successfully'
            }, "Post deleted successfully")

        except Exception as e:
            db.session.rollback()
            return error_response(f"Failed to delete post: {str(e)}", 500)

    # Admin Moderation Endpoints
    @app.route('/api/admin/posts', methods=['GET'])
    @admin_required
    def api_admin_get_posts():
        """Get all posts for admin moderation (Admin only) - includes deleted posts"""
        try:
            page = request.args.get('page', 1, type=int)
            per_page = request.args.get('per_page', 10, type=int)
            search = request.args.get('search', '').strip()
            status = request.args.get('status', '').strip()
            is_deleted = request.args.get('is_deleted', '').strip().lower()

            # Build query - include deleted posts for admin view
            query = BlogPost.query

            if search:
                query = query.filter(
                    db.or_(
                        BlogPost.title.ilike(f'%{search}%'),
                        BlogPost.content.ilike(f'%{search}%'),
                        BlogPost.user.has(User.name.ilike(f'%{search}%'))
                    )
                )

            if status:
                query = query.filter_by(status=status)

            # Filter by deletion status
            if is_deleted == 'true':
                query = query.filter_by(is_deleted=True)
            elif is_deleted == 'false':
                query = query.filter_by(is_deleted=False)
            # If not specified, show all (both deleted and non-deleted)

            # Order by newest first
            query = query.order_by(BlogPost.created_at.desc())

            # Paginate results
            posts = query.paginate(page=page, per_page=per_page, error_out=False)

            result_data = []
            for post in posts.items:
                result_data.append(post.to_dict(include_user=True))

            return success_response({
                'posts': result_data,
                'pagination': {
                    'page': posts.page,
                    'pages': posts.pages,
                    'total': posts.total,
                    'per_page': posts.per_page
                }
            }, "Posts retrieved successfully")

        except Exception as e:
            return error_response(f"Failed to get posts: {str(e)}", 500)

    @app.route('/api/admin/posts/<int:post_id>', methods=['PUT'])
    @admin_required
    def api_admin_edit_post(post_id):
        """Edit any post (Admin only)"""
        try:
            post = BlogPost.query.get(post_id)
            if not post:
                return error_response("Post not found", 404)

            data = request.get_json()
            title = data.get('title')
            content = data.get('content')
            tags = data.get('tags')
            status = data.get('status')
            is_featured = data.get('is_featured')

            # Update fields if provided
            if title:
                if len(title.strip()) < 5:
                    return error_response("Title must be at least 5 characters long", 400)
                post.title = title.strip()

            if content:
                if len(content.strip()) < 10:
                    return error_response("Content must be at least 10 characters long", 400)
                post.content = content.strip()

            if tags is not None:
                post.tags = tags.strip() if tags else None

            if status and status in ['draft', 'published', 'archived']:
                post.status = status

            if is_featured is not None:
                post.is_featured = bool(is_featured)

            db.session.commit()

            return success_response({
                'post': post.to_dict(include_user=True)
            }, "Post updated successfully")

        except Exception as e:
            db.session.rollback()
            return error_response(f"Failed to update post: {str(e)}", 500)

    @app.route('/api/admin/posts/<int:post_id>', methods=['DELETE'])
    @admin_required
    def api_admin_delete_post(post_id):
        """Delete any post (Admin only)"""
        try:
            post = BlogPost.query.get(post_id)
            if not post:
                return error_response("Post not found", 404)

            # Soft delete the post
            post.is_deleted = True
            db.session.commit()

            return success_response({
                'message': 'Post deleted successfully'
            }, "Post deleted successfully")

        except Exception as e:
            db.session.rollback()
            return error_response(f"Failed to delete post: {str(e)}", 500)

    @app.route('/api/admin/comments/<int:comment_id>', methods=['PUT'])
    @admin_required
    def api_admin_edit_comment(comment_id):
        """Edit any comment (Admin only)"""
        try:
            comment = BlogComment.query.get(comment_id)
            if not comment:
                return error_response("Comment not found", 404)

            data = request.get_json()
            content = data.get('content')

            if not content or len(content.strip()) < 3:
                return error_response("Comment must be at least 3 characters long", 400)

            comment.content = content.strip()
            db.session.commit()

            return success_response({
                'comment': comment.to_dict(include_user=True)
            }, "Comment updated successfully")

        except Exception as e:
            db.session.rollback()
            return error_response(f"Failed to update comment: {str(e)}", 500)

    @app.route('/api/admin/comments', methods=['GET'])
    @admin_required
    def api_admin_get_comments():
        """Get all comments for admin moderation (Admin only)"""
        try:
            page = request.args.get('page', 1, type=int)
            per_page = request.args.get('per_page', 10, type=int)
            search = request.args.get('search', '').strip()
            is_deleted = request.args.get('is_deleted', '').strip().lower()

            # Build query - include deleted comments for admin view
            query = BlogComment.query

            if search:
                query = query.filter(
                    db.or_(
                        BlogComment.content.ilike(f'%{search}%'),
                        BlogComment.user.has(User.name.ilike(f'%{search}%'))
                    )
                )

            # Filter by deletion status
            if is_deleted == 'true':
                query = query.filter_by(is_deleted=True)
            elif is_deleted == 'false':
                query = query.filter_by(is_deleted=False)
            # If not specified, show all (both deleted and non-deleted)

            # Order by newest first
            query = query.order_by(BlogComment.created_at.desc())

            # Paginate results
            comments = query.paginate(page=page, per_page=per_page, error_out=False)

            result_data = []
            for comment in comments.items:
                result_data.append(comment.to_dict(include_user=True, include_post=True))

            return success_response({
                'comments': result_data,
                'pagination': {
                    'page': comments.page,
                    'pages': comments.pages,
                    'total': comments.total,
                    'per_page': comments.per_page
                }
            }, "Comments retrieved successfully")

        except Exception as e:
            return error_response(f"Failed to get comments: {str(e)}", 500)

    @app.route('/api/admin/comments/<int:comment_id>', methods=['DELETE'])
    @admin_required
    def api_admin_delete_comment(comment_id):
        """Delete any comment (Admin only)"""
        try:
            comment = BlogComment.query.get(comment_id)
            if not comment:
                return error_response("Comment not found", 404)

            # Soft delete the comment
            comment.is_deleted = True

            # Get the post to update comment count
            post = BlogPost.query.get(comment.post_id)
            if post:
                post.comments_count = max(0, post.comments_count - 1)

            db.session.commit()

            return success_response({
                'message': 'Comment deleted successfully'
            }, "Comment deleted successfully")

        except Exception as e:
            db.session.rollback()
            return error_response(f"Failed to delete comment: {str(e)}", 500)

    # Enhanced AI Token Management System
    def get_user_token_limits(user):
        """Get user's daily token limits based on purchases - Enhanced for accurate limits"""
        from shared.models.purchase import ExamCategoryPurchase

        # Enhanced token limits as per requirements:
        # Normal users: 1000 tokens/day (increased for testing)
        # Single subject purchased: 2000 tokens/day (increased for testing)
        # Complete bundle purchased: Unlimited tokens

        base_limit = 1000  # Normal users (increased for testing)

        # Check if user has purchased any courses or subjects
        purchases = ExamCategoryPurchase.query.filter_by(
            user_id=user.id,
            status='active'
        ).all()

        if not purchases:
            return base_limit  # Normal user - 50 tokens/day

        has_full_bundle = False
        has_single_subject = False

        for purchase in purchases:
            # Check for full bundle purchase (unlimited tokens)
            if purchase.purchase_type == 'full_bundle' or purchase.chatbot_tokens_unlimited:
                has_full_bundle = True
                break
            elif purchase.purchase_type == 'single_subject' or purchase.subject_id:
                has_single_subject = True

        if has_full_bundle:
            return 0  # Unlimited tokens (0 means unlimited)
        elif has_single_subject:
            return 2000  # Single subject purchase - 2000 tokens/day (increased for testing)
        else:
            return base_limit  # Default - 50 tokens/day

    def check_daily_token_limit(user, tokens_needed=1):
        """Enhanced daily token limit checking with midnight refresh"""
        from datetime import datetime, timezone

        # Get current time in UTC for consistent timezone handling
        now = datetime.utcnow()
        today = now.date()

        # Get today's token usage (refreshed at midnight UTC)
        today_usage = db.session.query(db.func.sum(AIChatHistory.tokens_used)).filter(
            AIChatHistory.user_id == user.id,
            db.func.date(AIChatHistory.created_at) == today
        ).scalar() or 0

        # Get user's token limit
        token_limit = get_user_token_limits(user)

        # Unlimited tokens (0 means unlimited for bundle purchases)
        if token_limit == 0:
            return True, token_limit, today_usage

        # Check if user has enough tokens
        if today_usage + tokens_needed <= token_limit:
            return True, token_limit, today_usage
        else:
            return False, token_limit, today_usage

    def calculate_message_tokens(message, response=""):
        """Enhanced token calculation for more accurate tracking"""
        # More accurate token estimation:
        # - Input message: ~1 token per 4 characters
        # - Response: ~1 token per 4 characters
        # - Add base overhead for processing

        input_tokens = max(1, len(message) // 4)
        response_tokens = max(1, len(response) // 4) if response else 10  # Estimated response
        overhead_tokens = 5  # Base processing overhead

        total_tokens = input_tokens + response_tokens + overhead_tokens
        return max(1, total_tokens)  # Minimum 1 token

    def is_educational_query(message):
        """Enhanced educational query filtering"""
        message_lower = message.lower().strip()

        # Handle greetings and short responses
        if len(message_lower) <= 10:
            greetings = ['hi', 'hello', 'hey', 'thanks', 'thank you', 'bye', 'goodbye']
            if any(greeting in message_lower for greeting in greetings):
                return True  # Allow greetings but with minimal response

        # Educational keywords (expanded list)
        educational_keywords = [
            # Subjects
            'physics', 'chemistry', 'biology', 'mathematics', 'math', 'science',
            'history', 'geography', 'english', 'literature', 'computer', 'programming',

            # Educational terms
            'explain', 'what is', 'how does', 'why', 'define', 'formula', 'equation',
            'solve', 'calculate', 'theory', 'concept', 'principle', 'law', 'rule',
            'example', 'diagram', 'process', 'method', 'technique', 'study', 'learn',
            'understand', 'homework', 'assignment', 'exam', 'test', 'question',

            # Academic levels
            'class', 'grade', 'school', 'college', 'university', 'course', 'subject'
        ]

        # Check if message contains educational keywords
        if any(keyword in message_lower for keyword in educational_keywords):
            return True

        # Check for question patterns
        question_patterns = ['what', 'how', 'why', 'when', 'where', 'which', 'who']
        if any(pattern in message_lower for pattern in question_patterns):
            return True

        # If message is longer than 20 characters, assume it's educational
        if len(message_lower) > 20:
            return True

        return False

    def update_user_token_consumption(user, tokens_consumed, message, response, session_id, response_time):
        """Update user's token consumption in database with proper tracking"""
        try:
            # Save chat history with actual token consumption
            chat_history = AIChatHistory(
                user_id=user.id,
                session_id=session_id,
                message=message,
                response=response,
                tokens_used=tokens_consumed,
                response_time=response_time,
                is_academic=True
            )
            db.session.add(chat_history)

            # Update user AI stats for the current month
            current_month = datetime.utcnow().strftime('%Y-%m')
            user_stats = UserAIStats.query.filter_by(user_id=user.id, month_year=current_month).first()

            if not user_stats:
                user_stats = UserAIStats(
                    user_id=user.id,
                    month_year=current_month,
                    total_queries=1,
                    total_tokens_used=tokens_consumed,
                    monthly_queries=1,
                    monthly_tokens_used=tokens_consumed,
                    last_query_date=datetime.utcnow()
                )
                db.session.add(user_stats)
            else:
                user_stats.total_queries += 1
                user_stats.total_tokens_used += tokens_consumed
                user_stats.monthly_queries += 1
                user_stats.monthly_tokens_used += tokens_consumed
                user_stats.last_query_date = datetime.utcnow()

            # Commit the transaction
            db.session.commit()

            print(f"✅ Updated token consumption: User {user.id} consumed {tokens_consumed} tokens")
            return True

        except Exception as e:
            db.session.rollback()
            print(f"❌ Failed to update token consumption: {str(e)}")
            return False

    def save_chat_history_and_update_stats(user, message, response, tokens_consumed, session_id):
        """Save chat history and update user AI statistics"""
        try:
            # Save chat history with actual token consumption
            chat_history = AIChatHistory(
                user_id=user.id,
                session_id=session_id,
                message=message,
                response=response,
                tokens_used=tokens_consumed,
                is_academic=True
            )
            db.session.add(chat_history)

            # Update user AI stats for the current month
            current_month = datetime.utcnow().strftime('%Y-%m')
            user_stats = UserAIStats.query.filter_by(user_id=user.id, month_year=current_month).first()

            if not user_stats:
                user_stats = UserAIStats(
                    user_id=user.id,
                    month_year=current_month,
                    total_queries=1,
                    total_tokens_used=tokens_consumed,
                    monthly_queries=1,
                    monthly_tokens_used=tokens_consumed,
                    last_query_date=datetime.utcnow()
                )
                db.session.add(user_stats)
            else:
                user_stats.total_queries += 1
                user_stats.total_tokens_used += tokens_consumed
                user_stats.monthly_queries += 1
                user_stats.monthly_tokens_used += tokens_consumed
                user_stats.last_query_date = datetime.utcnow()

            db.session.commit()
            print(f"✅ Chat history saved and stats updated for user {user.id}")
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error saving chat history: {e}")
            # Don't fail the request if history saving fails

    def get_real_time_token_usage(user):
        """Get user's real-time token usage for today"""
        today = datetime.utcnow().date()

        today_usage = db.session.query(db.func.sum(AIChatHistory.tokens_used)).filter(
            AIChatHistory.user_id == user.id,
            db.func.date(AIChatHistory.created_at) == today
        ).scalar() or 0

        token_limit = get_user_token_limits(user)
        remaining_tokens = max(0, token_limit - today_usage) if token_limit > 0 else float('inf')

        return {
            'tokens_used_today': today_usage,
            'token_limit': token_limit,
            'remaining_tokens': remaining_tokens,
            'unlimited': token_limit == 0
        }







    # Backward Compatibility AI Endpoints
    @app.route('/api/ai/token-status', methods=['GET'])
    @user_required
    def api_ai_token_status():
        """Get current user's AI token usage and limits (backward compatibility)"""
        try:
            user = get_current_user()
            if not user:
                return error_response("User not found", 404)

            # Get real-time token usage
            token_info = get_real_time_token_usage(user)

            # Format response to match expected frontend format
            response_data = {
                'tokens_used_today': token_info['tokens_used_today'],
                'daily_limit': token_info['token_limit'],
                'remaining_tokens': token_info['remaining_tokens'] if token_info['remaining_tokens'] != float('inf') else token_info['token_limit'],
                'is_unlimited': token_info['unlimited']
            }

            return success_response(response_data, "Token status retrieved successfully")

        except Exception as e:
            return error_response(f"Failed to get token status: {str(e)}", 500)

    @app.route('/api/ai/chat', methods=['POST'])
    @user_required
    def api_ai_chat():
        """AI chatbot conversation (backward compatibility endpoint)"""
        try:
            user = get_current_user()
            if not user:
                return error_response("User not found", 404)

            data = request.get_json()
            message = data.get('message', '').strip()
            session_id = data.get('session_id', str(uuid.uuid4()))
            is_academic = data.get('is_academic', True)

            # Validation
            if not message or len(message) < 3:
                return error_response("Message must be at least 3 characters long", 400)

            # Check token limits
            can_proceed, token_limit, tokens_used_today = check_daily_token_limit(user, tokens_needed=1)
            if not can_proceed:
                return error_response(
                    f"Daily token limit exceeded. You have used {tokens_used_today}/{token_limit} tokens today. Purchase a course or subject to get more tokens.",
                    429
                )

            print(f"🤖 AI Chat (Legacy) - User: {user.id}, Message: {message[:50]}...")

            # Use new RAG service for backward compatibility
            from shared.services.rag_service import get_rag_service

            rag_service = get_rag_service(
                ollama_model=app.config.get('RAG_OLLAMA_MODEL', 'llama3.2:1b'),
                top_k_results=app.config.get('RAG_TOP_K_RESULTS', 3),
                similarity_threshold=app.config.get('RAG_SIMILARITY_THRESHOLD', 0.01)
            )

            # Generate response using new RAG pipeline
            import time
            import threading

            start_time = time.time()
            result = None
            error_occurred = None

            def generate_response():
                nonlocal result, error_occurred
                try:
                    result = rag_service.generate_chat_response(
                        query=message,
                        subject=None,  # No subject filtering for general chat
                        session_id=session_id
                    )
                except Exception as e:
                    error_occurred = str(e)

            # Run with timeout using threading
            thread = threading.Thread(target=generate_response)
            thread.daemon = True
            thread.start()
            thread.join(timeout=15)  # 15 second timeout for faster response

            if thread.is_alive():
                return error_response("AI response generation timed out. Please try a shorter question.", 408)

            if error_occurred:
                return error_response(f"Error generating response: {error_occurred}", 500)

            if not result:
                return error_response("Failed to generate response", 500)

            response_time = time.time() - start_time

            if not result['success']:
                return error_response(result['error'], 500)

            # Estimate tokens used (approximate)
            tokens_consumed = max(1, len(result['response']) // 4)  # Rough estimate: 4 chars per token

            # Save chat history and update stats
            save_chat_history_and_update_stats(user, message, result['response'], tokens_consumed, session_id)

            # Get updated token info
            updated_token_info = get_real_time_token_usage(user)

            # Format response to match expected frontend format
            response_data = {
                'response': result['response'],
                'session_id': session_id,
                'response_time': response_time,
                'sources': result.get('sources', []),
                'model_used': result.get('model_used', 'llama3.2:1b'),
                'token_info': {
                    'tokens_used_today': updated_token_info['tokens_used_today'],
                    'daily_limit': updated_token_info['token_limit'],
                    'remaining_tokens': updated_token_info['remaining_tokens'] if updated_token_info['remaining_tokens'] != float('inf') else updated_token_info['token_limit']
                }
            }

            return success_response(response_data, "AI response generated successfully")

        except Exception as e:
            return error_response(f"Failed to generate AI response: {str(e)}", 500)

    # New RAG-based AI Endpoints
    @app.route('/api/mcq/generate', methods=['POST'])
    @user_required
    def api_generate_mcq():
        """Generate MCQ questions using new RAG pipeline"""
        try:
            user = get_current_user()
            if not user:
                return error_response("User not found", 404)

            data = request.get_json()
            subject = data.get('subject', '').strip().lower()
            num_questions = data.get('num_questions', 5)
            difficulty = data.get('difficulty', 'hard')

            # Validation
            if not subject:
                return error_response("Subject is required", 400)

            if not isinstance(num_questions, int) or num_questions < 1 or num_questions > 20:
                return error_response("Number of questions must be between 1 and 20", 400)

            if difficulty not in ['easy', 'medium', 'hard']:
                return error_response("Difficulty must be 'easy', 'medium', or 'hard'", 400)

            # Valid subjects
            valid_subjects = ['physics', 'chemistry', 'biology', 'mathematics', 'computer_science']
            if subject not in valid_subjects:
                return error_response(f"Subject must be one of: {', '.join(valid_subjects)}", 400)

            print(f"🚀 New MCQ Generation - User: {user.id}, Subject: {subject}, Questions: {num_questions}")

            # Use optimized three-layer RAG service
            from shared.services.rag_service import get_rag_service

            rag_service = get_rag_service(
                ollama_model=app.config.get('RAG_OLLAMA_MODEL', 'llama3.2:1b'),
                top_k_results=app.config.get('RAG_TOP_K_RESULTS', 5),
                similarity_threshold=app.config.get('RAG_SIMILARITY_THRESHOLD', 0.2)
            )

            # Generate MCQs using new RAG pipeline
            import time
            start_time = time.time()

            result = rag_service.generate_mcq_questions(
                subject=subject,
                num_questions=num_questions,
                difficulty=difficulty
            )

            generation_time = time.time() - start_time

            if not result['success']:
                return error_response(result['error'], 500)

            questions = result['questions']

            # Save to database if questions were generated
            if questions:
                try:
                    for q_data in questions:
                        question = ExamCategoryQuestion(
                            user_id=user.id,
                            question=q_data.get('question', ''),
                            option_1=q_data.get('option_a', ''),
                            option_2=q_data.get('option_b', ''),
                            option_3=q_data.get('option_c', ''),
                            option_4=q_data.get('option_d', ''),
                            correct_answer=q_data.get('correct_answer', 'A'),
                            explanation=q_data.get('explanation', ''),
                            is_ai_generated=True,
                            ai_model_used=result['model_used'],
                            difficulty_level=difficulty,
                            source_content=f"Generated from {subject} PDFs using RAG pipeline"
                        )
                        db.session.add(question)

                    db.session.commit()
                    print(f"✅ Saved {len(questions)} questions to database")
                except Exception as e:
                    db.session.rollback()
                    print(f"⚠️ Failed to save questions to database: {str(e)}")

            return success_response({
                'questions': questions,
                'total_generated': len(questions),
                'subject': subject,
                'difficulty': difficulty,
                'generation_time': generation_time,
                'sources_used': result.get('sources_used', []),
                'model_used': result['model_used'],
                'saved_to_database': True,
                'method': 'rag_pipeline'
            }, f"Generated {len(questions)} {difficulty} MCQ questions for {subject} in {generation_time:.2f}s")

        except Exception as e:
            db.session.rollback()
            print(f"❌ Error in MCQ generation: {str(e)}")
            return error_response(f"Failed to generate MCQ questions: {str(e)}", 500)

    @app.route('/api/chatbot/query', methods=['POST'])
    @user_required
    def api_chatbot_query():
        """Answer user questions using new RAG pipeline"""
        try:
            user = get_current_user()
            if not user:
                return error_response("User not found", 404)

            data = request.get_json()
            query = data.get('query', '').strip()
            subject = data.get('subject', '').strip().lower()
            session_id = data.get('session_id', str(uuid.uuid4()))

            # Validation
            if not query or len(query) < 3:
                return error_response("Query must be at least 3 characters long", 400)

            # Enhanced educational query filtering
            if not is_educational_query(query):
                return error_response(
                    "I can only help with educational questions. Please ask about subjects like Physics, Chemistry, Biology, Mathematics, or other academic topics.",
                    400
                )

            # Valid subjects (optional filter)
            valid_subjects = ['physics', 'chemistry', 'biology', 'mathematics', 'computer_science']
            if subject and subject not in valid_subjects:
                return error_response(f"Subject must be one of: {', '.join(valid_subjects)}", 400)

            print(f"🤖 New Chatbot Query - User: {user.id}, Query: {query[:50]}...")

            # Use optimized three-layer RAG service
            from shared.services.rag_service import get_rag_service

            rag_service = get_rag_service(
                ollama_model=app.config.get('RAG_OLLAMA_MODEL', 'llama3.2:1b'),
                top_k_results=app.config.get('RAG_TOP_K_RESULTS', 3),
                similarity_threshold=app.config.get('RAG_SIMILARITY_THRESHOLD', 0.01)
            )

            # Generate response using new RAG pipeline
            import time
            start_time = time.time()

            result = rag_service.generate_chat_response(
                query=query,
                subject=subject if subject else None
            )

            response_time = time.time() - start_time

            if not result['success']:
                return error_response(result['error'], 500)

            ai_response = result['response']

            # Save to chat history
            try:
                chat_history = AIChatHistory(
                    user_id=user.id,
                    session_id=session_id,
                    message=query,
                    response=ai_response,
                    context_provided=subject,
                    response_time=response_time,
                    tokens_used=0,  # Token counting can be added later
                    model_used=result['model_used']
                )
                db.session.add(chat_history)
                db.session.commit()
                print(f"✅ Chat response generated in {response_time:.2f}s")
            except Exception as e:
                print(f"❌ Error saving chat history: {e}")
                # Don't fail the request if history saving fails

            return success_response({
                'response': ai_response,
                'sources': result.get('sources', []),
                'relevant_docs': result.get('relevant_docs', 0),
                'session_id': session_id,
                'response_time': response_time,
                'model_used': result['model_used'],
                'method': 'rag_pipeline'
            }, f"Chat response generated in {response_time:.2f}s")

        except Exception as e:
            db.session.rollback()
            print(f"❌ Error in chatbot query: {str(e)}")
            return error_response(f"Failed to process chatbot query: {str(e)}", 500)

    @app.route('/api/rag/status', methods=['GET'])
    def api_rag_status():
        """Get comprehensive three-layer RAG system status"""
        try:
            # Get status from all three layers
            status = {
                'system_name': 'Three-Layer RAG System',
                'layers': {}
            }

            # Layer 1: Model Service Status
            try:
                from shared.services.model_service import get_model_service
                model_service = get_model_service()
                status['layers']['layer_1_models'] = model_service.get_status()
            except Exception as e:
                status['layers']['layer_1_models'] = {'status': 'error', 'error': str(e)}

            # Layer 2: Vector Index Service Status
            try:
                from shared.services.vector_index_service import VectorIndexService
                vector_service = VectorIndexService()
                status['layers']['layer_2_indexing'] = vector_service.get_indexing_status()
            except Exception as e:
                status['layers']['layer_2_indexing'] = {'status': 'error', 'error': str(e)}

            # Layer 3: RAG Query Service Status
            try:
                from shared.services.rag_service import get_rag_service
                rag_service = get_rag_service()
                status['layers']['layer_3_query'] = rag_service.get_status()
            except Exception as e:
                status['layers']['layer_3_query'] = {'status': 'error', 'error': str(e)}

            # Overall system health
            layer_statuses = [layer.get('status', 'unknown') for layer in status['layers'].values()]
            if all(s == 'ready' for s in layer_statuses):
                status['overall_status'] = 'ready'
            elif any(s == 'ready' for s in layer_statuses):
                status['overall_status'] = 'partial'
            else:
                status['overall_status'] = 'error'

            return success_response(status, "Three-layer RAG status retrieved successfully")

        except Exception as e:
            return error_response(f"Failed to get RAG status: {str(e)}", 500)

    @app.route('/api/rag/initialize', methods=['POST'])
    @admin_required
    def api_rag_initialize():
        """Initialize three-layer RAG system (Admin only)"""
        try:
            data = request.get_json() or {}
            force_recreate = data.get('force_recreate', False)

            print(f"🔄 Initializing three-layer RAG system (force_recreate: {force_recreate})")

            results = {
                'layer_1_models': {'status': 'pending'},
                'layer_2_indexing': {'status': 'pending'},
                'layer_3_query': {'status': 'pending'}
            }

            # Layer 1: Initialize Model Service (always ready, just check)
            try:
                from shared.services.model_service import get_model_service
                model_service = get_model_service()
                model_status = model_service.get_status()
                results['layer_1_models'] = {
                    'status': 'ready' if model_status['status'] == 'ready' else 'error',
                    'details': model_status
                }
                print("✅ Layer 1: Model Service ready")
            except Exception as e:
                results['layer_1_models'] = {'status': 'error', 'error': str(e)}
                print(f"❌ Layer 1: Model Service error: {str(e)}")

            # Layer 2: Initialize Vector Index Service
            try:
                from shared.services.vector_index_service import VectorIndexService
                vector_service = VectorIndexService()

                if force_recreate:
                    print("🔄 Layer 2: Force re-indexing all subjects...")
                    index_result = vector_service.index_all_subjects(force_recreate=True)
                else:
                    print("🔄 Layer 2: Indexing missing/changed subjects...")
                    index_result = vector_service.index_all_subjects(force_recreate=False)

                results['layer_2_indexing'] = {
                    'status': 'success' if index_result['success'] else 'error',
                    'details': index_result
                }
                print(f"✅ Layer 2: Indexing completed - {index_result.get('indexed_subjects', 0)} subjects")
            except Exception as e:
                results['layer_2_indexing'] = {'status': 'error', 'error': str(e)}
                print(f"❌ Layer 2: Indexing error: {str(e)}")

            # Layer 3: Initialize RAG Query Service
            try:
                from shared.services.rag_service import get_rag_service
                rag_service = get_rag_service()
                rag_status = rag_service.get_status()
                results['layer_3_query'] = {
                    'status': 'ready',
                    'details': rag_status
                }
                print("✅ Layer 3: RAG Query Service ready")
            except Exception as e:
                results['layer_3_query'] = {'status': 'error', 'error': str(e)}
                print(f"❌ Layer 3: RAG Query Service error: {str(e)}")

            # Determine overall success
            layer_statuses = [layer['status'] for layer in results.values()]
            overall_success = all(status in ['ready', 'success'] for status in layer_statuses)

            if overall_success:
                print("🎉 Three-layer RAG system initialized successfully!")
                return success_response({
                    'message': "Three-layer RAG system initialized successfully",
                    'layers': results,
                    'force_recreate': force_recreate
                }, "RAG initialization completed")
            else:
                print("⚠️ RAG initialization had some failures")
                return error_response("RAG initialization had failures", 500, {
                    'layers': results,
                    'force_recreate': force_recreate
                })

        except Exception as e:
            return error_response(f"Failed to initialize RAG system: {str(e)}", 500)

    @app.route('/api/rag/reload/<subject>', methods=['POST'])
    @admin_required
    def api_rag_reload_subject(subject):
        """Reload vector store for a specific subject (Admin only)"""
        try:
            # Valid subjects
            valid_subjects = ['physics', 'chemistry', 'biology', 'mathematics', 'computer_science']
            if subject not in valid_subjects:
                return error_response(f"Subject must be one of: {', '.join(valid_subjects)}", 400)

            print(f"🔄 Reloading vector index for subject: {subject}")

            # Use Layer 2: Vector Index Service for reloading
            from shared.services.vector_index_service import VectorIndexService
            vector_service = VectorIndexService()

            # Force re-index this specific subject
            result = vector_service.index_subject(subject, force_recreate=True)

            if result['success']:
                print(f"✅ Successfully reloaded vector index for {subject}")
                return success_response({
                    'message': f'Successfully reloaded vector index for {subject}',
                    'subject': subject,
                    'details': result
                }, f"Reloaded {subject} vector index")
            else:
                print(f"❌ Failed to reload vector index for {subject}")
                return error_response(f"Failed to reload vector index for {subject}", 500, result)

        except Exception as e:
            return error_response(f"Failed to reload subject index: {str(e)}", 500)

    # Enhanced Purchase Endpoints with Mock Test Flow
    @app.route('/api/purchases', methods=['POST'])
    @user_required
    def api_create_purchase():
        """Create purchase record with conditional flow based on environment"""
        try:
            user = get_current_user()
            if not user:
                return error_response("User not found", 404)

            data = request.get_json()
            course_id = data.get('course_id')
            subject_id = data.get('subject_id')  # For single subject purchase
            subject_ids = data.get('subject_ids', [])  # For multiple subjects purchase
            purchase_type = data.get('purchase_type', 'single_subject')  # single_subject, multiple_subjects, full_bundle
            payment_method = data.get('payment_method', 'demo')  # For compatibility

            # Check environment mode for conditional purchase flow
            is_development = app.config.get('LOCAL_DEV_MODE', True) or app.config.get('BYPASS_PURCHASE_VALIDATION', True)
            is_production = app.config.get('FLASK_ENV', 'development').lower() == 'production'

            # Validation
            if not course_id:
                return error_response("Course ID is required", 400)

            if purchase_type not in ['single_subject', 'multiple_subjects', 'full_bundle']:
                return error_response("Invalid purchase type", 400)

            # Production mode: Implement full payment validation
            if is_production and not is_development:
                # TODO: Implement payment gateway integration
                # For now, return error in production without payment gateway
                return error_response("Payment gateway integration required for production. Contact administrator.", 501)

            # Development/Local mode: Skip payment validation, instant access

            # Check if course exists
            course = ExamCategory.query.get(course_id)
            if not course:
                return error_response("Course not found", 404)

            # Validate purchase type specific requirements
            subjects_to_include = []

            if purchase_type == 'single_subject':
                if not subject_id:
                    return error_response("Subject ID is required for single subject purchase", 400)

                subject = ExamCategorySubject.query.get(subject_id)
                if not subject or subject.exam_category_id != course_id:
                    return error_response("Subject not found or doesn't belong to this course", 404)

                subjects_to_include = [subject_id]

            elif purchase_type == 'multiple_subjects':
                if not subject_ids or len(subject_ids) < 2:
                    return error_response("At least 2 subject IDs required for multiple subjects purchase", 400)

                # Validate all subjects exist and belong to the course
                subjects = ExamCategorySubject.query.filter(
                    ExamCategorySubject.id.in_(subject_ids),
                    ExamCategorySubject.exam_category_id == course_id
                ).all()

                if len(subjects) != len(subject_ids):
                    return error_response("One or more subjects not found or don't belong to this course", 404)

                subjects_to_include = subject_ids
                subject_id = None  # For multiple subjects, subject_id should be None

            elif purchase_type == 'full_bundle':
                # Get all subjects for this course, excluding bundle subjects (is_bundle=True)
                course_subjects = ExamCategorySubject.query.filter_by(
                    exam_category_id=course_id,
                    is_deleted=False,
                    is_bundle=False  # Exclude bundle subjects - they're containers, not actual subjects
                ).all()

                if not course_subjects:
                    return error_response("No subjects found for this course", 404)

                subjects_to_include = [s.id for s in course_subjects]
                subject_id = None  # For bundle, subject_id should be None

            # Check for existing purchases that would conflict
            existing_purchase = None
            if purchase_type == 'single_subject':
                existing_purchase = ExamCategoryPurchase.query.filter_by(
                    user_id=user.id,
                    exam_category_id=course_id,
                    subject_id=subject_id
                ).first()
            else:
                # For multiple subjects or bundle, check if user already has full access
                existing_purchase = ExamCategoryPurchase.query.filter_by(
                    user_id=user.id,
                    exam_category_id=course_id,
                    purchase_type='full_bundle'
                ).first()

            if existing_purchase:
                return success_response({
                    'purchase': existing_purchase.to_dict(),
                    'message': 'You already have access to this content!'
                }, "Access already granted")

            # Calculate cost and benefits based on environment
            if is_development:
                # Development mode: Free access for testing
                cost = 0.00
                purchase_message = "🚀 Development Mode: Instant access granted for testing!"
            else:
                # Production mode: Calculate actual cost (placeholder for payment integration)
                cost_map = {
                    'single_subject': 599.00,
                    'multiple_subjects': 999.00,
                    'full_bundle': 1499.00
                }
                cost = cost_map.get(purchase_type, 599.00)
                purchase_message = f"Purchase successful! Amount: ₹{cost}"

            chatbot_unlimited = purchase_type == 'full_bundle'

            # Create purchase record
            purchase = ExamCategoryPurchase(
                user_id=user.id,
                exam_category_id=course_id,
                subject_id=subject_id,  # None for multiple/bundle
                cost=cost,
                purchase_type=purchase_type,
                subjects_included=subjects_to_include if purchase_type != 'single_subject' else None,
                chatbot_tokens_unlimited=chatbot_unlimited,
                total_mock_tests=len(subjects_to_include) * 50,  # 50 tests per subject
                mock_tests_used=0,
                status='active'
            )

            db.session.add(purchase)
            db.session.flush()  # Get the purchase ID

            # Import and use MockTestService to create test cards
            from shared.services.mock_test_service import MockTestService
            card_result = MockTestService.create_test_cards_for_purchase(purchase.id)

            if not card_result['success']:
                db.session.rollback()
                return error_response(f"Failed to create test cards: {card_result['error']}", 500)

            db.session.commit()

            return success_response({
                'purchase': purchase.to_dict(),
                'test_cards_created': card_result['cards_created'],
                'subjects_count': card_result['subjects_count'],
                'environment_mode': 'development' if is_development else 'production',
                'cost': cost,
                'message': f'{purchase_message} {card_result["cards_created"]} test cards created.'
            }, "Purchase completed successfully")

        except Exception as e:
            db.session.rollback()
            return error_response(f"Failed to create auto-purchase: {str(e)}", 500)

    # New Mock Test Card Endpoints
    @app.route('/api/user/test-cards', methods=['GET'])
    @user_required
    def api_get_user_test_cards():
        """Get user's test cards with re-attempt tracking"""
        try:
            user = get_current_user()
            if not user:
                return error_response("User not found", 404)

            subject_id = request.args.get('subject_id', type=int)

            from shared.services.mock_test_service import MockTestService
            test_cards = MockTestService.get_user_test_cards(user.id, subject_id)

            # Group by subject for better organization
            cards_by_subject = {}
            for card in test_cards:
                subject_key = f"{card['subject_id']}_{card['subject_name']}"
                if subject_key not in cards_by_subject:
                    cards_by_subject[subject_key] = {
                        'subject_id': card['subject_id'],
                        'subject_name': card['subject_name'],
                        'course_name': card['course_name'],
                        'total_cards': 0,
                        'available_cards': 0,
                        'completed_cards': 0,
                        'disabled_cards': 0,
                        'cards': []
                    }

                cards_by_subject[subject_key]['cards'].append(card)
                cards_by_subject[subject_key]['total_cards'] += 1

                if card['status'] == 'available' and card['is_available']:
                    cards_by_subject[subject_key]['available_cards'] += 1
                elif card['status'] == 'completed':
                    cards_by_subject[subject_key]['completed_cards'] += 1
                elif card['status'] == 'disabled':
                    cards_by_subject[subject_key]['disabled_cards'] += 1

            return success_response({
                'test_cards_by_subject': list(cards_by_subject.values()),
                'total_subjects': len(cards_by_subject)
            }, "Test cards retrieved successfully")

        except Exception as e:
            return error_response(f"Failed to get test cards: {str(e)}", 500)

    @app.route('/api/user/test-cards/<int:mock_test_id>/start', methods=['POST'])
    @user_required
    def api_start_mock_test(mock_test_id):
        """Start a test attempt for a specific test card"""
        try:
            user = get_current_user()
            if not user:
                return error_response("User not found", 404)

            from shared.services.mock_test_service import MockTestService
            result = MockTestService.start_test_attempt(mock_test_id, user.id)

            if not result['success']:
                return error_response(result['error'], 400)

            return success_response(result, "Test attempt started successfully")

        except Exception as e:
            return error_response(f"Failed to start test attempt: {str(e)}", 500)

    @app.route('/api/user/test-sessions/<int:session_id>/questions', methods=['GET'])
    @user_required
    def api_get_test_questions(session_id):
        """Get questions for a test session (generate if first attempt, reuse if re-attempt)"""
        try:
            user = get_current_user()
            if not user:
                return error_response("User not found", 404)

            session = TestAttemptSession.query.filter_by(
                id=session_id,
                user_id=user.id
            ).first()

            if not session:
                return error_response("Test session not found", 404)

            mock_test = session.mock_test

            # Check if questions already exist for this mock test
            existing_questions = ExamCategoryQuestion.query.filter_by(
                mock_test_id=mock_test.id
            ).all()

            if existing_questions:
                # Re-attempt: return existing questions
                questions = [q.to_dict(include_answer=False) for q in existing_questions]
                return success_response({
                    'questions': questions,
                    'session_id': session.id,
                    'mock_test_id': mock_test.id,
                    'attempt_number': session.attempt_number,
                    'is_re_attempt': True,
                    'total_questions': len(questions)
                }, "Existing questions loaded for re-attempt")

            else:
                # First attempt: generate real AI questions
                subject = db.session.get(ExamCategorySubject, mock_test.subject_id)
                if not subject:
                    return error_response("Subject not found", 404)

                course = db.session.get(ExamCategory, mock_test.course_id)
                if not course:
                    return error_response("Course not found", 404)

                print(f"🚀 Generating AI questions for mock test {mock_test.id}, subject: {subject.subject_name}")
                print(f"🔧 PDF folder: {app.config.get('AI_PDF_FOLDER')}")
                print(f"🔧 Ollama model: {app.config.get('AI_OLLAMA_MODEL', 'llama3.2:1b')}")
                import sys
                sys.stdout.flush()

                # Generate questions using new RAG service
                try:
                    from shared.services.rag_service import get_rag_service

                    rag_service = get_rag_service()

                    print(f"🔧 RAG service created successfully")

                    # Check RAG service status
                    rag_status = rag_service.get_status()
                    print(f"🔧 RAG service status: {rag_status.get('status', 'unknown')}")
                    sys.stdout.flush()

                    # Generate 50 questions for the test card using RAG pipeline with timeout
                    import threading
                    import queue

                    def rag_generation_worker(q, rag_service, subject_name):
                        """Worker function for RAG generation with timeout"""
                        try:
                            result = rag_service.generate_mcq_questions(
                                subject=subject_name.lower(),
                                num_questions=50,
                                difficulty='hard'  # Always use hard difficulty
                            )
                            q.put(result)
                        except Exception as e:
                            q.put({'success': False, 'error': str(e)})

                    # Use threading with timeout (cross-platform solution)
                    result_queue = queue.Queue()
                    worker_thread = threading.Thread(
                        target=rag_generation_worker,
                        args=(result_queue, rag_service, subject.subject_name)
                    )

                    worker_thread.start()

                    try:
                        # Wait for result with configurable timeout (default 120 seconds for MCQ generation)
                        timeout_seconds = app.config.get('RAG_TIMEOUT_SECONDS', 120)
                        result = result_queue.get(timeout=timeout_seconds)
                    except queue.Empty:
                        print("⏰ RAG generation timed out, using fallback")
                        result = {'success': False, 'error': 'RAG generation timed out'}
                    finally:
                        # Ensure thread cleanup
                        if worker_thread.is_alive():
                            worker_thread.join(timeout=1)

                    print(f"🔍 RAG Generation Result: success={result.get('success')}, questions={len(result.get('questions', []))}")
                    if not result.get('success'):
                        print(f"❌ RAG Generation Error: {result.get('error')}")
                    sys.stdout.flush()

                    if not result['success']:
                        print(f"⚠️ RAG generation failed: {result['error']}")
                        print("🔄 Falling back to simple question generation...")
                        sys.stdout.flush()

                        # Fallback: Use simple MCQ service
                        try:
                            from shared.services.simple_mcq_service import get_simple_mcq_service
                            simple_service = get_simple_mcq_service()
                            result = simple_service.generate_questions(subject.subject_name, 50)
                            result['fallback_used'] = True
                            print(f"✅ Fallback generated {len(result.get('questions', []))} questions")
                        except Exception as fallback_error:
                            print(f"❌ Fallback also failed: {str(fallback_error)}")
                            # Last resort: use the inline fallback
                            fallback_questions = generate_fallback_questions(subject.subject_name, 50)
                            result = {
                                'success': True,
                                'questions': fallback_questions,
                                'fallback_used': True,
                                'method': 'inline_fallback'
                            }

                    # Check if we actually got questions
                    if not result.get('questions') or len(result['questions']) == 0:
                        return error_response("Failed to generate questions. Please try again.", 500)

                    # Convert RAG questions to the expected format
                    formatted_questions = []
                    for q_data in result['questions']:
                        formatted_questions.append({
                            'question': q_data.get('question', ''),
                            'option_1': q_data.get('option_a', ''),
                            'option_2': q_data.get('option_b', ''),
                            'option_3': q_data.get('option_c', ''),
                            'option_4': q_data.get('option_d', ''),
                            'correct_answer': q_data.get('correct_answer', ''),
                            'explanation': q_data.get('explanation', '')
                        })

                    result['questions'] = formatted_questions

                    # Double-check we have valid questions
                    if len(formatted_questions) == 0:
                        return error_response("Failed to format RAG questions. Please try again.", 500)

                except Exception as rag_error:
                    print(f"❌ RAG generation failed: {str(rag_error)}")
                    import traceback
                    print(f"❌ Full traceback: {traceback.format_exc()}")
                    sys.stdout.flush()

                    # Provide more detailed error information
                    error_details = {
                        'error_type': type(rag_error).__name__,
                        'error_message': str(rag_error),
                        'subject': subject.subject_name if subject else 'Unknown',
                        'mock_test_id': mock_test.id if mock_test else 'Unknown',
                        'session_id': session.id if session else 'Unknown'
                    }

                    return error_response(f"RAG service error: {str(rag_error)}", 500, error_details)

                # Save questions to database linked to this mock test
                questions_data = []
                for q_data in result['questions']:
                    question = ExamCategoryQuestion(
                        exam_category_id=mock_test.course_id,
                        subject_id=mock_test.subject_id,
                        mock_test_id=mock_test.id,
                        question=q_data['question'],
                        option_1=q_data['option_1'],
                        option_2=q_data['option_2'],
                        option_3=q_data['option_3'],
                        option_4=q_data['option_4'],
                        correct_answer=q_data['correct_answer'],
                        explanation=q_data.get('explanation', ''),
                        is_ai_generated=True,
                        ai_model_used=app.config.get('AI_OLLAMA_MODEL', 'llama3.2:1b'),
                        difficulty_level='hard',
                        user_id=user.id,
                        purchased_id=mock_test.purchase_id
                    )
                    db.session.add(question)
                    questions_data.append(question.to_dict(include_answer=False))

                # Mark questions as generated
                mock_test.questions_generated = True
                mock_test.total_questions = len(questions_data)

                db.session.commit()

                return success_response({
                    'questions': questions_data,
                    'session_id': session.id,
                    'mock_test_id': mock_test.id,
                    'attempt_number': session.attempt_number,
                    'is_re_attempt': False,
                    'total_questions': len(questions_data),
                    'generation_info': {
                        'model_used': app.config.get('AI_OLLAMA_MODEL', 'llama3.2:1b'),
                        'sources_used': result.get('sources_used', [])
                    }
                }, "Questions generated successfully")

        except Exception as e:
            db.session.rollback()
            return error_response(f"Failed to get test questions: {str(e)}", 500)

    @app.route('/api/user/test-sessions/<int:session_id>/submit', methods=['POST'])
    @user_required
    def api_submit_test_session(session_id):
        """Submit answers for a test session"""
        try:
            user = get_current_user()
            if not user:
                return error_response("User not found", 404)

            data = request.get_json()
            answers = data.get('answers', [])  # List of {question_id, selected_answer}
            time_taken = data.get('time_taken', 0)

            session = TestAttemptSession.query.filter_by(
                id=session_id,
                user_id=user.id
            ).first()

            if not session:
                return error_response("Test session not found", 404)

            if session.status != 'in_progress':
                return error_response("Test session is not in progress", 400)

            # Get questions for this mock test
            questions = ExamCategoryQuestion.query.filter_by(
                mock_test_id=session.mock_test_id
            ).all()

            question_map = {q.id: q for q in questions}

            # Process answers and calculate score
            correct_answers = 0
            wrong_answers = 0
            unanswered = 0

            for answer_data in answers:
                question_id = answer_data.get('question_id')
                selected_answer = answer_data.get('selected_answer')

                if question_id in question_map:
                    question = question_map[question_id]
                    is_correct = selected_answer == question.correct_answer

                    if selected_answer:
                        if is_correct:
                            correct_answers += 1
                        else:
                            wrong_answers += 1
                    else:
                        unanswered += 1

                    # Save answer
                    test_answer = TestAnswer(
                        session_id=session.id,
                        question_id=question_id,
                        selected_answer=selected_answer,
                        is_correct=is_correct,
                        time_taken=answer_data.get('time_taken', 0)
                    )
                    db.session.add(test_answer)

            # Calculate final score
            total_questions = len(questions)
            score = correct_answers

            # Complete the test session using MockTestService
            from shared.services.mock_test_service import MockTestService
            result = MockTestService.complete_test_attempt(
                session.id, score, time_taken, correct_answers, wrong_answers, unanswered
            )

            if not result['success']:
                return error_response(result['error'], 500)

            return success_response(result, "Test submitted successfully")

        except Exception as e:
            db.session.rollback()
            return error_response(f"Failed to submit test: {str(e)}", 500)

    @app.route('/api/user/test-analytics', methods=['GET'])
    @user_required
    def api_get_test_analytics():
        """Get user's test analytics (based on latest attempts only)"""
        try:
            user = get_current_user()
            if not user:
                return error_response("User not found", 404)

            subject_id = request.args.get('subject_id', type=int)

            from shared.services.mock_test_service import MockTestService
            analytics = MockTestService.get_test_analytics(user.id, subject_id)

            return success_response(analytics, "Analytics retrieved successfully")

        except Exception as e:
            return error_response(f"Failed to get analytics: {str(e)}", 500)

    # Legacy endpoint compatibility (updated to use new system)
    @app.route('/api/user/available-tests', methods=['GET'])
    @user_required
    def api_get_user_available_tests_legacy():
        """Legacy endpoint - redirects to new test cards system"""
        try:
            user = get_current_user()
            if not user:
                return error_response("User not found", 404)

            # Get user's purchases for backward compatibility
            purchases = ExamCategoryPurchase.query.filter_by(
                user_id=user.id,
                status='active'
            ).all()

            available_tests = []
            for purchase in purchases:
                # Get test cards count for this purchase
                test_cards_count = MockTestAttempt.query.filter_by(
                    purchase_id=purchase.id
                ).count()

                available_cards_count = MockTestAttempt.query.filter_by(
                    purchase_id=purchase.id,
                    status='available'
                ).filter(MockTestAttempt.attempts_used < MockTestAttempt.max_attempts).count()

                if purchase.purchase_type == 'single_subject' and purchase.subject_id:
                    subject = ExamCategorySubject.query.get(purchase.subject_id)
                    if subject:
                        # Get first available test card for this subject
                        first_available_card = MockTestAttempt.query.filter_by(
                            purchase_id=purchase.id,
                            subject_id=purchase.subject_id,
                            status='available'
                        ).filter(MockTestAttempt.attempts_used < MockTestAttempt.max_attempts).first()

                        available_tests.append({
                            'purchase_id': purchase.id,
                            'subject_id': purchase.subject_id,
                            'subject_name': subject.subject_name,
                            'course_name': subject.exam_category.course_name,
                            'total_mock_tests': test_cards_count,
                            'available_tests': available_cards_count,
                            'purchase_type': 'subject',
                            'test_card_id': first_available_card.id if first_available_card else None  # Add test_card_id for new system
                        })
                else:
                    # Multiple subjects or bundle - create individual entries for each subject
                    course = ExamCategory.query.get(purchase.exam_category_id)
                    if course:
                        subjects_included = purchase.get_included_subjects()

                        for subj_id in subjects_included:
                            subj = ExamCategorySubject.query.get(subj_id)
                            # Only include non-bundle subjects in test listings
                            if subj and not subj.is_bundle:
                                subj_cards = MockTestAttempt.query.filter_by(
                                    purchase_id=purchase.id,
                                    subject_id=subj_id
                                ).count()

                                subj_available = MockTestAttempt.query.filter_by(
                                    purchase_id=purchase.id,
                                    subject_id=subj_id,
                                    status='available'
                                ).filter(MockTestAttempt.attempts_used < MockTestAttempt.max_attempts).count()

                                # Get first available test card for this subject
                                first_available_card = MockTestAttempt.query.filter_by(
                                    purchase_id=purchase.id,
                                    subject_id=subj_id,
                                    status='available'
                                ).filter(MockTestAttempt.attempts_used < MockTestAttempt.max_attempts).first()

                                # Create individual entry for each subject
                                available_tests.append({
                                    'purchase_id': purchase.id,
                                    'subject_id': subj_id,
                                    'subject_name': subj.subject_name,
                                    'course_name': course.course_name,
                                    'total_mock_tests': subj_cards,
                                    'available_tests': subj_available,
                                    'purchase_type': purchase.purchase_type,
                                    'test_card_id': first_available_card.id if first_available_card else None,  # Add test_card_id for new system
                                    'chatbot_unlimited': purchase.chatbot_tokens_unlimited
                                })

            return success_response({
                'available_tests': available_tests,
                'message': 'Consider using /api/user/test-cards for the new test card system'
            }, "Available tests retrieved (legacy format)")

        except Exception as e:
            return error_response(f"Failed to get available tests: {str(e)}", 500)

    @app.route('/api/dev/test-simple', methods=['GET'])
    def api_dev_test_simple():
        """Simple test endpoint"""
        print(f"🚀 SIMPLE DEV ENDPOINT CALLED: /api/dev/test-simple")
        import sys
        sys.stdout.flush()
        return success_response({"message": "Simple test endpoint working"}, "Test successful")



    @app.route('/api/dev/available-tests', methods=['GET'])
    def api_dev_get_available_tests():
        """Development endpoint - Get available tests without authentication"""
        if not app.config.get('LOCAL_DEV_MODE', False):
            return error_response("This endpoint is only available in development mode", 403)

        try:
            # Get all non-bundle subjects for demo purposes
            subjects = ExamCategorySubject.query.filter_by(is_bundle=False).all()

            available_tests = []
            for subject in subjects:
                available_tests.append({
                    'purchase_id': None,
                    'subject_id': subject.id,
                    'subject_name': subject.subject_name,
                    'course_name': subject.exam_category.course_name,
                    'total_mock_tests': subject.total_mock or 50,
                    'mock_tests_used': 0,
                    'available_tests': subject.total_mock or 50,
                    'purchase_type': 'demo'
                })

            return success_response({
                'available_tests': available_tests,
                'total_purchases': 0,
                'dev_mode': True
            }, "Available tests retrieved successfully (Development mode)")

        except Exception as e:
            return error_response(f"Failed to get available tests: {str(e)}", 500)

    @app.route('/api/user/start-test', methods=['POST'])
    @user_required
    def api_start_test():
        """Start a new mock test and track usage"""
        try:
            user = get_current_user()
            if not user:
                return error_response("User not found", 404)

            data = request.get_json()
            subject_id = data.get('subject_id')
            purchase_id = data.get('purchase_id')

            if not subject_id:
                return error_response("Subject ID is required", 400)

            # Verify user has access to this subject
            if purchase_id:
                purchase = ExamCategoryPurchase.query.filter_by(
                    id=purchase_id,
                    user_id=user.id,
                    status='active'
                ).first()
            else:
                # Find any active purchase that gives access to this subject
                purchase = ExamCategoryPurchase.query.filter(
                    ExamCategoryPurchase.user_id == user.id,
                    ExamCategoryPurchase.status == 'active',
                    db.or_(
                        ExamCategoryPurchase.subject_id == subject_id,
                        db.and_(
                            ExamCategoryPurchase.subject_id.is_(None),
                            ExamCategoryPurchase.exam_category_id == ExamCategorySubject.query.get(subject_id).exam_category_id
                        )
                    )
                ).first()

            if not purchase:
                return error_response("No active purchase found for this subject", 403)

            # Check if user has available tests
            if purchase.subject_id == subject_id:
                # Individual subject purchase
                available_tests = (purchase.total_mock_tests or 0) - (purchase.mock_tests_used or 0)
                if available_tests <= 0:
                    return error_response("No mock tests remaining for this subject", 403)
            else:
                # Full course purchase - check total available tests
                available_tests = (purchase.total_mock_tests or 0) - (purchase.mock_tests_used or 0)
                if available_tests <= 0:
                    return error_response("No mock tests remaining for this course", 403)

            # Create test attempt record
            test_attempt = TestAttempt(
                user_id=user.id,
                purchase_id=purchase.id,
                exam_category_id=purchase.exam_category_id,
                subject_id=subject_id,
                total_questions=0,  # Will be updated when questions are generated
                total_marks=0,      # Will be updated when questions are generated
                status='in_progress'
            )

            db.session.add(test_attempt)
            db.session.flush()  # Get the test attempt ID

            db.session.commit()

            return success_response({
                'test_attempt_id': test_attempt.id,
                'subject_id': subject_id,
                'remaining_tests': available_tests,  # Don't decrement until test is completed
                'message': 'Test started successfully',
                'next_step': 'Generate questions for this test attempt'
            }, "Test started successfully")

        except Exception as e:
            db.session.rollback()
            return error_response(f"Failed to start test: {str(e)}", 500)

    @app.route('/api/user/generate-test-questions', methods=['POST'])
    @user_required
    def api_generate_enhanced_test_questions():
        """Generate questions for a test attempt with exam-specific logic - supports both legacy and new test card systems"""
        try:
            user = get_current_user()
            if not user:
                return error_response("User not found", 404)

            data = request.get_json()
            test_attempt_id = data.get('test_attempt_id')
            session_id = data.get('session_id')  # For new test card system

            if not test_attempt_id and not session_id:
                return error_response("Either test_attempt_id or session_id is required", 400)

            print(f"🚀 MCQ Generation Request - User: {user.id}, Test Attempt: {test_attempt_id}, Session: {session_id}")
            import sys
            sys.stdout.flush()

            # Determine which system we're using
            test_attempt = None
            session = None
            mock_test = None

            if session_id:
                # New test card system
                session = TestAttemptSession.query.filter_by(
                    id=session_id,
                    user_id=user.id
                ).first()

                if not session:
                    return error_response("Test session not found", 404)

                mock_test = session.mock_test
                print(f"🔄 Using new test card system - Session: {session_id}, Mock Test: {mock_test.id}")

            elif test_attempt_id:
                # Legacy system
                test_attempt = TestAttempt.query.filter_by(
                    id=test_attempt_id,
                    user_id=user.id
                ).first()

                if not test_attempt:
                    return error_response("Test attempt not found", 404)

                print(f"🔄 Using legacy system - Test Attempt: {test_attempt_id}")

            sys.stdout.flush()

            # Check if questions already exist (prevent duplicate generation)
            existing_questions = []
            purchase_id = None
            subject_id = None
            course_id = None

            if session and mock_test:
                # New test card system - check for questions linked to this mock test
                existing_questions = ExamCategoryQuestion.query.filter_by(
                    mock_test_id=mock_test.id
                ).all()
                purchase_id = mock_test.purchase_id
                subject_id = mock_test.subject_id
                course_id = mock_test.course_id
                print(f"🔍 Checking for existing questions - Mock Test: {mock_test.id}")

            elif test_attempt:
                # Legacy system - check for questions linked to this purchase
                existing_questions = ExamCategoryQuestion.query.filter_by(
                    user_id=user.id,
                    purchased_id=test_attempt.purchase_id
                ).all()
                purchase_id = test_attempt.purchase_id
                subject_id = test_attempt.subject_id
                course_id = test_attempt.exam_category_id
                print(f"🔍 Checking for existing questions - User: {user.id}, Purchase: {test_attempt.purchase_id}")

            print(f"🔍 Found {len(existing_questions)} existing questions")
            sys.stdout.flush()

            if existing_questions:
                identifier = session_id if session else test_attempt_id
                print(f"🔄 Questions already exist for {'session' if session else 'test attempt'} {identifier}, returning {len(existing_questions)} existing questions")
                sys.stdout.flush()

                # Return existing questions in the expected format
                formatted_questions = []
                for q in existing_questions:
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

                # Get purchase info for response
                purchase = ExamCategoryPurchase.query.get(purchase_id) if purchase_id else None
                subject = ExamCategorySubject.query.get(subject_id) if subject_id else None
                course = ExamCategory.query.get(course_id) if course_id else None

                return success_response({
                    'test_attempt_id': test_attempt_id,
                    'session_id': session_id,
                    'questions_generated': len(formatted_questions),
                    'questions': formatted_questions,
                    'purchase_type': 'bundle' if (purchase and not purchase.subject_id) else 'subject',
                    'exam_type': course.course_name if course else 'Unknown',
                    'subject_directories_used': [],
                    'sources_used': [],
                    'ai_model': 'existing'
                }, f"Returned {len(formatted_questions)} existing questions")

            # Get subject and course information
            subject = ExamCategorySubject.query.get(subject_id)
            if not subject:
                return error_response("Subject not found", 404)

            course = ExamCategory.query.get(course_id)
            if not course:
                return error_response("Course not found", 404)

            # Get purchase information
            purchase = ExamCategoryPurchase.query.get(purchase_id) if purchase_id else None
            if not purchase:
                return error_response("Purchase not found", 404)

            # Determine question count based on purchase type
            if purchase.subject_id:
                # Individual subject purchase: 50 questions
                num_questions = 50
                exam_type = subject.subject_name
                subject_directories = None  # Will be determined by subject name
            else:
                # Full course/bundle purchase: 150 questions
                num_questions = 150
                exam_type = course.course_name
                subject_directories = None  # Will be determined by exam type

            # Generate questions using enhanced RAG service
            try:
                from shared.services.rag_service import get_rag_service

                rag_service = get_rag_service()

                # Debug: Log the parameters being passed to RAG service
                print(f"🔍 MCQ Generation Parameters:")
                print(f"   num_questions: {num_questions}")
                print(f"   subject_name: {subject.subject_name}")
                print(f"   exam_type: {exam_type}")
                import sys
                sys.stdout.flush()

                # Use RAG pipeline for MCQ generation
                result = rag_service.generate_mcq_questions(
                    subject=subject.subject_name.lower(),
                    num_questions=num_questions,
                    difficulty='hard'  # Always use hard difficulty for real exam challenge
                )

                print(f"🔍 MCQ Generation Result:")
                print(f"   success: {result.get('success')}")
                print(f"   questions_count: {len(result.get('questions', []))}")
                print(f"   sources_used: {result.get('sources_used', [])}")
                if not result.get('success'):
                    print(f"   error: {result.get('error')}")
                sys.stdout.flush()

                if not result['success']:
                    return error_response(f"Failed to generate questions: {result['error']}", 500)

                # Save questions to database
                saved_questions = []
                for i, question_data in enumerate(result['questions']):
                    question = ExamCategoryQuestion(
                        exam_category_id=course.id,
                        subject_id=subject.id,
                        question=question_data.get('question', ''),
                        option_1=question_data.get('option_a', ''),
                        option_2=question_data.get('option_b', ''),
                        option_3=question_data.get('option_c', ''),
                        option_4=question_data.get('option_d', ''),
                        correct_answer=question_data.get('correct_answer', 'A'),
                        explanation=question_data.get('explanation', ''),
                        difficulty_level='hard',  # Always hard difficulty
                        is_ai_generated=True,
                        ai_model_used=result.get('model_used', app.config.get('AI_OLLAMA_MODEL', 'llama3.2:1b')),
                        user_id=user.id,
                        purchased_id=purchase_id,
                        mock_test_id=mock_test.id if mock_test else None  # Link to mock test for new system
                    )

                    db.session.add(question)
                    db.session.flush()  # Get question ID

                    saved_questions.append({
                        'id': question.id,
                        'question': question.question,
                        'options': {
                            'A': question.option_1,
                            'B': question.option_2,
                            'C': question.option_3,
                            'D': question.option_4
                        },
                        'correct_answer': question.correct_answer,
                        'explanation': question.explanation
                    })

                # Update appropriate model with question count
                if test_attempt:
                    # Legacy system
                    test_attempt.total_questions = len(saved_questions)
                    test_attempt.updated_at = datetime.utcnow()
                elif mock_test:
                    # New test card system
                    mock_test.questions_generated = True
                    mock_test.total_questions = len(saved_questions)

                db.session.commit()

                return success_response({
                    'test_attempt_id': test_attempt_id,
                    'session_id': session_id,
                    'questions_generated': len(saved_questions),
                    'questions': saved_questions,
                    'purchase_type': 'subject' if purchase.subject_id else 'bundle',
                    'exam_type': exam_type,
                    'subject_directories_used': result.get('attempted_subjects', []),
                    'sources_used': result.get('sources_used', []),
                    'ai_model': app.config.get('AI_OLLAMA_MODEL', 'llama3.2:1b')
                }, f"Generated {len(saved_questions)} questions successfully")

            except Exception as rag_error:
                return error_response(f"RAG service error: {str(rag_error)}", 500)

        except Exception as e:
            db.session.rollback()
            return error_response(f"Failed to generate test questions: {str(e)}", 500)

    # Legacy endpoint removed - use /api/user/generate-test-questions instead

    # New Chunked MCQ Generation Endpoints
    @app.route('/api/user/generate-test-questions-chunked', methods=['POST'])
    @user_required
    def api_start_chunked_mcq_generation():
        """Start chunked MCQ generation - generates first 5 questions immediately, continues in background"""
        try:
            user = get_current_user()
            if not user:
                return error_response("User not found", 404)

            data = request.get_json()
            test_attempt_id = data.get('test_attempt_id')
            session_id = data.get('session_id')

            if not test_attempt_id and not session_id:
                return error_response("Either test_attempt_id or session_id is required", 400)

            from shared.services.chunked_mcq_service_simple import get_chunked_mcq_service

            chunked_service = get_chunked_mcq_service()
            result = chunked_service.start_chunked_generation(
                test_attempt_id=test_attempt_id,
                session_id=session_id,
                user_id=user.id
            )

            if not result['success']:
                return error_response(result['error'], 400)

            return success_response(result, "Chunked MCQ generation started successfully")

        except Exception as e:
            return error_response(f"Failed to start chunked generation: {str(e)}", 500)

    @app.route('/api/user/mcq-generation-progress/<generation_id>', methods=['GET'])
    @user_required
    def api_get_mcq_generation_progress(generation_id):
        """Get progress of ongoing MCQ generation"""
        try:
            user = get_current_user()
            if not user:
                return error_response("User not found", 404)

            from shared.services.chunked_mcq_service_simple import get_chunked_mcq_service

            chunked_service = get_chunked_mcq_service()
            result = chunked_service.get_generation_progress(generation_id)

            if not result['success']:
                return error_response(result['error'], 404)

            return success_response(result, "Generation progress retrieved successfully")

        except Exception as e:
            return error_response(f"Failed to get generation progress: {str(e)}", 500)

    @app.route('/api/user/mcq-generation-questions/<generation_id>', methods=['GET'])
    @user_required
    def api_get_all_generated_questions(generation_id):
        """Get all generated questions for a generation"""
        try:
            user = get_current_user()
            if not user:
                return error_response("User not found", 404)

            from shared.services.chunked_mcq_service_simple import get_chunked_mcq_service

            chunked_service = get_chunked_mcq_service()
            result = chunked_service.get_all_questions(generation_id)

            if not result['success']:
                return error_response(result['error'], 404)

            return success_response(result, "All generated questions retrieved successfully")

        except Exception as e:
            return error_response(f"Failed to get generated questions: {str(e)}", 500)

    @app.route('/api/user/mcq-generation-cancel/<generation_id>', methods=['POST'])
    @user_required
    def api_cancel_mcq_generation(generation_id):
        """Cancel ongoing MCQ generation"""
        try:
            user = get_current_user()
            if not user:
                return error_response("User not found", 404)

            from shared.services.chunked_mcq_service_simple import get_chunked_mcq_service

            chunked_service = get_chunked_mcq_service()
            result = chunked_service.cancel_generation(generation_id)

            if not result['success']:
                return error_response(result['error'], 400)

            return success_response(result, "MCQ generation cancelled successfully")

        except Exception as e:
            return error_response(f"Failed to cancel generation: {str(e)}", 500)





    @app.route('/api/user/test/<int:test_attempt_id>/submit', methods=['POST'])
    @user_required
    def api_submit_test(test_attempt_id):
        """Submit test answers and calculate results"""
        try:
            user = get_current_user()
            if not user:
                return error_response("User not found", 404)

            # Verify test attempt belongs to user
            test_attempt = TestAttempt.query.filter_by(
                id=test_attempt_id,
                user_id=user.id
            ).first()

            if not test_attempt:
                return error_response("Test attempt not found", 404)

            if test_attempt.status != 'in_progress':
                return error_response("Test attempt is not in progress", 400)

            data = request.get_json()
            answers = data.get('answers', {})  # {question_id: selected_option_index}
            time_taken = data.get('time_taken', 0)  # in seconds

            # Get all questions for this test attempt
            questions = ExamCategoryQuestion.query.filter_by(
                purchased_id=test_attempt.purchase_id,
                subject_id=test_attempt.subject_id
            ).all()

            if not questions:
                return error_response("No questions found for this test", 404)

            # Calculate results
            correct_answers = 0
            wrong_answers = 0
            unanswered = 0

            # Save individual answers
            for question in questions:
                question_id = str(question.id)
                if question_id in answers:
                    selected_option_index = answers[question_id]
                    selected_option = [question.option_1, question.option_2, question.option_3, question.option_4][selected_option_index]
                    is_correct = selected_option == question.correct_answer

                    if is_correct:
                        correct_answers += 1
                    else:
                        wrong_answers += 1

                    # Create a temporary session for legacy compatibility
                    # Check if a session already exists for this test attempt
                    existing_session = TestAttemptSession.query.filter_by(
                        user_id=user.id,
                        mock_test_id=None  # Legacy sessions don't have mock_test_id
                    ).filter(
                        TestAttemptSession.created_at >= test_attempt.started_at
                    ).first()

                    if not existing_session:
                        # Create a temporary session for this legacy test
                        temp_session = TestAttemptSession(
                            mock_test_id=None,  # Legacy compatibility
                            user_id=user.id,
                            attempt_number=1,
                            status='in_progress'
                        )
                        db.session.add(temp_session)
                        db.session.flush()  # Get the session ID
                        session_id = temp_session.id
                    else:
                        session_id = existing_session.id

                    # Save answer using session_id
                    test_answer = TestAnswer(
                        session_id=session_id,
                        question_id=question.id,
                        selected_answer=selected_option,
                        is_correct=is_correct,
                        time_taken=0  # Individual question time not tracked yet
                    )
                    db.session.add(test_answer)
                else:
                    unanswered += 1

            # Update test attempt with results
            test_attempt.correct_answers = correct_answers
            test_attempt.wrong_answers = wrong_answers
            test_attempt.unanswered = unanswered
            test_attempt.marks_scored = correct_answers  # 1 mark per correct answer
            test_attempt.percentage = (correct_answers / len(questions)) * 100 if questions else 0
            test_attempt.time_taken = time_taken
            test_attempt.completed_at = datetime.utcnow()
            test_attempt.status = 'completed'

            # Update the temporary session if it was created
            if 'session_id' in locals():
                temp_session = TestAttemptSession.query.get(session_id)
                if temp_session:
                    temp_session.score = correct_answers
                    temp_session.percentage = test_attempt.percentage
                    temp_session.time_taken = time_taken
                    temp_session.correct_answers = correct_answers
                    temp_session.wrong_answers = wrong_answers
                    temp_session.unanswered = unanswered
                    temp_session.status = 'completed'
                    temp_session.completed_at = datetime.utcnow()

            # Update purchase mock_tests_used counter
            purchase = test_attempt.purchase
            if purchase:
                purchase.mock_tests_used = (purchase.mock_tests_used or 0) + 1
                purchase.last_attempt_date = datetime.utcnow()

            db.session.commit()

            return success_response({
                'test_attempt_id': test_attempt.id,
                'total_questions': len(questions),
                'correct_answers': correct_answers,
                'wrong_answers': wrong_answers,
                'unanswered': unanswered,
                'marks_scored': test_attempt.marks_scored,
                'total_marks': test_attempt.total_marks,
                'percentage': float(test_attempt.percentage),
                'time_taken': time_taken,
                'completed_at': test_attempt.completed_at.isoformat()
            }, "Test submitted successfully")

        except Exception as e:
            db.session.rollback()
            return error_response(f"Failed to submit test: {str(e)}", 500)

    @app.route('/api/purchases', methods=['GET'])
    @user_required
    def api_get_user_purchases():
        """Get current user's purchases"""
        try:
            user = get_current_user()
            if not user:
                return error_response("User not found", 404)

            page = request.args.get('page', 1, type=int)
            per_page = request.args.get('per_page', 10, type=int)

            # Get user's purchases
            purchases = ExamCategoryPurchase.query.filter_by(user_id=user.id).order_by(
                ExamCategoryPurchase.purchase_date.desc()
            ).paginate(page=page, per_page=per_page, error_out=False)

            return success_response({
                'purchases': [purchase.to_dict() for purchase in purchases.items],
                'pagination': {
                    'page': purchases.page,
                    'pages': purchases.pages,
                    'per_page': purchases.per_page,
                    'total': purchases.total,
                    'has_next': purchases.has_next,
                    'has_prev': purchases.has_prev
                }
            }, "Purchases retrieved successfully")

        except Exception as e:
            return error_response(f"Failed to get purchases: {str(e)}", 500)

    @app.route('/api/create-test-user', methods=['POST'])
    def api_create_test_user():
        """Create a test user account for demo purposes"""
        try:
            data = request.get_json() or {}
            user_suffix = data.get('suffix', '')
            email = f'testuser{user_suffix}@jishu.com'

            # Check if test user already exists
            existing_user = User.query.filter_by(email_id=email).first()
            if existing_user:
                # Generate JWT tokens for existing user
                access_token = create_access_token(identity=str(existing_user.id))
                refresh_token = create_refresh_token(identity=str(existing_user.id))

                return success_response({
                    'user': existing_user.to_dict(),
                    'access_token': access_token,
                    'refresh_token': refresh_token,
                    'message': 'Test user already exists'
                }, "Test user retrieved successfully")

            # Create test user
            test_user = User(
                name=f'Test Admin User{user_suffix}',
                email_id=email,
                mobile_no=f'999999999{user_suffix[-1] if user_suffix else "9"}',
                otp_verified=True,
                is_admin=True,  # Make this user an admin for testing
                color_theme='light',
                status='active',
                auth_provider='manual',
                source='test'
            )

            db.session.add(test_user)
            db.session.flush()  # Get the user ID

            # Generate JWT tokens
            access_token = create_access_token(identity=str(test_user.id))
            refresh_token = create_refresh_token(identity=str(test_user.id))

            # Store refresh token
            refresh_expires_at = datetime.utcnow() + timedelta(seconds=app.config['JWT_REFRESH_TOKEN_EXPIRES'])
            test_user.set_refresh_token(refresh_token, refresh_expires_at)

            db.session.commit()

            return success_response({
                'user': test_user.to_dict(),
                'access_token': access_token,
                'refresh_token': refresh_token,
                'message': 'Test admin user created successfully. You can now use the provided tokens.'
            }, "Test user created successfully")

        except Exception as e:
            db.session.rollback()
            return error_response(f"Failed to create test user: {str(e)}", 500)

    @app.route('/api/dev/reset-purchases', methods=['POST'])
    @user_required
    def api_dev_reset_purchases():
        """Development endpoint - Reset current user's purchases"""
        if not app.config.get('LOCAL_DEV_MODE', False):
            return error_response("This endpoint is only available in development mode", 403)

        try:
            user = get_current_user()
            if not user:
                return error_response("User not found", 404)

            # Delete all purchases for current user
            deleted_count = ExamCategoryPurchase.query.filter_by(user_id=user.id).delete()
            db.session.commit()

            return success_response({
                'deleted_purchases': deleted_count,
                'user_email': user.email_id
            }, f"Reset {deleted_count} purchases for development testing")

        except Exception as e:
            db.session.rollback()
            return error_response(f"Failed to reset purchases: {str(e)}", 500)

    @app.route('/api/admin/chat/tokens', methods=['GET'])
    @admin_required
    def api_admin_chat_tokens():
        """Get all users' chat token statistics"""
        try:
            page = request.args.get('page', 1, type=int)
            per_page = request.args.get('per_page', 10, type=int)
            month_year = request.args.get('month_year')

            # Build query
            query = UserAIStats.query

            if month_year:
                query = query.filter_by(month_year=month_year)

            # Join with user table to get user details
            query = query.join(User).order_by(UserAIStats.total_tokens_used.desc())

            # Paginate results
            stats = query.paginate(page=page, per_page=per_page, error_out=False)

            result_data = []
            for stat in stats.items:
                result_data.append({
                    **stat.to_dict(),
                    'user_name': stat.user.name,
                    'user_email': stat.user.email_id
                })

            return success_response({
                'token_stats': result_data,
                'pagination': {
                    'page': stats.page,
                    'pages': stats.pages,
                    'per_page': stats.per_page,
                    'total': stats.total,
                    'has_next': stats.has_next,
                    'has_prev': stats.has_prev
                }
            }, "Token statistics retrieved successfully")

        except Exception as e:
            return error_response(f"Failed to get token statistics: {str(e)}", 500)

    # Track MCQ generation requests to prevent duplicates
    mcq_generation_requests = {}

    # Vector Store Management Endpoints (Admin Only)
    @app.route('/api/admin/vector-store/status', methods=['GET'])
    @admin_required
    def api_admin_vector_store_status():
        """Get vector store status and statistics"""
        try:
            from shared.services.vector_store_manager import get_vector_store_manager
            from shared.services.optimized_ai_service import get_optimized_ai_service

            vector_manager = get_vector_store_manager()
            optimized_service = get_optimized_ai_service()

            # Get comprehensive status
            vector_status = vector_manager.get_status()
            service_status = optimized_service.get_status()
            collection_stats = vector_manager.get_collection_stats()

            return success_response({
                'vector_store_status': vector_status,
                'optimized_service_status': service_status,
                'collection_statistics': collection_stats,
                'performance_report': optimized_service.get_performance_report()
            }, "Vector store status retrieved successfully")

        except Exception as e:
            return error_response(f"Failed to get vector store status: {str(e)}", 500)

    @app.route('/api/admin/vector-store/initialize', methods=['POST'])
    @admin_required
    def api_admin_vector_store_initialize():
        """Initialize vector stores for specified subjects"""
        try:
            data = request.get_json() or {}
            subjects = data.get('subjects', None)  # None means all subjects
            force_recreate = data.get('force_recreate', False)

            from shared.services.vector_store_manager import get_vector_store_manager

            vector_manager = get_vector_store_manager()

            if subjects:
                # Initialize specific subjects
                results = {}
                for subject in subjects:
                    results[subject] = vector_manager.create_subject_vector_store(subject, force_recreate)
            else:
                # Initialize all subjects
                results = vector_manager.initialize_all_subjects(force_recreate)

            successful = sum(1 for success in results.values() if success)
            total = len(results)

            return success_response({
                'results': results,
                'summary': {
                    'successful': successful,
                    'total': total,
                    'success_rate': successful / total if total > 0 else 0
                }
            }, f"Vector store initialization completed: {successful}/{total} subjects successful")

        except Exception as e:
            return error_response(f"Failed to initialize vector stores: {str(e)}", 500)

    @app.route('/api/admin/vector-store/reset', methods=['POST'])
    @admin_required
    def api_admin_vector_store_reset():
        """Reset all vector stores"""
        try:
            data = request.get_json() or {}
            confirm = data.get('confirm', False)

            if not confirm:
                return error_response("Reset confirmation required. Set 'confirm': true in request body", 400)

            from shared.services.vector_store_manager import get_vector_store_manager
            from shared.services.optimized_ai_service import get_optimized_ai_service

            vector_manager = get_vector_store_manager()
            optimized_service = get_optimized_ai_service()

            # Reset vector stores
            reset_success = vector_manager.reset_all_vector_stores()

            # Clear service cache
            optimized_service.clear_cache()

            if reset_success:
                return success_response({
                    'reset_successful': True,
                    'cache_cleared': True
                }, "All vector stores reset successfully")
            else:
                return error_response("Failed to reset vector stores", 500)

        except Exception as e:
            return error_response(f"Failed to reset vector stores: {str(e)}", 500)

    @app.route('/api/admin/vector-store/subject/<subject>/reindex', methods=['POST'])
    @admin_required
    def api_admin_vector_store_reindex_subject(subject):
        """Reindex vector store for a specific subject"""
        try:
            # Validate subject
            valid_subjects = ['physics', 'chemistry', 'biology', 'mathematics', 'computer_science']
            if subject not in valid_subjects:
                return error_response(f"Invalid subject. Must be one of: {', '.join(valid_subjects)}", 400)

            from shared.services.vector_store_manager import get_vector_store_manager

            vector_manager = get_vector_store_manager()

            # Force recreate the vector store for this subject
            success = vector_manager.create_subject_vector_store(subject, force_recreate=True)

            if success:
                # Get updated stats
                stats = vector_manager.get_collection_stats()
                subject_stats = stats.get(subject, {})

                return success_response({
                    'subject': subject,
                    'reindex_successful': True,
                    'collection_stats': subject_stats
                }, f"Vector store for {subject} reindexed successfully")
            else:
                return error_response(f"Failed to reindex vector store for {subject}", 500)

        except Exception as e:
            return error_response(f"Failed to reindex {subject}: {str(e)}", 500)

    @app.route('/api/admin/vector-store/performance', methods=['GET'])
    @admin_required
    def api_admin_vector_store_performance():
        """Get vector store performance metrics"""
        try:
            from shared.services.optimized_ai_service import get_optimized_ai_service

            optimized_service = get_optimized_ai_service()
            performance_report = optimized_service.get_performance_report()

            return success_response({
                'performance_metrics': performance_report,
                'recommendations': {
                    'cache_hit_rate': 'Good' if performance_report.get('cache_hit_rate', 0) > 0.3 else 'Consider increasing cache size',
                    'average_generation_time': 'Excellent' if performance_report.get('average_generation_time', 999) < 10 else 'Consider optimizing retrieval parameters'
                }
            }, "Performance metrics retrieved successfully")

        except Exception as e:
            return error_response(f"Failed to get performance metrics: {str(e)}", 500)









    # Question Management Endpoints
    @app.route('/api/questions', methods=['GET'])
    @user_required
    def api_get_questions():
        """Get questions with optional filtering"""
        try:
            page = request.args.get('page', 1, type=int)
            per_page = request.args.get('per_page', 20, type=int)
            exam_category_id = request.args.get('exam_category_id', type=int)
            subject_id = request.args.get('subject_id', type=int)
            difficulty = request.args.get('difficulty')

            # Build query
            query = ExamCategoryQuestion.query

            if exam_category_id:
                query = query.filter_by(exam_category_id=exam_category_id)

            if subject_id:
                query = query.filter_by(subject_id=subject_id)

            # Note: difficulty is not in the current model, but we can add it later

            # Order by creation date
            query = query.order_by(ExamCategoryQuestion.created_at.desc())

            # Paginate results
            questions = query.paginate(page=page, per_page=per_page, error_out=False)

            # Get current user to determine if they can see answers
            user = get_current_user()
            include_answers = user.is_admin if user else False

            result_data = []
            for question in questions.items:
                result_data.append(question.to_dict(include_answer=include_answers))

            return success_response({
                'questions': result_data,
                'pagination': {
                    'page': questions.page,
                    'pages': questions.pages,
                    'per_page': questions.per_page,
                    'total': questions.total,
                    'has_next': questions.has_next,
                    'has_prev': questions.has_prev
                }
            }, "Questions retrieved successfully")

        except Exception as e:
            return error_response(f"Failed to get questions: {str(e)}", 500)

    @app.route('/api/questions/<int:question_id>', methods=['GET'])
    @user_required
    def api_get_question_by_id(question_id):
        """Get a specific question by ID"""
        try:
            question = ExamCategoryQuestion.query.get(question_id)
            if not question:
                return error_response("Question not found", 404)

            # Get current user to determine if they can see answers
            user = get_current_user()
            include_answers = user.is_admin if user else False

            return success_response({
                'question': question.to_dict(include_answer=include_answers)
            }, "Question retrieved successfully")

        except Exception as e:
            return error_response(f"Failed to get question: {str(e)}", 500)

    @app.route('/api/admin/questions', methods=['POST'])
    @admin_required
    def api_admin_create_question():
        """Create a new question manually (Admin only)"""
        try:
            data = request.get_json()

            # Required fields
            required_fields = ['exam_category_id', 'subject_id', 'question', 'option_1', 'option_2', 'option_3', 'option_4', 'correct_answer']
            for field in required_fields:
                if field not in data:
                    return error_response(f"{field} is required", 400)

            # Validate exam category and subject
            exam_category = ExamCategory.query.get(data['exam_category_id'])
            if not exam_category:
                return error_response("Exam category not found", 404)

            subject = ExamCategorySubject.query.get(data['subject_id'])
            if not subject:
                return error_response("Subject not found", 404)

            # Validate that subject belongs to the exam category
            if subject.exam_category_id != data['exam_category_id']:
                return error_response("Subject does not belong to the specified exam category", 400)

            # Validate correct answer
            valid_options = [data['option_1'], data['option_2'], data['option_3'], data['option_4']]
            if data['correct_answer'] not in valid_options:
                return error_response("Correct answer must match one of the provided options", 400)

            user = get_current_user()

            # Create question
            question = ExamCategoryQuestion(
                exam_category_id=data['exam_category_id'],
                subject_id=data['subject_id'],
                question=data['question'],
                option_1=data['option_1'],
                option_2=data['option_2'],
                option_3=data['option_3'],
                option_4=data['option_4'],
                correct_answer=data['correct_answer'],
                explanation=data.get('explanation', ''),
                user_id=user.id,
                is_ai_generated=False,  # Manual creation
                difficulty_level=data.get('difficulty_level', 'medium')
            )

            db.session.add(question)
            db.session.commit()

            return success_response({
                'question': question.to_dict(include_answer=True)
            }, "Question created successfully")

        except Exception as e:
            db.session.rollback()
            return error_response(f"Failed to create question: {str(e)}", 500)

    @app.route('/api/admin/questions/<int:question_id>', methods=['PUT'])
    @admin_required
    def api_admin_update_question(question_id):
        """Update a question (Admin only)"""
        try:
            question = ExamCategoryQuestion.query.get(question_id)
            if not question:
                return error_response("Question not found", 404)

            data = request.get_json()

            # Update fields if provided
            if 'question' in data:
                question.question = data['question']

            if 'option_1' in data:
                question.option_1 = data['option_1']

            if 'option_2' in data:
                question.option_2 = data['option_2']

            if 'option_3' in data:
                question.option_3 = data['option_3']

            if 'option_4' in data:
                question.option_4 = data['option_4']

            if 'correct_answer' in data:
                # Validate correct answer against current options
                valid_options = [question.option_1, question.option_2, question.option_3, question.option_4]
                if data['correct_answer'] not in valid_options:
                    return error_response("Correct answer must match one of the provided options", 400)
                question.correct_answer = data['correct_answer']

            if 'explanation' in data:
                question.explanation = data['explanation']

            if 'exam_category_id' in data:
                exam_category = ExamCategory.query.get(data['exam_category_id'])
                if not exam_category:
                    return error_response("Exam category not found", 404)
                question.exam_category_id = data['exam_category_id']

            if 'subject_id' in data:
                subject = ExamCategorySubject.query.get(data['subject_id'])
                if not subject:
                    return error_response("Subject not found", 404)
                # Validate that subject belongs to the exam category
                if subject.exam_category_id != question.exam_category_id:
                    return error_response("Subject does not belong to the specified exam category", 400)
                question.subject_id = data['subject_id']

            question.updated_at = datetime.utcnow()
            db.session.commit()

            return success_response({
                'question': question.to_dict(include_answer=True)
            }, "Question updated successfully")

        except Exception as e:
            db.session.rollback()
            return error_response(f"Failed to update question: {str(e)}", 500)

    @app.route('/api/admin/questions/<int:question_id>', methods=['DELETE'])
    @admin_required
    def api_admin_delete_question(question_id):
        """Delete a question (Admin only)"""
        try:
            question = ExamCategoryQuestion.query.get(question_id)
            if not question:
                return error_response("Question not found", 404)

            # Check if question is used in any test attempts
            test_answers = TestAnswer.query.filter_by(question_id=question_id).first()
            if test_answers:
                return error_response("Cannot delete question that has been used in test attempts", 400)

            db.session.delete(question)
            db.session.commit()

            return success_response({
                'message': 'Question deleted successfully',
                'deleted_question_id': question_id
            }, "Question deleted successfully")

        except Exception as e:
            db.session.rollback()
            return error_response(f"Failed to delete question: {str(e)}", 500)

    @app.route('/api/admin/questions/bulk-delete', methods=['POST'])
    @admin_required
    def api_admin_bulk_delete_questions():
        """Bulk delete questions (Admin only)"""
        try:
            data = request.get_json()
            question_ids = data.get('question_ids', [])

            if not question_ids or not isinstance(question_ids, list):
                return error_response("question_ids must be a non-empty list", 400)

            # Check if any questions are used in test attempts
            used_questions = TestAnswer.query.filter(TestAnswer.question_id.in_(question_ids)).all()
            if used_questions:
                used_ids = [str(answer.question_id) for answer in used_questions]
                return error_response(f"Cannot delete questions that have been used in test attempts. Question IDs: {', '.join(used_ids)}", 400)

            # Delete questions
            deleted_count = ExamCategoryQuestion.query.filter(ExamCategoryQuestion.id.in_(question_ids)).delete(synchronize_session=False)
            db.session.commit()

            return success_response({
                'message': f'{deleted_count} questions deleted successfully',
                'deleted_count': deleted_count,
                'requested_ids': question_ids
            }, "Questions deleted successfully")

        except Exception as e:
            db.session.rollback()
            return error_response(f"Failed to bulk delete questions: {str(e)}", 500)

    # Admin User Management Endpoints
    @app.route('/api/admin/users', methods=['GET'])
    @admin_required
    def api_admin_get_users():
        """List all users (Admin only)"""
        try:
            # Validate pagination parameters
            page = request.args.get('page', 1, type=int)
            per_page = request.args.get('per_page', 10, type=int)

            if page < 1:
                return error_response("Page number must be greater than 0", 422)
            if per_page < 1 or per_page > 100:
                return error_response("Per page must be between 1 and 100", 422)

            status = request.args.get('status')
            source = request.args.get('source')
            search = request.args.get('search', '').strip()

            # Validate status parameter
            if status and status not in ['active', 'inactive', 'blocked']:
                return error_response("Invalid status. Must be 'active', 'inactive', or 'blocked'", 422)

            # Build query
            query = User.query

            if status:
                query = query.filter(User.status == status)
            if source:
                query = query.filter(User.source == source)
            if search:
                query = query.filter(
                    (User.name.ilike(f'%{search}%')) |
                    (User.email_id.ilike(f'%{search}%'))
                )

            # Order by creation date (newest first)
            query = query.order_by(User.created_at.desc())

            # Paginate results
            users = query.paginate(page=page, per_page=per_page, error_out=False)

            return success_response({
                'users': [user.to_dict() for user in users.items],
                'pagination': {
                    'page': users.page,
                    'pages': users.pages,
                    'per_page': users.per_page,
                    'total': users.total,
                    'has_next': users.has_next,
                    'has_prev': users.has_prev
                }
            }, "Users retrieved successfully")

        except Exception as e:
            import traceback
            print(f"Error in api_admin_get_users: {str(e)}")
            print(f"Traceback: {traceback.format_exc()}")
            return error_response(f"Failed to get users: {str(e)}", 500)

    @app.route('/api/admin/users/<int:user_id>/deactivate', methods=['PUT'])
    @admin_required
    def api_admin_deactivate_user(user_id):
        """Deactivate user account (Admin only)"""
        try:
            user = User.query.get(user_id)
            if not user:
                return error_response("User not found", 404)

            # Prevent admin from deactivating themselves
            current_user = get_current_user()
            if current_user.id == user_id:
                return error_response("You cannot deactivate your own account", 400)

            user.status = 'inactive'
            user.clear_refresh_token()  # Clear any active sessions

            db.session.commit()

            return success_response({
                'message': 'User account deactivated successfully',
                'user': user.to_dict()
            }, "User deactivated successfully")

        except Exception as e:
            db.session.rollback()
            return error_response(f"Failed to deactivate user: {str(e)}", 500)

    @app.route('/api/admin/users/<int:user_id>/purchases', methods=['GET'])
    @admin_required
    def api_admin_get_user_purchases(user_id):
        """Get user's purchase history (Admin only)"""
        try:
            user = User.query.get(user_id)
            if not user:
                return error_response("User not found", 404)

            page = request.args.get('page', 1, type=int)
            per_page = request.args.get('per_page', 10, type=int)

            # Get user's purchases
            purchases = ExamCategoryPurchase.query.filter_by(user_id=user_id).order_by(
                ExamCategoryPurchase.purchase_date.desc()
            ).paginate(page=page, per_page=per_page, error_out=False)

            return success_response({
                'user': user.to_dict(),
                'purchases': [purchase.to_dict() for purchase in purchases.items],
                'pagination': {
                    'page': purchases.page,
                    'pages': purchases.pages,
                    'per_page': purchases.per_page,
                    'total': purchases.total,
                    'has_next': purchases.has_next,
                    'has_prev': purchases.has_prev
                }
            }, "User purchases retrieved successfully")

        except Exception as e:
            return error_response(f"Failed to get user purchases: {str(e)}", 500)

    @app.route('/api/admin/users/<int:user_id>/chat_tokens', methods=['GET'])
    @admin_required
    def api_admin_get_user_chat_tokens(user_id):
        """Get user's AI chat token usage (Admin only)"""
        try:
            user = User.query.get(user_id)
            if not user:
                return error_response("User not found", 404)

            # Get user's AI stats
            ai_stats = UserAIStats.query.filter_by(user_id=user_id).order_by(
                UserAIStats.month_year.desc()
            ).all()

            # Get recent chat history
            recent_chats = AIChatHistory.query.filter_by(user_id=user_id).order_by(
                AIChatHistory.created_at.desc()
            ).limit(10).all()

            # Calculate totals
            total_queries = sum(stat.total_queries for stat in ai_stats)
            total_tokens = sum(stat.total_tokens_used for stat in ai_stats)

            return success_response({
                'user': user.to_dict(),
                'ai_stats': [stat.to_dict() for stat in ai_stats],
                'recent_chats': [chat.to_dict() for chat in recent_chats],
                'summary': {
                    'total_queries': total_queries,
                    'total_tokens_used': total_tokens,
                    'last_query_date': ai_stats[0].last_query_date.isoformat() if ai_stats and ai_stats[0].last_query_date else None
                }
            }, "User AI token usage retrieved successfully")

        except Exception as e:
            return error_response(f"Failed to get user AI token usage: {str(e)}", 500)

    @app.route('/api/admin/stats', methods=['GET'])
    @admin_required
    def api_admin_get_stats():
        """Get admin dashboard statistics (Admin only)"""
        try:
            # Get total users count
            total_users = User.query.count()
            active_users = User.query.filter_by(status='active').count()

            # Get total courses and subjects
            total_courses = ExamCategory.query.count()
            total_subjects = ExamCategorySubject.query.count()

            # Get total blog posts
            total_posts = BlogPost.query.count()
            published_posts = BlogPost.query.filter_by(status='published').count()

            # Get total purchases (if Purchase model exists)
            total_purchases = 0
            total_revenue = 0
            try:
                from shared.models.purchase import Purchase
                total_purchases = Purchase.query.count()
                # Calculate total revenue (assuming amount is in paisa/cents)
                revenue_result = db.session.query(db.func.sum(Purchase.amount)).scalar()
                total_revenue = revenue_result or 0
            except ImportError:
                # Purchase model doesn't exist yet
                pass

            # Get AI chat statistics
            total_ai_queries = 0
            total_tokens_used = 0
            try:
                from shared.models.ai_chat import UserAIStats
                ai_stats = db.session.query(
                    db.func.sum(UserAIStats.total_queries),
                    db.func.sum(UserAIStats.total_tokens_used)
                ).first()
                total_ai_queries = ai_stats[0] or 0
                total_tokens_used = ai_stats[1] or 0
            except ImportError:
                # AI models don't exist yet
                pass

            # Calculate average score (placeholder - implement based on your test results model)
            average_score = 75.5  # Placeholder value

            # Get recent activity counts (last 30 days)
            from datetime import datetime, timedelta
            thirty_days_ago = datetime.utcnow() - timedelta(days=30)

            recent_users = User.query.filter(User.created_at >= thirty_days_ago).count()
            recent_posts = BlogPost.query.filter(BlogPost.created_at >= thirty_days_ago).count()

            stats = {
                'totalUsers': total_users,
                'activeUsers': active_users,
                'totalCourses': total_courses,
                'totalSubjects': total_subjects,
                'totalPosts': total_posts,
                'publishedPosts': published_posts,
                'totalPurchases': total_purchases,
                'totalRevenue': total_revenue,
                'totalAIQueries': total_ai_queries,
                'totalTokensUsed': total_tokens_used,
                'averageScore': average_score,
                'recentUsers': recent_users,
                'recentPosts': recent_posts,
                'totalTests': total_subjects,  # Using subjects as tests for now
                'monthlyRevenue': total_revenue  # Same as total for now
            }

            return success_response({
                'stats': stats
            }, "Admin statistics retrieved successfully")

        except Exception as e:
            return error_response(f"Failed to get admin statistics: {str(e)}", 500)

    # --- GOOGLE OAUTH ENDPOINTS (LEGACY - KEEPING FOR COMPATIBILITY) ---
    @app.route('/auth/google', methods=['GET'])
    def google_auth():
        """Redirect user to Google OAuth consent screen"""
        try:
            if not google_oauth:
                return error_response("Google OAuth not configured", 503)

            authorization_url, state = google_oauth.get_authorization_url()
            if not authorization_url:
                return error_response("Failed to generate Google authorization URL", 500)

            # Store state in session for security (optional)
            from flask import session
            session['oauth_state'] = state

            # Return redirect URL for frontend to use
            return success_response({
                'authorization_url': authorization_url,
                'state': state
            }, "Google authorization URL generated")

        except Exception as e:
            return error_response(f"Google OAuth initialization failed: {str(e)}", 500)

    @app.route('/auth/google/callback', methods=['GET'])
    def google_callback():
        """Handle Google OAuth callback"""
        try:
            if not google_oauth:
                return error_response("Google OAuth not configured", 503)

            from flask import request
            authorization_code = request.args.get('code')
            if not authorization_code:
                return error_response("Authorization code not provided", 400)

            # Exchange code for user info
            success, user_info = google_oauth.exchange_code_for_token(authorization_code)
            if not success:
                return error_response(f"Failed to get user info from Google: {user_info}", 400)

            # Extract user information
            email = user_info.get('email')
            name = user_info.get('name')
            google_id = user_info.get('id')

            if not email or not name or not google_id:
                return error_response("Incomplete user information from Google", 400)

            # Check if user exists
            user = User.query.filter_by(email_id=email).first()

            if user:
                # User exists - update Google ID if not set and log them in
                if not user.google_id:
                    user.google_id = google_id
                    user.auth_provider = 'google'
                    user.source = 'google'

                user.last_login = datetime.utcnow()
                user.otp_verified = True  # Google users are automatically verified

                # Generate JWT tokens
                access_token = create_access_token(identity=str(user.id))
                refresh_token = create_refresh_token(identity=str(user.id))

                # Store refresh token in database
                refresh_expires_at = datetime.utcnow() + timedelta(seconds=app.config['JWT_REFRESH_TOKEN_EXPIRES'])
                user.set_refresh_token(refresh_token, refresh_expires_at)

                db.session.commit()

                return success_response({
                    'user': user.to_dict(),
                    'access_token': access_token,
                    'refresh_token': refresh_token
                }, "Login successful with Google")

            else:
                # User doesn't exist - create new user
                new_user = User(
                    email_id=email,
                    name=name,
                    google_id=google_id,
                    auth_provider='google',
                    source='google',
                    otp_verified=True,
                    mobile_no='',  # Google doesn't provide mobile number
                    status='active'
                )

                # Generate JWT tokens
                access_token = create_access_token(identity=str(new_user.id))
                refresh_token = create_refresh_token(identity=str(new_user.id))

                # Store refresh token in database
                refresh_expires_at = datetime.utcnow() + timedelta(seconds=app.config['JWT_REFRESH_TOKEN_EXPIRES'])
                new_user.set_refresh_token(refresh_token, refresh_expires_at)

                db.session.add(new_user)
                db.session.commit()

                return success_response({
                    'user': new_user.to_dict(),
                    'access_token': access_token,
                    'refresh_token': refresh_token
                }, "Registration and login successful with Google")

        except Exception as e:
            db.session.rollback()
            return error_response(f"Google OAuth callback failed: {str(e)}", 500)

    # Track processed authorization codes to prevent duplicate processing
    processed_auth_codes = set()
    # Add session tracking to prevent duplicate calls per session
    session_oauth_attempts = {}

    @app.route('/api/auth/google/verify', methods=['POST'])
    def api_google_verify():
        """Verify Google OAuth authorization code from frontend - called once per session"""
        try:
            if not google_oauth:
                return error_response("Google OAuth not configured", 503)

            data = request.get_json()
            authorization_code = data.get('code')
            session_id = data.get('session_id')  # Frontend should provide session identifier

            if not authorization_code:
                return error_response("Authorization code not provided", 400)

            # Check if this authorization code has already been processed
            code_hash = authorization_code[:20]  # Use first 20 chars as identifier
            if code_hash in processed_auth_codes:
                print(f"⚠️ Authorization code already processed: {code_hash}...")
                return error_response("Authorization code has already been used", 400)

            # Check if this session has already attempted OAuth (prevent duplicate calls)
            if session_id and session_id in session_oauth_attempts:
                print(f"⚠️ OAuth already attempted for session: {session_id}")
                return error_response("OAuth already attempted for this session", 400)

            # Mark this code as being processed and track session
            processed_auth_codes.add(code_hash)
            if session_id:
                session_oauth_attempts[session_id] = True

            print(f"🔄 Processing Google OAuth verification...")
            print(f"🔧 Authorization code received: {authorization_code[:20]}...")
            print(f"🔧 Google OAuth redirect URI: {google_oauth.redirect_uri}")

            # Exchange code for user info
            success, user_info = google_oauth.exchange_code_for_token(authorization_code)
            if not success:
                print(f"❌ Google OAuth exchange failed: {user_info}")
                # Remove from processed set and session tracking on failure so it can be retried
                processed_auth_codes.discard(code_hash)
                if session_id:
                    session_oauth_attempts.pop(session_id, None)
                return error_response(f"Failed to get user info from Google: {user_info}", 400)

            # Extract user information
            email = user_info.get('email')
            name = user_info.get('name')
            google_id = user_info.get('id')

            if not email or not name or not google_id:
                return error_response("Incomplete user information from Google", 400)

            # Check if user exists
            user = User.query.filter_by(email_id=email).first()

            if user:
                # Enhanced: Allow Google login regardless of original auth provider
                # This enables users to login with Google even if they originally registered with OTP
                # Removed the restriction: if user.auth_provider == 'manual' and user.google_id is None

                # User exists - update Google ID if not set and log them in
                if not user.google_id:
                    user.google_id = google_id
                    # Don't override auth_provider - let user use both methods
                    if not user.source:
                        user.source = 'google'

                user.last_login = datetime.utcnow()
                user.otp_verified = True  # Google users are automatically verified

                # Generate JWT tokens
                access_token = create_access_token(identity=str(user.id))
                refresh_token = create_refresh_token(identity=str(user.id))

                # Store refresh token in database
                refresh_expires_at = datetime.utcnow() + timedelta(seconds=app.config['JWT_REFRESH_TOKEN_EXPIRES'])
                user.set_refresh_token(refresh_token, refresh_expires_at)

                db.session.commit()

                return success_response({
                    'user': user.to_dict(),
                    'access_token': access_token,
                    'refresh_token': refresh_token,
                    'auth_method_used': 'google',
                    'available_auth_methods': ['google', 'otp'] if user.auth_provider == 'manual' else ['google']
                }, "Login successful with Google")

            else:
                # User doesn't exist - create new user
                new_user = User(
                    name=name,
                    email_id=email,
                    google_id=google_id,
                    auth_provider='google',
                    source='google',
                    otp_verified=True,
                    is_verified=True,
                    role='user'
                )

                db.session.add(new_user)
                db.session.flush()  # Get the user ID

                # Generate JWT tokens
                access_token = create_access_token(identity=str(new_user.id))
                refresh_token = create_refresh_token(identity=str(new_user.id))

                # Store refresh token in database
                refresh_expires_at = datetime.utcnow() + timedelta(seconds=app.config['JWT_REFRESH_TOKEN_EXPIRES'])
                new_user.set_refresh_token(refresh_token, refresh_expires_at)

                db.session.commit()

                return success_response({
                    'user': new_user.to_dict(),
                    'access_token': access_token,
                    'refresh_token': refresh_token
                }, "Registration and login successful with Google")

        except Exception as e:
            db.session.rollback()
            # Remove from processed set and session tracking on error so it can be retried
            if 'authorization_code' in locals():
                code_hash = authorization_code[:20]
                processed_auth_codes.discard(code_hash)
            if 'session_id' in locals() and session_id:
                session_oauth_attempts.pop(session_id, None)
            return error_response(f"Google OAuth verification failed: {str(e)}", 500)
        finally:
            # Clean up old processed codes (keep only last 100 to prevent memory issues)
            if len(processed_auth_codes) > 100:
                # Remove oldest entries (this is a simple cleanup, in production you'd want timestamp-based cleanup)
                processed_auth_codes.clear()

    @app.route('/api/debug/google-oauth', methods=['GET'])
    def debug_google_oauth():
        """Debug endpoint to check Google OAuth configuration"""
        try:
            if not google_oauth:
                return error_response("Google OAuth not configured", 503)

            config_info = {
                'client_id': app.config.get('GOOGLE_CLIENT_ID', 'Not set')[:20] + '...' if app.config.get('GOOGLE_CLIENT_ID') else 'Not set',
                'client_secret_set': bool(app.config.get('GOOGLE_CLIENT_SECRET')),
                'redirect_uri': google_oauth.redirect_uri,
                'scopes': google_oauth.scopes,
                'oauth_service_initialized': google_oauth is not None
            }

            return success_response(config_info, "Google OAuth configuration")

        except Exception as e:
            return error_response(f"Debug failed: {str(e)}", 500)

    # --- USER ENDPOINTS ---
    @app.route('/profile', methods=['GET'])
    @jwt_required()
    def get_profile():
        try:
            user_id = get_jwt_identity()
            user = User.query.get(int(user_id))
            if not user:
                return error_response("User not found", 404)
            if user.is_admin:
                # TODO: Add extra admin benefits here
                pass
            return success_response({'user': user.to_dict()}, "Profile retrieved successfully")
        except Exception as e:
            return error_response(f"Failed to get profile: {str(e)}", 500)
    @app.route('/profile', methods=['PUT'])
    @jwt_required()
    def update_profile():
        try:
            user_id = get_jwt_identity()
            user = User.query.get(int(user_id))
            if not user:
                return error_response("User not found", 404)
            if user.is_admin:
                # TODO: Add extra admin benefits here
                pass
            data = request.get_json()
            errors = {}
            if 'name' in data:
                is_valid_name, name_message = validate_name(data['name'])
                if not is_valid_name:
                    errors['name'] = name_message
                else:
                    user.name = data['name'].strip()
            if 'mobile_no' in data:
                if not validate_mobile_number(data['mobile_no']):
                    errors['mobile_no'] = "Invalid mobile number format"
                else:
                    user.mobile_no = data['mobile_no']
            if 'color_theme' in data:
                if data['color_theme'] in ['light', 'dark']:
                    user.color_theme = data['color_theme']
                else:
                    errors['color_theme'] = "Color theme must be 'light' or 'dark'"
            if errors:
                return validation_error_response(errors)
            user.updated_at = datetime.utcnow()
            db.session.commit()
            return success_response({'user': user.to_dict()}, "Profile updated successfully")
        except Exception as e:
            db.session.rollback()
            return error_response(f"Failed to update profile: {str(e)}", 500)

    # --- COMPREHENSIVE PROFILE ENDPOINTS ---

    @app.route('/api/user/profile', methods=['GET'])
    @jwt_required()
    def get_user_profile():
        """Get comprehensive user profile information"""
        try:
            user_id = get_jwt_identity()
            user = User.query.get(int(user_id))
            if not user:
                return error_response("User not found", 404)

            return success_response({
                'user': user.to_dict()
            }, "User profile retrieved successfully")
        except Exception as e:
            return error_response(f"Failed to get profile: {str(e)}", 500)

    @app.route('/api/user/profile', methods=['PATCH'])
    @jwt_required()
    def update_user_profile():
        """Update user personal information"""
        try:
            user_id = get_jwt_identity()
            user = User.query.get(int(user_id))
            if not user:
                return error_response("User not found", 404)

            data = request.get_json()
            errors = {}

            # Validate and update fields
            if 'name' in data:
                name = data['name'].strip()
                is_valid_name, name_message = validate_name(name)
                if not is_valid_name:
                    errors['name'] = name_message
                else:
                    user.name = name

            if 'mobile_no' in data:
                mobile_no = data['mobile_no'].strip()
                if mobile_no and not validate_mobile_number(mobile_no):
                    errors['mobile_no'] = 'Invalid mobile number format'
                else:
                    user.mobile_no = mobile_no

            if 'avatar' in data:
                user.avatar = data['avatar']

            if 'address' in data:
                user.address = data['address']

            if 'gender' in data:
                if data['gender'] in ['male', 'female', 'other', None]:
                    user.gender = data['gender']
                else:
                    errors['gender'] = "Gender must be 'male', 'female', or 'other'"

            if 'date_of_birth' in data:
                try:
                    if data['date_of_birth']:
                        user.date_of_birth = datetime.strptime(data['date_of_birth'], '%Y-%m-%d').date()
                except ValueError:
                    errors['date_of_birth'] = 'Invalid date format. Use YYYY-MM-DD'

            if 'city' in data:
                user.city = data['city']

            if 'state' in data:
                user.state = data['state']

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

    @app.route('/api/user/stats', methods=['GET'])
    @jwt_required()
    def get_user_stats():
        """Get user test statistics"""
        try:
            user_id = get_jwt_identity()
            user = User.query.get(int(user_id))
            if not user:
                return error_response("User not found", 404)

            # Get or create user stats
            stats = UserStats.query.filter_by(user_id=user_id).first()
            if not stats:
                stats = UserStats(user_id=user_id)
                db.session.add(stats)
                db.session.commit()

            return success_response({
                'stats': stats.to_dict()
            }, "User stats retrieved successfully")
        except Exception as e:
            return error_response(f"Failed to get stats: {str(e)}", 500)

    @app.route('/api/user/academics', methods=['GET'])
    @jwt_required()
    def get_user_academics():
        """Get user academic information"""
        try:
            user_id = get_jwt_identity()
            user = User.query.get(int(user_id))
            if not user:
                return error_response("User not found", 404)

            # Get or create user academics
            academics = UserAcademics.query.filter_by(user_id=user_id).first()
            if not academics:
                academics = UserAcademics(user_id=user_id)
                db.session.add(academics)
                db.session.commit()

            return success_response({
                'academics': academics.to_dict()
            }, "User academics retrieved successfully")
        except Exception as e:
            return error_response(f"Failed to get academics: {str(e)}", 500)

    @app.route('/api/user/academics', methods=['PATCH'])
    @jwt_required()
    def update_user_academics():
        """Update user academic information"""
        try:
            user_id = get_jwt_identity()
            user = User.query.get(int(user_id))
            if not user:
                return error_response("User not found", 404)

            # Get or create user academics
            academics = UserAcademics.query.filter_by(user_id=user_id).first()
            if not academics:
                academics = UserAcademics(user_id=user_id)
                db.session.add(academics)

            data = request.get_json()

            if 'school_college' in data:
                academics.school_college = data['school_college']

            if 'grade_year' in data:
                academics.grade_year = data['grade_year']

            if 'board_university' in data:
                academics.board_university = data['board_university']

            if 'current_exam_target' in data:
                academics.current_exam_target = data['current_exam_target']

            academics.updated_at = datetime.utcnow()
            db.session.commit()

            return success_response({
                'academics': academics.to_dict()
            }, "Academic information updated successfully")
        except Exception as e:
            db.session.rollback()
            return error_response(f"Failed to update academics: {str(e)}", 500)

    @app.route('/api/user/purchases', methods=['GET'])
    @jwt_required()
    def get_user_purchases():
        """Get user purchase history"""
        try:
            user_id = get_jwt_identity()
            user = User.query.get(int(user_id))
            if not user:
                return error_response("User not found", 404)

            # Get purchases from exam_category_purchase table
            purchases = ExamCategoryPurchase.query.filter_by(user_id=user_id).all()

            purchase_data = []
            for purchase in purchases:
                purchase_dict = purchase.to_dict()
                # Add course and subject names
                if purchase.exam_category_id:
                    course = ExamCategory.query.get(purchase.exam_category_id)
                    if course:
                        purchase_dict['course_name'] = course.course_name

                if purchase.subject_id:
                    subject = ExamCategorySubject.query.get(purchase.subject_id)
                    if subject:
                        purchase_dict['subject_name'] = subject.subject_name

                purchase_data.append(purchase_dict)

            return success_response({
                'purchases': purchase_data
            }, "Purchase history retrieved successfully")
        except Exception as e:
            return error_response(f"Failed to get purchases: {str(e)}", 500)

    @app.route('/users', methods=['GET'])
    @jwt_required()
    def get_users():
        try:
            user_id = get_jwt_identity()
            current_user = User.query.get(int(user_id))
            if not current_user or not current_user.is_admin:
                return error_response("Admin access required", 403)
            page = request.args.get('page', 1, type=int)
            per_page = request.args.get('per_page', 10, type=int)
            status = request.args.get('status')
            source = request.args.get('source')
            query = User.query
            if status:
                query = query.filter(User.status == status)
            if source:
                query = query.filter(User.source == source)
            users = query.paginate(page=page, per_page=per_page, error_out=False)
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
    def update_user_status(user_id):
        try:
            current_user_id = get_jwt_identity()
            current_user = User.query.get(int(current_user_id))
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
            return success_response({'user': user.to_dict()}, f"User status updated to {new_status}")
        except Exception as e:
            db.session.rollback()
            return error_response(f"Failed to update user status: {str(e)}", 500)

    # --- COURSE MANAGEMENT ENDPOINTS (ADMIN ONLY) ---
    @app.route('/courses', methods=['POST'])
    @jwt_required()
    def add_course():
        """Add a new course/exam category (Admin only)"""
        try:
            user_id = get_jwt_identity()
            current_user = User.query.get(int(user_id))

            # Check admin privileges
            if not current_user or not current_user.is_admin:
                return error_response("Admin privileges required to add courses", 403)

            data = request.get_json()
            course_name = data.get('course_name')
            description = data.get('description', '')

            # Validation
            if not course_name:
                return error_response("Course name is required", 400)

            if len(course_name.strip()) < 2:
                return error_response("Course name must be at least 2 characters long", 400)

            # Check if course already exists
            existing_course = ExamCategory.query.filter_by(course_name=course_name.strip()).first()
            if existing_course:
                return error_response("Course with this name already exists", 409)

            # Create new course
            new_course = ExamCategory(
                course_name=course_name.strip(),
                description=description.strip() if description else None
            )

            db.session.add(new_course)
            db.session.commit()

            return success_response({
                'course': new_course.to_dict()
            }, "Course added successfully")

        except Exception as e:
            db.session.rollback()
            return error_response(f"Failed to add course: {str(e)}", 500)

    @app.route('/courses', methods=['GET'])
    @jwt_required()
    def get_courses():
        """Get all courses with optional filtering"""
        try:
            user_id = get_jwt_identity()
            current_user = User.query.get(int(user_id))
            if not current_user:
                return error_response("User not found", 404)

            # Query parameters
            page = request.args.get('page', 1, type=int)
            per_page = request.args.get('per_page', 10, type=int)
            include_subjects = request.args.get('include_subjects', 'false').lower() == 'true'
            search = request.args.get('search', '').strip()

            # Build query
            query = ExamCategory.query

            if search:
                query = query.filter(ExamCategory.course_name.ilike(f'%{search}%'))

            # Order by creation date (newest first)
            query = query.order_by(ExamCategory.created_at.desc())

            # Paginate
            courses = query.paginate(page=page, per_page=per_page, error_out=False)

            return success_response({
                'courses': [course.to_dict(include_subjects=include_subjects) for course in courses.items],
                'pagination': {
                    'page': courses.page,
                    'pages': courses.pages,
                    'per_page': courses.per_page,
                    'total': courses.total,
                    'has_next': courses.has_next,
                    'has_prev': courses.has_prev
                }
            }, "Courses retrieved successfully")

        except Exception as e:
            return error_response(f"Failed to get courses: {str(e)}", 500)

    @app.route('/courses/<int:course_id>', methods=['GET'])
    @jwt_required()
    def get_course_by_id(course_id):
        """Get a specific course by ID"""
        try:
            user_id = get_jwt_identity()
            current_user = User.query.get(int(user_id))
            if not current_user:
                return error_response("User not found", 404)

            course = ExamCategory.query.get(course_id)
            if not course:
                return error_response("Course not found", 404)

            include_subjects = request.args.get('include_subjects', 'true').lower() == 'true'

            return success_response({
                'course': course.to_dict(include_subjects=include_subjects)
            }, "Course retrieved successfully")

        except Exception as e:
            return error_response(f"Failed to get course: {str(e)}", 500)

    @app.route('/courses/<int:course_id>', methods=['PUT'])
    @jwt_required()
    def update_course(course_id):
        """Update a course (Admin only)"""
        try:
            user_id = get_jwt_identity()
            current_user = User.query.get(int(user_id))

            # Check admin privileges
            if not current_user or not current_user.is_admin:
                return error_response("Admin privileges required to update courses", 403)

            course = ExamCategory.query.get(course_id)
            if not course:
                return error_response("Course not found", 404)

            data = request.get_json()
            course_name = data.get('course_name')
            description = data.get('description')

            # Validation
            if course_name is not None:
                if len(course_name.strip()) < 2:
                    return error_response("Course name must be at least 2 characters long", 400)

                # Check if another course with this name exists
                existing_course = ExamCategory.query.filter(
                    ExamCategory.course_name == course_name.strip(),
                    ExamCategory.id != course_id
                ).first()
                if existing_course:
                    return error_response("Another course with this name already exists", 409)

                course.course_name = course_name.strip()

            if description is not None:
                course.description = description.strip() if description else None

            course.updated_at = datetime.utcnow()
            db.session.commit()

            return success_response({
                'course': course.to_dict(include_subjects=True)
            }, "Course updated successfully")

        except Exception as e:
            db.session.rollback()
            return error_response(f"Failed to update course: {str(e)}", 500)

    @app.route('/courses/<int:course_id>', methods=['DELETE'])
    @jwt_required()
    def delete_course(course_id):
        """Delete a course (Admin only)"""
        try:
            user_id = get_jwt_identity()
            current_user = User.query.get(int(user_id))

            # Check admin privileges
            if not current_user or not current_user.is_admin:
                return error_response("Admin privileges required to delete courses", 403)

            course = ExamCategory.query.get(course_id)
            if not course:
                return error_response("Course not found", 404)

            course_name = course.course_name
            db.session.delete(course)
            db.session.commit()

            return success_response({
                'deleted_course_id': course_id,
                'deleted_course_name': course_name
            }, "Course deleted successfully")

        except Exception as e:
            db.session.rollback()
            return error_response(f"Failed to delete course: {str(e)}", 500)

    # --- SUBJECT MANAGEMENT ENDPOINTS (ADMIN ONLY) ---
    @app.route('/courses/<int:course_id>/subjects', methods=['POST'])
    @jwt_required()
    def add_subject_to_course(course_id):
        """Add a subject to a course (Admin only)"""
        try:
            user_id = get_jwt_identity()
            current_user = User.query.get(int(user_id))

            # Check admin privileges
            if not current_user or not current_user.is_admin:
                return error_response("Admin privileges required to add subjects", 403)

            # Check if course exists
            course = ExamCategory.query.get(course_id)
            if not course:
                return error_response("Course not found", 404)

            data = request.get_json()
            subject_name = data.get('subject_name')

            # Validation
            if not subject_name:
                return error_response("Subject name is required", 400)

            if len(subject_name.strip()) < 2:
                return error_response("Subject name must be at least 2 characters long", 400)

            # Check if subject already exists in this course
            existing_subject = ExamCategorySubject.query.filter_by(
                exam_category_id=course_id,
                subject_name=subject_name.strip()
            ).first()
            if existing_subject:
                return error_response("Subject already exists in this course", 409)

            # Create new subject
            new_subject = ExamCategorySubject(
                exam_category_id=course_id,
                subject_name=subject_name.strip()
            )

            db.session.add(new_subject)
            db.session.commit()

            return success_response({
                'subject': new_subject.to_dict(),
                'course': course.to_dict()
            }, "Subject added to course successfully")

        except Exception as e:
            db.session.rollback()
            return error_response(f"Failed to add subject: {str(e)}", 500)

    @app.route('/courses/<int:course_id>/subjects', methods=['GET'])
    @jwt_required()
    def get_course_subjects(course_id):
        """Get all subjects for a specific course"""
        try:
            user_id = get_jwt_identity()
            current_user = User.query.get(int(user_id))
            if not current_user:
                return error_response("User not found", 404)

            # Check if course exists
            course = ExamCategory.query.get(course_id)
            if not course:
                return error_response("Course not found", 404)

            # Query parameters
            page = request.args.get('page', 1, type=int)
            per_page = request.args.get('per_page', 20, type=int)
            search = request.args.get('search', '').strip()

            # Build query
            query = ExamCategorySubject.query.filter_by(exam_category_id=course_id)

            if search:
                query = query.filter(ExamCategorySubject.subject_name.ilike(f'%{search}%'))

            # Order by creation date (newest first)
            query = query.order_by(ExamCategorySubject.created_at.desc())

            # Paginate
            subjects = query.paginate(page=page, per_page=per_page, error_out=False)

            return success_response({
                'course': course.to_dict(),
                'subjects': [subject.to_dict() for subject in subjects.items],
                'pagination': {
                    'page': subjects.page,
                    'pages': subjects.pages,
                    'per_page': subjects.per_page,
                    'total': subjects.total,
                    'has_next': subjects.has_next,
                    'has_prev': subjects.has_prev
                }
            }, "Course subjects retrieved successfully")

        except Exception as e:
            return error_response(f"Failed to get course subjects: {str(e)}", 500)

    @app.route('/subjects/<int:subject_id>', methods=['GET'])
    @jwt_required()
    def get_subject_by_id(subject_id):
        """Get a specific subject by ID"""
        try:
            user_id = get_jwt_identity()
            current_user = User.query.get(int(user_id))
            if not current_user:
                return error_response("User not found", 404)

            subject = ExamCategorySubject.query.get(subject_id)
            if not subject:
                return error_response("Subject not found", 404)

            return success_response({
                'subject': subject.to_dict(),
                'course': subject.exam_category.to_dict()
            }, "Subject retrieved successfully")

        except Exception as e:
            return error_response(f"Failed to get subject: {str(e)}", 500)

    @app.route('/subjects/<int:subject_id>', methods=['PUT'])
    @jwt_required()
    def update_subject(subject_id):
        """Update a subject (Admin only)"""
        try:
            user_id = get_jwt_identity()
            current_user = User.query.get(int(user_id))

            # Check admin privileges
            if not current_user or not current_user.is_admin:
                return error_response("Admin privileges required to update subjects", 403)

            subject = ExamCategorySubject.query.get(subject_id)
            if not subject:
                return error_response("Subject not found", 404)

            data = request.get_json()
            subject_name = data.get('subject_name')

            # Validation
            if not subject_name:
                return error_response("Subject name is required", 400)

            if len(subject_name.strip()) < 2:
                return error_response("Subject name must be at least 2 characters long", 400)

            # Check if another subject with this name exists in the same course
            existing_subject = ExamCategorySubject.query.filter(
                ExamCategorySubject.exam_category_id == subject.exam_category_id,
                ExamCategorySubject.subject_name == subject_name.strip(),
                ExamCategorySubject.id != subject_id
            ).first()
            if existing_subject:
                return error_response("Another subject with this name already exists in this course", 409)

            subject.subject_name = subject_name.strip()
            subject.updated_at = datetime.utcnow()
            db.session.commit()

            return success_response({
                'subject': subject.to_dict(),
                'course': subject.exam_category.to_dict()
            }, "Subject updated successfully")

        except Exception as e:
            db.session.rollback()
            return error_response(f"Failed to update subject: {str(e)}", 500)

    @app.route('/subjects/<int:subject_id>', methods=['DELETE'])
    @jwt_required()
    def delete_subject(subject_id):
        """Delete a subject (Admin only)"""
        try:
            user_id = get_jwt_identity()
            current_user = User.query.get(int(user_id))

            # Check admin privileges
            if not current_user or not current_user.is_admin:
                return error_response("Admin privileges required to delete subjects", 403)

            subject = ExamCategorySubject.query.get(subject_id)
            if not subject:
                return error_response("Subject not found", 404)

            subject_name = subject.subject_name
            course_name = subject.exam_category.course_name
            db.session.delete(subject)
            db.session.commit()

            return success_response({
                'deleted_subject_id': subject_id,
                'deleted_subject_name': subject_name,
                'course_name': course_name
            }, "Subject deleted successfully")

        except Exception as e:
            db.session.rollback()
            return error_response(f"Failed to delete subject: {str(e)}", 500)

    return app


if __name__ == '__main__':
    print("🚀 Starting Jishu Backend - Complete Educational Platform API")
    print("📍 Server running on: http://localhost:5000")
    print("🔗 Health check: http://localhost:5000/health")
    print("📚 Available endpoints:")
    print("   🔐 Authentication & User Flow:")
    print("     • POST /api/auth/register - Register with email + OTP + name + mobile")
    print("     • POST /api/auth/login - Login with email + OTP")
    print("     • POST /api/auth/logout - Logout and blacklist token")
    print("     • POST /api/auth/otp/request - Request email OTP")
    print("     • GET /api/auth/profile - Get user profile")
    print("     • PUT /api/auth/profile/edit - Edit own profile")
    print("     • DELETE /api/auth/soft_delete - Soft delete own account")
    print("   📚 Course & Subject Management:")
    print("     • GET /api/courses - List all courses (public)")
    print("     • GET /api/courses/<id> - View course by ID (public)")
    print("     • GET /api/subjects?course_id=<id> - Get subjects for course (public)")
    print("     • GET /api/bundles?course_id=<id> - Get bundles for course (public)")
    print("     • POST /api/admin/courses - Add new course (admin)")
    print("     • PUT /api/admin/courses/<id> - Edit course (admin)")
    print("     • DELETE /api/admin/courses/<id> - Delete course (admin)")
    print("     • POST /api/admin/subjects - Add subject to course (admin)")
    print("     • PUT /api/admin/subjects/<id> - Edit subject (admin)")
    print("     • DELETE /api/admin/subjects/<id> - Delete subject (admin)")
    print("   💬 Community Blog:")
    print("     • GET /api/community/posts - List all posts (public)")
    print("     • POST /api/community/posts - Create new post")
    print("     • POST /api/community/posts/<id>/like - Like a post")
    print("     • POST /api/community/posts/<id>/comment - Add comment")
    print("     • DELETE /api/community/comments/<id> - Delete own comment")
    print("     • DELETE /api/community/posts/<id> - Delete own post")
    print("   👑 Admin Moderation:")
    print("     • PUT /api/admin/posts/<id> - Edit any post")
    print("     • DELETE /api/admin/posts/<id> - Delete any post")
    print("     • PUT /api/admin/comments/<id> - Edit any comment")
    print("     • DELETE /api/admin/comments/<id> - Delete any comment")

    print("   📝 Question Management:")
    print("     • GET /api/questions - List questions with filtering")
    print("     • GET /api/questions/<id> - Get specific question")
    print("     • POST /api/admin/questions - Create question manually (admin)")
    print("     • PUT /api/admin/questions/<id> - Update question (admin)")
    print("     • DELETE /api/admin/questions/<id> - Delete question (admin)")
    print("     • POST /api/admin/questions/bulk-delete - Bulk delete questions (admin)")
    print("   👥 Admin User Management:")
    print("     • GET /api/admin/users - List all users")
    print("     • PUT /api/admin/users/<id>/deactivate - Deactivate user")
    print("     • GET /api/admin/users/<id>/purchases - Get user purchases")
    print("     • GET /api/admin/users/<id>/chat_tokens - Get user AI usage")
    print("   🔍 Legacy Google OAuth (for compatibility):")
    print("     • GET /auth/google - Redirect to Google OAuth")
    print("     • GET /auth/google/callback - Handle Google OAuth callback")
    print("=" * 70)
    print("🎯 Ready to handle requests!")
    print("📝 Note: Most endpoints require JWT authentication")
    print("🔑 Admin endpoints require admin privileges")

    # Create the Flask application instance
    app = create_app()

    # Create database tables (commented out - tables already created)
    # with app.app_context():
    #     db.create_all()

    # Initialize three-layer RAG system at startup
    if app.config.get('RAG_AUTO_INITIALIZE', False):
        try:
            print("🚀 Initializing three-layer RAG system at startup...")

            # Layer 1: Initialize Model Service (pre-load models)
            from shared.services.model_service import get_model_service
            print("🔧 Layer 1: Initializing Model Service...")
            model_service = get_model_service()
            model_status = model_service.get_status()

            if model_status['status'] == 'ready':
                print("✅ Layer 1: Model Service initialized successfully")
            else:
                print(f"⚠️ Layer 1: Model Service status: {model_status['status']}")

            # Layer 2: Initialize Vector Index Service (index PDFs if needed)
            from shared.services.vector_index_service import VectorIndexService
            print("🔧 Layer 2: Checking Vector Index Service...")
            vector_service = VectorIndexService()

            # Check if indexing is needed
            indexing_status = vector_service.get_indexing_status()
            if indexing_status['needs_indexing']:
                print("🔄 Layer 2: Indexing PDFs...")
                index_result = vector_service.index_all_subjects()
                if index_result['success']:
                    print(f"✅ Layer 2: Indexed {index_result['total_subjects']} subjects successfully")
                else:
                    print(f"⚠️ Layer 2: Indexing completed with some failures")
            else:
                print("✅ Layer 2: All subjects already indexed")

            # Layer 3: Initialize RAG Query Service
            from shared.services.rag_service import get_rag_service
            print("🔧 Layer 3: Initializing RAG Query Service...")
            rag_service = get_rag_service(
                ollama_model=app.config.get('RAG_OLLAMA_MODEL', 'llama3.2:1b'),
                top_k_results=app.config.get('RAG_TOP_K_RESULTS', 5),
                similarity_threshold=app.config.get('RAG_SIMILARITY_THRESHOLD', 0.01)
            )

            rag_status = rag_service.get_status()
            print("✅ Layer 3: RAG Query Service initialized successfully")
            print("🎉 Three-layer RAG system ready for production!")

        except Exception as e:
            print(f"❌ Error initializing RAG system: {str(e)}")
            print("⚠️ Application will continue without RAG initialization")
    else:
        print("ℹ️ RAG auto-initialization disabled. Use /api/rag/initialize to initialize manually.")

    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True
    )
