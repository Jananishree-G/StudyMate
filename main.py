"""
StudyMate - AI-Powered Academic Assistant
Main entry point for the Streamlit application
"""

import streamlit as st
import sys
from pathlib import Path

# Add backend to Python path
backend_path = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_path))

# Import the new app
from app import main as run_app

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
