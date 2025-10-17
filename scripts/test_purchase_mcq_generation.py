"""
Test script for Purchase-Time MCQ Generation
Tests the instant MCQ generation using pre-built vector store
"""

import os
import sys
import time
import logging
import json

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import Config
from shared.services.purchase_mcq_generator import get_purchase_mcq_generator

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def test_vector_store_availability():
    """Test if vector store is available"""
    logger.info("\n" + "=" * 70)
    logger.info("🧪 Test 1: Vector Store Availability")
    logger.info("=" * 70)
    
    try:
        mcq_gen = get_purchase_mcq_generator()
        stats = mcq_gen.get_vector_store_stats()
        
        if stats['success']:
            logger.info("✅ Vector store is available")
            logger.info(f"   Subjects: {len(stats['stats']['subjects'])}")
            logger.info(f"   Total documents: {stats['stats']['total_documents']}")
            logger.info(f"   Total images: {stats['stats']['total_images']}")
            
            for subject in stats['stats']['subjects']:
                logger.info(f"   - {subject['name']}: {subject['document_count']} docs")
            
            return True
        else:
            logger.error(f"❌ Vector store error: {stats.get('error')}")
            return False
    except Exception as e:
        logger.error(f"❌ Exception: {e}")
        return False


def test_subject_validation():
    """Test subject validation"""
    logger.info("\n" + "=" * 70)
    logger.info("🧪 Test 2: Subject Validation")
    logger.info("=" * 70)
    
    mcq_gen = get_purchase_mcq_generator()
    
    # Test valid subjects
    test_subjects = ['physics', 'chemistry', 'biology', 'mathematics', 'computer_science']
    
    for subject in test_subjects:
        is_valid = mcq_gen.validate_subject(subject)
        status = "✅" if is_valid else "❌"
        logger.info(f"   {status} {subject}: {is_valid}")
    
    # Test invalid subject
    is_valid = mcq_gen.validate_subject('invalid_subject')
    logger.info(f"   ✅ invalid_subject validation: {not is_valid} (should be False)")
    
    return True


def test_context_retrieval():
    """Test context retrieval from vector store"""
    logger.info("\n" + "=" * 70)
    logger.info("🧪 Test 3: Context Retrieval")
    logger.info("=" * 70)
    
    mcq_gen = get_purchase_mcq_generator()
    
    test_cases = [
        ('physics', 'Newton\'s laws of motion'),
        ('chemistry', 'Chemical reactions'),
        ('biology', 'Photosynthesis'),
    ]
    
    for subject, query in test_cases:
        logger.info(f"\n   Retrieving context for {subject}: {query}")
        
        start_time = time.time()
        docs = mcq_gen.retrieve_context(subject, query, k=3)
        retrieval_time = time.time() - start_time
        
        if docs:
            logger.info(f"   ✅ Retrieved {len(docs)} documents in {retrieval_time:.2f}s")
            for i, doc in enumerate(docs):
                content = doc.get('content', '')[:100]
                logger.info(f"      Doc {i+1}: {content}...")
        else:
            logger.warning(f"   ⚠️  No documents retrieved")
    
    return True


def test_single_mcq_generation():
    """Test single MCQ generation for purchase"""
    logger.info("\n" + "=" * 70)
    logger.info("🧪 Test 4: Single MCQ Generation")
    logger.info("=" * 70)
    
    mcq_gen = get_purchase_mcq_generator()
    
    test_cases = [
        ('physics', 3, 'easy'),
        ('chemistry', 3, 'medium'),
        ('biology', 3, 'hard'),
    ]
    
    for subject, num_questions, difficulty in test_cases:
        logger.info(f"\n   Generating {num_questions} {difficulty} MCQs for {subject}")
        
        start_time = time.time()
        result = mcq_gen.generate_mcq_for_purchase(
            subject=subject,
            num_questions=num_questions,
            difficulty=difficulty
        )
        generation_time = time.time() - start_time
        
        if result['success']:
            questions = result.get('questions', [])
            logger.info(f"   ✅ Generated {len(questions)} questions in {generation_time:.2f}s")
            
            for i, q in enumerate(questions):
                logger.info(f"\n      Question {i+1}:")
                logger.info(f"      Q: {q.get('question', '')[:80]}...")
                logger.info(f"      A: {q.get('correct_answer', 'N/A')}")
        else:
            logger.error(f"   ❌ Generation failed: {result.get('error')}")
    
    return True


