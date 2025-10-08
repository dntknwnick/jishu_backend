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
from shared.utils.validators import validate_email_format, validate_mobile_number, validate_name
from shared.utils.response_helper import success_response, error_response, validation_error_response
from shared.utils.email_service import email_service
from shared.utils.google_oauth import create_google_oauth_service
from config import config

def create_app(config_name='development'):
    app = Flask(__name__)
    app.config.from_object(config[config_name])

    # Initialize extensions
    db.init_app(app)
    jwt = JWTManager(app)
    CORS(app, origins=app.config['CORS_ORIGINS'])

    # Initialize Google OAuth service
    google_oauth = create_google_oauth_service(app.config)

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
    @app.route('/send-otp', methods=['POST'])
    def send_otp():
        """Send OTP to email for registration or login"""
        try:
            data = request.get_json()
            email_id = data.get('email_id')
            action = data.get('action', 'login')  # 'register' or 'login'

            if not email_id:
                return error_response("Email ID is required", 400)

            if not validate_email_format(email_id):
                return error_response("Invalid email format", 400)

            user = User.query.filter_by(email_id=email_id).first()

            if action == 'register':
                if user:
                    return error_response("User with this email already exists", 409)
                # For registration, we'll create a temporary user record
                # This will be completed when OTP is verified
                return success_response({
                    'email_id': email_id,
                    'action': 'register',
                    'message': 'Please provide additional details for registration'
                }, "Ready for registration")

            elif action == 'login':
                if not user:
                    return error_response("User with this email does not exist", 404)

                if user.status != 'active':
                    return error_response("Account is not active", 403)

                # Generate and send OTP
                otp = user.generate_otp()
                db.session.commit()

                # Send OTP email
                success, message = email_service.send_otp_email(email_id, otp, user.name)
                if not success:
                    return error_response(f"Failed to send OTP: {message}", 500)

                return success_response({
                    'email_id': email_id,
                    'action': 'login',
                    'otp_sent': True
                }, "OTP sent to your email")

            else:
                return error_response("Invalid action. Must be 'register' or 'login'", 400)

        except Exception as e:
            db.session.rollback()
            return error_response(f"Failed to send OTP: {str(e)}", 500)

    @app.route('/register', methods=['POST'])
    def register():
        """Create user and send registration OTP"""
        try:
            data = request.get_json()

            if not data:
                return error_response("No JSON data provided", 400)

            required_fields = ['email_id', 'name', 'mobile_no']
            errors = {}

            for field in required_fields:
                if not data.get(field):
                    errors[field] = f"{field.replace('_', ' ').title()} is required"

            if errors:
                return validation_error_response(errors)

            # Validate input formats
            if not validate_email_format(data['email_id']):
                errors['email_id'] = "Invalid email format"
            if not validate_mobile_number(data['mobile_no']):
                errors['mobile_no'] = "Invalid mobile number format"
            is_valid_name, name_message = validate_name(data['name'])
            if not is_valid_name:
                errors['name'] = name_message

            if errors:
                return validation_error_response(errors)

            # Check if user already exists
            existing_user = User.query.filter_by(email_id=data['email_id']).first()
            if existing_user:
                return error_response("User with this email already exists", 409)

            # Create new user
            user = User(
                email_id=data['email_id'],
                name=data['name'].strip(),
                mobile_no=data['mobile_no'],
                source='email',
                auth_provider='manual',
                status='active'
            )

            # Generate OTP for verification
            otp = user.generate_otp()
            db.session.add(user)
            db.session.commit()

            # Send OTP email
            success, message = email_service.send_otp_email(data['email_id'], otp, user.name)
            if not success:
                db.session.rollback()
                return error_response(f"Failed to send OTP: {message}", 500)

            return success_response({
                'email_id': data['email_id'],
                'otp_sent': True,
                'message': 'Registration initiated. Please verify OTP sent to your email.'
            }, "Registration OTP sent", 201)

        except Exception as e:
            db.session.rollback()
            return error_response(f"Registration failed: {str(e)}", 500)
    @app.route('/verify-otp', methods=['POST'])
    def verify_otp():
        """Verify OTP for registration completion or login"""
        try:
            data = request.get_json()
            email_id = data.get('email_id')
            otp = data.get('otp')
            action = data.get('action', 'login')  # 'register' or 'login'

            if not email_id or not otp:
                return error_response("Email ID and OTP are required", 400)

            user = User.query.filter_by(email_id=email_id).first()
            if not user:
                return error_response("User not found", 404)

            # Verify OTP
            is_valid, message = user.verify_otp(otp)
            if not is_valid:
                return error_response(message, 400)

            # Update user status and login time
            user.last_login = datetime.utcnow()
            user.status = 'active'

            # Generate JWT tokens
            access_token = create_access_token(identity=user.id)
            refresh_token = create_refresh_token(identity=user.id)

            # Store refresh token in database
            refresh_expires_at = datetime.utcnow() + timedelta(seconds=app.config['JWT_REFRESH_TOKEN_EXPIRES'])
            user.set_refresh_token(refresh_token, refresh_expires_at)

            db.session.commit()

            # Send welcome email for new registrations
            if action == 'register':
                email_service.send_welcome_email(email_id, user.name)
                message = "Registration completed successfully"
            else:
                message = "Login successful"

            return success_response({
                'user': user.to_dict(),
                'access_token': access_token,
                'refresh_token': refresh_token
            }, message)

        except Exception as e:
            db.session.rollback()
            return error_response(f"OTP verification failed: {str(e)}", 500)

    @app.route('/login', methods=['POST'])
    def login():
        """Initiate login by sending OTP to email"""
        try:
            data = request.get_json()
            email_id = data.get('email_id')

            if not email_id:
                return error_response("Email ID is required", 400)

            if not validate_email_format(email_id):
                return error_response("Invalid email format", 400)

            user = User.query.filter_by(email_id=email_id).first()
            if not user:
                return error_response("User with this email does not exist", 404)

            if user.status != 'active':
                return error_response("Account is not active", 403)

            # Generate and send OTP
            otp = user.generate_otp()
            db.session.commit()

            # Send OTP email
            success, message = email_service.send_otp_email(email_id, otp, user.name)
            if not success:
                return error_response(f"Failed to send OTP: {message}", 500)

            return success_response({
                'email_id': email_id,
                'otp_sent': True,
                'message': 'OTP sent to your email. Please verify to complete login.'
            }, "Login OTP sent")

        except Exception as e:
            db.session.rollback()
            return error_response(f"Login failed: {str(e)}", 500)

    @app.route('/verify-token', methods=['POST'])
    @jwt_required()
    def verify_token():
        try:
            user_id = get_jwt_identity()
            user = User.query.get(user_id)
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
            user = User.query.get(user_id)
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
            new_access_token = create_access_token(identity=user.id)

            # Optionally generate new refresh token (rotate refresh tokens)
            new_refresh_token = create_refresh_token(identity=user.id)
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
            user = User.query.get(user_id)
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

    # --- GOOGLE OAUTH ENDPOINTS ---
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
                access_token = create_access_token(identity=user.id)
                refresh_token = create_refresh_token(identity=user.id)

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
                access_token = create_access_token(identity=new_user.id)
                refresh_token = create_refresh_token(identity=new_user.id)

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

    # --- USER ENDPOINTS ---
    @app.route('/profile', methods=['GET'])
    @jwt_required()
    def get_profile():
        try:
            user_id = get_jwt_identity()
            user = User.query.get(user_id)
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
            user = User.query.get(user_id)
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
            current_user = User.query.get(user_id)
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
            current_user = User.query.get(user_id)

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
            current_user = User.query.get(user_id)
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
            current_user = User.query.get(user_id)
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
            current_user = User.query.get(user_id)

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
            current_user = User.query.get(user_id)

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
            current_user = User.query.get(user_id)

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
            current_user = User.query.get(user_id)
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
            current_user = User.query.get(user_id)
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
            current_user = User.query.get(user_id)

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
            current_user = User.query.get(user_id)

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
    print("🚀 Starting Jishu Backend - OTP-Based Authentication API")
    print("📍 Server running on: http://localhost:5000")
    print("🔗 Health check: http://localhost:5000/health")
    print("📚 Available endpoints:")
    print("   🔐 Authentication (OTP-based):")
    print("     • POST /send-otp - Send OTP for registration/login")
    print("     • POST /register - Complete registration with OTP")
    print("     • POST /login - Initiate login (sends OTP)")
    print("     • POST /verify-otp - Verify OTP and complete login")
    print("     • POST /verify-token - Verify JWT token")
    print("     • POST /refresh-token - Refresh access token using refresh token")
    print("     • POST /logout - Logout and invalidate refresh token")
    print("   🔍 Google OAuth:")
    print("     • GET /auth/google - Redirect to Google OAuth")
    print("     • GET /auth/google/callback - Handle Google OAuth callback")
    print("   👤 User Management:")
    print("     • GET /profile - Get user profile")
    print("     • PUT /profile - Update user profile")
    print("   👑 Admin:")
    print("     • GET /users - Get all users (admin)")
    print("     • PUT /users/<id>/status - Update user status (admin)")
    print("   📚 Course Management (Admin):")
    print("     • POST /courses - Add new course")
    print("     • GET /courses - Get all courses")
    print("     • GET /courses/<id> - Get course by ID")
    print("     • PUT /courses/<id> - Update course")
    print("     • DELETE /courses/<id> - Delete course")
    print("   📖 Subject Management (Admin):")
    print("     • POST /courses/<id>/subjects - Add subject to course")
    print("     • GET /courses/<id>/subjects - Get course subjects")
    print("     • GET /subjects/<id> - Get subject by ID")
    print("     • PUT /subjects/<id> - Update subject")
    print("     • DELETE /subjects/<id> - Delete subject")
    print("=" * 60)

    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True
    )
