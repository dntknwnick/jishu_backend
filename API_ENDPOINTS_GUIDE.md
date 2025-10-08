# 🚀 Jishu Backend - API Endpoints Guide

## 📋 Overview

**Base URL**: `http://localhost:5000`

**Authentication Methods**:
- 🔐 **Email + OTP** (Manual Registration)
- 🔍 **Google OAuth** (One-click Registration/Login)

---

## 🔄 User Flow 1: Manual Registration with Email + OTP

### Step 1: Register New User

**Endpoint**: `POST /register`

**Request Body**:
```json
{
  "email_id": "john@example.com",
  "name": "John Doe",
  "mobile_no": "9876543210"
}
```

**Response**:
```json
{
  "success": true,
  "message": "Registration OTP sent",
  "data": {
    "email_id": "john@example.com",
    "otp_sent": true,
    "message": "Registration initiated. Please verify OTP sent to your email."
  }
}
```

### Step 2: Verify OTP to Complete Registration

**Endpoint**: `POST /verify-otp`

**Request Body**:
```json
{
  "email_id": "john@example.com",
  "otp": "123456",
  "action": "register"
}
```

**Response**:
```json
{
  "success": true,
  "message": "Registration successful",
  "data": {
    "user": {
      "id": 1,
      "name": "John Doe",
      "email_id": "john@example.com",
      "mobile_no": "9876543210",
      "is_premium": false,
      "is_admin": false,
      "color_theme": "light",
      "otp_verified": true,
      "auth_provider": "manual",
      "status": "active",
      "source": "email"
    },
    "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
  }
}
```

---

## 🔄 User Flow 2: Login for Existing Users

### Step 1: Send Login OTP

**Endpoint**: `POST /login`

**Request Body**:
```json
{
  "email_id": "john@example.com"
}
```

**Response**:
```json
{
  "success": true,
  "message": "Login OTP sent",
  "data": {
    "email_id": "john@example.com",
    "otp_sent": true,
    "message": "OTP sent to your email. Please verify to complete login."
  }
}
```

### Step 2: Verify OTP to Complete Login

**Endpoint**: `POST /verify-otp`

**Request Body**:
```json
{
  "email_id": "john@example.com",
  "otp": "654321",
  "action": "login"
}
```

**Response**:
```json
{
  "success": true,
  "message": "Login successful",
  "data": {
    "user": {
      "id": 1,
      "name": "John Doe",
      "email_id": "john@example.com",
      "mobile_no": "9876543210",
      "is_premium": false,
      "is_admin": false,
      "color_theme": "light",
      "otp_verified": true,
      "auth_provider": "manual",
      "last_login": "2024-01-15T10:30:00",
      "status": "active",
      "source": "email"
    },
    "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
  }
}
```

---

## 🔄 User Flow 3: Google OAuth Registration/Login

### Step 1: Get Google Authorization URL

**Endpoint**: `GET /auth/google`

**Response**:
```json
{
  "success": true,
  "message": "Google authorization URL generated",
  "data": {
    "authorization_url": "https://accounts.google.com/o/oauth2/auth?response_type=code&client_id=123456789.apps.googleusercontent.com&redirect_uri=http%3A%2F%2Flocalhost%3A5000%2Fauth%2Fgoogle%2Fcallback&scope=openid+email+profile&state=random_state_string"
  }
}
```

**Frontend Action**: Redirect user to the `authorization_url`

### Step 2: Google Handles Authentication

User logs in with Google → Google redirects back to your callback URL

### Step 3: Automatic Registration/Login

**Endpoint**: `GET /auth/google/callback` (Handled automatically)

**Response for New User**:
```json
{
  "success": true,
  "message": "Registration and login successful with Google",
  "data": {
    "user": {
      "id": 2,
      "name": "Jane Smith",
      "email_id": "jane@gmail.com",
      "mobile_no": "",
      "is_premium": false,
      "is_admin": false,
      "color_theme": "light",
      "otp_verified": true,
      "google_id": "1234567890123456789",
      "auth_provider": "google",
      "status": "active",
      "source": "google"
    },
    "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
  }
}
```

**Response for Existing User**:
```json
{
  "success": true,
  "message": "Login successful with Google",
  "data": {
    "user": {
      "id": 2,
      "name": "Jane Smith",
      "email_id": "jane@gmail.com",
      "mobile_no": "",
      "is_premium": false,
      "is_admin": false,
      "color_theme": "light",
      "otp_verified": true,
      "google_id": "1234567890123456789",
      "auth_provider": "google",
      "last_login": "2024-01-15T11:00:00",
      "status": "active",
      "source": "google"
    },
    "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
  }
}
```

