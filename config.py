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
    AI_PDF_FOLDER = os.getenv('AI_PDF_FOLDER', os.path.join(os.getcwd(), 'pdfs'))
    AI_OLLAMA_MODEL = os.getenv('AI_OLLAMA_MODEL', 'llama3.2:1b')
    AI_MAX_CONTENT_LENGTH = int(os.getenv('AI_MAX_CONTENT_LENGTH', '8000'))
    AI_DEFAULT_QUESTIONS_COUNT = int(os.getenv('AI_DEFAULT_QUESTIONS_COUNT', '5'))
    AI_SIMILARITY_THRESHOLD = float(os.getenv('AI_SIMILARITY_THRESHOLD', '0.1'))
    AI_RAG_TOP_K = int(os.getenv('AI_RAG_TOP_K', '3'))

    # Development Configuration
    BYPASS_PURCHASE_VALIDATION = os.getenv('BYPASS_PURCHASE_VALIDATION', 'True').lower() == 'true'
    LOCAL_DEV_MODE = os.getenv('LOCAL_DEV_MODE', 'True').lower() == 'true'

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
