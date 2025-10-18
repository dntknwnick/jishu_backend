#!/usr/bin/env python3
"""
Diagnostic script to check ChromaDB collections
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from shared.services.multimodal_rag_service import get_multimodal_rag_service
from config import config

def check_collections():
    """Check what collections exist in ChromaDB"""
    
    app = create_app('development')
    
    with app.app_context():
        try:
            print("🔍 Checking ChromaDB collections...\n")
            
            chromadb_path = app.config.get('MULTIMODAL_CHROMADB_PATH')
            ollama_model = app.config.get('MULTIMODAL_OLLAMA_MODEL', 'llava')
            
            print(f"📁 ChromaDB Path: {chromadb_path}")
            print(f"🤖 Ollama Model: {ollama_model}\n")
            
            # Get the service
            service = get_multimodal_rag_service(
                chromadb_path=chromadb_path,
                ollama_model=ollama_model
            )
            
            # Check collections
            print("=" * 60)
            print("COLLECTIONS IN MEMORY:")
            print("=" * 60)
            
            if service.collections:
                for name, collection in service.collections.items():
                    try:
                        count = collection.count()
                        print(f"✅ {name}: {count} documents")
                    except Exception as e:
                        print(f"⚠️  {name}: Error getting count - {e}")
            else:
                print("❌ No collections loaded in memory")
            
            print("\n" + "=" * 60)
            print("COLLECTIONS IN CHROMADB:")
            print("=" * 60)
            
            try:
                all_collections = service.client.list_collections()
                print(f"Total collections: {len(all_collections)}\n")
                
                for collection in all_collections:
                    print(f"📚 Collection: {collection.name}")
                    try:
                        count = collection.count()
                        print(f"   Documents: {count}")
                    except Exception as e:
                        print(f"   Error: {e}")
            except Exception as e:
                print(f"❌ Error listing collections: {e}")
            
            print("\n" + "=" * 60)
            print("TESTING RETRIEVAL:")
            print("=" * 60)
            
            # Test retrieval for different subjects
            test_subjects = ['physics', 'chemistry', 'biology', 'mathematics', 'computer_science']
            
            for subject in test_subjects:
                print(f"\n🔍 Testing {subject}...")
                try:
                    result = service.generate_mcq(
                        query=subject,
                        subject=subject,
                        num_questions=2
                    )
                    
                    if result.get('success'):
                        print(f"   ✅ Generated {len(result.get('questions', []))} questions")
                    else:
                        print(f"   ❌ Error: {result.get('error')}")
                except Exception as e:
                    print(f"   ❌ Exception: {e}")
            
            return True
            
        except Exception as e:
            print(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()
            return False

if __name__ == '__main__':
    success = check_collections()
    sys.exit(0 if success else 1)

