"""
Migration script to add multimodal RAG fields to exam_category_questions table
"""

import os
import sys
import logging
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import Config
from shared.models.user import db
from app import create_app

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def migrate_add_multimodal_fields():
    """Add multimodal RAG fields to exam_category_questions table"""
    
    app = create_app()
    
    with app.app_context():
        logger.info("=" * 70)
        logger.info("🚀 Adding Multimodal RAG Fields to Database")
        logger.info("=" * 70)

        try:
            # Get database connection
            connection = db.engine.raw_connection()
            cursor = connection.cursor()

            # Check if columns already exist
            cursor.execute("""
                SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS 
                WHERE TABLE_NAME = 'exam_category_questions' 
                AND COLUMN_NAME IN (
                    'chromadb_collection',
                    'multimodal_source_type',
                    'image_references',
                    'clip_embedding_id',
                    'generation_method'
                )
            """)
            
            existing_columns = {row[0] for row in cursor.fetchall()}
            logger.info(f"Existing multimodal columns: {existing_columns if existing_columns else 'None'}")

            # Add chromadb_collection column
            if 'chromadb_collection' not in existing_columns:
                logger.info("Adding chromadb_collection column...")
                cursor.execute("""
                    ALTER TABLE exam_category_questions 
                    ADD COLUMN chromadb_collection VARCHAR(100) NULL
                """)
                logger.info("✅ chromadb_collection column added")

            # Add multimodal_source_type column
            if 'multimodal_source_type' not in existing_columns:
                logger.info("Adding multimodal_source_type column...")
                cursor.execute("""
                    ALTER TABLE exam_category_questions 
                    ADD COLUMN multimodal_source_type ENUM('text', 'image', 'mixed') DEFAULT 'text'
                """)
                logger.info("✅ multimodal_source_type column added")

            # Add image_references column
            if 'image_references' not in existing_columns:
                logger.info("Adding image_references column...")
                cursor.execute("""
                    ALTER TABLE exam_category_questions 
                    ADD COLUMN image_references JSON NULL
                """)
                logger.info("✅ image_references column added")

            # Add clip_embedding_id column
            if 'clip_embedding_id' not in existing_columns:
                logger.info("Adding clip_embedding_id column...")
                cursor.execute("""
                    ALTER TABLE exam_category_questions 
                    ADD COLUMN clip_embedding_id VARCHAR(255) NULL
                """)
                logger.info("✅ clip_embedding_id column added")

            # Add generation_method column
            if 'generation_method' not in existing_columns:
                logger.info("Adding generation_method column...")
                cursor.execute("""
                    ALTER TABLE exam_category_questions 
                    ADD COLUMN generation_method VARCHAR(50) DEFAULT 'multimodal_rag'
                """)
                logger.info("✅ generation_method column added")

            # Commit changes
            connection.commit()
            logger.info("\n✅ All multimodal RAG fields added successfully!")

            # Verify columns
            cursor.execute("""
                SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS 
                WHERE TABLE_NAME = 'exam_category_questions' 
                AND COLUMN_NAME IN (
                    'chromadb_collection',
                    'multimodal_source_type',
                    'image_references',
                    'clip_embedding_id',
                    'generation_method'
                )
            """)
            
            verified_columns = {row[0] for row in cursor.fetchall()}
            logger.info(f"\n✅ Verified columns: {verified_columns}")

            cursor.close()
            connection.close()

            logger.info("\n" + "=" * 70)
            logger.info("✅ Migration completed successfully!")
            logger.info("=" * 70)
            return True

        except Exception as e:
            logger.error(f"❌ Migration failed: {e}")
            logger.error("Rolling back changes...")
            try:
                connection.rollback()
            except:
                pass
            return False


if __name__ == "__main__":
    logger.info("Starting migration...")
    success = migrate_add_multimodal_fields()
    sys.exit(0 if success else 1)

