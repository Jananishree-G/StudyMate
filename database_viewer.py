#!/usr/bin/env python3
"""
StudyMate Database Viewer
View and interact with your SQLite database
"""

import streamlit as st
import sqlite3
import pandas as pd
from pathlib import Path
import json
from datetime import datetime

def main():
    st.set_page_config(
        page_title="StudyMate Database Viewer",
        page_icon="🗄️",
        layout="wide"
    )
    
    st.title("🗄️ StudyMate Database Viewer")
    st.markdown("---")
    
    # Check if database exists
    db_path = Path("studymate.db")
    if not db_path.exists():
        st.error("❌ Database not found! Please run `python init_database.py` first.")
        return
    
    st.success(f"✅ Connected to database: {db_path.absolute()}")
    
    # Sidebar navigation
    st.sidebar.title("Database Tables")
    
    # Get table list
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [row[0] for row in cursor.fetchall()]
    conn.close()
    
    selected_table = st.sidebar.selectbox("Select table to view:", tables)
    
    # Main content
    if selected_table:
        show_table_data(selected_table, db_path)
    
    # Database statistics
    st.sidebar.markdown("---")
    st.sidebar.subheader("📊 Database Stats")
    show_database_stats(db_path)

def show_table_data(table_name: str, db_path: Path):
    """Show data from selected table"""
    st.header(f"📄 Table: {table_name}")
    
    try:
        conn = sqlite3.connect(str(db_path))
        
        # Get table schema
        cursor = conn.cursor()
        cursor.execute(f"PRAGMA table_info({table_name})")
        schema = cursor.fetchall()
        
        # Show schema
        with st.expander("🔍 Table Schema"):
            schema_df = pd.DataFrame(schema, columns=['ID', 'Name', 'Type', 'NotNull', 'Default', 'PK'])
            st.dataframe(schema_df, use_container_width=True)
        
        # Get data
        df = pd.read_sql_query(f"SELECT * FROM {table_name}", conn)
        
        # Show record count
        st.metric("Total Records", len(df))
        
        if len(df) > 0:
            # Show data
            st.subheader("📋 Table Data")
            st.dataframe(df, use_container_width=True)
            
            # Show specific actions based on table
            if table_name == "documents":
                show_document_actions(df, conn)
            elif table_name == "users":
                show_user_actions(df, conn)
            elif table_name == "document_chunks":
                show_chunk_actions(df, conn)
        else:
            st.info("📭 No records found in this table")
        
        conn.close()
        
    except Exception as e:
        st.error(f"❌ Error accessing table: {e}")

def show_document_actions(df: pd.DataFrame, conn: sqlite3.Connection):
    """Show document-specific actions"""
    st.subheader("📄 Document Actions")
    
    if len(df) > 0:
        # Document selector
        doc_options = [f"{row['filename']} ({row['id'][:8]}...)" for _, row in df.iterrows()]
        selected_doc = st.selectbox("Select document:", doc_options)
        
        if selected_doc:
            doc_index = doc_options.index(selected_doc)
            doc_row = df.iloc[doc_index]
            
            # Show document details
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("File Size", f"{doc_row['file_size']:,} bytes")
            with col2:
                st.metric("Status", doc_row['status'])
            with col3:
                st.metric("Chunks", doc_row['chunk_count'])
            
            # Show document chunks
            if st.button("View Document Chunks"):
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM document_chunks WHERE document_id = ?", (doc_row['id'],))
                chunks = cursor.fetchall()
                
                if chunks:
                    st.write(f"📋 Found {len(chunks)} chunks:")
                    for i, chunk in enumerate(chunks[:5]):  # Show first 5 chunks
                        with st.expander(f"Chunk {i+1}"):
                            st.text(chunk[2][:500] + "..." if len(chunk[2]) > 500 else chunk[2])
                else:
                    st.info("No chunks found for this document")

