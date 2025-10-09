import os
from flask import jsonify, request
from app.api import bp

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

# PDF folder path relative to backend directory
PDF_FOLDER = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'pdfs')

# Global variables for caching
texts = []
sources = []
embeddings = []

# Step 1: Extract Text from PDFs (including subdirectories)
def extract_texts_from_pdfs(folder_path):
    if not PYPDF2_AVAILABLE:
        print("Cannot extract text from PDFs: PyPDF2 not available")
        return []

    # Check if the folder exists
    if not os.path.exists(folder_path):
        print(f"Warning: PDF folder '{folder_path}' does not exist. Creating it.")
        os.makedirs(folder_path, exist_ok=True)
        return []

    all_text = []

    # Walk through all subdirectories
    for root, dirs, files in os.walk(folder_path):
        for filename in files:
            if filename.endswith('.pdf'):
                pdf_path = os.path.join(root, filename)
                try:
                    reader = PdfReader(pdf_path)
                    text = ''
                    for page in reader.pages:
                        text += page.extract_text() or ''

                    # Include subdirectory in source name for better identification
                    relative_path = os.path.relpath(pdf_path, folder_path)
                    all_text.append((text, relative_path))
                except Exception as e:
                    print(f"Error reading PDF {relative_path}: {str(e)}")
                    continue
    return all_text

# Step 2: Create embeddings for text data
def create_embeddings(text_data):
    texts = [item[0] for item in text_data]
    sources = [item[1] for item in text_data]

    if not SENTENCE_TRANSFORMERS_AVAILABLE:
        print("Cannot create embeddings: sentence_transformers not available")
        return None, texts, sources

    try:
        text_embeddings = embedding_model.encode(texts, convert_to_tensor=False)
        return text_embeddings, texts, sources
    except Exception as e:
        print(f"Error creating embeddings: {str(e)}")
        return None, texts, sources

# Step 3: Load or Create embeddings
def load_or_create_index():
    data = extract_texts_from_pdfs(PDF_FOLDER)
    if not data:
        return None, [], []
    text_embeddings, texts, sources = create_embeddings(data)
    return text_embeddings, texts, sources

# Step 4: Generate MCQ via Ollama from combined content
def generate_mcq_from_combined_content(all_texts, sources, max_content_length=8000):
    if not OLLAMA_AVAILABLE:
        print("Cannot generate MCQs: ollama not available")
        return "MCQ generation not available. Please install ollama package.", []

    # Combine content from multiple PDFs, keeping track of sources
    combined_content = ""
    used_sources = []

    for i, (text, source) in enumerate(zip(all_texts, sources)):
        if len(combined_content) + len(text[:1000]) < max_content_length:
            combined_content += f"\n--- From {source} ---\n{text[:1000]}\n"
            used_sources.append(source)
        else:
            break

    prompt = f"""Based on the following content from multiple educational documents, generate 5 comprehensive multiple-choice questions with 4 options each. Mark the correct answer clearly.

Make sure the questions cover different topics and difficulty levels from the provided content.

Content from multiple sources:
\"\"\"
{combined_content}
\"\"\"

Format each question as:
Question X: [Question text]
A) [Option A]
B) [Option B]
C) [Option C]
D) [Option D]
Correct Answer: [Letter]

Sources used: {', '.join(used_sources)}
"""
    try:
        response = ollama.chat(model='llama3.2:1b', messages=[{'role': 'user', 'content': prompt}])
        return response['message']['content'], used_sources
    except Exception as e:
        print(f"Error generating MCQ with Ollama: {str(e)}")
        return f"Error generating MCQ: {str(e)}", used_sources

# RAG Chat functionality
def search_similar_content(query, top_k=3):
    """Search for similar content based on query"""
    global texts, sources, embeddings
    
    if not SENTENCE_TRANSFORMERS_AVAILABLE or embeddings is None:
        return []
    
    try:
        # Encode the query
        query_embedding = embedding_model.encode([query], convert_to_tensor=False)
        
        # Calculate similarities (simple dot product)
        import numpy as np
        similarities = np.dot(embeddings, query_embedding.T).flatten()
        
        # Get top-k most similar documents
        top_indices = np.argsort(similarities)[-top_k:][::-1]
        
        results = []
        for idx in top_indices:
            if similarities[idx] > 0.1:  # Threshold for relevance
                results.append({
                    'text': texts[idx][:500],  # First 500 chars
                    'source': sources[idx],
                    'similarity': float(similarities[idx])
                })
        
        return results
    except Exception as e:
        print(f"Error in similarity search: {str(e)}")
        return []

