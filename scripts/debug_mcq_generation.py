#!/usr/bin/env python3
"""
Debug script to see what the AI is actually generating for MCQ questions
"""

import sys
import os
import time
import json

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def debug_mcq_generation():
    """Debug MCQ generation to see raw AI response"""
    try:
        from shared.services.rag_service import get_rag_service
        
        print("🔍 Debugging MCQ generation - checking raw AI response...")
        
        # Initialize RAG service
        rag = get_rag_service()
        
        # Get the model service and clients
        model_service = rag.model_service
        ollama_client = model_service.get_ollama_client()
        
        if not ollama_client:
            print("❌ Ollama client not available")
            return False
            
        # Get relevant content for physics
        print("\n📚 Getting relevant content...")
        relevant_docs = rag.search_similar_content("physics", "physics", top_k=3)
        print(f"Found {len(relevant_docs)} relevant documents")
        
        if not relevant_docs:
            print("❌ No relevant content found")
            return False
            
        # Prepare context
        context = "\n\n".join([
            f"From {doc['metadata']['source_file']}:\n{doc['content'][:800]}"
            for doc in relevant_docs
        ])
        
        print(f"Context length: {len(context)} characters")
        
        # Create the prompt (simplified version)
        prompt = f"""Based on the following physics content, generate 5 multiple choice questions in JSON format.

Context:
{context[:1500]}

Generate exactly 5 physics questions in this JSON format:
[
  {{
    "question": "What is the definition of velocity?",
    "option_a": "Rate of change of position",
    "option_b": "Rate of change of acceleration", 
    "option_c": "Rate of change of momentum",
    "option_d": "Rate of change of energy",
    "correct_answer": "A",
    "explanation": "Velocity is defined as the rate of change of position with respect to time."
  }}
]

Requirements:
- Questions must be medium difficulty level
- All questions must be based on the provided context
- Each question must have exactly 4 options (A, B, C, D)
- Provide clear explanations for correct answers
- Return ONLY valid JSON, no additional text"""

        print(f"\n📝 Prompt length: {len(prompt)} characters")
        
        # Generate response
        print("\n🤖 Generating AI response...")
        start_time = time.time()
        
        response = ollama_client.generate(
            model=rag.ollama_model,
            prompt=prompt,
            options={
                'temperature': 0.7,
                'top_p': 0.9,
                'num_predict': 3000,  # Larger for 5 questions
                'top_k': 40,
                'repeat_penalty': 1.1
            }
        )
        
        generation_time = time.time() - start_time
        ai_response = response['response']
        
        print(f"⏱️ Generation time: {generation_time:.2f}s")
        print(f"📄 Response length: {len(ai_response)} characters")
        
        # Show raw response
        print(f"\n🔍 Raw AI Response:")
        print("=" * 50)
        print(ai_response)
        print("=" * 50)
        
        # Try to parse JSON
        print(f"\n🧪 Attempting to parse JSON...")
        
        # Look for JSON array
        json_start = ai_response.find('[')
        json_end = ai_response.rfind(']') + 1
        
        print(f"JSON start position: {json_start}")
        print(f"JSON end position: {json_end}")
        
        if json_start != -1 and json_end > 0:
            json_str = ai_response[json_start:json_end]
            print(f"\nExtracted JSON string:")
            print("-" * 30)
            print(json_str)
            print("-" * 30)
            
            try:
                questions = json.loads(json_str)
                print(f"✅ JSON parsing successful!")
                print(f"📊 Found {len(questions)} questions")
                
                # Validate structure
                for i, q in enumerate(questions):
                    print(f"\nQuestion {i+1} structure:")
                    required_keys = ['question', 'option_a', 'option_b', 'option_c', 'option_d', 'correct_answer']
                    for key in required_keys:
                        status = "✅" if key in q else "❌"
                        print(f"  {status} {key}")
                        
            except json.JSONDecodeError as e:
                print(f"❌ JSON parsing failed: {str(e)}")
                
        else:
            print("❌ No JSON array found in response")
            
        return True
        
    except Exception as e:
        print(f"❌ Debug failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    debug_mcq_generation()
