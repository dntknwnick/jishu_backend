#!/usr/bin/env python3
"""
Simple API integration test
"""

import sys
import os

# Add the parent directory to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def main():
    print("🧪 Simple API Integration Test")
    
    try:
        from shared.services.ai_service import AIService
        print("✅ AI Service imported successfully")
        
        # Initialize service
        ai_service = AIService(
            pdf_folder_path="./pdfs",
            ollama_model="llama3.2:1b"
        )
        print("✅ AI Service initialized")
        
        # Get status
        status = ai_service.get_status()
        print(f"📊 Status: {status}")
        
        # Test optimized service import
        try:
            from shared.services.optimized_ai_service import get_optimized_ai_service
            print("✅ Optimized AI Service imported successfully")
            
            optimized_service = get_optimized_ai_service(
                pdf_folder_path="./pdfs",
                ollama_model="llama3.2:1b"
            )
            print("✅ Optimized AI Service initialized")
            
            opt_status = optimized_service.get_status()
            print(f"📊 Optimized Status: {opt_status}")
            
        except Exception as e:
            print(f"❌ Optimized service error: {str(e)}")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
