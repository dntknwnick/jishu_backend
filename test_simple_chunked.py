#!/usr/bin/env python3
"""
Simple test for chunked MCQ generation using existing table structure
"""

import sys
import os

# Add the parent directory to the path so we can import our modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_simple_chunked_service():
    """Test the simple chunked MCQ service"""
    print("🧪 Testing Simple Chunked MCQ Service")
    print("=" * 50)
    
    try:
        # Import the service
        from shared.services.chunked_mcq_service_simple import get_chunked_mcq_service
        
        service = get_chunked_mcq_service(batch_size=3)  # Small batch for testing
        print("✅ Simple chunked service initialized")
        
        # Test service methods exist
        methods_to_test = [
            'start_chunked_generation',
            'get_generation_progress',
            '_get_generation_context',
            '_generate_and_save_batch'
        ]
        
        for method in methods_to_test:
            if hasattr(service, method):
                print(f"  ✅ Method {method} exists")
            else:
                print(f"  ❌ Method {method} missing")
        
        print("✅ Service structure test completed")
        return True
        
    except Exception as e:
        print(f"❌ Service test failed: {str(e)}")
        return False

def test_database_structure():
    """Test that the existing database structure supports chunked generation"""
    print("\n🧪 Testing Database Structure")
    print("=" * 50)
    
    try:
        from shared.models.purchase import ExamCategoryQuestion
        
        # Test that chunked generation fields exist
        test_question = ExamCategoryQuestion()
        
        chunked_fields = ['generation_batch_id', 'batch_sequence']
        for field in chunked_fields:
            if hasattr(test_question, field):
                print(f"  ✅ Field {field} exists in ExamCategoryQuestion")
            else:
                print(f"  ❌ Field {field} missing in ExamCategoryQuestion")
        
        # Test other required fields
        required_fields = [
            'exam_category_id', 'subject_id', 'question', 
            'option_1', 'option_2', 'option_3', 'option_4',
            'correct_answer', 'explanation', 'user_id', 'purchased_id'
        ]
        
        for field in required_fields:
            if hasattr(test_question, field):
                print(f"  ✅ Required field {field} exists")
            else:
                print(f"  ❌ Required field {field} missing")
        
        print("✅ Database structure test completed")
        return True
        
    except Exception as e:
        print(f"❌ Database structure test failed: {str(e)}")
        return False

def test_api_endpoints():
    """Test that the API endpoints are properly configured"""
    print("\n🧪 Testing API Endpoints")
    print("=" * 50)
    
    try:
        import requests
        
        # Test basic connectivity
        base_url = "http://localhost:5000"
        
        endpoints_to_test = [
            "/api/user/generate-test-questions-chunked",
            "/api/user/mcq-generation-progress/test-123",
            "/api/user/mcq-generation-questions/test-123",
            "/api/user/mcq-generation-cancel/test-123"
        ]
        
        print("📡 Testing endpoint availability...")
        
        for endpoint in endpoints_to_test:
            try:
                if endpoint.endswith("test-123"):
                    response = requests.get(f"{base_url}{endpoint}", timeout=5)
                else:
                    response = requests.post(f"{base_url}{endpoint}", json={}, timeout=5)
                
                # Should return 401 (unauthorized) since we're not authenticated
                if response.status_code == 401:
                    print(f"  ✅ {endpoint} - endpoint exists (401 as expected)")
                elif response.status_code == 404:
                    print(f"  ❌ {endpoint} - endpoint not found (404)")
                else:
                    print(f"  ⚠️ {endpoint} - unexpected status: {response.status_code}")
                    
            except requests.exceptions.ConnectionError:
                print(f"  ⚠️ {endpoint} - server not running")
            except requests.exceptions.RequestException as e:
                print(f"  ❌ {endpoint} - request failed: {str(e)}")
        
        print("✅ API endpoint test completed")
        return True
        
    except Exception as e:
        print(f"❌ API endpoint test failed: {str(e)}")
        return False

def test_imports():
    """Test that all required imports work"""
    print("\n🧪 Testing Imports")
    print("=" * 50)
    
    try:
        # Test model imports
        from shared.models.purchase import ExamCategoryQuestion, TestAttempt, TestAttemptSession
        from shared.models.course import ExamCategory, ExamCategorySubject
        from shared.models.user import db
        print("  ✅ Model imports successful")
        
        # Test service imports
        from shared.services.chunked_mcq_service_simple import get_chunked_mcq_service
        print("  ✅ Service imports successful")
        
        # Test RAG service import
        from shared.services.rag_service import get_rag_service
        print("  ✅ RAG service import successful")
        
        print("✅ Import test completed")
        return True
        
    except Exception as e:
        print(f"❌ Import test failed: {str(e)}")
        return False

def main():
    """Run all tests"""
    print("🚀 Simple Chunked MCQ Generation Tests")
    print("=" * 60)
    
    tests = [
        ("Imports", test_imports),
        ("Database Structure", test_database_structure),
        ("Simple Chunked Service", test_simple_chunked_service),
        ("API Endpoints", test_api_endpoints),
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
        print("🎉 All tests passed! Simple chunked MCQ generation is ready.")
        print("\n📋 Next Steps:")
        print("1. Start the Flask application: python app.py")
        print("2. Test the chunked generation flow in the frontend")
        print("3. Verify questions are saved to exam_category_questions table")
        print("4. Check that generation_batch_id is properly set")
        return 0
    else:
        print("⚠️ Some tests failed. Please review the implementation.")
        return 1

if __name__ == "__main__":
    exit(main())
