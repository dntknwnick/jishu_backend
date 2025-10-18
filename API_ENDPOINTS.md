# Jishu Backend - Complete API Documentation

## Base URL
```
http://localhost:5000
```

---

## Authentication Endpoints

### 1. Request OTP
**Endpoint:** `POST /api/auth/otp/request`
**Authentication:** None

**Request:**
```json
{
  "email": "user@example.com"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "email": "user@example.com",
    "otp_sent": true,
    "action": "registration",
    "user_exists": false,
    "message": "OTP sent for registration"
  },
  "message": "OTP sent for registration"
}
```

### 2. Register with OTP
**Endpoint:** `POST /api/auth/register`
**Authentication:** None

**Request:**
```json
{
  "email": "user@example.com",
  "otp": "123456",
  "name": "John Doe",
  "mobile_no": "9876543210"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "user": {
      "id": 1,
      "email_id": "user@example.com",
      "name": "John Doe",
      "mobile_no": "9876543210",
      "status": "active",
      "auth_provider": "manual",
      "created_at": "2024-01-15T10:30:00"
    }
  },
  "message": "Registration completed successfully"
}
```

### 3. Login with OTP
**Endpoint:** `POST /api/auth/login`
**Authentication:** None

**Request:**
```json
{
  "email": "user@example.com",
  "otp": "123456"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "user": {
      "id": 1,
      "email_id": "user@example.com",
      "name": "John Doe",
      "status": "active"
    },
    "auth_method_used": "otp",
    "available_auth_methods": ["otp", "google"]
  },
  "message": "Login successful"
}
```

### 4. Verify Token
**Endpoint:** `POST /verify-token`
**Authentication:** JWT Required

**Response:**
```json
{
  "success": true,
  "data": {
    "user": {
      "id": 1,
      "email_id": "user@example.com",
      "name": "John Doe"
    }
  },
  "message": "Token is valid"
}
```

### 5. Refresh Token
**Endpoint:** `POST /refresh-token`
**Authentication:** Refresh JWT Required

**Response:**
```json
{
  "success": true,
  "data": {
    "access_token": "new_access_token...",
    "refresh_token": "new_refresh_token...",
    "user": { "id": 1, "email_id": "user@example.com" }
  },
  "message": "Tokens refreshed successfully"
}
```

### 6. Logout
**Endpoint:** `POST /api/auth/logout` or `POST /logout`
**Authentication:** JWT Required

**Response:**
```json
{
  "success": true,
  "data": {
    "message": "Logged out successfully"
  },
  "message": "Logout successful"
}
```

### 7. Get Profile
**Endpoint:** `GET /api/auth/profile`
**Authentication:** JWT Required

**Response:**
```json
{
  "success": true,
  "data": {
    "user": {
      "id": 1,
      "email_id": "user@example.com",
      "name": "John Doe",
      "mobile_no": "9876543210",
      "status": "active",
      "color_theme": "light",
      "avatar": "https://...",
      "gender": "male",
      "date_of_birth": "1995-05-15",
      "city": "Mumbai",
      "state": "Maharashtra"
    }
  },
  "message": "Profile retrieved successfully"
}
```

### 8. Edit Profile
**Endpoint:** `PUT /api/auth/profile/edit`
**Authentication:** JWT Required

**Request:**
```json
{
  "name": "John Doe Updated",
  "mobile_no": "9876543210",
  "color_theme": "dark",
  "avatar": "https://...",
  "gender": "male",
  "date_of_birth": "1995-05-15",
  "city": "Mumbai",
  "state": "Maharashtra",
  "address": "123 Main St"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "user": { "id": 1, "name": "John Doe Updated", ... }
  },
  "message": "Profile updated successfully"
}
```

### 9. Soft Delete Account
**Endpoint:** `DELETE /api/auth/soft_delete`
**Authentication:** JWT Required

**Response:**
```json
{
  "success": true,
  "data": {
    "message": "Account has been deactivated successfully"
  },
  "message": "Account deactivated"
}
```

---

## Course & Subject Endpoints

### 1. Get All Courses
**Endpoint:** `GET /api/courses`
**Authentication:** None
**Query Params:** `page=1&per_page=10&search=JEE`

**Response:**
```json
{
  "success": true,
  "data": {
    "courses": [
      {
        "id": 1,
        "course_name": "JEE Main",
        "description": "Joint Entrance Examination",
        "amount": 999.00,
        "offer_amount": 499.00,
        "max_tokens": 100,
        "created_at": "2024-01-01T10:00:00"
      }
    ],
    "pagination": {
      "page": 1,
      "pages": 5,
      "per_page": 10,
      "total": 50,
      "has_next": true,
      "has_prev": false
    }
  },
  "message": "Courses retrieved successfully"
}
```

### 2. Get Course by ID
**Endpoint:** `GET /api/courses/<course_id>`
**Authentication:** None
**Query Params:** `include_subjects=true`

