#!/usr/bin/env python3
"""
StudyMate Database Browser - Web Interface
Access and explore your databases through a web interface
"""

import streamlit as st
import sys
import os
import json
from pathlib import Path
from typing import List, Dict, Any
import pandas as pd

# Add project root to path
sys.path.append('.')

def main():
    st.set_page_config(
        page_title="StudyMate Database Browser",
        page_icon="🗄️",
        layout="wide"
    )
    
    st.title("🗄️ StudyMate Database Browser")
    st.markdown("---")
    
    # Sidebar navigation
    st.sidebar.title("Database Explorer")
    option = st.sidebar.selectbox(
        "Choose database to explore:",
        ["File Storage", "Vector Database", "Backend State", "Upload New Document"]
    )
    
    if option == "File Storage":
        explore_file_storage()
    elif option == "Vector Database":
        explore_vector_database()
    elif option == "Backend State":
        explore_backend_state()
    elif option == "Upload New Document":
        upload_document()

def explore_file_storage():
    """Explore file-based storage"""
    st.header("📁 File-Based Storage Explorer")
    
    data_dirs = {
        'Uploads': Path('data/uploads'),
        'Processed': Path('data/processed'), 
        'Embeddings': Path('data/embeddings'),
        'Root Data': Path('data')
    }
    
    # Create tabs for each directory
    tabs = st.tabs(list(data_dirs.keys()))
    
    for i, (name, path) in enumerate(data_dirs.items()):
        with tabs[i]:
            st.subheader(f"📂 {name} Directory")
            st.code(f"Path: {path.absolute()}")
            
            if path.exists():
                files = list(path.glob('*'))
                
                if files:
                    # Create file information table
                    file_data = []
                    for file in files:
                        if file.is_file():
                            size_kb = file.stat().st_size / 1024
                            file_data.append({
                                'Filename': file.name,
                                'Size (KB)': f"{size_kb:.1f}",
                                'Type': file.suffix or 'No extension',
                                'Modified': file.stat().st_mtime
                            })
                    
                    if file_data:
                        df = pd.DataFrame(file_data)
                        st.dataframe(df, use_container_width=True)
                        
                        # File content preview
                        selected_file = st.selectbox(
                            f"Preview file from {name}:",
                            options=[f['Filename'] for f in file_data],
                            key=f"select_{name}"
                        )
                        
                        if selected_file and selected_file != '.gitkeep':
                            file_path = path / selected_file
                            preview_file_content(file_path)
                    else:
                        st.info("Directory contains no files")
                else:
                    st.info("Directory is empty")
            else:
                st.error("Directory not found")

def preview_file_content(file_path: Path):
    """Preview file content"""
    st.subheader(f"📄 File Preview: {file_path.name}")
    
    try:
        if file_path.suffix.lower() == '.pdf':
            st.info("PDF file detected. Content preview not available in browser.")
            st.markdown(f"**File size:** {file_path.stat().st_size / 1024:.1f} KB")
            
        elif file_path.suffix.lower() in ['.txt', '.json', '.md']:
            content = file_path.read_text(encoding='utf-8')
            if len(content) > 5000:
                st.warning("Large file - showing first 5000 characters")
                content = content[:5000] + "\n... (truncated)"
            
            st.text_area("File Content:", content, height=300)
            
        elif file_path.suffix.lower() in ['.pkl', '.pickle']:
            st.info("Pickle file detected. Binary content cannot be displayed.")
            try:
                import pickle
                with open(file_path, 'rb') as f:
                    data = pickle.load(f)
                st.json({"type": str(type(data)), "info": "Pickle file loaded successfully"})
            except Exception as e:
                st.error(f"Error loading pickle file: {e}")
                
        else:
            st.info(f"File type {file_path.suffix} - Preview not available")
            
    except Exception as e:
        st.error(f"Error reading file: {e}")

