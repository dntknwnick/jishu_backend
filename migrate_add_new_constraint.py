#!/usr/bin/env python3
"""
Database Migration: Add New Unique Constraint for Mock Test Attempts

This migration adds a new unique constraint that includes subject_id without dropping the old one.
The application logic will handle preventing duplicates.
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

def add_new_constraint():
    """Add a new unique constraint that includes subject_id"""
    
    with app.app_context():
        try:
            print("🔧 Adding new unique constraint...")
            
            # Check if the new constraint already exists
            result = db.session.execute(text("""
                SHOW INDEX FROM mock_test_attempts WHERE Key_name = 'unique_test_per_purchase_subject'
            """))
            
            existing_constraint = result.fetchall()
            if existing_constraint:
                print("ℹ️  New constraint 'unique_test_per_purchase_subject' already exists")
                print("✅ Migration already completed")
                return True
            
            # Check current record count
            result = db.session.execute(text("SELECT COUNT(*) as count FROM mock_test_attempts"))
            count = result.fetchone().count
            print(f"📊 Current records in table: {count}")
            
            if count > 0:
                print("🔍 Checking for potential conflicts with new constraint...")
                
                # Check for records that would violate the new constraint
                result = db.session.execute(text("""
                    SELECT purchase_id, subject_id, test_number, COUNT(*) as count
                    FROM mock_test_attempts 
                    GROUP BY purchase_id, subject_id, test_number 
                    HAVING COUNT(*) > 1
                """))
                
                conflicts = result.fetchall()
                if conflicts:
                    print(f"❌ Found {len(conflicts)} conflicting record groups:")
                    for conflict in conflicts:
                        print(f"   - Purchase {conflict.purchase_id}, Subject {conflict.subject_id}, Test {conflict.test_number}: {conflict.count} records")
                    
                    # Remove duplicates
                    print("🧹 Removing duplicate records...")
                    for conflict in conflicts:
                        # Get all IDs for this duplicate group
                        ids_result = db.session.execute(text("""
                            SELECT id FROM mock_test_attempts 
                            WHERE purchase_id = :purchase_id 
                            AND subject_id = :subject_id 
                            AND test_number = :test_number 
                            ORDER BY id
                        """), {
                            'purchase_id': conflict.purchase_id,
                            'subject_id': conflict.subject_id,
                            'test_number': conflict.test_number
                        }).fetchall()
                        
                        # Keep the first ID, delete the rest
                        if len(ids_result) > 1:
                            ids_to_delete = [row.id for row in ids_result[1:]]  # Skip first ID
                            for id_to_delete in ids_to_delete:
                                db.session.execute(text("""
                                    DELETE FROM mock_test_attempts WHERE id = :id
                                """), {'id': id_to_delete})
                            print(f"   ✅ Removed {len(ids_to_delete)} duplicate records for Purchase {conflict.purchase_id}, Subject {conflict.subject_id}, Test {conflict.test_number}")
                else:
                    print("✅ No conflicts found")
            
            # Create the new unique constraint
            print("📋 Creating new unique constraint 'unique_test_per_purchase_subject'...")
            try:
                db.session.execute(text("""
                    ALTER TABLE mock_test_attempts 
                    ADD CONSTRAINT unique_test_per_purchase_subject 
                    UNIQUE (purchase_id, subject_id, test_number)
                """))
                print("✅ New constraint created successfully")
            except Exception as e:
                if "already exists" in str(e).lower() or "duplicate" in str(e).lower():
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
            print("   - New constraint (purchase_id, subject_id, test_number) added")
            print("   - Old constraint kept for compatibility")
            print("   - Application logic will prevent duplicates")
            print("   - Database ready for purchase operations")
            
            return True
            
        except Exception as e:
            print(f"❌ Migration failed: {str(e)}")
            db.session.rollback()
            return False

if __name__ == "__main__":
    print("🚀 Mock Test Attempts - Add New Constraint")
    print("=" * 60)
    
    success = add_new_constraint()
    
    if success:
        print("\n✅ Migration completed successfully!")
        print("🔄 You can now retry the purchase operation.")
    else:
        print("\n❌ Migration failed!")
        print("🔧 Please check the error messages above and try again.")
    
    print("=" * 60)
