#!/usr/bin/env python3
"""
Database Migration: Fix Unique Constraint for Mock Test Attempts

This migration fixes the unique constraint on mock_test_attempts table to include subject_id,
allowing the same test number for different subjects within the same purchase.

Issue: Current constraint is (purchase_id, test_number) but should be (purchase_id, subject_id, test_number)
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import Flask app and database
from flask import Flask
from shared.models.user import db
from shared.models.purchase import MockTestAttempt
from sqlalchemy import text
from config import Config

# Create Flask app instance
app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)

def migrate_unique_constraint():
    """Fix the unique constraint on mock_test_attempts table"""
    
    with app.app_context():
        try:
            print("🔧 Starting unique constraint migration...")
            
            # Check if the old constraint exists
            result = db.session.execute(text("""
                SELECT CONSTRAINT_NAME 
                FROM INFORMATION_SCHEMA.TABLE_CONSTRAINTS 
                WHERE TABLE_NAME = 'mock_test_attempts' 
                AND CONSTRAINT_TYPE = 'UNIQUE'
                AND CONSTRAINT_NAME = 'unique_test_per_purchase'
            """))
            
            old_constraint_exists = result.fetchone() is not None
            
            if old_constraint_exists:
                print("📋 Dropping old unique constraint 'unique_test_per_purchase'...")
                db.session.execute(text("""
                    ALTER TABLE mock_test_attempts 
                    DROP INDEX unique_test_per_purchase
                """))
                print("✅ Old constraint dropped successfully")
            else:
                print("ℹ️  Old constraint 'unique_test_per_purchase' not found, skipping drop")
            
            # Check if the new constraint already exists
            result = db.session.execute(text("""
                SELECT CONSTRAINT_NAME 
                FROM INFORMATION_SCHEMA.TABLE_CONSTRAINTS 
                WHERE TABLE_NAME = 'mock_test_attempts' 
                AND CONSTRAINT_TYPE = 'UNIQUE'
                AND CONSTRAINT_NAME = 'unique_test_per_purchase_subject'
            """))
            
            new_constraint_exists = result.fetchone() is not None
            
            if not new_constraint_exists:
                print("📋 Creating new unique constraint 'unique_test_per_purchase_subject'...")
                db.session.execute(text("""
                    ALTER TABLE mock_test_attempts 
                    ADD CONSTRAINT unique_test_per_purchase_subject 
                    UNIQUE (purchase_id, subject_id, test_number)
                """))
                print("✅ New constraint created successfully")
            else:
                print("ℹ️  New constraint 'unique_test_per_purchase_subject' already exists")
            
            # Check for and remove any duplicate records that might exist
            print("🔍 Checking for duplicate records...")
            duplicates = db.session.execute(text("""
                SELECT purchase_id, subject_id, test_number, COUNT(*) as count
                FROM mock_test_attempts 
                GROUP BY purchase_id, subject_id, test_number 
                HAVING COUNT(*) > 1
            """)).fetchall()
            
            if duplicates:
                print(f"⚠️  Found {len(duplicates)} duplicate record groups")
                for dup in duplicates:
                    print(f"   - Purchase {dup.purchase_id}, Subject {dup.subject_id}, Test {dup.test_number}: {dup.count} records")
                
                # Remove duplicates, keeping only the first one
                for dup in duplicates:
                    print(f"🧹 Removing duplicates for Purchase {dup.purchase_id}, Subject {dup.subject_id}, Test {dup.test_number}")
                    
                    # Get all IDs for this duplicate group
                    ids_result = db.session.execute(text("""
                        SELECT id FROM mock_test_attempts 
                        WHERE purchase_id = :purchase_id 
                        AND subject_id = :subject_id 
                        AND test_number = :test_number 
                        ORDER BY id
                    """), {
                        'purchase_id': dup.purchase_id,
                        'subject_id': dup.subject_id,
                        'test_number': dup.test_number
                    }).fetchall()
                    
                    # Keep the first ID, delete the rest
                    if len(ids_result) > 1:
                        ids_to_delete = [row.id for row in ids_result[1:]]  # Skip first ID
                        for id_to_delete in ids_to_delete:
                            db.session.execute(text("""
                                DELETE FROM mock_test_attempts WHERE id = :id
                            """), {'id': id_to_delete})
                        print(f"   ✅ Removed {len(ids_to_delete)} duplicate records")
            else:
                print("✅ No duplicate records found")
            
            # Commit all changes
            db.session.commit()
            
            # Verify the new constraint is working
            print("🔍 Verifying new constraint...")
            result = db.session.execute(text("""
                SHOW INDEX FROM mock_test_attempts WHERE Key_name = 'unique_test_per_purchase_subject'
            """))
            
            constraint_info = result.fetchall()
            if constraint_info:
                print("✅ New unique constraint verified:")
                for info in constraint_info:
                    print(f"   - Column: {info.Column_name}")
            else:
                print("❌ Failed to verify new constraint")
                return False
            
            print("🎉 Migration completed successfully!")
            print("📋 Summary:")
            print("   - Old constraint (purchase_id, test_number) removed")
            print("   - New constraint (purchase_id, subject_id, test_number) added")
            print("   - Duplicate records cleaned up")
            print("   - Database integrity restored")
            
            return True
            
        except Exception as e:
            print(f"❌ Migration failed: {str(e)}")
            db.session.rollback()
            return False

if __name__ == "__main__":
    print("🚀 Mock Test Attempts Unique Constraint Migration")
    print("=" * 60)
    
    success = migrate_unique_constraint()
    
    if success:
        print("\n✅ Migration completed successfully!")
        print("🔄 You can now retry the purchase operation.")
    else:
        print("\n❌ Migration failed!")
        print("🔧 Please check the error messages above and try again.")
    
    print("=" * 60)
