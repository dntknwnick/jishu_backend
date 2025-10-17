"""
Multimodal PDF RAG System using CLIP, ChromaDB, and Ollama Qwen2-VL
Processes PDFs with text and images, creates unified embeddings, and generates MCQs/answers
"""

import os
import io
import base64
import json
import logging
import numpy as np
import fitz  # PyMuPDF
import torch
from PIL import Image
from transformers import CLIPModel, CLIPProcessor
from typing import List, Dict, Tuple, Optional
import ollama

# Fix ChromaDB Pydantic validation issue BEFORE importing chromadb
import warnings
warnings.filterwarnings('ignore', category=DeprecationWarning)
warnings.filterwarnings('ignore', category=UserWarning)

# Clear old ChromaDB environment variables that cause deprecated configuration error
# These are from the old ChromaDB API and cause validation errors in 1.1.1
chroma_keys_to_remove = [
    'CHROMA_DB_IMPL', 'CHROMA_TELEMETRY_IMPL', 'CHROMA_SERVER_NOFILE',
    'CHROMA_ANONYMIZED_TELEMETRY', 'CHROMA_USE_HTTP'
]
for key in chroma_keys_to_remove:
    if key in os.environ:
        del os.environ[key]

# Suppress Pydantic warnings
os.environ['PYTHONWARNINGS'] = 'ignore::DeprecationWarning'

import chromadb
from chromadb.utils.embedding_functions import EmbeddingFunction

logger = logging.getLogger(__name__)

# Initialize CLIP Model for unified embeddings
try:
    logger.info("Loading CLIP model...")
    clip_model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
    clip_processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")
    clip_model.eval()
    CLIP_AVAILABLE = True
    logger.info("✅ CLIP model loaded successfully")
except Exception as e:
    logger.error(f"❌ Failed to load CLIP model: {e}")
    CLIP_AVAILABLE = False


class CLIPEmbeddingFunction(EmbeddingFunction):
    """Custom CLIP embedding function for ChromaDB"""

    def __call__(self, input: List[str]) -> List[List[float]]:
        """Embed texts using CLIP"""
        embeddings = []
        for text in input:
            try:
                embedding = embed_text(text)
                embeddings.append(embedding.tolist())
            except Exception as e:
                logger.error(f"Error embedding text: {e}")
                embeddings.append([0.0] * 512)  # Fallback embedding
        return embeddings


def embed_image(image_data) -> np.ndarray:
    """Embed image using CLIP"""
    if not CLIP_AVAILABLE:
        raise RuntimeError("CLIP model not available")
    
    if isinstance(image_data, str):
        image = Image.open(image_data).convert("RGB")
    else:
        image = image_data

    inputs = clip_processor(images=image, return_tensors="pt")
    with torch.no_grad():
        features = clip_model.get_image_features(**inputs)
        features = features / features.norm(dim=-1, keepdim=True)
    return features.squeeze().numpy()


def embed_text(text: str) -> np.ndarray:
    """Embed text using CLIP"""
    if not CLIP_AVAILABLE:
        raise RuntimeError("CLIP model not available")
    
    inputs = clip_processor(
        text=text,
        return_tensors="pt",
        padding=True,
        truncation=True,
        max_length=77
    )
    with torch.no_grad():
        features = clip_model.get_text_features(**inputs)
        features = features / features.norm(dim=-1, keepdim=True)
    return features.squeeze().numpy()


def chunk_text(text: str, chunk_size: int = 500, chunk_overlap: int = 100) -> List[str]:
    """Chunk text using character-based splitting"""
    chunks = []
    start = 0
    text_len = len(text)

    while start < text_len:
        end = start + chunk_size
        chunk = text[start:end]
        if chunk.strip():
            chunks.append(chunk)
        start += chunk_size - chunk_overlap

    return chunks


