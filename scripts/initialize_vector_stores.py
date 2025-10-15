#!/usr/bin/env python3
"""
Vector Store Initialization Script
Initialize and manage vector stores for optimized MCQ generation
"""

import os
import sys
import time
import argparse
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

try:
    from shared.services.vector_store_manager import get_vector_store_manager
    CHROMADB_MANAGER_AVAILABLE = True
except ImportError:
    CHROMADB_MANAGER_AVAILABLE = False

try:
    from shared.services.simple_vector_store_manager import get_simple_vector_store_manager
    SIMPLE_VECTOR_STORE_AVAILABLE = True
except ImportError:
    SIMPLE_VECTOR_STORE_AVAILABLE = False

from shared.services.enhanced_pdf_processor import get_pdf_processor

def print_banner():
    """Print initialization banner"""
    print("=" * 60)
    print("🚀 JISHU BACKEND - VECTOR STORE INITIALIZATION")
    print("=" * 60)
    print("Optimizing MCQ generation with LangChain + ChromaDB")
    print()

def check_dependencies():
    """Check if all required dependencies are available"""
    print("🔍 Checking dependencies...")
    
    dependencies = {
        'ChromaDB': False,
        'LangChain': False,
        'PyPDF2': False,
        'Ollama': False
    }
    
    try:
        import faiss
        dependencies['FAISS'] = True
        print("✅ FAISS available")
    except ImportError:
        print("❌ FAISS not available - install with: pip install faiss-cpu")

    try:
        import chromadb
        dependencies['ChromaDB'] = True
        print("✅ ChromaDB available (optional)")
    except ImportError:
        print("⚠️ ChromaDB not available (using FAISS instead)")
    
    try:
        from langchain_community.document_loaders import PyPDFLoader
        from langchain_ollama import OllamaEmbeddings
        dependencies['LangChain'] = True
        print("✅ LangChain available")
    except ImportError:
        try:
            # Fallback to older import structure
            from langchain.document_loaders import PyPDFLoader
            from langchain_ollama import OllamaEmbeddings
            dependencies['LangChain'] = True
            print("✅ LangChain available (legacy imports)")
        except ImportError:
            print("❌ LangChain not available - install with: pip install langchain langchain-community langchain-ollama")
    
    try:
        from PyPDF2 import PdfReader
        dependencies['PyPDF2'] = True
        print("✅ PyPDF2 available")
    except ImportError:
        print("❌ PyPDF2 not available - install with: pip install PyPDF2")
    
    try:
        import ollama
        dependencies['Ollama'] = True
        print("✅ Ollama available")
    except ImportError:
        print("❌ Ollama not available - install with: pip install ollama")
    
    print()
    
    # Check critical dependencies
    critical_missing = []
    if not dependencies['FAISS'] and not dependencies['ChromaDB']:
        critical_missing.append('Vector Store (FAISS or ChromaDB)')
    if not dependencies['LangChain']:
        critical_missing.append('LangChain')
    if not dependencies['PyPDF2']:
        critical_missing.append('PyPDF2')
    if not dependencies['Ollama']:
        critical_missing.append('Ollama')

    if critical_missing:
        print(f"❌ Missing critical dependencies: {', '.join(critical_missing)}")
        print("Please install missing dependencies before proceeding.")
        return False

    print("✅ All critical dependencies available!")
    return True

def check_ollama_service():
    """Check if Ollama service is running"""
    print("🔍 Checking Ollama service...")
    
    try:
        import requests
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code == 200:
            models = response.json().get('models', [])
            print(f"✅ Ollama service running with {len(models)} models")
            
            # Check for llama3.2:1b model
            model_names = [model['name'] for model in models]
            if 'llama3.2:1b' in model_names:
                print("✅ llama3.2:1b model available")
                return True
            else:
                print("⚠️ llama3.2:1b model not found")
                print("Available models:", model_names)
                print("Please pull the model with: ollama pull llama3.2:1b")
                return False
        else:
            print("❌ Ollama service not responding")
            return False
    except Exception as e:
        print(f"❌ Cannot connect to Ollama service: {str(e)}")
        print("Please start Ollama service with: ollama serve")
        return False

def check_pdf_directories():
    """Check PDF directory structure"""
    print("🔍 Checking PDF directories...")
    
    pdf_path = Path("./pdfs/subjects")
    if not pdf_path.exists():
        print(f"❌ PDF directory not found: {pdf_path}")
        return False
    
    subjects = ['physics', 'chemistry', 'biology', 'mathematics', 'computer_science']
    found_subjects = []
    
    for subject in subjects:
        subject_path = pdf_path / subject
        if subject_path.exists():
            pdf_files = list(subject_path.glob("*.pdf"))
            if pdf_files:
                found_subjects.append(subject)
                print(f"✅ {subject}: {len(pdf_files)} PDF files")
            else:
                print(f"⚠️ {subject}: directory exists but no PDF files")
        else:
            print(f"❌ {subject}: directory not found")
    
    print()
    if found_subjects:
        print(f"✅ Found {len(found_subjects)} subjects with PDF files")
        return True
    else:
        print("❌ No subjects with PDF files found")
        return False

