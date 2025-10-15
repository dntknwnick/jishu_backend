#!/usr/bin/env python3
"""
Test Script for New RAG Pipeline
Validates MCQ generation, chatbot functionality, and vector store persistence
"""

import os
import sys
import time
import json
import requests
from pathlib import Path

# Add the parent directory to the path so we can import from shared
sys.path.append(str(Path(__file__).parent.parent))

# Configuration
BASE_URL = "http://localhost:5000"
TEST_SUBJECTS = ['physics', 'chemistry', 'biology', 'mathematics', 'computer_science']

def test_rag_status():
    """Test RAG system status endpoint"""
    print("🔍 Testing RAG Status Endpoint...")
    
    try:
        response = requests.get(f"{BASE_URL}/api/rag/status")
        
        if response.status_code == 200:
            data = response.json()
            if data['success']:
                status = data['data']
                print(f"✅ RAG Status: {status['system_status']}")
                print(f"📊 Health: {status['health']}")
                print(f"🔧 Dependencies: {status['dependencies']}")
                
                # Check vector stores
                vector_stores = status['vector_stores']
                available_subjects = []
                for subject, info in vector_stores.items():
                    if info['available']:
                        available_subjects.append(subject)
                        print(f"📚 {subject}: {info['document_count']} documents")
                    else:
                        print(f"❌ {subject}: not available")
                
                return available_subjects
            else:
                print(f"❌ RAG status failed: {data.get('message', 'Unknown error')}")
                return []
        else:
            print(f"❌ RAG status request failed: {response.status_code}")
            return []
            
    except Exception as e:
        print(f"❌ Error testing RAG status: {str(e)}")
        return []

def test_mcq_generation(subject: str, num_questions: int = 3):
    """Test MCQ generation for a specific subject"""
    print(f"\n🧠 Testing MCQ Generation for {subject}...")
    
    try:
        # Create test user first
        auth_response = requests.post(f"{BASE_URL}/api/create-test-user")
        if auth_response.status_code != 200:
            print(f"❌ Failed to create test user: {auth_response.status_code}")
            return False
        
        auth_data = auth_response.json()
        if not auth_data['success']:
            print(f"❌ Test user creation failed: {auth_data.get('message', 'Unknown error')}")
            return False
        
        access_token = auth_data['data']['access_token']
        headers = {'Authorization': f'Bearer {access_token}', 'Content-Type': 'application/json'}
        
        # Test MCQ generation
        mcq_data = {
            'subject': subject,
            'num_questions': num_questions,
            'difficulty': 'hard'
        }
        
        start_time = time.time()
        response = requests.post(f"{BASE_URL}/api/mcq/generate", 
                               json=mcq_data, headers=headers)
        generation_time = time.time() - start_time
        
        if response.status_code == 200:
            data = response.json()
            if data['success']:
                result = data['data']
                questions = result['questions']
                
                print(f"✅ Generated {len(questions)} questions in {generation_time:.2f}s")
                print(f"📊 Model: {result['model_used']}")
                print(f"📚 Sources: {len(result['sources_used'])} documents")
                print(f"💾 Saved to DB: {result['saved_to_database']}")
                
                # Validate question format
                for i, q in enumerate(questions[:2]):  # Show first 2 questions
                    print(f"\n📝 Question {i+1}:")
                    print(f"   Q: {q['question'][:100]}...")
                    print(f"   A: {q['option_a'][:50]}...")
                    print(f"   B: {q['option_b'][:50]}...")
                    print(f"   C: {q['option_c'][:50]}...")
                    print(f"   D: {q['option_d'][:50]}...")
                    print(f"   Correct: {q['correct_answer']}")
                    if q.get('explanation'):
                        print(f"   Explanation: {q['explanation'][:100]}...")
                
                return True
            else:
                print(f"❌ MCQ generation failed: {data.get('message', 'Unknown error')}")
                return False
        else:
            print(f"❌ MCQ generation request failed: {response.status_code}")
            if response.headers.get('content-type', '').startswith('application/json'):
                error_data = response.json()
                print(f"   Error: {error_data.get('message', 'Unknown error')}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing MCQ generation: {str(e)}")
        return False

