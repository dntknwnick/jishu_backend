#!/usr/bin/env python3
"""
Migration script to add pricing and token fields to course and subject models
Run this script to update the database schema with new fields.
"""

import sys
import os
from sqlalchemy import text

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from shared.models.user import db

def run_migration():
    """Run the migration to add pricing and token fields"""
    app = create_app()
    
    with app.app_context():
        try:
            print("🔄 Starting migration: Adding pricing and token fields...")
            
            # Add fields to exam_category table
            print("📝 Adding fields to exam_category table...")
            
            # Check if columns already exist before adding them
            result = db.session.execute(text("""
                SELECT COLUMN_NAME 
                FROM INFORMATION_SCHEMA.COLUMNS 
                WHERE TABLE_NAME = 'exam_category' 
                AND TABLE_SCHEMA = DATABASE()
                AND COLUMN_NAME IN ('amount', 'offer_amount', 'max_tokens')
            """))
            existing_columns = [row[0] for row in result.fetchall()]
            
            if 'amount' not in existing_columns:
                db.session.execute(text("""
                    ALTER TABLE exam_category 
                    ADD COLUMN amount DECIMAL(10,2) DEFAULT 0.00
                """))
                print("✅ Added 'amount' column to exam_category")
            else:
                print("⚠️  Column 'amount' already exists in exam_category")
            
            if 'offer_amount' not in existing_columns:
                db.session.execute(text("""
                    ALTER TABLE exam_category 
                    ADD COLUMN offer_amount DECIMAL(10,2) DEFAULT 0.00
                """))
                print("✅ Added 'offer_amount' column to exam_category")
            else:
                print("⚠️  Column 'offer_amount' already exists in exam_category")
            
            if 'max_tokens' not in existing_columns:
                db.session.execute(text("""
                    ALTER TABLE exam_category 
                    ADD COLUMN max_tokens INT DEFAULT 0
                """))
                print("✅ Added 'max_tokens' column to exam_category")
            else:
                print("⚠️  Column 'max_tokens' already exists in exam_category")
            
            # Add fields to exam_category_subjects table
            print("📝 Adding fields to exam_category_subjects table...")
            
            result = db.session.execute(text("""
                SELECT COLUMN_NAME 
                FROM INFORMATION_SCHEMA.COLUMNS 
                WHERE TABLE_NAME = 'exam_category_subjects' 
                AND TABLE_SCHEMA = DATABASE()
                AND COLUMN_NAME IN ('amount', 'offer_amount', 'max_tokens')
            """))
            existing_subject_columns = [row[0] for row in result.fetchall()]
            
            if 'amount' not in existing_subject_columns:
                db.session.execute(text("""
                    ALTER TABLE exam_category_subjects 
                    ADD COLUMN amount DECIMAL(10,2) DEFAULT 0.00
                """))
                print("✅ Added 'amount' column to exam_category_subjects")
            else:
                print("⚠️  Column 'amount' already exists in exam_category_subjects")
            
            if 'offer_amount' not in existing_subject_columns:
                db.session.execute(text("""
                    ALTER TABLE exam_category_subjects 
                    ADD COLUMN offer_amount DECIMAL(10,2) DEFAULT 0.00
                """))
                print("✅ Added 'offer_amount' column to exam_category_subjects")
            else:
                print("⚠️  Column 'offer_amount' already exists in exam_category_subjects")
            
            if 'max_tokens' not in existing_subject_columns:
                db.session.execute(text("""
                    ALTER TABLE exam_category_subjects 
                    ADD COLUMN max_tokens INT DEFAULT 100
                """))
                print("✅ Added 'max_tokens' column to exam_category_subjects")
            else:
                print("⚠️  Column 'max_tokens' already exists in exam_category_subjects")
            
            # Commit the changes
            db.session.commit()
            print("✅ Migration completed successfully!")
            
            # Update existing records with sample data
            print("📝 Updating existing records with sample pricing...")
            
            # Update exam categories with sample pricing
            db.session.execute(text("""
                UPDATE exam_category 
                SET amount = 999.00, offer_amount = 799.00, max_tokens = 0 
                WHERE amount = 0.00 OR amount IS NULL
            """))
            
            # Update subjects with sample pricing
            db.session.execute(text("""
                UPDATE exam_category_subjects 
                SET amount = 299.00, offer_amount = 199.00, max_tokens = 100 
                WHERE amount = 0.00 OR amount IS NULL
            """))
            
            db.session.commit()
            print("✅ Sample pricing data added to existing records!")
            
        except Exception as e:
            print(f"❌ Migration failed: {str(e)}")
            db.session.rollback()
            return False
            
    return True

def rollback_migration():
    """Rollback the migration by removing the added fields"""
    app = create_app()
    
    with app.app_context():
        try:
            print("🔄 Starting rollback: Removing pricing and token fields...")
            
            # Remove fields from exam_category table
            db.session.execute(text("ALTER TABLE exam_category DROP COLUMN IF EXISTS amount"))
            db.session.execute(text("ALTER TABLE exam_category DROP COLUMN IF EXISTS offer_amount"))
            db.session.execute(text("ALTER TABLE exam_category DROP COLUMN IF EXISTS max_tokens"))
            
            # Remove fields from exam_category_subjects table
            db.session.execute(text("ALTER TABLE exam_category_subjects DROP COLUMN IF EXISTS amount"))
            db.session.execute(text("ALTER TABLE exam_category_subjects DROP COLUMN IF EXISTS offer_amount"))
            db.session.execute(text("ALTER TABLE exam_category_subjects DROP COLUMN IF EXISTS max_tokens"))
            
            db.session.commit()
            print("✅ Rollback completed successfully!")
            
        except Exception as e:
            print(f"❌ Rollback failed: {str(e)}")
            db.session.rollback()
            return False
            
    return True

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "rollback":
        success = rollback_migration()
    else:
        success = run_migration()
    
    if success:
        print("🎉 Operation completed successfully!")
    else:
        print("💥 Operation failed!")
        sys.exit(1)