---

## � Protected Endpoints (Require JWT Token)

### Get User Profile

**Endpoint**: `GET /profile`

**Headers**:
```
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...
```

**Response**:
```json
{
  "success": true,
  "message": "Profile retrieved successfully",
  "data": {
    "user": {
      "id": 1,
      "name": "John Doe",
      "email_id": "john@example.com",
      "mobile_no": "9876543210",
      "is_premium": false,
      "is_admin": false,
      "color_theme": "light",
      "otp_verified": true,
      "auth_provider": "manual",
      "status": "active",
      "source": "email"
    }
  }
}
```

### Update User Profile

**Endpoint**: `PUT /profile`

**Headers**:
```
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...
```

**Request Body**:
```json
{
  "name": "John Smith",
  "mobile_no": "9123456789",
  "color_theme": "dark"
}
```

**Response**:
```json
{
  "success": true,
  "message": "Profile updated successfully",
  "data": {
    "user": {
      "id": 1,
      "name": "John Smith",
      "email_id": "john@example.com",
      "mobile_no": "9123456789",
      "is_premium": false,
      "is_admin": false,
      "color_theme": "dark",
      "otp_verified": true,
      "auth_provider": "manual",
      "updated_at": "2024-01-15T12:00:00",
      "status": "active",
      "source": "email"
    }
  }
}
```

### Refresh Access Token

**Endpoint**: `POST /refresh-token`

**Headers**:
```
Authorization: Bearer REFRESH_TOKEN_HERE
```

**Response**:
```json
{
  "success": true,
  "message": "Tokens refreshed successfully",
  "data": {
    "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "user": {
      "id": 1,
      "name": "John Doe",
      "email_id": "john@example.com",
      "mobile_no": "9876543210",
      "is_premium": false,
      "is_admin": false,
      "color_theme": "light",
      "otp_verified": true,
      "auth_provider": "manual",
      "status": "active",
      "source": "email"
    }
  }
}
```

### Logout User

**Endpoint**: `POST /logout`

**Headers**:
```
Authorization: Bearer ACCESS_TOKEN_HERE
```

**Response**:
```json
{
  "success": true,
  "message": "Logout successful",
  "data": {
    "message": "Logged out successfully"
  }
}
```

---

## � Common Error Responses

### Validation Errors
```json
{
  "success": false,
  "message": "Validation failed",
  "errors": {
    "email_id": "Invalid email format",
    "mobile_no": "Mobile number must be 10 digits and start with 6-9",
    "name": "Name must be at least 2 characters long"
  }
}
```

### Authentication Errors
```json
{
  "success": false,
  "message": "Invalid or expired token"
}
```

### OTP Errors
```json
{
  "success": false,
  "message": "Invalid OTP"
}
```

```json
{
  "success": false,
  "message": "OTP has expired"
}
```

### User Not Found
```json
{
  "success": false,
  "message": "User with this email does not exist"
}
```

### Email Already Exists
```json
{
  "success": false,
  "message": "User with this email already exists"
}
```

---

## 📚 Course Management Endpoints (Admin Only)

### Add New Course

**Endpoint**: `POST /courses`

**Headers**:
```
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...
Content-Type: application/json
```

**Request Body**:
```json
{
  "course_name": "UPSC Civil Services",
  "description": "Comprehensive course for UPSC Civil Services examination preparation"
}
```

**Response**:
```json
{
  "success": true,
  "message": "Course added successfully",
  "data": {
    "course": {
      "id": 1,
      "course_name": "UPSC Civil Services",
      "description": "Comprehensive course for UPSC Civil Services examination preparation",
      "created_at": "2024-01-15T10:30:00",
      "updated_at": "2024-01-15T10:30:00",
      "subjects_count": 0
    }
  }
}
```

### Get All Courses

**Endpoint**: `GET /courses`

**Headers**:
```
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...
```

**Query Parameters**:
- `page` (optional): Page number (default: 1)
- `per_page` (optional): Items per page (default: 10)
- `include_subjects` (optional): Include subjects in response (default: false)
- `search` (optional): Search courses by name

**Response**:
```json
{
  "success": true,
  "message": "Courses retrieved successfully",
  "data": {
    "courses": [
      {
        "id": 1,
        "course_name": "UPSC Civil Services",
        "description": "Comprehensive course for UPSC Civil Services examination preparation",
        "created_at": "2024-01-15T10:30:00",
        "updated_at": "2024-01-15T10:30:00",
        "subjects_count": 3
      }
    ],
    "pagination": {
      "page": 1,
      "pages": 1,
      "per_page": 10,
      "total": 1,
      "has_next": false,
      "has_prev": false
    }
  }
}
```

