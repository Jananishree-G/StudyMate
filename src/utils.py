"""
Utility functions for StudyMate application
"""

import os
import hashlib
import logging
from pathlib import Path
from typing import List, Optional, Union
from datetime import datetime
import streamlit as st

from config import config

def setup_logging():
    """Setup logging configuration"""
    log_file = config.LOGS_DIR / "studymate.log"
    
    logging.basicConfig(
        level=getattr(logging, config.LOG_LEVEL.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )
    
    return logging.getLogger(__name__)

def get_file_hash(file_path: Union[str, Path]) -> str:
    """Generate MD5 hash of a file"""
    hash_md5 = hashlib.md5()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()

def validate_file_type(filename: str) -> bool:
    """Validate if file type is allowed"""
    file_extension = filename.split('.')[-1].lower()
    return file_extension in config.ALLOWED_EXTENSIONS

def validate_file_size(file_size: int) -> bool:
    """Validate if file size is within limits"""
    max_size_bytes = config.MAX_FILE_SIZE_MB * 1024 * 1024
    return file_size <= max_size_bytes

def format_file_size(size_bytes: int) -> str:
    """Format file size in human readable format"""
    if size_bytes == 0:
        return "0B"
    
    size_names = ["B", "KB", "MB", "GB"]
    i = 0
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024.0
        i += 1
    
    return f"{size_bytes:.1f}{size_names[i]}"

def clean_text(text: str) -> str:
    """Clean and normalize text"""
    # Remove extra whitespace
    text = ' '.join(text.split())
    
    # Remove special characters but keep basic punctuation
    import re
    text = re.sub(r'[^\w\s\.\,\!\?\;\:\-\(\)]', ' ', text)
    
    # Remove extra spaces
    text = ' '.join(text.split())
    
    return text.strip()

def chunk_text(text: str, chunk_size: int = None, overlap: int = None) -> List[str]:
    """Split text into chunks with overlap"""
    if chunk_size is None:
        chunk_size = config.CHUNK_SIZE
    if overlap is None:
        overlap = config.CHUNK_OVERLAP
    
    if len(text) <= chunk_size:
        return [text]
    
    chunks = []
    start = 0
    
    while start < len(text):
        end = start + chunk_size
        
        # Try to break at sentence boundary
        if end < len(text):
            # Look for sentence endings
            sentence_ends = ['.', '!', '?', '\n']
            for i in range(end, max(start + chunk_size // 2, end - 100), -1):
                if text[i] in sentence_ends:
                    end = i + 1
                    break
        
        chunk = text[start:end].strip()
        if len(chunk) >= config.MIN_CHUNK_SIZE:
            chunks.append(chunk)
        
        start = end - overlap
        
        if start >= len(text):
            break
    
    return chunks

def save_uploaded_file(uploaded_file, upload_dir: Path) -> Optional[Path]:
    """Save uploaded file to disk"""
    try:
        file_path = upload_dir / uploaded_file.name
        
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        
        return file_path
    
    except Exception as e:
        st.error(f"Error saving file: {str(e)}")
        return None

def get_timestamp() -> str:
    """Get current timestamp as string"""
    return datetime.now().strftime("%Y%m%d_%H%M%S")

def create_session_id() -> str:
    """Create unique session ID"""
    import uuid
    return str(uuid.uuid4())

def display_error(message: str, logger: logging.Logger = None):
    """Display error message to user and log it"""
    st.error(message)
    if logger:
        logger.error(message)

def display_success(message: str, logger: logging.Logger = None):
    """Display success message to user and log it"""
    st.success(message)
    if logger:
        logger.info(message)

def display_info(message: str, logger: logging.Logger = None):
    """Display info message to user and log it"""
    st.info(message)
    if logger:
        logger.info(message)

def display_warning(message: str, logger: logging.Logger = None):
    """Display warning message to user and log it"""
    st.warning(message)
    if logger:
        logger.warning(message)

# Initialize logger
logger = setup_logging()
