#!/usr/bin/env python3
"""
Test only the optimized MCQ generation with vector stores
"""

import sys
import os
import time

# Add the parent directory to the path so we can import from shared
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_optimized_mcq():
    """Test optimized MCQ generation"""
    print("🧪 Testing Optimized MCQ Generation with FAISS Vector Stores...")
    
    try:
        from shared.services.simple_vector_store_manager import get_simple_vector_store_manager
        
        # Initialize manager
        manager = get_simple_vector_store_manager(
            pdf_folder_path="./pdfs/subjects",
            vector_store_path="./vector_stores",
            ollama_model="llama3.2:1b"
        )
        
        print("✅ Simple Vector Store Manager initialized")
        
        # Test physics MCQ generation
        subject = 'physics'
        print(f"\n🔬 Testing {subject.upper()} MCQ generation...")
        
        # Get context first
        print("📄 Getting context from vector store...")
        context = manager.get_subject_context(subject, max_tokens=1000)
        
        if context:
            print(f"✅ Context retrieved: {len(context)} characters")
            print(f"📝 Sample context: {context[:200]}...")
            
            # Now test MCQ generation with this context
            print("\n🤖 Testing MCQ generation with context...")
            
            # Create a simple prompt
            prompt = f"""EDUCATIONAL TASK: Create 1 academic multiple choice question for {subject} exam preparation.

STUDY MATERIAL:
{context[:500]}

REQUIREMENTS:
- Academic level question for exam preparation
- 4 options (A, B, C, D)
- 1 correct answer
- Focus on {subject} concepts
- Educational language only

FORMAT:
Question 1: [Academic question]
A) [option]
B) [option]
C) [option]
D) [option]
Correct Answer: [A/B/C/D]

Generate 1 question:"""
            
            # Test with Ollama
            import ollama
            
            start_time = time.time()
            response = ollama.generate(
                model="llama3.2:1b",
                prompt=prompt,
                options={
                    'temperature': 0.7,
                    'top_p': 0.9,
                    'num_predict': 500
                }
            )
            end_time = time.time()
            
            response_text = response.get('response', '')
            
            if response_text and len(response_text) > 50:
                print(f"✅ SUCCESS: MCQ generated in {end_time - start_time:.2f} seconds")
                print(f"📝 Response length: {len(response_text)} characters")
                print(f"📄 Generated MCQ:\n{response_text}")
                
                # Check for safety filter responses
                if "discriminatory" in response_text.lower() or "harmful" in response_text.lower() or "can't assist" in response_text.lower():
                    print("⚠️ Safety filter detected in response")
                    return False
                
                return True
            else:
                print(f"❌ FAILED: Empty or very short response")
                print(f"📄 Full response: {response_text}")
                return False
        else:
            print("❌ No context retrieved from vector store")
            return False
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

def main():
    """Main test function"""
    print("=" * 60)
    print("🚀 OPTIMIZED MCQ GENERATION TEST")
    print("=" * 60)
    
    success = test_optimized_mcq()
    
    print("\n" + "=" * 60)
    print("📊 TEST RESULT")
    print("=" * 60)
    
    if success:
        print("🎉 SUCCESS! Optimized MCQ generation is working!")
    else:
        print("❌ FAILED! Check the output above for details.")

if __name__ == "__main__":
    main()
