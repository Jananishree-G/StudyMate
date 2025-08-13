"""
File uploader component for StudyMate
"""

import streamlit as st
from pathlib import Path
from typing import List, Optional
import sys

# Add src to path
sys.path.append(str(Path(__file__).parent.parent.parent / "src"))

from config import config
from utils import validate_file_type, validate_file_size, format_file_size, save_uploaded_file

def render_file_uploader() -> Optional[List[Path]]:
    """
    Render file uploader component
    
    Returns:
        List of uploaded file paths or None
    """
    st.subheader("📁 Upload Study Materials")
    
    # File uploader
    uploaded_files = st.file_uploader(
        "Choose PDF files",
        type=['pdf'],
        accept_multiple_files=True,
        help=f"Upload up to {config.MAX_FILES_UPLOAD} PDF files (max {config.MAX_FILE_SIZE_MB}MB each)"
    )
    
    if not uploaded_files:
        st.info("Please upload PDF files to get started.")
        return None
    
    # Validate files
    valid_files = []
    invalid_files = []
    
    for uploaded_file in uploaded_files:
        # Check file type
        if not validate_file_type(uploaded_file.name):
            invalid_files.append(f"{uploaded_file.name}: Invalid file type")
            continue
        
        # Check file size
        if not validate_file_size(uploaded_file.size):
            invalid_files.append(f"{uploaded_file.name}: File too large ({format_file_size(uploaded_file.size)})")
            continue
        
        valid_files.append(uploaded_file)
    
    # Display validation results
    if invalid_files:
        st.error("Some files were rejected:")
        for error in invalid_files:
            st.write(f"❌ {error}")
    
    if not valid_files:
        st.warning("No valid files to process.")
        return None
    
    # Check file count limit
    if len(valid_files) > config.MAX_FILES_UPLOAD:
        st.warning(f"Too many files. Only the first {config.MAX_FILES_UPLOAD} files will be processed.")
        valid_files = valid_files[:config.MAX_FILES_UPLOAD]
    
    # Display file information
    st.success(f"✅ {len(valid_files)} valid file(s) ready for processing:")
    
    total_size = 0
    for file in valid_files:
        file_size = format_file_size(file.size)
        total_size += file.size
        st.write(f"📄 {file.name} ({file_size})")
    
    st.write(f"**Total size:** {format_file_size(total_size)}")
    
    # Process files button
    if st.button("🚀 Process Files", type="primary"):
        return process_uploaded_files(valid_files)
    
    return None

def process_uploaded_files(uploaded_files: List) -> List[Path]:
    """
    Process and save uploaded files
    
    Args:
        uploaded_files: List of uploaded file objects
        
    Returns:
        List of saved file paths
    """
    saved_files = []
    
    with st.spinner("Saving uploaded files..."):
        for uploaded_file in uploaded_files:
            file_path = save_uploaded_file(uploaded_file, config.UPLOAD_DIR)
            if file_path:
                saved_files.append(file_path)
    
    if saved_files:
        st.success(f"✅ Successfully saved {len(saved_files)} file(s)")
    else:
        st.error("❌ Failed to save files")
    
    return saved_files

def display_file_stats(file_paths: List[Path]):
    """
    Display statistics about uploaded files
    
    Args:
        file_paths: List of file paths
    """
    if not file_paths:
        return
    
    st.subheader("📊 File Statistics")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total Files", len(file_paths))
    
    with col2:
        total_size = sum(file_path.stat().st_size for file_path in file_paths)
        st.metric("Total Size", format_file_size(total_size))
    
    with col3:
        avg_size = total_size / len(file_paths) if file_paths else 0
        st.metric("Average Size", format_file_size(avg_size))
    
    # File details
    with st.expander("📋 File Details"):
        for i, file_path in enumerate(file_paths, 1):
            file_size = format_file_size(file_path.stat().st_size)
            st.write(f"{i}. **{file_path.name}** - {file_size}")

def clear_uploaded_files():
    """Clear uploaded files from session state"""
    if 'uploaded_files' in st.session_state:
        del st.session_state['uploaded_files']
    
    if 'processed_pdfs' in st.session_state:
        del st.session_state['processed_pdfs']
    
    if 'embedding_manager' in st.session_state:
        del st.session_state['embedding_manager']
    
    st.success("✅ Cleared all uploaded files")
