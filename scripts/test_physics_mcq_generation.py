#!/usr/bin/env python3
"""
Test script to verify Physics MCQ generation with optimizations
"""

import sys
import os
import time

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_physics_mcq_generation():
    """Test Physics MCQ generation with different question counts"""
    try:
        from shared.services.rag_service import get_rag_service
        
        print("🧪 Testing Physics MCQ generation with optimizations...")
        
        # Initialize RAG service
        rag = get_rag_service()
        
        # Test with smaller batches first
        test_cases = [
            {"questions": 5, "description": "Small batch (5 questions)"},
            {"questions": 10, "description": "Medium batch (10 questions)"},
            {"questions": 25, "description": "Large batch (25 questions)"}
        ]
        
        for test_case in test_cases:
            print(f"\n🔬 {test_case['description']}")
            
            start_time = time.time()
            
            result = rag.generate_mcq_questions(
                subject="physics",
                num_questions=test_case["questions"],
                difficulty="medium"
            )
            
            generation_time = time.time() - start_time
            
            if result['success']:
                print(f"✅ Success! Generated {len(result['questions'])} questions in {generation_time:.2f}s")
                print(f"   Average: {generation_time/test_case['questions']:.2f}s per question")
                
                # Show first question as example
                if result['questions']:
                    q = result['questions'][0]
                    print(f"   Example: {q['question'][:80]}...")
                    
            else:
                print(f"❌ Failed: {result['error']}")
                print(f"   Time taken: {generation_time:.2f}s")
                
            # Check if we should continue with larger batches
            if not result['success'] or generation_time > 60:
                print(f"⚠️ Stopping tests - generation too slow or failed")
                break
                
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_timeout_configuration():
    """Test timeout configuration"""
    try:
        import sys
        sys.path.insert(0, '.')
        from config import Config
        
        print(f"\n⏰ Current timeout configuration:")
        print(f"   RAG_TIMEOUT_SECONDS: {Config.RAG_TIMEOUT_SECONDS}")
        
        return True
        
    except Exception as e:
        print(f"❌ Config test failed: {str(e)}")
        return False

if __name__ == "__main__":
    print("🚀 Testing Physics MCQ Generation Optimizations")
    print("=" * 50)
    
    # Test timeout config
    test_timeout_configuration()
    
    # Test MCQ generation
    test_physics_mcq_generation()
    
    print("\n" + "=" * 50)
    print("✅ Test completed!")
