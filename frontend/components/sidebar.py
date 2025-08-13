"""
Sidebar component for StudyMate
"""

import streamlit as st
from pathlib import Path
import sys

# Add src to path
sys.path.append(str(Path(__file__).parent.parent.parent / "src"))

from config import config

def render_sidebar():
    """Render the main sidebar"""
    with st.sidebar:
        # App header
        st.title(f"{config.APP_ICON} StudyMate")
        st.markdown("*AI-Powered Academic Assistant*")
        st.markdown("---")
        
        # Navigation
        render_navigation()
        
        # Document status
        render_document_status()
        
        # Settings
        render_settings()
        
        # Help and info
        render_help_section()

def render_navigation():
    """Render navigation menu"""
    st.subheader("📋 Navigation")
    
    # Page selection
    pages = {
        "🏠 Home": "home",
        "📁 Upload Documents": "upload",
        "💬 Chat": "chat",
        "📊 Analytics": "analytics",
        "⚙️ Settings": "settings"
    }
    
    if 'current_page' not in st.session_state:
        st.session_state.current_page = "home"
    
    for page_name, page_key in pages.items():
        if st.button(page_name, key=f"nav_{page_key}"):
            st.session_state.current_page = page_key
            st.rerun()
    
    st.markdown("---")

def render_document_status():
    """Render document processing status"""
    st.subheader("📚 Document Status")
    
    # Check if documents are uploaded
    if 'uploaded_files' in st.session_state and st.session_state.uploaded_files:
        st.success(f"✅ {len(st.session_state.uploaded_files)} files uploaded")
    else:
        st.info("📄 No documents uploaded")
    
    # Check if documents are processed
    if 'processed_pdfs' in st.session_state and st.session_state.processed_pdfs:
        st.success(f"✅ {len(st.session_state.processed_pdfs)} files processed")
    else:
        st.info("⏳ Documents not processed")
    
    # Check if index is built
    if 'embedding_manager' in st.session_state and st.session_state.embedding_manager.index is not None:
        stats = st.session_state.embedding_manager.get_index_stats()
        st.success(f"✅ Search index ready")
        st.caption(f"📊 {stats.get('total_vectors', 0)} text chunks indexed")
    else:
        st.info("🔍 Search index not ready")
    
    # Quick actions
    if st.button("🗑️ Clear All Data", help="Clear all uploaded documents and chat history"):
        clear_all_data()
    
    st.markdown("---")

def render_settings():
    """Render settings section"""
    st.subheader("⚙️ Settings")
    
    # Model settings
    with st.expander("🤖 Model Settings"):
        st.write("**Embedding Model:**")
        st.code(config.HUGGINGFACE_MODEL)
        
        st.write("**LLM Model:**")
        st.code(config.WATSONX_MODEL_ID)
        
        # Generation parameters
        st.write("**Generation Parameters:**")
        st.write(f"Max Tokens: {config.MAX_TOKENS}")
        st.write(f"Temperature: {config.TEMPERATURE}")
        st.write(f"Top P: {config.TOP_P}")
    
    # Processing settings
    with st.expander("📝 Processing Settings"):
        st.write(f"**Chunk Size:** {config.CHUNK_SIZE}")
        st.write(f"**Chunk Overlap:** {config.CHUNK_OVERLAP}")
        st.write(f"**Min Chunk Size:** {config.MIN_CHUNK_SIZE}")
    
    # File settings
    with st.expander("📁 File Settings"):
        st.write(f"**Max File Size:** {config.MAX_FILE_SIZE_MB} MB")
        st.write(f"**Max Files:** {config.MAX_FILES_UPLOAD}")
        st.write(f"**Allowed Extensions:** {', '.join(config.ALLOWED_EXTENSIONS)}")
    
    st.markdown("---")

def render_help_section():
    """Render help and information section"""
    st.subheader("❓ Help & Info")
    
    # Quick help
    with st.expander("🚀 Quick Start"):
        st.markdown("""
        1. **Upload Documents**: Click 'Upload Documents' and select your PDF files
        2. **Process Files**: Click 'Process Files' to extract text and build search index
        3. **Ask Questions**: Go to 'Chat' and start asking questions about your materials
        4. **Review Sources**: Check the sources provided with each answer
        """)
    
    # Tips
    with st.expander("💡 Tips for Better Results"):
        st.markdown("""
        - **Be Specific**: Ask detailed questions for better answers
        - **Use Keywords**: Include important terms from your documents
        - **Context Matters**: Reference specific topics or sections
        - **Follow Up**: Ask clarifying questions to dive deeper
        - **Check Sources**: Always review the source materials provided
        """)
    
    # Troubleshooting
    with st.expander("🔧 Troubleshooting"):
        st.markdown("""
        - **No Results**: Try rephrasing your question or using different keywords
        - **Poor Quality**: Ensure your PDFs have clear, readable text
        - **Slow Processing**: Large files may take longer to process
        - **Connection Issues**: Check your internet connection and API keys
        """)
    
    # About
    with st.expander("ℹ️ About StudyMate"):
        st.markdown("""
        **StudyMate** is an AI-powered academic assistant that helps students interact with their study materials through conversational Q&A.
        
        **Technologies Used:**
        - IBM Watsonx (LLM)
        - HuggingFace Transformers
        - FAISS (Vector Search)
        - PyMuPDF (PDF Processing)
        - Streamlit (Web Interface)
        
        **Version:** 1.0.0
        """)

def clear_all_data():
    """Clear all application data"""
    # Clear session state
    keys_to_clear = [
        'uploaded_files',
        'processed_pdfs',
        'embedding_manager',
        'messages',
        'qa_engine'
    ]
    
    for key in keys_to_clear:
        if key in st.session_state:
            del st.session_state[key]
    
    st.success("✅ All data cleared successfully!")
    st.rerun()

def display_system_status():
    """Display system status information"""
    st.subheader("🖥️ System Status")
    
    # Check API connections
    col1, col2 = st.columns(2)
    
    with col1:
        # Watson status
        if config.WATSONX_API_KEY:
            st.success("✅ Watson API Key Set")
        else:
            st.error("❌ Watson API Key Missing")
    
    with col2:
        # HuggingFace status
        if config.HUGGINGFACE_API_KEY:
            st.success("✅ HuggingFace API Key Set")
        else:
            st.warning("⚠️ HuggingFace API Key Missing")
    
    # Memory usage (if available)
    try:
        import psutil
        memory = psutil.virtual_memory()
        st.metric("Memory Usage", f"{memory.percent}%")
    except ImportError:
        pass

def render_progress_tracker():
    """Render progress tracker for current operations"""
    if 'current_operation' in st.session_state:
        operation = st.session_state.current_operation
        st.subheader(f"⏳ {operation['name']}")
        
        if 'progress' in operation:
            st.progress(operation['progress'])
        
        if 'status' in operation:
            st.info(operation['status'])
        
        st.markdown("---")
