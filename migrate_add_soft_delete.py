#!/usr/bin/env python3
"""
Migration script to add soft delete functionality to blog posts and comments
Adds is_deleted column to blog_posts and blog_comments tables
"""

import sys
import os
from sqlalchemy import text

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app
from shared.models.user import db

def add_soft_delete_columns():
    """Add is_deleted columns to blog_posts and blog_comments tables"""
    
    print("🔄 Starting migration: Adding soft delete columns...")
    
    with app.app_context():
        try:
            # Add is_deleted column to blog_posts table
            print("📝 Adding is_deleted column to blog_posts table...")
            db.session.execute(text("""
                ALTER TABLE blog_posts 
                ADD COLUMN is_deleted BOOLEAN DEFAULT FALSE
            """))
            print("✅ Added 'is_deleted' column to blog_posts")
            
            # Add is_deleted column to blog_comments table
            print("📝 Adding is_deleted column to blog_comments table...")
            db.session.execute(text("""
                ALTER TABLE blog_comments 
                ADD COLUMN is_deleted BOOLEAN DEFAULT FALSE
            """))
            print("✅ Added 'is_deleted' column to blog_comments")
            
            # Commit the changes
            db.session.commit()
            print("✅ Migration completed successfully!")
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ Migration failed: {str(e)}")
            return False
            
    return True

def rollback_soft_delete_columns():
    """Remove is_deleted columns from blog_posts and blog_comments tables"""
    
    print("🔄 Starting rollback: Removing soft delete columns...")
    
    with app.app_context():
        try:
            # Remove is_deleted column from blog_posts table
            print("📝 Removing is_deleted column from blog_posts table...")
            db.session.execute(text("""
                ALTER TABLE blog_posts 
                DROP COLUMN is_deleted
            """))
            print("✅ Removed 'is_deleted' column from blog_posts")
            
            # Remove is_deleted column from blog_comments table
            print("📝 Removing is_deleted column from blog_comments table...")
            db.session.execute(text("""
                ALTER TABLE blog_comments 
                DROP COLUMN is_deleted
            """))
            print("✅ Removed 'is_deleted' column from blog_comments")
            
            # Commit the changes
            db.session.commit()
            print("✅ Rollback completed successfully!")
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ Rollback failed: {str(e)}")
            return False
            
    return True

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "rollback":
        success = rollback_soft_delete_columns()
    else:
        success = add_soft_delete_columns()
    
    if success:
        print("🎉 Operation completed successfully!")
    else:
        print("💥 Operation failed!")
        sys.exit(1)