**Response:**
```json
{
  "success": true,
  "data": {
    "course": {
      "id": 1,
      "course_name": "JEE Main",
      "description": "Joint Entrance Examination",
      "amount": 999.00,
      "offer_amount": 499.00,
      "max_tokens": 100,
      "subjects": [
        {
          "id": 1,
          "subject_name": "Physics",
          "amount": 299.00,
          "offer_amount": 149.00,
          "max_tokens": 50,
          "total_mock": 25
        }
      ]
    }
  },
  "message": "Course retrieved successfully"
}
```

### 3. Get Subjects for Course
**Endpoint:** `GET /api/subjects`
**Authentication:** None
**Query Params:** `course_id=1&page=1&per_page=10`

**Response:**
```json
{
  "success": true,
  "data": {
    "subjects": [
      {
        "id": 1,
        "subject_name": "Physics",
        "amount": 299.00,
        "offer_amount": 149.00,
        "max_tokens": 50,
        "total_mock": 25,
        "is_bundle": false,
        "is_deleted": false
      }
    ],
    "course": { "id": 1, "course_name": "JEE Main" },
    "pagination": { "page": 1, "pages": 1, "per_page": 10, "total": 3 }
  },
  "message": "Subjects retrieved successfully"
}
```

### 4. Get Bundles for Course
**Endpoint:** `GET /api/bundles`
**Authentication:** None
**Query Params:** `course_id=1`

**Response:**
```json
{
  "success": true,
  "data": {
    "bundles": [
      {
        "id": 5,
        "subject_name": "Physics + Chemistry Bundle",
        "amount": 499.00,
        "offer_amount": 249.00,
        "is_bundle": true
      }
    ],
    "course": { "id": 1, "course_name": "JEE Main" }
  },
  "message": "Bundles retrieved successfully"
}
```

### 5. Admin: Get All Courses
**Endpoint:** `GET /api/admin/courses`
**Authentication:** Admin JWT Required
**Query Params:** `page=1&per_page=50`

**Response:**
```json
{
  "success": true,
  "data": {
    "courses": [
      {
        "id": 1,
        "course_name": "JEE Main",
        "description": "Joint Entrance Examination",
        "amount": 999.00,
        "offer_amount": 499.00,
        "max_tokens": 100,
        "status": "active",
        "subjects_count": 3,
        "created_at": "2024-01-01T10:00:00"
      }
    ],
    "pagination": { "page": 1, "per_page": 50, "total": 5 }
  },
  "message": "Courses retrieved successfully"
}
```

### 6. Admin: Add Course
**Endpoint:** `POST /api/admin/courses`
**Authentication:** Admin JWT Required

**Request:**
```json
{
  "course_name": "NEET",
  "description": "National Eligibility cum Entrance Test",
  "amount": 1299.00,
  "offer_amount": 649.00,
  "max_tokens": 150
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "course": {
      "id": 2,
      "course_name": "NEET",
      "description": "National Eligibility cum Entrance Test",
      "amount": 1299.00,
      "offer_amount": 649.00,
      "max_tokens": 150,
      "created_at": "2024-01-15T10:30:00"
    }
  },
  "message": "Course added successfully"
}
```

### 7. Admin: Edit Course
**Endpoint:** `PUT /api/admin/courses/<course_id>`
**Authentication:** Admin JWT Required

**Request:**
```json
{
  "course_name": "NEET Updated",
  "description": "Updated description",
  "amount": 1399.00,
  "offer_amount": 699.00,
  "max_tokens": 200
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "course": { "id": 2, "course_name": "NEET Updated", ... }
  },
  "message": "Course updated successfully"
}
```

### 8. Admin: Delete Course
**Endpoint:** `DELETE /api/admin/courses/<course_id>`
**Authentication:** Admin JWT Required

**Response:**
```json
{
  "success": true,
  "data": {
    "message": "Course deleted successfully"
  },
  "message": "Course deleted successfully"
}
```

### 9. Admin: Add Subject
**Endpoint:** `POST /api/admin/subjects`
**Authentication:** Admin JWT Required

**Request:**
```json
{
  "course_id": 1,
  "subject_name": "Chemistry",
  "amount": 299.00,
  "offer_amount": 149.00,
  "max_tokens": 50,
  "total_mock": 25,
  "is_bundle": false
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "subject": {
      "id": 2,
      "exam_category_id": 1,
      "subject_name": "Chemistry",
      "amount": 299.00,
      "offer_amount": 149.00,
      "max_tokens": 50,
      "total_mock": 25,
      "is_bundle": false,
      "is_deleted": false,
      "created_at": "2024-01-15T10:30:00"
    }
  },
  "message": "Subject added successfully"
}
```

### 10. Admin: Edit Subject
**Endpoint:** `PUT /api/admin/subjects/<subject_id>`
**Authentication:** Admin JWT Required

