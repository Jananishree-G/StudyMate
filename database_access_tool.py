#!/usr/bin/env python3
"""
StudyMate Database Access Tool
Interactive tool to access and explore databases
"""

import sys
import os
import json
import pickle
from pathlib import Path
from typing import List, Dict, Any

def explore_file_storage():
    """Explore file-based storage"""
    print("📁 FILE-BASED STORAGE EXPLORER")
    print("=" * 50)
    
    data_dirs = {
        'uploads': Path('data/uploads'),
        'processed': Path('data/processed'), 
        'embeddings': Path('data/embeddings'),
        'root_data': Path('data')
    }
    
    for name, path in data_dirs.items():
        print(f"\n📂 {name.upper()} Directory: {path}")
        if path.exists():
            files = list(path.glob('*'))
            print(f"   Files: {len(files)}")
            
            for file in files[:5]:  # Show first 5 files
                size = file.stat().st_size / 1024  # KB
                print(f"   📄 {file.name} ({size:.1f} KB)")
                
                # Try to read file content preview
                if file.suffix in ['.txt', '.json']:
                    try:
                        content = file.read_text()[:200]
                        print(f"      Preview: {content[:100]}...")
                    except:
                        print("      Preview: [Binary/Unreadable]")
                elif file.suffix in ['.pkl', '.pickle']:
                    print("      Type: Pickle file (Python object)")
                elif file.suffix == '.faiss':
                    print("      Type: FAISS index file")
                    
            if len(files) > 5:
                print(f"   ... and {len(files) - 5} more files")
        else:
            print("   ❌ Directory not found")

def explore_vector_database():
    """Explore FAISS vector database"""
    print("\n🔍 VECTOR DATABASE EXPLORER")
    print("=" * 50)
    
    try:
        sys.path.append('.')
        from backend.vector_database import VectorDatabase
        from backend.config import config
        
        print("✅ Vector database module loaded")
        
        # Initialize vector database
        vector_db = VectorDatabase()
        
        # Check if index exists
        if vector_db.load_index():
            print(f"✅ FAISS index loaded successfully")
            print(f"   Index type: {config.FAISS_INDEX_TYPE}")
            print(f"   Embedding dimension: {config.EMBEDDING_DIMENSION}")
            print(f"   Total documents: {len(vector_db.documents)}")
            print(f"   Index trained: {vector_db.is_trained}")
            
            # Show some document metadata
            if vector_db.documents:
                print(f"\n📋 DOCUMENT SAMPLES:")
                for i, doc in enumerate(vector_db.documents[:3]):
                    print(f"   Document {i+1}:")
                    if isinstance(doc, dict):
                        for key, value in doc.items():
                            if isinstance(value, str) and len(value) > 100:
                                value = value[:100] + "..."
                            print(f"      {key}: {value}")
                    else:
                        print(f"      Content: {str(doc)[:100]}...")
                    print()
        else:
            print("❌ No FAISS index found - database is empty")
            
    except Exception as e:
        print(f"❌ Vector database error: {e}")

def explore_backend_state():
    """Explore backend state and loaded data"""
    print("\n🔧 BACKEND STATE EXPLORER")
    print("=" * 50)
    
    try:
        from backend.manager import StudyMateBackend
        
        print("✅ Backend manager loaded")
        
        # Initialize backend
        backend = StudyMateBackend()
        
        # Check vector database state
        if hasattr(backend, 'vector_db') and backend.vector_db:
            print("✅ Vector database initialized in backend")
            
            # Check if documents are loaded
            if hasattr(backend.vector_db, 'documents'):
                doc_count = len(backend.vector_db.documents)
                print(f"   Loaded documents: {doc_count}")
                
                if doc_count > 0:
                    print("   Sample document keys:")
                    sample_doc = backend.vector_db.documents[0]
                    if isinstance(sample_doc, dict):
                        for key in list(sample_doc.keys())[:5]:
                            print(f"      - {key}")
        else:
            print("❌ Vector database not initialized in backend")
            
        # Check model manager
        if hasattr(backend, 'model_manager'):
            print("✅ Model manager available")
            print(f"   Device: {backend.model_manager.device}")
            
        # Check QA engine
        if hasattr(backend, 'qa_engine'):
            print("✅ QA engine available")
            
    except Exception as e:
        print(f"❌ Backend exploration error: {e}")

