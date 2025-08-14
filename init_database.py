#!/usr/bin/env python3
"""
Initialize SQLite Database for StudyMate
Simple database setup for PDF storage
"""

import sqlite3
import os
from pathlib import Path

def create_database():
    """Create SQLite database with tables for PDF storage"""
    
    print("🗄️  INITIALIZING STUDYMATE DATABASE")
    print("=" * 50)
    
    # Database file path
    db_path = Path("studymate.db")
    
    # Remove existing database if it exists
    if db_path.exists():
        print(f"⚠️  Removing existing database: {db_path}")
        db_path.unlink()
    
    # Create new database
    print(f"📁 Creating database: {db_path}")
    
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    
    # Create users table
    cursor.execute('''
        CREATE TABLE users (
            id TEXT PRIMARY KEY,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            full_name TEXT,
            hashed_password TEXT NOT NULL,
            is_active BOOLEAN DEFAULT 1,
            is_superuser BOOLEAN DEFAULT 0,
            preferred_model TEXT DEFAULT 'granite-3b-code-instruct',
            settings TEXT DEFAULT '{}',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create documents table
    cursor.execute('''
        CREATE TABLE documents (
            id TEXT PRIMARY KEY,
            filename TEXT NOT NULL,
            original_filename TEXT NOT NULL,
            file_path TEXT NOT NULL,
            file_size INTEGER NOT NULL,
            file_type TEXT NOT NULL,
            mime_type TEXT,
            status TEXT DEFAULT 'uploaded',
            processing_error TEXT,
            total_pages INTEGER,
            total_words INTEGER,
            total_characters INTEGER,
            language TEXT,
            chunk_count INTEGER DEFAULT 0,
            processing_time REAL,
            owner_id TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (owner_id) REFERENCES users (id)
        )
    ''')
    
    # Create document_chunks table
    cursor.execute('''
        CREATE TABLE document_chunks (
            id TEXT PRIMARY KEY,
            chunk_index INTEGER NOT NULL,
            text TEXT NOT NULL,
            word_count INTEGER NOT NULL,
            character_count INTEGER NOT NULL,
            page_number INTEGER,
            embedding BLOB,
            embedding_model TEXT,
            faiss_index_id INTEGER,
            document_id TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (document_id) REFERENCES documents (id)
        )
    ''')
    
    # Create conversations table
    cursor.execute('''
        CREATE TABLE conversations (
            id TEXT PRIMARY KEY,
            title TEXT,
            message_count INTEGER DEFAULT 0,
            total_tokens INTEGER DEFAULT 0,
            user_id TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    # Create messages table
    cursor.execute('''
        CREATE TABLE messages (
            id TEXT PRIMARY KEY,
            role TEXT NOT NULL,
            content TEXT NOT NULL,
            token_count INTEGER,
            model_used TEXT,
            confidence_score REAL,
            processing_time REAL,
            generation_params TEXT,
            source_chunks TEXT,
            conversation_id TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (conversation_id) REFERENCES conversations (id)
        )
    ''')
    
    # Create indexes for better performance
    cursor.execute('CREATE INDEX idx_documents_owner ON documents(owner_id)')
    cursor.execute('CREATE INDEX idx_documents_status ON documents(status)')
    cursor.execute('CREATE INDEX idx_chunks_document ON document_chunks(document_id)')
    cursor.execute('CREATE INDEX idx_conversations_user ON conversations(user_id)')
    cursor.execute('CREATE INDEX idx_messages_conversation ON messages(conversation_id)')
    
    # No default users - all users must register through the application
    
    # Commit changes
    conn.commit()
    conn.close()
    
    print("✅ Database created successfully!")
    print(f"📊 Database file: {db_path.absolute()}")
    
    # Show table information
    print("\n📋 Created tables:")
    tables = [
        "users", "documents", "document_chunks", 
        "conversations", "messages"
    ]
    
    for table in tables:
        print(f"   📄 {table}")
    
    print("\n🎯 Database is ready for PDF storage!")
    
    return str(db_path.absolute())

def test_database():
    """Test database connection and operations"""
    print("\n🔍 TESTING DATABASE:")
    print("-" * 25)
    
    try:
        conn = sqlite3.connect("studymate.db")
        cursor = conn.cursor()
        
        # Test query
        cursor.execute("SELECT COUNT(*) FROM users")
        user_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM documents")
        doc_count = cursor.fetchone()[0]
        
        print(f"✅ Database connection successful")
        print(f"📊 Users: {user_count}")
        print(f"📊 Documents: {doc_count}")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Database test failed: {e}")
        return False

def show_usage():
    """Show how to use the database"""
    print("\n📚 HOW TO USE YOUR DATABASE:")
    print("=" * 40)
    
    print("1. 📤 STORE PDF FILES:")
    print("   • Upload through StudyMate web interface")
    print("   • Files metadata stored in 'documents' table")
    print("   • Text chunks stored in 'document_chunks' table")
    
    print("\n2. 🔍 ACCESS DATABASE:")
    print("   • SQLite browser tools (DB Browser for SQLite)")
    print("   • Python sqlite3 module")
    print("   • StudyMate database browser (http://localhost:8511)")
    
    print("\n3. 📊 DATABASE STRUCTURE:")
    print("   • users: User accounts and preferences")
    print("   • documents: PDF file metadata and status")
    print("   • document_chunks: Text chunks for AI processing")
    print("   • conversations: Chat history")
    print("   • messages: Individual chat messages")
    
    print("\n4. 🚀 NEXT STEPS:")
    print("   • Start StudyMate: streamlit run main.py")
    print("   • Upload PDF files through the web interface")
    print("   • Files will be automatically stored in database")

def main():
    """Main function"""
    try:
        # Create database
        db_path = create_database()
        
        # Test database
        if test_database():
            show_usage()
            
            print("\n🎉 DATABASE SETUP COMPLETE!")
            print("=" * 40)
            print("✅ SQLite database created and tested")
            print("✅ Ready to store PDF files and metadata")
            print(f"📁 Database location: {db_path}")
            
        else:
            print("❌ Database setup failed")
            
    except Exception as e:
        print(f"❌ Setup error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