**Request:**
```json
{
  "subject_name": "Chemistry Updated",
  "amount": 349.00,
  "offer_amount": 174.00,
  "max_tokens": 60,
  "total_mock": 30,
  "is_bundle": false,
  "is_deleted": false
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "subject": { "id": 2, "subject_name": "Chemistry Updated", ... }
  },
  "message": "Subject updated successfully"
}
```

### 11. Admin: Delete Subject
**Endpoint:** `DELETE /api/admin/subjects/<subject_id>`
**Authentication:** Admin JWT Required

**Response:**
```json
{
  "success": true,
  "data": {
    "message": "Subject deleted successfully",
    "subject_id": 2,
    "subject_name": "Chemistry"
  },
  "message": "Subject deleted successfully"
}
```

---

## Community & Blog Endpoints

### 1. Get Community Posts
**Endpoint:** `GET /api/community/posts`
**Authentication:** None (Optional for like status)
**Query Params:** `page=1&per_page=10&search=tips&tags=jee&featured=true`

**Response:**
```json
{
  "success": true,
  "data": {
    "posts": [
      {
        "id": 1,
        "title": "Tips for JEE Preparation",
        "content": "Here are some tips...",
        "tags": "jee,preparation,tips",
        "image_url": "https://...",
        "likes_count": 45,
        "comments_count": 12,
        "is_featured": true,
        "is_liked": false,
        "recent_comments": [
          {
            "id": 1,
            "content": "Great tips!",
            "user": { "id": 2, "name": "Jane Doe" },
            "created_at": "2024-01-15T10:30:00"
          }
        ],
        "user": { "id": 1, "name": "John Doe" },
        "created_at": "2024-01-15T10:00:00"
      }
    ],
    "pagination": { "page": 1, "pages": 5, "per_page": 10, "total": 50 }
  },
  "message": "Posts retrieved successfully"
}
```

### 2. Get Post Comments
**Endpoint:** `GET /api/community/posts/<post_id>/comments`
**Authentication:** None
**Query Params:** `page=1&per_page=20`

**Response:**
```json
{
  "success": true,
  "data": {
    "comments": [
      {
        "id": 1,
        "content": "Great post!",
        "user": { "id": 2, "name": "Jane Doe" },
        "created_at": "2024-01-15T10:30:00",
        "replies": []
      }
    ],
    "pagination": { "page": 1, "pages": 1, "per_page": 20, "total": 5 }
  },
  "message": "Comments retrieved successfully"
}
```

### 3. Create Blog Post
**Endpoint:** `POST /api/community/posts`
**Authentication:** JWT Required

**Request (JSON):**
```json
{
  "title": "My Study Tips",
  "content": "Here are my study tips...",
  "tags": "study,tips,preparation"
}
```

**Request (Form Data with Image):**
```
title: "My Study Tips"
content: "Here are my study tips..."
tags: "study,tips,preparation"
image: <file>
```

**Response:**
```json
{
  "success": true,
  "data": {
    "post": {
      "id": 2,
      "title": "My Study Tips",
      "content": "Here are my study tips...",
      "tags": "study,tips,preparation",
      "image_url": "https://api.example.com/assets/images/post_2_abc123.jpg",
      "status": "published",
      "likes_count": 0,
      "comments_count": 0,
      "user_id": 1,
      "created_at": "2024-01-15T11:00:00"
    }
  },
  "message": "Post created successfully"
}
```

### 4. Like Post
**Endpoint:** `POST /api/community/posts/<post_id>/like`
**Authentication:** JWT Required

**Response:**
```json
{
  "success": true,
  "data": {
    "post_id": 1,
    "is_liked": true,
    "likes_count": 46
  },
  "message": "Post liked successfully"
}
```

### 5. Add Comment
**Endpoint:** `POST /api/community/posts/<post_id>/comment`
**Authentication:** JWT Required

**Request:**
```json
{
  "content": "Great post! Very helpful.",
  "parent_comment_id": null
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "comment": {
      "id": 2,
      "post_id": 1,
      "content": "Great post! Very helpful.",
      "user_id": 1,
      "parent_comment_id": null,
      "created_at": "2024-01-15T11:05:00"
    }
  },
  "message": "Comment added successfully"
}
```

### 6. Delete Comment
**Endpoint:** `DELETE /api/community/comments/<comment_id>`
**Authentication:** JWT Required

**Response:**
```json
{
  "success": true,
  "data": {
    "message": "Comment deleted successfully"
  },
  "message": "Comment deleted successfully"
}
```

### 7. Delete Post
**Endpoint:** `DELETE /api/community/posts/<post_id>`
**Authentication:** JWT Required

**Response:**
```json
{
  "success": true,
  "data": {
    "message": "Post deleted successfully"
  },
  "message": "Post deleted successfully"
}
```

### 8. Admin: Get All Posts
**Endpoint:** `GET /api/admin/posts`
**Authentication:** Admin JWT Required
**Query Params:** `page=1&per_page=50&status=published`

