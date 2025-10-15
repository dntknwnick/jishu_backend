#!/usr/bin/env python3
"""
Database Migration Script: Fix test_answers table schema
This script updates the test_answers table to match the current model definition
"""

import os
import sys
import pymysql
from datetime import datetime

# Add the parent directory to the path so we can import from shared
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import Config

def get_db_connection():
    """Get database connection"""
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
        print(f"❌ Error connecting to database: {str(e)}")
        return None

def check_table_structure():
    """Check current test_answers table structure"""
    connection = get_db_connection()
    if not connection:
        return False
    
    try:
        with connection.cursor() as cursor:
            # Check current table structure
            cursor.execute("DESCRIBE test_answers")
            columns = cursor.fetchall()
            
            print("📊 Current test_answers table structure:")
            for col in columns:
                print(f"  - {col['Field']}: {col['Type']} {'NULL' if col['Null'] == 'YES' else 'NOT NULL'}")
            
            # Check if attempt_id exists
            has_attempt_id = any(col['Field'] == 'attempt_id' for col in columns)
            has_session_id = any(col['Field'] == 'session_id' for col in columns)
            
            print(f"\n🔍 Column Analysis:")
            print(f"  - Has attempt_id: {has_attempt_id}")
            print(f"  - Has session_id: {has_session_id}")
            
            return {
                'has_attempt_id': has_attempt_id,
                'has_session_id': has_session_id,
                'columns': columns
            }
            
    except Exception as e:
        print(f"❌ Error checking table structure: {str(e)}")
        return False
    finally:
        connection.close()

def check_data_usage():
    """Check how the test_answers table is currently being used"""
    connection = get_db_connection()
    if not connection:
        return False
    
    try:
        with connection.cursor() as cursor:
            # Count total records
            cursor.execute("SELECT COUNT(*) as total FROM test_answers")
            total_count = cursor.fetchone()['total']
            
            print(f"\n📈 Data Usage Analysis:")
            print(f"  - Total test_answers records: {total_count}")
            
            if total_count > 0:
                # Check for NULL values in attempt_id (if it exists)
                try:
                    cursor.execute("SELECT COUNT(*) as null_attempt_id FROM test_answers WHERE attempt_id IS NULL")
                    null_attempt_id = cursor.fetchone()['null_attempt_id']
                    print(f"  - Records with NULL attempt_id: {null_attempt_id}")
                except:
                    print("  - attempt_id column doesn't exist")
                
                # Check for NULL values in session_id (if it exists)
                try:
                    cursor.execute("SELECT COUNT(*) as null_session_id FROM test_answers WHERE session_id IS NULL")
                    null_session_id = cursor.fetchone()['null_session_id']
                    print(f"  - Records with NULL session_id: {null_session_id}")
                except:
                    print("  - session_id column doesn't exist")
            
            return True
            
    except Exception as e:
        print(f"❌ Error checking data usage: {str(e)}")
        return False
    finally:
        connection.close()

def backup_table():
    """Create a backup of the test_answers table"""
    connection = get_db_connection()
    if not connection:
        return False
    
    try:
        with connection.cursor() as cursor:
            # Create backup table
            backup_table_name = f"test_answers_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            print(f"💾 Creating backup table: {backup_table_name}")
            cursor.execute(f"CREATE TABLE {backup_table_name} AS SELECT * FROM test_answers")
            
            # Check backup
            cursor.execute(f"SELECT COUNT(*) as count FROM {backup_table_name}")
            backup_count = cursor.fetchone()['count']
            
            print(f"✅ Backup created successfully with {backup_count} records")
            return backup_table_name
            
    except Exception as e:
        print(f"❌ Error creating backup: {str(e)}")
        return False
    finally:
        connection.close()

