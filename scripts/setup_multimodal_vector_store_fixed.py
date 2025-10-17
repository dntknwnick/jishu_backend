"""
Multimodal Vector Store Setup Script - Fixed Version
Processes all subject PDFs, creates CLIP embeddings, and stores in ChromaDB
This script is idempotent and safe to re-run when new PDFs are added

Usage:
    python scripts/setup_multimodal_vector_store_fixed.py [--reset] [--subject SUBJECT]
    
Options:
    --reset         : Delete existing ChromaDB and rebuild from scratch
    --subject NAME  : Process only specific subject (e.g., physics, chemistry)
    --verbose       : Enable verbose logging
"""

import os
import sys
import json
import logging
import argparse
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple

# CRITICAL: Clear old ChromaDB environment variables BEFORE any chromadb imports
# These are from the old ChromaDB API and cause validation errors in 1.1.1
chroma_keys_to_remove = [
    'CHROMA_DB_IMPL', 'CHROMA_TELEMETRY_IMPL', 'CHROMA_SERVER_NOFILE',
    'CHROMA_ANONYMIZED_TELEMETRY', 'CHROMA_USE_HTTP'
]
for key in chroma_keys_to_remove:
    if key in os.environ:
        del os.environ[key]

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import Config
from shared.services.multimodal_rag_service import (
    MultimodalRAGService,
    process_pdf,
    embed_text,
    CLIP_AVAILABLE
)

