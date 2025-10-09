# 🚀 Jishu Backend - Complete API Endpoints Documentation

## 📋 Overview

**Base URL**: `http://localhost:5000`

**Authentication Methods**:
- 🔐 **Email + OTP** (Manual Registration)
- 🔍 **Google OAuth** (One-click Registration/Login)
- 🎫 **JWT Tokens** (Access & Refresh tokens for protected routes)

**Content-Type**: `application/json` for all POST/PUT requests
**Authorization Header**: `Bearer <JWT_TOKEN>` for protected routes

---

## 🔐 Authentication & User Flow

### 1. Request OTP for Registration
**Endpoint**: `POST /api/auth/otp/request`
**Auth**: None
**Description**: Request OTP for email verification

**Request Body**:
```json
{
  "email": "user@example.com"
}
```

**Success Response (200)**:
```json
{
  "success": true,
  "message": "OTP sent successfully",
  "data": {
    "email": "user@example.com",
    "otp_sent": true,
    "expires_in": "10 minutes"
  }
}
```

### 2. Register New User
**Endpoint**: `POST /api/auth/register`
**Auth**: None
**Description**: Complete user registration with OTP verification

**Request Body**:
```json
{
  "email": "user@example.com",
  "otp": "123456",
  "password": "SecurePass123!",
  "name": "John Doe",
  "mobile_no": "9876543210"
}
```

**Success Response (201)**:
```json
{
  "success": true,
  "message": "Registration successful",
  "data": {
    "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "user": {
      "id": 1,
      "email_id": "user@example.com",
      "name": "John Doe",
      "mobile_no": "9876543210",
      "is_premium": false,
      "is_admin": false,
      "color_theme": "light",
      "status": "active",
      "created_at": "2024-01-15T10:30:00Z"
    }
  }
}
```

### 3. User Login
**Endpoint**: `POST /api/auth/login`
**Auth**: None
**Description**: Login with email/password or Google OAuth

**Request Body (Email/Password)**:
```json
{
  "email": "user@example.com",
  "password": "SecurePass123!"
}
```

**Request Body (Google OAuth)**:
```json
{
  "email": "user@example.com",
  "oauth_token": "google_oauth_token_here"
}
```

**Success Response (200)**:
```json
{
  "success": true,
  "message": "Login successful",
  "data": {
    "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "user": {
      "id": 1,
      "email_id": "user@example.com",
      "name": "John Doe",
      "is_premium": false,
      "is_admin": false,
      "last_login": "2024-01-15T10:30:00Z"
    }
  }
}
```

### 4. Get User Profile
**Endpoint**: `GET /api/auth/profile`
**Auth**: Bearer Token (User)
**Description**: Get current user's profile information

**Headers**:
```
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...
```

**Success Response (200)**:
```json
{
  "success": true,
  "message": "Profile retrieved successfully",
  "data": {
    "user": {
      "id": 1,
      "email_id": "user@example.com",
      "name": "John Doe",
      "mobile_no": "9876543210",
      "is_premium": false,
      "is_admin": false,
      "color_theme": "light",
      "status": "active",
      "created_at": "2024-01-15T10:30:00Z",
      "updated_at": "2024-01-15T10:30:00Z"
    }
  }
}
```

### 5. Edit User Profile
**Endpoint**: `PUT /api/auth/profile/edit`
**Auth**: Bearer Token (User)
**Description**: Update user profile information

**Request Body**:
```json
{
  "name": "John Smith",
  "mobile_no": "9876543211",
  "color_theme": "dark"
}
```

**Success Response (200)**:
```json
{
  "success": true,
  "message": "Profile updated successfully",
  "data": {
    "user": {
      "id": 1,
      "name": "John Smith",
      "mobile_no": "9876543211",
      "color_theme": "dark",
      "updated_at": "2024-01-15T11:30:00Z"
    }
  }
}
```

### 6. Reset Password
**Endpoint**: `POST /api/auth/reset_password`
**Auth**: None
**Description**: Initiate password reset process

**Request Body**:
```json
{
  "email": "user@example.com"
}
```

**Success Response (200)**:
```json
{
  "success": true,
  "message": "Password reset instructions sent to your email",
  "data": {
    "email": "user@example.com",
    "reset_token_sent": true
  }
}
```

### 7. Logout
**Endpoint**: `POST /api/auth/logout`
**Auth**: Bearer Token (User)
**Description**: Logout and blacklist current token

**Success Response (200)**:
```json
{
  "success": true,
  "message": "Logged out successfully",
  "data": {
    "logged_out": true
  }
}
```

### 8. Soft Delete Account
**Endpoint**: `DELETE /api/auth/soft_delete`
**Auth**: Bearer Token (User)
**Description**: Deactivate user account (soft delete)

**Success Response (200)**:
```json
{
  "success": true,
  "message": "Account deactivated successfully",
  "data": {
    "account_status": "inactive",
    "deactivated_at": "2024-01-15T12:00:00Z"
  }
}
```

---

## 📚 Course & Subject Management

### 1. List All Courses
**Endpoint**: `GET /api/courses`
**Auth**: None (Public)
**Description**: Get paginated list of all available courses

**Query Parameters**:
- `page` (optional): Page number (default: 1)
- `per_page` (optional): Items per page (default: 10)
- `search` (optional): Search term for course names

**Example Request**:
```
GET /api/courses?page=1&per_page=5&search=UPSC
```

