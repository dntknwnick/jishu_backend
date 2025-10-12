#!/usr/bin/env python3
"""
Migration script to add AI-related fields to exam_category_questions table.

This script adds the following columns:
- is_ai_generated: Boolean flag for AI-generated questions
- ai_model_used: Model name used for generation
- difficulty_level: Question difficulty (easy/medium/hard)
- source_content: Original content used for generation

Run this script to update your database schema.
"""

import pymysql
import sys
from config import Config

def connect_to_database():
    """Connect to the MySQL database"""
    try:
        connection = pymysql.connect(
            host=Config.MYSQL_HOST,
            user=Config.MYSQL_USER,
            password=Config.MYSQL_PASSWORD,
            database=Config.MYSQL_DB,
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )
        return connection
    except Exception as e:
        print(f"Error connecting to database: {e}")
        return None

def check_column_exists(cursor, table_name, column_name):
    """Check if a column exists in a table"""
    cursor.execute(f"""
        SELECT COUNT(*) as count 
        FROM INFORMATION_SCHEMA.COLUMNS 
        WHERE TABLE_SCHEMA = DATABASE() 
        AND TABLE_NAME = '{table_name}' 
        AND COLUMN_NAME = '{column_name}'
    """)
    result = cursor.fetchone()
    return result['count'] > 0

def add_ai_fields_to_questions_table():
    """Add AI-related fields to exam_category_questions table"""
    connection = connect_to_database()
    if not connection:
        print("Failed to connect to database")
        return False
    
    try:
        cursor = connection.cursor()
        
        # Check current table structure
        print("Checking current table structure...")
        cursor.execute("DESCRIBE exam_category_questions")
        current_columns = cursor.fetchall()
        print("Current columns:")
        for col in current_columns:
            print(f"  - {col['Field']} ({col['Type']})")
        
        # List of columns to add
        columns_to_add = [
            {
                'name': 'is_ai_generated',
                'definition': 'is_ai_generated BOOLEAN DEFAULT FALSE'
            },
            {
                'name': 'ai_model_used',
                'definition': 'ai_model_used VARCHAR(100) NULL'
            },
            {
                'name': 'difficulty_level',
                'definition': "difficulty_level ENUM('easy', 'medium', 'hard') DEFAULT 'medium'"
            },
            {
                'name': 'source_content',
                'definition': 'source_content TEXT NULL'
            }
        ]
        
        # Add each column if it doesn't exist
        for column in columns_to_add:
            if check_column_exists(cursor, 'exam_category_questions', column['name']):
                print(f"Column '{column['name']}' already exists, skipping...")
            else:
                print(f"Adding column '{column['name']}'...")
                alter_sql = f"ALTER TABLE exam_category_questions ADD COLUMN {column['definition']}"
                cursor.execute(alter_sql)
                print(f"✓ Added column '{column['name']}'")
        
        # Commit the changes
        connection.commit()
        
        # Verify the changes
        print("\nVerifying changes...")
        cursor.execute("DESCRIBE exam_category_questions")
        updated_columns = cursor.fetchall()
        print("Updated table structure:")
        for col in updated_columns:
            print(f"  - {col['Field']} ({col['Type']})")
        
        print("\n✅ Migration completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error during migration: {e}")
        connection.rollback()
        return False
    finally:
        connection.close()

def main():
    """Main function"""
    print("🚀 Starting migration to add AI fields to exam_category_questions table...")
    print("=" * 70)
    
    success = add_ai_fields_to_questions_table()
    
    if success:
        print("\n🎉 Migration completed successfully!")
        print("You can now use AI-related features in your application.")
    else:
        print("\n💥 Migration failed!")
        print("Please check the error messages above and try again.")
        sys.exit(1)

if __name__ == "__main__":
    main()
