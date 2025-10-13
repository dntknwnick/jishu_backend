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

# Check PyPDF2 availability with version compatibility
PYPDF2_AVAILABLE = False
try:
    # Try PyPDF2 v3+ first
    from PyPDF2 import PdfReader
    PYPDF2_AVAILABLE = True
    print("✅ PyPDF2 v3+ available")
except ImportError:
    try:
        # Try PyPDF2 v2
        from PyPDF2 import PdfFileReader
        PYPDF2_AVAILABLE = True
        print("✅ PyPDF2 v2 available")
    except ImportError:
        try:
            # Try basic PyPDF2 import
            import PyPDF2
            PYPDF2_AVAILABLE = True
            print("✅ PyPDF2 basic import available")
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
        # Fix PDF path to use absolute path
        if pdf_folder_path:
            self.pdf_folder_path = pdf_folder_path
        else:
            # Use absolute path to ensure we find the PDFs
            current_dir = os.path.dirname(os.path.abspath(__file__))
            # Go up to the project root (from shared/services to project root)
            project_root = os.path.dirname(os.path.dirname(current_dir))
            self.pdf_folder_path = os.path.join(project_root, 'pdfs')
            print(f"🔧 AI Service using PDF path: {self.pdf_folder_path}")
            import sys
            sys.stdout.flush()
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
        """DEPRECATED: Text-based MCQ generation is no longer supported. Use PDF-based generation only."""
        return {
            'success': False,
            'error': 'Text-based MCQ generation is not supported. MCQs can only be generated from PDF textbooks.',
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

    def _parse_simple_mcq_response(self, response_text: str, num_questions: int) -> List[Dict]:
        """Parse ultra-fast compact format MCQ response"""
        questions = []
        lines = response_text.split('\n')

        current_question = {}

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # Look for question pattern (Q1:, Q2:, Question 1:, etc.)
            if (line.startswith('Q') and ':' in line) or (line.startswith('Question') and ':' in line):
                # Save previous question if exists
                if current_question and 'question' in current_question:
                    questions.append(current_question)
                    if len(questions) >= num_questions:
                        break

                current_question = {
                    'question': line.split(':', 1)[1].strip(),
                    'option_a': '',
                    'option_b': '',
                    'option_c': '',
                    'option_d': '',
                    'correct_option': '',
                    'explanation': ''
                }

            # Look for individual options on separate lines
            elif line.startswith('A)'):
                current_question['option_a'] = line[2:].strip()
            elif line.startswith('B)'):
                current_question['option_b'] = line[2:].strip()
            elif line.startswith('C)'):
                current_question['option_c'] = line[2:].strip()
            elif line.startswith('D)'):
                current_question['option_d'] = line[2:].strip()

            # Also handle compact format: A) option B) option C) option D) option
            elif 'A)' in line and 'B)' in line and 'C)' in line and 'D)' in line:
                parts = line.split('A)')[1].split('B)')
                if len(parts) >= 2:
                    current_question['option_a'] = parts[0].strip()

                    parts2 = parts[1].split('C)')
                    if len(parts2) >= 2:
                        current_question['option_b'] = parts2[0].strip()

                        parts3 = parts2[1].split('D)')
                        if len(parts3) >= 2:
                            current_question['option_c'] = parts3[0].strip()
                            current_question['option_d'] = parts3[1].strip()

            # Look for answer (Demo-style format)
            elif line.startswith('Answer:') or line.startswith('Correct Answer:'):
                answer_part = line.split(':', 1)[1].strip()
                # Handle formats like "A", "A)", "A) Chemistry"
                if answer_part.startswith('A'):
                    current_question['correct_option'] = 'A'
                elif answer_part.startswith('B'):
                    current_question['correct_option'] = 'B'
                elif answer_part.startswith('C'):
                    current_question['correct_option'] = 'C'
                elif answer_part.startswith('D'):
                    current_question['correct_option'] = 'D'

        # Add the last question
        if current_question and 'question' in current_question and current_question['question']:
            questions.append(current_question)

        return questions[:num_questions]  # Ensure we don't exceed requested count

    def generate_mcq_from_pdfs(self, num_questions: int = 5, subject_name: str = None,
                              difficulty: str = 'hard', max_content_length: int = 8000,
                              exam_type: str = None, subject_directories: List[str] = None) -> Dict:
        """Generate MCQs from combined PDF content with exam-specific subject filtering. Always uses hard difficulty."""
        print(f"🚀 generate_mcq_from_pdfs called with:")
        print(f"   📊 num_questions={num_questions}")
        print(f"   📚 subject_name={subject_name}")
        print(f"   🎯 exam_type={exam_type}")
        print(f"   📁 subject_directories={subject_directories}")
        import sys
        sys.stdout.flush()

        # Force hard difficulty for real exam challenge
        difficulty = 'hard'

        # Determine which subject directories to use based on exam type
        if subject_directories is None:
            subject_directories = self._get_subject_directories_for_exam(exam_type, subject_name)

        print(f"🔍 Subject directories determined: {subject_directories}")
        sys.stdout.flush()

        # Load content from specific subject directories
        embeddings, texts, sources = self._load_subject_specific_content(subject_directories)

        if not texts:
            # No PDF content available - return error since we only support PDF-based generation
            print(f"❌ No PDF files found for subjects: {subject_directories}")
            return {
                'success': False,
                'error': f'No PDF textbooks found for subjects: {", ".join(subject_directories)}. MCQ generation requires PDF textbooks.',
                'questions': [],
                'sources_used': [],
                'total_pdfs_processed': 0
            }

        # Combine content from multiple PDFs (ultra-optimized for 6-8 second generation)
        combined_content = ""
        used_sources = []
        max_content_length = 1500  # Ultra-reduced for 6-8 sec target
        max_sources = 4  # Further limit sources for speed

        for i, (text, source) in enumerate(zip(texts, sources)):
            if i >= max_sources:  # Stop after max sources for speed
                break

            # Use very small chunks (300 chars) for maximum speed
            chunk_size = 300
            if len(combined_content) + len(text[:chunk_size]) < max_content_length:
                combined_content += f"\n--- From {source} ---\n{text[:chunk_size]}\n"
                if source not in used_sources:  # Avoid duplicate sources
                    used_sources.append(source)
            else:
                break

        # Generate questions directly from PDF content using Ollama
        if not OLLAMA_AVAILABLE:
            return {
                'success': False,
                'error': 'Ollama not available. Please install ollama package.',
                'questions': [],
                'sources_used': used_sources,
                'total_pdfs_processed': len(texts)
            }

        # Determine if this is a single subject or multi-subject test
        is_multi_subject = len(subject_directories) > 1

        if subject_name:
            subject_context = f" for {subject_name}"
        elif is_multi_subject:
            subject_context = f" covering {', '.join(subject_directories)} subjects"
        else:
            subject_context = ""

        # Enhanced prompt for better question distribution
        if is_multi_subject:
            distribution_instruction = f"""
IMPORTANT: Distribute the {num_questions} questions evenly across all subjects mentioned in the content.
Ensure each subject ({', '.join(subject_directories)}) is represented proportionally in the question set.
"""
        else:
            distribution_instruction = ""

        # Debug: Show content length and details
        print(f"🔍 Combined content length: {len(combined_content)} characters")
        print(f"🔍 Used sources: {used_sources}")
        print(f"🔍 First 200 chars of content: {combined_content[:200]}...")

        if len(combined_content) < 100:
            print(f"⚠️  WARNING: Very short content ({len(combined_content)} chars), this may cause poor question generation")

        # Simple Demo-style prompt for maximum speed (3-6 seconds like Demo)
        prompt = f"""Based on the following content from educational documents, generate {num_questions} multiple-choice questions with 4 options each. Mark the correct answer clearly.

Content:
{combined_content}

Format each question as:
Question 1: [Question text]
A) [Option A]
B) [Option B]
C) [Option C]
D) [Option D]
Correct Answer: [Letter]

Question 2: [Question text]
A) [Option A]
B) [Option B]
C) [Option C]
D) [Option D]
Correct Answer: [Letter]

Generate exactly {num_questions} questions."""

        try:
            # Simple Demo-style model call for maximum speed (3-6 seconds like Demo)
            response = ollama.chat(
                model='llama3.2:1b',
                messages=[{'role': 'user', 'content': prompt}]
            )

            # Parse the simpler text format instead of JSON
            response_text = response['message']['content']
            print(f"🤖 AI Response length: {len(response_text)} characters")
            print(f"🤖 AI Response preview: {response_text[:300]}...")

            questions = self._parse_simple_mcq_response(response_text, num_questions)
            print(f"📝 Parsed {len(questions)} questions from AI response")

            # Convert to format expected by the endpoint
            formatted_questions = []
            for q in questions:
                formatted_q = {
                    'question': q.get('question', ''),
                    'options': {
                        'A': q.get('option_a', ''),
                        'B': q.get('option_b', ''),
                        'C': q.get('option_c', ''),
                        'D': q.get('option_d', '')
                    },
                    'correct_answer': q.get('correct_option', 'A'),
                    'explanation': q.get('explanation', ''),
                    # Keep original format for backward compatibility
                    'option_a': q.get('option_a', ''),
                    'option_b': q.get('option_b', ''),
                    'option_c': q.get('option_c', ''),
                    'option_d': q.get('option_d', ''),
                    'correct_option': q.get('correct_option', 'A')
                }
                formatted_questions.append(formatted_q)

            return {
                'success': True,
                'questions': formatted_questions,
                'raw_response': response_text,
                'model_used': 'llama3.2:1b',
                'sources_used': used_sources,
                'total_pdfs_processed': len(texts),
                'total_sources_used_for_mcq': len(used_sources)
            }

        except Exception as e:
            return {
                'success': False,
                'error': f"Error generating MCQ with Ollama: {str(e)}",
                'questions': [],
                'sources_used': used_sources,
                'total_pdfs_processed': len(texts)
            }

    def _get_subject_directories_for_exam(self, exam_type: str = None, subject_name: str = None) -> List[str]:
        """Determine which subject directories to use based on exam type and subject"""

        # If specific subject is provided, try to map it
        if subject_name:
            subject_lower = subject_name.lower()
            if 'physics' in subject_lower:
                return ['physics']
            elif 'chemistry' in subject_lower:
                return ['chemistry']
            elif 'biology' in subject_lower or 'bio' in subject_lower:
                return ['biology']
            elif 'math' in subject_lower:
                return ['mathematics']
            elif 'computer' in subject_lower or 'cs' in subject_lower:
                return ['computer_science']

        # Exam-specific subject combinations
        if exam_type:
            exam_lower = exam_type.lower()
            if 'neet' in exam_lower:
                return ['biology', 'physics', 'chemistry']
            elif 'jee' in exam_lower or 'cet' in exam_lower or 'engineering' in exam_lower:
                return ['physics', 'chemistry', 'mathematics']
            elif 'medical' in exam_lower:
                return ['biology', 'physics', 'chemistry']

        # Default: use all available subjects
        return ['physics', 'chemistry', 'biology', 'mathematics']

    def _load_subject_specific_content(self, subject_directories: List[str]) -> tuple:
        """Load content from specific subject directories with optimized speed"""
        import os
        print(f"🚀 _load_subject_specific_content called with: {subject_directories}")
        import sys
        sys.stdout.flush()
        # Try to use langchain first, fallback to PyPDF2
        use_langchain = False
        try:
            from langchain_community.document_loaders import PyPDFLoader
            from langchain.text_splitter import RecursiveCharacterTextSplitter
            use_langchain = True
            print("✅ Using langchain document loaders")
        except ImportError:
            try:
                from langchain.document_loaders import PyPDFLoader
                from langchain.text_splitter import RecursiveCharacterTextSplitter
                use_langchain = True
                print("✅ Using langchain document loaders (legacy import)")
            except ImportError:
                print("⚠️  langchain not available. Using PyPDF2 fallback for speed.")
                use_langchain = False

        all_texts = []
        all_sources = []

        subjects_folder = os.path.join(self.pdf_folder_path, 'subjects')
        print(f"🔍 Looking for PDFs in subjects folder: {subjects_folder}")
        print(f"🔍 Current working directory: {os.getcwd()}")
        print(f"🔍 PDF folder path: {self.pdf_folder_path}")
        print(f"🔍 Subjects folder exists: {os.path.exists(subjects_folder)}")

        # Limit PDFs per subject for speed (max 2 PDFs per subject for 6-8 sec target)
        max_pdfs_per_subject = 2

        for subject_dir in subject_directories:
            subject_path = os.path.join(subjects_folder, subject_dir)
            print(f"🔍 Checking subject directory: {subject_path}")

            if not os.path.exists(subject_path):
                print(f"❌ Subject directory not found: {subject_path}")
                continue

            # Load limited PDFs from this subject directory for speed
            pdf_count = 0
            pdf_files = [f for f in os.listdir(subject_path) if f.lower().endswith('.pdf')]
            print(f"📚 Found {len(pdf_files)} PDF files in {subject_dir}")

            # Take only first few PDFs for speed
            for filename in pdf_files[:max_pdfs_per_subject]:
                file_path = os.path.join(subject_path, filename)
                try:
                    if use_langchain:
                        # Use langchain method
                        loader = PyPDFLoader(file_path)
                        documents = loader.load()

                        # Use smaller chunks for faster processing (optimized for 6-8 sec)
                        text_splitter = RecursiveCharacterTextSplitter(
                            chunk_size=400,  # Further reduced for speed
                            chunk_overlap=30  # Further reduced for speed
                        )

                        # Limit chunks per document for speed (only 1 chunk per doc for 6-8 sec target)
                        max_chunks_per_doc = 1
                        for doc in documents[:1]:  # Only first page per PDF for speed
                            chunks = text_splitter.split_text(doc.page_content)
                            for chunk in chunks[:max_chunks_per_doc]:
                                all_texts.append(chunk)
                                all_sources.append(f"{subject_dir}/{filename}")
                    else:
                        # Use PyPDF2 fallback (faster, simpler) - optimized for 6-8 sec
                        text_content = self._extract_text_with_pypdf2(file_path)
                        if text_content:
                            # Simple text chunking for speed (smaller chunks for 6-8 sec target)
                            chunk_size = 600  # Reduced from 1000
                            chunks = [text_content[i:i+chunk_size] for i in range(0, len(text_content), chunk_size)]
                            # Take only first chunk for speed (6-8 sec target)
                            for chunk in chunks[:1]:
                                if chunk.strip():
                                    all_texts.append(chunk.strip())
                                    all_sources.append(f"{subject_dir}/{filename}")

                    pdf_count += 1
                    print(f"✅ Loaded PDF: {subject_dir}/{filename}")

                except Exception as e:
                    print(f"❌ Error loading {file_path}: {str(e)}")
                    continue

            print(f"📚 Loaded {pdf_count} PDFs from {subject_dir}")

        print(f"📊 Total chunks loaded: {len(all_texts)} from {len(subject_directories)} subjects")

        # Skip embeddings for speed - not needed for direct generation
        return None, all_texts, all_sources

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

    def _extract_text_with_pypdf2(self, pdf_path: str) -> str:
        """Extract text from PDF using PyPDF2 (fallback method)"""
        try:
            # Try different PyPDF2 import methods for compatibility
            try:
                from PyPDF2 import PdfReader
                print("✅ Using PyPDF2 v3+ API")
            except ImportError:
                try:
                    from PyPDF2 import PdfFileReader as PdfReader
                    print("✅ Using PyPDF2 v2 API")
                except ImportError:
                    import PyPDF2
                    PdfReader = PyPDF2.PdfReader if hasattr(PyPDF2, 'PdfReader') else PyPDF2.PdfFileReader
                    print("✅ Using PyPDF2 fallback API")
        except ImportError:
            print("❌ PyPDF2 not available. Cannot extract PDF text.")
            return ""

        try:
            text_content = ""
            with open(pdf_path, 'rb') as file:
                pdf_reader = PdfReader(file)

                # Handle different PyPDF2 versions
                if hasattr(pdf_reader, 'pages'):
                    # PyPDF2 v3+
                    pages = pdf_reader.pages
                elif hasattr(pdf_reader, 'getNumPages'):
                    # PyPDF2 v2
                    pages = [pdf_reader.getPage(i) for i in range(pdf_reader.getNumPages())]
                else:
                    print("❌ Unknown PyPDF2 API version")
                    return ""

                # Only read first 2 pages for speed
                max_pages = min(2, len(pages))
                for page_num in range(max_pages):
                    page = pages[page_num]
                    if hasattr(page, 'extract_text'):
                        text_content += page.extract_text() + "\n"
                    elif hasattr(page, 'extractText'):
                        text_content += page.extractText() + "\n"
                    else:
                        print(f"❌ Cannot extract text from page {page_num}")

            print(f"✅ Extracted {len(text_content)} characters from {pdf_path}")
            return text_content.strip()
        except Exception as e:
            print(f"❌ Error extracting text from {pdf_path}: {e}")
            return ""


# Global AI service instance
ai_service = None

def get_ai_service(pdf_folder_path: str = None, ollama_model: str = 'llama3.2:1b') -> AIService:
    """Get or create global AI service instance"""
    global ai_service
    if ai_service is None:
        ai_service = AIService(pdf_folder_path, ollama_model)
    return ai_service
