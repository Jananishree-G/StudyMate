"""
StudyMate - AI-Powered Academic Assistant
Main entry point for the Streamlit application
"""

import streamlit as st
import sys
import os
from pathlib import Path

# Add src directory to Python path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

# Import frontend components
from frontend.streamlit_app import main as run_app

if __name__ == "__main__":
    # Set page configuration
    st.set_page_config(
        page_title="StudyMate - AI Academic Assistant",
        page_icon="📚",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Run the main application
    run_app()
