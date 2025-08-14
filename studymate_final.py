#!/usr/bin/env python3
"""
StudyMate - Final Working Version
Complete StudyMate application without authentication
"""

import streamlit as st
import sys
from pathlib import Path
import json
import time

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
                st.code(str(e))
                st.stop()
    
    # Initialize session state
    if 'current_page' not in st.session_state:
        st.session_state.current_page = "home"
    
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    
    # Sidebar
    with st.sidebar:
        st.markdown("""
        <div style="text-align: center; padding: 1rem; background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%); border-radius: 1rem; margin-bottom: 1rem;">
            <h2 style="color: white; margin: 0;">📚 StudyMate</h2>
            <p style="color: rgba(255,255,255,0.8); margin: 0; font-size: 0.9rem;">AI Academic Assistant</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("### 🧭 Navigation")
        
        pages = {
            "🏠 Home": "home",
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
        
        st.markdown("---")
        
        # Model selection
        st.markdown("### 🤖 AI Model")
        try:
            available_models = st.session_state.backend.get_available_models()
            current_model = st.session_state.backend.get_current_model()
            
            model_options = {key: info['name'] for key, info in available_models.items()}
            
            selected_model = st.selectbox(
                "Choose AI Model:",
                options=list(model_options.keys()),
                format_func=lambda x: model_options[x],
                index=list(model_options.keys()).index(current_model) if current_model in model_options else 0
            )
            
            if selected_model != current_model:
                with st.spinner(f"Loading {model_options[selected_model]}..."):
                    if st.session_state.backend.set_generation_model(selected_model):
                        st.success(f"✅ Switched to {model_options[selected_model]}")
                        st.rerun()
                    else:
                        st.error(f"❌ Failed to load {model_options[selected_model]}")
            
            # Model info
            model_info = st.session_state.backend.get_model_info()
            if model_info:
                st.info(f"🔄 **Current:** {model_info['name']}")
        except Exception as e:
            st.error(f"Model error: {str(e)}")
    
    # Main content
    current_page = st.session_state.current_page
    
    try:
        if current_page == "home":
            show_home_page()
        elif current_page == "upload":
            show_upload_page()
        elif current_page == "chat":
            show_chat_page()
        elif current_page == "analytics":
            show_analytics_page()
        elif current_page == "settings":
            show_settings_page()
    except Exception as e:
        st.error(f"Page error: {str(e)}")
        st.code(str(e))

def show_home_page():
    """Home page"""
    st.markdown("## 🏠 Welcome to StudyMate!")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        ### ✨ Features
        - 📄 **Smart PDF Processing** - Advanced text extraction with PyMuPDF
        - 🔍 **Intelligent Search** - FAISS vector search for semantic matching
        - 💬 **AI Q&A** - IBM Granite and Mistral models for natural language answers
        - 📊 **Analytics** - Detailed insights and statistics
        """)
    
    with col2:
        st.markdown("### 📊 Quick Stats")
        try:
            stats = st.session_state.backend.get_system_stats()
            st.json({
                "Documents": stats['documents_processed'],
                "Chunks": stats['total_chunks'],
                "Questions": stats['session_stats']['questions_answered'],
                "Session Time": f"{stats['session_stats']['session_duration_minutes']:.1f}m"
            })
        except Exception as e:
            st.error(f"Stats error: {str(e)}")
    
    # Quick actions
    st.markdown("### 🚀 Quick Actions")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📁 Upload Documents", type="primary", use_container_width=True):
            st.session_state.current_page = "upload"
            st.rerun()
    
    with col2:
        if st.button("💬 Start Chat", use_container_width=True):
            st.session_state.current_page = "chat"
            st.rerun()
    
    with col3:
        if st.button("📊 View Analytics", use_container_width=True):
            st.session_state.current_page = "analytics"
            st.rerun()