**Success Response (200)**:
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
        "subjects_count": 8,
        "created_at": "2024-01-15T10:00:00Z",
        "updated_at": "2024-01-15T10:00:00Z"
      },
      {
        "id": 2,
        "course_name": "NEET Medical Entrance",
        "description": "Complete preparation course for NEET medical entrance exam",
        "subjects_count": 4,
        "created_at": "2024-01-15T10:00:00Z",
        "updated_at": "2024-01-15T10:00:00Z"
      }
    ],
    "pagination": {
      "page": 1,
      "pages": 3,
      "per_page": 5,
      "total": 12,
      "has_next": true,
      "has_prev": false
    }
  }
}
```

### 2. Get Course by ID
**Endpoint**: `GET /api/courses/{course_id}`
**Auth**: None (Public)
**Description**: Get detailed information about a specific course

**Query Parameters**:
- `include_subjects` (optional): Include subjects list (default: true)

**Example Request**:
```
GET /api/courses/1?include_subjects=true
```

**Success Response (200)**:
```json
{
  "success": true,
  "message": "Course retrieved successfully",
  "data": {
    "course": {
      "id": 1,
      "course_name": "UPSC Civil Services",
      "description": "Comprehensive course for UPSC Civil Services examination preparation",
      "subjects_count": 8,
      "created_at": "2024-01-15T10:00:00Z",
      "updated_at": "2024-01-15T10:00:00Z",
      "subjects": [
        {
          "id": 1,
          "subject_name": "General Studies Paper 1",
          "exam_category_id": 1,
          "created_at": "2024-01-15T10:00:00Z"
        },
        {
          "id": 2,
          "subject_name": "General Studies Paper 2",
          "exam_category_id": 1,
          "created_at": "2024-01-15T10:00:00Z"
        }
      ]
    }
  }
}
```

### 3. Get Subjects for Course
**Endpoint**: `GET /api/subjects`
**Auth**: None (Public)
**Description**: Get subjects for a specific course

**Query Parameters**:
- `course_id` (required): Course ID
- `page` (optional): Page number (default: 1)
- `per_page` (optional): Items per page (default: 20)

**Example Request**:
```
GET /api/subjects?course_id=1&page=1&per_page=10
```

**Success Response (200)**:
```json
{
  "success": true,
  "message": "Subjects retrieved successfully",
  "data": {
    "subjects": [
      {
        "id": 1,
        "subject_name": "General Studies Paper 1",
        "exam_category_id": 1,
        "created_at": "2024-01-15T10:00:00Z",
        "updated_at": "2024-01-15T10:00:00Z"
      },
      {
        "id": 2,
        "subject_name": "General Studies Paper 2",
        "exam_category_id": 1,
        "created_at": "2024-01-15T10:00:00Z",
        "updated_at": "2024-01-15T10:00:00Z"
      }
    ],
    "pagination": {
      "page": 1,
      "pages": 1,
      "per_page": 10,
      "total": 8,
      "has_next": false,
      "has_prev": false
    }
  }
}
```

### 4. Create New Course (Admin)
**Endpoint**: `POST /api/admin/courses`
**Auth**: Bearer Token (Admin)
**Description**: Create a new course

**Request Body**:
```json
{
  "course_name": "JEE Main & Advanced",
  "description": "Complete preparation course for JEE Main and Advanced engineering entrance exams"
}
```

**Success Response (201)**:
```json
{
  "success": true,
  "message": "Course created successfully",
  "data": {
    "course": {
      "id": 3,
      "course_name": "JEE Main & Advanced",
      "description": "Complete preparation course for JEE Main and Advanced engineering entrance exams",
      "subjects_count": 0,
      "created_at": "2024-01-15T12:00:00Z",
      "updated_at": "2024-01-15T12:00:00Z"
    }
  }
}
```

### 5. Update Course (Admin)
**Endpoint**: `PUT /api/admin/courses/{course_id}`
**Auth**: Bearer Token (Admin)
**Description**: Update an existing course

**Request Body**:
```json
{
  "course_name": "UPSC Civil Services - Updated",
  "description": "Updated comprehensive course for UPSC Civil Services examination preparation with latest syllabus"
}
```

**Success Response (200)**:
```json
{
  "success": true,
  "message": "Course updated successfully",
  "data": {
    "course": {
      "id": 1,
      "course_name": "UPSC Civil Services - Updated",
      "description": "Updated comprehensive course for UPSC Civil Services examination preparation with latest syllabus",
      "subjects_count": 8,
      "updated_at": "2024-01-15T13:00:00Z"
    }
  }
}
```

### 6. Delete Course (Admin)
**Endpoint**: `DELETE /api/admin/courses/{course_id}`
**Auth**: Bearer Token (Admin)
**Description**: Delete a course and all its subjects

**Success Response (200)**:
```json
{
  "success": true,
  "message": "Course deleted successfully",
  "data": {
    "deleted_course_id": 3,
    "deleted_course_name": "JEE Main & Advanced",
    "subjects_deleted": 0
  }
}
```

### 7. Add Subject to Course (Admin)
**Endpoint**: `POST /api/admin/subjects`
**Auth**: Bearer Token (Admin)
**Description**: Add a new subject to an existing course

**Request Body**:
```json
{
  "exam_category_id": 1,
  "subject_name": "Essay Writing"
}
```

**Success Response (201)**:
```json
{
  "success": true,
  "message": "Subject added successfully",
  "data": {
    "subject": {
      "id": 9,
      "subject_name": "Essay Writing",
      "exam_category_id": 1,
      "created_at": "2024-01-15T14:00:00Z",
      "updated_at": "2024-01-15T14:00:00Z"
    },
    "course": {
      "id": 1,
      "course_name": "UPSC Civil Services",
      "subjects_count": 9
    }
  }
}
```

### 8. Update Subject (Admin)
**Endpoint**: `PUT /api/admin/subjects/{subject_id}`
**Auth**: Bearer Token (Admin)
**Description**: Update an existing subject

**Request Body**:
```json
{
  "subject_name": "Essay Writing & Comprehension"
}
```

**Success Response (200)**:
```json
{
  "success": true,
  "message": "Subject updated successfully",
  "data": {
    "subject": {
      "id": 9,
      "subject_name": "Essay Writing & Comprehension",
      "exam_category_id": 1,
      "updated_at": "2024-01-15T15:00:00Z"
    }
  }
}
```

### 9. Delete Subject (Admin)
**Endpoint**: `DELETE /api/admin/subjects/{subject_id}`
**Auth**: Bearer Token (Admin)
**Description**: Delete a subject from a course

**Success Response (200)**:
```json
{
  "success": true,
  "message": "Subject deleted successfully",
  "data": {
    "deleted_subject_id": 9,
    "deleted_subject_name": "Essay Writing & Comprehension",
    "course_name": "UPSC Civil Services"
  }
}
```

---

## 🤖 AI Question Generation & Management

### 1. Generate Questions from Text (Admin)
**Endpoint**: `POST /api/ai/generate-questions-from-text`
**Auth**: Bearer Token (Admin)
**Description**: Generate MCQs from provided text content using AI

**Request Body**:
```json
{
  "content": "Photosynthesis is the process by which plants convert light energy, usually from the sun, into chemical energy that can be later released to fuel the organism's activities. This process occurs in the chloroplasts of plant cells and involves two main stages: the light-dependent reactions and the Calvin cycle.",
  "num_questions": 3,
  "subject_name": "Biology",
  "difficulty": "medium",
  "exam_category_id": 2,
  "subject_id": 4,
  "save_to_database": true
}
```

**Success Response (200)**:
```json
{
  "success": true,
  "message": "Questions generated successfully",
  "data": {
    "questions": [
      {
        "question": "What is the primary function of photosynthesis in plants?",
        "option_a": "Convert light energy into chemical energy",
        "option_b": "Convert chemical energy into light energy",
        "option_c": "Break down glucose molecules",
        "option_d": "Absorb water from soil",
        "correct_option": "A",
        "explanation": "Photosynthesis converts light energy into chemical energy that plants can use for their activities."
      },
      {
        "question": "Where does photosynthesis primarily occur in plant cells?",
        "option_a": "Mitochondria",
        "option_b": "Nucleus",
        "option_c": "Chloroplasts",
        "option_d": "Ribosomes",
        "correct_option": "C",
        "explanation": "Photosynthesis occurs in the chloroplasts of plant cells."
      }
    ],
    "total_generated": 3,
    "model_used": "llama3.2:1b",
    "subject_name": "Biology",
    "difficulty": "medium",
    "saved_to_database": true,
    "saved_count": 3,
    "saved_question_ids": [15, 16, 17]
  }
}
```

### 2. Generate Questions from PDFs (Admin)
**Endpoint**: `POST /api/ai/generate-questions-from-pdfs`
**Auth**: Bearer Token (Admin)
**Description**: Generate MCQs from PDF documents in the pdfs folder

**Request Body**:
```json
{
  "num_questions": 5,
  "subject_name": "Physics",
  "difficulty": "hard",
  "exam_category_id": 3,
  "subject_id": 7,
  "save_to_database": true
}
```

**Success Response (200)**:
```json
{
  "success": true,
  "message": "Questions generated from PDFs successfully",
  "data": {
    "questions": [
      {
        "question": "According to Newton's first law, what happens to an object at rest?",
        "option_a": "It will start moving automatically",
        "option_b": "It remains at rest unless acted upon by a force",
        "option_c": "It will accelerate gradually",
        "option_d": "It will change direction",
        "correct_option": "B",
        "explanation": "Newton's first law states that an object at rest stays at rest unless acted upon by an external force."
      }
    ],
    "total_generated": 5,
    "sources_used": ["physics_mechanics.pdf", "newton_laws.pdf"],
    "total_pdfs_processed": 8,
    "model_used": "llama3.2:1b",
    "subject_name": "Physics",
    "difficulty": "hard",
    "saved_to_database": true,
    "saved_count": 5,
    "saved_question_ids": [18, 19, 20, 21, 22]
  }
}
```

### 3. RAG Chat with PDFs
**Endpoint**: `POST /api/ai/rag/chat`
**Auth**: Bearer Token (User)
**Description**: Chat with AI using PDF documents as context

**Request Body**:
```json
{
  "query": "Explain the concept of momentum and its conservation",
  "session_id": "physics_session_123"
}
```

**Success Response (200)**:
```json
{
  "success": true,
  "message": "RAG response generated successfully",
  "data": {
    "response": "Momentum is the product of an object's mass and velocity (p = mv). The law of conservation of momentum states that in a closed system, the total momentum before and after a collision remains constant. This principle is fundamental in physics and applies to all interactions where no external forces act on the system.",
    "sources": ["physics_mechanics.pdf", "conservation_laws.pdf"],
    "relevant_docs": 2,
    "tokens_used": 67,
    "session_id": "physics_session_123",
    "model_used": "llama3.2:1b"
  }
}
```

### 4. Check RAG System Status
**Endpoint**: `GET /api/ai/rag/status`
**Auth**: None (Public)
**Description**: Check RAG system status and loaded documents

**Success Response (200)**:
```json
{
  "success": true,
  "message": "RAG status retrieved successfully",
  "data": {
    "status": "running",
    "dependencies": {
      "sentence_transformers": true,
      "PyPDF2": true,
      "ollama": true,
      "numpy": true
    },
    "pdf_folder": "./pdfs",
    "pdfs_loaded": 15,
    "sources": [
      "subjects/mathematics/calculus.pdf",
      "subjects/physics/mechanics.pdf",
      "subjects/chemistry/organic.pdf",
      "general/study_tips.pdf"
    ],
    "ollama_model": "llama3.2:1b",
    "embeddings_available": true
  }
}
```

### 5. Reload RAG Index (Admin)
**Endpoint**: `POST /api/ai/rag/reload`
**Auth**: Bearer Token (Admin)
**Description**: Reload RAG index from PDF documents

**Success Response (200)**:
```json
{
  "success": true,
  "message": "RAG index reloaded successfully",
  "data": {
    "message": "RAG index reloaded successfully",
    "pdfs_loaded": 18,
    "sources": [
      "subjects/mathematics/algebra.pdf",
      "subjects/physics/thermodynamics.pdf",
      "subjects/chemistry/inorganic.pdf"
    ]
  }
}
```

---

## 📝 Question Management

### 1. List Questions
**Endpoint**: `GET /api/questions`
**Auth**: Bearer Token (User)
**Description**: Get paginated list of questions with filtering options

**Query Parameters**:
- `page` (optional): Page number (default: 1)
- `per_page` (optional): Items per page (default: 20)
- `exam_category_id` (optional): Filter by course ID
- `subject_id` (optional): Filter by subject ID

**Example Request**:
```
GET /api/questions?page=1&per_page=10&subject_id=4
```

**Success Response (200)**:
```json
{
  "success": true,
  "message": "Questions retrieved successfully",
  "data": {
    "questions": [
      {
        "id": 15,
        "exam_category_id": 2,
        "subject_id": 4,
        "question": "What is the primary function of photosynthesis in plants?",
        "option_1": "Convert light energy into chemical energy",
        "option_2": "Convert chemical energy into light energy",
        "option_3": "Break down glucose molecules",
        "option_4": "Absorb water from soil",
        "explanation": "Photosynthesis converts light energy into chemical energy.",
        "is_ai_generated": true,
        "ai_model_used": "llama3.2:1b",
        "difficulty_level": "medium",
        "created_at": "2024-01-15T16:00:00Z",
        "updated_at": "2024-01-15T16:00:00Z"
      }
    ],
    "pagination": {
      "page": 1,
      "pages": 5,
      "per_page": 10,
      "total": 45,
      "has_next": true,
      "has_prev": false
    }
  }
}
```

### 2. Get Question by ID
**Endpoint**: `GET /api/questions/{question_id}`
**Auth**: Bearer Token (User)
**Description**: Get detailed information about a specific question

**Success Response (200)**:
```json
{
  "success": true,
  "message": "Question retrieved successfully",
  "data": {
    "question": {
      "id": 15,
      "exam_category_id": 2,
      "subject_id": 4,
      "question": "What is the primary function of photosynthesis in plants?",
      "option_1": "Convert light energy into chemical energy",
      "option_2": "Convert chemical energy into light energy",
      "option_3": "Break down glucose molecules",
      "option_4": "Absorb water from soil",
      "explanation": "Photosynthesis converts light energy into chemical energy.",
      "is_ai_generated": true,
      "ai_model_used": "llama3.2:1b",
      "difficulty_level": "medium",
      "created_at": "2024-01-15T16:00:00Z",
      "updated_at": "2024-01-15T16:00:00Z"
    }
  }
}
```

### 3. Create Question Manually (Admin)
**Endpoint**: `POST /api/admin/questions`
**Auth**: Bearer Token (Admin)
**Description**: Create a new question manually

**Request Body**:
```json
{
  "exam_category_id": 1,
  "subject_id": 2,
  "question": "Who was the first President of India?",
  "option_1": "Dr. Rajendra Prasad",
  "option_2": "Dr. A.P.J. Abdul Kalam",
  "option_3": "Dr. Sarvepalli Radhakrishnan",
  "option_4": "Pandit Jawaharlal Nehru",
  "correct_answer": "Dr. Rajendra Prasad",
  "explanation": "Dr. Rajendra Prasad was the first President of India, serving from 1950 to 1962.",
  "difficulty_level": "easy"
}
```

**Success Response (201)**:
```json
{
  "success": true,
  "message": "Question created successfully",
  "data": {
    "question": {
      "id": 23,
      "exam_category_id": 1,
      "subject_id": 2,
      "question": "Who was the first President of India?",
      "option_1": "Dr. Rajendra Prasad",
      "option_2": "Dr. A.P.J. Abdul Kalam",
      "option_3": "Dr. Sarvepalli Radhakrishnan",
      "option_4": "Pandit Jawaharlal Nehru",
      "explanation": "Dr. Rajendra Prasad was the first President of India, serving from 1950 to 1962.",
      "is_ai_generated": false,
      "difficulty_level": "easy",
      "created_at": "2024-01-15T17:00:00Z"
    }
  }
}
```

### 4. Update Question (Admin)
**Endpoint**: `PUT /api/admin/questions/{question_id}`
**Auth**: Bearer Token (Admin)
**Description**: Update an existing question

**Request Body**:
```json
{
  "question": "Who was the first President of independent India?",
  "option_1": "Dr. Rajendra Prasad",
  "option_2": "Dr. A.P.J. Abdul Kalam",
  "option_3": "Dr. Sarvepalli Radhakrishnan",
  "option_4": "Mahatma Gandhi",
  "correct_answer": "Dr. Rajendra Prasad",
  "explanation": "Dr. Rajendra Prasad was the first President of independent India, serving from 1950 to 1962.",
  "difficulty_level": "medium"
}
```

**Success Response (200)**:
```json
{
  "success": true,
  "message": "Question updated successfully",
  "data": {
    "question": {
      "id": 23,
      "question": "Who was the first President of independent India?",
      "option_1": "Dr. Rajendra Prasad",
      "option_2": "Dr. A.P.J. Abdul Kalam",
      "option_3": "Dr. Sarvepalli Radhakrishnan",
      "option_4": "Mahatma Gandhi",
      "explanation": "Dr. Rajendra Prasad was the first President of independent India, serving from 1950 to 1962.",
      "difficulty_level": "medium",
      "updated_at": "2024-01-15T18:00:00Z"
    }
  }
}
```

### 5. Delete Question (Admin)
**Endpoint**: `DELETE /api/admin/questions/{question_id}`
**Auth**: Bearer Token (Admin)
**Description**: Delete a specific question

**Success Response (200)**:
```json
{
  "success": true,
  "message": "Question deleted successfully",
  "data": {
    "message": "Question deleted successfully",
    "deleted_question_id": 23
  }
}
```

### 6. Bulk Delete Questions (Admin)
**Endpoint**: `POST /api/admin/questions/bulk-delete`
**Auth**: Bearer Token (Admin)
**Description**: Delete multiple questions at once

**Request Body**:
```json
{
  "question_ids": [15, 16, 17, 18, 19]
}
```

**Success Response (200)**:
```json
{
  "success": true,
  "message": "Questions deleted successfully",
  "data": {
    "message": "5 questions deleted successfully",
    "deleted_count": 5,
    "requested_ids": [15, 16, 17, 18, 19]
  }
}
```

---

## 💬 Community Blog

### 1. List Community Posts
**Endpoint**: `GET /api/community/posts`
**Auth**: None (Public)
**Description**: Get paginated list of community blog posts

**Query Parameters**:
- `page` (optional): Page number (default: 1)
- `per_page` (optional): Items per page (default: 10)
- `search` (optional): Search term in title/content
- `tags` (optional): Filter by tags (comma-separated)
- `featured` (optional): Filter featured posts (true/false)

**Example Request**:
```
GET /api/community/posts?page=1&per_page=5&tags=physics,tips&featured=true
```

**Success Response (200)**:
```json
{
  "success": true,
  "message": "Posts retrieved successfully",
  "data": {
    "posts": [
      {
        "id": 1,
        "user_id": 5,
        "title": "Top 10 Physics Tips for NEET",
        "content": "Here are some essential physics tips that will help you excel in NEET...",
        "tags": "physics,neet,tips",
        "likes_count": 45,
        "comments_count": 12,
        "is_featured": true,
        "status": "published",
        "created_at": "2024-01-15T10:00:00Z",
        "updated_at": "2024-01-15T10:00:00Z",
        "author": {
          "id": 5,
          "name": "Dr. Physics Expert",
          "email_id": "physics@example.com"
        }
      }
    ],
    "pagination": {
      "page": 1,
      "pages": 8,
      "per_page": 5,
      "total": 38,
      "has_next": true,
      "has_prev": false
    }
  }
}
```

### 2. Create New Post
**Endpoint**: `POST /api/community/posts`
**Auth**: Bearer Token (User)
**Description**: Create a new community blog post

**Request Body**:
```json
{
  "title": "Effective Study Techniques for UPSC",
  "content": "Preparing for UPSC requires a systematic approach. Here are some proven techniques that can help you succeed in your UPSC journey...",
  "tags": "upsc,study,techniques,tips"
}
```

**Success Response (201)**:
```json
{
  "success": true,
  "message": "Post created successfully",
  "data": {
    "post": {
      "id": 39,
      "user_id": 3,
      "title": "Effective Study Techniques for UPSC",
      "content": "Preparing for UPSC requires a systematic approach...",
      "tags": "upsc,study,techniques,tips",
      "likes_count": 0,
      "comments_count": 0,
      "is_featured": false,
      "status": "published",
      "created_at": "2024-01-15T19:00:00Z",
      "updated_at": "2024-01-15T19:00:00Z"
    }
  }
}
```

### 3. Like a Post
**Endpoint**: `POST /api/community/posts/{post_id}/like`
**Auth**: Bearer Token (User)
**Description**: Like or unlike a community post

**Success Response (200)**:
```json
{
  "success": true,
  "message": "Post liked successfully",
  "data": {
    "post_id": 1,
    "liked": true,
    "likes_count": 46,
    "user_liked": true
  }
}
```

### 4. Add Comment to Post
**Endpoint**: `POST /api/community/posts/{post_id}/comment`
**Auth**: Bearer Token (User)
**Description**: Add a comment to a community post

**Request Body**:
```json
{
  "content": "Great tips! This really helped me understand the concepts better. Thank you for sharing!"
}
```

**Success Response (201)**:
```json
{
  "success": true,
  "message": "Comment added successfully",
  "data": {
    "comment": {
      "id": 25,
      "post_id": 1,
      "user_id": 3,
      "content": "Great tips! This really helped me understand the concepts better. Thank you for sharing!",
      "created_at": "2024-01-15T20:00:00Z",
      "updated_at": "2024-01-15T20:00:00Z",
      "author": {
        "id": 3,
        "name": "John Doe",
        "email_id": "john@example.com"
      }
    },
    "post": {
      "id": 1,
      "comments_count": 13
    }
  }
}
```

### 5. Delete Own Comment
**Endpoint**: `DELETE /api/community/comments/{comment_id}`
**Auth**: Bearer Token (User)
**Description**: Delete user's own comment

**Success Response (200)**:
```json
{
  "success": true,
  "message": "Comment deleted successfully",
  "data": {
    "deleted_comment_id": 25,
    "post_id": 1,
    "updated_comments_count": 12
  }
}
```

### 6. Delete Own Post
**Endpoint**: `DELETE /api/community/posts/{post_id}`
**Auth**: Bearer Token (User)
**Description**: Delete user's own blog post

**Success Response (200)**:
```json
{
  "success": true,
  "message": "Post deleted successfully",
  "data": {
    "deleted_post_id": 39,
    "deleted_post_title": "Effective Study Techniques for UPSC"
  }
}
```

---

## 👑 Admin Moderation

### 1. Edit Any Post (Admin)
**Endpoint**: `PUT /api/admin/posts/{post_id}`
**Auth**: Bearer Token (Admin)
**Description**: Edit any community post (admin privilege)

**Request Body**:
```json
{
  "title": "Top 10 Physics Tips for NEET - Updated",
  "content": "Here are some essential physics tips that will help you excel in NEET (updated with latest syllabus)...",
  "tags": "physics,neet,tips,updated",
  "is_featured": true,
  "status": "published"
}
```

**Success Response (200)**:
```json
{
  "success": true,
  "message": "Post updated successfully",
  "data": {
    "post": {
      "id": 1,
      "title": "Top 10 Physics Tips for NEET - Updated",
      "content": "Here are some essential physics tips that will help you excel in NEET (updated with latest syllabus)...",
      "tags": "physics,neet,tips,updated",
      "is_featured": true,
      "status": "published",
      "updated_at": "2024-01-15T21:00:00Z"
    }
  }
}
```

### 2. Delete Any Post (Admin)
**Endpoint**: `DELETE /api/admin/posts/{post_id}`
**Auth**: Bearer Token (Admin)
**Description**: Delete any community post (admin privilege)

**Success Response (200)**:
```json
{
  "success": true,
  "message": "Post deleted successfully",
  "data": {
    "deleted_post_id": 1,
    "deleted_post_title": "Top 10 Physics Tips for NEET - Updated",
    "author_name": "Dr. Physics Expert"
  }
}
```

### 3. Edit Any Comment (Admin)
**Endpoint**: `PUT /api/admin/comments/{comment_id}`
**Auth**: Bearer Token (Admin)
**Description**: Edit any comment (admin privilege)

**Request Body**:
```json
{
  "content": "[Edited by Admin] Great tips! This really helped me understand the concepts better."
}
```

**Success Response (200)**:
```json
{
  "success": true,
  "message": "Comment updated successfully",
  "data": {
    "comment": {
      "id": 25,
      "content": "[Edited by Admin] Great tips! This really helped me understand the concepts better.",
      "updated_at": "2024-01-15T22:00:00Z"
    }
  }
}
```

### 4. Delete Any Comment (Admin)
**Endpoint**: `DELETE /api/admin/comments/{comment_id}`
**Auth**: Bearer Token (Admin)
**Description**: Delete any comment (admin privilege)

**Success Response (200)**:
```json
{
  "success": true,
  "message": "Comment deleted successfully",
  "data": {
    "deleted_comment_id": 25,
    "post_id": 1,
    "author_name": "John Doe",
    "updated_comments_count": 11
  }
}
```

---

## 🤖 AI Chatbot

### 1. Ask Educational Question
**Endpoint**: `POST /api/ai/chat`
**Auth**: Bearer Token (User)
**Description**: Ask educational questions to AI chatbot

**Request Body**:
```json
{
  "message": "Explain the concept of photosynthesis and its importance in the ecosystem",
  "context": "biology",
  "session_id": "biology_session_456"
}
```

**Success Response (200)**:
```json
{
  "success": true,
  "message": "AI response generated successfully",
  "data": {
    "response": "Photosynthesis is a vital biological process where plants convert light energy into chemical energy. It involves two main stages: light-dependent reactions and the Calvin cycle. This process is crucial for the ecosystem as it produces oxygen and serves as the foundation of most food chains.",
    "tokens_used": 52,
    "session_id": "biology_session_456"
  }
}
```

### 2. Get Chat Token Statistics (Admin)
**Endpoint**: `GET /api/admin/chat/tokens`
**Auth**: Bearer Token (Admin)
**Description**: Get AI chat token usage statistics for all users

**Query Parameters**:
- `page` (optional): Page number (default: 1)
- `per_page` (optional): Items per page (default: 10)
- `month_year` (optional): Filter by month (format: YYYY-MM)

**Example Request**:
```
GET /api/admin/chat/tokens?page=1&per_page=5&month_year=2024-01
```

**Success Response (200)**:
```json
{
  "success": true,
  "message": "Token statistics retrieved successfully",
  "data": {
    "token_stats": [
      {
        "id": 1,
        "user_id": 3,
        "total_queries": 45,
        "total_tokens_used": 2340,
        "monthly_queries": 15,
        "monthly_tokens_used": 780,
        "last_query_date": "2024-01-15T22:30:00Z",
        "month_year": "2024-01",
        "user_name": "John Doe",
        "user_email": "john@example.com"
      },
      {
        "id": 2,
        "user_id": 5,
        "total_queries": 32,
        "total_tokens_used": 1890,
        "monthly_queries": 12,
        "monthly_tokens_used": 650,
        "last_query_date": "2024-01-15T21:45:00Z",
        "month_year": "2024-01",
        "user_name": "Dr. Physics Expert",
        "user_email": "physics@example.com"
      }
    ],
    "pagination": {
      "page": 1,
      "pages": 3,
      "per_page": 5,
      "total": 12,
      "has_next": true,
      "has_prev": false
    }
  }
}
```

---

## 👥 Admin User Management

### 1. List All Users (Admin)
**Endpoint**: `GET /api/admin/users`
**Auth**: Bearer Token (Admin)
**Description**: Get paginated list of all users in the system

**Query Parameters**:
- `page` (optional): Page number (default: 1)
- `per_page` (optional): Items per page (default: 10)
- `search` (optional): Search by name or email
- `status` (optional): Filter by status (active/inactive/blocked)
- `is_premium` (optional): Filter premium users (true/false)

**Example Request**:
```
GET /api/admin/users?page=1&per_page=5&status=active&search=john
```

**Success Response (200)**:
```json
{
  "success": true,
  "message": "Users retrieved successfully",
  "data": {
    "users": [
      {
        "id": 3,
        "email_id": "john@example.com",
        "name": "John Doe",
        "mobile_no": "9876543210",
        "is_premium": false,
        "is_admin": false,
        "color_theme": "light",
        "status": "active",
        "auth_provider": "manual",
        "last_login": "2024-01-15T22:30:00Z",
        "created_at": "2024-01-10T10:00:00Z",
        "updated_at": "2024-01-15T22:30:00Z"
      },
      {
        "id": 5,
        "email_id": "physics@example.com",
        "name": "Dr. Physics Expert",
        "mobile_no": "9876543211",
        "is_premium": true,
        "is_admin": false,
        "color_theme": "dark",
        "status": "active",
        "auth_provider": "google",
        "last_login": "2024-01-15T21:45:00Z",
        "created_at": "2024-01-08T15:30:00Z",
        "updated_at": "2024-01-15T21:45:00Z"
      }
    ],
    "pagination": {
      "page": 1,
      "pages": 4,
      "per_page": 5,
      "total": 18,
      "has_next": true,
      "has_prev": false
    }
  }
}
```

### 2. Deactivate User Account (Admin)
**Endpoint**: `PUT /api/admin/users/{user_id}/deactivate`
**Auth**: Bearer Token (Admin)
**Description**: Deactivate a user account

**Success Response (200)**:
```json
{
  "success": true,
  "message": "User deactivated successfully",
  "data": {
    "user_id": 3,
    "user_name": "John Doe",
    "user_email": "john@example.com",
    "previous_status": "active",
    "new_status": "inactive",
    "deactivated_at": "2024-01-15T23:00:00Z"
  }
}
```

### 3. Get User Purchase History (Admin)
**Endpoint**: `GET /api/admin/users/{user_id}/purchases`
**Auth**: Bearer Token (Admin)
**Description**: Get detailed purchase history for a specific user

**Query Parameters**:
- `page` (optional): Page number (default: 1)
- `per_page` (optional): Items per page (default: 10)

**Example Request**:
```
GET /api/admin/users/3/purchases?page=1&per_page=5
```

**Success Response (200)**:
```json
{
  "success": true,
  "message": "User purchases retrieved successfully",
  "data": {
    "user": {
      "id": 3,
      "name": "John Doe",
      "email_id": "john@example.com"
    },
    "purchases": [
      {
        "id": 1,
        "user_id": 3,
        "exam_category_id": 1,
        "subject_id": 2,
        "cost": 299.00,
        "no_of_attempts": 3,
        "attempts_used": 1,
        "total_marks": 100,
        "marks_scored": 85,
        "purchase_date": "2024-01-10T12:00:00Z",
        "last_attempt_date": "2024-01-12T14:30:00Z",
        "status": "active",
        "exam_category_name": "UPSC Civil Services",
        "subject_name": "General Studies Paper 2"
      }
    ],
    "pagination": {
      "page": 1,
      "pages": 1,
      "per_page": 5,
      "total": 2,
      "has_next": false,
      "has_prev": false
    },
    "summary": {
      "total_purchases": 2,
      "total_amount_spent": 598.00,
      "active_purchases": 2,
      "completed_purchases": 0
    }
  }
}
```

### 4. Get User AI Chat Token Usage (Admin)
**Endpoint**: `GET /api/admin/users/{user_id}/chat_tokens`
**Auth**: Bearer Token (Admin)
**Description**: Get AI chat token usage statistics for a specific user

**Success Response (200)**:
```json
{
  "success": true,
  "message": "User AI token usage retrieved successfully",
  "data": {
    "user": {
      "id": 3,
      "name": "John Doe",
      "email_id": "john@example.com"
    },
    "token_usage": {
      "total_queries": 45,
      "total_tokens_used": 2340,
      "monthly_queries": 15,
      "monthly_tokens_used": 780,
      "last_query_date": "2024-01-15T22:30:00Z",
      "current_month": "2024-01"
    },
    "monthly_breakdown": [
      {
        "month_year": "2024-01",
        "queries": 15,
        "tokens_used": 780
      },
      {
        "month_year": "2023-12",
        "queries": 30,
        "tokens_used": 1560
      }
    ]
  }
}
```

---

## 🔍 Legacy Endpoints (For Compatibility)

### 1. Google OAuth Redirect
**Endpoint**: `GET /auth/google`
**Auth**: None
**Description**: Redirect to Google OAuth authorization

**Success Response (302)**:
```
Redirects to Google OAuth authorization URL
```

### 2. Google OAuth Callback
**Endpoint**: `GET /auth/google/callback`
**Auth**: None
**Description**: Handle Google OAuth callback and complete authentication

**Query Parameters**:
- `code`: Authorization code from Google
- `state`: State parameter for security

**Success Response (200)**:
```json
{
  "success": true,
  "message": "Google OAuth login successful",
  "data": {
    "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "user": {
      "id": 7,
      "email_id": "user@gmail.com",
      "name": "Google User",
      "auth_provider": "google",
      "google_id": "google_user_id_123"
    }
  }
}
```

### 3. Health Check
**Endpoint**: `GET /health`
**Auth**: None
**Description**: Check API health status

**Success Response (200)**:
```json
{
  "success": true,
  "message": "Jishu Backend API is running",
  "version": "1.0.0",
  "architecture": "monolithic"
}
```

---

## 📝 Complete cURL Examples

### Authentication Flow
```bash
# 1. Request OTP
curl -X POST http://localhost:5000/api/auth/otp/request \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com"}'