**Response:**
```json
{
  "success": true,
  "data": {
    "posts": [
      {
        "id": 1,
        "title": "Tips for JEE Preparation",
        "content": "Here are some tips...",
        "status": "published",
        "is_deleted": false,
        "user": { "id": 1, "name": "John Doe" },
        "created_at": "2024-01-15T10:00:00"
      }
    ],
    "pagination": { "page": 1, "pages": 1, "per_page": 50, "total": 10 }
  },
  "message": "Posts retrieved successfully"
}
```

### 9. Admin: Edit Post
**Endpoint:** `PUT /api/admin/posts/<post_id>`
**Authentication:** Admin JWT Required

**Request:**
```json
{
  "title": "Updated Title",
  "content": "Updated content",
  "tags": "updated,tags",
  "status": "published",
  "is_featured": true
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "post": { "id": 1, "title": "Updated Title", ... }
  },
  "message": "Post updated successfully"
}
```

### 10. Admin: Delete Post
**Endpoint:** `DELETE /api/admin/posts/<post_id>`
**Authentication:** Admin JWT Required

**Response:**
```json
{
  "success": true,
  "data": {
    "message": "Post deleted successfully"
  },
  "message": "Post deleted successfully"
}
```

### 11. Admin: Get Comments
**Endpoint:** `GET /api/admin/comments`
**Authentication:** Admin JWT Required
**Query Params:** `page=1&per_page=50`

**Response:**
```json
{
  "success": true,
  "data": {
    "comments": [
      {
        "id": 1,
        "content": "Great post!",
        "post_id": 1,
        "user": { "id": 2, "name": "Jane Doe" },
        "is_deleted": false,
        "created_at": "2024-01-15T10:30:00"
      }
    ],
    "pagination": { "page": 1, "pages": 1, "per_page": 50, "total": 5 }
  },
  "message": "Comments retrieved successfully"
}
```

### 12. Admin: Edit Comment
**Endpoint:** `PUT /api/admin/comments/<comment_id>`
**Authentication:** Admin JWT Required

**Request:**
```json
{
  "content": "Updated comment content"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "comment": { "id": 1, "content": "Updated comment content", ... }
  },
  "message": "Comment updated successfully"
}
```

### 13. Admin: Delete Comment
**Endpoint:** `DELETE /api/admin/comments/<comment_id>`
**Authentication:** Admin JWT Required

**Response:**
```json
{
  "success": true,
  "data": {
    "message": "Comment deleted successfully"
  },
  "message": "Comment deleted successfully"
}
```

---

## AI Features Endpoints

### 1. Get AI Token Status
**Endpoint:** `GET /api/ai/token-status`
**Authentication:** JWT Required

**Response:**
```json
{
  "success": true,
  "data": {
    "user_id": 1,
    "total_tokens": 100,
    "used_tokens": 25,
    "remaining_tokens": 75,
    "token_limit": 100,
    "purchases": [
      {
        "id": 1,
        "subject_name": "Physics",
        "tokens_purchased": 100,
        "tokens_used": 25,
        "tokens_remaining": 75,
        "purchase_date": "2024-01-10T10:00:00"
      }
    ]
  },
  "message": "Token status retrieved successfully"
}
```

### 2. AI Chat (Backward Compatibility)
**Endpoint:** `POST /api/ai/chat`
**Authentication:** JWT Required

**Request:**
```json
{
  "message": "What is Newton's first law of motion?",
  "subject": "physics",
  "conversation_id": "conv_123"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "response": "Newton's first law of motion states that an object at rest stays at rest...",
    "conversation_id": "conv_123",
    "tokens_used": 5,
    "tokens_remaining": 70,
    "sources": [
      {
        "title": "Physics Textbook Chapter 3",
        "relevance": 0.95
      }
    ]
  },
  "message": "Response generated successfully"
}
```

### 3. Generate MCQ
**Endpoint:** `POST /api/mcq/generate`
**Authentication:** JWT Required

**Request:**
```json
{
  "subject": "physics",
  "num_questions": 10,
  "difficulty": "medium",
  "topics": ["mechanics", "thermodynamics"]
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "generation_batch_id": "batch_123",
    "questions": [
      {
        "id": 1,
        "question": "What is the SI unit of force?",
        "option_a": "Newton",
        "option_b": "Joule",
        "option_c": "Watt",
        "option_d": "Pascal",
        "correct_answer": "Newton",
        "explanation": "The SI unit of force is Newton...",
        "ai_model_used": "llava",
        "difficulty": "easy"
      }
    ],
    "total_questions": 10,
    "tokens_used": 15,
    "tokens_remaining": 55
  },
  "message": "MCQ generated successfully"
}
```

### 4. Chatbot Query
**Endpoint:** `POST /api/chatbot/query`
**Authentication:** JWT Required