def process_pdf(pdf_path: str, chunk_size: int = 500, chunk_overlap: int = 100) -> Tuple[List[Dict], List[np.ndarray], Dict]:
    """Process PDF and extract text and images with embeddings"""
    logger.info(f"📄 Processing PDF: {pdf_path}")
    
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"PDF not found: {pdf_path}")
    
    doc = fitz.open(pdf_path)
    all_docs = []
    all_embeddings = []
    image_data_store = {}

    for i, page in enumerate(doc):
        logger.info(f"Processing page {i+1}/{len(doc)}")

        # Process text
        text = page.get_text()
        if text.strip():
            text_chunks = chunk_text(text, chunk_size, chunk_overlap)
            for chunk_idx, chunk in enumerate(text_chunks):
                try:
                    embedding = embed_text(chunk)
                    all_embeddings.append(embedding)
                    all_docs.append({
                        "content": chunk,
                        "page": i,
                        "type": "text",
                        "chunk_index": chunk_idx
                    })
                except Exception as e:
                    logger.error(f"Error processing text chunk: {e}")

        # Process images
        for img_index, img in enumerate(page.get_images(full=True)):
            try:
                xref = img[0]
                base_image = doc.extract_image(xref)
                image_bytes = base_image["image"]
                pil_image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
                image_id = f"page_{i}_img_{img_index}"

                # Store as base64
                buffered = io.BytesIO()
                pil_image.save(buffered, format="PNG")
                img_base64 = base64.b64encode(buffered.getvalue()).decode()
                image_data_store[image_id] = img_base64

                # Embed image
                embedding = embed_image(pil_image)
                all_embeddings.append(embedding)
                all_docs.append({
                    "content": f"[Image: {image_id}]",
                    "page": i,
                    "type": "image",
                    "image_id": image_id
                })
            except Exception as e:
                logger.error(f"Error processing image {img_index} on page {i}: {e}")

    doc.close()
    logger.info(f"✅ Processed {len(all_docs)} documents")
    return all_docs, all_embeddings, image_data_store


