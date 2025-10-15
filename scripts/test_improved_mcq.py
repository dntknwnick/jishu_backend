#!/usr/bin/env python3
"""
Test improved MCQ generation
"""

import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_improved_mcq():
    """Test improved MCQ generation"""
    try:
        from shared.services.rag_service import get_rag_service
        
        print("🧪 Testing improved MCQ generation...")
        rag = get_rag_service()
        
        result = rag.generate_mcq_questions("physics", 5, "medium")
        
        print(f"Success: {result['success']}")
        if result['success']:
            print(f"Generated {len(result['questions'])} questions")
            print(f"First question: {result['questions'][0]['question'][:80]}...")
        else:
            print(f"Error: {result['error']}")
            
        return result['success']
        
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        return False

if __name__ == "__main__":
    test_improved_mcq()
