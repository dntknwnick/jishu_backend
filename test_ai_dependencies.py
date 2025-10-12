#!/usr/bin/env python3
"""
Test script to verify AI dependencies are working
"""

def test_dependencies():
    """Test if all AI dependencies are available"""
    results = {}
    
    # Test ollama
    try:
        import ollama
        results['ollama'] = True
        print("✅ ollama: Available")
    except ImportError as e:
        results['ollama'] = False
        print(f"❌ ollama: Not available - {e}")
    
    # Test sentence_transformers
    try:
        import sentence_transformers
        results['sentence_transformers'] = True
        print("✅ sentence_transformers: Available")
    except ImportError as e:
        results['sentence_transformers'] = False
        print(f"❌ sentence_transformers: Not available - {e}")
    
    # Test PyPDF2
    try:
        import PyPDF2
        results['PyPDF2'] = True
        print("✅ PyPDF2: Available")
    except ImportError as e:
        results['PyPDF2'] = False
        print(f"❌ PyPDF2: Not available - {e}")
    
    # Test numpy
    try:
        import numpy
        results['numpy'] = True
        print("✅ numpy: Available")
    except ImportError as e:
        results['numpy'] = False
        print(f"❌ numpy: Not available - {e}")
    
    # Test torch
    try:
        import torch
        results['torch'] = True
        print("✅ torch: Available")
    except ImportError as e:
        results['torch'] = False
        print(f"❌ torch: Not available - {e}")
    
    return results

def test_ai_service():
    """Test the AI service initialization"""
    try:
        from shared.services.ai_service import AIService
        
        ai_service = AIService()
        status = ai_service.get_status()
        
        print("\n🔍 AI Service Status:")
        print(f"Status: {status['status']}")
        print(f"Dependencies: {status['dependencies']}")
        print(f"Ollama Model: {status['ollama_model']}")
        print(f"PDF Folder: {status['pdf_folder']}")
        
        return True
    except Exception as e:
        print(f"❌ AI Service initialization failed: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Testing AI Dependencies...")
    print("=" * 50)
    
    # Test basic dependencies
    deps = test_dependencies()
    
    print("\n" + "=" * 50)
    
    # Test AI service
    ai_working = test_ai_service()
    
    print("\n" + "=" * 50)
    print("📊 Summary:")
    
    all_deps_available = all(deps.values())
    if all_deps_available and ai_working:
        print("✅ All AI dependencies are working correctly!")
    else:
        print("❌ Some issues found:")
        for dep, available in deps.items():
            if not available:
                print(f"  - {dep}: Not available")
        if not ai_working:
            print("  - AI Service: Not working")
