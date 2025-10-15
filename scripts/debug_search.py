#!/usr/bin/env python3
"""
Debug script to test vector search functionality
"""

import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_search():
    """Test the search functionality"""
    try:
        from shared.services.rag_service import get_rag_service
        
        print("🔍 Testing vector search functionality...")
        
        # Initialize RAG service with low threshold
        rag_service = get_rag_service(
            ollama_model="llama3.2:1b",
            top_k_results=5,
            similarity_threshold=0.0  # Very low threshold
        )
        
        # Check what subjects are available
        print(f"Available subjects: {rag_service.subjects}")
        
        # Check collections
        chroma_client = rag_service.model_service.get_chroma_client()
        collections = chroma_client.list_collections()
        print(f"Available collections: {[c.name for c in collections]}")
        
        # Test specific collection
        try:
            math_collection = chroma_client.get_collection("subject_mathematics")
            count = math_collection.count()
            print(f"Mathematics collection has {count} documents")
            
            # Get a sample document to see what's in there
            sample = math_collection.peek(limit=3)
            print(f"Sample documents: {len(sample['documents'])} docs")
            if sample['documents']:
                print(f"First document preview: {sample['documents'][0][:200]}...")
        except Exception as e:
            print(f"Error accessing mathematics collection: {e}")
        
        # Test different search queries
        test_queries = [
            "algebra",
            "equation",
            "mathematics",
            "number",
            "calculate",
            "formula",
            "solve",
            "linear algebra",
            "quadratic equation"
        ]
        
        for query in test_queries:
            print(f"\n🔍 Testing query: '{query}'")
            results = rag_service.search_similar_content(query, "mathematics", top_k=3)
            print(f"  Results found: {len(results)}")
            
            if results:
                for i, result in enumerate(results[:2]):
                    print(f"  Result {i+1}: {result.get('content', '')[:100]}...")
                    print(f"    Similarity: {result.get('similarity', 'N/A')}")
                break  # Stop after first successful query
            else:
                # Test raw ChromaDB query to see actual distances
                try:
                    math_collection = chroma_client.get_collection("subject_mathematics")
                    embedding_model = rag_service.model_service.get_embedding_model()
                    query_embedding = embedding_model.encode([query])[0].tolist()

                    raw_results = math_collection.query(
                        query_embeddings=[query_embedding],
                        n_results=3,
                        include=['documents', 'metadatas', 'distances']
                    )

                    print(f"  Raw ChromaDB results for '{query}':")
                    for i, (doc, distance) in enumerate(zip(raw_results['documents'][0], raw_results['distances'][0])):
                        similarity = 1 - distance
                        print(f"    Result {i+1}: distance={distance:.4f}, similarity={similarity:.4f}")
                        print(f"      Content: {doc[:100]}...")

                except Exception as e:
                    print(f"  Error in raw query: {e}")
        
        # Test without specifying subject
        print(f"\n🔍 Testing query without subject: 'mathematics'")
        results = rag_service.search_similar_content("mathematics", top_k=3)
        print(f"  Results found: {len(results)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error during search test: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_search()