**Request:**
```json
{
  "query": "Explain photosynthesis",
  "subjects": ["biology", "chemistry"],
  "include_images": true
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "answer": "Photosynthesis is the process by which plants convert light energy...",
    "sources": [
      {
        "type": "text",
        "title": "Biology Textbook",
        "relevance": 0.98
      },
      {
        "type": "image",
        "url": "https://...",
        "relevance": 0.92
      }
    ],
    "tokens_used": 8,
    "tokens_remaining": 47
  },
  "message": "Query answered successfully"
}
```

---

## Test & MCQ Endpoints

### 1. Get User Test Cards
**Endpoint:** `GET /api/user/test-cards`
**Authentication:** JWT Required

**Response:**
```json
{
  "success": true,
  "data": {
    "test_cards": [
      {
        "id": 1,
        "subject_name": "Physics",
        "course_name": "JEE Main",
        "total_questions": 50,
        "duration_minutes": 60,
        "attempts": 2,
        "best_score": 85,
        "last_attempt_score": 82,
        "last_attempt_date": "2024-01-14T15:30:00",
        "can_reattempt": true,
        "status": "completed"
      }
    ]
  },
  "message": "Test cards retrieved successfully"
}
```

### 2. Get Test Instructions
**Endpoint:** `POST /api/user/test-cards/<mock_test_id>/instructions`
**Authentication:** JWT Required

**Response:**
```json
{
  "success": true,
  "data": {
    "mock_test_id": 1,
    "subject_name": "Physics",
    "total_questions": 50,
    "duration_minutes": 60,
    "instructions": "Read each question carefully...",
    "generation_batch_id": "batch_456",
    "generation_status": "in_progress",
    "initial_questions_ready": 5,
    "total_questions_generated": 5
  },
  "message": "Test instructions retrieved"
}
```

### 3. Poll Generation Status
**Endpoint:** `GET /api/user/test-cards/<mock_test_id>/generation-status`
**Authentication:** JWT Required

**Response:**
```json
{
  "success": true,
  "data": {
    "mock_test_id": 1,
    "generation_batch_id": "batch_456",
    "status": "completed",
    "total_questions_generated": 50,
    "progress_percentage": 100,
    "initial_questions": [
      {
        "id": 1,
        "question": "What is the SI unit of force?",
        "option_a": "Newton",
        "option_b": "Joule",
        "option_c": "Watt",
        "option_d": "Pascal",
        "correct_answer": "Newton"
      }
    ]
  },
  "message": "Generation status retrieved"
}
```

### 4. Start Mock Test
**Endpoint:** `POST /api/user/test-cards/<mock_test_id>/start`
**Authentication:** JWT Required

**Response:**
```json
{
  "success": true,
  "data": {
    "session_id": 1,
    "mock_test_id": 1,
    "subject_name": "Physics",
    "total_questions": 50,
    "duration_minutes": 60,
    "start_time": "2024-01-15T14:00:00",
    "end_time": "2024-01-15T15:00:00"
  },
  "message": "Test started successfully"
}
```

### 5. Get Test Questions
**Endpoint:** `GET /api/user/test-sessions/<session_id>/questions`
**Authentication:** JWT Required
**Query Params:** `page=1&per_page=10`

**Response:**
```json
{
  "success": true,
  "data": {
    "session_id": 1,
    "questions": [
      {
        "id": 1,
        "question": "What is the SI unit of force?",
        "option_a": "Newton",
        "option_b": "Joule",
        "option_c": "Watt",
        "option_d": "Pascal",
        "explanation": "The SI unit of force is Newton..."
      }
    ],
    "pagination": { "page": 1, "pages": 5, "per_page": 10, "total": 50 }
  },
  "message": "Questions retrieved successfully"
}
```

### 6. Submit Test
**Endpoint:** `POST /api/user/test-sessions/<session_id>/submit`
**Authentication:** JWT Required

**Request:**
```json
{
  "answers": [
    {
      "question_id": 1,
      "selected_answer": "Newton"
    },
    {
      "question_id": 2,
      "selected_answer": "3 × 10⁸ m/s"
    }
  ]
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "session_id": 1,
    "total_questions": 50,
    "correct_answers": 42,
    "incorrect_answers": 8,
    "score": 84,
    "percentage": 84.0,
    "time_taken_seconds": 3600,
    "result_details": [
      {
        "question_id": 1,
        "question": "What is the SI unit of force?",
        "selected_answer": "Newton",
        "correct_answer": "Newton",
        "is_correct": true,
        "explanation": "The SI unit of force is Newton..."
      }
    ],
    "submitted_at": "2024-01-15T15:00:00"
  },
  "message": "Test submitted successfully"
}
```

### 7. Get Test Analytics
**Endpoint:** `GET /api/user/test-analytics`
**Authentication:** JWT Required

