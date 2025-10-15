#!/usr/bin/env python3
"""
Test script to verify Physics collection is accessible
"""

import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_physics_collection():
    """Test if Physics collection is accessible"""
    try:
        from shared.services.rag_service import get_rag_service
        
        print("🧪 Testing Physics collection access...")
        
        # Initialize RAG service
        rag = get_rag_service()
        
        # Test Physics search
        results = rag.search_similar_content('physics', 'physics', top_k=2)
        print(f"Physics search results: {len(results)} found")
        
        if results:
            print("✅ Physics collection is now accessible!")
            for i, result in enumerate(results[:2]):
                content_preview = result['content'][:100] + "..." if len(result['content']) > 100 else result['content']
                print(f"  Result {i+1}: {content_preview}")
                print(f"    Similarity: {result['similarity']:.4f}")
                print(f"    Source: {result['metadata'].get('source_file', 'Unknown')}")
        else:
            print("❌ Still no results found")
            
        # Test MCQ generation for Physics
        print("\n🧪 Testing Physics MCQ generation...")
        mcq_result = rag.generate_mcq_questions(
            subject="physics",
            num_questions=2,
            difficulty="medium"
        )
        
        if mcq_result['success']:
            print(f"✅ MCQ generation successful! Generated {len(mcq_result['questions'])} questions")
            for i, q in enumerate(mcq_result['questions'][:1]):
                print(f"  Question {i+1}: {q['question'][:100]}...")
        else:
            print(f"❌ MCQ generation failed: {mcq_result['error']}")
            
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_physics_collection()
