# 🤖 AI Features Guide - Jishu Backend

This guide covers the AI-powered features integrated into the Jishu Backend, including Ollama integration, RAG (Retrieval-Augmented Generation), and automated question generation.

## 🚀 Overview

The AI service provides:
- **Question Generation**: Create MCQs from text content or PDF documents
- **RAG Chat**: Chat with AI using PDF documents as context
- **Ollama Integration**: Local AI model for question generation and chat
- **PDF Processing**: Extract and index content from educational PDFs

## 📋 Prerequisites

### Required Dependencies
```bash
pip install ollama sentence-transformers PyPDF2 numpy torch transformers
```

### Ollama Setup
1. Install Ollama: https://ollama.ai/
2. Pull the required model:
```bash
ollama pull llama3.2:1b
```

### PDF Documents
- Place educational PDF files in the `pdfs/` directory
- Organize by subject in subdirectories for better results

## 🔧 Configuration

### Environment Variables
Add to your `.env` file:
```env
AI_PDF_FOLDER=./pdfs
AI_OLLAMA_MODEL=llama3.2:1b
AI_MAX_CONTENT_LENGTH=8000
AI_DEFAULT_QUESTIONS_COUNT=5
AI_SIMILARITY_THRESHOLD=0.1
AI_RAG_TOP_K=3
```

### Database Migration
Run the migration script to add AI-related fields:
```sql
-- Run add_ai_question_fields.sql
mysql -u root -p jishu_app < add_ai_question_fields.sql
```

## 📚 API Endpoints

### 1. Question Generation from Text

**Endpoint**: `POST /api/ai/generate-questions-from-text`
**Auth**: Admin required
**Description**: Generate MCQs from provided text content

**Request Body**:
```json
{
  "content": "Your educational content here...",
  "num_questions": 5,
  "subject_name": "Mathematics",
  "difficulty": "medium",
  "exam_category_id": 1,
  "subject_id": 1,
  "save_to_database": true
}
```

**Response**:
```json
{
  "success": true,
  "data": {
    "questions": [
      {
        "question": "What is the derivative of x²?",
        "option_a": "2x",
        "option_b": "x²",
        "option_c": "2",
        "option_d": "x",
        "correct_option": "A",
        "explanation": "The derivative of x² is 2x using the power rule."
      }
    ],
    "total_generated": 5,
    "model_used": "llama3.2:1b",
    "saved_to_database": true,
    "saved_count": 5
  },
  "message": "Questions generated successfully"
}
```

### 2. Question Generation from PDFs

**Endpoint**: `POST /api/ai/generate-questions-from-pdfs`
**Auth**: Admin required
**Description**: Generate MCQs from PDF documents in the pdfs folder

**Request Body**:
```json
{
  "num_questions": 5,
  "subject_name": "Physics",
  "difficulty": "hard",
  "exam_category_id": 2,
  "subject_id": 3,
  "save_to_database": true
}
```

**Response**:
```json
{
  "success": true,
  "data": {
    "questions": [...],
    "sources_used": ["physics_chapter1.pdf", "mechanics.pdf"],
    "total_pdfs_processed": 5,
    "total_generated": 5
  },
  "message": "Questions generated from PDFs successfully"
}
```

### 3. RAG Chat

**Endpoint**: `POST /api/ai/rag/chat`
**Auth**: User required
**Description**: Chat with AI using PDF documents as context

**Request Body**:
```json
{
  "query": "Explain Newton's laws of motion",
  "session_id": "optional-session-id"
}
```

**Response**:
```json
{
  "success": true,
  "data": {
    "response": "Newton's laws of motion are three fundamental principles...",
    "sources": ["physics_fundamentals.pdf"],
    "relevant_docs": 2,
    "tokens_used": 45,
    "session_id": "session-123"
  },
  "message": "RAG response generated successfully"
}
```

### 4. RAG Status

**Endpoint**: `GET /api/ai/rag/status`
**Auth**: Public
**Description**: Check RAG system status and loaded documents

**Response**:
```json
{
  "success": true,
  "data": {
    "status": "running",
    "dependencies": {
      "sentence_transformers": true,
      "PyPDF2": true,
      "ollama": true,
      "numpy": true
    },
    "pdf_folder": "./pdfs",
    "pdfs_loaded": 10,
    "sources": ["math.pdf", "physics.pdf", "..."]
  }
}
```

### 5. Question Management

**List Questions**: `GET /api/questions`
- Query params: `page`, `per_page`, `exam_category_id`, `subject_id`

**Get Question**: `GET /api/questions/<id>`

**Create Question**: `POST /api/admin/questions` (Admin)

**Update Question**: `PUT /api/admin/questions/<id>` (Admin)

**Delete Question**: `DELETE /api/admin/questions/<id>` (Admin)

**Bulk Delete**: `POST /api/admin/questions/bulk-delete` (Admin)

## 🗂️ Database Schema Updates

New fields added to `exam_category_questions` table:
- `is_ai_generated`: Boolean flag for AI-generated questions
- `ai_model_used`: Model name used for generation
- `difficulty_level`: Question difficulty (easy/medium/hard)
- `source_content`: Original content used for generation

## 📁 Directory Structure

```
jishu_backend/
├── pdfs/                          # PDF documents for RAG
│   ├── subjects/
│   │   ├── mathematics/
│   │   ├── physics/
│   │   ├── chemistry/
│   │   └── ...
│   └── general/
├── shared/
│   └── services/
│       └── ai_service.py          # AI service implementation
└── add_ai_question_fields.sql     # Database migration
```

## 🔍 Usage Examples

### 1. Generate Questions from Text
```bash
curl -X POST http://localhost:5000/api/ai/generate-questions-from-text \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "Photosynthesis is the process by which plants convert light energy into chemical energy...",
    "num_questions": 3,
    "subject_name": "Biology",
    "difficulty": "medium",
    "save_to_database": true
  }'
```

### 2. Chat with RAG
```bash
curl -X POST http://localhost:5000/api/ai/rag/chat \
  -H "Authorization: Bearer YOUR_USER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What are the main types of chemical bonds?"
  }'
```

## 🚨 Troubleshooting

### Common Issues

1. **Ollama not available**: Ensure Ollama is installed and running
2. **Model not found**: Pull the required model with `ollama pull llama3.2:1b`
3. **PDF processing fails**: Check if PyPDF2 is installed and PDFs are readable
4. **Embeddings error**: Ensure sentence-transformers is properly installed

### Performance Tips

1. **PDF Organization**: Organize PDFs by subject for better question generation
2. **Content Length**: Keep text content under 8000 characters for optimal results
3. **Model Selection**: Use smaller models (1b) for faster generation, larger for quality
4. **Batch Processing**: Generate multiple questions in single requests

## 🔒 Security Considerations

- Question generation endpoints require admin privileges
- RAG chat is available to all authenticated users
- PDF content is cached in memory - restart to clear sensitive data
- AI responses are logged in chat history

## 📈 Monitoring

- Check AI usage statistics via `/api/admin/chat/tokens`
- Monitor PDF loading status via `/api/ai/rag/status`
- Track question generation in database with AI flags
