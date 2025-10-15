#!/usr/bin/env python3
"""
Check Database Constraints for Mock Test Attempts Table
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

def check_constraints():
    """Check all constraints on mock_test_attempts table"""
    
    with app.app_context():
        try:
            print("🔍 Checking constraints on mock_test_attempts table...")
            
            # Check all constraints
            result = db.session.execute(text("""
                SELECT
                    CONSTRAINT_NAME,
                    COLUMN_NAME
                FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE
                WHERE TABLE_NAME = 'mock_test_attempts'
                ORDER BY CONSTRAINT_NAME, ORDINAL_POSITION
            """))

            constraints = result.fetchall()

            print(f"Found {len(constraints)} constraint entries:")
            for constraint in constraints:
                print(f"  - {constraint.CONSTRAINT_NAME}: {constraint.COLUMN_NAME}")
            
            # Check indexes
            print("\n🔍 Checking indexes on mock_test_attempts table...")
            result = db.session.execute(text("""
                SHOW INDEX FROM mock_test_attempts
            """))
            
            indexes = result.fetchall()
            
            print(f"Found {len(indexes)} index entries:")
            for index in indexes:
                print(f"  - {index.Key_name}: {index.Column_name} (Unique: {index.Non_unique == 0})")
            
            # Check foreign keys
            print("\n🔍 Checking foreign key constraints...")
            result = db.session.execute(text("""
                SELECT 
                    CONSTRAINT_NAME,
                    COLUMN_NAME,
                    REFERENCED_TABLE_NAME,
                    REFERENCED_COLUMN_NAME
                FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE 
                WHERE TABLE_NAME = 'mock_test_attempts'
                AND REFERENCED_TABLE_NAME IS NOT NULL
            """))
            
            fks = result.fetchall()
            
            print(f"Found {len(fks)} foreign key constraints:")
            for fk in fks:
                print(f"  - {fk.CONSTRAINT_NAME}: {fk.COLUMN_NAME} -> {fk.REFERENCED_TABLE_NAME}.{fk.REFERENCED_COLUMN_NAME}")
            
            # Check for duplicate records
            print("\n🔍 Checking for duplicate records...")
            result = db.session.execute(text("""
                SELECT purchase_id, subject_id, test_number, COUNT(*) as count
                FROM mock_test_attempts 
                GROUP BY purchase_id, subject_id, test_number 
                HAVING COUNT(*) > 1
            """))
            
            duplicates = result.fetchall()
            
            if duplicates:
                print(f"⚠️  Found {len(duplicates)} duplicate record groups:")
                for dup in duplicates:
                    print(f"  - Purchase {dup.purchase_id}, Subject {dup.subject_id}, Test {dup.test_number}: {dup.count} records")
            else:
                print("✅ No duplicate records found")
            
            # Check current record count
            result = db.session.execute(text("SELECT COUNT(*) as count FROM mock_test_attempts"))
            count = result.fetchone().count
            print(f"\n📊 Total records in mock_test_attempts: {count}")
            
        except Exception as e:
            print(f"❌ Error checking constraints: {str(e)}")

if __name__ == "__main__":
    print("🔍 Mock Test Attempts Constraint Analysis")
    print("=" * 60)
    
    check_constraints()
    
    print("=" * 60)