# 2. Complete Registration
curl -X POST http://localhost:5000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "otp": "123456",
    "password": "SecurePass123!",
    "name": "John Doe",
    "mobile_no": "9876543210"
  }'

# 3. Login
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "SecurePass123!"
  }'
```

### Course Management
```bash
# Create Course (Admin)
curl -X POST http://localhost:5000/api/admin/courses \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN" \
  -d '{
    "course_name": "JEE Main & Advanced",
    "description": "Complete preparation course for JEE engineering entrance exams"
  }'

# Add Subject to Course (Admin)
curl -X POST http://localhost:5000/api/admin/subjects \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN" \
  -d '{
    "exam_category_id": 3,
    "subject_name": "Mathematics"
  }'
```

### AI Question Generation
```bash
# Generate Questions from Text (Admin)
curl -X POST http://localhost:5000/api/ai/generate-questions-from-text \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN" \
  -d '{
    "content": "Photosynthesis is the process by which plants convert light energy into chemical energy...",
    "num_questions": 3,
    "subject_name": "Biology",
    "difficulty": "medium",
    "exam_category_id": 2,
    "subject_id": 4,
    "save_to_database": true
  }'

# RAG Chat
curl -X POST http://localhost:5000/api/ai/rag/chat \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_USER_TOKEN" \
  -d '{
    "query": "Explain Newton's laws of motion",
    "session_id": "physics_session_123"
  }'
