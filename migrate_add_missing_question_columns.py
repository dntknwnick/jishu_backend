#!/usr/bin/env python3
"""
Migration script to add missing columns to exam_category_questions table
These columns are defined in the model but missing from the database
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from shared.models.user import db

def migrate():
    """Add missing columns to exam_category_questions table"""

    app = create_app('development')

    with app.app_context():
        try:
            print("🔄 Starting migration: Adding missing columns to exam_category_questions...")
            
            # Get the database connection
            connection = db.engine.raw_connection()
            cursor = connection.cursor()
            
            # List of columns to add with their definitions
            columns_to_add = [
                ('mock_test_id', 'INT NULL, ADD FOREIGN KEY (mock_test_id) REFERENCES mock_test_attempts(id)'),
                ('is_ai_generated', 'BOOLEAN DEFAULT FALSE'),
                ('ai_model_used', 'VARCHAR(100) NULL'),
                ('difficulty_level', "ENUM('easy', 'medium', 'hard') DEFAULT 'medium'"),
                ('source_content', 'TEXT NULL'),
                ('generation_batch_id', 'VARCHAR(50) NULL'),
                ('batch_sequence', 'INT NULL'),
                ('chromadb_collection', 'VARCHAR(100) NULL'),
                ('multimodal_source_type', "ENUM('text', 'image', 'mixed') DEFAULT 'text'"),
                ('image_references', 'JSON NULL'),
                ('clip_embedding_id', 'VARCHAR(255) NULL'),
                ('generation_method', "VARCHAR(50) DEFAULT 'multimodal_rag'"),
            ]
            
            # Check which columns already exist
            cursor.execute("DESCRIBE exam_category_questions")
            existing_columns = {row[0] for row in cursor.fetchall()}
            print(f"✅ Existing columns: {len(existing_columns)}")
            
            # Add missing columns
            added_count = 0
            for col_name, col_def in columns_to_add:
                if col_name not in existing_columns:
                    try:
                        if col_name == 'mock_test_id':
                            # Special handling for foreign key
                            sql = f"ALTER TABLE exam_category_questions ADD COLUMN {col_name} {col_def}"
                        else:
                            sql = f"ALTER TABLE exam_category_questions ADD COLUMN {col_name} {col_def}"
                        
                        cursor.execute(sql)
                        print(f"  ✅ Added column: {col_name}")
                        added_count += 1
                    except Exception as e:
                        print(f"  ⚠️  Could not add column {col_name}: {str(e)}")
                else:
                    print(f"  ℹ️  Column already exists: {col_name}")
            
            connection.commit()
            cursor.close()
            connection.close()
            
            print(f"\n✅ Migration completed successfully!")
            print(f"   Added {added_count} new columns")
            print(f"   Total columns now: {len(existing_columns) + added_count}")
            
            return True
            
        except Exception as e:
            print(f"❌ Migration failed: {str(e)}")
            import traceback
            traceback.print_exc()
            return False

if __name__ == '__main__':
    success = migrate()
    sys.exit(0 if success else 1)