# Ensure logs directory exists BEFORE configuring logging
os.makedirs('logs', exist_ok=True)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/vector_store_setup.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class VectorStoreSetup:
    """Setup and manage multimodal vector store"""

    def __init__(self, chromadb_path: str, pdf_root: str = None):
        self.chromadb_path = chromadb_path
        self.pdf_root = pdf_root or os.path.join(os.getcwd(), 'pdfs', 'subjects')
        self.service = None
        self.stats = {
            'subjects_processed': 0,
            'pdfs_processed': 0,
            'total_documents': 0,
            'total_images': 0,
            'errors': 0,
            'start_time': datetime.now()
        }

    def validate_setup(self) -> bool:
        """Validate setup requirements"""
        logger.info("\nValidating Setup Requirements...")

        # Check CLIP availability
        if not CLIP_AVAILABLE:
            logger.error("CLIP model not available")
            return False
        logger.info("CLIP model available")

        # Check PDF root directory
        if not os.path.exists(self.pdf_root):
            logger.error(f"PDF root directory not found: {self.pdf_root}")
            return False
        logger.info(f"PDF root directory exists: {self.pdf_root}")

        # Check ChromaDB path
        os.makedirs(self.chromadb_path, exist_ok=True)
        if not os.access(self.chromadb_path, os.W_OK):
            logger.error(f"ChromaDB path not writable: {self.chromadb_path}")
            return False
        logger.info(f"ChromaDB path writable: {self.chromadb_path}")
        
        return True

    def get_subjects(self) -> Dict[str, List[str]]:
        """Get all subjects and their PDF files"""
        logger.info("\nScanning Subjects and PDFs...")
        subjects = {}

        for subject_dir in os.listdir(self.pdf_root):
            subject_path = os.path.join(self.pdf_root, subject_dir)
            if not os.path.isdir(subject_path):
                continue

            pdf_files = [f for f in os.listdir(subject_path) if f.endswith('.pdf')]
            if pdf_files:
                subjects[subject_dir] = [os.path.join(subject_path, f) for f in pdf_files]
                logger.info(f"   {subject_dir}: {len(pdf_files)} PDF(s)")

        if not subjects:
            logger.error("No subjects with PDFs found")
            return {}

        logger.info(f"Found {len(subjects)} subjects")
        return subjects

    def initialize_service(self):
        """Initialize MultimodalRAGService"""
        logger.info("\nInitializing MultimodalRAGService...")
        try:
            self.service = MultimodalRAGService(
                chromadb_path=self.chromadb_path,
                ollama_model=Config.MULTIMODAL_OLLAMA_MODEL
            )
            logger.info("Service initialized")
            return True
        except Exception as e:
            logger.error(f"Failed to initialize service: {e}")
            return False

    def process_subject(self, subject: str, pdf_files: List[str]) -> Tuple[int, int, int]:
        """Process all PDFs for a subject"""
        logger.info(f"\nProcessing Subject: {subject}")
        logger.info(f"   PDFs to process: {len(pdf_files)}")
        
        total_docs = 0
        total_images = 0
        error_count = 0
        
        for pdf_path in pdf_files:
            try:
                logger.info(f"   Processing: {os.path.basename(pdf_path)}")

                # Process PDF
                all_docs, all_embeddings, image_data_store = process_pdf(
                    pdf_path,
                    chunk_size=Config.MULTIMODAL_CHUNK_SIZE,
                    chunk_overlap=Config.MULTIMODAL_CHUNK_OVERLAP
                )

                # Add metadata
                for doc in all_docs:
                    doc['subject'] = subject
                    doc['pdf_file'] = os.path.basename(pdf_path)

                # Store in ChromaDB
                collection = self.service.client.get_or_create_collection(
                    name=subject.lower(),
                    metadata={"description": f"Multimodal embeddings for {subject}"}
                )

                # Add documents in batches
                ids = [f"{subject}_{i}_{datetime.now().timestamp()}" for i in range(len(all_docs))]
                documents = [doc["content"] for doc in all_docs]
                metadatas = [{k: str(v) for k, v in doc.items() if k != "content"} for doc in all_docs]
                embeddings = [emb.tolist() for emb in all_embeddings]

                batch_size = Config.MULTIMODAL_BATCH_SIZE
                for i in range(0, len(ids), batch_size):
                    batch_end = min(i + batch_size, len(ids))
                    collection.add(
                        ids=ids[i:batch_end],
                        documents=documents[i:batch_end],
                        metadatas=metadatas[i:batch_end],
                        embeddings=embeddings[i:batch_end]
                    )

                # Store images
                if image_data_store:
                    if subject.lower() not in self.service.image_stores:
                        self.service.image_stores[subject.lower()] = {}
                    self.service.image_stores[subject.lower()].update(image_data_store)

                total_docs += len(all_docs)
                total_images += len(image_data_store)

                logger.info(f"      Added {len(all_docs)} documents, {len(image_data_store)} images")

            except Exception as e:
                logger.error(f"      Error processing {os.path.basename(pdf_path)}: {e}")
                error_count += 1
        
        return total_docs, total_images, error_count

    def run(self, reset: bool = False, subject: str = None):
        """Run the setup"""
        logger.info("=" * 80)
        logger.info("MULTIMODAL VECTOR STORE SETUP")
        logger.info("=" * 80)

        # Validate setup
        if not self.validate_setup():
            logger.error("Setup validation failed")
            return False

        # Reset if requested
        if reset:
            logger.info("\nResetting ChromaDB...")
            import shutil
            if os.path.exists(self.chromadb_path):
                shutil.rmtree(self.chromadb_path)
            os.makedirs(self.chromadb_path, exist_ok=True)
            logger.info("ChromaDB reset")

        # Initialize service
        if not self.initialize_service():
            logger.error("Failed to initialize service")
            return False

        # Get subjects
        subjects = self.get_subjects()
        if not subjects:
            logger.error("No subjects found")
            return False

        # Filter by subject if specified
        if subject:
            if subject.lower() not in subjects:
                logger.error(f"Subject not found: {subject}")
                return False
            subjects = {subject.lower(): subjects[subject.lower()]}

        # Process subjects
        logger.info(f"\nProcessing {len(subjects)} subjects...")
        for subj, pdf_files in subjects.items():
            docs, images, errors = self.process_subject(subj, pdf_files)
            self.stats['subjects_processed'] += 1
            self.stats['pdfs_processed'] += len(pdf_files)
            self.stats['total_documents'] += docs
            self.stats['total_images'] += images
            self.stats['errors'] += errors
        
        # Print summary
        self.print_summary()
        return True

    def print_summary(self):
        """Print setup summary"""
        elapsed = (datetime.now() - self.stats['start_time']).total_seconds()

        logger.info("\n" + "=" * 80)
        logger.info("SETUP COMPLETE")
        logger.info("=" * 80)
        logger.info(f"Subjects Processed: {self.stats['subjects_processed']}")
        logger.info(f"PDFs Processed: {self.stats['pdfs_processed']}")
        logger.info(f"Total Documents: {self.stats['total_documents']}")
        logger.info(f"Total Images: {self.stats['total_images']}")
        logger.info(f"Errors: {self.stats['errors']}")
        logger.info(f"Time Elapsed: {elapsed:.2f} seconds")
        logger.info("=" * 80)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Setup multimodal vector store")
    parser.add_argument("--reset", action="store_true", help="Reset ChromaDB")
    parser.add_argument("--subject", type=str, help="Process specific subject")
    parser.add_argument("--verbose", action="store_true", help="Verbose logging")
    
    args = parser.parse_args()
    
    setup = VectorStoreSetup(
        chromadb_path=Config.MULTIMODAL_CHROMADB_PATH,
        pdf_root=os.path.join(os.getcwd(), 'pdfs', 'subjects')
    )
    
    success = setup.run(reset=args.reset, subject=args.subject)
    sys.exit(0 if success else 1)

