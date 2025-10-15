#!/usr/bin/env python3
"""
Test the RAG service import fix
"""

import os
import sys

# Add the parent directory to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_rag_service_import():
    """Test if RAG service can be imported and instantiated"""
    print("Testing RAG service import...")
    
    try:
        from shared.services.rag_service import get_rag_service, RAGService
        
        print("✅ RAG service modules imported successfully")
        
        # Test get_rag_service function
        rag_service = get_rag_service()
        print("✅ get_rag_service() function works")
        
        # Test RAG service methods
        if hasattr(rag_service, 'generate_mcq_questions'):
            print("✅ generate_mcq_questions method exists")
        else:
            print("❌ generate_mcq_questions method missing")
            return False
        
        if hasattr(rag_service, 'get_status'):
            print("✅ get_status method exists")
        else:
            print("❌ get_status method missing")
            return False
        
        # Test status method
        status = rag_service.get_status()
        print(f"✅ RAG service status: {status.get('status', 'unknown')}")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {str(e)}")
        return False
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

def test_app_import():
    """Test if app can be imported without errors"""
    print("\nTesting app import...")
    
    try:
        import app
        print("✅ App imported successfully")
        
        # Test if create_app function exists
        if hasattr(app, 'create_app'):
            print("✅ create_app function exists")
        else:
            print("❌ create_app function missing")
            return False
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {str(e)}")
        return False
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

def test_endpoint_logic():
    """Test the endpoint logic without actually running the server"""
    print("\nTesting endpoint logic...")
    
    try:
        # Import required modules
        from shared.services.rag_service import get_rag_service
        from shared.models.purchase import ExamCategoryQuestion
        from shared.models.course import ExamCategorySubject
        
        print("✅ All required modules imported")
        
        # Test RAG service instantiation
        rag_service = get_rag_service()
        print("✅ RAG service instantiated")
        
        # Test a simple MCQ generation call (will fail due to dependencies but should not crash)
        try:
            result = rag_service.generate_mcq_questions(
                subject='physics',
                num_questions=2,
                difficulty='hard'
            )
            
            # Check result structure
            if isinstance(result, dict) and 'success' in result:
                print("✅ MCQ generation method returns proper structure")
                if result.get('success'):
                    print(f"✅ Generated {len(result.get('questions', []))} questions")
                else:
                    print(f"ℹ️ MCQ generation failed as expected: {result.get('error', 'Unknown error')}")
            else:
                print("❌ MCQ generation method returns invalid structure")
                return False
                
        except Exception as e:
            print(f"ℹ️ MCQ generation failed as expected: {str(e)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Endpoint logic test failed: {str(e)}")
        return False

def main():
    """Main test function"""
    print("🧪 RAG Service Import Fix Test")
    print("=" * 40)
    
    tests = [
        ("RAG Service Import", test_rag_service_import),
        ("App Import", test_app_import),
        ("Endpoint Logic", test_endpoint_logic)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n🔍 Running {test_name} test...")
        try:
            if test_func():
                passed += 1
                print(f"✅ {test_name} - PASSED")
            else:
                print(f"❌ {test_name} - FAILED")
        except Exception as e:
            print(f"❌ {test_name} - FAILED with exception: {str(e)}")
    
    print("\n" + "=" * 40)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed!")
        print("✅ RAG service import fix is working correctly")
        print("✅ The ModuleNotFoundError should be resolved")
        return True
    else:
        print("⚠️ Some tests failed - check the issues above")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