```

### Community Interaction
```bash
# Create Post
curl -X POST http://localhost:5000/api/community/posts \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_USER_TOKEN" \
  -d '{
    "title": "Top 10 Physics Tips for NEET",
    "content": "Here are some essential physics tips...",
    "tags": "physics,neet,tips"
  }'

# Like Post
curl -X POST http://localhost:5000/api/community/posts/1/like \
  -H "Authorization: Bearer YOUR_USER_TOKEN"

# Add Comment
curl -X POST http://localhost:5000/api/community/posts/1/comment \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_USER_TOKEN" \
  -d '{
    "content": "Great tips! Very helpful for NEET preparation."
  }'
```

### Question Management
```bash
# List Questions
curl -X GET "http://localhost:5000/api/questions?page=1&per_page=10&subject_id=4" \
  -H "Authorization: Bearer YOUR_USER_TOKEN"

# Create Question Manually (Admin)
curl -X POST http://localhost:5000/api/admin/questions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN" \
  -d '{
    "exam_category_id": 1,
    "subject_id": 2,
    "question": "Who was the first President of India?",
    "option_1": "Dr. Rajendra Prasad",
    "option_2": "Dr. A.P.J. Abdul Kalam",
    "option_3": "Dr. Sarvepalli Radhakrishnan",
    "option_4": "Pandit Jawaharlal Nehru",
    "correct_answer": "Dr. Rajendra Prasad",
    "explanation": "Dr. Rajendra Prasad was the first President of India.",
    "difficulty_level": "easy"
  }'
