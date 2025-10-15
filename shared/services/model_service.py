"""
Layer 1: Model Initialization Service
Pre-download and cache Hugging Face embedding model and Ollama LLM locally.
Load both models once at application start — do not re-download or reinitialize on requests.
Initialize a persistent ChromaDB client at startup; this client should be reused in all API requests.
"""

import os
import logging
import time
from typing import Optional, Dict, Any
from pathlib import Path
import threading

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Try to import dependencies
try:
    import chromadb
    from chromadb.config import Settings
    CHROMADB_AVAILABLE = True
except ImportError:
    CHROMADB_AVAILABLE = False
    logger.warning("ChromaDB not available. Vector storage will be limited.")

try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False
    logger.warning("SentenceTransformers not available. Embeddings will be limited.")

try:
    import ollama
    OLLAMA_AVAILABLE = True
except ImportError:
    OLLAMA_AVAILABLE = False
    logger.warning("Ollama not available. LLM generation will not work.")


class ModelService:
    """
    Singleton service for managing all AI models and database connections.
    Initializes once at startup and provides cached instances for all requests.
    """
    
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super(ModelService, cls).__new__(cls)
        return cls._instance
    
    def __init__(self, 
                 embedding_model_name: str = "all-MiniLM-L6-v2",
                 ollama_model_name: str = "llama3.2:1b",
                 vector_store_path: str = "./vector_stores",
                 models_cache_path: str = "./models"):
        """
        Initialize the model service with all required models and connections.
        
        Args:
            embedding_model_name: Name of the SentenceTransformer model
            ollama_model_name: Name of the Ollama model
            vector_store_path: Path to ChromaDB persistent storage
            models_cache_path: Path to cache downloaded models
        """
        # Prevent re-initialization
        if hasattr(self, '_initialized'):
            return
            
        self.embedding_model_name = embedding_model_name
        self.ollama_model_name = ollama_model_name
        self.vector_store_path = Path(vector_store_path)
        self.models_cache_path = Path(models_cache_path)
        
        # Ensure directories exist
        self.vector_store_path.mkdir(parents=True, exist_ok=True)
        self.models_cache_path.mkdir(parents=True, exist_ok=True)
        
        # Model instances
        self.embedding_model: Optional[SentenceTransformer] = None
        self.chroma_client: Optional[chromadb.PersistentClient] = None
        self.ollama_client = None
        
        # Status tracking
        self.initialization_status = {
            'embedding_model': False,
            'chroma_client': False,
            'ollama_client': False,
            'initialization_time': None,
            'last_health_check': None
        }
        
        # Initialize all components
        self._initialize_all_models()
        self._initialized = True
    
    def _initialize_all_models(self):
        """Initialize all models and connections at startup"""
        start_time = time.time()
        logger.info("🚀 Starting model initialization...")
        
        # Initialize embedding model
        self._initialize_embedding_model()
        
        # Initialize ChromaDB client
        self._initialize_chroma_client()
        
        # Initialize Ollama client
        self._initialize_ollama_client()
        
        initialization_time = time.time() - start_time
        self.initialization_status['initialization_time'] = initialization_time
        
        logger.info(f"✅ Model initialization completed in {initialization_time:.2f}s")
        self._log_initialization_summary()
    
    def _initialize_embedding_model(self):
        """Initialize and cache the embedding model"""
        if not SENTENCE_TRANSFORMERS_AVAILABLE:
            logger.warning("❌ SentenceTransformers not available")
            return
            
        try:
            logger.info(f"📥 Loading embedding model: {self.embedding_model_name}")
            
            # Force CPU mode and use local cache to prevent downloads during requests
            self.embedding_model = SentenceTransformer(
                self.embedding_model_name,
                device='cpu',
                cache_folder=str(self.models_cache_path / 'sentence_transformers')
            )
            
            # Warm up the model with a test embedding
            test_text = "This is a test sentence for model warmup."
            _ = self.embedding_model.encode([test_text])
            
            self.initialization_status['embedding_model'] = True
            logger.info(f"✅ Embedding model loaded and warmed up: {self.embedding_model_name}")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize embedding model: {str(e)}")
            self.initialization_status['embedding_model'] = False
    
    def _initialize_chroma_client(self):
        """Initialize persistent ChromaDB client"""
        if not CHROMADB_AVAILABLE:
            logger.warning("❌ ChromaDB not available")
            return
            
        try:
            logger.info("📥 Initializing ChromaDB client...")
            
            # Initialize with optimized settings for production
            self.chroma_client = chromadb.PersistentClient(
                path=str(self.vector_store_path),
                settings=Settings(
                    anonymized_telemetry=False,
                    allow_reset=True,
                    is_persistent=True
                )
            )
            
            # Test the connection
            collections = self.chroma_client.list_collections()
            logger.info(f"📊 ChromaDB connected. Found {len(collections)} existing collections.")
            
            self.initialization_status['chroma_client'] = True
            logger.info("✅ ChromaDB client initialized successfully")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize ChromaDB client: {str(e)}")
            self.initialization_status['chroma_client'] = False
    
    def _initialize_ollama_client(self):
        """Initialize Ollama client and verify model availability"""
        if not OLLAMA_AVAILABLE:
            logger.warning("❌ Ollama not available")
            return
            
        try:
            logger.info(f"📥 Initializing Ollama client for model: {self.ollama_model_name}")
            
            # Test Ollama connection and model availability
            models_response = ollama.list()
            available_models = []

            if 'models' in models_response:
                for model in models_response['models']:
                    if 'name' in model:
                        available_models.append(model['name'])
                    elif 'model' in model:
                        available_models.append(model['model'])

            logger.info(f"Available Ollama models: {available_models}")

            if self.ollama_model_name in available_models:
                # Warm up the model with a test generation
                test_response = ollama.generate(
                    model=self.ollama_model_name,
                    prompt="Test prompt for model warmup.",
                    options={'num_predict': 10}
                )
                
                self.ollama_client = ollama
                self.initialization_status['ollama_client'] = True
                logger.info(f"✅ Ollama model warmed up: {self.ollama_model_name}")
            else:
                logger.warning(f"⚠️ Ollama model not found: {self.ollama_model_name}")
                logger.info(f"Available models: {available_models}")
                self.initialization_status['ollama_client'] = False
                
        except Exception as e:
            logger.error(f"❌ Failed to initialize Ollama client: {str(e)}")
            self.initialization_status['ollama_client'] = False
    
    def _log_initialization_summary(self):
        """Log a summary of initialization status"""
        logger.info("📊 Model Service Initialization Summary:")
        logger.info(f"   Embedding Model: {'✅' if self.initialization_status['embedding_model'] else '❌'}")
        logger.info(f"   ChromaDB Client: {'✅' if self.initialization_status['chroma_client'] else '❌'}")
        logger.info(f"   Ollama Client: {'✅' if self.initialization_status['ollama_client'] else '❌'}")
        logger.info(f"   Total Time: {self.initialization_status['initialization_time']:.2f}s")
    
    def get_embedding_model(self) -> Optional[SentenceTransformer]:
        """Get the cached embedding model instance"""
        return self.embedding_model
    
    def get_chroma_client(self) -> Optional[chromadb.PersistentClient]:
        """Get the cached ChromaDB client instance"""
        return self.chroma_client
    
    def get_ollama_client(self):
        """Get the Ollama client"""
        return self.ollama_client
    
    def health_check(self) -> Dict[str, Any]:
        """Perform health check on all initialized models and connections"""
        health_status = {
            'timestamp': time.time(),
            'overall_status': 'healthy',
            'components': {}
        }
        
        # Check embedding model
        if self.embedding_model:
            try:
                test_embedding = self.embedding_model.encode(["Health check test"])
                health_status['components']['embedding_model'] = {
                    'status': 'healthy',
                    'model_name': self.embedding_model_name,
                    'embedding_dim': len(test_embedding[0])
                }
            except Exception as e:
                health_status['components']['embedding_model'] = {
                    'status': 'unhealthy',
                    'error': str(e)
                }
                health_status['overall_status'] = 'degraded'
        else:
            health_status['components']['embedding_model'] = {'status': 'not_initialized'}
            health_status['overall_status'] = 'degraded'
        
        # Check ChromaDB client
        if self.chroma_client:
            try:
                collections = self.chroma_client.list_collections()
                health_status['components']['chroma_client'] = {
                    'status': 'healthy',
                    'collections_count': len(collections),
                    'path': str(self.vector_store_path)
                }
            except Exception as e:
                health_status['components']['chroma_client'] = {
                    'status': 'unhealthy',
                    'error': str(e)
                }
                health_status['overall_status'] = 'degraded'
        else:
            health_status['components']['chroma_client'] = {'status': 'not_initialized'}
            health_status['overall_status'] = 'degraded'
        
        # Check Ollama client
        if self.ollama_client:
            try:
                models = ollama.list()
                health_status['components']['ollama_client'] = {
                    'status': 'healthy',
                    'model_name': self.ollama_model_name,
                    'available_models': len(models.get('models', []))
                }
            except Exception as e:
                health_status['components']['ollama_client'] = {
                    'status': 'unhealthy',
                    'error': str(e)
                }
                health_status['overall_status'] = 'degraded'
        else:
            health_status['components']['ollama_client'] = {'status': 'not_initialized'}
            health_status['overall_status'] = 'degraded'
        
        self.initialization_status['last_health_check'] = health_status['timestamp']
        return health_status
    
    def get_status(self) -> Dict[str, Any]:
        """Get comprehensive status of the model service"""
        # Determine overall status
        if all(self.initialization_status.values()):
            overall_status = 'ready'
        elif any(self.initialization_status.values()):
            overall_status = 'partial'
        else:
            overall_status = 'error'

        return {
            'service_name': 'ModelService',
            'status': overall_status,
            'initialization_status': self.initialization_status,
            'configuration': {
                'embedding_model_name': self.embedding_model_name,
                'ollama_model_name': self.ollama_model_name,
                'vector_store_path': str(self.vector_store_path),
                'models_cache_path': str(self.models_cache_path)
            },
            'dependencies': {
                'chromadb': CHROMADB_AVAILABLE,
                'sentence_transformers': SENTENCE_TRANSFORMERS_AVAILABLE,
                'ollama': OLLAMA_AVAILABLE
            }
        }


# Global model service instance
_model_service: Optional[ModelService] = None
_service_lock = threading.Lock()


def get_model_service(**kwargs) -> ModelService:
    """
    Get or create the global model service instance.
    Thread-safe singleton pattern.
    """
    global _model_service
    
    if _model_service is None:
        with _service_lock:
            if _model_service is None:
                _model_service = ModelService(**kwargs)
    
    return _model_service


def initialize_models_at_startup(**kwargs):
    """
    Initialize models at application startup.
    Call this once when the Flask app starts.
    """
    logger.info("🚀 Initializing models at application startup...")
    model_service = get_model_service(**kwargs)
    return model_service.get_status()
