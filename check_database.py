#!/usr/bin/env python3
"""
Database Check Script for Jishu Backend
This script verifies that all required tables exist in the database
"""

import os
import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def get_db_connection():
    """Create database connection"""
    try:
        connection = mysql.connector.connect(
            host=os.getenv('MYSQL_HOST', 'localhost'),
            user=os.getenv('MYSQL_USER', 'root'),
            password=os.getenv('MYSQL_PASSWORD', 'admin'),
            database=os.getenv('MYSQL_DB', 'jishu_app')
        )
        return connection
    except Error as e:
        print(f"❌ Error connecting to MySQL: {e}")
        return None

def check_tables():
    """Check if all required tables exist"""
    connection = get_db_connection()
    if not connection:
        return False
    
    # List of all required tables
    required_tables = [
        'users',
        'exam_category',
        'exam_category_subjects',
        'exam_category_purchase',
        'exam_category_questions',
        'test_attempts',
        'test_answers',
        'blog_posts',
        'blog_likes',
        'blog_comments',
        'ai_chat_history',
        'user_ai_stats',
        'password_reset_tokens'
    ]
    
    try:
        cursor = connection.cursor()
        
        # Get all existing tables
        cursor.execute("SHOW TABLES")
        existing_tables = [table[0] for table in cursor.fetchall()]
        
        print("🔍 Checking database tables...")
        print("=" * 50)
        
        missing_tables = []
        for table in required_tables:
            if table in existing_tables:
                print(f"✅ {table}")
            else:
                print(f"❌ {table} - MISSING")
                missing_tables.append(table)
        
        print("=" * 50)
        
        if missing_tables:
            print(f"❌ Missing {len(missing_tables)} tables: {', '.join(missing_tables)}")
            print("🔧 Run 'python setup_database.py' to create missing tables")
            return False
        else:
            print("🎉 All required tables exist!")
            
            # Check table structures
            print("\n📊 Table row counts:")
            print("-" * 30)
            for table in required_tables:
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                count = cursor.fetchone()[0]
                print(f"{table}: {count} rows")
            
            return True
        
    except Error as e:
        print(f"❌ Error checking tables: {e}")
        return False
    finally:
        if connection:
            cursor.close()
            connection.close()

def check_indexes():
    """Check if indexes exist"""
    connection = get_db_connection()
    if not connection:
        return False
    
    try:
        cursor = connection.cursor()
        
        print("\n🔍 Checking indexes...")
        print("-" * 30)
        
        # Check some key indexes
        key_indexes = [
            ('users', 'idx_users_email'),
            ('blog_posts', 'idx_posts_user'),
            ('blog_comments', 'idx_comments_post'),
            ('ai_chat_history', 'idx_chat_user'),
            ('test_attempts', 'idx_attempts_user')
        ]
        
        for table, index in key_indexes:
            cursor.execute(f"SHOW INDEX FROM {table} WHERE Key_name = '{index}'")
            result = cursor.fetchall()
            if result:
                print(f"✅ {table}.{index}")
            else:
                print(f"❌ {table}.{index} - MISSING")
        
        return True
        
    except Error as e:
        print(f"❌ Error checking indexes: {e}")
        return False
    finally:
        if connection:
            cursor.close()
            connection.close()

def main():
    """Main check function"""
    print("🔍 Jishu Backend Database Check")
    print("=" * 40)
    
    # Check database connection
    connection = get_db_connection()
    if not connection:
        print("❌ Cannot connect to database. Please check your .env file.")
        return
    
    db_name = os.getenv('MYSQL_DB', 'jishu_app')
    print(f"📊 Connected to database: {db_name}")
    connection.close()
    
    # Check tables
    tables_ok = check_tables()
    
    # Check indexes
    indexes_ok = check_indexes()
    
    print("\n" + "=" * 40)
    if tables_ok:
        print("✅ Database check completed successfully!")
        print("🚀 You can start the Flask application with: python app.py")
    else:
        print("❌ Database check failed!")
        print("🔧 Please run: python setup_database.py")

if __name__ == "__main__":
    main()
