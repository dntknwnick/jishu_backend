# Chunked MCQ Generation Fix

## Issue Identified

From the error logs:
```
ERROR:shared.services.chunked_mcq_service_simple:❌ Error getting generation context: 'TestAttemptSession' object has no attribute 'purchase'
```

## Root Cause

The chunked MCQ service was trying to access `session.purchase` directly, but `TestAttemptSession` doesn't have a direct `purchase` relationship. The correct relationship chain is:

```
TestAttemptSession → MockTestAttempt → ExamCategoryPurchase
```

## Fix Applied

### Before (Incorrect):
```python
session = TestAttemptSession.query.get(session_id)
purchase = session.purchase  # ❌ This doesn't exist
subject = purchase.subject
```

### After (Correct):
```python
session = TestAttemptSession.query.get(session_id)
mock_test = session.mock_test  # ✅ Get mock test first
purchase = mock_test.purchase  # ✅ Get purchase through mock test
subject = mock_test.subject    # ✅ Get subject through mock test
```

## Database Relationship Chain

```
TestAttemptSession
├── mock_test_id (FK) → MockTestAttempt
    ├── purchase_id (FK) → ExamCategoryPurchase
    ├── subject_id (FK) → ExamCategorySubject
    ├── course_id (FK) → ExamCategory
    └── user_id (FK) → User
```

## Files Modified

1. **`shared/services/chunked_mcq_service_simple.py`**
   - Fixed `_get_generation_context()` method
   - Added proper relationship chain: `session.mock_test.purchase`
   - Added debug logging for troubleshooting
   - Added `mock_test_id` to context for question linking

## Changes Made

### 1. Fixed Context Generation
```python
# Get purchase through mock_test relationship
mock_test = session.mock_test
if not mock_test:
    return {'success': False, 'error': 'Mock test not found'}

purchase = mock_test.purchase
subject = mock_test.subject
total_questions = 50  # Mock tests always have 50 questions
```

### 2. Added Debug Logging
```python
logger.info(f"🔍 Getting context for session_id: {session_id}")
logger.info(f"✅ Found session: {session.id}, mock_test_id: {session.mock_test_id}")
logger.info(f"✅ Found mock_test: {mock_test.id}")
logger.info(f"✅ Context: purchase_id={purchase.id}, subject={subject.subject_name}")
```

### 3. Fixed Question Linking
```python
# Link to mock test if this is for a test card
if 'mock_test_id' in context:
    question.mock_test_id = context['mock_test_id']
```

## Testing Steps

### 1. Start the Application
```bash
cd myenv && scripts/activate && cd ../jishu_backend && python app.py
```

### 2. Test Chunked Generation
1. Go to the frontend
2. Click "Start Test" on any test card
3. Check the logs for successful context generation:
   ```
   INFO:shared.services.chunked_mcq_service_simple:🔍 Getting context for session_id: 477
   INFO:shared.services.chunked_mcq_service_simple:✅ Found session: 477, mock_test_id: 123
   INFO:shared.services.chunked_mcq_service_simple:✅ Found mock_test: 123
   INFO:shared.services.chunked_mcq_service_simple:✅ Context: purchase_id=45, subject=Physics, total_questions=50
   ```

### 3. Verify Database
Check that questions are saved with proper linking:
```sql
SELECT 
    id, question, generation_batch_id, batch_sequence, mock_test_id
FROM exam_category_questions 
WHERE generation_batch_id IS NOT NULL
ORDER BY generation_batch_id, batch_sequence;
```

## Expected Behavior

### 1. Successful Generation
- First 5 questions generate in 3-5 seconds
- User navigates to instructions page
- Background generation continues
- Progress bar shows loading status

### 2. Database Records
- Questions saved to `exam_category_questions` table
- `generation_batch_id` set to UUID
- `batch_sequence` set to 1, 2, 3, 4, 5 for first batch
- `mock_test_id` linked to the test card

### 3. Frontend Experience
- Loading screen shows progress
- Instructions page shows "X of Y questions ready"
- User can start test with initial 5 questions
- More questions load in background

## Troubleshooting

### If Error Persists:
1. Check the logs for the specific error message
2. Verify the session ID exists in database:
   ```sql
   SELECT * FROM test_attempt_sessions WHERE id = [session_id];
   ```
3. Check mock test relationship:
   ```sql
   SELECT s.id, s.mock_test_id, m.id, m.purchase_id 
   FROM test_attempt_sessions s 
   JOIN mock_test_attempts m ON s.mock_test_id = m.id 
   WHERE s.id = [session_id];
   ```

### Common Issues:
1. **Session not found**: Check if session ID is valid
2. **Mock test not found**: Check if mock_test_id is properly set
3. **Purchase not found**: Check if mock test has valid purchase_id
4. **Subject not found**: Check if mock test has valid subject_id

## Verification Checklist

- [ ] No more "object has no attribute 'purchase'" errors
- [ ] Context generation succeeds with proper logging
- [ ] First 5 questions generate successfully
- [ ] Questions saved to database with correct relationships
- [ ] Frontend shows progress and allows test start
- [ ] Background generation continues for remaining questions

## Next Steps

Once this fix is verified:
1. Test with multiple concurrent users
2. Verify re-attempt flow still works
3. Test legacy flow (if used)
4. Monitor performance and error rates
5. Consider adding more comprehensive error handling

The fix addresses the core relationship issue and should resolve the chunked MCQ generation error.