def explore_vector_database():
    """Explore FAISS vector database"""
    st.header("🔍 Vector Database Explorer")
    
    try:
        from backend.vector_database import VectorDatabase
        from backend.config import config
        
        st.success("✅ Vector database module loaded")
        
        # Show configuration
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Index Type", config.FAISS_INDEX_TYPE)
        with col2:
            st.metric("Embedding Dimension", config.EMBEDDING_DIMENSION)
        
        # Initialize vector database
        vector_db = VectorDatabase()
        
        if vector_db.load_index():
            st.success("✅ FAISS index loaded successfully")
            
            # Show database stats
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Documents", len(vector_db.documents))
            with col2:
                st.metric("Index Trained", vector_db.is_trained)
            with col3:
                st.metric("Dimension", vector_db.dimension)
            
            # Show document samples
            if vector_db.documents:
                st.subheader("📋 Document Samples")
                
                for i, doc in enumerate(vector_db.documents[:5]):
                    with st.expander(f"Document {i+1}"):
                        if isinstance(doc, dict):
                            st.json(doc)
                        else:
                            st.text(str(doc)[:500] + "..." if len(str(doc)) > 500 else str(doc))
            else:
                st.info("No documents found in vector database")
                
        else:
            st.warning("❌ No FAISS index found - database is empty")
            st.info("Upload some documents through the main StudyMate app to populate the database")
            
    except Exception as e:
        st.error(f"❌ Vector database error: {e}")

def explore_backend_state():
    """Explore backend state"""
    st.header("🔧 Backend State Explorer")
    
    try:
        from backend.manager import StudyMateBackend
        
        st.success("✅ Backend manager loaded")
        
        # Initialize backend
        with st.spinner("Initializing backend..."):
            backend = StudyMateBackend()
        
        # Check components
        components = {
            "Vector Database": hasattr(backend, 'vector_db') and backend.vector_db is not None,
            "Model Manager": hasattr(backend, 'model_manager'),
            "QA Engine": hasattr(backend, 'qa_engine'),
            "Embedding Model": hasattr(backend, 'embedding_model')
        }
        
        # Display component status
        col1, col2 = st.columns(2)
        for i, (component, status) in enumerate(components.items()):
            with col1 if i % 2 == 0 else col2:
                if status:
                    st.success(f"✅ {component}")
                else:
                    st.error(f"❌ {component}")
        
        # Show detailed information
        if hasattr(backend, 'model_manager'):
            st.subheader("🤖 Model Manager Details")
            st.info(f"Device: {backend.model_manager.device}")
            
        # Interactive query section
        st.subheader("💬 Interactive Query")
        
        query_type = st.selectbox("Query Type:", ["Search Documents", "Ask Question"])
        query_input = st.text_input("Enter your query:")
        
        if st.button("Execute Query") and query_input:
            with st.spinner("Processing query..."):
                try:
                    if query_type == "Search Documents":
                        results = backend.search_documents(query_input, top_k=5)
                        if results:
                            st.success(f"Found {len(results)} results:")
                            for i, result in enumerate(results):
                                with st.expander(f"Result {i+1} (Score: {result.get('score', 'N/A')})"):
                                    st.text(result.get('text', 'N/A'))
                        else:
                            st.warning("No results found")
                            
                    elif query_type == "Ask Question":
                        answer = backend.get_answer(query_input)
                        st.success("Answer:")
                        st.write(answer)
                        
                except Exception as e:
                    st.error(f"Query error: {e}")
                    
    except Exception as e:
        st.error(f"❌ Backend exploration error: {e}")

def upload_document():
    """Upload and process new document"""
    st.header("📤 Upload New Document")
    
    uploaded_file = st.file_uploader(
        "Choose a file to upload",
        type=['pdf', 'txt', 'docx'],
        help="Upload a document to add to the database"
    )
    
    if uploaded_file is not None:
        # Save uploaded file
        upload_dir = Path('data/uploads')
        upload_dir.mkdir(exist_ok=True)
        
        file_path = upload_dir / uploaded_file.name
        
        with open(file_path, 'wb') as f:
            f.write(uploaded_file.getbuffer())
        
        st.success(f"✅ File uploaded: {uploaded_file.name}")
        st.info(f"File saved to: {file_path}")
        
        # Process the document
        if st.button("Process Document"):
            with st.spinner("Processing document..."):
                try:
                    from backend.manager import StudyMateBackend
                    backend = StudyMateBackend()
                    
                    # Process the document
                    result = backend.process_document(str(file_path))
                    
                    if result:
                        st.success("✅ Document processed successfully!")
                        st.json(result)
                    else:
                        st.error("❌ Document processing failed")
                        
                except Exception as e:
                    st.error(f"Processing error: {e}")

if __name__ == "__main__":
    main()
