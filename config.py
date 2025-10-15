import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Database Configuration
    MYSQL_HOST = os.getenv('MYSQL_HOST', 'localhost')
    MYSQL_USER = os.getenv('MYSQL_USER', 'root')
    MYSQL_PASSWORD = os.getenv('MYSQL_PASSWORD', 'admin')
    MYSQL_DB = os.getenv('MYSQL_DB', 'jishu_app')
    
    SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}/{MYSQL_DB}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # JWT Configuration
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'your-secret-key-change-in-production')
    JWT_ACCESS_TOKEN_EXPIRES = 3600  # 1 hour
    JWT_REFRESH_TOKEN_EXPIRES = 2592000  # 30 days
    
    # Google OAuth Configuration
    GOOGLE_CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID')
    GOOGLE_CLIENT_SECRET = os.getenv('GOOGLE_CLIENT_SECRET')
    GOOGLE_DISCOVERY_URL = "https://accounts.google.com/.well-known/openid_configuration"
    # Frontend callback URL for OAuth flow
    GOOGLE_REDIRECT_URI = os.getenv('GOOGLE_REDIRECT_URI', 'http://localhost:3000/auth/google/callback')

    # Flask Configuration
    SECRET_KEY = os.getenv('SECRET_KEY', 'your-secret-key-change-in-production')

    # Application Configuration
    APP_NAME = 'Jishu Backend'
    APP_VERSION = '1.0.0'
    ARCHITECTURE = 'monolithic'
    
    # CORS Configuration
    CORS_ORIGINS = os.getenv('CORS_ORIGINS', '*').split(',')

    # AI Service Configuration
    AI_PDF_FOLDER = os.getenv('AI_PDF_FOLDER', os.path.join(os.getcwd(), 'pdfs', 'subjects'))
    AI_OLLAMA_MODEL = os.getenv('AI_OLLAMA_MODEL', 'llama3.2:1b')
    AI_OLLAMA_BASE_URL = os.getenv('AI_OLLAMA_BASE_URL', 'http://localhost:11434')
    AI_MAX_CONTENT_LENGTH = int(os.getenv('AI_MAX_CONTENT_LENGTH', '8000'))
    AI_DEFAULT_QUESTIONS_COUNT = int(os.getenv('AI_DEFAULT_QUESTIONS_COUNT', '5'))
    AI_SIMILARITY_THRESHOLD = float(os.getenv('AI_SIMILARITY_THRESHOLD', '0.1'))
    AI_RAG_TOP_K = int(os.getenv('AI_RAG_TOP_K', '3'))

    # Vector Store Configuration
    AI_VECTOR_STORE_PATH = os.getenv('AI_VECTOR_STORE_PATH', os.path.join(os.getcwd(), 'vector_stores'))
    VECTOR_STORE_CHUNK_SIZE = int(os.getenv('VECTOR_STORE_CHUNK_SIZE', '1000'))

    # New RAG Pipeline Configuration
    RAG_PDF_FOLDER = os.getenv('RAG_PDF_FOLDER', os.path.join(os.getcwd(), 'pdfs', 'subjects'))
    RAG_VECTOR_STORE_PATH = os.getenv('RAG_VECTOR_STORE_PATH', os.path.join(os.getcwd(), 'vector_stores'))
    RAG_OLLAMA_MODEL = os.getenv('RAG_OLLAMA_MODEL', 'llama3.2:1b')
    RAG_EMBEDDING_MODEL = os.getenv('RAG_EMBEDDING_MODEL', 'all-MiniLM-L6-v2')
    RAG_CHUNK_SIZE = int(os.getenv('RAG_CHUNK_SIZE', '1000'))
    RAG_CHUNK_OVERLAP = int(os.getenv('RAG_CHUNK_OVERLAP', '200'))
    RAG_TOP_K_RESULTS = int(os.getenv('RAG_TOP_K_RESULTS', '3'))
    RAG_SIMILARITY_THRESHOLD = float(os.getenv('RAG_SIMILARITY_THRESHOLD', '0.01'))

    # RAG System Settings
    RAG_AUTO_INITIALIZE = os.getenv('RAG_AUTO_INITIALIZE', 'false').lower() == 'true'  # Disabled by default
    RAG_FORCE_RECREATE = os.getenv('RAG_FORCE_RECREATE', 'false').lower() == 'true'
    RAG_CACHE_ENABLED = os.getenv('RAG_CACHE_ENABLED', 'true').lower() == 'true'
    RAG_USE_FALLBACK = os.getenv('RAG_USE_FALLBACK', 'true').lower() == 'true'  # Enable fallback by default
    RAG_TIMEOUT_SECONDS = int(os.getenv('RAG_TIMEOUT_SECONDS', '120'))  # 120 second timeout for MCQ generation
    VECTOR_STORE_CHUNK_OVERLAP = int(os.getenv('VECTOR_STORE_CHUNK_OVERLAP', '200'))
    VECTOR_STORE_MAX_TOKENS = int(os.getenv('VECTOR_STORE_MAX_TOKENS', '4000'))
    VECTOR_STORE_TOP_K = int(os.getenv('VECTOR_STORE_TOP_K', '10'))

    # MCQ Generation Configuration
    MCQ_CACHE_ENABLED = os.getenv('MCQ_CACHE_ENABLED', 'true').lower() == 'true'
    MCQ_CACHE_SIZE = int(os.getenv('MCQ_CACHE_SIZE', '50'))
    MCQ_GENERATION_TIMEOUT = int(os.getenv('MCQ_GENERATION_TIMEOUT', '30'))
    MCQ_TARGET_TIME = int(os.getenv('MCQ_TARGET_TIME', '10'))

    # Performance Configuration
    ENABLE_VECTOR_STORE_OPTIMIZATION = os.getenv('ENABLE_VECTOR_STORE_OPTIMIZATION', 'true').lower() == 'true'
    AUTO_INITIALIZE_VECTOR_STORES = os.getenv('AUTO_INITIALIZE_VECTOR_STORES', 'false').lower() == 'true'

    # Environment Configuration
    FLASK_ENV = os.getenv('FLASK_ENV', 'development')
    NODE_ENV = os.getenv('NODE_ENV', 'development')

    # API Configuration
    API_BASE_URL = os.getenv('API_BASE_URL', 'http://localhost:5000')

    # Development Configuration
    BYPASS_PURCHASE_VALIDATION = os.getenv('BYPASS_PURCHASE_VALIDATION', 'True').lower() == 'true'
    LOCAL_DEV_MODE = os.getenv('LOCAL_DEV_MODE', 'True').lower() == 'true'

    # Purchase Flow Configuration
    @property
    def IS_PRODUCTION(self):
        """Check if running in production environment"""
        return self.FLASK_ENV.lower() == 'production'

    @property
    def IS_DEVELOPMENT(self):
        """Check if running in development environment"""
        return self.FLASK_ENV.lower() in ['development', 'local']

class DevelopmentConfig(Config):
    DEBUG = True
    # Override for development - always bypass purchase validation
    BYPASS_PURCHASE_VALIDATION = True
    LOCAL_DEV_MODE = True

class ProductionConfig(Config):
    DEBUG = False
    # Production settings - require actual purchase validation
    BYPASS_PURCHASE_VALIDATION = False
    LOCAL_DEV_MODE = False

class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
