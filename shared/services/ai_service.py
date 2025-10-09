"""
AI Service Module for Ollama Integration and Question Generation
Provides RAG functionality, PDF processing, and MCQ generation capabilities
"""

import os
import json
import re
from typing import List, Dict, Tuple, Optional
from datetime import datetime

# Try to import optional dependencies
try:
    from sentence_transformers import SentenceTransformer
    embedding_model = SentenceTransformer('all-MiniLM-L6-v2')  # Open-source model
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    print("Warning: sentence_transformers not available. Some features will be limited.")
    embedding_model = None
    SENTENCE_TRANSFORMERS_AVAILABLE = False

try:
    from PyPDF2 import PdfReader
    PYPDF2_AVAILABLE = True
except ImportError:
    print("Warning: PyPDF2 not available. PDF processing will not work.")
    PYPDF2_AVAILABLE = False

try:
    import ollama
    OLLAMA_AVAILABLE = True
except ImportError:
    print("Warning: ollama not available. MCQ generation will not work.")
    OLLAMA_AVAILABLE = False

try:
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError:
    print("Warning: numpy not available. Similarity search will not work.")
    NUMPY_AVAILABLE = False


class AIService:
    """Main AI service class for handling Ollama integration and question generation"""
    
    def __init__(self, pdf_folder_path: str = None, ollama_model: str = 'llama3.2:1b'):
        """
        Initialize AI Service
        
        Args:
            pdf_folder_path: Path to folder containing PDF documents
            ollama_model: Ollama model to use for generation
        """
        self.pdf_folder_path = pdf_folder_path or os.path.join(os.getcwd(), 'pdfs')
        self.ollama_model = ollama_model
        
        # Cache for embeddings and texts
        self.texts = []
        self.sources = []
        self.embeddings = None
        
        # Ensure PDF folder exists
        os.makedirs(self.pdf_folder_path, exist_ok=True)
    
    def check_dependencies(self) -> Dict[str, bool]:
        """Check availability of required dependencies"""
        return {
            'sentence_transformers': SENTENCE_TRANSFORMERS_AVAILABLE,
            'PyPDF2': PYPDF2_AVAILABLE,
            'ollama': OLLAMA_AVAILABLE,
            'numpy': NUMPY_AVAILABLE
        }
    
    def extract_text_from_pdf(self, pdf_path: str) -> str:
        """Extract text from a single PDF file"""
        if not PYPDF2_AVAILABLE:
            raise ImportError("PyPDF2 not available for PDF processing")
        
        try:
            reader = PdfReader(pdf_path)
            text = ''
            for page in reader.pages:
                text += page.extract_text() or ''
            return text
        except Exception as e:
            raise Exception(f"Error reading PDF {pdf_path}: {str(e)}")
    
    def extract_texts_from_pdfs(self, folder_path: str = None) -> List[Tuple[str, str]]:
        """Extract text from all PDFs in folder and subdirectories"""
        if not PYPDF2_AVAILABLE:
            return []
        
        folder_path = folder_path or self.pdf_folder_path
        
        if not os.path.exists(folder_path):
            os.makedirs(folder_path, exist_ok=True)
            return []
        
        all_text = []
        
        # Walk through all subdirectories
        for root, dirs, files in os.walk(folder_path):
            for filename in files:
                if filename.endswith('.pdf'):
                    pdf_path = os.path.join(root, filename)
                    try:
                        text = self.extract_text_from_pdf(pdf_path)
                        relative_path = os.path.relpath(pdf_path, folder_path)
                        all_text.append((text, relative_path))
                    except Exception as e:
                        print(f"Error processing PDF {filename}: {str(e)}")
                        continue
        
        return all_text
    
    def create_embeddings(self, text_data: List[Tuple[str, str]]) -> Tuple[Optional[any], List[str], List[str]]:
        """Create embeddings for text data"""
        texts = [item[0] for item in text_data]
        sources = [item[1] for item in text_data]
        
        if not SENTENCE_TRANSFORMERS_AVAILABLE or not embedding_model:
            return None, texts, sources
        
        try:
            text_embeddings = embedding_model.encode(texts, convert_to_tensor=False)
            return text_embeddings, texts, sources
        except Exception as e:
            print(f"Error creating embeddings: {str(e)}")
            return None, texts, sources
    
    def load_or_create_index(self) -> Tuple[Optional[any], List[str], List[str]]:
        """Load or create embeddings index from PDFs"""
        data = self.extract_texts_from_pdfs()
        if not data:
            return None, [], []
        
        embeddings, texts, sources = self.create_embeddings(data)
        
        # Cache the results
        self.embeddings = embeddings
        self.texts = texts
        self.sources = sources
        
        return embeddings, texts, sources
    
    def search_similar_content(self, query: str, top_k: int = 3) -> List[Dict]:
        """Search for similar content based on query using embeddings"""
        if not SENTENCE_TRANSFORMERS_AVAILABLE or not NUMPY_AVAILABLE or self.embeddings is None:
            return []
        
        try:
            # Encode the query
            query_embedding = embedding_model.encode([query], convert_to_tensor=False)
            
            # Calculate similarities (dot product)
            similarities = np.dot(self.embeddings, query_embedding.T).flatten()
            
            # Get top-k most similar documents
            top_indices = np.argsort(similarities)[-top_k:][::-1]
            
            results = []
            for idx in top_indices:
                if similarities[idx] > 0.1:  # Threshold for relevance
                    results.append({
                        'text': self.texts[idx][:1000],  # First 1000 chars
                        'source': self.sources[idx],
                        'similarity': float(similarities[idx])
                    })
            
            return results
        except Exception as e:
            print(f"Error in similarity search: {str(e)}")
            return []
    
    def generate_mcq_from_text(self, content: str, num_questions: int = 5, 
                              subject_name: str = None, difficulty: str = 'medium') -> Dict:
        """Generate MCQs from text content using Ollama"""
        if not OLLAMA_AVAILABLE:
            return {
                'success': False,
                'error': 'Ollama not available. Please install ollama package.',
                'questions': []
            }
        
        # Limit content length to avoid token limits
        max_content_length = 8000
        if len(content) > max_content_length:
            content = content[:max_content_length] + "..."
        
        subject_context = f" for {subject_name}" if subject_name else ""
        
        prompt = f"""Based on the following educational content, generate {num_questions} comprehensive multiple-choice questions{subject_context}. 
        
Make the questions {difficulty} difficulty level and ensure they test understanding of key concepts.

Content:
\"\"\"
{content}
\"\"\"

Format each question EXACTLY as follows (include the JSON structure):
{{
  "questions": [
    {{
      "question": "Question text here",
      "option_a": "First option",
      "option_b": "Second option", 
      "option_c": "Third option",
      "option_d": "Fourth option",
      "correct_option": "A",
      "explanation": "Explanation of why this is correct"
    }}
  ]
}}

Generate exactly {num_questions} questions in valid JSON format."""
        
        try:
            response = ollama.chat(
                model=self.ollama_model, 
                messages=[{'role': 'user', 'content': prompt}]
            )
            
            # Try to parse JSON from response
            response_text = response['message']['content']
            questions = self._parse_mcq_response(response_text)
            
            return {
                'success': True,
                'questions': questions,
                'raw_response': response_text,
                'model_used': self.ollama_model
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f"Error generating MCQ with Ollama: {str(e)}",
                'questions': []
            }
    
    def _parse_mcq_response(self, response_text: str) -> List[Dict]:
        """Parse MCQ response from Ollama and extract structured questions"""
        questions = []
        
        try:
            # Try to find JSON in the response
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                json_data = json.loads(json_match.group())
                if 'questions' in json_data:
                    return json_data['questions']
        except:
            pass
        
        # Fallback: Parse text format
        question_blocks = re.split(r'Question \d+:', response_text)[1:]
        
        for block in question_blocks:
            try:
                question_data = self._parse_question_block(block)
                if question_data:
                    questions.append(question_data)
            except Exception as e:
                print(f"Error parsing question block: {str(e)}")
                continue
        
        return questions
    
    def _parse_question_block(self, block: str) -> Optional[Dict]:
        """Parse individual question block from text"""
        lines = [line.strip() for line in block.strip().split('\n') if line.strip()]
        
        if not lines:
            return None
        
        question_text = lines[0]
        options = {}
        correct_option = None
        explanation = ""
        
        for line in lines[1:]:
            if line.startswith('A)') or line.startswith('A.'):
                options['option_a'] = line[2:].strip()
            elif line.startswith('B)') or line.startswith('B.'):
                options['option_b'] = line[2:].strip()
            elif line.startswith('C)') or line.startswith('C.'):
                options['option_c'] = line[2:].strip()
            elif line.startswith('D)') or line.startswith('D.'):
                options['option_d'] = line[2:].strip()
            elif 'correct answer' in line.lower():
                correct_match = re.search(r'[ABCD]', line)
                if correct_match:
                    correct_option = correct_match.group()
            elif 'explanation' in line.lower():
                explanation = line.split(':', 1)[-1].strip()
        
        if len(options) == 4 and correct_option:
            return {
                'question': question_text,
                'option_a': options.get('option_a', ''),
                'option_b': options.get('option_b', ''),
                'option_c': options.get('option_c', ''),
                'option_d': options.get('option_d', ''),
                'correct_option': correct_option,
                'explanation': explanation
            }
        
        return None

    def generate_mcq_from_pdfs(self, num_questions: int = 5, subject_name: str = None,
                              difficulty: str = 'medium', max_content_length: int = 8000) -> Dict:
        """Generate MCQs from combined PDF content"""
        # Load or refresh index
        embeddings, texts, sources = self.load_or_create_index()

        if not texts:
            return {
                'success': False,
                'error': 'No PDF files found in the pdfs directory',
                'questions': [],
                'pdf_folder': self.pdf_folder_path
            }

        # Combine content from multiple PDFs
        combined_content = ""
        used_sources = []

        for i, (text, source) in enumerate(zip(texts, sources)):
            if len(combined_content) + len(text[:1000]) < max_content_length:
                combined_content += f"\n--- From {source} ---\n{text[:1000]}\n"
                used_sources.append(source)
            else:
                break

        # Generate questions from combined content
        result = self.generate_mcq_from_text(
            combined_content,
            num_questions=num_questions,
            subject_name=subject_name,
            difficulty=difficulty
        )

        # Add PDF-specific information
        if result['success']:
            result.update({
                'sources_used': used_sources,
                'total_pdfs_processed': len(texts),
                'total_sources_used_for_mcq': len(used_sources)
            })

        return result

    def generate_rag_response(self, query: str, context_docs: List[Dict] = None) -> Dict:
        """Generate response using RAG with Ollama"""
        if not OLLAMA_AVAILABLE:
            return {
                'success': False,
                'error': 'RAG chat not available. Please install ollama package.',
                'response': ''
            }

        # If no context provided, search for relevant content
        if context_docs is None:
            context_docs = self.search_similar_content(query, top_k=3)

        if not context_docs:
            return {
                'success': True,
                'response': "I couldn't find relevant information in the available documents to answer your question.",
                'sources': [],
                'relevant_docs': 0
            }

        # Prepare context from retrieved documents
        context = "\n\n".join([f"From {doc['source']}:\n{doc['text']}" for doc in context_docs])

        prompt = f"""Based on the following context from educational documents, answer the user's question.
If the answer is not in the context, say so clearly. Provide a helpful and educational response.

Context:
{context}

Question: {query}

Answer:"""

        try:
            response = ollama.chat(
                model=self.ollama_model,
                messages=[{'role': 'user', 'content': prompt}]
            )

            return {
                'success': True,
                'response': response['message']['content'],
                'sources': [doc['source'] for doc in context_docs],
                'relevant_docs': len(context_docs),
                'model_used': self.ollama_model
            }

        except Exception as e:
            return {
                'success': False,
                'error': f"Error generating response: {str(e)}",
                'response': ''
            }

    def get_status(self) -> Dict:
        """Get AI service status and information"""
        return {
            'status': 'running',
            'dependencies': self.check_dependencies(),
            'pdf_folder': self.pdf_folder_path,
            'pdfs_loaded': len(self.texts),
            'sources': self.sources,
            'ollama_model': self.ollama_model,
            'embeddings_available': self.embeddings is not None
        }

    def reload_index(self) -> Dict:
        """Reload the RAG index from PDFs"""
        try:
            embeddings, texts, sources = self.load_or_create_index()

            return {
                'success': True,
                'message': 'RAG index reloaded successfully',
                'pdfs_loaded': len(texts),
                'sources': sources
            }

        except Exception as e:
            return {
                'success': False,
                'error': f'Error reloading RAG index: {str(e)}'
            }


# Global AI service instance
ai_service = None

def get_ai_service(pdf_folder_path: str = None, ollama_model: str = 'llama3.2:1b') -> AIService:
    """Get or create global AI service instance"""
    global ai_service
    if ai_service is None:
        ai_service = AIService(pdf_folder_path, ollama_model)
    return ai_service
