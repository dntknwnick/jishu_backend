# Multimodal RAG System - Deployment Checklist

## Pre-Deployment Verification

### System Requirements
- [ ] Python 3.8+ installed
- [ ] MySQL 8.0+ running
- [ ] Ollama installed and running
- [ ] GPU available (recommended)
- [ ] Minimum 8GB RAM
- [ ] Minimum 10GB disk space

### Dependencies
- [ ] All Python packages installed: `pip install -r requirements.txt`
- [ ] PyTorch installed: `pip install torch torchvision`
- [ ] ChromaDB installed: `pip install chromadb`
- [ ] Transformers installed: `pip install transformers`
- [ ] PyMuPDF installed: `pip install pymupdf`
- [ ] Ollama client installed: `pip install ollama`

### Ollama Setup
- [ ] Ollama service running: `ollama serve`
- [ ] Qwen2-VL model pulled: `ollama pull qwen2-vl:2b`
- [ ] Model verified: `ollama list` (should show qwen2-vl:2b)
- [ ] Ollama accessible at http://localhost:11434

---

## Configuration Setup

### Environment Variables
- [ ] Copy `.env.multimodal.example` to `.env`
- [ ] Update `MYSQL_HOST` with correct host
- [ ] Update `MYSQL_USER` with correct username
- [ ] Update `MYSQL_PASSWORD` with correct password
- [ ] Update `MYSQL_DB` with correct database name
- [ ] Update `JWT_SECRET_KEY` with secure key
- [ ] Update `GOOGLE_CLIENT_ID` if using OAuth
- [ ] Update `GOOGLE_CLIENT_SECRET` if using OAuth
- [ ] Verify `MULTIMODAL_RAG_ENABLED=true`
- [ ] Verify `MULTIMODAL_CHROMADB_PATH` is writable
- [ ] Verify `MULTIMODAL_OLLAMA_MODEL=qwen2-vl:2b`

### Directory Structure
- [ ] Create `pdfs/subjects/` directory
- [ ] Create `pdfs/subjects/physics/` directory
- [ ] Create `pdfs/subjects/chemistry/` directory
- [ ] Create `pdfs/subjects/biology/` directory
- [ ] Create `pdfs/subjects/mathematics/` directory
- [ ] Create `pdfs/subjects/computer_science/` directory
- [ ] Create `chromadb_data/` directory (will be auto-created)
- [ ] Verify all directories are writable

### PDF Files
- [ ] Add physics PDFs to `pdfs/subjects/physics/`
- [ ] Add chemistry PDFs to `pdfs/subjects/chemistry/`
- [ ] Add biology PDFs to `pdfs/subjects/biology/`
- [ ] Add mathematics PDFs to `pdfs/subjects/mathematics/`
- [ ] Add computer science PDFs to `pdfs/subjects/computer_science/`
- [ ] Verify all PDFs are readable
- [ ] Verify PDFs contain extractable text/images

---

## Database Setup

### Migration
- [ ] Run migration script: `python migrate_add_multimodal_rag_fields.py`
- [ ] Verify migration completed successfully
- [ ] Check database for new columns:
  - [ ] `chromadb_collection`
  - [ ] `multimodal_source_type`
  - [ ] `image_references`
  - [ ] `clip_embedding_id`
  - [ ] `generation_method`

### Verification
- [ ] Connect to MySQL database
- [ ] Verify `exam_category_questions` table has new columns
- [ ] Verify no data loss in existing records
- [ ] Backup database before proceeding

---

## Multimodal RAG Initialization

### Collection Initialization
- [ ] Run initialization script: `python scripts/initialize_multimodal_rag.py`
- [ ] Verify script completed without errors
- [ ] Check `chromadb_data/` directory for collections
- [ ] Verify collections created for each subject:
  - [ ] physics
  - [ ] chemistry
  - [ ] biology
  - [ ] mathematics
  - [ ] computer_science

### Verification
- [ ] Check ChromaDB collections:
  ```bash
  python -c "
  import chromadb
  client = chromadb.PersistentClient(path='./chromadb_data')
  for c in client.list_collections():
      print(f'Collection: {c.name}, Documents: {c.count()}')
  "
  ```
- [ ] Verify each collection has documents
- [ ] Verify embeddings are stored

---

## Testing

### Unit Tests
- [ ] Run test script: `python scripts/test_multimodal_rag_system.py`
- [ ] Verify all tests pass
- [ ] Check MCQ generation works
- [ ] Check chat response generation works
- [ ] Verify response times are acceptable