def interactive_database_query():
    """Interactive database query interface"""
    print("\n💬 INTERACTIVE DATABASE QUERY")
    print("=" * 50)
    
    try:
        from backend.manager import StudyMateBackend
        backend = StudyMateBackend()
        
        print("✅ Backend ready for queries")
        print("Commands:")
        print("  'search <query>' - Search documents")
        print("  'ask <question>' - Ask a question")
        print("  'docs' - List all documents")
        print("  'stats' - Show database statistics")
        print("  'quit' - Exit")
        
        while True:
            try:
                command = input("\n🔍 Query> ").strip()
                
                if command.lower() == 'quit':
                    break
                elif command.lower() == 'docs':
                    if hasattr(backend, 'vector_db') and backend.vector_db.documents:
                        print(f"📚 Total documents: {len(backend.vector_db.documents)}")
                        for i, doc in enumerate(backend.vector_db.documents[:5]):
                            if isinstance(doc, dict) and 'filename' in doc:
                                print(f"   {i+1}. {doc['filename']}")
                            else:
                                print(f"   {i+1}. Document {i+1}")
                    else:
                        print("❌ No documents found")
                        
                elif command.lower() == 'stats':
                    if hasattr(backend, 'vector_db'):
                        vdb = backend.vector_db
                        print(f"📊 Database Statistics:")
                        print(f"   Documents: {len(vdb.documents) if vdb.documents else 0}")
                        print(f"   Index trained: {vdb.is_trained if hasattr(vdb, 'is_trained') else 'Unknown'}")
                        print(f"   Dimension: {vdb.dimension if hasattr(vdb, 'dimension') else 'Unknown'}")
                        
                elif command.startswith('search '):
                    query = command[7:]  # Remove 'search '
                    print(f"🔍 Searching for: '{query}'")
                    
                    # Perform search
                    results = backend.search_documents(query, top_k=3)
                    if results:
                        print(f"📋 Found {len(results)} results:")
                        for i, result in enumerate(results):
                            print(f"   {i+1}. Score: {result.get('score', 'N/A')}")
                            print(f"      Text: {result.get('text', 'N/A')[:100]}...")
                    else:
                        print("❌ No results found")
                        
                elif command.startswith('ask '):
                    question = command[4:]  # Remove 'ask '
                    print(f"❓ Question: '{question}'")
                    
                    # Get answer
                    try:
                        answer = backend.get_answer(question)
                        print(f"💡 Answer: {answer}")
                    except Exception as e:
                        print(f"❌ Error getting answer: {e}")
                        
                else:
                    print("❌ Unknown command. Type 'quit' to exit.")
                    
            except KeyboardInterrupt:
                print("\n👋 Exiting...")
                break
            except Exception as e:
                print(f"❌ Error: {e}")
                
    except Exception as e:
        print(f"❌ Interactive query setup error: {e}")

def main():
    """Main database access interface"""
    print("🗄️  STUDYMATE DATABASE ACCESS TOOL")
    print("=" * 60)
    
    print("Available database access options:")
    print("1. Explore file-based storage")
    print("2. Explore vector database (FAISS)")
    print("3. Explore backend state")
    print("4. Interactive database query")
    print("5. Show all information")
    print("0. Exit")
    
    while True:
        try:
            choice = input("\nSelect option (0-5): ").strip()
            
            if choice == '0':
                print("👋 Goodbye!")
                break
            elif choice == '1':
                explore_file_storage()
            elif choice == '2':
                explore_vector_database()
            elif choice == '3':
                explore_backend_state()
            elif choice == '4':
                interactive_database_query()
            elif choice == '5':
                explore_file_storage()
                explore_vector_database()
                explore_backend_state()
            else:
                print("❌ Invalid choice. Please select 0-5.")
                
        except KeyboardInterrupt:
            print("\n👋 Exiting...")
            break
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()
