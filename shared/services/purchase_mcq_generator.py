"""
Purchase-Time MCQ Generator
Uses pre-built ChromaDB vector store for instant MCQ generation at purchase time
No re-chunking or re-embedding - only retrieval and generation
"""

import logging
import json
from typing import Dict, List, Optional
from datetime import datetime

from config import Config
from shared.services.multimodal_rag_service import (
    get_multimodal_rag_service,
    embed_text
)

logger = logging.getLogger(__name__)


class PurchaseMCQGenerator:
    """Generate MCQs instantly at purchase time using pre-built vector store"""

    def __init__(self):
        """Initialize with pre-built vector store"""
        self.service = get_multimodal_rag_service(
            chromadb_path=Config.MULTIMODAL_CHROMADB_PATH,
            ollama_model=Config.MULTIMODAL_OLLAMA_MODEL
        )
        self.cache = {}
        logger.info("✅ PurchaseMCQGenerator initialized with pre-built vector store")

    def validate_subject(self, subject: str) -> bool:
        """Validate subject exists in vector store"""
        try:
            collections = self.service.client.list_collections()
            collection_names = [c.name for c in collections]
            return subject.lower() in collection_names
        except Exception as e:
            logger.error(f"Error validating subject: {e}")
            return False

    def retrieve_context(self, subject: str, query: str, k: int = 5) -> List[Dict]:
        """Retrieve context from pre-built vector store"""
        try:
            logger.info(f"Retrieving context for {subject}: {query}")
            
            # Use pre-built vector store
            retrieved_docs = self.service.retrieve_multimodal(
                query=query,
                subject=subject,
                k=k
            )
            
            if not retrieved_docs:
                logger.warning(f"No context found for {subject}")
                return []
            
            logger.info(f"Retrieved {len(retrieved_docs)} documents")
            return retrieved_docs
            
        except Exception as e:
            logger.error(f"Error retrieving context: {e}")
            return []

    def generate_mcq_for_purchase(
        self,
        subject: str,
        num_questions: int = 5,
        difficulty: str = "medium",
        query: Optional[str] = None
    ) -> Dict:
        """
        Generate MCQs instantly at purchase time
        
        Args:
            subject: Subject name (physics, chemistry, etc.)
            num_questions: Number of questions to generate (1-10)
            difficulty: Difficulty level (easy, medium, hard)
            query: Optional specific topic query
        
        Returns:
            Dict with success status and questions
        """
        try:
            logger.info(f"🎯 Generating MCQs for purchase: {subject}, {num_questions} questions")
            
            # Validate subject
            if not self.validate_subject(subject):
                return {
                    "success": False,
                    "error": f"Subject not found in vector store: {subject}",
                    "available_subjects": self._get_available_subjects()
                }
            
            # Use subject as query if not provided
            if not query:
                query = subject
            
            # Retrieve context from pre-built vector store
            retrieved_docs = self.retrieve_context(subject, query, k=5)
            
            if not retrieved_docs:
                return {
                    "success": False,
                    "error": f"No content found for subject: {subject}"
                }
            
            # Build context from retrieved documents
            context_parts = []
            for doc in retrieved_docs:
                content = doc.get("content", "")
                if content and not content.startswith("[Image:"):
                    context_parts.append(content)
            
            if not context_parts:
                return {
                    "success": False,
                    "error": "No text content found for MCQ generation"
                }
            
            context = "\n".join(context_parts[:3])  # Use top 3 documents
            
            # Generate MCQs using Ollama
            result = self.service.generate_mcq(
                query=query,
                subject=subject,
                num_questions=num_questions
            )
            
            if result.get("success"):
                # Add purchase metadata
                questions = result.get("questions", [])
                for q in questions:
                    q["purchase_generated"] = True
                    q["generated_at"] = datetime.now().isoformat()
                    q["difficulty"] = difficulty
                
                logger.info(f"✅ Generated {len(questions)} MCQs for purchase")
                return {
                    "success": True,
                    "questions": questions,
                    "subject": subject,
                    "num_questions": len(questions),
                    "difficulty": difficulty,
                    "generation_method": "purchase_vector_store",
                    "generation_time": result.get("generation_time", 0)
                }
            else:
                return {
                    "success": False,
                    "error": result.get("error", "Failed to generate MCQs")
                }
            
        except Exception as e:
            logger.error(f"Error generating MCQs for purchase: {e}", exc_info=True)
            return {
                "success": False,
                "error": f"MCQ generation failed: {str(e)}"
            }

    def batch_generate_for_purchase(
        self,
        subject: str,
        num_sets: int = 3,
        questions_per_set: int = 5
    ) -> Dict:
        """
        Generate multiple MCQ sets for a purchase
        
        Args:
            subject: Subject name
            num_sets: Number of MCQ sets to generate
            questions_per_set: Questions per set
        
        Returns:
            Dict with all generated MCQ sets
        """
        try:
            logger.info(f"Batch generating {num_sets} MCQ sets for {subject}")
            
            all_sets = []
            for i in range(num_sets):
                result = self.generate_mcq_for_purchase(
                    subject=subject,
                    num_questions=questions_per_set,
                    query=f"{subject} topic {i+1}"
                )
                
                if result.get("success"):
                    all_sets.append({
                        "set_number": i + 1,
                        "questions": result.get("questions", [])
                    })
                else:
                    logger.warning(f"Failed to generate set {i+1}: {result.get('error')}")
            
            return {
                "success": len(all_sets) > 0,
                "total_sets": len(all_sets),
                "total_questions": sum(len(s["questions"]) for s in all_sets),
                "sets": all_sets,
                "subject": subject
            }
            
        except Exception as e:
            logger.error(f"Error in batch generation: {e}")
            return {
                "success": False,
                "error": f"Batch generation failed: {str(e)}"
            }

    def _get_available_subjects(self) -> List[str]:
        """Get list of available subjects in vector store"""
        try:
            collections = self.service.client.list_collections()
            return [c.name for c in collections]
        except Exception as e:
            logger.error(f"Error getting available subjects: {e}")
            return []

    def get_vector_store_stats(self) -> Dict:
        """Get statistics about the vector store"""
        try:
            stats = {
                "subjects": [],
                "total_documents": 0,
                "total_images": 0
            }
            
            collections = self.service.client.list_collections()
            for collection in collections:
                count = collection.count()
                stats["subjects"].append({
                    "name": collection.name,
                    "document_count": count
                })
                stats["total_documents"] += count
            
            return {
                "success": True,
                "stats": stats
            }
        except Exception as e:
            logger.error(f"Error getting vector store stats: {e}")
            return {
                "success": False,
                "error": str(e)
            }


# Global instance
_purchase_mcq_generator = None


def get_purchase_mcq_generator() -> PurchaseMCQGenerator:
    """Get or create global PurchaseMCQGenerator instance"""
    global _purchase_mcq_generator
    if _purchase_mcq_generator is None:
        _purchase_mcq_generator = PurchaseMCQGenerator()
    return _purchase_mcq_generator