**Response:**
```json
{
  "success": true,
  "data": {
    "total_tests_attempted": 5,
    "average_score": 78.5,
    "best_score": 92,
    "worst_score": 65,
    "total_time_spent_hours": 5.5,
    "subject_wise_performance": [
      {
        "subject": "Physics",
        "attempts": 2,
        "average_score": 82,
        "best_score": 88
      },
      {
        "subject": "Chemistry",
        "attempts": 3,
        "average_score": 76,
        "best_score": 85
      }
    ]
  },
  "message": "Analytics retrieved successfully"
}
```

---

## Purchase Endpoints

### 1. Create Purchase
**Endpoint:** `POST /api/purchases`
**Authentication:** JWT Required

**Request:**
```json
{
  "exam_category_id": 1,
  "exam_category_subject_id": 1,
  "amount": 299.00,
  "payment_method": "razorpay",
  "transaction_id": "txn_123456"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "purchase_id": 1,
    "user_id": 1,
    "exam_category_id": 1,
    "exam_category_subject_id": 1,
    "amount": 299.00,
    "tokens_purchased": 50,
    "status": "completed",
    "purchase_date": "2024-01-15T14:30:00"
  },
  "message": "Purchase created successfully"
}
```

### 2. Get User Purchases
**Endpoint:** `GET /api/purchases` or `GET /api/user/purchases`
**Authentication:** JWT Required

**Response:**
```json
{
  "success": true,
  "data": {
    "purchases": [
      {
        "id": 1,
        "exam_category_id": 1,
        "course_name": "JEE Main",
        "subject_name": "Physics",
        "amount": 299.00,
        "tokens_purchased": 50,
        "tokens_used": 15,
        "tokens_remaining": 35,
        "status": "completed",
        "purchase_date": "2024-01-10T10:00:00"
      }
    ]
  },
  "message": "Purchases retrieved successfully"
}
```

---

## User Profile Endpoints

### 1. Get User Profile
**Endpoint:** `GET /api/user/profile`
**Authentication:** JWT Required

**Response:**
```json
{
  "success": true,
  "data": {
    "user": {
      "id": 1,
      "email_id": "user@example.com",
      "name": "John Doe",
      "mobile_no": "9876543210",
      "status": "active",
      "color_theme": "light",
      "avatar": "https://...",
      "gender": "male",
      "date_of_birth": "1995-05-15",
      "city": "Mumbai",
      "state": "Maharashtra",
      "address": "123 Main St",
      "created_at": "2024-01-01T10:00:00"
    }
  },
  "message": "User profile retrieved successfully"
}
```

### 2. Update User Profile
**Endpoint:** `PATCH /api/user/profile`
**Authentication:** JWT Required

**Request:**
```json
{
  "name": "John Doe Updated",
  "mobile_no": "9876543210",
  "color_theme": "dark",
  "avatar": "https://...",
  "gender": "male",
  "date_of_birth": "1995-05-15",
  "city": "Mumbai",
  "state": "Maharashtra",
  "address": "123 Main St"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "user": { "id": 1, "name": "John Doe Updated", ... }
  },
  "message": "Profile updated successfully"
}
```

### 3. Get User Stats
**Endpoint:** `GET /api/user/stats`
**Authentication:** JWT Required

**Response:**
```json
{
  "success": true,
  "data": {
    "stats": {
      "user_id": 1,
      "total_tests_attempted": 5,
      "average_score": 78.5,
      "best_score": 92,
      "worst_score": 65,
      "total_time_spent_hours": 5.5,
      "last_test_date": "2024-01-14T15:30:00"
    }
  },
  "message": "User stats retrieved successfully"
}
```

### 4. Get User Academics
**Endpoint:** `GET /api/user/academics`
**Authentication:** JWT Required

**Response:**
```json
{
  "success": true,
  "data": {
    "academics": {
      "user_id": 1,
      "board": "CBSE",
      "class": "12",
      "school_name": "ABC School",
      "target_exam": "JEE Main",
      "target_year": 2024,
      "preferred_subjects": ["Physics", "Chemistry", "Mathematics"]
    }
  },
  "message": "User academics retrieved successfully"
}
```

### 5. Update User Academics
**Endpoint:** `PATCH /api/user/academics`
**Authentication:** JWT Required

**Request:**
```json
{
  "board": "CBSE",
  "class": "12",
  "school_name": "ABC School",
  "target_exam": "JEE Main",
  "target_year": 2024,
  "preferred_subjects": ["Physics", "Chemistry", "Mathematics"]
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "academics": { "user_id": 1, "board": "CBSE", ... }
  },
  "message": "Academic information updated successfully"
}
```

---

## Admin Management Endpoints

### 1. Get All Users
**Endpoint:** `GET /api/admin/users`
**Authentication:** Admin JWT Required
**Query Params:** `page=1&per_page=50&search=john&status=active`

**Response:**
```json
{
  "success": true,
  "data": {
    "users": [
      {
        "id": 1,
        "email_id": "user@example.com",
        "name": "John Doe",
        "status": "active",
        "created_at": "2024-01-01T10:00:00",
        "last_login": "2024-01-15T14:30:00"
      }
    ],
    "pagination": { "page": 1, "pages": 10, "per_page": 50, "total": 500 }
  },
  "message": "Users retrieved successfully"
}
```

