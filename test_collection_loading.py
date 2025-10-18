#!/usr/bin/env python3
"""
Test script to verify ChromaDB collection loading works correctly
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Suppress warnings
import warnings
warnings.filterwarnings('ignore')

from app import create_app
from config import config

def test_collection_loading():
    """Test that collections load correctly"""
    
    app = create_app('development')
    
    with app.app_context():
        try:
            print("=" * 70)
            print("🔍 Testing ChromaDB Collection Loading")
            print("=" * 70)
            
            chromadb_path = app.config.get('MULTIMODAL_CHROMADB_PATH')
            ollama_model = app.config.get('MULTIMODAL_OLLAMA_MODEL', 'llava')
            
            print(f"\n📁 ChromaDB Path: {chromadb_path}")
            print(f"🤖 Ollama Model: {ollama_model}\n")
            
            # Import and get the service
            from shared.services.multimodal_rag_service import get_multimodal_rag_service
            
            print("🚀 Initializing MultimodalRAGService...")
            service = get_multimodal_rag_service(
                chromadb_path=chromadb_path,
                ollama_model=ollama_model
            )
            
            print("\n" + "=" * 70)
            print("COLLECTIONS LOADED IN MEMORY:")
            print("=" * 70)
            
            if service.collections:
                print(f"\n✅ Successfully loaded {len(service.collections)} collections:\n")
                for name, collection in service.collections.items():
                    try:
                        count = collection.count()
                        print(f"   📚 {name}: {count} documents")
                    except Exception as e:
                        print(f"   ⚠️  {name}: Error getting count - {e}")
            else:
                print("\n❌ No collections loaded!")
                return False
            
            print("\n" + "=" * 70)
            print("TESTING MCQ GENERATION:")
            print("=" * 70)
            
            # Test MCQ generation for physics
            print("\n🔬 Testing Physics MCQ generation...")
            result = service.generate_mcq(
                query='physics',
                subject='physics',
                num_questions=5
            )
            
            if result.get('success'):
                questions = result.get('questions', [])
                print(f"✅ SUCCESS: Generated {len(questions)} questions")
                
                if questions:
                    q = questions[0]
                    print(f"\n📝 Sample Question:")
                    print(f"   Question: {q.get('question', 'N/A')[:80]}...")
                    print(f"   Option A: {q.get('option_a', 'N/A')[:50]}...")
                    print(f"   Correct Answer: {q.get('correct_answer', 'N/A')}")
            else:
                print(f"❌ FAILED: {result.get('error')}")
                return False
            
            print("\n" + "=" * 70)
            print("✅ ALL TESTS PASSED!")
            print("=" * 70)
            return True
            
        except Exception as e:
            print(f"\n❌ Error: {e}")
            import traceback
            traceback.print_exc()
            return False

if __name__ == '__main__':
    success = test_collection_loading()
    sys.exit(0 if success else 1)