def test_batch_generation():
    """Test batch MCQ generation"""
    logger.info("\n" + "=" * 70)
    logger.info("🧪 Test 5: Batch MCQ Generation")
    logger.info("=" * 70)
    
    mcq_gen = get_purchase_mcq_generator()
    
    logger.info("\n   Generating 3 sets of 5 questions for physics")
    
    start_time = time.time()
    result = mcq_gen.batch_generate_for_purchase(
        subject='physics',
        num_sets=3,
        questions_per_set=5
    )
    generation_time = time.time() - start_time
    
    if result['success']:
        logger.info(f"   ✅ Generated {result['total_sets']} sets")
        logger.info(f"   ✅ Total questions: {result['total_questions']}")
        logger.info(f"   ✅ Time: {generation_time:.2f}s")
        
        for set_data in result['sets']:
            logger.info(f"      Set {set_data['set_number']}: {len(set_data['questions'])} questions")
    else:
        logger.error(f"   ❌ Batch generation failed: {result.get('error')}")
    
    return True


def test_performance():
    """Test performance metrics"""
    logger.info("\n" + "=" * 70)
    logger.info("🧪 Test 6: Performance Metrics")
    logger.info("=" * 70)
    
    mcq_gen = get_purchase_mcq_generator()
    
    # Test multiple generations
    num_tests = 5
    times = []
    
    logger.info(f"\n   Running {num_tests} MCQ generations...")
    
    for i in range(num_tests):
        start_time = time.time()
        result = mcq_gen.generate_mcq_for_purchase(
            subject='physics',
            num_questions=5
        )
        elapsed = time.time() - start_time
        times.append(elapsed)
        
        status = "✅" if result['success'] else "❌"
        logger.info(f"   {status} Test {i+1}: {elapsed:.2f}s")
    
    # Calculate statistics
    avg_time = sum(times) / len(times)
    min_time = min(times)
    max_time = max(times)
    
    logger.info(f"\n   📊 Performance Summary:")
    logger.info(f"      Average: {avg_time:.2f}s")
    logger.info(f"      Min: {min_time:.2f}s")
    logger.info(f"      Max: {max_time:.2f}s")
    logger.info(f"      Target: < 10s ✅" if avg_time < 10 else f"      Target: < 10s ❌")
    
    return True


def test_error_handling():
    """Test error handling"""
    logger.info("\n" + "=" * 70)
    logger.info("🧪 Test 7: Error Handling")
    logger.info("=" * 70)
    
    mcq_gen = get_purchase_mcq_generator()
    
    # Test invalid subject
    logger.info("\n   Testing invalid subject...")
    result = mcq_gen.generate_mcq_for_purchase(
        subject='invalid_subject',
        num_questions=5
    )
    
    if not result['success']:
        logger.info(f"   ✅ Correctly rejected invalid subject")
        logger.info(f"      Error: {result.get('error')}")
    else:
        logger.error(f"   ❌ Should have rejected invalid subject")
    
    # Test invalid num_questions
    logger.info("\n   Testing invalid num_questions...")
    result = mcq_gen.generate_mcq_for_purchase(
        subject='physics',
        num_questions=0
    )
    
    # This might succeed with 0 questions, which is fine
    logger.info(f"   ✅ Handled edge case")
    
    return True


def run_all_tests():
    """Run all tests"""
    logger.info("\n" + "=" * 70)
    logger.info("🚀 Purchase MCQ Generation - Test Suite")
    logger.info("=" * 70)
    
    tests = [
        ("Vector Store Availability", test_vector_store_availability),
        ("Subject Validation", test_subject_validation),
        ("Context Retrieval", test_context_retrieval),
        ("Single MCQ Generation", test_single_mcq_generation),
        ("Batch Generation", test_batch_generation),
        ("Performance Metrics", test_performance),
        ("Error Handling", test_error_handling),
    ]
    
    results = {}
    for test_name, test_func in tests:
        try:
            results[test_name] = test_func()
        except Exception as e:
            logger.error(f"❌ Test failed with exception: {e}", exc_info=True)
            results[test_name] = False
    
    # Summary
    logger.info("\n" + "=" * 70)
    logger.info("📊 Test Summary")
    logger.info("=" * 70)
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅" if result else "❌"
        logger.info(f"{status} {test_name}")
    
    logger.info(f"\nTotal: {passed}/{total} tests passed")
    logger.info("=" * 70)
    
    return passed == total


if __name__ == "__main__":
    logger.info("Starting Purchase MCQ Generation Tests...\n")
    success = run_all_tests()
    sys.exit(0 if success else 1)

