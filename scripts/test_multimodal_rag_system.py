"""
Test script for Multimodal RAG System
Tests MCQ generation and chat responses using CLIP + ChromaDB + Ollama Qwen2-VL
"""

import os
import sys
import json
import time
import logging

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import Config
from shared.services.multimodal_rag_service import get_multimodal_rag_service

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def test_multimodal_rag_system():
    """Test the multimodal RAG system"""
    
    logger.info("=" * 70)
    logger.info("🧪 Testing Multimodal RAG System")
    logger.info("=" * 70)

    # Check configuration
    logger.info("\n📋 Configuration Check:")
    logger.info(f"   Multimodal RAG Enabled: {Config.MULTIMODAL_RAG_ENABLED}")
    logger.info(f"   ChromaDB Path: {Config.MULTIMODAL_CHROMADB_PATH}")
    logger.info(f"   CLIP Model: {Config.MULTIMODAL_CLIP_MODEL}")
    logger.info(f"   Ollama Model: {Config.MULTIMODAL_OLLAMA_MODEL}")
    logger.info(f"   Chunk Size: {Config.MULTIMODAL_CHUNK_SIZE}")
    logger.info(f"   Top K Retrieval: {Config.MULTIMODAL_TOP_K_RETRIEVAL}")

    if not Config.MULTIMODAL_RAG_ENABLED:
        logger.error("❌ Multimodal RAG is disabled!")
        return False

    # Initialize service
    logger.info("\n🔧 Initializing MultimodalRAGService...")
    try:
        service = get_multimodal_rag_service(
            chromadb_path=Config.MULTIMODAL_CHROMADB_PATH,
            ollama_model=Config.MULTIMODAL_OLLAMA_MODEL
        )
        logger.info("✅ Service initialized successfully")
    except Exception as e:
        logger.error(f"❌ Failed to initialize service: {e}")
        return False

    # Test MCQ Generation
    logger.info("\n" + "=" * 70)
    logger.info("🧪 Test 1: MCQ Generation")
    logger.info("=" * 70)

    test_subjects = ['physics', 'chemistry', 'biology']
    mcq_results = {}

    for subject in test_subjects:
        logger.info(f"\n📚 Testing MCQ generation for {subject}...")
        
        try:
            start_time = time.time()
            
            result = service.generate_mcq(
                query=subject,
                subject=subject,
                num_questions=3
            )
            
            generation_time = time.time() - start_time
            
            if result['success']:
                questions = result.get('questions', [])
                logger.info(f"✅ Generated {len(questions)} MCQ questions in {generation_time:.2f}s")
                
                # Validate MCQ format
                valid_count = 0
                for i, q in enumerate(questions):
                    if all(key in q for key in ['question', 'option_a', 'option_b', 'option_c', 'option_d', 'correct_answer']):
                        valid_count += 1
                        logger.info(f"   Question {i+1}: ✅ Valid format")
                    else:
                        logger.warning(f"   Question {i+1}: ⚠️ Invalid format - missing keys")
                
                mcq_results[subject] = {
                    'success': True,
                    'total_generated': len(questions),
                    'valid_format': valid_count,
                    'generation_time': generation_time,
                    'model': result.get('model_used', 'unknown')
                }
            else:
                logger.error(f"❌ Failed to generate MCQ: {result.get('error', 'Unknown error')}")
                mcq_results[subject] = {
                    'success': False,
                    'error': result.get('error', 'Unknown error')
                }
                
        except Exception as e:
            logger.error(f"❌ Exception during MCQ generation: {e}")
            mcq_results[subject] = {
                'success': False,
                'error': str(e)
            }

    # Test Chat Response
    logger.info("\n" + "=" * 70)
    logger.info("🧪 Test 2: Chat Response Generation")
    logger.info("=" * 70)

    test_queries = [
        ("What is photosynthesis?", "biology"),
        ("Explain Newton's laws of motion", "physics"),
        ("What is the periodic table?", "chemistry")
    ]

    chat_results = {}

    for query, subject in test_queries:
        logger.info(f"\n💬 Testing chat for: {query} ({subject})")
        
        try:
            start_time = time.time()
            
            result = service.generate_chat_response(
                query=query,
                subject=subject
            )
            
            response_time = time.time() - start_time
            
            if result['success']:
                response = result.get('response', '')
                logger.info(f"✅ Generated response in {response_time:.2f}s")
                logger.info(f"   Response length: {len(response)} characters")
                logger.info(f"   Model: {result.get('model_used', 'unknown')}")
                
                chat_results[query] = {
                    'success': True,
                    'response_length': len(response),
                    'response_time': response_time,
                    'model': result.get('model_used', 'unknown')
                }
            else:
                logger.error(f"❌ Failed to generate response: {result.get('error', 'Unknown error')}")
                chat_results[query] = {
                    'success': False,
                    'error': result.get('error', 'Unknown error')
                }
                
        except Exception as e:
            logger.error(f"❌ Exception during chat generation: {e}")
            chat_results[query] = {
                'success': False,
                'error': str(e)
            }

    # Summary
    logger.info("\n" + "=" * 70)
    logger.info("📊 Test Summary")
    logger.info("=" * 70)

    logger.info("\n📚 MCQ Generation Results:")
    mcq_success = sum(1 for r in mcq_results.values() if r.get('success'))
    logger.info(f"   Successful: {mcq_success}/{len(mcq_results)}")
    for subject, result in mcq_results.items():
        if result.get('success'):
            logger.info(f"   ✅ {subject}: {result['total_generated']} questions, {result['generation_time']:.2f}s")
        else:
            logger.info(f"   ❌ {subject}: {result.get('error', 'Unknown error')}")

    logger.info("\n💬 Chat Response Results:")
    chat_success = sum(1 for r in chat_results.values() if r.get('success'))
    logger.info(f"   Successful: {chat_success}/{len(chat_results)}")
    for query, result in chat_results.items():
        if result.get('success'):
            logger.info(f"   ✅ {query}: {result['response_time']:.2f}s")
        else:
            logger.info(f"   ❌ {query}: {result.get('error', 'Unknown error')}")

    logger.info("\n" + "=" * 70)
    
    # Overall result
    all_success = mcq_success == len(mcq_results) and chat_success == len(chat_results)
    if all_success:
        logger.info("✅ All tests passed!")
        return True
    else:
        logger.warning("⚠️ Some tests failed - check configuration and PDF availability")
        return False


if __name__ == "__main__":
    logger.info("Starting Multimodal RAG System Tests...\n")
    success = test_multimodal_rag_system()
    sys.exit(0 if success else 1)

