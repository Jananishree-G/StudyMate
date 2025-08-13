"""
Main Streamlit application for StudyMate
"""

import streamlit as st
import sys
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent.parent / "src"))

from config import config
from pdf_processor import PDFProcessor
from embeddings import EmbeddingManager
from qa_engine import QAEngine

# Import components
from frontend.components.sidebar import render_sidebar
from frontend.components.file_uploader import render_file_uploader, display_file_stats, clear_uploaded_files
from frontend.components.chat_interface import (
    initialize_chat, render_chat_interface, render_sample_questions,
    display_chat_stats
)

def initialize_session_state():
    """Initialize session state variables"""
    if 'current_page' not in st.session_state:
        st.session_state.current_page = "home"
    
    if 'pdf_processor' not in st.session_state:
        st.session_state.pdf_processor = PDFProcessor()
    
    if 'embedding_manager' not in st.session_state:
        st.session_state.embedding_manager = EmbeddingManager()
    
    initialize_chat()

def render_home_page():
    """Render the home page"""
    st.title(f"{config.APP_ICON} Welcome to StudyMate")
    st.markdown("### Your AI-Powered Academic Assistant")
    
    st.markdown("""
    StudyMate helps you interact with your study materials through conversational Q&A. 
    Upload your PDFs and start asking questions to get instant, contextual answers.
    """)
    
    # Features
    st.subheader("✨ Features")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        **📚 Smart Document Processing**
        - Extract text from multiple PDFs
        - Intelligent text chunking
        - Metadata preservation
        
        **🔍 Semantic Search**
        - FAISS-powered vector search
        - Context-aware retrieval
        - Relevance scoring
        """)
    
    with col2:
        st.markdown("""
        **🤖 AI-Powered Answers**
        - IBM Watsonx integration
        - Contextual responses
        - Source attribution
        
        **💬 Interactive Chat**
        - Natural language queries
        - Conversation history
        - Export capabilities
        """)
    
    # Getting started
    st.subheader("🚀 Getting Started")
    
    steps = [
        "Upload your PDF study materials",
        "Wait for processing to complete",
        "Start asking questions in the chat",
        "Review sources and explore further"
    ]
    
    for i, step in enumerate(steps, 1):
        st.markdown(f"**{i}.** {step}")
    
    # Quick actions
    st.subheader("⚡ Quick Actions")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📁 Upload Documents", type="primary"):
            st.session_state.current_page = "upload"
            st.rerun()
    
    with col2:
        if st.button("💬 Start Chatting"):
            st.session_state.current_page = "chat"
            st.rerun()
    
    with col3:
        if st.button("📊 View Analytics"):
            st.session_state.current_page = "analytics"
            st.rerun()

def render_upload_page():
    """Render the document upload page"""
    st.title("📁 Upload Study Materials")
    
    # File uploader
    uploaded_file_paths = render_file_uploader()
    
    if uploaded_file_paths:
        st.session_state.uploaded_files = uploaded_file_paths
        
        # Display file stats
        display_file_stats(uploaded_file_paths)
        
        # Process documents
        if st.button("🔄 Process Documents", type="primary"):
            process_documents(uploaded_file_paths)

def process_documents(file_paths):
    """Process uploaded documents"""
    try:
        # Process PDFs
        st.subheader("📝 Processing Documents")
        processed_pdfs = st.session_state.pdf_processor.process_multiple_pdfs(file_paths)
        
        if not processed_pdfs:
            st.error("Failed to process documents")
            return
        
        st.session_state.processed_pdfs = processed_pdfs
        
        # Display processing stats
        stats = st.session_state.pdf_processor.get_processing_stats(processed_pdfs)
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Files Processed", stats['total_files'])
        with col2:
            st.metric("Total Pages", stats['total_pages'])
        with col3:
            st.metric("Total Words", f"{stats['total_words']:,}")
        with col4:
            st.metric("Avg Words/File", f"{stats['average_words_per_file']:.0f}")
        
        # Create text chunks
        st.subheader("🔍 Building Search Index")
        chunks = st.session_state.pdf_processor.create_chunks_from_multiple_pdfs(processed_pdfs)
        
        # Build embeddings index
        if st.session_state.embedding_manager.build_index_from_chunks(chunks):
            st.success(f"✅ Successfully built search index with {len(chunks)} text chunks")
            
            # Display index stats
            index_stats = st.session_state.embedding_manager.get_index_stats()
            st.info(f"🔍 Index ready with {index_stats['total_vectors']} vectors")
            
            # Suggest next steps
            st.subheader("🎉 Ready to Go!")
            st.markdown("Your documents have been processed successfully. You can now:")
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("💬 Start Asking Questions", type="primary"):
                    st.session_state.current_page = "chat"
                    st.rerun()
            
            with col2:
                if st.button("📊 View Analytics"):
                    st.session_state.current_page = "analytics"
                    st.rerun()
        
        else:
            st.error("Failed to build search index")
    
    except Exception as e:
        st.error(f"Error processing documents: {str(e)}")

def render_chat_page():
    """Render the chat page"""
    st.title("💬 Chat with Your Study Materials")
    
    # Check if ready for chat
    if 'embedding_manager' not in st.session_state or st.session_state.embedding_manager.index is None:
        st.warning("⚠️ Please upload and process documents first.")
        
        if st.button("📁 Go to Upload Page"):
            st.session_state.current_page = "upload"
            st.rerun()
        return
    
    # Render chat interface
    render_chat_interface()
    
    # Sample questions (if no chat history)
    if not st.session_state.get('messages', []):
        render_sample_questions()

def render_analytics_page():
    """Render the analytics page"""
    st.title("📊 Analytics & Insights")
    
    # Document analytics
    if 'processed_pdfs' in st.session_state and st.session_state.processed_pdfs:
        render_document_analytics()
    
    # Chat analytics
    if 'messages' in st.session_state and st.session_state.messages:
        render_chat_analytics()
    
    # Index analytics
    if 'embedding_manager' in st.session_state and st.session_state.embedding_manager.index is not None:
        render_index_analytics()

def render_document_analytics():
    """Render document analytics"""
    st.subheader("📚 Document Analytics")
    
    processed_pdfs = st.session_state.processed_pdfs
    stats = st.session_state.pdf_processor.get_processing_stats(processed_pdfs)
    
    # Overview metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Documents", stats['total_files'])
    
    with col2:
        st.metric("Total Pages", stats['total_pages'])
    
    with col3:
        st.metric("Total Words", f"{stats['total_words']:,}")
    
    with col4:
        st.metric("Total Characters", f"{stats['total_characters']:,}")
    
    # Document details
    with st.expander("📋 Document Details"):
        for pdf in processed_pdfs:
            metadata = pdf['metadata']
            st.markdown(f"**{metadata['filename']}**")
            st.write(f"- Pages: {metadata['total_pages']}")
            st.write(f"- Words: {metadata['total_words']:,}")
            st.write(f"- Characters: {metadata['total_characters']:,}")
            if metadata.get('title'):
                st.write(f"- Title: {metadata['title']}")
            st.markdown("---")

def render_chat_analytics():
    """Render chat analytics"""
    st.subheader("💬 Chat Analytics")
    
    display_chat_stats()
    
    # Recent questions
    messages = st.session_state.messages
    user_messages = [m for m in messages if m["role"] == "user"]
    
    if user_messages:
        st.subheader("❓ Recent Questions")
        for i, message in enumerate(reversed(user_messages[-5:]), 1):
            st.write(f"{i}. {message['content']}")

def render_index_analytics():
    """Render search index analytics"""
    st.subheader("🔍 Search Index Analytics")
    
    stats = st.session_state.embedding_manager.get_index_stats()
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total Vectors", stats.get('total_vectors', 0))
    
    with col2:
        st.metric("Embedding Dimension", stats.get('embedding_dimension', 0))
    
    with col3:
        st.metric("Total Chunks", stats.get('total_chunks', 0))
    
    st.write(f"**Model:** {stats.get('model_name', 'Unknown')}")
    st.write(f"**Index Type:** {stats.get('index_type', 'Unknown')}")

def render_settings_page():
    """Render the settings page"""
    st.title("⚙️ Settings")
    
    # Configuration display
    st.subheader("🔧 Current Configuration")
    
    config_data = {
        "Watson Model": config.WATSONX_MODEL_ID,
        "Embedding Model": config.HUGGINGFACE_MODEL,
        "Max Tokens": config.MAX_TOKENS,
        "Temperature": config.TEMPERATURE,
        "Chunk Size": config.CHUNK_SIZE,
        "Chunk Overlap": config.CHUNK_OVERLAP,
        "Max File Size": f"{config.MAX_FILE_SIZE_MB} MB",
        "Max Files": config.MAX_FILES_UPLOAD
    }
    
    for key, value in config_data.items():
        st.write(f"**{key}:** {value}")
    
    # Data management
    st.subheader("🗂️ Data Management")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🗑️ Clear All Data", type="secondary"):
            clear_all_data()
    
    with col2:
        if st.button("💾 Export Data"):
            export_data()

def clear_all_data():
    """Clear all application data"""
    clear_uploaded_files()
    st.success("✅ All data cleared!")

def export_data():
    """Export application data"""
    st.info("Export functionality coming soon!")

def main():
    """Main application function"""
    # Initialize
    initialize_session_state()
    
    # Render sidebar
    render_sidebar()
    
    # Render main content based on current page
    current_page = st.session_state.current_page
    
    if current_page == "home":
        render_home_page()
    elif current_page == "upload":
        render_upload_page()
    elif current_page == "chat":
        render_chat_page()
    elif current_page == "analytics":
        render_analytics_page()
    elif current_page == "settings":
        render_settings_page()
    else:
        render_home_page()

if __name__ == "__main__":
    main()