### Manual Testing
- [ ] Start application: `python app.py`
- [ ] Test MCQ generation endpoint:
  ```bash
  curl -X POST http://localhost:5000/api/mcq/generate \
    -H "Authorization: Bearer TEST_TOKEN" \
    -H "Content-Type: application/json" \
    -d '{"subject": "physics", "num_questions": 3}'
  ```
- [ ] Test chat endpoint:
  ```bash
  curl -X POST http://localhost:5000/api/chatbot/query \
    -H "Authorization: Bearer TEST_TOKEN" \
    -H "Content-Type: application/json" \
    -d '{"query": "What is photosynthesis?", "subject": "biology"}'
  ```
- [ ] Verify responses are valid JSON
- [ ] Verify response times are acceptable
- [ ] Check application logs for errors

### Performance Testing
- [ ] MCQ generation time < 15 seconds
- [ ] Chat response time < 5 seconds
- [ ] No memory leaks after 100+ requests
- [ ] CPU usage reasonable (< 80%)
- [ ] Disk usage reasonable (< 50GB)

---

## Production Deployment

### Pre-Deployment
- [ ] All tests passing
- [ ] All configurations verified
- [ ] Database backed up
- [ ] PDFs verified
- [ ] Ollama model verified
- [ ] Team notified of deployment

### Deployment
- [ ] Deploy code to production server
- [ ] Copy `.env` file to production
- [ ] Run database migration on production
- [ ] Run initialization script on production
- [ ] Run tests on production
- [ ] Verify all endpoints working

### Post-Deployment
- [ ] Monitor application logs
- [ ] Monitor system resources (CPU, RAM, disk)
- [ ] Monitor response times
- [ ] Monitor error rates
- [ ] Verify user reports no issues
- [ ] Document any issues found

---

## Monitoring & Maintenance

### Daily Checks
- [ ] Application running without errors
- [ ] No unusual CPU/memory usage
- [ ] Response times normal
- [ ] No database errors
- [ ] ChromaDB collections accessible

### Weekly Checks
- [ ] Review application logs
- [ ] Check disk space usage
- [ ] Verify backup status
- [ ] Check for any performance degradation
- [ ] Review user feedback

### Monthly Checks
- [ ] Full system health check
- [ ] Performance optimization review
- [ ] Security audit
- [ ] Database optimization
- [ ] Update documentation if needed

---

## Rollback Plan

### If Issues Occur
1. [ ] Stop application: `Ctrl+C` or `kill <pid>`
2. [ ] Restore database from backup
3. [ ] Restore previous code version
4. [ ] Restart application
5. [ ] Verify system working
6. [ ] Document issue
7. [ ] Contact team lead

### Backup Locations
- [ ] Database backup: `backups/db_backup_YYYY-MM-DD.sql`
- [ ] Code backup: `git` repository
- [ ] ChromaDB backup: `chromadb_data_backup/`

---

## Documentation

### Team Onboarding
- [ ] Share `MULTIMODAL_RAG_TEAM_ONBOARDING.md`
- [ ] Share `MULTIMODAL_RAG_API_ENDPOINTS.md`
- [ ] Share `MULTIMODAL_RAG_IMPLEMENTATION_GUIDE.md`
- [ ] Conduct team training session
- [ ] Answer team questions

### Troubleshooting
- [ ] Share troubleshooting guide
- [ ] Document common issues
- [ ] Create FAQ document
- [ ] Set up support channel

---

## Sign-Off

- [ ] All checklist items completed
- [ ] All tests passing
- [ ] All documentation reviewed
- [ ] Team trained and ready
- [ ] Ready for production deployment

**Deployment Date**: _______________

**Deployed By**: _______________

**Verified By**: _______________

**Notes**: 
```
_________________________________________________________________
_________________________________________________________________
_________________________________________________________________
```

---

## Quick Reference

### Important Commands
```bash
# Start Ollama
ollama serve

# Pull model
ollama pull qwen2-vl:2b

# Run migration
python migrate_add_multimodal_rag_fields.py

# Initialize collections
python scripts/initialize_multimodal_rag.py

# Run tests
python scripts/test_multimodal_rag_system.py

# Start application
python app.py

# Check ChromaDB collections
python -c "import chromadb; client = chromadb.PersistentClient(path='./chromadb_data'); print([c.name for c in client.list_collections()])"
```

### Important Files
- Configuration: `.env`
- Service: `shared/services/multimodal_rag_service.py`
- Endpoints: `app.py`
- Database: `shared/models/purchase.py`
- Tests: `scripts/test_multimodal_rag_system.py`
- Docs: `MULTIMODAL_RAG_*.md`

### Support Contacts
- Team Lead: _______________
- DevOps: _______________
- Database Admin: _______________
- Emergency: _______________

---

**Last Updated**: 2025-10-17
**Version**: 1.0
**Status**: Ready for Deployment