def test_chatbot_query(subject: str = None):
    """Test chatbot query functionality"""
    print(f"\n🤖 Testing Chatbot Query...")
    
    try:
        # Create test user first
        auth_response = requests.post(f"{BASE_URL}/api/create-test-user")
        if auth_response.status_code != 200:
            print(f"❌ Failed to create test user: {auth_response.status_code}")
            return False
        
        auth_data = auth_response.json()
        if not auth_data['success']:
            print(f"❌ Test user creation failed: {auth_data.get('message', 'Unknown error')}")
            return False
        
        access_token = auth_data['data']['access_token']
        headers = {'Authorization': f'Bearer {access_token}', 'Content-Type': 'application/json'}
        
        # Test chatbot query
        query_data = {
            'query': 'What is Newton\'s first law of motion?',
            'subject': subject
        }
        
        start_time = time.time()
        response = requests.post(f"{BASE_URL}/api/chatbot/query", 
                               json=query_data, headers=headers)
        response_time = time.time() - start_time
        
        if response.status_code == 200:
            data = response.json()
            if data['success']:
                result = data['data']
                
                print(f"✅ Chatbot responded in {response_time:.2f}s")
                print(f"📊 Model: {result['model_used']}")
                print(f"📚 Sources: {len(result['sources'])} documents")
                print(f"🔍 Relevant docs: {result['relevant_docs']}")
                print(f"💬 Response: {result['response'][:200]}...")
                
                return True
            else:
                print(f"❌ Chatbot query failed: {data.get('message', 'Unknown error')}")
                return False
        else:
            print(f"❌ Chatbot query request failed: {response.status_code}")
            if response.headers.get('content-type', '').startswith('application/json'):
                error_data = response.json()
                print(f"   Error: {error_data.get('message', 'Unknown error')}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing chatbot query: {str(e)}")
        return False

def test_vector_store_persistence():
    """Test vector store persistence by checking if they exist"""
    print(f"\n💾 Testing Vector Store Persistence...")
    
    try:
        from shared.services.rag_service import get_rag_service
        
        rag_service = get_rag_service()
        status = rag_service.get_status()
        
        persistent_subjects = []
        for subject in TEST_SUBJECTS:
            vector_info = status['vector_stores'].get(subject, {})
            if vector_info.get('available', False):
                doc_count = vector_info.get('document_count', 0)
                if doc_count > 0:
                    persistent_subjects.append(subject)
                    print(f"✅ {subject}: {doc_count} documents persisted")
                else:
                    print(f"⚠️ {subject}: available but no documents")
            else:
                print(f"❌ {subject}: not available")
        
        if persistent_subjects:
            print(f"✅ Vector stores persistent for: {', '.join(persistent_subjects)}")
            return True
        else:
            print("❌ No persistent vector stores found")
            return False
            
    except Exception as e:
        print(f"❌ Error testing vector store persistence: {str(e)}")
        return False

def main():
    """Main test function"""
    print("🎯 RAG Pipeline Validation Test")
    print("=" * 50)
    
    # Test 1: RAG Status
    available_subjects = test_rag_status()
    if not available_subjects:
        print("❌ Cannot proceed without available vector stores")
        return False
    
    # Test 2: Vector Store Persistence
    persistence_ok = test_vector_store_persistence()
    
    # Test 3: MCQ Generation
    mcq_results = []
    for subject in available_subjects[:2]:  # Test first 2 available subjects
        result = test_mcq_generation(subject)
        mcq_results.append(result)
    
    # Test 4: Chatbot Query
    chatbot_result = test_chatbot_query(available_subjects[0] if available_subjects else None)
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 TEST SUMMARY")
    print("=" * 50)
    print(f"✅ RAG Status: {'PASS' if available_subjects else 'FAIL'}")
    print(f"✅ Vector Persistence: {'PASS' if persistence_ok else 'FAIL'}")
    print(f"✅ MCQ Generation: {'PASS' if any(mcq_results) else 'FAIL'}")
    print(f"✅ Chatbot Query: {'PASS' if chatbot_result else 'FAIL'}")
    
    overall_success = (
        bool(available_subjects) and 
        persistence_ok and 
        any(mcq_results) and 
        chatbot_result
    )
    
    if overall_success:
        print("\n🎉 All tests PASSED! RAG pipeline is working correctly.")
        return True
    else:
        print("\n❌ Some tests FAILED. Please check the issues above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