### Get Course by ID

**Endpoint**: `GET /courses/{course_id}`

**Headers**:
```
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...
```

**Query Parameters**:
- `include_subjects` (optional): Include subjects in response (default: true)

**Response**:
```json
{
  "success": true,
  "message": "Course retrieved successfully",
  "data": {
    "course": {
      "id": 1,
      "course_name": "UPSC Civil Services",
      "description": "Comprehensive course for UPSC Civil Services examination preparation",
      "created_at": "2024-01-15T10:30:00",
      "updated_at": "2024-01-15T10:30:00",
      "subjects_count": 3,
      "subjects": [
        {
          "id": 1,
          "exam_category_id": 1,
          "subject_name": "General Studies Paper 1",
          "created_at": "2024-01-15T10:35:00",
          "updated_at": "2024-01-15T10:35:00"
        }
      ]
    }
  }
}
```

### Update Course

**Endpoint**: `PUT /courses/{course_id}`

**Headers**:
```
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...
Content-Type: application/json
```

**Request Body**:
```json
{
  "course_name": "UPSC Civil Services - Updated",
  "description": "Updated comprehensive course for UPSC Civil Services examination preparation"
}
```

### Delete Course

**Endpoint**: `DELETE /courses/{course_id}`

**Headers**:
```
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...
```

**Response**:
```json
{
  "success": true,
  "message": "Course deleted successfully",
  "data": {
    "deleted_course_id": 1,
    "deleted_course_name": "UPSC Civil Services"
  }
}
```

---

## 📖 Subject Management Endpoints (Admin Only)

### Add Subject to Course

**Endpoint**: `POST /courses/{course_id}/subjects`

**Headers**:
```
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...
Content-Type: application/json
```

**Request Body**:
```json
{
  "subject_name": "General Studies Paper 1"
}
```

**Response**:
```json
{
  "success": true,
  "message": "Subject added to course successfully",
  "data": {
    "subject": {
      "id": 1,
      "exam_category_id": 1,
      "subject_name": "General Studies Paper 1",
      "created_at": "2024-01-15T10:35:00",
      "updated_at": "2024-01-15T10:35:00"
    },
    "course": {
      "id": 1,
      "course_name": "UPSC Civil Services",
      "description": "Comprehensive course for UPSC Civil Services examination preparation",
      "created_at": "2024-01-15T10:30:00",
      "updated_at": "2024-01-15T10:30:00",
      "subjects_count": 1
    }
  }
}
```

### Get Course Subjects

**Endpoint**: `GET /courses/{course_id}/subjects`

**Headers**:
```
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...
```

**Query Parameters**:
- `page` (optional): Page number (default: 1)
- `per_page` (optional): Items per page (default: 20)
- `search` (optional): Search subjects by name

**Response**:
```json
{
  "success": true,
  "message": "Course subjects retrieved successfully",
  "data": {
    "course": {
      "id": 1,
      "course_name": "UPSC Civil Services",
      "description": "Comprehensive course for UPSC Civil Services examination preparation",
      "created_at": "2024-01-15T10:30:00",
      "updated_at": "2024-01-15T10:30:00",
      "subjects_count": 3
    },
    "subjects": [
      {
        "id": 1,
        "exam_category_id": 1,
        "subject_name": "General Studies Paper 1",
        "created_at": "2024-01-15T10:35:00",
        "updated_at": "2024-01-15T10:35:00"
      }
    ],
    "pagination": {
      "page": 1,
      "pages": 1,
      "per_page": 20,
      "total": 3,
      "has_next": false,
      "has_prev": false
    }
  }
}
```

### Get Subject by ID

**Endpoint**: `GET /subjects/{subject_id}`

**Headers**:
```
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...
```

### Update Subject

**Endpoint**: `PUT /subjects/{subject_id}`

**Headers**:
```
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...
Content-Type: application/json
```

**Request Body**:
```json
{
  "subject_name": "General Studies Paper 1 - Updated"
}
```

### Delete Subject

**Endpoint**: `DELETE /subjects/{subject_id}`

**Headers**:
```
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...
```

**Response**:
```json
{
  "success": true,
  "message": "Subject deleted successfully",
  "data": {
    "deleted_subject_id": 1,
    "deleted_subject_name": "General Studies Paper 1",
    "course_name": "UPSC Civil Services"
  }
}
```

---

## ⚠️ Error Responses

### Admin Privilege Required

**Status Code**: `403 Forbidden`

**Response**:
```json
{
  "success": false,
  "message": "Admin privileges required to add courses",
  "error": "Forbidden"
}
```

