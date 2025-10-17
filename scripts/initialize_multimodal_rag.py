"""
Initialize Multimodal RAG Collections for all subjects
Processes PDFs and creates ChromaDB collections with CLIP embeddings
"""

import os
import sys
import logging
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import Config
from shared.services.multimodal_rag_service import get_multimodal_rag_service

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def initialize_multimodal_rag():
    """Initialize multimodal RAG collections for all subjects"""
    
    logger.info("=" * 70)
    logger.info("🚀 Initializing Multimodal RAG System")
    logger.info("=" * 70)

    # Check if multimodal RAG is enabled
    if not Config.MULTIMODAL_RAG_ENABLED:
        logger.error("❌ Multimodal RAG is disabled in configuration")
        return False

    # Create ChromaDB directory if it doesn't exist
    chromadb_path = Config.MULTIMODAL_CHROMADB_PATH
    os.makedirs(chromadb_path, exist_ok=True)
    logger.info(f"✅ ChromaDB path ready: {chromadb_path}")

    # Initialize service
    try:
        service = get_multimodal_rag_service(
            chromadb_path=chromadb_path,
            ollama_model=Config.MULTIMODAL_OLLAMA_MODEL
        )
        logger.info(f"✅ MultimodalRAGService initialized with model: {Config.MULTIMODAL_OLLAMA_MODEL}")
    except Exception as e:
        logger.error(f"❌ Failed to initialize service: {e}")
        return False

    # Define subjects and their PDF paths
    subjects = {
        'physics': 'physics_textbook.pdf',
        'chemistry': 'chemistry_textbook.pdf',
        'biology': 'biology_textbook.pdf',
        'mathematics': 'mathematics_textbook.pdf',
        'computer_science': 'cs_textbook.pdf'
    }

    pdf_base_path = Config.RAG_PDF_FOLDER
    logger.info(f"📁 PDF base path: {pdf_base_path}")

    # Initialize collections for each subject
    successful = []
    failed = []

    for subject, pdf_filename in subjects.items():
        pdf_path = os.path.join(pdf_base_path, subject, pdf_filename)
        
        logger.info(f"\n📚 Processing subject: {subject}")
        logger.info(f"   PDF path: {pdf_path}")

        # Check if PDF exists
        if not os.path.exists(pdf_path):
            logger.warning(f"   ⚠️ PDF not found: {pdf_path}")
            logger.info(f"   📝 Expected PDF at: {pdf_path}")
            failed.append(subject)
            continue

        try:
            logger.info(f"   🔄 Initializing collection...")
            service.initialize_subject_collection(
                subject=subject,
                pdf_path=pdf_path,
                chunk_size=Config.MULTIMODAL_CHUNK_SIZE,
                chunk_overlap=Config.MULTIMODAL_CHUNK_OVERLAP
            )
            logger.info(f"   ✅ Collection initialized successfully")
            successful.append(subject)

        except Exception as e:
            logger.error(f"   ❌ Failed to initialize collection: {e}")
            failed.append(subject)

    # Summary
    logger.info("\n" + "=" * 70)
    logger.info("📊 Initialization Summary")
    logger.info("=" * 70)
    logger.info(f"✅ Successful: {len(successful)} subjects")
    for subject in successful:
        logger.info(f"   • {subject}")

    if failed:
        logger.warning(f"❌ Failed: {len(failed)} subjects")
        for subject in failed:
            logger.warning(f"   • {subject}")

    logger.info("=" * 70)

    # Return success if at least one subject was initialized
    return len(successful) > 0


def verify_setup():
    """Verify multimodal RAG setup"""
    logger.info("\n🔍 Verifying Setup...")
    
    checks = {
        "CLIP Model": Config.MULTIMODAL_CLIP_MODEL,
        "Ollama Model": Config.MULTIMODAL_OLLAMA_MODEL,
        "ChromaDB Path": Config.MULTIMODAL_CHROMADB_PATH,
        "Chunk Size": Config.MULTIMODAL_CHUNK_SIZE,
        "Chunk Overlap": Config.MULTIMODAL_CHUNK_OVERLAP,
        "Top K Retrieval": Config.MULTIMODAL_TOP_K_RETRIEVAL,
    }

    for check_name, check_value in checks.items():
        logger.info(f"   {check_name}: {check_value}")

    # Check PDF directory
    pdf_path = Config.RAG_PDF_FOLDER
    if os.path.exists(pdf_path):
        logger.info(f"   ✅ PDF directory exists: {pdf_path}")
        subjects_dir = os.path.join(pdf_path, 'subjects')
        if os.path.exists(subjects_dir):
            logger.info(f"   ✅ Subjects directory exists")
        else:
            logger.warning(f"   ⚠️ Subjects directory not found: {subjects_dir}")
    else:
        logger.warning(f"   ⚠️ PDF directory not found: {pdf_path}")


if __name__ == "__main__":
    logger.info("Starting Multimodal RAG Initialization...")
    
    # Verify setup
    verify_setup()
    
    # Initialize
    success = initialize_multimodal_rag()
    
    if success:
        logger.info("\n✅ Multimodal RAG initialization completed successfully!")
        sys.exit(0)
    else:
        logger.error("\n❌ Multimodal RAG initialization failed!")
        sys.exit(1)

