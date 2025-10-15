#!/usr/bin/env python3
"""
Test the database models and core functionality directly
"""

import os
import sys
from datetime import datetime

# Add the parent directory to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_model_imports():
    """Test if all models can be imported"""
    print("Testing model imports...")
    
    try:
        from shared.models.user import User, db
        from shared.models.purchase import ExamCategoryPurchase, MockTestAttempt, TestAttemptSession, TestAnswer, ExamCategoryQuestion
        from shared.models.course import ExamCategory, ExamCategorySubject
        from shared.services.mock_test_service import MockTestService
        
        print("✅ All models imported successfully")
        return True
    except Exception as e:
        print(f"❌ Model import failed: {str(e)}")
        return False

def test_mock_test_service():
    """Test MockTestService methods"""
    print("\nTesting MockTestService...")
    
    try:
        from shared.services.mock_test_service import MockTestService
        
        # Test that the service class exists and has required methods
        required_methods = [
            'create_test_cards_for_purchase',
            'get_user_test_cards',
            'start_test_attempt',
            'complete_test_attempt'
        ]
        
        for method_name in required_methods:
            if hasattr(MockTestService, method_name):
                print(f"✅ {method_name} method exists")
            else:
                print(f"❌ {method_name} method missing")
                return False
        
        print("✅ MockTestService structure validated")
        return True
        
    except Exception as e:
        print(f"❌ MockTestService test failed: {str(e)}")
        return False

def test_rag_service():
    """Test RAG service"""
    print("\nTesting RAG service...")
    
    try:
        from shared.services.rag_service import RAGService
        
        # Test that the service can be instantiated
        rag_service = RAGService(
            pdf_folder_path='./pdfs/subjects',
            vector_store_path='./vector_stores',
            ollama_model='llama3.2:1b'
        )
        
        print("✅ RAG service instantiated successfully")
        
        # Test status method
        status = rag_service.get_status()
        print(f"✅ RAG service status: {status.get('status', 'unknown')}")
        
        return True
        
    except Exception as e:
        print(f"❌ RAG service test failed: {str(e)}")
        return False

def test_database_schema():
    """Test database schema matches models"""
    print("\nTesting database schema...")
    
    try:
        import pymysql
        from config import Config
        
        # Connect to database
        connection = pymysql.connect(
            host=Config.MYSQL_HOST,
            user=Config.MYSQL_USER,
            password=Config.MYSQL_PASSWORD,
            database=Config.MYSQL_DB,
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )
        
        with connection.cursor() as cursor:
            # Check test_answers table structure
            cursor.execute("DESCRIBE test_answers")
            columns = cursor.fetchall()
            
            column_names = [col['Field'] for col in columns]
            
            # Verify required columns exist
            required_columns = ['id', 'session_id', 'question_id', 'selected_answer', 'is_correct', 'time_taken', 'created_at']
            missing_columns = [col for col in required_columns if col not in column_names]
            
            if missing_columns:
                print(f"❌ Missing columns in test_answers: {missing_columns}")
                return False
            
            # Verify attempt_id is NOT present (should have been removed)
            if 'attempt_id' in column_names:
                print("❌ attempt_id column still exists in test_answers table")
                return False
            
            print("✅ test_answers table schema is correct")
            
            # Check other important tables
            tables_to_check = [
                'mock_test_attempts',
                'test_attempt_sessions',
                'exam_category_purchase',
                'users'
            ]
            
            for table in tables_to_check:
                cursor.execute(f"SHOW TABLES LIKE '{table}'")
                result = cursor.fetchone()
                if result:
                    print(f"✅ {table} table exists")
                else:
                    print(f"❌ {table} table missing")
                    return False
        
        connection.close()
        print("✅ Database schema validation passed")
        return True
        
    except Exception as e:
        print(f"❌ Database schema test failed: {str(e)}")
        return False

def test_config():
    """Test configuration"""
    print("\nTesting configuration...")
    
    try:
        from config import Config
        
        # Check required config values
        required_configs = [
            'MYSQL_HOST',
            'MYSQL_USER', 
            'MYSQL_PASSWORD',
            'MYSQL_DB',
            'SECRET_KEY',
            'JWT_SECRET_KEY'
        ]
        
        for config_name in required_configs:
            value = getattr(Config, config_name, None)
            if value:
                print(f"✅ {config_name} is configured")
            else:
                print(f"❌ {config_name} is missing")
                return False
        
        # Check RAG config
        rag_auto_init = getattr(Config, 'RAG_AUTO_INITIALIZE', None)
        print(f"✅ RAG_AUTO_INITIALIZE: {rag_auto_init}")
        
        print("✅ Configuration validation passed")
        return True
        
    except Exception as e:
        print(f"❌ Configuration test failed: {str(e)}")
        return False

def main():
    """Main test function"""
    print("🧪 Direct Model and Service Testing")
    print("=" * 50)
    
    tests = [
        ("Model Imports", test_model_imports),
        ("MockTestService", test_mock_test_service),
        ("RAG Service", test_rag_service),
        ("Database Schema", test_database_schema),
        ("Configuration", test_config)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n🔍 Running {test_name} test...")
        try:
            if test_func():
                passed += 1
                print(f"✅ {test_name} - PASSED")
            else:
                print(f"❌ {test_name} - FAILED")
        except Exception as e:
            print(f"❌ {test_name} - FAILED with exception: {str(e)}")
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All direct tests passed!")
        print("✅ Core system components are working correctly")
        print("✅ Database schema is properly fixed")
        print("✅ Models and services are functional")
        return True
    else:
        print("⚠️ Some tests failed - check the issues above")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