### Course/Subject Not Found

**Status Code**: `404 Not Found`

**Response**:
```json
{
  "success": false,
  "message": "Course not found",
  "error": "Not Found"
}
```

### Duplicate Course/Subject

**Status Code**: `409 Conflict`

**Response**:
```json
{
  "success": false,
  "message": "Course with this name already exists",
  "error": "Conflict"
}
```

---

## 🧪 Complete Testing Examples

### Manual Registration Flow
```bash
# Step 1: Register
curl -X POST http://localhost:5000/register \
  -H "Content-Type: application/json" \
  -d '{
    "email_id": "test@example.com",
    "name": "Test User",
    "mobile_no": "9876543210"
  }'

# Step 2: Check email for OTP, then verify
curl -X POST http://localhost:5000/verify-otp \
  -H "Content-Type: application/json" \
  -d '{
    "email_id": "test@example.com",
    "otp": "123456",
    "action": "register"
  }'
```

### Login Flow
```bash
# Step 1: Send login OTP
curl -X POST http://localhost:5000/login \
  -H "Content-Type: application/json" \
  -d '{
    "email_id": "test@example.com"
  }'

# Step 2: Verify OTP
curl -X POST http://localhost:5000/verify-otp \
  -H "Content-Type: application/json" \
  -d '{
    "email_id": "test@example.com",
    "otp": "654321",
    "action": "login"
  }'
```

### Google OAuth Flow
```bash
# Step 1: Get authorization URL
curl -X GET http://localhost:5000/auth/google

# Step 2: User visits URL in browser and logs in with Google
# Step 3: Google redirects back automatically with JWT token
```

### Using JWT Token
```bash
# Get profile
curl -X GET http://localhost:5000/profile \
  -H "Authorization: Bearer YOUR_JWT_TOKEN_HERE"

# Update profile
curl -X PUT http://localhost:5000/profile \
  -H "Authorization: Bearer YOUR_JWT_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Updated Name",
    "color_theme": "dark"
  }'
```

### Course Management (Admin Only)
```bash
# Add a new course
curl -X POST http://localhost:5000/courses \
  -H "Authorization: Bearer YOUR_ADMIN_JWT_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{
    "course_name": "UPSC Civil Services",
    "description": "Comprehensive course for UPSC Civil Services examination preparation"
  }'

# Get all courses
curl -X GET http://localhost:5000/courses \
  -H "Authorization: Bearer YOUR_JWT_TOKEN_HERE"

# Get course with subjects
curl -X GET "http://localhost:5000/courses/1?include_subjects=true" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN_HERE"

# Update course
curl -X PUT http://localhost:5000/courses/1 \
  -H "Authorization: Bearer YOUR_ADMIN_JWT_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{
    "course_name": "UPSC Civil Services - Updated",
    "description": "Updated comprehensive course description"
  }'

# Delete course
curl -X DELETE http://localhost:5000/courses/1 \
  -H "Authorization: Bearer YOUR_ADMIN_JWT_TOKEN_HERE"
```

### Subject Management (Admin Only)
```bash
# Add subject to course
curl -X POST http://localhost:5000/courses/1/subjects \
  -H "Authorization: Bearer YOUR_ADMIN_JWT_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{
    "subject_name": "General Studies Paper 1"
  }'

# Get course subjects
curl -X GET http://localhost:5000/courses/1/subjects \
  -H "Authorization: Bearer YOUR_JWT_TOKEN_HERE"

# Get specific subject
curl -X GET http://localhost:5000/subjects/1 \
  -H "Authorization: Bearer YOUR_JWT_TOKEN_HERE"

# Update subject
curl -X PUT http://localhost:5000/subjects/1 \
  -H "Authorization: Bearer YOUR_ADMIN_JWT_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{
    "subject_name": "General Studies Paper 1 - Updated"
  }'

# Delete subject
curl -X DELETE http://localhost:5000/subjects/1 \
  -H "Authorization: Bearer YOUR_ADMIN_JWT_TOKEN_HERE"
```

---

## 📝 Important Notes

- **OTP Expiry**: All OTPs expire after 10 minutes
- **JWT Access Token Expiry**: Access tokens expire after 1 hour
- **JWT Refresh Token Expiry**: Refresh tokens expire after 30 days
- **Token Refresh**: Use refresh token to get new access token without re-authentication
- **Logout**: Logout endpoint invalidates refresh token for security
- **Mobile Numbers**: Only Indian format (10 digits, starts with 6-9)
- **Email Delivery**: Check spam folder if OTP email not received
- **Google OAuth**: Requires Google Cloud Console setup
- **Development Mode**: OTPs printed to console if email not configured