class MultimodalRAGService:
    """Main multimodal RAG service"""

    def __init__(self, chromadb_path: str, ollama_model: str = "llava"):
        self.chromadb_path = chromadb_path
        self.ollama_model = ollama_model

        # Initialize ChromaDB using the new API (v1.1.1+)
        try:
            # Create directory if it doesn't exist
            os.makedirs(chromadb_path, exist_ok=True)

            # Use the new ChromaDB API with persistent storage
            # PersistentClient stores data in the specified path
            self.client = chromadb.PersistentClient(path=chromadb_path)

            logger.info(f"ChromaDB client initialized (persistent storage at {chromadb_path})")
        except Exception as e:
            logger.error(f"Failed to initialize ChromaDB: {e}")
            raise

        self.collections = {}
        self.image_stores = {}
        logger.info(f"MultimodalRAGService initialized with model: {ollama_model}")

    def initialize_subject_collection(self, subject: str, pdf_path: str, chunk_size: int = 500, chunk_overlap: int = 100):
        """Initialize ChromaDB collection for a subject"""
        logger.info(f"Initializing collection for subject: {subject}")
        
        # Process PDF
        all_docs, all_embeddings, image_data_store = process_pdf(pdf_path, chunk_size, chunk_overlap)
        
        # Create collection
        collection = self.client.get_or_create_collection(
            name=subject.lower(),
            embedding_function=CLIPEmbeddingFunction(),
            metadata={"description": f"Multimodal embeddings for {subject}"}
        )

        # Add to ChromaDB
        ids = [f"doc_{i}" for i in range(len(all_docs))]
        documents = [doc["content"] for doc in all_docs]
        metadatas = [{k: v for k, v in doc.items() if k != "content"} for doc in all_docs]
        embeddings = [emb.tolist() for emb in all_embeddings]

        batch_size = 100
        for i in range(0, len(ids), batch_size):
            batch_end = min(i + batch_size, len(ids))
            collection.add(
                ids=ids[i:batch_end],
                documents=documents[i:batch_end],
                metadatas=metadatas[i:batch_end],
                embeddings=embeddings[i:batch_end]
            )

        self.collections[subject.lower()] = collection
        self.image_stores[subject.lower()] = image_data_store
        logger.info(f"✅ Collection initialized for {subject} with {len(all_docs)} documents")

    def retrieve_multimodal(self, query: str, subject: str, k: int = 5) -> List[Dict]:
        """Retrieve relevant documents using CLIP embeddings"""
        subject_key = subject.lower()
        if subject_key not in self.collections:
            logger.warning(f"Collection not found for subject: {subject}")
            return []

        query_embedding = embed_text(query)
        collection = self.collections[subject_key]
        
        results = collection.query(
            query_embeddings=[query_embedding.tolist()],
            n_results=k
        )

        retrieved_docs = []
        for i in range(len(results["ids"][0])):
            retrieved_docs.append({
                "content": results["documents"][0][i],
                "metadata": results["metadatas"][0][i],
                "distance": results["distances"][0][i] if "distances" in results else None
            })

        return retrieved_docs

    def generate_mcq(self, query: str, subject: str, num_questions: int = 5) -> Dict:
        """Generate MCQ questions using multimodal context"""
        try:
            subject_key = subject.lower()
            retrieved_docs = self.retrieve_multimodal(query, subject, k=5)
            
            if not retrieved_docs:
                return {"success": False, "error": f"No content found for subject: {subject}"}

            # Create prompt
            prompt_parts = [
                f"Generate {num_questions} multiple-choice questions based on the following educational content.\n"
                f"Each question must be in JSON format:\n"
                f"[{{\"question\": \"str\", \"option_a\": \"str\", \"option_b\": \"str\", "
                f"\"option_c\": \"str\", \"option_d\": \"str\", \"correct_answer\": \"str\"}}, ...]\n\n"
                f"### Topic: {query}\n\n### Context:\n"
            ]

            images = []
            for doc in retrieved_docs:
                if doc["metadata"].get("type") == "text":
                    prompt_parts.append(f"{doc['content']}\n")
                elif doc["metadata"].get("type") == "image":
                    image_id = doc["metadata"].get("image_id")
                    if image_id and image_id in self.image_stores.get(subject_key, {}):
                        images.append(self.image_stores[subject_key][image_id])

            prompt_text = "".join(prompt_parts)

            # Call Ollama
            messages = [{"role": "user", "content": prompt_text}]
            if images:
                messages[0]["content"] = [{"type": "text", "text": prompt_text}]
                for img_b64 in images:
                    messages[0]["content"].append({
                        "type": "image_url",
                        "image_url": f"data:image/png;base64,{img_b64}"
                    })

            response = ollama.chat(model=self.ollama_model, messages=messages)
            answer = response["message"]["content"]

            # Parse JSON
            try:
                questions = json.loads(answer)
                return {"success": True, "questions": questions, "model_used": self.ollama_model}
            except json.JSONDecodeError:
                return {"success": False, "error": "Failed to parse MCQ JSON", "raw_response": answer}

        except Exception as e:
            logger.error(f"Error generating MCQ: {e}")
            return {"success": False, "error": str(e)}

    def generate_chat_response(self, query: str, subject: str) -> Dict:
        """Generate chat response using multimodal context"""
        try:
            retrieved_docs = self.retrieve_multimodal(query, subject, k=3)
            
            if not retrieved_docs:
                return {"success": False, "error": "No relevant content found"}

            context = "\n".join([doc["content"] for doc in retrieved_docs])
            prompt = f"Context: {context}\n\nQuestion: {query}\n\nAnswer briefly:"

            response = ollama.chat(model=self.ollama_model, messages=[{"role": "user", "content": prompt}])
            
            return {
                "success": True,
                "response": response["message"]["content"],
                "model_used": self.ollama_model
            }

        except Exception as e:
            logger.error(f"Error generating chat response: {e}")
            return {"success": False, "error": str(e)}


# Global service instance
_multimodal_service = None

def get_multimodal_rag_service(chromadb_path: str, ollama_model: str = "llava") -> MultimodalRAGService:
    """Get or create global multimodal RAG service"""
    global _multimodal_service
    if _multimodal_service is None:
        _multimodal_service = MultimodalRAGService(chromadb_path, ollama_model)
    return _multimodal_service

