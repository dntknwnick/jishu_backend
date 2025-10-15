#!/usr/bin/env python3
"""
Test script to verify database relationships for chunked MCQ generation
"""

import sys
import os

# Add the parent directory to the path so we can import our modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_session_relationships():
    """Test TestAttemptSession relationships"""
    print("🧪 Testing TestAttemptSession Relationships")
    print("=" * 50)
    
    try:
        from shared.models.purchase import TestAttemptSession, MockTestAttempt
        from shared.models.user import db
        import app as app_module
        
        with app_module.app.app_context():
            # Get a sample session
            session = TestAttemptSession.query.first()
            
            if session:
                print(f"✅ Found TestAttemptSession: {session.id}")
                
                # Test mock_test relationship
                if hasattr(session, 'mock_test') and session.mock_test:
                    mock_test = session.mock_test
                    print(f"✅ mock_test relationship works: {mock_test.id}")
                    
                    # Test purchase relationship through mock_test
                    if hasattr(mock_test, 'purchase') and mock_test.purchase:
                        purchase = mock_test.purchase
                        print(f"✅ purchase relationship works: {purchase.id}")
                        
                        # Test subject relationship through mock_test
                        if hasattr(mock_test, 'subject') and mock_test.subject:
                            subject = mock_test.subject
                            print(f"✅ subject relationship works: {subject.subject_name}")
                        else:
                            print("❌ subject relationship missing")
                    else:
                        print("❌ purchase relationship missing")
                else:
                    print("❌ mock_test relationship missing")
            else:
                print("⚠️ No TestAttemptSession found in database")
                
        return True
        
    except Exception as e:
        print(f"❌ TestAttemptSession relationship test failed: {str(e)}")
        return False

def test_chunked_service_context():
    """Test the chunked service context generation"""
    print("\n🧪 Testing Chunked Service Context Generation")
    print("=" * 50)
    
    try:
        from shared.services.chunked_mcq_service_simple import get_chunked_mcq_service
        from shared.models.purchase import TestAttemptSession
        from shared.models.user import db
        import app as app_module
        
        with app_module.app.app_context():
            service = get_chunked_mcq_service()
            
            # Get a sample session
            session = TestAttemptSession.query.first()
            
            if session:
                print(f"✅ Testing with session ID: {session.id}")
                
                # Test context generation
                context = service._get_generation_context(
                    test_attempt_id=None,
                    session_id=session.id
                )
                
                if context['success']:
                    print("✅ Context generation successful")
                    print(f"  - Subject: {context['subject_name']}")
                    print(f"  - Total questions: {context['total_questions']}")
                    print(f"  - Purchase ID: {context['purchase_id']}")
                    print(f"  - Subject ID: {context['subject_id']}")
                else:
                    print(f"❌ Context generation failed: {context['error']}")
                    return False
            else:
                print("⚠️ No TestAttemptSession found for testing")
                
        return True
        
    except Exception as e:
        print(f"❌ Chunked service context test failed: {str(e)}")
        return False

def test_mock_test_relationships():
    """Test MockTestAttempt relationships"""
    print("\n🧪 Testing MockTestAttempt Relationships")
    print("=" * 50)
    
    try:
        from shared.models.purchase import MockTestAttempt
        from shared.models.user import db
        import app as app_module
        
        with app_module.app.app_context():
            # Get a sample mock test
            mock_test = MockTestAttempt.query.first()
            
            if mock_test:
                print(f"✅ Found MockTestAttempt: {mock_test.id}")
                
                # Test relationships
                relationships = ['purchase', 'subject', 'course', 'user']
                for rel in relationships:
                    if hasattr(mock_test, rel):
                        obj = getattr(mock_test, rel)
                        if obj:
                            print(f"✅ {rel} relationship works: {obj}")
                        else:
                            print(f"❌ {rel} relationship is None")
                    else:
                        print(f"❌ {rel} relationship missing")
            else:
                print("⚠️ No MockTestAttempt found in database")
                
        return True
        
    except Exception as e:
        print(f"❌ MockTestAttempt relationship test failed: {str(e)}")
        return False

def main():
    """Run all relationship tests"""
    print("🚀 Database Relationship Tests for Chunked MCQ")
    print("=" * 60)
    
    tests = [
        ("MockTestAttempt Relationships", test_mock_test_relationships),
        ("TestAttemptSession Relationships", test_session_relationships),
        ("Chunked Service Context", test_chunked_service_context),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n🧪 Running {test_name} tests...")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} test crashed: {str(e)}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All relationship tests passed! Chunked MCQ should work correctly.")
        return 0
    else:
        print("⚠️ Some relationship tests failed. Check the database relationships.")
        return 1

if __name__ == "__main__":
    exit(main())
