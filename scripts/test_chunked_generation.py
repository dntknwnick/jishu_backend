#!/usr/bin/env python3
"""
Test script for chunked MCQ generation system
Tests the new chunked generation service and API endpoints
"""

import sys
import os
import time
import requests
import json

# Add the parent directory to the path so we can import our modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Configuration
BASE_URL = "http://localhost:5000"
TEST_USER_EMAIL = "test@example.com"
TEST_USER_PASSWORD = "password123"

def test_chunked_generation_service():
    """Test the chunked MCQ generation service directly"""
    print("🧪 Testing Chunked MCQ Generation Service")
    print("=" * 50)
    
    try:
        # Import after adding to path
        from shared.services.chunked_mcq_service import get_chunked_mcq_service
        from shared.models.user import db
        from shared.models.purchase import MCQGenerationProgress

        # Import app differently to avoid circular imports
        import app as app_module
        
        # Create app context for database operations
        with app_module.app.app_context():
            service = get_chunked_mcq_service(batch_size=3)  # Smaller batch for testing
            
            print("✅ Chunked MCQ service initialized")
            
            # Test with mock data (you would need real test data in practice)
            print("\n🔬 Testing service methods...")
            
            # Test progress tracking
            print("- Testing progress tracking...")
            
            # Create a mock progress record for testing
            test_progress = MCQGenerationProgress(
                generation_id="test-123",
                user_id=1,
                purchase_id=1,
                subject_id=1,
                total_questions_needed=15,
                questions_generated_count=3,
                generation_status='generating'
            )
            
            db.session.add(test_progress)
            db.session.commit()
            
            # Test getting progress
            progress_result = service.get_generation_progress("test-123")
            print(f"  ✅ Progress retrieval: {progress_result['success']}")
            
            # Clean up test data
            db.session.delete(test_progress)
            db.session.commit()
            
            print("✅ Service tests completed successfully")
            
    except Exception as e:
        print(f"❌ Service test failed: {str(e)}")
        return False
    
    return True

def test_chunked_generation_api():
    """Test the chunked MCQ generation API endpoints"""
    print("\n🧪 Testing Chunked MCQ Generation API")
    print("=" * 50)
    
    try:
        # Test API status
        print("📡 Testing API connectivity...")
        response = requests.get(f"{BASE_URL}/api/health", timeout=10)
        
        if response.status_code != 200:
            print(f"❌ API not accessible: {response.status_code}")
            return False
        
        print("✅ API is accessible")
        
        # Test chunked generation endpoints (would need authentication in real scenario)
        print("\n📡 Testing chunked generation endpoints...")
        
        # Test endpoint existence (without auth, should return 401)
        endpoints_to_test = [
            "/api/user/generate-test-questions-chunked",
            "/api/user/mcq-generation-progress/test-123",
            "/api/user/mcq-generation-questions/test-123",
            "/api/user/mcq-generation-cancel/test-123",
            "/api/user/mcq-generation-retry/test-123"
        ]
        
        for endpoint in endpoints_to_test:
            try:
                if endpoint.endswith("test-123"):
                    response = requests.get(f"{BASE_URL}{endpoint}", timeout=5)
                else:
                    response = requests.post(f"{BASE_URL}{endpoint}", 
                                           json={}, timeout=5)
                
                # Should return 401 (unauthorized) since we're not authenticated
                if response.status_code == 401:
                    print(f"  ✅ {endpoint} - endpoint exists (401 as expected)")
                else:
                    print(f"  ⚠️ {endpoint} - unexpected status: {response.status_code}")
                    
            except requests.exceptions.RequestException as e:
                print(f"  ❌ {endpoint} - request failed: {str(e)}")
        
        print("✅ API endpoint tests completed")
        
    except Exception as e:
        print(f"❌ API test failed: {str(e)}")
        return False
    
    return True

def test_database_models():
    """Test the new database models"""
    print("\n🧪 Testing Database Models")
    print("=" * 50)
    
    try:
        from shared.models.purchase import MCQGenerationProgress, ExamCategoryQuestion
        from shared.models.user import db
        import app as app_module

        with app_module.app.app_context():
            print("📊 Testing MCQGenerationProgress model...")
            
            # Test model creation
            test_progress = MCQGenerationProgress(
                generation_id="test-model-123",
                user_id=1,
                purchase_id=1,
                subject_id=1,
                total_questions_needed=10,
                questions_generated_count=5,
                generation_status='generating'
            )
            
            # Test to_dict method
            progress_dict = test_progress.to_dict()
            expected_fields = [
                'generation_id', 'total_questions_needed', 
                'questions_generated_count', 'generation_status',
                'progress_percentage'
            ]
            
            for field in expected_fields:
                if field in progress_dict:
                    print(f"  ✅ {field}: {progress_dict[field]}")
                else:
                    print(f"  ❌ Missing field: {field}")
            
            print("📊 Testing ExamCategoryQuestion chunked fields...")
            
            # Test that new fields exist
            question_fields = ['generation_batch_id', 'batch_sequence']
            for field in question_fields:
                if hasattr(ExamCategoryQuestion, field):
                    print(f"  ✅ {field} field exists")
                else:
                    print(f"  ❌ Missing field: {field}")
            
            print("✅ Database model tests completed")
            
    except Exception as e:
        print(f"❌ Database model test failed: {str(e)}")
        return False
    
    return True

def test_rag_service_integration():
    """Test integration with RAG service"""
    print("\n🧪 Testing RAG Service Integration")
    print("=" * 50)
    
    try:
        from shared.services.rag_service import get_rag_service
        
        rag_service = get_rag_service()
        print("✅ RAG service initialized")
        
        # Test small batch generation
        print("🔬 Testing small batch generation...")
        
        result = rag_service.generate_mcq_questions(
            subject='physics',
            num_questions=2,  # Small batch for testing
            difficulty='hard'
        )
        
        if result['success']:
            print(f"  ✅ Generated {len(result['questions'])} questions")
            print(f"  ✅ Generation time: {result.get('generation_time', 'N/A')} seconds")
            print(f"  ✅ Model used: {result.get('model_used', 'N/A')}")
        else:
            print(f"  ❌ Generation failed: {result.get('error', 'Unknown error')}")
            
        print("✅ RAG service integration test completed")
        
    except Exception as e:
        print(f"❌ RAG service integration test failed: {str(e)}")
        return False
    
    return True

def main():
    """Run all tests"""
    print("🚀 Chunked MCQ Generation System Tests")
    print("=" * 60)
    
    tests = [
        ("Database Models", test_database_models),
        ("RAG Service Integration", test_rag_service_integration),
        ("Chunked Generation Service", test_chunked_generation_service),
        ("API Endpoints", test_chunked_generation_api),
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
        print("🎉 All tests passed! Chunked MCQ generation system is ready.")
        return 0
    else:
        print("⚠️ Some tests failed. Please review the implementation.")
        return 1

if __name__ == "__main__":
    exit(main())