def migrate_schema():
    """Migrate the test_answers table schema"""
    connection = get_db_connection()
    if not connection:
        return False
    
    try:
        with connection.cursor() as cursor:
            print("🔄 Starting schema migration...")
            
            # Step 1: Add session_id column if it doesn't exist
            print("  1. Adding session_id column...")
            try:
                cursor.execute("""
                    ALTER TABLE test_answers 
                    ADD COLUMN session_id INT NULL 
                    AFTER id
                """)
                print("     ✅ session_id column added")
            except pymysql.err.OperationalError as e:
                if "Duplicate column name" in str(e):
                    print("     ℹ️ session_id column already exists")
                else:
                    raise e
            
            # Step 2: Add foreign key constraint for session_id
            print("  2. Adding foreign key constraint for session_id...")
            try:
                cursor.execute("""
                    ALTER TABLE test_answers 
                    ADD CONSTRAINT fk_test_answers_session 
                    FOREIGN KEY (session_id) REFERENCES test_attempt_sessions(id) ON DELETE CASCADE
                """)
                print("     ✅ Foreign key constraint added")
            except pymysql.err.OperationalError as e:
                if "Duplicate key name" in str(e) or "already exists" in str(e):
                    print("     ℹ️ Foreign key constraint already exists")
                else:
                    print(f"     ⚠️ Could not add foreign key: {str(e)}")
            
            # Step 3: Make session_id NOT NULL (after data migration if needed)
            print("  3. Checking if session_id can be made NOT NULL...")
            cursor.execute("SELECT COUNT(*) as null_count FROM test_answers WHERE session_id IS NULL")
            null_count = cursor.fetchone()['null_count']
            
            if null_count == 0:
                try:
                    cursor.execute("ALTER TABLE test_answers MODIFY session_id INT NOT NULL")
                    print("     ✅ session_id set to NOT NULL")
                except Exception as e:
                    print(f"     ⚠️ Could not set session_id to NOT NULL: {str(e)}")
            else:
                print(f"     ⚠️ Cannot set session_id to NOT NULL - {null_count} records have NULL values")
            
            # Step 4: Remove attempt_id column if it exists and is not used
            print("  4. Checking attempt_id column...")
            try:
                cursor.execute("SELECT COUNT(*) as count FROM test_answers WHERE attempt_id IS NOT NULL")
                attempt_id_usage = cursor.fetchone()['count']
                
                if attempt_id_usage == 0:
                    print("     🗑️ Removing unused attempt_id column...")
                    cursor.execute("ALTER TABLE test_answers DROP COLUMN attempt_id")
                    print("     ✅ attempt_id column removed")
                else:
                    print(f"     ⚠️ attempt_id column has {attempt_id_usage} records - keeping for now")
            except pymysql.err.OperationalError:
                print("     ℹ️ attempt_id column doesn't exist")
            
            connection.commit()
            print("✅ Schema migration completed successfully")
            return True
            
    except Exception as e:
        print(f"❌ Error during migration: {str(e)}")
        connection.rollback()
        return False
    finally:
        connection.close()

def verify_migration():
    """Verify the migration was successful"""
    print("\n🔍 Verifying migration...")
    structure = check_table_structure()
    
    if structure and structure['has_session_id']:
        print("✅ Migration verification successful")
        return True
    else:
        print("❌ Migration verification failed")
        return False

def main():
    """Main migration function"""
    print("🚀 Test Answers Schema Migration Tool")
    print("=" * 50)
    
    # Step 1: Check current structure
    print("Step 1: Analyzing current table structure...")
    structure = check_table_structure()
    if not structure:
        print("❌ Failed to analyze table structure")
        return False
    
    # Step 2: Check data usage
    print("\nStep 2: Analyzing data usage...")
    if not check_data_usage():
        print("❌ Failed to analyze data usage")
        return False
    
    # Step 3: Determine if migration is needed
    if structure['has_session_id'] and not structure['has_attempt_id']:
        print("\n✅ Table schema is already correct - no migration needed")
        return True
    
    # Step 4: Create backup
    print("\nStep 3: Creating backup...")
    backup_name = backup_table()
    if not backup_name:
        print("❌ Failed to create backup")
        return False
    
    # Step 5: Perform migration
    print("\nStep 4: Performing schema migration...")
    if not migrate_schema():
        print("❌ Migration failed")
        return False
    
    # Step 6: Verify migration
    if not verify_migration():
        print("❌ Migration verification failed")
        return False
    
    print("\n🎉 Migration completed successfully!")
    print(f"💾 Backup table created: {backup_name}")
    print("\nNext steps:")
    print("1. Test the application to ensure everything works")
    print("2. If issues occur, you can restore from the backup table")
    print("3. Once confirmed working, you can drop the backup table")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
