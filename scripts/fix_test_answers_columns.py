#!/usr/bin/env python3
"""
Fix test_answers table columns
Remove attempt_id column since the model only uses session_id
"""

import os
import sys
import pymysql

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
        print(f"Error connecting to database: {str(e)}")
        return None

def fix_test_answers_table():
    """Fix the test_answers table by removing attempt_id column"""
    connection = get_db_connection()
    if not connection:
        return False
    
    try:
        with connection.cursor() as cursor:
            print("Fixing test_answers table...")
            
            # Step 1: Check current structure
            cursor.execute("DESCRIBE test_answers")
            columns = cursor.fetchall()
            
            has_attempt_id = any(col['Field'] == 'attempt_id' for col in columns)
            has_session_id = any(col['Field'] == 'session_id' for col in columns)
            
            print(f"Current state: attempt_id={has_attempt_id}, session_id={has_session_id}")
            
            if not has_attempt_id:
                print("attempt_id column doesn't exist - nothing to fix")
                return True
            
            if not has_session_id:
                print("ERROR: session_id column missing - cannot proceed")
                return False
            
            # Step 2: Check if there's any data
            cursor.execute("SELECT COUNT(*) as count FROM test_answers")
            record_count = cursor.fetchone()['count']
            
            if record_count > 0:
                print(f"WARNING: Table has {record_count} records")
                print("This operation will only work if no data depends on attempt_id")
            
            # Step 3: Drop foreign key constraint for attempt_id if it exists
            print("Dropping foreign key constraint for attempt_id...")
            try:
                # Get constraint name
                cursor.execute("""
                    SELECT CONSTRAINT_NAME 
                    FROM information_schema.KEY_COLUMN_USAGE 
                    WHERE TABLE_SCHEMA = %s 
                    AND TABLE_NAME = 'test_answers' 
                    AND COLUMN_NAME = 'attempt_id'
                    AND REFERENCED_TABLE_NAME IS NOT NULL
                """, (Config.MYSQL_DB,))
                
                constraints = cursor.fetchall()
                for constraint in constraints:
                    constraint_name = constraint['CONSTRAINT_NAME']
                    print(f"  Dropping constraint: {constraint_name}")
                    cursor.execute(f"ALTER TABLE test_answers DROP FOREIGN KEY {constraint_name}")
                
            except Exception as e:
                print(f"  Warning: Could not drop foreign key constraint: {str(e)}")
            
            # Step 4: Drop the attempt_id column
            print("Dropping attempt_id column...")
            cursor.execute("ALTER TABLE test_answers DROP COLUMN attempt_id")
            
            # Step 5: Verify the change
            cursor.execute("DESCRIBE test_answers")
            new_columns = cursor.fetchall()
            
            has_attempt_id_after = any(col['Field'] == 'attempt_id' for col in new_columns)
            has_session_id_after = any(col['Field'] == 'session_id' for col in new_columns)
            
            print(f"After fix: attempt_id={has_attempt_id_after}, session_id={has_session_id_after}")
            
            if not has_attempt_id_after and has_session_id_after:
                print("SUCCESS: test_answers table fixed!")
                connection.commit()
                return True
            else:
                print("ERROR: Fix did not work as expected")
                connection.rollback()
                return False
            
    except Exception as e:
        print(f"Error fixing table: {str(e)}")
        connection.rollback()
        return False
    finally:
        connection.close()

def main():
    """Main function"""
    print("Test Answers Table Fix")
    print("=" * 30)
    
    success = fix_test_answers_table()
    
    if success:
        print("\nTable fixed successfully!")
        print("The test_answers table now only has session_id column")
        print("This matches the TestAnswer model definition")
    else:
        print("\nFix failed!")
        print("Please check the error messages above")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
