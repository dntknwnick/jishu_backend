#!/usr/bin/env python3
"""
RAG System Initialization Script
Initialize vector stores for all subjects at startup
"""

import os
import sys
import time
import logging
from pathlib import Path

# Add the parent directory to the path so we can import from shared
sys.path.append(str(Path(__file__).parent.parent))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def initialize_rag_system():
    """Initialize the RAG system with vector stores for all subjects"""
    try:
        logger.info("🚀 Starting RAG system initialization...")
        
        # Import RAG service
        from shared.services.rag_service import get_rag_service
        
        # Configuration from environment or defaults
        pdf_folder_path = os.getenv('AI_PDF_FOLDER', './pdfs/subjects')
        vector_store_path = os.getenv('VECTOR_STORE_PATH', './vector_stores')
        ollama_model = os.getenv('AI_OLLAMA_MODEL', 'llama3.2:1b')
        
        logger.info(f"📁 PDF folder: {pdf_folder_path}")
        logger.info(f"🗄️ Vector store: {vector_store_path}")
        logger.info(f"🤖 Ollama model: {ollama_model}")
        
        # Initialize RAG service
        rag_service = get_rag_service(
            pdf_folder_path=pdf_folder_path,
            vector_store_path=vector_store_path,
            ollama_model=ollama_model
        )
        
        # Check system status first
        status = rag_service.get_status()
        logger.info(f"📊 System health: {status['health']}")
        
        # Check dependencies
        deps = status['dependencies']
        missing_deps = [dep for dep, available in deps.items() if not available]
        
        if missing_deps:
            logger.error(f"❌ Missing dependencies: {', '.join(missing_deps)}")
            logger.error("Please install missing dependencies before initializing RAG system")
            return False
        
        logger.info("✅ All dependencies available")
        
        # Check if vector stores already exist
        existing_stores = []
        missing_stores = []
        
        for subject in rag_service.subjects:
            if subject in rag_service.collections:
                existing_stores.append(subject)
            else:
                missing_stores.append(subject)
        
        if existing_stores:
            logger.info(f"📚 Existing vector stores: {', '.join(existing_stores)}")
        
        if missing_stores:
            logger.info(f"🔄 Need to create vector stores for: {', '.join(missing_stores)}")
            
            # Initialize missing vector stores using efficient method
            start_time = time.time()
            result = rag_service.initialize_missing_subjects(force_recreate=False)
            initialization_time = time.time() - start_time
            
            if result['success']:
                logger.info(f"✅ Successfully initialized {result['successful_count']}/{result['total_subjects']} subjects in {initialization_time:.2f}s")
                logger.info(f"📚 Successful subjects: {', '.join(result['successful_subjects'])}")
                
                # Log any failures
                failed_subjects = [s for s, success in result['results'].items() if not success]
                if failed_subjects:
                    logger.warning(f"⚠️ Failed to initialize: {', '.join(failed_subjects)}")
                
                return True
            else:
                logger.error("❌ Failed to initialize any vector stores")
                return False
        else:
            logger.info("✅ All vector stores already exist")
            return True
            
    except Exception as e:
        logger.error(f"❌ Error initializing RAG system: {str(e)}")
        return False

def check_pdf_availability():
    """Check if PDF files are available for processing"""
    try:
        pdf_folder_path = os.getenv('AI_PDF_FOLDER', './pdfs/subjects')
        pdf_folder = Path(pdf_folder_path)
        
        if not pdf_folder.exists():
            logger.warning(f"📁 PDF folder does not exist: {pdf_folder_path}")
            return False
        
        subjects = ['physics', 'chemistry', 'biology', 'mathematics', 'computer_science']
        available_subjects = []
        
        for subject in subjects:
            subject_folder = pdf_folder / subject
            if subject_folder.exists():
                pdf_files = list(subject_folder.glob("*.pdf"))
                if pdf_files:
                    available_subjects.append(subject)
                    logger.info(f"📚 {subject}: {len(pdf_files)} PDF files")
                else:
                    logger.warning(f"📁 {subject}: folder exists but no PDF files found")
            else:
                logger.warning(f"📁 {subject}: folder not found")
        
        if available_subjects:
            logger.info(f"✅ PDF files available for: {', '.join(available_subjects)}")
            return True
        else:
            logger.error("❌ No PDF files found for any subject")
            return False
            
    except Exception as e:
        logger.error(f"❌ Error checking PDF availability: {str(e)}")
        return False

def main():
    """Main function to run the initialization"""
    logger.info("🎯 RAG System Initialization Script")
    logger.info("=" * 50)
    
    # Check PDF availability first
    if not check_pdf_availability():
        logger.error("❌ Cannot proceed without PDF files")
        sys.exit(1)
    
    # Initialize RAG system
    success = initialize_rag_system()
    
    if success:
        logger.info("🎉 RAG system initialization completed successfully!")
        logger.info("🚀 System is ready for MCQ generation and chatbot queries")
        sys.exit(0)
    else:
        logger.error("❌ RAG system initialization failed")
        sys.exit(1)

if __name__ == "__main__":
    main()
