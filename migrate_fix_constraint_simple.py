#!/usr/bin/env python3
"""
Simple Database Migration: Fix Unique Constraint for Mock Test Attempts

This migration fixes the unique constraint on mock_test_attempts table to include subject_id.
Since the table is empty, we can safely drop and recreate the constraint.
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

def migrate_constraint():
    """Fix the unique constraint on mock_test_attempts table"""
    
    with app.app_context():
        try:
            print("🔧 Starting constraint migration...")
            
            # Check current record count
            result = db.session.execute(text("SELECT COUNT(*) as count FROM mock_test_attempts"))
            count = result.fetchone().count
            print(f"📊 Current records in table: {count}")
            
            if count > 0:
                print("⚠️  Table has existing records. Migration may fail if duplicates exist.")
                print("🔍 Checking for potential conflicts...")
                
                # Check for records that would violate the new constraint
                result = db.session.execute(text("""
                    SELECT purchase_id, subject_id, test_number, COUNT(*) as count
                    FROM mock_test_attempts 
                    GROUP BY purchase_id, subject_id, test_number 
                    HAVING COUNT(*) > 1
                """))
                
                conflicts = result.fetchall()
                if conflicts:
                    print(f"❌ Found {len(conflicts)} conflicting record groups. Cannot proceed.")
                    for conflict in conflicts:
                        print(f"   - Purchase {conflict.purchase_id}, Subject {conflict.subject_id}, Test {conflict.test_number}: {conflict.count} records")
                    return False
                else:
                    print("✅ No conflicts found. Proceeding with migration.")
            
            # Drop the old unique constraint
            print("📋 Dropping old unique constraint...")
            try:
                db.session.execute(text("""
                    ALTER TABLE mock_test_attempts 
                    DROP INDEX unique_test_per_purchase
                """))
                print("✅ Old constraint dropped successfully")
            except Exception as e:
                if "doesn't exist" in str(e).lower():
                    print("ℹ️  Old constraint doesn't exist, skipping drop")
                else:
                    print(f"❌ Failed to drop old constraint: {str(e)}")
                    return False
            
            # Create the new unique constraint
            print("📋 Creating new unique constraint...")
            try:
                db.session.execute(text("""
                    ALTER TABLE mock_test_attempts 
                    ADD CONSTRAINT unique_test_per_purchase_subject 
                    UNIQUE (purchase_id, subject_id, test_number)
                """))
                print("✅ New constraint created successfully")
            except Exception as e:
                if "already exists" in str(e).lower():
                    print("ℹ️  New constraint already exists")
                else:
                    print(f"❌ Failed to create new constraint: {str(e)}")
                    return False
            
            # Commit the changes
            db.session.commit()
            
            # Verify the new constraint
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
            print("   - Database ready for purchase operations")
            
            return True
            
        except Exception as e:
            print(f"❌ Migration failed: {str(e)}")
            db.session.rollback()
            return False

if __name__ == "__main__":
    print("🚀 Mock Test Attempts Constraint Migration (Simple)")
    print("=" * 60)
    
    success = migrate_constraint()
    
    if success:
        print("\n✅ Migration completed successfully!")
        print("🔄 You can now retry the purchase operation.")
    else:
        print("\n❌ Migration failed!")
        print("🔧 Please check the error messages above and try again.")
    
    print("=" * 60)
