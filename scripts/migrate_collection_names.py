#!/usr/bin/env python3
"""
Migration script to update ChromaDB collection names from old format to new format
Old format: physics, chemistry, biology, mathematics
New format: subject_physics, subject_chemistry, subject_biology, subject_mathematics
"""

import sys
import os
import logging

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def migrate_collection_names():
    """Migrate old collection names to new naming convention"""
    try:
        import chromadb
        
        print("🔄 Starting ChromaDB collection name migration...")
        
        # Connect to ChromaDB
        client = chromadb.PersistentClient(path='./vector_stores')
        
        # List all existing collections
        collections = client.list_collections()
        print(f"📊 Found {len(collections)} existing collections")
        
        # Define subjects and their expected naming
        subjects = ['physics', 'chemistry', 'biology', 'mathematics', 'computer_science']
        
        for subject in subjects:
            old_name = subject
            new_name = f"subject_{subject}"
            
            # Check if old collection exists
            old_exists = any(col.name == old_name for col in collections)
            new_exists = any(col.name == new_name for col in collections)
            
            print(f"\n📚 Processing {subject}:")
            print(f"  - Old format ({old_name}): {'✅ EXISTS' if old_exists else '❌ NOT FOUND'}")
            print(f"  - New format ({new_name}): {'✅ EXISTS' if new_exists else '❌ NOT FOUND'}")
            
            if old_exists and not new_exists:
                # Migrate from old to new
                print(f"🔄 Migrating {old_name} → {new_name}")
                
                try:
                    # Get the old collection
                    old_collection = client.get_collection(old_name)
                    old_count = old_collection.count()
                    print(f"  - Old collection has {old_count} documents")
                    
                    if old_count > 0:
                        # Get all data from old collection
                        all_data = old_collection.get(include=['documents', 'metadatas', 'embeddings'])
                        
                        # Create new collection
                        new_collection = client.create_collection(new_name)
                        
                        # Add all data to new collection
                        new_collection.add(
                            ids=all_data['ids'],
                            documents=all_data['documents'],
                            metadatas=all_data['metadatas'],
                            embeddings=all_data['embeddings']
                        )
                        
                        new_count = new_collection.count()
                        print(f"  - New collection created with {new_count} documents")
                        
                        # Verify migration
                        if new_count == old_count:
                            # Delete old collection
                            client.delete_collection(old_name)
                            print(f"  - ✅ Migration successful! Old collection deleted.")
                        else:
                            print(f"  - ❌ Migration failed! Document count mismatch: {old_count} → {new_count}")
                    else:
                        # Empty collection, just create new one and delete old
                        client.create_collection(new_name)
                        client.delete_collection(old_name)
                        print(f"  - ✅ Empty collection migrated successfully")
                        
                except Exception as e:
                    print(f"  - ❌ Migration failed: {str(e)}")
                    
            elif old_exists and new_exists:
                # Both exist - check which one to keep
                old_collection = client.get_collection(old_name)
                new_collection = client.get_collection(new_name)
                old_count = old_collection.count()
                new_count = new_collection.count()
                
                print(f"  - Both collections exist: old={old_count}, new={new_count}")
                
                if new_count >= old_count:
                    # Keep new, delete old
                    client.delete_collection(old_name)
                    print(f"  - ✅ Kept new collection, deleted old one")
                else:
                    print(f"  - ⚠️ Old collection has more data. Manual review needed.")
                    
            elif not old_exists and new_exists:
                print(f"  - ✅ Already using new naming convention")
                
            else:
                print(f"  - ⚠️ No collection found for {subject}")
        
        # Final status
        print(f"\n🎉 Migration completed!")
        
        # List final collections
        final_collections = client.list_collections()
        print(f"\n📊 Final collections:")
        for col in final_collections:
            print(f"  - {col.name}: {col.count()} documents")
            
        return True
        
    except Exception as e:
        print(f"❌ Migration failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = migrate_collection_names()
    if success:
        print("\n✅ Collection name migration completed successfully!")
    else:
        print("\n❌ Collection name migration failed!")
        sys.exit(1)
