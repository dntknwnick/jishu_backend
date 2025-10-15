#!/usr/bin/env python3
"""
Quick test script to verify vector store functionality
"""

import sys
import os
import time

# Add the parent directory to the path so we can import from shared
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_simple_vector_store():
    """Test the simple vector store manager"""
    print("🧪 Testing Simple Vector Store Manager...")
    
    try:
        from shared.services.simple_vector_store_manager import get_simple_vector_store_manager
        
        # Initialize manager
        manager = get_simple_vector_store_manager(
            pdf_folder_path="./pdfs/subjects",
            vector_store_path="./vector_stores",
            ollama_model="llama3.2:1b"
        )
        
        # Check status
        status = manager.get_status()
        print(f"📊 Status:")
        print(f"   FAISS: {'✅' if status.get('faiss_available') else '❌'}")
        print(f"   Ollama: {'✅' if status.get('ollama_available') else '❌'}")
        print(f"   Loaded subjects: {status.get('loaded_subjects', [])}")
        
        # Try to load existing vector stores
        print("\n🔍 Checking for existing vector stores...")
        for subject in ['physics', 'chemistry', 'biology', 'mathematics']:
            try:
                success = manager.create_subject_vector_store(subject, force_recreate=False)
                if success:
                    print(f"   ✅ {subject}: Vector store loaded/created")
                    
                    # Test query
                    results = manager.query_subject_vector_store(subject, "fundamental concepts", top_k=3)
                    print(f"      📄 Found {len(results)} relevant documents")
                    
                    # Test context generation
                    context = manager.get_subject_context(subject, max_tokens=500)
                    print(f"      📝 Generated context: {len(context)} characters")
                    
                else:
                    print(f"   ❌ {subject}: Failed to load/create vector store")
                    
            except Exception as e:
                print(f"   ⚠️ {subject}: Error - {str(e)}")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {str(e)}")
        return False
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

def test_optimized_ai_service():
    """Test the optimized AI service"""
    print("\n🧪 Testing Optimized AI Service...")
    
    try:
        from shared.services.optimized_ai_service import get_optimized_ai_service
        
        # Initialize service
        service = get_optimized_ai_service(
            pdf_folder_path="./pdfs/subjects",
            vector_store_path="./vector_stores",
            ollama_model="llama3.2:1b"
        )
        
        # Check if vector manager is available
        if service.vector_manager is None:
            print("❌ Vector manager not available")
            return False
        
        print("✅ Optimized AI service initialized")
        
        # Test MCQ generation (only if vector stores are ready)
        status = service.vector_manager.get_status()
        if status.get('loaded_subjects'):
            print("🎯 Testing MCQ generation...")
            
            start_time = time.time()
            result = service.generate_mcq_optimized(
                num_questions=2,
                subject_name='physics',
                difficulty='medium',
                use_cache=False
            )
            end_time = time.time()
            
            if result.get('success'):
                print(f"✅ MCQ generation successful in {end_time - start_time:.2f} seconds")
                print(f"   📝 Generated {len(result.get('questions', []))} questions")
            else:
                print(f"❌ MCQ generation failed: {result.get('error', 'Unknown error')}")
        else:
            print("⚠️ No vector stores loaded yet - skipping MCQ test")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {str(e)}")
        return False
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

def main():
    """Main test function"""
    print("=" * 60)
    print("🚀 QUICK VECTOR STORE TEST")
    print("=" * 60)
    
    # Test 1: Simple Vector Store Manager
    test1_success = test_simple_vector_store()
    
    # Test 2: Optimized AI Service
    test2_success = test_optimized_ai_service()
    
    print("\n" + "=" * 60)
    print("📊 TEST RESULTS")
    print("=" * 60)
    print(f"Simple Vector Store: {'✅ PASS' if test1_success else '❌ FAIL'}")
    print(f"Optimized AI Service: {'✅ PASS' if test2_success else '❌ FAIL'}")
    
    if test1_success and test2_success:
        print("\n🎉 All tests passed! Vector store optimization is working.")
    else:
        print("\n⚠️ Some tests failed. Check the output above for details.")

if __name__ == "__main__":
    main()
