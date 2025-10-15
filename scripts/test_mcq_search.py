#!/usr/bin/env python3
"""
Test MCQ search query
"""

import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_mcq_search():
    """Test the MCQ search query"""
    try:
        from shared.services.rag_service import get_rag_service
        
        print("🔍 Testing MCQ search query...")
        
        # Initialize RAG service with low threshold
        rag_service = get_rag_service(similarity_threshold=0.01)
        
        # Test the exact query used by MCQ generation
        mcq_query = "mathematics concepts questions topics"
        print(f"Testing query: '{mcq_query}'")
        
        results = rag_service.search_similar_content(mcq_query, "mathematics", top_k=5)
        print(f"Results found: {len(results)}")
        
        if results:
            for i, result in enumerate(results[:3]):
                print(f"  Result {i+1}: {result['content'][:100]}...")
                print(f"    Similarity: {result.get('similarity', 'N/A')}")
        else:
            print("  No results found!")
            
            # Try a simpler query
            simple_query = "mathematics"
            print(f"\nTrying simpler query: '{simple_query}'")
            results2 = rag_service.search_similar_content(simple_query, "mathematics", top_k=5)
            print(f"Results found: {len(results2)}")
            
            if results2:
                print("  Simple query works! The issue is with the complex query.")
        
        return True
        
    except Exception as e:
        print(f"❌ Error during MCQ search test: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_mcq_search()
