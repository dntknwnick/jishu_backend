#!/usr/bin/env python3
"""
Database Setup Script for Jishu Backend
This script creates all the necessary tables and indexes for the complete educational platform
"""

import os
import sys
import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def get_db_connection():
    """Create database connection"""
    try:
        connection = mysql.connector.connect(
            host=os.getenv('MYSQL_HOST', 'localhost'),
            user=os.getenv('MYSQL_USER', 'root'),
            password=os.getenv('MYSQL_PASSWORD', 'admin'),
            database=os.getenv('MYSQL_DB', 'jishu_app'),
            autocommit=True
        )
        return connection
    except Error as e:
        print(f"❌ Error connecting to MySQL: {e}")
        return None

def execute_sql_file(connection, file_path):
    """Execute SQL commands from a file"""
    try:
        cursor = connection.cursor()
        
        with open(file_path, 'r', encoding='utf-8') as file:
            sql_content = file.read()
        
        # Split SQL commands by semicolon and execute each
        sql_commands = [cmd.strip() for cmd in sql_content.split(';') if cmd.strip()]
        
        for command in sql_commands:
            if command and not command.startswith('--'):
                try:
                    cursor.execute(command)
                    print(f"✅ Executed: {command[:50]}...")
                except Error as e:
                    if "already exists" in str(e).lower() or "duplicate" in str(e).lower():
                        print(f"⚠️  Skipped (already exists): {command[:50]}...")
                    else:
                        print(f"❌ Error executing command: {e}")
                        print(f"Command: {command}")
        
        cursor.close()
        return True
        
    except Exception as e:
        print(f"❌ Error executing SQL file: {e}")
        return False

def create_database_if_not_exists():
    """Create database if it doesn't exist"""
    try:
        connection = mysql.connector.connect(
            host=os.getenv('MYSQL_HOST', 'localhost'),
            user=os.getenv('MYSQL_USER', 'root'),
            password=os.getenv('MYSQL_PASSWORD', 'admin'),
            autocommit=True
        )
        
        cursor = connection.cursor()
        db_name = os.getenv('MYSQL_DB', 'jishu_app')
        
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {db_name}")
        print(f"✅ Database '{db_name}' created or already exists")
        
        cursor.close()
        connection.close()
        return True
        
    except Error as e:
        print(f"❌ Error creating database: {e}")
        return False

def run_original_schema():
    """Run the original schema first"""
    connection = get_db_connection()
    if not connection:
        return False
    
    print("📋 Running original schema...")
    
    # Original schema SQL
    original_schema = """
    CREATE TABLE IF NOT EXISTS `users` (
      `id` int NOT NULL AUTO_INCREMENT,
      `mobile_no` varchar(20) NOT NULL,
      `email_id` varchar(100) NOT NULL,
      `name` varchar(100) NOT NULL,
      `password` varchar(255) NOT NULL,
      `is_premium` tinyint(1) DEFAULT '0',
      `is_admin` tinyint(1) DEFAULT '0',
      `color_theme` enum('light','dark') DEFAULT 'light',
      `otp` varchar(10) DEFAULT NULL,
      `otp_verified` tinyint(1) DEFAULT '0',
      `last_login` datetime DEFAULT NULL,
      `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
      `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
      `status` enum('active','inactive','blocked') DEFAULT 'active',
      `source` varchar(100) DEFAULT NULL,
      PRIMARY KEY (`id`),
      UNIQUE KEY `email_id` (`email_id`)
    );

    CREATE TABLE IF NOT EXISTS exam_category (
      id INT PRIMARY KEY AUTO_INCREMENT,
      course_name VARCHAR(100) NOT NULL,
      description TEXT,
      created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
      updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS exam_category_subjects (
      id INT PRIMARY KEY AUTO_INCREMENT,
      exam_category_id INT,
      subject_name VARCHAR(100) NOT NULL,
      created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
      updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
      FOREIGN KEY (exam_category_id) REFERENCES exam_category(id)
    );

    CREATE TABLE IF NOT EXISTS exam_category_purchase (
      id INT PRIMARY KEY AUTO_INCREMENT,
      user_id INT,
      exam_category_id INT,
      subject_id INT,
      cost DECIMAL(10, 2) NOT NULL,
      no_of_attempts INT DEFAULT 3,
      attempts_used INT DEFAULT 0,
      total_marks INT,
      marks_scored INT DEFAULT 0,
      purchase_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
      last_attempt_date TIMESTAMP NULL,
      status ENUM('active', 'completed', 'expired') DEFAULT 'active',
      FOREIGN KEY (user_id) REFERENCES users(id),
      FOREIGN KEY (exam_category_id) REFERENCES exam_category(id),
      FOREIGN KEY (subject_id) REFERENCES exam_category_subjects(id)
    );

    CREATE TABLE IF NOT EXISTS exam_category_questions (
      id INT PRIMARY KEY AUTO_INCREMENT,
      exam_category_id INT,
      subject_id INT,
      question TEXT NOT NULL,
      option_1 VARCHAR(255) NOT NULL,
      option_2 VARCHAR(255) NOT NULL,
      option_3 VARCHAR(255) NOT NULL,
      option_4 VARCHAR(255) NOT NULL,
      correct_answer VARCHAR(255) NOT NULL,
      explanation TEXT,
      user_id INT,
      purchased_id INT,
      created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
      updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
      FOREIGN KEY (exam_category_id) REFERENCES exam_category(id),
      FOREIGN KEY (subject_id) REFERENCES exam_category_subjects(id),
      FOREIGN KEY (user_id) REFERENCES users(id),
      FOREIGN KEY (purchased_id) REFERENCES exam_category_purchase(id)
    );
    """
    
    try:
        cursor = connection.cursor()
        sql_commands = [cmd.strip() for cmd in original_schema.split(';') if cmd.strip()]
        
        for command in sql_commands:
            if command:
                cursor.execute(command)
                print(f"✅ Created original table")
        
        cursor.close()
        connection.close()
        return True
        
    except Error as e:
        print(f"❌ Error creating original schema: {e}")
        connection.close()
        return False

def main():
    """Main setup function"""
    print("🚀 Starting Jishu Backend Database Setup")
    print("=" * 50)
    
    # Step 1: Create database if not exists
    print("📊 Step 1: Creating database...")
    if not create_database_if_not_exists():
        print("❌ Failed to create database. Exiting.")
        sys.exit(1)
    
    # Step 2: Run original schema
    print("\n📋 Step 2: Creating original tables...")
    if not run_original_schema():
        print("❌ Failed to create original tables. Exiting.")
        sys.exit(1)
    
    # Step 3: Run new tables setup
    print("\n🆕 Step 3: Creating new tables and indexes...")
    connection = get_db_connection()
    if not connection:
        print("❌ Failed to connect to database. Exiting.")
        sys.exit(1)
    
    if os.path.exists('setup_new_tables.sql'):
        if execute_sql_file(connection, 'setup_new_tables.sql'):
            print("✅ New tables and indexes created successfully!")
        else:
            print("❌ Failed to create new tables.")
            connection.close()
            sys.exit(1)
    else:
        print("❌ setup_new_tables.sql file not found!")
        connection.close()
        sys.exit(1)
    
    connection.close()
    
    print("\n" + "=" * 50)
    print("🎉 Database setup completed successfully!")
    print("🔗 You can now start the Flask application")
    print("📍 Run: python app.py")

if __name__ == "__main__":
    main()
