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

        # Load existing collections from ChromaDB
        self._load_existing_collections()

        logger.info(f"MultimodalRAGService initialized with model: {ollama_model}")

    def _load_existing_collections(self):
        """Load existing collections from ChromaDB persistent storage"""
        try:
            existing_collections = self.client.list_collections()
            logger.info(f"Found {len(existing_collections)} existing collections in ChromaDB")

            for collection in existing_collections:
                collection_name = collection.name
                try:
                    # Try to get the collection WITHOUT specifying embedding function first
                    # The embedding function is already persisted in the collection metadata
                    try:
                        col = self.client.get_collection(name=collection_name)
                    except Exception as e:
                        # If that fails, try with the CLIP embedding function
                        logger.warning(f"Trying with CLIP embedding function for {collection_name}: {e}")
                        col = self.client.get_collection(
                            name=collection_name,
                            embedding_function=CLIPEmbeddingFunction()
                        )

                    self.collections[collection_name] = col
                    doc_count = col.count()
                    logger.info(f"✅ Loaded collection: {collection_name} with {doc_count} documents")
                except Exception as e:
                    logger.warning(f"Failed to load collection {collection_name}: {e}")
        except Exception as e:
            logger.warning(f"Error loading existing collections: {e}")

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

    def generate_mcq_chunk(self, query: str, subject: str, num_questions: int = 5, chunk_num: int = 1) -> Dict:
        """Generate a chunk of MCQ questions (5 at a time to avoid timeout)

        Args:
            query: Topic/subject query
            subject: Subject name
            num_questions: Number of questions to generate (default 5)
            chunk_num: Chunk number for logging
        """
        try:
            subject_key = subject.lower()

            logger.info(f"🔄 Generating chunk {chunk_num}: {num_questions} questions for {subject}...")

            # Retrieve docs for this chunk
            retrieved_docs = self.retrieve_multimodal(query, subject, k=5)

            # If no docs found in specific subject, search across all collections
            if not retrieved_docs:
                logger.warning(f"⚠️ No docs found in '{subject}', searching across all collections...")

                all_docs = []
                for collection_name in self.collections.keys():
                    try:
                        docs = self.retrieve_multimodal(query, collection_name, k=3)
                        if docs:
                            all_docs.extend(docs)
                    except Exception as e:
                        logger.warning(f"  ❌ Error searching {collection_name}: {e}")

                retrieved_docs = all_docs[:5]

                if not retrieved_docs:
                    logger.error(f"❌ No content found for chunk {chunk_num}")
                    return {"success": False, "error": f"No content found for subject: {subject}"}

            # Create prompt for this chunk - SIMPLIFIED for better JSON output
            prompt_parts = [
                f"Generate {num_questions} multiple-choice questions.\n"
                f"Return ONLY valid JSON array. No text before or after.\n"
                f"Format: [{{\n"
                f'  "question": "Q text",\n'
                f'  "option_a": "A",\n'
                f'  "option_b": "B",\n'
                f'  "option_c": "C",\n'
                f'  "option_d": "D",\n'
                f'  "correct_answer": "A or B or C or D"\n'
                f"}}]\n\n"
                f"Topic: {query}\n\n"
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

            # Call Ollama with timeout
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

            logger.info(f"📝 Raw response length: {len(answer)} chars")

            # Parse JSON - try multiple approaches
            questions = None
            import re

            # Approach 1: Direct JSON parsing
            try:
                questions = json.loads(answer)
                logger.info(f"✅ Direct JSON parsing successful")
            except json.JSONDecodeError as e:
                logger.warning(f"⚠️ Direct JSON parsing failed: {str(e)[:100]}")

                # Approach 2: Remove markdown code blocks
                try:
                    cleaned = answer.replace("```json", "").replace("```", "").strip()
                    questions = json.loads(cleaned)
                    logger.info(f"✅ Cleaned markdown JSON parsing successful")
                except json.JSONDecodeError:
                    logger.warning(f"⚠️ Cleaned markdown parsing failed")

                # Approach 3: Extract JSON array with regex
                if not questions:
                    try:
                        # Find the first [ and last ]
                        start_idx = answer.find('[')
                        end_idx = answer.rfind(']')
                        if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
                            json_str = answer[start_idx:end_idx+1]
                            questions = json.loads(json_str)
                            logger.info(f"✅ Extracted JSON array successfully")
                    except json.JSONDecodeError:
                        logger.warning(f"⚠️ JSON array extraction failed")

                # Approach 4: Try to fix common JSON issues (trailing commas, single quotes, escaped backslashes)
                if not questions:
                    try:
                        # Remove trailing commas before ] or }
                        cleaned = re.sub(r',(\s*[}\]])', r'\1', answer)
                        # Replace single quotes with double quotes (but be careful)
                        cleaned = cleaned.replace("'", '"')
                        # Fix escaped underscores and other characters in JSON (e.g., \_ becomes _)
                        # This handles cases where Ollama escapes special characters
                        cleaned = re.sub(r'\\_', '_', cleaned)  # \_ -> _
                        cleaned = re.sub(r'\\-', '-', cleaned)  # \- -> -
                        cleaned = re.sub(r'\\:', ':', cleaned)  # \: -> :
                        cleaned = re.sub(r'\\.', '.', cleaned)  # \. -> .
                        questions = json.loads(cleaned)
                        logger.info(f"✅ Fixed JSON syntax successfully")
                    except json.JSONDecodeError:
                        logger.warning(f"⚠️ JSON syntax fixing failed")

                # Approach 5: Extract just the first valid JSON object/array
                if not questions:
                    try:
                        # Try to find valid JSON by looking for complete objects
                        matches = re.findall(r'\[.*?\]', answer, re.DOTALL)
                        if matches:
                            for match in matches:
                                try:
                                    questions = json.loads(match)
                                    logger.info(f"✅ Extracted first valid JSON array")
                                    break
                                except:
                                    continue
                    except Exception as e:
                        logger.warning(f"⚠️ Regex extraction failed: {str(e)[:100]}")

            # If we got questions, validate and return them
            if questions and isinstance(questions, list) and len(questions) > 0:
                logger.info(f"✅ Chunk {chunk_num} generated: {len(questions)} questions")
                return {"success": True, "questions": questions, "model_used": self.ollama_model}
            else:
                logger.error(f"❌ Failed to parse valid JSON for chunk {chunk_num}")
                logger.error(f"Raw response (first 300 chars): {answer[:300]}")
                return {"success": False, "error": "Failed to parse MCQ JSON", "raw_response": answer[:300]}

        except Exception as e:
            logger.error(f"Error generating MCQ chunk {chunk_num}: {e}")
            return {"success": False, "error": str(e)}

    def generate_mcq_initial(self, query: str, subject: str, num_questions: int = 10) -> Dict:
        """Generate initial batch of MCQ questions (10 questions)

        This is called first to return questions immediately to user.
        Then background generation continues for remaining questions.
        """
        try:
            subject_key = subject.lower()
            logger.info(f"🚀 Generating initial batch: {num_questions} questions for {subject}...")

            # Generate just the initial batch
            result = self.generate_mcq_chunk(
                query=query,
                subject=subject,
                num_questions=num_questions,
                chunk_num=1
            )

            if result.get('success') and result.get('questions'):
                logger.info(f"✅ Initial batch generated: {len(result['questions'])} questions")
                return result
            else:
                error_msg = result.get('error', 'Unknown error')
                logger.error(f"❌ Initial batch generation failed: {error_msg}")
                return result

        except Exception as e:
            logger.error(f"Error in initial MCQ generation: {e}", exc_info=True)
            return {"success": False, "error": str(e)}

    def generate_mcq(self, query: str, subject: str, num_questions: int = 50) -> Dict:
        """Generate MCQ questions in chunks (5 questions per chunk)

        Generates questions in chunks to avoid timeout issues with Ollama.
        For 50 questions: generates 10 chunks of 5 questions each.
        """
        try:
            subject_key = subject.lower()

            # Log available collections for debugging
            logger.info(f"📚 Available collections: {list(self.collections.keys())}")
            logger.info(f"🔍 Looking for collection: {subject_key}")
            logger.info(f"🎯 Generating {num_questions} questions in chunks of 5...")

            all_questions = []
            chunk_size = 5
            num_chunks = (num_questions + chunk_size - 1) // chunk_size  # Ceiling division

            # Generate questions in chunks
            for chunk_num in range(1, num_chunks + 1):
                logger.info(f"\n📝 Chunk {chunk_num}/{num_chunks}...")

                result = self.generate_mcq_chunk(
                    query=query,
                    subject=subject,
                    num_questions=chunk_size,
                    chunk_num=chunk_num
                )

                if result.get('success') and result.get('questions'):
                    all_questions.extend(result['questions'])
                    logger.info(f"✅ Total questions so far: {len(all_questions)}")
                else:
                    error_msg = result.get('error', 'Unknown error')
                    logger.warning(f"⚠️ Chunk {chunk_num} failed: {error_msg}")
                    # Continue with next chunk even if one fails

            # Return all generated questions
            if all_questions:
                logger.info(f"\n✅ MCQ generation complete: {len(all_questions)} questions generated")
                return {"success": True, "questions": all_questions, "model_used": self.ollama_model}
            else:
                logger.error(f"❌ No questions generated after {num_chunks} chunks")
                return {"success": False, "error": f"Failed to generate questions after {num_chunks} attempts"}

        except Exception as e:
            logger.error(f"Error in chunked MCQ generation: {e}", exc_info=True)
            return {"success": False, "error": str(e)}

    def generate_chat_response(self, query: str, subject: str = None) -> Dict:
        """Generate chat response using multimodal context from all available collections

        For chatbot use case: searches across ALL collections to answer any educational question
        This supports multi-subject queries like "Compare Newton's Laws with atomic structure"
        """
        try:
            logger.info(f"🤖 Generating chat response for query: {query[:80]}...")
            logger.info(f"📚 Available collections: {list(self.collections.keys())}")

            # For chat, search across ALL collections to get comprehensive context
            # This allows answering multi-subject questions
            all_docs = []
            docs_by_collection = {}

            for collection_name in self.collections.keys():
                try:
                    docs = self.retrieve_multimodal(query, collection_name, k=3)
                    if docs:
                        all_docs.extend(docs)
                        docs_by_collection[collection_name] = len(docs)
                        logger.info(f"  ✅ {collection_name}: {len(docs)} relevant docs")
                    else:
                        logger.info(f"  ⚠️ {collection_name}: no relevant docs")
                except Exception as e:
                    logger.warning(f"  ❌ Error searching {collection_name}: {e}")

            if not all_docs:
                logger.error(f"❌ No relevant content found in any collection")
                return {"success": False, "error": "No relevant content found in any collection"}

            # Get top 5 most relevant docs from all collections combined
            # This ensures we have diverse context from multiple subjects if available
            retrieved_docs = all_docs[:5]

            logger.info(f"✅ Retrieved {len(retrieved_docs)} relevant docs from {len(docs_by_collection)} collections")

            # Build context with collection information for better understanding
            context_parts = []
            for doc in retrieved_docs:
                collection = doc.get("metadata", {}).get("collection", "unknown")
                content = doc["content"]
                context_parts.append(f"[{collection.upper()}] {content}")

            context = "\n\n".join(context_parts)

            # Enhanced prompt for multi-subject educational queries
            prompt = f"""You are an expert educational tutor for competitive exams (JEE, NEET, etc.).
Answer the following question comprehensively using the provided educational context.
If the question involves multiple subjects, provide answers for each subject mentioned.
Keep the answer clear, concise, and suitable for exam preparation.

Educational Context:
{context}

Question: {query}

Answer:"""

            response = ollama.chat(model=self.ollama_model, messages=[{"role": "user", "content": prompt}])

            sources_used = list(docs_by_collection.keys())

            return {
                "success": True,
                "response": response["message"]["content"],
                "model_used": self.ollama_model,
                "sources_used": sources_used,
                "docs_count": len(retrieved_docs)
            }

        except Exception as e:
            logger.error(f"Error generating chat response: {e}", exc_info=True)
            return {"success": False, "error": str(e)}


# Global service instance
_multimodal_service = None

def get_multimodal_rag_service(chromadb_path: str, ollama_model: str = "llava") -> MultimodalRAGService:
    """Get or create global multimodal RAG service"""
    global _multimodal_service
    if _multimodal_service is None:
        _multimodal_service = MultimodalRAGService(chromadb_path, ollama_model)
    return _multimodal_service

