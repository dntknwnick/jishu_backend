"""
Layer 3: RAG Query API Service
Lightweight API service that fetches pre-indexed relevant PDF chunks for requests.
Passes context plus user prompt to the Ollama model (already running).
Returns MCQ/question/chatbot responses instantly — no blocking or re-embedding.
"""

import json
import time
import logging
from typing import List, Dict, Optional
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    import ollama
    OLLAMA_AVAILABLE = True
except ImportError:
    OLLAMA_AVAILABLE = False
    logger.warning("Ollama not available. LLM generation will not work.")

from .model_service import get_model_service


class RAGQueryService:
    """
    Lightweight RAG query service for instant MCQ generation and chatbot responses.
    Uses pre-initialized models and pre-indexed vector stores.
    """

    def __init__(self,
                 ollama_model: str = "llama3.2:1b",
                 top_k_results: int = 5,
                 similarity_threshold: float = 0.5):
        """
        Initialize RAG Query Service

        Args:
            ollama_model: Ollama model name for generation
            top_k_results: Number of top similar chunks to retrieve
            similarity_threshold: Minimum similarity threshold for results
        """
        self.ollama_model = ollama_model
        self.top_k_results = top_k_results
        self.similarity_threshold = similarity_threshold

        # Get pre-initialized model service
        self.model_service = get_model_service()

        # Subject mapping
        self.subjects = ['physics', 'chemistry', 'biology', 'mathematics', 'computer_science']

        # Response cache for repeated queries
        self.response_cache = {}
        self.cache_max_size = 100

    def _get_cache_key(self, query_type: str, **kwargs) -> str:
        """Generate cache key for query"""
        key_data = {'type': query_type, **kwargs}
        return str(hash(json.dumps(key_data, sort_keys=True)))

    def _get_from_cache(self, cache_key: str) -> Optional[Dict]:
        """Get response from cache if available"""
        if cache_key in self.response_cache:
            cached_response = self.response_cache[cache_key]
            # Check if cache entry is still fresh (within 1 hour)
            if time.time() - cached_response['cached_at'] < 3600:
                logger.info("📋 Returning cached response")
                return cached_response['response']
        return None

    def _save_to_cache(self, cache_key: str, response: Dict):
        """Save response to cache"""
        if len(self.response_cache) >= self.cache_max_size:
            # Remove oldest entry
            oldest_key = min(self.response_cache.keys(),
                           key=lambda k: self.response_cache[k]['cached_at'])
            del self.response_cache[oldest_key]

        self.response_cache[cache_key] = {
            'response': response,
            'cached_at': time.time()
        }

    def search_similar_content(self, query: str, subject: str = None, top_k: int = None) -> List[Dict]:
        """
        Search for similar content in pre-indexed vector stores.
        Fast retrieval using pre-computed embeddings.
        """
        if top_k is None:
            top_k = self.top_k_results

        # Get pre-initialized components
        chroma_client = self.model_service.get_chroma_client()
        embedding_model = self.model_service.get_embedding_model()

        if not chroma_client or not embedding_model:
            logger.error("❌ Required models not initialized")
            return []

        try:
            # Generate query embedding
            query_embedding = embedding_model.encode([query])[0].tolist()

            # Determine which collections to search
            collections_to_search = []
            if subject and subject in self.subjects:
                collection_name = f"subject_{subject}"
                try:
                    collection = chroma_client.get_collection(collection_name)
                    collections_to_search.append((subject, collection))
                except Exception:
                    logger.warning(f"Collection not found for subject: {subject}")
            else:
                # Search all available collections
                for subj in self.subjects:
                    collection_name = f"subject_{subj}"
                    try:
                        collection = chroma_client.get_collection(collection_name)
                        collections_to_search.append((subj, collection))
                    except Exception:
                        continue

            if not collections_to_search:
                logger.warning("No collections available for search")
                return []

            # Search collections and aggregate results
            all_results = []
            for subj, collection in collections_to_search:
                try:
                    results = collection.query(
                        query_embeddings=[query_embedding],
                        n_results=min(top_k, 10),  # Limit per collection
                        include=['documents', 'metadatas', 'distances']
                    )

                    # Process results
                    for i, (doc, metadata, distance) in enumerate(zip(
                        results['documents'][0],
                        results['metadatas'][0],
                        results['distances'][0]
                    )):
                        if distance <= (1 - self.similarity_threshold):  # Convert to similarity
                            all_results.append({
                                'content': doc,
                                'metadata': metadata,
                                'similarity': 1 - distance,
                                'subject': subj
                            })

                except Exception as e:
                    logger.error(f"Error searching collection {subj}: {str(e)}")

            # Sort by similarity and return top results
            all_results.sort(key=lambda x: x['similarity'], reverse=True)
            return all_results[:top_k]

        except Exception as e:
            logger.error(f"❌ Error in similarity search: {str(e)}")
            return []

    def generate_mcq_questions(self, subject: str, num_questions: int = 5, difficulty: str = "hard") -> Dict:
        """
        Generate MCQ questions using pre-indexed content.
        Fast generation with no re-embedding or model initialization.
        """
        if not OLLAMA_AVAILABLE:
            return {
                'success': False,
                'error': 'Ollama not available. Please install ollama package.',
                'questions': []
            }

        # Check cache first
        cache_key = self._get_cache_key('mcq', subject=subject, num_questions=num_questions, difficulty=difficulty)
        cached_response = self._get_from_cache(cache_key)
        if cached_response:
            return cached_response

        try:
            start_time = time.time()

            # Search for relevant content using pre-indexed vectors
            # Use simple subject name for better matching with indexed content
            search_query = subject
            relevant_docs = self.search_similar_content(search_query, subject, top_k=5)

            if not relevant_docs:
                return {
                    'success': False,
                    'error': f'No relevant content found for subject: {subject}. Vector search returned no results.',
                    'questions': []
                }

            # Prepare context from relevant documents
            context = "\n\n".join([
                f"From {doc['metadata']['source_file']}:\n{doc['content'][:800]}"
                for doc in relevant_docs
            ])

            prompt = f"""
Read the following educational content about {subject}.
Generate exactly {num_questions} high-quality MCQ (multiple choice) questions in JSON array format.
Each MCQ must be an object with exactly these keys:
- "question": (the text of the MCQ)
- "option_a": (string, first answer)
- "option_b": (string, second answer)
- "option_c": (string, third answer)
- "option_d": (string, fourth answer)
- "correct_answer": (must be the EXACT text of one of the provided options, never repeat the question)

Instructions:
- You must generate EXACTLY {num_questions} MCQs.
- Output must strictly be a JSON array of {num_questions} objects.
- Never output more than the requested number.
- Format exactly:

Rules:
- Never use the question text as an answer or correct_answer.
- correct_answer must match one of the 4 options exactly (a case-sensitive string match).
- The correct output is a single valid JSON array, e.g.:
[
  {{
    "question": "What is force?",
    "option_a": "Energy",
    "option_b": "Push or pull",
    "option_c": "Speed",
    "option_d": "Mass",
    "correct_answer": "Push or pull"
  }},
  ...
]
- Absolutely NO explanations, comments, or text outside the JSON array.
- Output must start with [ and end with ].
- All object keys should be lowercase as shown.
- The JSON **must** be parseable by Python's json.loads() with no changes.

Context:
{context}
"""



            # Generate with Ollama using pre-initialized client
            ollama_client = self.model_service.get_ollama_client()
            if not ollama_client:
                return {
                    'success': False,
                    'error': 'Ollama client not initialized',
                    'questions': []
                }

            logger.info(f"🤖 Generating {num_questions} MCQ questions for {subject}")

            # Calculate appropriate token limit based on number of questions
            # Each MCQ needs ~150 tokens (question + 4 options + JSON formatting, no explanation)
            # Add extra buffer for JSON structure and safety margin
            estimated_tokens = max(num_questions * 150 + 500, 3000)
            max_tokens = min(estimated_tokens, 20000)  # Cap at 20000 tokens for large batches

            logger.info(f"🔧 Token calculation: {num_questions} questions × 150 + 500 = {estimated_tokens}, using {max_tokens}")

            response = ollama_client.generate(
                model=self.ollama_model,
                prompt=prompt,
                options={
                    'temperature': 0.7,
                    'top_p': 0.9,
                    'num_predict': max_tokens,
                    'top_k': 40,
                    'repeat_penalty': 1.1
                }
            )

            ai_response = response['response'].strip()
            generation_time = time.time() - start_time

            # Debug logging
            logger.info(f"🔍 AI Response length: {len(ai_response)} characters")
            logger.info(f"🔍 AI Response: {ai_response}")

            # Parse JSON response
            try:
                # Try to extract JSON - handle both array format and object format
                questions = None

                # First try: Look for direct JSON array [...]
                json_start = ai_response.find('[')
                json_end = ai_response.rfind(']') + 1

                if json_start != -1 and json_end > 0:
                    json_str = ai_response[json_start:json_end]
                    logger.info(f"🔍 Extracted JSON string length: {len(json_str)}")
                    logger.info(f"🔍 JSON string starts with: {json_str[:100]}")
                    logger.info(f"🔍 JSON string ends with: {json_str[-100:]}")

                    # Clean up the JSON string
                    json_str = json_str.strip()

                    try:
                        questions = json.loads(json_str)
                        logger.info(f"✅ Successfully parsed {len(questions)} questions from JSON array")
                    except json.JSONDecodeError as e:
                        logger.error(f"❌ JSON decode error: {str(e)}")
                        logger.error(f"❌ Error at position: {e.pos if hasattr(e, 'pos') else 'unknown'}")

                        # Try to fix common JSON issues
                        try:
                            # Remove any trailing commas before closing brackets
                            cleaned_json = json_str.replace(',]', ']').replace(',}', '}')
                            questions = json.loads(cleaned_json)
                            logger.info(f"✅ Successfully parsed after cleanup: {len(questions)} questions")
                        except json.JSONDecodeError:
                            pass

                # Second try: Look for JSON object with "questions" key
                if questions is None:
                    obj_start = ai_response.find('{')
                    obj_end = ai_response.rfind('}') + 1

                    if obj_start != -1 and obj_end > 0:
                        json_str = ai_response[obj_start:obj_end]
                        try:
                            parsed_obj = json.loads(json_str)
                            if isinstance(parsed_obj, dict) and 'questions' in parsed_obj:
                                questions = parsed_obj['questions']
                        except json.JSONDecodeError:
                            pass

                # Third try: Look for single question object and wrap in array
                if questions is None:
                    # Try to find a single question object
                    obj_start = ai_response.find('{')
                    obj_end = ai_response.rfind('}') + 1

                    if obj_start != -1 and obj_end > 0:
                        json_str = ai_response[obj_start:obj_end]
                        try:
                            parsed_obj = json.loads(json_str)
                            if isinstance(parsed_obj, dict) and 'question' in parsed_obj:
                                # Single question object - wrap in array
                                questions = [parsed_obj]
                                logger.warning("Found single question object, wrapped in array")
                        except json.JSONDecodeError:
                            pass

                if questions is None:
                    logger.error(f"Failed to parse JSON. Response length: {len(ai_response)}")
                    logger.error(f"Response preview: {ai_response[:500]}")
                    logger.error(f"Response ending: ...{ai_response[-200:]}")

                    # Check if response seems truncated
                    if not ai_response.strip().endswith((']', '}')) and len(ai_response) > 1000:
                        raise ValueError("AI response appears to be truncated - increase token limit")
                    else:
                        raise ValueError("No valid JSON found in response")

                if not isinstance(questions, list):
                    raise ValueError("Questions data is not a list")

                # Parser-side Safeguard: Filter or correct invalid correct_answer
                validated_questions = []
                for i, q in enumerate(questions):
                    # Check if all required fields are present
                    if all(key in q for key in ['question', 'option_a', 'option_b', 'option_c', 'option_d', 'correct_answer']):
                        # Extract and validate correct_answer against options
                        correct = q.get("correct_answer", "").strip()
                        options = [q.get("option_a", "").strip(), q.get("option_b", "").strip(),
                                 q.get("option_c", "").strip(), q.get("option_d", "").strip()]

                        logger.info(f"🔍 Validating question {i+1}:")
                        logger.info(f"  Correct answer: '{correct}'")
                        logger.info(f"  Options: {options}")
                        logger.info(f"  Match found: {correct in options}")

                        # Ensure correct_answer matches one of the options exactly
                        if correct and correct in options:
                            validated_questions.append(q)
                            logger.info(f"✅ Question {i+1} validated successfully")
                        else:
                            logger.error(f"❌ Discarded invalid MCQ: correct_answer '{correct}' does not match any option")
                            logger.error(f"   Available options: {options}")
                    else:
                        missing_keys = [key for key in ['question', 'option_a', 'option_b', 'option_c', 'option_d', 'correct_answer'] if key not in q]
                        logger.error(f"❌ Discarded MCQ with missing keys: {missing_keys}")

                if not validated_questions:
                    raise ValueError("No valid questions found in response")

                # Get sources used
                sources_used = [doc['metadata']['source_file'] for doc in relevant_docs]

                result = {
                    'success': True,
                    'questions': validated_questions,
                    'total_generated': len(validated_questions),
                    'subject': subject,
                    'difficulty': difficulty,
                    'generation_time': generation_time,
                    'sources_used': sources_used,
                    'model_used': self.ollama_model,
                    'method': 'rag_optimized'
                }

                # Cache the result
                self._save_to_cache(cache_key, result)

                logger.info(f"✅ Generated {len(validated_questions)} MCQ questions for {subject} in {generation_time:.2f}s")
                return result

            except (json.JSONDecodeError, ValueError) as e:
                logger.error(f"❌ Failed to parse MCQ response: {str(e)}")
                return {
                    'success': False,
                    'error': f'Failed to parse AI response: {str(e)}',
                    'questions': [],
                    'raw_response': ai_response[:500]
                }

        except Exception as e:
            logger.error(f"❌ Error generating MCQ questions: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'questions': []
            }

    def generate_chat_response(self, query: str, subject: str = None, session_id: str = None) -> Dict:
        """
        Generate chatbot response using pre-indexed content.
        Fast response with no re-embedding or model initialization.
        """
        if not OLLAMA_AVAILABLE:
            return {
                'success': False,
                'error': 'Ollama not available. Please install ollama package.',
                'response': ''
            }

        # Check cache first
        cache_key = self._get_cache_key('chat', query=query, subject=subject)
        cached_response = self._get_from_cache(cache_key)
        if cached_response:
            return cached_response

        try:
            start_time = time.time()

            # Search for relevant content using pre-indexed vectors (reduced for speed)
            relevant_docs = self.search_similar_content(query, subject, top_k=2)

            if not relevant_docs:
                # Quick fallback for common educational topics
                quick_responses = {
                    'chemical bonding': 'Chemical bonding is the attraction between atoms that allows the formation of chemical compounds. Main types include ionic, covalent, and metallic bonds.',
                    'quadratic equation': 'A quadratic equation has the form ax² + bx + c = 0. Solve using the quadratic formula: x = (-b ± √(b²-4ac)) / 2a',
                    'photosynthesis': 'Photosynthesis is the process by which plants convert light energy into chemical energy using chlorophyll, producing glucose and oxygen.',
                    'newton': 'Newton\'s laws describe motion: 1) Objects at rest stay at rest, 2) F=ma, 3) Every action has an equal and opposite reaction.',
                    'physics': 'Physics is the study of matter, energy, and their interactions in the universe.',
                    'chemistry': 'Chemistry is the study of matter, its properties, composition, and the changes it undergoes.',
                    'mathematics': 'Mathematics is the study of numbers, quantities, shapes, and patterns using logical reasoning.'
                }

                # Check for quick response
                query_lower = query.lower()
                for key, quick_answer in quick_responses.items():
                    if key in query_lower:
                        return {
                            'success': True,
                            'response': quick_answer,
                            'response_time': time.time() - start_time,
                            'sources': [],
                            'relevant_docs': 0,
                            'model_used': 'quick_response',
                            'session_id': session_id or f"session_{int(time.time())}",
                            'method': 'quick_fallback'
                        }

                # Fallback response without context (shorter for speed)
                prompt = f"""Answer briefly: {query}

Provide a concise educational response."""
            else:
                # Create context from relevant documents (reduced size for faster processing)
                context = "\n\n".join([
                    f"{doc['content'][:200]}"  # Even shorter context
                    for doc in relevant_docs[:2]  # Use only top 2 documents for speed
                ])

                prompt = f"""Context: {context}

Question: {query}

Answer briefly based on the context:"""

            # Generate response with Ollama using pre-initialized client
            ollama_client = self.model_service.get_ollama_client()
            if not ollama_client:
                return {
                    'success': False,
                    'error': 'Ollama client not initialized',
                    'response': ''
                }

            logger.info(f"🤖 Generating chat response for query: {query[:50]}...")

            # Use highly optimized options for fastest response
            response = ollama_client.chat(
                model=self.ollama_model,
                messages=[{'role': 'user', 'content': prompt}],
                options={
                    'num_predict': 100,  # Very short responses for speed
                    'temperature': 0.3,  # Lower temperature for faster, more deterministic responses
                    'top_p': 0.8,       # More focused token selection
                    'top_k': 20,        # Fewer token choices for speed
                    'repeat_penalty': 1.0,  # Minimal penalty for speed
                    'num_ctx': 1024,    # Smaller context window
                    'num_thread': 4,    # Use multiple threads
                    'num_gpu': 0        # Force CPU for consistency
                }
            )

            ai_response = response['message']['content']
            response_time = time.time() - start_time

            # Get sources used
            sources_used = [doc['metadata']['source_file'] for doc in relevant_docs] if relevant_docs else []

            result = {
                'success': True,
                'response': ai_response,
                'response_time': response_time,
                'sources': sources_used,
                'relevant_docs': len(relevant_docs),
                'model_used': self.ollama_model,
                'session_id': session_id or f"session_{int(time.time())}",
                'method': 'rag_optimized'
            }

            # Cache the result
            self._save_to_cache(cache_key, result)

            logger.info(f"✅ Generated chat response in {response_time:.2f}s")
            return result

        except Exception as e:
            logger.error(f"❌ Error generating chat response: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'response': ''
            }

    def get_status(self) -> Dict:
        """Get comprehensive status of the RAG query service"""
        chroma_client = self.model_service.get_chroma_client()

        status = {
            'service_name': 'RAGQueryService',
            'configuration': {
                'ollama_model': self.ollama_model,
                'top_k_results': self.top_k_results,
                'similarity_threshold': self.similarity_threshold
            },
            'cache_info': {
                'cache_size': len(self.response_cache),
                'cache_max_size': self.cache_max_size
            },
            'collections': {},
            'dependencies': {
                'model_service': self.model_service.get_status(),
                'ollama': OLLAMA_AVAILABLE
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

    def clear_cache(self):
        """Clear the response cache"""
        self.response_cache.clear()
        logger.info("🧹 Response cache cleared")






# Global RAG service instance
_rag_query_service = None

def get_rag_service(ollama_model: str = "llama3.2:1b",
                   top_k_results: int = 5,
                   similarity_threshold: float = 0.01) -> RAGQueryService:
    """Get or create global RAG query service instance"""
    global _rag_query_service

    if _rag_query_service is None:
        _rag_query_service = RAGQueryService(
            ollama_model=ollama_model,
            top_k_results=top_k_results,
            similarity_threshold=similarity_threshold
        )

    return _rag_query_service