def generate_rag_response(query, context_docs):
    """Generate response using RAG with Ollama"""
    if not OLLAMA_AVAILABLE:
        return "RAG chat not available. Please install ollama package."
    
    # Prepare context from retrieved documents
    context = "\n\n".join([f"From {doc['source']}:\n{doc['text']}" for doc in context_docs])
    
    prompt = f"""Based on the following context from educational documents, answer the user's question. If the answer is not in the context, say so clearly.

Context:
{context}

Question: {query}

Answer:"""
    
    try:
        response = ollama.chat(model='llama3.2:1b', messages=[{'role': 'user', 'content': prompt}])
        return response['message']['content']
    except Exception as e:
        return f"Error generating response: {str(e)}"

# API Endpoints

@bp.route('/rag/generate-mcq', methods=['GET', 'POST'])
def generate_mcq_from_pdf():
    """Generate MCQs from PDF content"""
    global texts, sources, embeddings

    embeddings, texts, sources = load_or_create_index()

    if not texts:
        return jsonify({
            'status': 'error', 
            'message': 'No PDF files found in the pdfs directory',
            'pdf_folder': PDF_FOLDER
        })

    try:
        # Generate 5 MCQs from combined content of all PDFs
        mcq_content, used_sources = generate_mcq_from_combined_content(texts, sources)

        result = {
            'status': 'success',
            'mcq_content': mcq_content,
            'sources_used': used_sources,
            'total_pdfs_processed': len(texts),
            'total_sources_used_for_mcq': len(used_sources)
        }

    except Exception as e:
        result = {
            'status': 'error',
            'message': f'Error generating MCQs: {str(e)}',
            'total_pdfs_processed': len(texts)
        }

    return jsonify(result)

@bp.route('/rag/chat', methods=['POST'])
def rag_chat():
    """RAG-based chat endpoint"""
    global texts, sources, embeddings
    
    data = request.get_json()
    if not data or 'query' not in data:
        return jsonify({'status': 'error', 'message': 'Query is required'}), 400
    
    query = data['query']
    
    # Load index if not already loaded
    if not texts:
        embeddings, texts, sources = load_or_create_index()
    
    if not texts:
        return jsonify({
            'status': 'error',
            'message': 'No PDF documents available for chat'
        }), 400
    
    try:
        # Search for relevant content
        relevant_docs = search_similar_content(query, top_k=3)
        
        if not relevant_docs:
            return jsonify({
                'status': 'success',
                'response': "I couldn't find relevant information in the available documents to answer your question.",
                'sources': []
            })
        
        # Generate response using RAG
        response = generate_rag_response(query, relevant_docs)
        
        return jsonify({
            'status': 'success',
            'response': response,
            'sources': [doc['source'] for doc in relevant_docs],
            'relevant_docs': len(relevant_docs)
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Error processing chat request: {str(e)}'
        }), 500

@bp.route('/rag/status', methods=['GET'])
def rag_status():
    """Check RAG system status and dependencies"""
    global texts, sources
    
    status = {
        'status': 'running',
        'dependencies': {
            'sentence_transformers': SENTENCE_TRANSFORMERS_AVAILABLE,
            'PyPDF2': PYPDF2_AVAILABLE,
            'ollama': OLLAMA_AVAILABLE
        },
        'pdf_folder': PDF_FOLDER,
        'pdfs_loaded': len(texts),
        'sources': sources
    }
    return jsonify(status)

@bp.route('/rag/reload', methods=['POST'])
def reload_rag_index():
    """Reload the RAG index from PDFs"""
    global texts, sources, embeddings
    
    try:
        embeddings, texts, sources = load_or_create_index()
        
        return jsonify({
            'status': 'success',
            'message': 'RAG index reloaded successfully',
            'pdfs_loaded': len(texts),
            'sources': sources
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Error reloading RAG index: {str(e)}'
        }), 500