```

---

## 🔒 Security Features

- **JWT Authentication**: Access and refresh tokens with configurable expiration
- **Role-based Access Control**: User/Admin permissions with granular access
- **OTP Verification**: Email-based verification for registration and password reset
- **Input Validation**: Comprehensive data validation and sanitization
- **CORS Protection**: Configurable origins for cross-origin requests
- **Password Security**: Bcrypt hashing with salt for password storage
- **Token Blacklisting**: Logout functionality with token invalidation
- **Rate Limiting**: (To be implemented for API protection)

---

## 🗄️ Database Models

The API uses the following main models:

### Core Models
- **Users**: User accounts, authentication, and profile information
- **ExamCategory**: Courses/exam categories for different competitive exams
- **ExamCategorySubject**: Subjects within each course/exam category
- **ExamCategoryPurchase**: User purchase history and subscription tracking
- **ExamCategoryQuestion**: Questions with AI generation tracking
- **TestAttempt**: User test attempts and scoring
- **TestAnswer**: Individual answers for each test attempt

### Community Models
- **BlogPost**: Community blog posts with tags and moderation
- **BlogComment**: Comments on community posts
- **BlogLike**: Like system for community posts

### AI Models
- **AIChatHistory**: AI chat interactions and conversation history
- **UserAIStats**: AI usage statistics and token consumption tracking
- **PasswordResetToken**: Secure password reset token management

### Enhanced Question Model Fields
- `is_ai_generated`: Boolean flag for AI-generated questions
- `ai_model_used`: AI model name used for generation (e.g., 'llama3.2:1b')
- `difficulty_level`: Question difficulty (easy/medium/hard)
- `source_content`: Original content used for AI generation

---

## 🚀 Getting Started

### Prerequisites
- Python 3.8+
- MySQL 8.0+
- Ollama (for AI features)

### Installation Steps
1. **Clone Repository**: `git clone <repository_url>`
2. **Install Dependencies**: `pip install -r requirements.txt`
3. **Setup Ollama**:
   ```bash
   # Install Ollama from https://ollama.ai/
   ollama pull llama3.2:1b
   ```
4. **Environment Setup**: Copy `.env.example` to `.env` and configure:
   ```env
   MYSQL_HOST=localhost
   MYSQL_USER=root
   MYSQL_PASSWORD=your_password
   MYSQL_DB=jishu_app
   JWT_SECRET_KEY=your_jwt_secret
   GOOGLE_CLIENT_ID=your_google_client_id
   GOOGLE_CLIENT_SECRET=your_google_client_secret
   AI_PDF_FOLDER=./pdfs
   AI_OLLAMA_MODEL=llama3.2:1b
   ```
5. **Database Setup**:
   ```bash
   # Create database
   mysql -u root -p -e "CREATE DATABASE jishu_app;"

   # Run migration for AI features
   mysql -u root -p jishu_app < add_ai_question_fields.sql
   ```
6. **PDF Setup**: Place educational PDFs in `pdfs/` directory
7. **Start Server**: `python app.py`
8. **Test Health**: Visit `http://localhost:5000/health`

