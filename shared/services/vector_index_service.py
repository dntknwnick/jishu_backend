"""
Layer 2: Vector Indexing Service
Build a one-time/offline indexing pipeline to:
- Chunk and embed every PDF in your data_pdfs/subjects/ directory
- Organize embeddings/collections per subject, using ChromaDB
- Store all vector data persistently—never redo on every query
- Allow for efficient re-indexing (only changed/new PDFs) via checksum logic
"""

import os
import json
import hashlib
import logging
import time
from typing import List, Dict, Optional, Tuple
from pathlib import Path
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Try to import dependencies
try:
    from PyPDF2 import PdfReader
    PYPDF2_AVAILABLE = True
except ImportError:
    PYPDF2_AVAILABLE = False
    logger.warning("PyPDF2 not available. PDF processing will not work.")

from .model_service import get_model_service


class VectorIndexService:
    """
    Service for offline PDF indexing and vector store management.
    Handles chunking, embedding, and persistent storage of PDF content.
    """
    
    def __init__(self, 
                 pdf_folder_path: str = "./pdfs/subjects",
                 chunk_size: int = 1000,
                 chunk_overlap: int = 200,
                 subjects: List[str] = None):
        """
        Initialize the vector indexing service.
        
        Args:
            pdf_folder_path: Path to the subjects PDF directory
            chunk_size: Size of text chunks for embedding
            chunk_overlap: Overlap between chunks
            subjects: List of subjects to process (default: auto-detect)
        """
        self.pdf_folder_path = Path(pdf_folder_path)
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        
        # Auto-detect subjects if not provided
        if subjects is None:
            self.subjects = self._detect_subjects()
        else:
            self.subjects = subjects
        
        # Get model service instance
        self.model_service = get_model_service()
        
        # Metadata tracking
        self.index_metadata_path = self.pdf_folder_path.parent / "index_metadata.json"
        self.index_metadata = self._load_index_metadata()
    
    def _detect_subjects(self) -> List[str]:
        """Auto-detect available subjects from PDF folder structure"""
        subjects = []
        if self.pdf_folder_path.exists():
            for item in self.pdf_folder_path.iterdir():
                if item.is_dir() and not item.name.startswith('.'):
                    subjects.append(item.name.lower())
        
        logger.info(f"📚 Detected subjects: {subjects}")
        return subjects
    
    def _load_index_metadata(self) -> Dict:
        """Load indexing metadata for tracking changes"""
        if self.index_metadata_path.exists():
            try:
                with open(self.index_metadata_path, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"Failed to load index metadata: {e}")
        
        return {
            'last_indexed': {},
            'file_checksums': {},
            'collection_info': {}
        }
    
    def _save_index_metadata(self):
        """Save indexing metadata"""
        try:
            with open(self.index_metadata_path, 'w') as f:
                json.dump(self.index_metadata, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save index metadata: {e}")
    
    def _calculate_file_checksum(self, file_path: Path) -> str:
        """Calculate MD5 checksum of a file"""
        hash_md5 = hashlib.md5()
        try:
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_md5.update(chunk)
            return hash_md5.hexdigest()
        except Exception as e:
            logger.error(f"Failed to calculate checksum for {file_path}: {e}")
            return ""
    
    def _extract_text_from_pdf(self, pdf_path: Path) -> str:
        """Extract text content from a PDF file"""
        if not PYPDF2_AVAILABLE:
            logger.error("PyPDF2 not available for PDF processing")
            return ""
        
        try:
            text = ""
            with open(pdf_path, 'rb') as file:
                pdf_reader = PdfReader(file)
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
            
            return text.strip()
        except Exception as e:
            logger.error(f"Failed to extract text from {pdf_path}: {e}")
            return ""
    
    def _chunk_text(self, text: str, metadata: Dict) -> List[Dict]:
        """Split text into overlapping chunks with metadata"""
        if not text:
            return []
        
        chunks = []
        start = 0
        chunk_id = 0
        
        while start < len(text):
            end = start + self.chunk_size
            chunk_text = text[start:end]
            
            # Try to break at sentence boundaries
            if end < len(text):
                last_period = chunk_text.rfind('.')
                last_newline = chunk_text.rfind('\n')
                break_point = max(last_period, last_newline)
                
                if break_point > start + self.chunk_size // 2:
                    chunk_text = text[start:start + break_point + 1]
                    end = start + break_point + 1
            
            chunk_metadata = {
                **metadata,
                'chunk_id': chunk_id,
                'start_char': start,
                'end_char': end,
                'chunk_length': len(chunk_text)
            }
            
            chunks.append({
                'content': chunk_text.strip(),
                'metadata': chunk_metadata
            })
            
            start = end - self.chunk_overlap
            chunk_id += 1
        
        return chunks
    
    def _get_subject_pdfs(self, subject: str) -> List[Path]:
        """Get all PDF files for a specific subject"""
        subject_path = self.pdf_folder_path / subject
        if not subject_path.exists():
            logger.warning(f"Subject directory not found: {subject_path}")
            return []
        
        pdf_files = list(subject_path.glob("*.pdf"))
        logger.info(f"📄 Found {len(pdf_files)} PDF files for {subject}")
        return pdf_files
    
    def _check_if_reindexing_needed(self, subject: str, pdf_files: List[Path]) -> Tuple[bool, List[Path]]:
        """Check if re-indexing is needed for a subject"""
        if subject not in self.index_metadata['last_indexed']:
            return True, pdf_files
        
        files_to_reindex = []
        
        for pdf_file in pdf_files:
            file_key = str(pdf_file.relative_to(self.pdf_folder_path))
            current_checksum = self._calculate_file_checksum(pdf_file)
            
            if (file_key not in self.index_metadata['file_checksums'] or 
                self.index_metadata['file_checksums'][file_key] != current_checksum):
                files_to_reindex.append(pdf_file)
        
        return len(files_to_reindex) > 0, files_to_reindex
    
    def index_subject(self, subject: str, force_recreate: bool = False) -> Dict:
        """
        Index all PDFs for a specific subject.
        
        Args:
            subject: Subject name to index
            force_recreate: Force recreation of the collection
            
        Returns:
            Dict with indexing results
        """
        start_time = time.time()
        logger.info(f"🔄 Starting indexing for subject: {subject}")
        
        # Get model service components
        chroma_client = self.model_service.get_chroma_client()
        embedding_model = self.model_service.get_embedding_model()
        
        if not chroma_client or not embedding_model:
            return {
                'success': False,
                'error': 'Required models not initialized',
                'subject': subject
            }
        
        # Get PDF files for this subject
        pdf_files = self._get_subject_pdfs(subject)
        if not pdf_files:
            return {
                'success': False,
                'error': f'No PDF files found for subject: {subject}',
                'subject': subject
            }
        
        # Check if re-indexing is needed
        if not force_recreate:
            needs_reindex, files_to_process = self._check_if_reindexing_needed(subject, pdf_files)
            if not needs_reindex:
                logger.info(f"✅ Subject {subject} is up to date, skipping indexing")
                return {
                    'success': True,
                    'skipped': True,
                    'subject': subject,
                    'message': 'Subject is up to date'
                }
        else:
            files_to_process = pdf_files
        
        try:
            # Create or get collection
            collection_name = f"subject_{subject}"
            
            if force_recreate:
                try:
                    chroma_client.delete_collection(collection_name)
                    logger.info(f"🗑️ Deleted existing collection: {collection_name}")
                except Exception:
                    pass  # Collection might not exist
            
            collection = chroma_client.get_or_create_collection(
                name=collection_name,
                metadata={"subject": subject, "indexed_at": datetime.now().isoformat()}
            )
            
            # Process each PDF file
            total_chunks = 0
            processed_files = []
            
            for pdf_file in files_to_process:
                logger.info(f"📄 Processing: {pdf_file.name}")
                
                # Extract text
                text_content = self._extract_text_from_pdf(pdf_file)
                if not text_content:
                    logger.warning(f"⚠️ No text extracted from {pdf_file.name}")
                    continue
                
                # Create chunks
                file_metadata = {
                    'source_file': pdf_file.name,
                    'subject': subject,
                    'file_path': str(pdf_file.relative_to(self.pdf_folder_path)),
                    'indexed_at': datetime.now().isoformat()
                }
                
                chunks = self._chunk_text(text_content, file_metadata)
                if not chunks:
                    continue
                
                # Generate embeddings
                chunk_texts = [chunk['content'] for chunk in chunks]
                embeddings = embedding_model.encode(chunk_texts).tolist()
                
                # Prepare data for ChromaDB
                chunk_ids = [f"{subject}_{pdf_file.stem}_{i}" for i in range(len(chunks))]
                metadatas = [chunk['metadata'] for chunk in chunks]
                
                # Add to collection
                collection.add(
                    ids=chunk_ids,
                    embeddings=embeddings,
                    documents=chunk_texts,
                    metadatas=metadatas
                )
                
                total_chunks += len(chunks)
                processed_files.append(pdf_file.name)
                
                # Update file checksum
                file_key = str(pdf_file.relative_to(self.pdf_folder_path))
                self.index_metadata['file_checksums'][file_key] = self._calculate_file_checksum(pdf_file)
            
            # Update metadata
            self.index_metadata['last_indexed'][subject] = datetime.now().isoformat()
            self.index_metadata['collection_info'][subject] = {
                'collection_name': collection_name,
                'total_chunks': total_chunks,
                'processed_files': processed_files,
                'last_updated': datetime.now().isoformat()
            }
            
            self._save_index_metadata()
            
            indexing_time = time.time() - start_time
            logger.info(f"✅ Indexed {subject}: {total_chunks} chunks from {len(processed_files)} files in {indexing_time:.2f}s")
            
            return {
                'success': True,
                'subject': subject,
                'total_chunks': total_chunks,
                'processed_files': processed_files,
                'indexing_time': indexing_time,
                'collection_name': collection_name
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to index subject {subject}: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'subject': subject
            }
    
    def index_all_subjects(self, force_recreate: bool = False) -> Dict:
        """
        Index all available subjects.
        
        Args:
            force_recreate: Force recreation of all collections
            
        Returns:
            Dict with overall indexing results
        """
        start_time = time.time()
        logger.info(f"🚀 Starting indexing for all subjects: {self.subjects}")
        
        results = {}
        successful_subjects = []
        
        for subject in self.subjects:
            result = self.index_subject(subject, force_recreate)
            results[subject] = result
            
            if result['success'] and not result.get('skipped', False):
                successful_subjects.append(subject)
        
        total_time = time.time() - start_time
        
        return {
            'success': len(successful_subjects) > 0,
            'results': results,
            'successful_subjects': successful_subjects,
            'total_subjects': len(self.subjects),
            'successful_count': len(successful_subjects),
            'total_time': total_time
        }
    
    def get_indexing_status(self) -> Dict:
        """Get comprehensive indexing status"""
        chroma_client = self.model_service.get_chroma_client()
        
        status = {
            'service_name': 'VectorIndexService',
            'subjects': self.subjects,
            'configuration': {
                'pdf_folder_path': str(self.pdf_folder_path),
                'chunk_size': self.chunk_size,
                'chunk_overlap': self.chunk_overlap
            },
            'collections': {},
            'last_indexed': self.index_metadata.get('last_indexed', {}),
            'dependencies': {
                'model_service': self.model_service.get_status(),
                'pypdf2': PYPDF2_AVAILABLE
            }
        }
        
        if chroma_client:
            try:
                collections = chroma_client.list_collections()
                for collection in collections:
                    if collection.name.startswith('subject_'):
                        subject = collection.name.replace('subject_', '')
                        try:
                            count = collection.count()
                            status['collections'][subject] = {
                                'name': collection.name,
                                'count': count,
                                'metadata': collection.metadata
                            }
                        except Exception as e:
                            status['collections'][subject] = {
                                'name': collection.name,
                                'error': str(e)
                            }
            except Exception as e:
                status['collections_error'] = str(e)
        
        return status


# Global vector index service instance
_vector_index_service: Optional[VectorIndexService] = None


def get_vector_index_service(**kwargs) -> VectorIndexService:
    """Get or create the global vector index service instance"""
    global _vector_index_service
    
    if _vector_index_service is None:
        _vector_index_service = VectorIndexService(**kwargs)
    
    return _vector_index_service
