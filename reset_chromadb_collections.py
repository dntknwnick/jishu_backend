#!/usr/bin/env python3
"""
Reset ChromaDB collections to fix embedding function conflicts
Deletes all existing collections and recreates them properly
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import warnings
warnings.filterwarnings('ignore')

from app import create_app
import shutil

def reset_chromadb():
    """Reset ChromaDB by deleting and recreating collections"""
    
    app = create_app('development')
    
    with app.app_context():
        try:
            print("=" * 70)
            print("🔄 Resetting ChromaDB Collections")
            print("=" * 70)
            
            chromadb_path = app.config.get('MULTIMODAL_CHROMADB_PATH')
            
            print(f"\n📁 ChromaDB Path: {chromadb_path}")
            
            # Check if path exists
            if not os.path.exists(chromadb_path):
                print(f"❌ ChromaDB path does not exist: {chromadb_path}")
                return False
            
            # Backup the old data
            backup_path = chromadb_path + "_backup"
            if os.path.exists(backup_path):
                print(f"⚠️  Removing old backup: {backup_path}")
                shutil.rmtree(backup_path)
            
            print(f"\n📦 Backing up ChromaDB to: {backup_path}")
            shutil.copytree(chromadb_path, backup_path)
            print(f"✅ Backup created")
            
            # Delete the ChromaDB directory
            print(f"\n🗑️  Deleting ChromaDB directory...")
            shutil.rmtree(chromadb_path)
            print(f"✅ ChromaDB directory deleted")
            
            # Recreate the directory
            print(f"\n📁 Recreating ChromaDB directory...")
            os.makedirs(chromadb_path, exist_ok=True)
            print(f"✅ ChromaDB directory recreated")
            
            print("\n" + "=" * 70)
            print("✅ ChromaDB Reset Complete!")
            print("=" * 70)
            print("\n📝 Next Steps:")
            print("   1. Run: python scripts/initialize_multimodal_rag.py")
            print("   2. This will recreate collections with proper embedding functions")
            print("   3. Then restart the Flask application")
            print("\n💾 Backup saved at: " + backup_path)
            
            return True
            
        except Exception as e:
            print(f"\n❌ Error: {e}")
            import traceback
            traceback.print_exc()
            return False

if __name__ == '__main__':
    print("\n⚠️  WARNING: This will delete all ChromaDB collections!")
    print("A backup will be created at: chromadb_data_backup\n")
    
    response = input("Are you sure you want to continue? (yes/no): ").strip().lower()
    
    if response == 'yes':
        success = reset_chromadb()
        sys.exit(0 if success else 1)
    else:
        print("❌ Operation cancelled")
        sys.exit(1)