### Quick Test
```bash
# Test health endpoint
curl http://localhost:5000/health

# Test RAG status
curl http://localhost:5000/api/ai/rag/status
```

---

## 📊 HTTP Status Codes

### Success Codes
- **200 OK**: Request successful
- **201 Created**: Resource created successfully
- **302 Found**: Redirect (used for OAuth)

### Client Error Codes
- **400 Bad Request**: Invalid request data or parameters
- **401 Unauthorized**: Authentication required or invalid token
- **403 Forbidden**: Insufficient permissions (admin required)
- **404 Not Found**: Resource not found
- **409 Conflict**: Resource already exists or conflict
- **422 Unprocessable Entity**: Validation errors

### Server Error Codes
- **500 Internal Server Error**: Server-side error

---

## 🔧 Configuration Options

### AI Service Configuration
```python
AI_PDF_FOLDER = "./pdfs"                    # PDF documents folder
AI_OLLAMA_MODEL = "llama3.2:1b"            # Ollama model name
AI_MAX_CONTENT_LENGTH = 8000                # Max content length for generation
AI_DEFAULT_QUESTIONS_COUNT = 5              # Default number of questions
AI_SIMILARITY_THRESHOLD = 0.1               # RAG similarity threshold
AI_RAG_TOP_K = 3                           # Number of similar documents to retrieve
```

