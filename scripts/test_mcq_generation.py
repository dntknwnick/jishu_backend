#!/usr/bin/env python3
"""
Test MCQ Generation with Updated Prompts
Tests both optimized and regular MCQ generation to ensure they work without safety filter issues
"""

import sys
import os
import time

# Add the parent directory to the path so we can import from shared
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_optimized_mcq_generation():
    """Test the optimized MCQ generation"""
    print("🧪 Testing Optimized MCQ Generation...")
    
    try:
        from shared.services.optimized_ai_service import get_optimized_ai_service
        
        # Initialize service
        service = get_optimized_ai_service(
            pdf_folder_path="./pdfs/subjects",
            vector_store_path="./vector_stores",
            ollama_model="llama3.2:1b"
        )
        
        if service.vector_manager is None:
            print("❌ Vector manager not available")
            return False
        
        print("✅ Optimized AI service initialized")
        
        # Test MCQ generation for each available subject
        subjects = ['physics', 'chemistry', 'biology']
        
        for subject in subjects:
            print(f"\n🔬 Testing {subject.upper()} MCQ generation...")
            
            start_time = time.time()
            result = service.generate_mcq_optimized(
                num_questions=2,  # Small number for quick test
                subject_name=subject,
                difficulty='medium',
                use_cache=False
            )
            end_time = time.time()
            
            if result.get('success'):
                questions = result.get('questions', [])
                print(f"✅ SUCCESS: Generated {len(questions)} questions in {end_time - start_time:.2f} seconds")
                
                # Display first question as example
                if questions:
                    q = questions[0]
                    print(f"   📝 Sample Question: {q.get('question', 'N/A')[:100]}...")
                    print(f"   🎯 Correct Answer: {q.get('correct_answer', 'N/A')}")
                
            else:
                error_msg = result.get('error', 'Unknown error')
                print(f"❌ FAILED: {error_msg}")
                
                # Check if it's a safety filter issue
                if "discriminatory" in error_msg.lower() or "harmful" in error_msg.lower():
                    print("   ⚠️ This appears to be a safety filter issue")
                    return False
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {str(e)}")
        return False
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

def test_regular_mcq_generation():
    """Test the regular MCQ generation"""
    print("\n🧪 Testing Regular MCQ Generation...")
    
    try:
        from shared.services.ai_service import AIService
        
        # Initialize service
        service = AIService(
            pdf_folder_path="./pdfs/subjects",
            ollama_model="llama3.2:1b"
        )
        
        print("✅ Regular AI service initialized")
        
        # Test MCQ generation
        print(f"\n🔬 Testing regular MCQ generation...")
        
        start_time = time.time()
        result = service.generate_mcq_from_pdfs_fast(
            num_questions=2,  # Small number for quick test
            subject_name='physics',
            difficulty='medium'
        )
        end_time = time.time()
        
        if result.get('success'):
            questions = result.get('questions', [])
            print(f"✅ SUCCESS: Generated {len(questions)} questions in {end_time - start_time:.2f} seconds")
            
            # Display first question as example
            if questions:
                q = questions[0]
                print(f"   📝 Sample Question: {q.get('question', 'N/A')[:100]}...")
                print(f"   🎯 Correct Answer: {q.get('correct_answer', 'N/A')}")
            
            return True
        else:
            error_msg = result.get('error', 'Unknown error')
            print(f"❌ FAILED: {error_msg}")
            
            # Check if it's a safety filter issue
            if "discriminatory" in error_msg.lower() or "harmful" in error_msg.lower():
                print("   ⚠️ This appears to be a safety filter issue")
                return False
            
            return False
        
    except ImportError as e:
        print(f"❌ Import error: {str(e)}")
        return False
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

def test_ollama_direct():
    """Test Ollama directly with a simple educational prompt"""
    print("\n🧪 Testing Ollama Direct Communication...")
    
    try:
        import ollama
        
        # Simple educational prompt
        prompt = """You are an educational content creator. Create 1 simple physics multiple choice question about Newton's laws of motion for academic assessment.

Format:
Question 1: [Educational physics question]
A) [option]
B) [option] 
C) [option]
D) [option]
Correct Answer: [A/B/C/D]

Create the question now:"""
        
        print("🤖 Testing direct Ollama communication...")
        
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
            print(f"✅ SUCCESS: Ollama responded in {end_time - start_time:.2f} seconds")
            print(f"   📝 Response length: {len(response_text)} characters")
            print(f"   📄 Sample: {response_text[:200]}...")
            
            # Check for safety filter responses
            if "discriminatory" in response_text.lower() or "harmful" in response_text.lower():
                print("   ⚠️ Safety filter detected in response")
                return False
            
            return True
        else:
            print(f"❌ FAILED: Empty or very short response")
            print(f"   📄 Full response: {response_text}")
            return False
        
    except ImportError as e:
        print(f"❌ Ollama not available: {str(e)}")
        return False
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

def main():
    """Main test function"""
    print("=" * 70)
    print("🚀 MCQ GENERATION SAFETY FILTER TEST")
    print("=" * 70)
    print("Testing updated prompts to avoid AI safety filter issues...")
    print()
    
    # Test 1: Direct Ollama communication
    test1_success = test_ollama_direct()
    
    # Test 2: Optimized MCQ generation
    test2_success = test_optimized_mcq_generation()
    
    # Test 3: Regular MCQ generation
    test3_success = test_regular_mcq_generation()
    
    print("\n" + "=" * 70)
    print("📊 TEST RESULTS")
    print("=" * 70)
    print(f"Direct Ollama Test: {'✅ PASS' if test1_success else '❌ FAIL'}")
    print(f"Optimized MCQ Test: {'✅ PASS' if test2_success else '❌ FAIL'}")
    print(f"Regular MCQ Test: {'✅ PASS' if test3_success else '❌ FAIL'}")
    
    if test1_success and test2_success and test3_success:
        print("\n🎉 All tests passed! MCQ generation should work without safety filter issues.")
    else:
        print("\n⚠️ Some tests failed. The prompts may need further adjustment.")
        
        if not test1_success:
            print("   - Direct Ollama communication failed - check Ollama service")
        if not test2_success:
            print("   - Optimized MCQ generation failed - check vector stores and prompts")
        if not test3_success:
            print("   - Regular MCQ generation failed - check prompts and PDF processing")

if __name__ == "__main__":
    main()
