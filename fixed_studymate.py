#!/usr/bin/env python3
"""
Fixed StudyMate - Working PDF Processing
Complete StudyMate with fixed PDF upload and processing
"""

import streamlit as st
import sys
from pathlib import Path
import tempfile
import os

# Add paths
sys.path.append(str(Path(__file__).parent / "backend"))
sys.path.append(str(Path(__file__).parent / "frontend"))

def main():
    st.set_page_config(
        page_title="StudyMate - AI Academic Assistant",
        page_icon="📚",
        layout="wide"
    )
    
    st.title("📚 StudyMate - AI Academic Assistant")
    st.markdown("### Your AI-Powered Document Analysis Tool")
    
    # Initialize backend
    if 'backend_initialized' not in st.session_state:
        with st.spinner("🔄 Initializing StudyMate backend..."):
            try:
                from backend.manager import StudyMateBackend
                from frontend.styles import get_custom_css
                
                st.session_state.backend = StudyMateBackend()
                st.session_state.backend_initialized = True
                
                # Apply custom CSS
                st.markdown(get_custom_css(), unsafe_allow_html=True)
                
                st.success("✅ Backend initialized successfully!")
            except Exception as e:
                st.error(f"❌ Backend initialization failed: {str(e)}")
                st.stop()
    
    # Initialize session state
    if 'current_page' not in st.session_state:
        st.session_state.current_page = "upload"  # Start with upload page
    
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    
    # Sidebar
    with st.sidebar:
        st.markdown("### 🧭 Navigation")
        
        pages = {
            "📁 Upload Documents": "upload",
            "💬 Chat": "chat",
            "📊 Analytics": "analytics",
            "⚙️ Settings": "settings"
        }
        
        current_page = st.session_state.current_page
        
        for page_name, page_key in pages.items():
            button_type = "primary" if page_key == current_page else "secondary"
            if st.button(page_name, key=f"nav_{page_key}", use_container_width=True, type=button_type):
                st.session_state.current_page = page_key
                st.rerun()
        
        st.markdown("---")
        
        # System status
        st.markdown("### 📊 System Status")
        try:
            stats = st.session_state.backend.get_system_stats()
            st.metric("Documents", stats['documents_processed'])
            st.metric("Chunks", stats['total_chunks'])
            
            if stats['ready_for_questions']:
                st.success("✅ Ready for questions")
            else:
                st.info("📄 Upload documents to start")
        except Exception as e:
            st.error(f"Stats error: {str(e)}")
    
    # Main content
    current_page = st.session_state.current_page
    
    if current_page == "upload":
        show_upload_page()
    elif current_page == "chat":
        show_chat_page()
    elif current_page == "analytics":
        show_analytics_page()
    elif current_page == "settings":
        show_settings_page()

def show_upload_page():
    """Fixed upload page with proper error handling"""
    st.markdown("## 📁 Document Upload")
    
    uploaded_files = st.file_uploader(
        "Choose PDF files",
        type=['pdf'],
        accept_multiple_files=True,
        help="Select one or more PDF files to upload and process"
    )
    
    if uploaded_files:
        st.markdown("### 📋 Selected Files")
        
        valid_files = []
        for file in uploaded_files:
            size_mb = file.size / (1024 * 1024)
            col1, col2, col3 = st.columns([3, 1, 1])
            
            with col1:
                st.write(f"📄 **{file.name}**")
            with col2:
                st.write(f"{size_mb:.1f} MB")
            with col3:
                if size_mb <= 50:
                    st.success("Valid")
                    valid_files.append(file)
                else:
                    st.error("Too large")
        
        if valid_files and st.button("🚀 Process Documents", type="primary"):
            process_documents(valid_files)

