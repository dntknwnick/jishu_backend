#!/usr/bin/env python3
"""
Simple script to check vector store counts
"""

import os
import pickle
from pathlib import Path

def main():
    print("=" * 60)
    print("📊 VECTOR STORE INDEX COUNTS")
    print("=" * 60)
    
    vector_store_path = Path("./vector_stores")
    
    if not vector_store_path.exists():
        print("❌ Vector stores directory not found!")
        return
    
    subjects = ['physics', 'chemistry', 'biology', 'mathematics']
    
    for subject in subjects:
        print(f"\n🔍 {subject.upper()}:")
        
        index_file = vector_store_path / f"{subject}_index.faiss"
        docs_file = vector_store_path / f"{subject}_docs.pkl"
        meta_file = vector_store_path / f"{subject}_meta.pkl"
        
        if index_file.exists():
            print(f"   ✅ Index file exists: {index_file.stat().st_size / (1024*1024):.2f} MB")
        else:
            print(f"   ❌ Index file missing")
            
        if docs_file.exists():
            try:
                with open(docs_file, 'rb') as f:
                    documents = pickle.load(f)
                print(f"   ✅ Documents: {len(documents):,}")
            except Exception as e:
                print(f"   ❌ Error reading docs: {str(e)}")
        else:
            print(f"   ❌ Docs file missing")
            
        if meta_file.exists():
            try:
                with open(meta_file, 'rb') as f:
                    metadata = pickle.load(f)
                print(f"   ✅ Chunks: {metadata.get('chunk_count', 'Unknown'):,}")
                print(f"   📅 Created: {metadata.get('created_at', 'Unknown')}")
            except Exception as e:
                print(f"   ❌ Error reading meta: {str(e)}")
        else:
            print(f"   ❌ Meta file missing")
    
    # Try to load FAISS and check index counts
    print(f"\n🔢 FAISS INDEX COUNTS:")
    try:
        import faiss
        print(f"   ✅ FAISS version: {faiss.__version__}")
        
        for subject in subjects:
            index_file = vector_store_path / f"{subject}_index.faiss"
            if index_file.exists():
                try:
                    index = faiss.read_index(str(index_file))
                    print(f"   📊 {subject}: {index.ntotal:,} embeddings")
                except Exception as e:
                    print(f"   ❌ {subject}: Error reading index - {str(e)}")
            else:
                print(f"   ⚠️ {subject}: No index file")
                
    except ImportError:
        print(f"   ❌ FAISS not available")
    except Exception as e:
        print(f"   ❌ Error with FAISS: {str(e)}")

if __name__ == "__main__":
    main()
