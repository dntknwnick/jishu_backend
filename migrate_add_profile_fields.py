#!/usr/bin/env python3
"""
Migration script to add profile-related fields and tables for comprehensive user profile management
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from shared.models.user import db, User
from app import create_app
from sqlalchemy import text

def migrate():
    """Run migration to add profile fields and tables"""
    print("🔄 Starting profile fields migration...")

    app = create_app()
    with app.app_context():
        try:
            # Add new columns to users table
            print("📝 Adding new columns to users table...")
            
            # Check if columns exist before adding
            inspector = db.inspect(db.engine)
            users_columns = [col['name'] for col in inspector.get_columns('users')]
            
            alter_statements = []
            
            if 'avatar' not in users_columns:
                alter_statements.append("ALTER TABLE users ADD COLUMN avatar VARCHAR(500) DEFAULT NULL")
            if 'address' not in users_columns:
                alter_statements.append("ALTER TABLE users ADD COLUMN address VARCHAR(500) DEFAULT NULL")
            if 'gender' not in users_columns:
                alter_statements.append("ALTER TABLE users ADD COLUMN gender ENUM('male', 'female', 'other') DEFAULT NULL")
            if 'date_of_birth' not in users_columns:
                alter_statements.append("ALTER TABLE users ADD COLUMN date_of_birth DATE DEFAULT NULL")
            if 'city' not in users_columns:
                alter_statements.append("ALTER TABLE users ADD COLUMN city VARCHAR(100) DEFAULT NULL")
            if 'state' not in users_columns:
                alter_statements.append("ALTER TABLE users ADD COLUMN state VARCHAR(100) DEFAULT NULL")
            
            for statement in alter_statements:
                try:
                    db.session.execute(text(statement))
                    print(f"✅ {statement}")
                except Exception as e:
                    print(f"⚠️ {statement} - {str(e)}")
            
            # Create user_stats table
            print("\n📊 Creating user_stats table...")
            create_stats_table = """
            CREATE TABLE IF NOT EXISTS user_stats (
                id INT PRIMARY KEY AUTO_INCREMENT,
                user_id INT NOT NULL UNIQUE,
                total_tests_taken INT DEFAULT 0,
                highest_score INT DEFAULT 0,
                average_score DECIMAL(5,2) DEFAULT 0.00,
                current_streak INT DEFAULT 0,
                total_attempts INT DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
            """
            db.session.execute(text(create_stats_table))
            print("✅ user_stats table created")
            
            # Create user_academics table
            print("\n🎓 Creating user_academics table...")
            create_academics_table = """
            CREATE TABLE IF NOT EXISTS user_academics (
                id INT PRIMARY KEY AUTO_INCREMENT,
                user_id INT NOT NULL UNIQUE,
                school_college VARCHAR(255) DEFAULT NULL,
                grade_year VARCHAR(100) DEFAULT NULL,
                board_university VARCHAR(255) DEFAULT NULL,
                current_exam_target VARCHAR(255) DEFAULT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
            """
            db.session.execute(text(create_academics_table))
            print("✅ user_academics table created")
            
            # Create user_purchase_history table
            print("\n💳 Creating user_purchase_history table...")
            create_purchases_table = """
            CREATE TABLE IF NOT EXISTS user_purchase_history (
                id INT PRIMARY KEY AUTO_INCREMENT,
                user_id INT NOT NULL,
                purchase_id INT NOT NULL,
                exam_category_id INT DEFAULT NULL,
                subject_id INT DEFAULT NULL,
                purchase_type VARCHAR(50) DEFAULT 'single_subject',
                amount DECIMAL(10,2) DEFAULT 0.00,
                purchase_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                expiry_date DATE DEFAULT NULL,
                status ENUM('active', 'expired', 'cancelled') DEFAULT 'active',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                FOREIGN KEY (purchase_id) REFERENCES exam_category_purchase(id) ON DELETE CASCADE
            )
            """
            db.session.execute(text(create_purchases_table))
            print("✅ user_purchase_history table created")
            
            db.session.commit()
            print("\n✅ Migration completed successfully!")
            return True
            
        except Exception as e:
            db.session.rollback()
            print(f"\n❌ Migration failed: {str(e)}")
            import traceback
            traceback.print_exc()
            return False

if __name__ == '__main__':
    success = migrate()
    sys.exit(0 if success else 1)