### 2. Deactivate User
**Endpoint:** `PUT /api/admin/users/<user_id>/deactivate`
**Authentication:** Admin JWT Required

**Response:**
```json
{
  "success": true,
  "data": {
    "user_id": 1,
    "status": "inactive",
    "message": "User account deactivated"
  },
  "message": "User deactivated successfully"
}
```

### 3. Get User Purchases (Admin)
**Endpoint:** `GET /api/admin/users/<user_id>/purchases`
**Authentication:** Admin JWT Required

**Response:**
```json
{
  "success": true,
  "data": {
    "user_id": 1,
    "purchases": [
      {
        "id": 1,
        "course_name": "JEE Main",
        "subject_name": "Physics",
        "amount": 299.00,
        "tokens_purchased": 50,
        "purchase_date": "2024-01-10T10:00:00"
      }
    ]
  },
  "message": "User purchases retrieved successfully"
}
```

### 4. Get Admin Statistics
**Endpoint:** `GET /api/admin/stats`
**Authentication:** Admin JWT Required

**Response:**
```json
{
  "success": true,
  "data": {
    "total_users": 500,
    "active_users": 450,
    "inactive_users": 50,
    "total_revenue": 125000.00,
    "total_purchases": 250,
    "total_tests_attempted": 1500,
    "average_test_score": 75.5,
    "total_blog_posts": 50,
    "total_comments": 200,
    "courses_count": 5,
    "subjects_count": 15
  },
  "message": "Admin statistics retrieved successfully"
}
```

### 5. Get Questions
**Endpoint:** `GET /api/questions`
**Authentication:** JWT Required
**Query Params:** `page=1&per_page=10&subject=Physics&course_id=1`

**Response:**
```json
{
  "success": true,
  "data": {
    "questions": [
      {
        "id": 1,
        "question": "What is the SI unit of force?",
        "option_a": "Newton",
        "option_b": "Joule",
        "option_c": "Watt",
        "option_d": "Pascal",
        "correct_answer": "Newton",
        "subject": "Physics",
        "difficulty": "easy"
      }
    ],
    "pagination": { "page": 1, "pages": 10, "per_page": 10, "total": 100 }
  },
  "message": "Questions retrieved successfully"
}
```

### 6. Admin: Create Question
**Endpoint:** `POST /api/admin/questions`
**Authentication:** Admin JWT Required

**Request:**
```json
{
  "exam_category_id": 1,
  "exam_category_subject_id": 1,
  "question": "What is the SI unit of force?",
  "option_a": "Newton",
  "option_b": "Joule",
  "option_c": "Watt",
  "option_d": "Pascal",
  "correct_answer": "Newton",
  "explanation": "The SI unit of force is Newton...",
  "difficulty": "easy"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "question": {
      "id": 1,
      "question": "What is the SI unit of force?",
      "correct_answer": "Newton",
      "difficulty": "easy",
      "created_at": "2024-01-15T14:30:00"
    }
  },
  "message": "Question created successfully"
}
```

### 7. Admin: Update Question
**Endpoint:** `PUT /api/admin/questions/<question_id>`
**Authentication:** Admin JWT Required

**Request:**
```json
{
  "question": "Updated question text",
  "option_a": "Updated option A",
  "correct_answer": "Updated option A",
  "difficulty": "medium"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "question": { "id": 1, "question": "Updated question text", ... }
  },
  "message": "Question updated successfully"
}
```

### 8. Admin: Delete Question
**Endpoint:** `DELETE /api/admin/questions/<question_id>`
**Authentication:** Admin JWT Required

**Response:**
```json
{
  "success": true,
  "data": {
    "message": "Question deleted successfully"
  },
  "message": "Question deleted successfully"
}
```

### 9. Admin: Bulk Delete Questions
**Endpoint:** `POST /api/admin/questions/bulk-delete`
**Authentication:** Admin JWT Required

**Request:**
```json
{
  "question_ids": [1, 2, 3, 4, 5]
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "deleted_count": 5,
    "message": "5 questions deleted successfully"
  },
  "message": "Questions deleted successfully"
}
```

---

## Ollama Integration Endpoints

### 1. Check Ollama Health
**Endpoint:** `GET /api/ollama/health`
**Authentication:** None

**Response:**
```json
{
  "success": true,
  "data": {
    "ollama_status": "running",
    "server_url": "http://localhost:11434",
    "models_available": 3,
    "models": [
      {
        "name": "llava",
        "size": "4.7GB",
        "status": "loaded"
      },
      {
        "name": "qwen2-vl",
        "size": "8.2GB",
        "status": "available"
      }
    ]
  },
  "message": "Ollama server is healthy"
}
```

### 2. Get Available Models
**Endpoint:** `GET /api/ollama/models`
**Authentication:** None

