#!/usr/bin/env python3
"""
Migration script to remove no_of_attempts and attempts_used columns
from exam_category_purchase table
"""

import sys
import os
from sqlalchemy import create_engine, text

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config import Config

def main():
    """Main migration function"""
    print("🚀 Starting migration to remove attempts-based logic...")
    print("📋 This will remove no_of_attempts and attempts_used columns from exam_category_purchase table")
    
    # Confirm with user
    confirm = input("⚠️  Are you sure you want to proceed? (y/N): ").strip().lower()
    if confirm != 'y':
        print("❌ Migration cancelled")
        return
    
    try:
        # Create database engine
        engine = create_engine(Config.SQLALCHEMY_DATABASE_URI)
        
        with engine.connect() as connection:
            # Start transaction
            trans = connection.begin()
            
            try:
                # Check if columns exist first
                print("🔍 Checking if columns exist...")
                
                result = connection.execute(text("""
                    SELECT COLUMN_NAME 
                    FROM INFORMATION_SCHEMA.COLUMNS 
                    WHERE TABLE_SCHEMA = :db_name 
                    AND TABLE_NAME = 'exam_category_purchase' 
                    AND COLUMN_NAME IN ('no_of_attempts', 'attempts_used')
                """), {"db_name": Config.MYSQL_DB})
                
                existing_columns = [row[0] for row in result.fetchall()]
                
                if not existing_columns:
                    print("✅ Columns do not exist. Migration not needed.")
                    return
                
                print(f"📝 Found columns to remove: {existing_columns}")
                
                # Remove columns
                if 'no_of_attempts' in existing_columns:
                    print("🗑️  Removing no_of_attempts column...")
                    connection.execute(text("ALTER TABLE exam_category_purchase DROP COLUMN no_of_attempts"))
                    print("✅ Removed no_of_attempts column")
                
                if 'attempts_used' in existing_columns:
                    print("🗑️  Removing attempts_used column...")
                    connection.execute(text("ALTER TABLE exam_category_purchase DROP COLUMN attempts_used"))
                    print("✅ Removed attempts_used column")
                
                # Commit transaction
                trans.commit()
                print("🎉 Migration completed successfully!")
                print("📝 The following changes were made:")
                print("   - Removed no_of_attempts column from exam_category_purchase table")
                print("   - Removed attempts_used column from exam_category_purchase table")
                print("   - System now uses only total_mock_tests and mock_tests_used for test limits")
                
            except Exception as e:
                trans.rollback()
                print(f"❌ Error during migration: {e}")
                raise
                
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
