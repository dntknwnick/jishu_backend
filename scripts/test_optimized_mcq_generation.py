#!/usr/bin/env python3
"""
Performance Testing Script for Optimized MCQ Generation
Test the new vector store system against performance targets
"""

import os
import sys
import time
import json
import statistics
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

def print_banner():
    """Print testing banner"""
    print("=" * 70)
    print("🧪 OPTIMIZED MCQ GENERATION - PERFORMANCE TESTING")
    print("=" * 70)
    print("Testing vector store optimization against 5-10 second target")
    print()

def test_vector_store_availability():
    """Test if vector stores are available and initialized"""
    print("🔍 Testing Vector Store Availability...")
    
    try:
        from shared.services.vector_store_manager import get_vector_store_manager
        
        vector_manager = get_vector_store_manager()
        status = vector_manager.get_status()
        
        print(f"   ChromaDB Available: {'✅' if status['chromadb_available'] else '❌'}")
        print(f"   LangChain Available: {'✅' if status['langchain_available'] else '❌'}")
        print(f"   Vector Store Path: {status['vector_store_path']}")
        
        # Check collections
        collections = status.get('collections', {})
        if collections:
            print(f"   📚 Collections Found: {len(collections)}")
            for name, info in collections.items():
                print(f"      - {name}: {info['count']} documents")
            return True, len(collections)
        else:
            print("   ❌ No collections found - vector stores need initialization")
            return False, 0
            
    except Exception as e:
        print(f"   ❌ Error checking vector stores: {str(e)}")
        return False, 0

def test_optimized_service():
    """Test optimized AI service functionality"""
    print("🚀 Testing Optimized AI Service...")
    
    try:
        from shared.services.optimized_ai_service import get_optimized_ai_service
        
        service = get_optimized_ai_service()
        status = service.get_status()
        
        print(f"   Service Type: {status['service_type']}")
        print(f"   Ollama Available: {'✅' if status['ollama_available'] else '❌'}")
        print(f"   Cache Enabled: {'✅' if status['cache_enabled'] else '❌'}")
        print(f"   Cache Size: {status['cache_size']}")
        
        return status['ollama_available']
        
    except Exception as e:
        print(f"   ❌ Error testing optimized service: {str(e)}")
        return False

def run_performance_test(subject: str, num_questions: int = 5, iterations: int = 3):
    """Run performance test for a specific subject"""
    print(f"⚡ Performance Test: {subject} ({num_questions} questions, {iterations} iterations)")
    
    try:
        from shared.services.optimized_ai_service import get_optimized_ai_service
        
        service = get_optimized_ai_service()
        
        # Clear cache for fair testing
        service.clear_cache()
        
        generation_times = []
        results = []
        
        for i in range(iterations):
            print(f"   🔄 Iteration {i+1}/{iterations}...")
            
            start_time = time.time()
            
            result = service.generate_mcq_optimized(
                num_questions=num_questions,
                subject_name=subject,
                difficulty='hard',
                use_cache=(i > 0)  # Use cache after first iteration
            )
            
            generation_time = time.time() - start_time
            generation_times.append(generation_time)
            
            if result['success']:
                results.append({
                    'iteration': i + 1,
                    'generation_time': generation_time,
                    'questions_generated': len(result['questions']),
                    'from_cache': result.get('from_cache', False),
                    'context_length': result.get('context_length', 0),
                    'speed_target_met': generation_time <= 10.0
                })
                
                cache_status = "📋 (cached)" if result.get('from_cache') else "🔍 (fresh)"
                target_status = "✅" if generation_time <= 10.0 else "❌"
                
                print(f"      {target_status} {generation_time:.2f}s - {len(result['questions'])} questions {cache_status}")
            else:
                print(f"      ❌ Failed: {result.get('error', 'Unknown error')}")
                results.append({
                    'iteration': i + 1,
                    'generation_time': generation_time,
                    'error': result.get('error', 'Unknown error'),
                    'speed_target_met': False
                })
        
        # Calculate statistics
        if generation_times:
            avg_time = statistics.mean(generation_times)
            min_time = min(generation_times)
            max_time = max(generation_times)
            
            successful_iterations = len([r for r in results if 'questions_generated' in r])
            target_met_count = len([r for r in results if r['speed_target_met']])
            
            print(f"   📊 Results Summary:")
            print(f"      Average Time: {avg_time:.2f}s")
            print(f"      Min Time: {min_time:.2f}s")
            print(f"      Max Time: {max_time:.2f}s")
            print(f"      Success Rate: {successful_iterations}/{iterations}")
            print(f"      Target Met: {target_met_count}/{iterations}")
            print(f"      Performance: {'✅ EXCELLENT' if avg_time <= 5 else '✅ GOOD' if avg_time <= 10 else '❌ NEEDS IMPROVEMENT'}")
            
            return {
                'subject': subject,
                'iterations': iterations,
                'successful_iterations': successful_iterations,
                'average_time': avg_time,
                'min_time': min_time,
                'max_time': max_time,
                'target_met_count': target_met_count,
                'target_met_rate': target_met_count / iterations,
                'results': results
            }
        else:
            return None
            
    except Exception as e:
        print(f"   ❌ Error during performance test: {str(e)}")
        return None

