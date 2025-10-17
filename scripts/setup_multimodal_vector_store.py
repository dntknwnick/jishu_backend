"""
Multimodal Vector Store Setup Script
Processes all subject PDFs, creates CLIP embeddings, and stores in ChromaDB
This script is idempotent and safe to re-run when new PDFs are added

Usage:
    python scripts/setup_multimodal_vector_store.py [--reset] [--subject SUBJECT]
    
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

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import Config
from shared.services.multimodal_rag_service import (
    MultimodalRAGService,
    process_pdf,
    embed_text,
    CLIP_AVAILABLE
)

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

# Ensure logs directory exists
os.makedirs('logs', exist_ok=True)


class VectorStoreSetup:
    """Setup and manage multimodal vector store initialization"""

    def __init__(self, chromadb_path: str, pdf_root: str = None):
        """Initialize setup manager"""
        self.chromadb_path = chromadb_path
        self.pdf_root = pdf_root or os.path.join(os.getcwd(), 'pdfs', 'subjects')
        self.service = None
        self.stats = {
            'subjects_processed': 0,
            'pdfs_processed': 0,
            'total_documents': 0,
            'total_images': 0,
            'errors': 0,
            'start_time': datetime.now(),
            'end_time': None,
            'duration_seconds': 0
        }
        
        logger.info("=" * 80)
        logger.info("🚀 Multimodal Vector Store Setup")
        logger.info("=" * 80)
        logger.info(f"ChromaDB Path: {self.chromadb_path}")
        logger.info(f"PDF Root: {self.pdf_root}")

    def verify_prerequisites(self) -> bool:
        """Verify all prerequisites are met"""
        logger.info("\n📋 Verifying Prerequisites...")
        
        # Check CLIP availability
        if not CLIP_AVAILABLE:
            logger.error("❌ CLIP model not available. Install: pip install torch transformers")
            return False
        logger.info("✅ CLIP model available")
        
        # Check PDF directory
        if not os.path.exists(self.pdf_root):
            logger.error(f"❌ PDF root directory not found: {self.pdf_root}")
            return False
        logger.info(f"✅ PDF root directory exists: {self.pdf_root}")
        
        # Check for PDFs
        pdf_count = len(list(Path(self.pdf_root).rglob('*.pdf')))
        if pdf_count == 0:
            logger.warning(f"⚠️  No PDF files found in {self.pdf_root}")
            logger.warning("   Add PDFs to pdfs/subjects/{subject}/ directories")
            return False
        logger.info(f"✅ Found {pdf_count} PDF files")
        
        # Check ChromaDB path is writable
        os.makedirs(self.chromadb_path, exist_ok=True)
        if not os.access(self.chromadb_path, os.W_OK):
            logger.error(f"❌ ChromaDB path not writable: {self.chromadb_path}")
            return False
        logger.info(f"✅ ChromaDB path writable: {self.chromadb_path}")
        
        return True

    def get_subjects(self) -> Dict[str, List[str]]:
        """Get all subjects and their PDF files"""
        logger.info("\n📚 Scanning Subjects and PDFs...")
        subjects = {}
        
        for subject_dir in os.listdir(self.pdf_root):
            subject_path = os.path.join(self.pdf_root, subject_dir)
            if not os.path.isdir(subject_path):
                continue
            
            pdf_files = [f for f in os.listdir(subject_path) if f.endswith('.pdf')]
            if pdf_files:
                subjects[subject_dir] = [os.path.join(subject_path, f) for f in pdf_files]
                logger.info(f"   📁 {subject_dir}: {len(pdf_files)} PDF(s)")
        
        if not subjects:
            logger.error("❌ No subjects with PDFs found")
            return {}
        
        logger.info(f"✅ Found {len(subjects)} subjects")
        return subjects

    def initialize_service(self):
        """Initialize MultimodalRAGService"""
        logger.info("\n🔧 Initializing MultimodalRAGService...")
        try:
            self.service = MultimodalRAGService(
                chromadb_path=self.chromadb_path,
                ollama_model=Config.MULTIMODAL_OLLAMA_MODEL
            )
            logger.info("✅ Service initialized")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to initialize service: {e}")
            return False

    def process_subject(self, subject: str, pdf_files: List[str]) -> Tuple[int, int, int]:
        """Process all PDFs for a subject"""
        logger.info(f"\n📚 Processing Subject: {subject}")
        logger.info(f"   PDFs to process: {len(pdf_files)}")
        
        total_docs = 0
        total_images = 0
        error_count = 0
        
        for pdf_path in pdf_files:
            try:
                logger.info(f"   📄 Processing: {os.path.basename(pdf_path)}")
                
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
                
                logger.info(f"      ✅ Added {len(all_docs)} documents, {len(image_data_store)} images")
                self.stats['pdfs_processed'] += 1
                
            except Exception as e:
                logger.error(f"      ❌ Error processing {os.path.basename(pdf_path)}: {e}")
                error_count += 1
                self.stats['errors'] += 1
        
        logger.info(f"   ✅ Subject {subject} complete: {total_docs} docs, {total_images} images")
        self.stats['subjects_processed'] += 1
        self.stats['total_documents'] += total_docs
        self.stats['total_images'] += total_images
        
        return total_docs, total_images, error_count

    def verify_collections(self) -> bool:
        """Verify all collections were created"""
        logger.info("\n✅ Verifying Collections...")
        try:
            collections = self.service.client.list_collections()
            logger.info(f"   Collections created: {len(collections)}")
            
            for collection in collections:
                count = collection.count()
                logger.info(f"   📚 {collection.name}: {count} documents")
            
            return len(collections) > 0
        except Exception as e:
            logger.error(f"❌ Error verifying collections: {e}")
            return False

    def save_metadata(self):
        """Save setup metadata for reference"""
        logger.info("\n💾 Saving Metadata...")
        metadata = {
            'setup_timestamp': datetime.now().isoformat(),
            'chromadb_path': self.chromadb_path,
            'pdf_root': self.pdf_root,
            'config': {
                'chunk_size': Config.MULTIMODAL_CHUNK_SIZE,
                'chunk_overlap': Config.MULTIMODAL_CHUNK_OVERLAP,
                'top_k_retrieval': Config.MULTIMODAL_TOP_K_RETRIEVAL,
                'batch_size': Config.MULTIMODAL_BATCH_SIZE,
                'clip_model': Config.MULTIMODAL_CLIP_MODEL,
                'ollama_model': Config.MULTIMODAL_OLLAMA_MODEL
            },
            'statistics': self.stats
        }
        
        metadata_path = os.path.join(self.chromadb_path, 'setup_metadata.json')
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2, default=str)
        
        logger.info(f"✅ Metadata saved to {metadata_path}")

    def run(self, reset: bool = False, subject_filter: str = None):
        """Run the complete setup"""
        try:
            # Reset if requested
            if reset:
                logger.warning("🔄 Resetting ChromaDB...")
                import shutil
                if os.path.exists(self.chromadb_path):
                    shutil.rmtree(self.chromadb_path)
                os.makedirs(self.chromadb_path, exist_ok=True)
                logger.info("✅ ChromaDB reset")
            
            # Verify prerequisites
            if not self.verify_prerequisites():
                return False
            
            # Initialize service
            if not self.initialize_service():
                return False
            
            # Get subjects
            subjects = self.get_subjects()
            if not subjects:
                return False
            
            # Filter subjects if requested
            if subject_filter:
                subjects = {k: v for k, v in subjects.items() if k.lower() == subject_filter.lower()}
                if not subjects:
                    logger.error(f"❌ Subject not found: {subject_filter}")
                    return False
            
            # Process each subject
            logger.info("\n" + "=" * 80)
            logger.info("🔄 Processing Subjects...")
            logger.info("=" * 80)
            
            for subject, pdf_files in subjects.items():
                self.process_subject(subject, pdf_files)
            
            # Verify collections
            if not self.verify_collections():
                logger.warning("⚠️  No collections created")
                return False
            
            # Save metadata
            self.save_metadata()
            
            # Print summary
            self.stats['end_time'] = datetime.now()
            self.stats['duration_seconds'] = (self.stats['end_time'] - self.stats['start_time']).total_seconds()
            
            logger.info("\n" + "=" * 80)
            logger.info("📊 Setup Complete - Summary")
            logger.info("=" * 80)
            logger.info(f"Subjects Processed: {self.stats['subjects_processed']}")
            logger.info(f"PDFs Processed: {self.stats['pdfs_processed']}")
            logger.info(f"Total Documents: {self.stats['total_documents']}")
            logger.info(f"Total Images: {self.stats['total_images']}")
            logger.info(f"Errors: {self.stats['errors']}")
            logger.info(f"Duration: {self.stats['duration_seconds']:.2f} seconds")
            logger.info("=" * 80)
            logger.info("✅ Vector store setup complete!")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Setup failed: {e}", exc_info=True)
            return False


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='Setup multimodal vector store for MCQ generation',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    parser.add_argument('--reset', action='store_true', help='Reset ChromaDB and rebuild')
    parser.add_argument('--subject', type=str, help='Process only specific subject')
    parser.add_argument('--verbose', action='store_true', help='Enable verbose logging')
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    setup = VectorStoreSetup(
        chromadb_path=Config.MULTIMODAL_CHROMADB_PATH,
        pdf_root=os.path.join(os.getcwd(), 'pdfs', 'subjects')
    )
    
    success = setup.run(reset=args.reset, subject_filter=args.subject)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()

