#!/usr/bin/env python3
"""
Database Schema Checker: Check test_answers table schema
This script checks the current test_answers table structure
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
            
            print("Current test_answers table structure:")
            for col in columns:
                null_str = 'NULL' if col['Null'] == 'YES' else 'NOT NULL'
                print(f"  - {col['Field']}: {col['Type']} {null_str}")
            
            # Check if attempt_id exists
            has_attempt_id = any(col['Field'] == 'attempt_id' for col in columns)
            has_session_id = any(col['Field'] == 'session_id' for col in columns)
            
            print(f"\nColumn Analysis:")
            print(f"  - Has attempt_id: {has_attempt_id}")
            print(f"  - Has session_id: {has_session_id}")
            
            return {
                'has_attempt_id': has_attempt_id,
                'has_session_id': has_session_id,
                'columns': columns
            }
            
    except Exception as e:
        print(f"Error checking table structure: {str(e)}")
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
            
            print(f"\nData Usage Analysis:")
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
        print(f"Error checking data usage: {str(e)}")
        return False
    finally:
        connection.close()

def main():
    """Main function"""
    print("Test Answers Schema Checker")
    print("=" * 40)
    
    # Step 1: Check current structure
    print("Step 1: Analyzing current table structure...")
    structure = check_table_structure()
    if not structure:
        print("Failed to analyze table structure")
        return False
    
    # Step 2: Check data usage
    print("\nStep 2: Analyzing data usage...")
    if not check_data_usage():
        print("Failed to analyze data usage")
        return False
    
    # Step 3: Provide recommendations
    print("\nRecommendations:")
    if structure['has_attempt_id'] and not structure['has_session_id']:
        print("  - Database has attempt_id but model expects session_id")
        print("  - Need to add session_id column and update references")
    elif structure['has_session_id'] and not structure['has_attempt_id']:
        print("  - Database schema matches model - no changes needed")
    elif structure['has_attempt_id'] and structure['has_session_id']:
        print("  - Database has both columns - need to clean up")
    else:
        print("  - Database missing both columns - major issue!")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
