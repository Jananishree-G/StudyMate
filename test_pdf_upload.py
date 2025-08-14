#!/usr/bin/env python3
"""
Test PDF Upload and Processing
Simple test to verify PDF processing works
"""

import streamlit as st
import sys
from pathlib import Path
import tempfile
import traceback

# Add paths
sys.path.append(str(Path(__file__).parent / "backend"))

def main():
    st.set_page_config(
        page_title="Test PDF Upload",
        page_icon="📄",
        layout="wide"
    )
    
    st.title("📄 Test PDF Upload and Processing")
    
    # Initialize backend
    if 'backend_initialized' not in st.session_state:
        with st.spinner("🔄 Initializing backend..."):
            try:
                from backend.manager import StudyMateBackend
                st.session_state.backend = StudyMateBackend()
                st.session_state.backend_initialized = True
                st.success("✅ Backend initialized successfully!")
            except Exception as e:
                st.error(f"❌ Backend initialization failed: {str(e)}")
                st.code(traceback.format_exc())
                st.stop()
    
    # File upload
    st.markdown("## 📁 Upload PDF Files")
    
    uploaded_files = st.file_uploader(
        "Choose PDF files",
        type=['pdf'],
        accept_multiple_files=True,
        help="Select one or more PDF files to test processing"
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
        
        if st.button("🧪 Test Processing", type="primary"):
            st.markdown("### 🔄 Processing Steps")
            
            # Step 1: Save files
            st.markdown("#### Step 1: Saving Files")
            temp_paths = []
            temp_dir = Path("test_uploads")
            temp_dir.mkdir(exist_ok=True)
            
            for i, uploaded_file in enumerate(uploaded_files):
                try:
                    safe_filename = f"test_{i}_{uploaded_file.name}"
                    temp_path = temp_dir / safe_filename
                    
                    with open(temp_path, "wb") as f:
                        f.write(uploaded_file.getbuffer())
                    
                    temp_paths.append(temp_path)
                    st.success(f"✅ Saved: {uploaded_file.name} → {temp_path}")
                    
                    # Verify file exists and has content
                    if temp_path.exists():
                        file_size = temp_path.stat().st_size
                        st.info(f"📊 File size on disk: {file_size / (1024*1024):.1f} MB")
                    else:
                        st.error(f"❌ File not found after saving: {temp_path}")
                        
                except Exception as e:
                    st.error(f"❌ Failed to save {uploaded_file.name}: {str(e)}")
                    st.code(traceback.format_exc())
            
            if not temp_paths:
                st.error("❌ No files were saved successfully")
                return
            
            # Step 2: Test individual PDF processing
            st.markdown("#### Step 2: Individual PDF Processing")
            
            from backend.pdf_processor import PDFProcessor
            processor = PDFProcessor()
            
            for temp_path in temp_paths:
                st.markdown(f"**Testing: {temp_path.name}**")
                
                try:
                    # Test basic PDF opening
                    import fitz
                    doc = fitz.open(temp_path)
                    st.success(f"✅ PDF opened: {len(doc)} pages")
                    
                    # Test text extraction from first page
                    if len(doc) > 0:
                        page = doc.load_page(0)
                        page_text = page.get_text()
                        if page_text.strip():
                            st.success(f"✅ Text extracted: {len(page_text)} characters")
                            st.text_area(f"Preview of {temp_path.name}:", page_text[:200] + "..." if len(page_text) > 200 else page_text, height=100)
                        else:
                            st.warning("⚠️ No text found on first page")
                    
                    doc.close()
                    
                    # Test full processing
                    result = processor.process_pdf(temp_path)
                    st.success(f"✅ Full processing successful: {result['chunk_count']} chunks created")
                    
                except Exception as e:
                    st.error(f"❌ Processing failed for {temp_path.name}: {str(e)}")
                    st.code(traceback.format_exc())
            
            # Step 3: Test backend integration
            st.markdown("#### Step 3: Backend Integration")
            
            try:
                result = st.session_state.backend.process_uploaded_files(temp_paths)
                
                if result['success']:
                    st.success(f"🎉 Backend processing successful!")
                    
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Files Processed", result['stats'].get('files_processed', 0))
                    with col2:
                        st.metric("Total Chunks", result.get('num_chunks', 0))
                    with col3:
                        st.metric("Processing Time", f"{result.get('processing_time', 0):.2f}s")
                    
                    # Show detailed stats
                    with st.expander("📊 Detailed Statistics"):
                        st.json(result['stats'])
                    
                    st.balloons()
                    
                else:
                    st.error(f"❌ Backend processing failed: {result['message']}")
                    
                    if 'stats' in result:
                        with st.expander("🔍 Error Details"):
                            st.json(result['stats'])
                            
            except Exception as e:
                st.error(f"❌ Backend integration failed: {str(e)}")
                st.code(traceback.format_exc())
            
            # Step 4: Test chat functionality
            st.markdown("#### Step 4: Test Chat")
            
            try:
                stats = st.session_state.backend.get_system_stats()
                if stats['ready_for_questions']:
                    st.success("✅ System ready for questions!")
                    
                    test_question = "What is this document about?"
                    if st.button(f"🧪 Test Question: '{test_question}'"):
                        with st.spinner("Testing chat..."):
                            try:
                                response = st.session_state.backend.ask_question(test_question)
                                st.success("✅ Chat response generated!")
                                st.markdown(f"**Answer:** {response['answer']}")
                                
                                if response.get('sources'):
                                    st.info(f"📚 Found {len(response['sources'])} source(s)")
                                    
                            except Exception as e:
                                st.error(f"❌ Chat test failed: {str(e)}")
                                st.code(traceback.format_exc())
                else:
                    st.warning("⚠️ System not ready for questions")
                    
            except Exception as e:
                st.error(f"❌ Chat test setup failed: {str(e)}")
            
            # Cleanup
            st.markdown("#### Step 5: Cleanup")
            
            for temp_path in temp_paths:
                try:
                    if temp_path.exists():
                        temp_path.unlink()
                        st.success(f"✅ Cleaned: {temp_path.name}")
                except Exception as e:
                    st.warning(f"⚠️ Could not clean {temp_path.name}: {str(e)}")
            
            try:
                if temp_dir.exists() and not any(temp_dir.iterdir()):
                    temp_dir.rmdir()
                    st.success("✅ Temporary directory cleaned")
            except Exception as e:
                st.warning(f"⚠️ Could not remove temp directory: {str(e)}")
    
    # System status
    st.markdown("## 📊 System Status")
    
    try:
        stats = st.session_state.backend.get_system_stats()
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Documents", stats['documents_processed'])
        with col2:
            st.metric("Chunks", stats['total_chunks'])
        with col3:
            st.metric("Questions", stats['session_stats']['questions_answered'])
        with col4:
            st.metric("Ready", "Yes" if stats['ready_for_questions'] else "No")
        
    except Exception as e:
        st.error(f"Stats error: {str(e)}")

if __name__ == "__main__":
    main()