**Response:**
```json
{
  "success": true,
  "data": {
    "models": [
      {
        "name": "llava",
        "size": "4.7GB",
        "modified_at": "2024-01-15T10:00:00"
      },
      {
        "name": "qwen2-vl",
        "size": "8.2GB",
        "modified_at": "2024-01-14T15:30:00"
      }
    ]
  },
  "message": "Models retrieved successfully"
}
```

### 3. Check Specific Model
**Endpoint:** `GET /api/ollama/model/<model_name>/check`
**Authentication:** None

**Response:**
```json
{
  "success": true,
  "data": {
    "model_name": "llava",
    "is_available": true,
    "size": "4.7GB",
    "status": "loaded"
  },
  "message": "Model is available"
}
```

---

## Vector Store Management (Admin Only)

### 1. Get Vector Store Status
**Endpoint:** `GET /api/admin/vector-store/status`
**Authentication:** Admin JWT Required

**Response:**
```json
{
  "success": true,
  "data": {
    "total_subjects": 5,
    "initialized_subjects": 4,
    "vector_store_stats": [
      {
        "subject": "Physics",
        "documents_count": 150,
        "embeddings_count": 150,
        "status": "initialized"
      }
    ]
  },
  "message": "Vector store status retrieved successfully"
}
```

### 2. Initialize Vector Stores
**Endpoint:** `POST /api/admin/vector-store/initialize`
**Authentication:** Admin JWT Required

**Request:**
```json
{
  "subjects": ["Physics", "Chemistry", "Biology"]
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "successful": 3,
    "failed": 0,
    "results": [
      {
        "subject": "Physics",
        "status": "success",
        "documents_indexed": 150
      }
    ]
  },
  "message": "Vector store initialization completed: 3/3 subjects successful"
}
```

### 3. Reset Vector Stores
**Endpoint:** `POST /api/admin/vector-store/reset`
**Authentication:** Admin JWT Required

**Request:**
```json
{
  "confirm": true
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "message": "All vector stores have been reset successfully"
  },
  "message": "Vector stores reset successfully"
}
```

### 4. Reindex Subject Vector Store
**Endpoint:** `POST /api/admin/vector-store/subject/<subject>/reindex`
**Authentication:** Admin JWT Required

**Response:**
```json
{
  "success": true,
  "data": {
    "subject": "Physics",
    "documents_indexed": 150,
    "status": "success"
  },
  "message": "Vector store reindexed successfully for Physics"
}
```

### 5. Get Vector Store Performance
**Endpoint:** `GET /api/admin/vector-store/performance`
**Authentication:** Admin JWT Required

**Response:**
```json
{
  "success": true,
  "data": {
    "performance_metrics": {
      "average_query_time_ms": 45.5,
      "total_queries": 1000,
      "cache_hit_rate": 0.75,
      "subjects_performance": [
        {
          "subject": "Physics",
          "avg_query_time_ms": 42.3,
          "queries_count": 300
        }
      ]
    }
  },
  "message": "Performance metrics retrieved successfully"
}
```

---

## Google OAuth (Legacy)

### 1. Get Google Auth URL
**Endpoint:** `GET /auth/google`
**Authentication:** None

**Response:**
```json
{
  "success": true,
  "data": {
    "auth_url": "https://accounts.google.com/o/oauth2/v2/auth?client_id=..."
  },
  "message": "Google authorization URL generated"
}
```

### 2. Verify Google OAuth
**Endpoint:** `POST /api/auth/google/verify`
**Authentication:** None

**Request:**
```json
{
  "code": "authorization_code_from_google"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "access_token": "jwt_access_token...",
    "refresh_token": "jwt_refresh_token...",
    "user": {
      "id": 1,
      "email_id": "user@gmail.com",
      "name": "John Doe",
      "google_id": "google_user_id"
    }
  },
  "message": "Google OAuth verification successful"
}
```

---

## Error Responses

All endpoints return error responses in the following format:

```json
{
  "success": false,
  "error": "Error message",
  "status_code": 400
}
```

### Common Error Codes:
- **400**: Bad Request - Invalid input data
- **401**: Unauthorized - Missing or invalid JWT token
- **403**: Forbidden - Insufficient permissions (not admin)
- **404**: Not Found - Resource not found
- **409**: Conflict - Resource already exists
- **500**: Internal Server Error - Server error

### Validation Error Response:
```json
{
  "success": false,
  "errors": {
    "email": "Invalid email format",
    "mobile_no": "Invalid mobile number format"
  },
  "status_code": 400
}
```

---

## Authentication Headers

All authenticated endpoints require:

```
Authorization: Bearer <access_token>
```

---

## Notes

- All timestamps are in ISO 8601 format (UTC)
- All monetary values are in INR (Indian Rupees)
- JWT tokens expire after configured duration
- Refresh tokens are stored in database for validation
- All endpoints support CORS
- Content-Type should be `application/json` for JSON requests
- File uploads use `multipart/form-data`


