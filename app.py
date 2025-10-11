# Entry point for monolithic architecture
# Jishu Backend - Flask RESTful API

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'shared'))

from flask import Flask, request, jsonify
from flask_jwt_extended import JWTManager, jwt_required, get_jwt_identity, create_access_token, create_refresh_token, get_jwt
from flask_cors import CORS
from datetime import datetime, timedelta

from shared.models.user import db, User
from shared.models.course import ExamCategory, ExamCategorySubject
from shared.models.purchase import ExamCategoryPurchase, ExamCategoryQuestion, TestAttempt, TestAnswer
from shared.models.community import BlogPost, BlogLike, BlogComment, AIChatHistory, UserAIStats
from shared.utils.validators import validate_email_format, validate_mobile_number, validate_name
from shared.utils.response_helper import success_response, error_response, validation_error_response
from shared.utils.email_service import email_service
from shared.utils.google_oauth import create_google_oauth_service
from shared.utils.decorators import admin_required, user_required, get_current_user
from config import config
import secrets
import uuid

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
        """Login with email/OTP only (no password)"""
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

            # Verify OTP
            is_valid, message = user.verify_otp(otp)
            if not is_valid:
                return error_response(message, 400)

            # Update last login
            user.last_login = datetime.utcnow()

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
                'user': user.to_dict()
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
        """Request email OTP"""
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
                    status='inactive'  # Will be activated after OTP verification
                )
                db.session.add(user)

            # Generate and send OTP
            otp = user.generate_otp()
            db.session.commit()

            # Send OTP email
            success, message = email_service.send_otp_email(email_id, otp, user.name or 'User')
            if not success:
                return error_response(f"Failed to send OTP: {message}", 500)

            return success_response({
                'email': email_id,
                'otp_sent': True
            }, "OTP sent to your email")

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
                if not validate_name(name):
                    errors['name'] = 'Invalid name format'
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

            if errors:
                return validation_error_response(errors)

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
            if not course_id:
                return error_response("course_id parameter is required", 400)

            # Check if course exists
            course = ExamCategory.query.get(course_id)
            if not course:
                return error_response("Course not found", 404)

            page = request.args.get('page', 1, type=int)
            per_page = request.args.get('per_page', 10, type=int)

            # Get subjects for the course
            subjects = ExamCategorySubject.query.filter_by(exam_category_id=course_id).paginate(
                page=page, per_page=per_page, error_out=False
            )

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

            if not course_id or not subject_name:
                return error_response("course_id and subject_name are required", 400)

            # Check if course exists
            course = ExamCategory.query.get(course_id)
            if not course:
                return error_response("Course not found", 404)

            # Validation
            if len(subject_name.strip()) < 2:
                return error_response("Subject name must be at least 2 characters long", 400)

            # Validate pricing
            try:
                amount = float(amount) if amount else 0.00
                offer_amount = float(offer_amount) if offer_amount else 0.00
                max_tokens = int(max_tokens) if max_tokens else 100
            except (ValueError, TypeError):
                return error_response("Invalid pricing or token values", 400)

            if amount < 0 or offer_amount < 0 or max_tokens < 0:
                return error_response("Pricing and token values must be non-negative", 400)

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
                max_tokens=max_tokens
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
        """Delete subject (Admin only)"""
        try:
            subject = ExamCategorySubject.query.get(subject_id)
            if not subject:
                return error_response("Subject not found", 404)

            # Check if subject has any purchases
            purchases = ExamCategoryPurchase.query.filter_by(subject_id=subject_id).first()
            if purchases:
                return error_response("Cannot delete subject with existing purchases", 400)

            db.session.delete(subject)
            db.session.commit()

            return success_response({
                'message': 'Subject deleted successfully'
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

            return success_response({
                'posts': [post.to_dict(include_user=True) for post in posts.items],
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
        """Create a new post"""
        try:
            user = get_current_user()
            if not user:
                return error_response("User not found", 404)

            data = request.get_json()
            title = data.get('title', '').strip()
            content = data.get('content', '').strip()
            tags = data.get('tags', '').strip()

            # Validation
            if not title or len(title) < 5:
                return error_response("Title must be at least 5 characters long", 400)

            if not content or len(content) < 10:
                return error_response("Content must be at least 10 characters long", 400)

            # Create new post
            new_post = BlogPost(
                user_id=user.id,
                title=title,
                content=content,
                tags=tags if tags else None,
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
            if not content or len(content) < 3:
                return error_response("Comment must be at least 3 characters long", 400)

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

    # AI Token Limit Helper Functions
    def get_user_token_limits(user):
        """Get user's daily token limits based on purchases"""
        from shared.models.purchase import ExamCategoryPurchase

        # Default daily limit
        daily_limit = 50

        # Check if user has purchased any courses or subjects
        purchases = ExamCategoryPurchase.query.filter_by(user_id=user.id).all()

        max_tokens = daily_limit
        for purchase in purchases:
            if purchase.course_id and not purchase.subject_id:
                # Full course purchase
                course = ExamCategory.query.get(purchase.course_id)
                if course and course.max_tokens == 0:
                    return 0  # Unlimited tokens
                elif course and course.max_tokens > max_tokens:
                    max_tokens = course.max_tokens
            elif purchase.subject_id:
                # Subject purchase
                subject = ExamCategorySubject.query.get(purchase.subject_id)
                if subject and subject.max_tokens > max_tokens:
                    max_tokens = subject.max_tokens

        return max_tokens

    def check_daily_token_limit(user, tokens_needed=1):
        """Check if user has enough tokens for today"""
        today = datetime.utcnow().date()

        # Get today's token usage
        today_usage = db.session.query(db.func.sum(AIChatHistory.tokens_used)).filter(
            AIChatHistory.user_id == user.id,
            db.func.date(AIChatHistory.created_at) == today
        ).scalar() or 0

        # Get user's token limit
        token_limit = get_user_token_limits(user)

        # Unlimited tokens (0 means unlimited)
        if token_limit == 0:
            return True, token_limit, today_usage

        # Check if user has enough tokens
        if today_usage + tokens_needed <= token_limit:
            return True, token_limit, today_usage
        else:
            return False, token_limit, today_usage

    # AI Chatbot Endpoints
    @app.route('/api/ai/chat', methods=['POST'])
    @user_required
    def api_ai_chat():
        """Ask educational question to chatbot"""
        try:
            user = get_current_user()
            if not user:
                return error_response("User not found", 404)

            data = request.get_json()
            message = data.get('message', '').strip()
            context = data.get('context', '').strip()
            session_id = data.get('session_id', str(uuid.uuid4()))

            # Validation
            if not message or len(message) < 3:
                return error_response("Message must be at least 3 characters long", 400)

            # Check if message is academic (basic keyword filtering)
            academic_keywords = ['study', 'learn', 'exam', 'test', 'question', 'explain', 'what', 'how', 'why', 'define']
            is_academic = any(keyword in message.lower() for keyword in academic_keywords)

            if not is_academic:
                return error_response("Please ask only academic/educational questions", 400)

            # Estimate tokens needed (simple estimation)
            estimated_tokens = len(message.split()) + 50  # Estimate response tokens

            # Check token limits
            can_proceed, token_limit, tokens_used_today = check_daily_token_limit(user, estimated_tokens)
            if not can_proceed:
                return error_response(
                    f"Daily token limit exceeded. You have used {tokens_used_today}/{token_limit} tokens today. "
                    f"Purchase a course or subject to get more tokens.",
                    429
                )

            # TODO: Integrate with Ollama model here
            # For now, we'll return a placeholder response
            ai_response = f"This is a placeholder response for: {message}. Please integrate with your Ollama model."
            tokens_used = len(message.split()) + len(ai_response.split())  # Simple token estimation
            response_time = 1.5  # Placeholder response time

            # Save chat history
            chat_history = AIChatHistory(
                user_id=user.id,
                session_id=session_id,
                message=message,
                response=ai_response,
                tokens_used=tokens_used,
                response_time=response_time,
                is_academic=is_academic
            )
            db.session.add(chat_history)

            # Update user AI stats
            current_month = datetime.utcnow().strftime('%Y-%m')
            user_stats = UserAIStats.query.filter_by(user_id=user.id, month_year=current_month).first()

            if not user_stats:
                user_stats = UserAIStats(
                    user_id=user.id,
                    month_year=current_month,
                    total_queries=1,
                    total_tokens_used=tokens_used,
                    monthly_queries=1,
                    monthly_tokens_used=tokens_used,
                    last_query_date=datetime.utcnow()
                )
                db.session.add(user_stats)
            else:
                user_stats.total_queries += 1
                user_stats.total_tokens_used += tokens_used
                user_stats.monthly_queries += 1
                user_stats.monthly_tokens_used += tokens_used
                user_stats.last_query_date = datetime.utcnow()

            db.session.commit()

            # Get updated token usage
            _, token_limit, tokens_used_today = check_daily_token_limit(user, 0)

            return success_response({
                'response': ai_response,
                'tokens_used': tokens_used,
                'session_id': session_id,
                'token_info': {
                    'tokens_used_today': tokens_used_today + tokens_used,
                    'daily_limit': token_limit,
                    'remaining_tokens': max(0, token_limit - (tokens_used_today + tokens_used)) if token_limit > 0 else 'unlimited'
                }
            }, "AI response generated successfully")

        except Exception as e:
            db.session.rollback()
            return error_response(f"Failed to process AI chat: {str(e)}", 500)

    @app.route('/api/ai/token-status', methods=['GET'])
    @user_required
    def api_get_token_status():
        """Get user's current token usage and limits"""
        try:
            user = get_current_user()
            if not user:
                return error_response("User not found", 404)

            # Get token limits and usage
            _, token_limit, tokens_used_today = check_daily_token_limit(user, 0)

            return success_response({
                'tokens_used_today': tokens_used_today,
                'daily_limit': token_limit,
                'remaining_tokens': max(0, token_limit - tokens_used_today) if token_limit > 0 else 'unlimited',
                'is_unlimited': token_limit == 0
            }, "Token status retrieved successfully")

        except Exception as e:
            return error_response(f"Failed to get token status: {str(e)}", 500)

    # Purchase Endpoints
    @app.route('/api/purchases', methods=['POST'])
    @user_required
    def api_create_purchase():
        """Create a new purchase (Demo - no payment processing)"""
        try:
            user = get_current_user()
            if not user:
                return error_response("User not found", 404)

            data = request.get_json()
            course_id = data.get('course_id')
            subject_id = data.get('subject_id')
            payment_method = data.get('payment_method', 'demo')

            # Validation
            if not course_id:
                return error_response("Course ID is required", 400)

            # Check if course exists
            course = ExamCategory.query.get(course_id)
            if not course:
                return error_response("Course not found", 404)

            # Check if subject exists (if provided)
            subject = None
            if subject_id:
                subject = ExamCategorySubject.query.get(subject_id)
                if not subject or subject.exam_category_id != course_id:
                    return error_response("Subject not found or doesn't belong to this course", 404)

            # Calculate cost
            if subject:
                cost = subject.offer_amount if subject.offer_amount > 0 else subject.amount
            else:
                cost = course.offer_amount if course.offer_amount > 0 else course.amount

            # Check if user already purchased this item
            existing_purchase = ExamCategoryPurchase.query.filter_by(
                user_id=user.id,
                exam_category_id=course_id,
                subject_id=subject_id
            ).first()

            if existing_purchase:
                return error_response("You have already purchased this item", 409)

            # Create purchase record (demo - no actual payment processing)
            purchase = ExamCategoryPurchase(
                user_id=user.id,
                exam_category_id=course_id,
                subject_id=subject_id,
                cost=cost,
                no_of_attempts=3,
                attempts_used=0,
                status='active'
            )

            db.session.add(purchase)
            db.session.commit()

            return success_response({
                'purchase': purchase.to_dict(),
                'message': 'Purchase completed successfully! You now have access to the content.'
            }, "Purchase created successfully")

        except Exception as e:
            db.session.rollback()
            return error_response(f"Failed to create purchase: {str(e)}", 500)

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
            # Check if test user already exists
            existing_user = User.query.filter_by(email_id='testuser@jishu.com').first()
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
                name='Test Admin User',
                email_id='testuser@jishu.com',
                mobile_no='9999999999',
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

    # AI Question Generation Endpoints
    @app.route('/api/ai/generate-questions-from-text', methods=['POST'])
    @admin_required
    def api_generate_questions_from_text():
        """Generate MCQs from text content using AI (Admin only)"""
        try:
            from shared.services.ai_service import get_ai_service

            data = request.get_json()
            content = data.get('content', '').strip()
            num_questions = data.get('num_questions', app.config.get('AI_DEFAULT_QUESTIONS_COUNT', 5))
            subject_name = data.get('subject_name', '')
            difficulty = data.get('difficulty', 'medium')
            exam_category_id = data.get('exam_category_id')
            subject_id = data.get('subject_id')

            # Validation
            if not content or len(content) < 100:
                return error_response("Content must be at least 100 characters long", 400)

            if num_questions < 1 or num_questions > 20:
                return error_response("Number of questions must be between 1 and 20", 400)

            if difficulty not in ['easy', 'medium', 'hard']:
                return error_response("Difficulty must be 'easy', 'medium', or 'hard'", 400)

            # Validate exam category and subject if provided
            if exam_category_id:
                exam_category = ExamCategory.query.get(exam_category_id)
                if not exam_category:
                    return error_response("Exam category not found", 404)

            if subject_id:
                subject = ExamCategorySubject.query.get(subject_id)
                if not subject:
                    return error_response("Subject not found", 404)
                if not subject_name:
                    subject_name = subject.subject_name

            # Generate questions using AI service
            ai_service = get_ai_service(
                pdf_folder_path=app.config.get('AI_PDF_FOLDER'),
                ollama_model=app.config.get('AI_OLLAMA_MODEL', 'llama3.2:1b')
            )

            result = ai_service.generate_mcq_from_text(
                content=content,
                num_questions=num_questions,
                subject_name=subject_name,
                difficulty=difficulty
            )

            if not result['success']:
                return error_response(result['error'], 500)

            # Optionally save questions to database
            save_to_db = data.get('save_to_database', False)
            saved_questions = []

            if save_to_db and exam_category_id and subject_id:
                user = get_current_user()
                for q_data in result['questions']:
                    question = ExamCategoryQuestion(
                        exam_category_id=exam_category_id,
                        subject_id=subject_id,
                        question=q_data['question'],
                        option_1=q_data['option_a'],
                        option_2=q_data['option_b'],
                        option_3=q_data['option_c'],
                        option_4=q_data['option_d'],
                        correct_answer=q_data['option_a'] if q_data['correct_option'] == 'A' else
                                     q_data['option_b'] if q_data['correct_option'] == 'B' else
                                     q_data['option_c'] if q_data['correct_option'] == 'C' else
                                     q_data['option_d'],
                        explanation=q_data.get('explanation', ''),
                        user_id=user.id,
                        is_ai_generated=True,
                        ai_model_used=result.get('model_used'),
                        difficulty_level=difficulty,
                        source_content=content[:1000] if len(content) > 1000 else content  # Store first 1000 chars
                    )
                    db.session.add(question)
                    saved_questions.append(question)

                db.session.commit()

            response_data = {
                'questions': result['questions'],
                'total_generated': len(result['questions']),
                'model_used': result.get('model_used'),
                'subject_name': subject_name,
                'difficulty': difficulty
            }

            if saved_questions:
                response_data['saved_to_database'] = True
                response_data['saved_count'] = len(saved_questions)
                response_data['saved_question_ids'] = [q.id for q in saved_questions]

            return success_response(response_data, "Questions generated successfully")

        except Exception as e:
            db.session.rollback()
            return error_response(f"Failed to generate questions: {str(e)}", 500)

    @app.route('/api/ai/generate-questions-from-pdfs', methods=['POST'])
    @admin_required
    def api_generate_questions_from_pdfs():
        """Generate MCQs from PDF documents using AI (Admin only)"""
        try:
            from shared.services.ai_service import get_ai_service

            data = request.get_json() or {}
            num_questions = data.get('num_questions', app.config.get('AI_DEFAULT_QUESTIONS_COUNT', 5))
            subject_name = data.get('subject_name', '')
            difficulty = data.get('difficulty', 'medium')
            exam_category_id = data.get('exam_category_id')
            subject_id = data.get('subject_id')

            # Validation
            if num_questions < 1 or num_questions > 20:
                return error_response("Number of questions must be between 1 and 20", 400)

            if difficulty not in ['easy', 'medium', 'hard']:
                return error_response("Difficulty must be 'easy', 'medium', or 'hard'", 400)

            # Validate exam category and subject if provided
            if exam_category_id:
                exam_category = ExamCategory.query.get(exam_category_id)
                if not exam_category:
                    return error_response("Exam category not found", 404)

            if subject_id:
                subject = ExamCategorySubject.query.get(subject_id)
                if not subject:
                    return error_response("Subject not found", 404)
                if not subject_name:
                    subject_name = subject.subject_name

            # Generate questions using AI service
            ai_service = get_ai_service(
                pdf_folder_path=app.config.get('AI_PDF_FOLDER'),
                ollama_model=app.config.get('AI_OLLAMA_MODEL', 'llama3.2:1b')
            )

            result = ai_service.generate_mcq_from_pdfs(
                num_questions=num_questions,
                subject_name=subject_name,
                difficulty=difficulty
            )

            if not result['success']:
                return error_response(result['error'], 500)

            # Optionally save questions to database
            save_to_db = data.get('save_to_database', False)
            saved_questions = []

            if save_to_db and exam_category_id and subject_id:
                user = get_current_user()
                sources_text = ', '.join(result.get('sources_used', []))
                for q_data in result['questions']:
                    question = ExamCategoryQuestion(
                        exam_category_id=exam_category_id,
                        subject_id=subject_id,
                        question=q_data['question'],
                        option_1=q_data['option_a'],
                        option_2=q_data['option_b'],
                        option_3=q_data['option_c'],
                        option_4=q_data['option_d'],
                        correct_answer=q_data['option_a'] if q_data['correct_option'] == 'A' else
                                     q_data['option_b'] if q_data['correct_option'] == 'B' else
                                     q_data['option_c'] if q_data['correct_option'] == 'C' else
                                     q_data['option_d'],
                        explanation=q_data.get('explanation', ''),
                        user_id=user.id,
                        is_ai_generated=True,
                        ai_model_used=result.get('model_used'),
                        difficulty_level=difficulty,
                        source_content=f"Generated from PDFs: {sources_text}"
                    )
                    db.session.add(question)
                    saved_questions.append(question)

                db.session.commit()

            response_data = {
                'questions': result['questions'],
                'total_generated': len(result['questions']),
                'sources_used': result.get('sources_used', []),
                'total_pdfs_processed': result.get('total_pdfs_processed', 0),
                'model_used': result.get('model_used'),
                'subject_name': subject_name,
                'difficulty': difficulty
            }

            if saved_questions:
                response_data['saved_to_database'] = True
                response_data['saved_count'] = len(saved_questions)
                response_data['saved_question_ids'] = [q.id for q in saved_questions]

            return success_response(response_data, "Questions generated from PDFs successfully")

        except Exception as e:
            db.session.rollback()
            return error_response(f"Failed to generate questions from PDFs: {str(e)}", 500)

    @app.route('/api/ai/rag/chat', methods=['POST'])
    @user_required
    def api_rag_chat():
        """RAG-based chat with PDF documents"""
        try:
            from shared.services.ai_service import get_ai_service

            user = get_current_user()
            if not user:
                return error_response("User not found", 404)

            data = request.get_json()
            query = data.get('query', '').strip()
            session_id = data.get('session_id', str(uuid.uuid4()))

            # Validation
            if not query or len(query) < 3:
                return error_response("Query must be at least 3 characters long", 400)

            # Initialize AI service
            ai_service = get_ai_service(
                pdf_folder_path=app.config.get('AI_PDF_FOLDER'),
                ollama_model=app.config.get('AI_OLLAMA_MODEL', 'llama3.2:1b')
            )

            # Generate RAG response
            result = ai_service.generate_rag_response(query)

            if not result['success']:
                return error_response(result['error'], 500)

            ai_response = result['response']
            tokens_used = len(query.split()) + len(ai_response.split())  # Simple token estimation
            response_time = 2.0  # Placeholder response time

            # Save chat history
            chat_history = AIChatHistory(
                user_id=user.id,
                session_id=session_id,
                message=query,
                response=ai_response,
                tokens_used=tokens_used,
                response_time=response_time,
                is_academic=True  # RAG responses are always academic
            )
            db.session.add(chat_history)

            # Update user AI stats
            current_month = datetime.utcnow().strftime('%Y-%m')
            user_stats = UserAIStats.query.filter_by(user_id=user.id, month_year=current_month).first()

            if not user_stats:
                user_stats = UserAIStats(
                    user_id=user.id,
                    month_year=current_month,
                    total_queries=1,
                    total_tokens_used=tokens_used,
                    monthly_queries=1,
                    monthly_tokens_used=tokens_used,
                    last_query_date=datetime.utcnow()
                )
                db.session.add(user_stats)
            else:
                user_stats.total_queries += 1
                user_stats.total_tokens_used += tokens_used
                user_stats.monthly_queries += 1
                user_stats.monthly_tokens_used += tokens_used
                user_stats.last_query_date = datetime.utcnow()

            db.session.commit()

            return success_response({
                'response': ai_response,
                'sources': result.get('sources', []),
                'relevant_docs': result.get('relevant_docs', 0),
                'tokens_used': tokens_used,
                'session_id': session_id,
                'model_used': result.get('model_used')
            }, "RAG response generated successfully")

        except Exception as e:
            db.session.rollback()
            return error_response(f"Failed to process RAG chat: {str(e)}", 500)

    @app.route('/api/ai/rag/status', methods=['GET'])
    def api_rag_status():
        """Check RAG system status and dependencies (Public endpoint)"""
        try:
            from shared.services.ai_service import get_ai_service

            ai_service = get_ai_service(
                pdf_folder_path=app.config.get('AI_PDF_FOLDER'),
                ollama_model=app.config.get('AI_OLLAMA_MODEL', 'llama3.2:1b')
            )

            status = ai_service.get_status()

            return success_response(status, "RAG status retrieved successfully")

        except Exception as e:
            return error_response(f"Failed to get RAG status: {str(e)}", 500)

    @app.route('/api/ai/rag/reload', methods=['POST'])
    @admin_required
    def api_rag_reload():
        """Reload RAG index from PDFs (Admin only)"""
        try:
            from shared.services.ai_service import get_ai_service

            ai_service = get_ai_service(
                pdf_folder_path=app.config.get('AI_PDF_FOLDER'),
                ollama_model=app.config.get('AI_OLLAMA_MODEL', 'llama3.2:1b')
            )

            result = ai_service.reload_index()

            if not result['success']:
                return error_response(result['error'], 500)

            return success_response({
                'message': result['message'],
                'pdfs_loaded': result['pdfs_loaded'],
                'sources': result['sources']
            }, "RAG index reloaded successfully")

        except Exception as e:
            return error_response(f"Failed to reload RAG index: {str(e)}", 500)

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

    @app.route('/api/auth/google/verify', methods=['POST'])
    def api_google_verify():
        """Verify Google OAuth authorization code from frontend"""
        try:
            if not google_oauth:
                return error_response("Google OAuth not configured", 503)

            data = request.get_json()
            authorization_code = data.get('code')

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
            return error_response(f"Google OAuth verification failed: {str(e)}", 500)

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
    def update_user_status():
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


# Create the Flask application instance
app = create_app()

# Create database tables
with app.app_context():
    db.create_all()

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
    print("   🤖 AI Chatbot & Question Generation:")
    print("     • POST /api/ai/chat - Ask educational question")
    print("     • POST /api/ai/rag/chat - RAG-based chat with PDF documents")
    print("     • POST /api/ai/generate-questions-from-text - Generate MCQs from text (admin)")
    print("     • POST /api/ai/generate-questions-from-pdfs - Generate MCQs from PDFs (admin)")
    print("     • GET /api/ai/rag/status - Check RAG system status")
    print("     • POST /api/ai/rag/reload - Reload RAG index (admin)")
    print("     • GET /api/admin/chat/tokens - Get all users' token stats (admin)")
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

    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True
    )