def process_documents(uploaded_files):
    """Process uploaded documents with detailed error handling"""
    st.markdown("### 🔄 Processing Documents")
    
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    try:
        # Step 1: Save files to temporary directory
        status_text.text("📁 Saving uploaded files...")
        progress_bar.progress(10)
        
        temp_dir = Path(tempfile.mkdtemp(prefix="studymate_"))
        temp_paths = []
        
        for i, uploaded_file in enumerate(uploaded_files):
            try:
                # Create safe filename
                safe_name = f"{i:03d}_{uploaded_file.name}"
                temp_path = temp_dir / safe_name
                
                # Write file
                with open(temp_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                
                # Verify file was written
                if temp_path.exists() and temp_path.stat().st_size > 0:
                    temp_paths.append(temp_path)
                    st.success(f"✅ Saved: {uploaded_file.name}")
                else:
                    st.error(f"❌ Failed to save: {uploaded_file.name}")
                    
            except Exception as e:
                st.error(f"❌ Error saving {uploaded_file.name}: {str(e)}")
        
        if not temp_paths:
            st.error("❌ No files were saved successfully")
            return
        
        progress_bar.progress(30)
        
        # Step 2: Process with backend
        status_text.text(f"🔄 Processing {len(temp_paths)} files...")
        
        result = st.session_state.backend.process_uploaded_files(temp_paths)
        progress_bar.progress(80)
        
        # Step 3: Show results
        status_text.text("📊 Displaying results...")
        
        if result['success']:
            st.success(f"🎉 {result['message']}")
            
            # Show statistics
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Files Processed", result['stats'].get('files_processed', 0))
            with col2:
                st.metric("Total Chunks", result.get('num_chunks', 0))
            with col3:
                st.metric("Total Words", result['stats'].get('total_words', 0))
            with col4:
                st.metric("Processing Time", f"{result.get('processing_time', 0):.1f}s")
            
            # Show detailed stats
            with st.expander("📊 Detailed Statistics"):
                st.json(result['stats'])
            
            st.balloons()
            
            # Suggest next step
            st.info("💬 Documents processed successfully! Go to the Chat page to ask questions.")
            
        else:
            st.error(f"❌ Processing failed: {result['message']}")
            
            # Show error details
            if 'stats' in result and result['stats']:
                with st.expander("🔍 Error Details"):
                    st.json(result['stats'])
            
            # Show failed files
            if 'failed_files' in result and result['failed_files']:
                st.markdown("**Failed Files:**")
                for failed_file in result['failed_files']:
                    st.error(f"• {failed_file}")
        
        progress_bar.progress(100)
        status_text.text("✅ Processing complete!")
        
    except Exception as e:
        st.error(f"❌ Processing error: {str(e)}")
        import traceback
        with st.expander("🔍 Debug Information"):
            st.code(traceback.format_exc())
    
    finally:
        # Cleanup temporary files
        try:
            for temp_path in temp_paths:
                if temp_path.exists():
                    temp_path.unlink()
            
            if temp_dir.exists():
                temp_dir.rmdir()
            
            st.success("🗑️ Temporary files cleaned up")
        except Exception as e:
            st.warning(f"⚠️ Cleanup warning: {str(e)}")

def show_chat_page():
    """Chat page"""
    st.markdown("## 💬 Chat with Your Documents")
    
    # Check if documents are loaded
    try:
        stats = st.session_state.backend.get_system_stats()
        if not stats['ready_for_questions']:
            st.warning("⚠️ No documents loaded. Please upload documents first.")
            if st.button("📁 Go to Upload", type="primary"):
                st.session_state.current_page = "upload"
                st.rerun()
            return
    except Exception as e:
        st.error(f"Error checking system status: {str(e)}")
        return
    
    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            
            # Show sources for assistant messages
            if message["role"] == "assistant" and "sources" in message:
                if message["sources"]:
                    with st.expander(f"📚 Sources ({len(message['sources'])} documents)"):
                        for i, source in enumerate(message["sources"], 1):
                            st.markdown(f"**{i}. {source['filename']}**")
                            st.markdown(f"Similarity: {source.get('similarity_score', 0):.3f}")
                            st.markdown(f"```\n{source['text_preview']}\n```")
    
    # Chat input
    if prompt := st.chat_input("Ask a question about your documents..."):
        # Add user message
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Generate response
        with st.chat_message("assistant"):
            with st.spinner("🤔 Analyzing your documents..."):
                try:
                    response = st.session_state.backend.ask_question(prompt)
                    
                    st.markdown(response["answer"])
                    
                    # Add assistant message with metadata
                    assistant_message = {
                        "role": "assistant",
                        "content": response["answer"],
                        "sources": response.get("sources", []),
                        "confidence": response.get("confidence", 0)
                    }
                    st.session_state.messages.append(assistant_message)
                    
                except Exception as e:
                    error_msg = f"❌ Error generating response: {str(e)}"
                    st.error(error_msg)
                    st.session_state.messages.append({"role": "assistant", "content": error_msg})

def show_analytics_page():
    """Analytics page"""
    st.markdown("## 📊 Analytics & Insights")
    
    try:
        stats = st.session_state.backend.get_system_stats()
        
        if stats['documents_processed'] == 0:
            st.info("📄 No documents processed yet. Upload some documents to see analytics.")
            return
        
        # Overview metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Documents", stats['documents_processed'])
        with col2:
            st.metric("Total Chunks", stats['total_chunks'])
        with col3:
            st.metric("Questions Asked", stats['session_stats']['questions_answered'])
        with col4:
            st.metric("Session Time", f"{stats['session_stats']['session_duration_minutes']:.1f}m")
        
        # Document list
        st.markdown("### 📋 Document Details")
        documents = st.session_state.backend.get_document_list()
        
        for doc in documents:
            with st.expander(f"📄 {doc['filename']}"):
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("Pages", doc['pages'])
                with col2:
                    st.metric("Words", f"{doc['words']:,}")
                with col3:
                    st.metric("Chunks", doc['chunks'])
                    
    except Exception as e:
        st.error(f"Analytics error: {str(e)}")

def show_settings_page():
    """Settings page"""
    st.markdown("## ⚙️ Settings")
    
    st.markdown("### 🔧 System Configuration")
    
    try:
        from backend.config import config
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Text Processing:**")
            st.write(f"• Chunk Size: {config.CHUNK_SIZE} characters")
            st.write(f"• Chunk Overlap: {config.CHUNK_OVERLAP} characters")
        
        with col2:
            st.markdown("**Search Settings:**")
            st.write(f"• Max Search Results: {config.MAX_SEARCH_RESULTS}")
            st.write(f"• Min Similarity Score: {config.MIN_SIMILARITY_SCORE}")
        
        st.markdown("---")
        
        # Data management
        st.markdown("### 🗂️ Data Management")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🗑️ Clear All Data", use_container_width=True):
                if st.button("⚠️ Confirm Clear All", type="secondary", use_container_width=True):
                    st.session_state.backend.clear_all_data()
                    if 'messages' in st.session_state:
                        st.session_state.messages = []
                    st.success("All data cleared successfully!")
                    st.rerun()
        
        with col2:
            if st.button("📥 Export Session Data", use_container_width=True):
                try:
                    export_data = st.session_state.backend.export_session_data()
                    st.download_button(
                        "💾 Download Session Data",
                        data=str(export_data),
                        file_name="studymate_session.json",
                        mime="application/json",
                        use_container_width=True
                    )
                except Exception as e:
                    st.error(f"Export error: {str(e)}")
                    
    except Exception as e:
        st.error(f"Settings error: {str(e)}")

if __name__ == "__main__":
    main()