### JWT Configuration
```python
JWT_ACCESS_TOKEN_EXPIRES = 3600             # 1 hour
JWT_REFRESH_TOKEN_EXPIRES = 2592000         # 30 days
```

### Database Configuration
```python
SQLALCHEMY_DATABASE_URI = "mysql+pymysql://user:pass@host/db"
SQLALCHEMY_TRACK_MODIFICATIONS = False
```

---

## 📈 Performance & Monitoring

### AI Features Performance
- **Question Generation**: ~2-5 seconds per request (depends on content length)
- **RAG Chat**: ~1-3 seconds per query (depends on document corpus size)
- **PDF Processing**: Processed once and cached in memory
- **Embedding Generation**: One-time process per PDF document

### Recommended Limits
- **Questions per request**: 1-20 (optimal: 5)
- **Content length**: Max 8000 characters
- **PDF file size**: Max 50MB per file
- **Concurrent users**: Tested up to 100 concurrent users

### Monitoring Endpoints
- `/health` - API health status
- `/api/ai/rag/status` - AI system status and dependencies
- `/api/admin/chat/tokens` - AI usage statistics

---

## 🆘 Troubleshooting

### Common Issues

1. **Ollama not available**
   - Ensure Ollama is installed and running
   - Check if the model is pulled: `ollama list`
   - Verify model name in configuration

2. **PDF processing fails**
   - Check if PyPDF2 is installed
   - Ensure PDFs are readable (not password-protected)
   - Verify PDF folder permissions

3. **Database connection errors**
   - Check MySQL service status
   - Verify database credentials in `.env`
   - Ensure database exists and is accessible

4. **JWT token errors**
   - Check token expiration
   - Verify JWT secret key configuration
   - Ensure proper Authorization header format

### Support
For technical support and bug reports, please refer to the project documentation or contact the development team.