def initialize_vector_stores(subjects=None, force_recreate=False):
    """Initialize vector stores for specified subjects"""
    print("🚀 Initializing vector stores...")
    
    try:
        # Get vector store manager - try simple FAISS first since ChromaDB has issues
        vector_manager = None

        if SIMPLE_VECTOR_STORE_AVAILABLE:
            try:
                vector_manager = get_simple_vector_store_manager(
                    pdf_folder_path="./pdfs/subjects",
                    vector_store_path="./vector_stores",
                    ollama_model="llama3.2:1b"
                )
                print("✅ Using Simple FAISS vector store")
            except Exception as e:
                print(f"⚠️ Simple vector store failed: {str(e)}")

        if vector_manager is None and CHROMADB_MANAGER_AVAILABLE:
            try:
                vector_manager = get_vector_store_manager(
                    pdf_folder_path="./pdfs/subjects",
                    vector_store_path="./vector_stores",
                    ollama_model="llama3.2:1b"
                )
                print("✅ Using ChromaDB vector store")
            except Exception as e:
                print(f"⚠️ ChromaDB failed: {str(e)}")

        if vector_manager is None:
            print("❌ No vector store manager available")
            return False
        
        # Check status
        status = vector_manager.get_status()
        print(f"📊 Vector Store Manager Status:")

        # Check what type of vector store we're using
        if 'chromadb_available' in status:
            print(f"   ChromaDB: {'✅' if status.get('chromadb_available') else '❌'}")
            print(f"   LangChain: {'✅' if status.get('langchain_available') else '❌'}")
            required_available = status.get('chromadb_available') and status.get('langchain_available')
        else:
            # Simple vector store
            print(f"   FAISS: {'✅' if status.get('faiss_available') else '❌'}")
            print(f"   Ollama: {'✅' if status.get('ollama_available') else '❌'}")
            required_available = status.get('faiss_available') and status.get('ollama_available')

        print(f"   Model: {status['ollama_model']}")
        print(f"   Vector Store Path: {status['vector_store_path']}")
        print()

        if not required_available:
            print("❌ Required components not available")
            return False
        
        # Initialize for specific subjects or all
        if subjects:
            print(f"📚 Initializing vector stores for: {', '.join(subjects)}")
            results = {}
            for subject in subjects:
                print(f"\n🔄 Processing {subject}...")
                results[subject] = vector_manager.create_subject_vector_store(subject, force_recreate)
        else:
            print("📚 Initializing vector stores for all subjects...")
            results = vector_manager.initialize_all_subjects(force_recreate)
        
        # Report results
        print("\n📊 Initialization Results:")
        successful = 0
        for subject, success in results.items():
            status_icon = "✅" if success else "❌"
            print(f"   {status_icon} {subject}")
            if success:
                successful += 1
        
        print(f"\n🎯 Summary: {successful}/{len(results)} subjects initialized successfully")
        
        if successful > 0:
            # Get collection stats
            stats = vector_manager.get_collection_stats()
            print("\n📈 Collection Statistics:")
            for subject, stat in stats.items():
                print(f"   📚 {subject}: {stat['count']} documents")
        
        return successful == len(results)
        
    except Exception as e:
        print(f"❌ Error during initialization: {str(e)}")
        return False

def show_status():
    """Show current vector store status"""
    print("📊 Vector Store Status")
    print("-" * 30)
    
    try:
        vector_manager = get_vector_store_manager()
        status = vector_manager.get_status()
        
        print(f"ChromaDB Available: {'✅' if status['chromadb_available'] else '❌'}")
        print(f"LangChain Available: {'✅' if status['langchain_available'] else '❌'}")
        print(f"Vector Store Path: {status['vector_store_path']}")
        print(f"PDF Folder Path: {status['pdf_folder_path']}")
        print(f"Ollama Model: {status['ollama_model']}")
        print()
        
        # Collection stats
        if status['collections']:
            print("📚 Collections:")
            for name, info in status['collections'].items():
                print(f"   {name}: {info['count']} documents")
        else:
            print("📚 No collections found")
        
    except Exception as e:
        print(f"❌ Error getting status: {str(e)}")

def reset_vector_stores():
    """Reset all vector stores"""
    print("🗑️ Resetting all vector stores...")
    
    try:
        vector_manager = get_vector_store_manager()
        success = vector_manager.reset_all_vector_stores()
        
        if success:
            print("✅ All vector stores reset successfully")
        else:
            print("❌ Failed to reset vector stores")
        
        return success
        
    except Exception as e:
        print(f"❌ Error resetting vector stores: {str(e)}")
        return False

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="Initialize and manage vector stores for MCQ generation")
    parser.add_argument('action', choices=['init', 'status', 'reset'], 
                       help='Action to perform')
    parser.add_argument('--subjects', nargs='+', 
                       choices=['physics', 'chemistry', 'biology', 'mathematics', 'computer_science'],
                       help='Specific subjects to initialize')
    parser.add_argument('--force', action='store_true',
                       help='Force recreate existing vector stores')
    parser.add_argument('--skip-checks', action='store_true',
                       help='Skip dependency and service checks')
    
    args = parser.parse_args()
    
    print_banner()
    
    if args.action == 'status':
        show_status()
        return
    
    if args.action == 'reset':
        confirm = input("⚠️ This will delete all vector stores. Continue? (y/N): ")
        if confirm.lower() == 'y':
            reset_vector_stores()
        else:
            print("❌ Reset cancelled")
        return
    
    if args.action == 'init':
        if not args.skip_checks:
            print("🔍 Running pre-initialization checks...")
            
            if not check_dependencies():
                sys.exit(1)
            
            if not check_ollama_service():
                sys.exit(1)
            
            if not check_pdf_directories():
                sys.exit(1)
            
            print("✅ All checks passed!\n")
        
        # Initialize vector stores
        start_time = time.time()
        success = initialize_vector_stores(args.subjects, args.force)
        total_time = time.time() - start_time
        
        print(f"\n⏱️ Total time: {total_time:.2f} seconds")
        
        if success:
            print("🎉 Vector store initialization completed successfully!")
            print("\n📝 Next steps:")
            print("   1. Test MCQ generation with the new vector stores")
            print("   2. Monitor performance improvements")
            print("   3. Update your application to use the optimized service")
        else:
            print("❌ Vector store initialization failed")
            sys.exit(1)

if __name__ == "__main__":
    main()