def show_user_actions(df: pd.DataFrame, conn: sqlite3.Connection):
    """Show user-specific actions"""
    st.subheader("👤 User Actions")
    
    if len(df) > 0:
        # User selector
        user_options = [f"{row['username']} ({row['email']})" for _, row in df.iterrows()]
        selected_user = st.selectbox("Select user:", user_options)
        
        if selected_user:
            user_index = user_options.index(selected_user)
            user_row = df.iloc[user_index]
            
            # Show user details
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Active", "✅" if user_row['is_active'] else "❌")
            with col2:
                st.metric("Superuser", "✅" if user_row['is_superuser'] else "❌")
            with col3:
                st.metric("Preferred Model", user_row['preferred_model'])
            
            # Show user's documents
            if st.button("View User's Documents"):
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM documents WHERE owner_id = ?", (user_row['id'],))
                docs = cursor.fetchall()
                
                if docs:
                    st.write(f"📄 Found {len(docs)} documents:")
                    doc_df = pd.DataFrame(docs, columns=[
                        'id', 'filename', 'original_filename', 'file_path', 'file_size',
                        'file_type', 'mime_type', 'status', 'processing_error',
                        'total_pages', 'total_words', 'total_characters', 'language',
                        'chunk_count', 'processing_time', 'owner_id', 'created_at', 'updated_at'
                    ])
                    st.dataframe(doc_df[['filename', 'file_size', 'status', 'chunk_count']], use_container_width=True)
                else:
                    st.info("No documents found for this user")

def show_chunk_actions(df: pd.DataFrame, conn: sqlite3.Connection):
    """Show chunk-specific actions"""
    st.subheader("📝 Chunk Actions")
    
    if len(df) > 0:
        # Show chunk statistics
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Chunks", len(df))
        with col2:
            st.metric("Avg Word Count", f"{df['word_count'].mean():.0f}")
        with col3:
            st.metric("Total Words", f"{df['word_count'].sum():,}")
        
        # Search chunks
        search_query = st.text_input("🔍 Search in chunks:")
        if search_query:
            filtered_df = df[df['text'].str.contains(search_query, case=False, na=False)]
            st.write(f"Found {len(filtered_df)} matching chunks:")
            
            for _, chunk in filtered_df.head(10).iterrows():  # Show first 10 matches
                with st.expander(f"Chunk {chunk['chunk_index']} (Document: {chunk['document_id'][:8]}...)"):
                    # Highlight search term
                    text = chunk['text']
                    highlighted = text.replace(search_query, f"**{search_query}**")
                    st.markdown(highlighted)

def show_database_stats(db_path: Path):
    """Show database statistics in sidebar"""
    try:
        conn = sqlite3.connect(str(db_path))
        
        # Get table counts
        tables = ['users', 'documents', 'document_chunks', 'conversations', 'messages']
        
        for table in tables:
            try:
                cursor = conn.cursor()
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                count = cursor.fetchone()[0]
                st.sidebar.metric(f"{table.title()}", count)
            except:
                st.sidebar.metric(f"{table.title()}", "N/A")
        
        # Database size
        db_size = db_path.stat().st_size / 1024  # KB
        st.sidebar.metric("Database Size", f"{db_size:.1f} KB")
        
        conn.close()
        
    except Exception as e:
        st.sidebar.error(f"Stats error: {e}")

def add_sample_data():
    """Add sample data for testing"""
    st.sidebar.markdown("---")
    st.sidebar.subheader("🧪 Testing")
    
    if st.sidebar.button("Add Sample Document"):
        try:
            conn = sqlite3.connect("studymate.db")
            cursor = conn.cursor()
            
            # Add sample document
            doc_id = f"sample-doc-{datetime.now().strftime('%Y%m%d%H%M%S')}"
            cursor.execute('''
                INSERT INTO documents (
                    id, filename, original_filename, file_path, file_size,
                    file_type, status, owner_id
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                doc_id, "sample.pdf", "Sample Document.pdf", "/data/uploads/sample.pdf",
                1024000, "pdf", "uploaded", "default-user-id"
            ))
            
            # Add sample chunks
            for i in range(3):
                chunk_id = f"chunk-{doc_id}-{i}"
                cursor.execute('''
                    INSERT INTO document_chunks (
                        id, chunk_index, text, word_count, character_count, document_id
                    ) VALUES (?, ?, ?, ?, ?, ?)
                ''', (
                    chunk_id, i, f"This is sample text chunk {i+1} for testing purposes.",
                    10, 50, doc_id
                ))
            
            # Update document chunk count
            cursor.execute('UPDATE documents SET chunk_count = 3 WHERE id = ?', (doc_id,))
            
            conn.commit()
            conn.close()
            
            st.sidebar.success("✅ Sample data added!")
            st.rerun()
            
        except Exception as e:
            st.sidebar.error(f"❌ Error: {e}")

if __name__ == "__main__":
    main()
    add_sample_data()