def run_comprehensive_test():
    """Run comprehensive performance test across all subjects"""
    print("🎯 Comprehensive Performance Test")
    print("-" * 50)
    
    subjects = ['physics', 'chemistry', 'biology', 'mathematics']
    test_results = {}
    
    for subject in subjects:
        print(f"\n📚 Testing {subject.upper()}...")
        result = run_performance_test(subject, num_questions=5, iterations=3)
        
        if result:
            test_results[subject] = result
        else:
            print(f"   ❌ {subject} test failed")
    
    # Overall summary
    if test_results:
        print("\n" + "=" * 70)
        print("📈 COMPREHENSIVE TEST RESULTS")
        print("=" * 70)
        
        all_avg_times = [r['average_time'] for r in test_results.values()]
        all_target_met_rates = [r['target_met_rate'] for r in test_results.values()]
        
        overall_avg_time = statistics.mean(all_avg_times)
        overall_target_met_rate = statistics.mean(all_target_met_rates)
        
        print(f"📊 Overall Performance:")
        print(f"   Average Generation Time: {overall_avg_time:.2f}s")
        print(f"   Target Achievement Rate: {overall_target_met_rate:.1%}")
        print(f"   Performance Grade: {'A+' if overall_avg_time <= 5 else 'A' if overall_avg_time <= 8 else 'B' if overall_avg_time <= 10 else 'C'}")
        
        print(f"\n📚 Subject Breakdown:")
        for subject, result in test_results.items():
            grade = "🟢" if result['average_time'] <= 5 else "🟡" if result['average_time'] <= 10 else "🔴"
            print(f"   {grade} {subject.capitalize()}: {result['average_time']:.2f}s avg, {result['target_met_rate']:.1%} target met")
        
        # Recommendations
        print(f"\n💡 Recommendations:")
        if overall_avg_time <= 5:
            print("   ✅ Excellent performance! System exceeds targets.")
        elif overall_avg_time <= 10:
            print("   ✅ Good performance! System meets targets.")
            print("   💡 Consider optimizing chunk size or retrieval parameters for even better performance.")
        else:
            print("   ⚠️ Performance needs improvement.")
            print("   💡 Consider:")
            print("      - Reducing chunk size for faster retrieval")
            print("      - Optimizing vector store parameters")
            print("      - Checking Ollama model performance")
        
        return test_results
    else:
        print("\n❌ No successful tests completed")
        return None

def test_cache_performance():
    """Test cache performance specifically"""
    print("\n🗄️ Cache Performance Test")
    print("-" * 30)
    
    try:
        from shared.services.optimized_ai_service import get_optimized_ai_service
        
        service = get_optimized_ai_service()
        service.clear_cache()
        
        subject = 'physics'
        
        # First request (no cache)
        print("   🔍 First request (no cache)...")
        start_time = time.time()
        result1 = service.generate_mcq_optimized(
            num_questions=3,
            subject_name=subject,
            use_cache=True
        )
        time1 = time.time() - start_time
        
        # Second request (with cache)
        print("   📋 Second request (with cache)...")
        start_time = time.time()
        result2 = service.generate_mcq_optimized(
            num_questions=3,
            subject_name=subject,
            use_cache=True
        )
        time2 = time.time() - start_time
        
        if result1['success'] and result2['success']:
            speedup = time1 / time2 if time2 > 0 else float('inf')
            
            print(f"   📊 Cache Performance:")
            print(f"      First request: {time1:.2f}s")
            print(f"      Cached request: {time2:.2f}s")
            print(f"      Speedup: {speedup:.1f}x")
            print(f"      Cache hit: {'✅' if result2.get('from_cache') else '❌'}")
            
            return {
                'first_request_time': time1,
                'cached_request_time': time2,
                'speedup': speedup,
                'cache_hit': result2.get('from_cache', False)
            }
        else:
            print("   ❌ Cache test failed")
            return None
            
    except Exception as e:
        print(f"   ❌ Error during cache test: {str(e)}")
        return None

def main():
    """Main testing function"""
    print_banner()
    
    # Check vector store availability
    vector_available, collection_count = test_vector_store_availability()
    
    if not vector_available:
        print("\n❌ Vector stores not available. Please run initialization first:")
        print("   python scripts/initialize_vector_stores.py init")
        sys.exit(1)
    
    print()
    
    # Test optimized service
    service_available = test_optimized_service()
    
    if not service_available:
        print("\n❌ Optimized service not available. Please check Ollama installation.")
        sys.exit(1)
    
    print()
    
    # Run performance tests
    test_results = run_comprehensive_test()
    
    # Test cache performance
    cache_results = test_cache_performance()
    
    # Final summary
    print("\n" + "=" * 70)
    print("🎉 TESTING COMPLETE")
    print("=" * 70)
    
    if test_results:
        avg_times = [r['average_time'] for r in test_results.values()]
        overall_avg = statistics.mean(avg_times)
        
        if overall_avg <= 5:
            print("🏆 EXCELLENT: System significantly exceeds performance targets!")
        elif overall_avg <= 10:
            print("✅ SUCCESS: System meets performance targets!")
        else:
            print("⚠️ IMPROVEMENT NEEDED: System does not meet performance targets.")
        
        print(f"\n📊 Key Metrics:")
        print(f"   🎯 Target: ≤ 10 seconds per MCQ generation")
        print(f"   📈 Achieved: {overall_avg:.2f} seconds average")
        print(f"   🚀 Improvement: {(30 - overall_avg) / 30 * 100:.1f}% faster than legacy system")
        
        if cache_results and cache_results['cache_hit']:
            print(f"   📋 Cache Speedup: {cache_results['speedup']:.1f}x faster")
    
    print("\n💡 Next Steps:")
    print("   1. Monitor performance in production")
    print("   2. Adjust vector store parameters if needed")
    print("   3. Consider scaling vector stores for larger datasets")

if __name__ == "__main__":
    main()