def show_upload_page():
    """Upload page"""
    st.markdown("## 📁 Document Upload")
    
    uploaded_files = st.file_uploader(
        "Choose PDF files",
        type=['pdf'],
        accept_multiple_files=True,
        help="Select one or more PDF files to upload and process"
    )
    
    if uploaded_files:
        st.markdown("### 📋 Selected Files")
        
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
                else:
                    st.error("Too large")
        
        if st.button("🚀 Process Documents", type="primary"):
            with st.spinner("Processing documents..."):
                try:
                    # Save files temporarily with better error handling
                    temp_paths = []
                    temp_dir = Path("temp_uploads")
                    temp_dir.mkdir(exist_ok=True)

                    st.info(f"📁 Saving {len(uploaded_files)} files to temporary directory...")

                    for i, uploaded_file in enumerate(uploaded_files):
                        # Create unique filename to avoid conflicts
                        safe_filename = f"{i}_{uploaded_file.name}"
                        temp_path = temp_dir / safe_filename

                        try:
                            with open(temp_path, "wb") as f:
                                f.write(uploaded_file.getbuffer())
                            temp_paths.append(temp_path)
                            st.success(f"✅ Saved: {uploaded_file.name}")
                        except Exception as e:
                            st.error(f"❌ Failed to save {uploaded_file.name}: {str(e)}")
                            continue

                    if not temp_paths:
                        st.error("❌ No files were saved successfully")
                        return

                    st.info(f"🔄 Processing {len(temp_paths)} files with backend...")

                    # Process with backend
                    result = st.session_state.backend.process_uploaded_files(temp_paths)

                    # Show detailed results
                    st.markdown("### 📊 Processing Results")

                    if result['success']:
                        st.success(f"🎉 {result['message']}")

                        # Show statistics
                        if 'stats' in result:
                            col1, col2, col3 = st.columns(3)
                            with col1:
                                st.metric("Files Processed", result['stats'].get('files_processed', 0))
                            with col2:
                                st.metric("Total Chunks", result['stats'].get('total_chunks', 0))
                            with col3:
                                st.metric("Total Words", result['stats'].get('total_words', 0))

                        st.balloons()
                    else:
                        st.error(f"❌ Processing failed: {result['message']}")

                        # Show detailed error information
                        if 'details' in result:
                            with st.expander("🔍 Error Details"):
                                st.json(result['details'])

                    # Clean up temporary files
                    st.info("🗑️ Cleaning up temporary files...")
                    for temp_path in temp_paths:
                        try:
                            if temp_path.exists():
                                temp_path.unlink()
                                st.success(f"✅ Cleaned: {temp_path.name}")
                        except Exception as e:
                            st.warning(f"⚠️ Could not clean {temp_path.name}: {str(e)}")

                    # Remove temp directory if empty
                    try:
                        if temp_dir.exists() and not any(temp_dir.iterdir()):
                            temp_dir.rmdir()
                            st.success("✅ Temporary directory cleaned")
                    except Exception as e:
                        st.warning(f"⚠️ Could not remove temp directory: {str(e)}")

                except Exception as e:
                    st.error(f"❌ Processing error: {str(e)}")
                    st.code(str(e))

                    # Show traceback for debugging
                    import traceback
                    with st.expander("🔍 Debug Information"):
                        st.code(traceback.format_exc())

def show_chat_page():
    """Chat page"""
    st.markdown("## 💬 Chat with Your Documents")
    
    # Check if documents are loaded
    try:
        stats = st.session_state.backend.get_system_stats()
        if not stats['ready_for_questions']:
            st.warning("⚠️ No documents loaded. Please upload documents first.")
            if st.button("📁 Upload Documents", type="primary"):
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
            st.write(f"• Min Chunk Size: {config.MIN_CHUNK_SIZE} characters")
        
        with col2:
            st.markdown("**Search Settings:**")
            st.write(f"• Max Search Results: {config.MAX_SEARCH_RESULTS}")
            st.write(f"• Min Similarity Score: {config.MIN_SIMILARITY_SCORE}")
            st.write(f"• Allowed Extensions: {', '.join(config.ALLOWED_EXTENSIONS)}")
        
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
