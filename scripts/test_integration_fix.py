#!/usr/bin/env python3
"""
Test the specific integration fix for the API issue
"""

import sys
import os
import time

# Add the parent directory to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_integration_fix():
    """Test the specific integration issue that was failing"""
    print("🧪 Testing Integration Fix...")
    
    try:
        from shared.services.ai_service import AIService
        
        # Initialize AI service (exactly like in the API)
        ai_service = AIService(
            pdf_folder_path="./pdfs",
            ollama_model="llama3.2:1b"
        )
        
        print("✅ AI service initialized")
        
        # Test the exact call that was failing in the API
        print(f"\n🚀 Testing generate_mcq_from_pdfs_fast (API method)...")
        print(f"   📊 Questions: 3, Subject: Physics")
        
        start_time = time.time()
        result = ai_service.generate_mcq_from_pdfs_fast(
            num_questions=3,  # Small number for quick test
            subject_name='Physics',  # Exact format from API
            difficulty='hard'
        )
        end_time = time.time()
        
        print(f"⏱️ Total time: {end_time - start_time:.2f} seconds")
        
        if result.get('success'):
            questions = result.get('questions', [])
            print(f"✅ SUCCESS: Generated {len(questions)} questions")
            
            # Check if it used optimized approach
            if end_time - start_time < 30:  # If less than 30 seconds, likely optimized
                print("🚀 Likely used optimized approach (fast generation)")
            else:
                print("🐌 Likely used legacy approach (slow generation)")
            
            # Display sample question
            if questions:
                q = questions[0]
                question_text = q.get('question', '')
                print(f"\n📝 Sample Question: {question_text[:100]}...")
                
                # Check for safety filter issues
                if "can't assist" in question_text.lower() or "discriminatory" in question_text.lower():
                    print("⚠️ Safety filter detected")
                    return False
                else:
                    print("✅ No safety filter issues detected")
            
            return True
        else:
            error_msg = result.get('error', 'Unknown error')
            print(f"❌ FAILED: {error_msg}")
            return False
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main test function"""
    print("=" * 60)
    print("🔧 INTEGRATION FIX TEST")
    print("=" * 60)
    print("Testing the fix for the API integration issue...")
    print()
    
    success = test_integration_fix()
    
    print("\n" + "=" * 60)
    print("📊 RESULT")
    print("=" * 60)
    
    if success:
        print("🎉 SUCCESS! Integration fix is working!")
        print("✅ The API should now use optimized MCQ generation")
        print("⚡ Expected performance: 15-20 seconds instead of 60+ seconds")
    else:
        print("❌ FAILED! Integration issue still exists")
        print("🔧 Check the error messages above for details")

if __name__ == "__main__":
    main()
