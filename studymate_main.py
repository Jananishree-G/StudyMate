"""
StudyMate - Main Application
Clean, modern interface for document Q&A without authentication
"""

import streamlit as st
import sys
from pathlib import Path
import json
import time

# Add paths
sys.path.append(str(Path(__file__).parent / "backend"))
sys.path.append(str(Path(__file__).parent / "frontend"))

from backend.manager import StudyMateBackend
from frontend.styles import get_custom_css
from backend.config import config

def initialize_session_state():
    """Initialize session state variables"""
    if 'backend' not in st.session_state:
        st.session_state.backend = StudyMateBackend()
    
    if 'current_page' not in st.session_state:
        st.session_state.current_page = "home"
    
    if 'messages' not in st.session_state:
        st.session_state.messages = []

def render_header():
    """Render the main header"""
    st.markdown("""
    <div class="main-header fade-in-up">
        <h1>📚 StudyMate</h1>
        <p>Your AI-Powered Academic Assistant</p>
    </div>
    """, unsafe_allow_html=True)

def render_sidebar():
    """Render the enhanced sidebar navigation"""
    with st.sidebar:
        # App branding
        st.markdown("""
        <div style="text-align: center; padding: 1rem; background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%); border-radius: 1rem; margin-bottom: 1rem;">
            <h2 style="color: white; margin: 0;">📚 StudyMate</h2>
            <p style="color: rgba(255,255,255,0.8); margin: 0; font-size: 0.9rem;">AI Academic Assistant</p>
        </div>
        """, unsafe_allow_html=True)

        # Navigation
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
            # Highlight current page
            button_type = "primary" if page_key == current_page else "secondary"
            if st.button(page_name, key=f"nav_{page_key}", use_container_width=True, type=button_type):
                st.session_state.current_page = page_key
                st.rerun()

        st.markdown("---")

        # Model selection
        st.markdown("### 🤖 AI Model")

        try:
            available_models = st.session_state.backend.get_available_models()
            current_model = st.session_state.backend.get_current_model()

            model_options = {key: f"{info['name']}" for key, info in available_models.items()}

            selected_model = st.selectbox(
                "Choose AI Model:",
                options=list(model_options.keys()),
                format_func=lambda x: model_options[x],
                index=list(model_options.keys()).index(current_model) if current_model in model_options else 0,
                help="Select the AI model for answering questions"
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
            st.error(f"Model loading error: {str(e)}")

        st.markdown("---")

        # Enhanced system status
        st.markdown("### 📊 System Status")
        try:
            stats = st.session_state.backend.get_system_stats()

            col1, col2 = st.columns(2)
            with col1:
                st.metric("Documents", stats['documents_processed'])
            with col2:
                st.metric("Chunks", stats['total_chunks'])

            # Session info
            session_stats = stats.get('session_stats', {})
            if session_stats:
                st.metric("Questions", session_stats.get('questions_answered', 0))
                st.metric("Session", f"{session_stats.get('session_duration_minutes', 0):.1f}m")

            # Status indicator
            if stats['ready_for_questions']:
                st.success("✅ Ready for questions")
            else:
                st.info("📄 Upload documents to start")
        except Exception as e:
            st.error(f"Stats error: {str(e)}")

        st.markdown("---")

        # Action buttons
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🗑️ Clear Data", use_container_width=True):
                try:
                    st.session_state.backend.clear_all_data()
                    st.session_state.messages = []
                    st.success("Data cleared!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Clear error: {str(e)}")

        with col2:
            if st.button("📥 Export", use_container_width=True):
                try:
                    export_data = st.session_state.backend.export_session_data()
                    st.download_button(
                        "💾 Download",
                        data=json.dumps(export_data, indent=2),
                        file_name="studymate_session.json",
                        mime="application/json",
                        use_container_width=True
                    )
                except Exception as e:
                    st.error(f"Export error: {str(e)}")

def render_home_page():
    """Render the enhanced home page"""
    # Welcome section
    st.markdown("""
    <div class="custom-card fade-in-up">
        <h2>🎓 Welcome to StudyMate!</h2>
        <p style="font-size: 1.1rem; color: var(--text-secondary);">
            Transform your study experience with AI-powered document analysis. Upload your PDFs,
            ask questions, and get instant, contextual answers from your study materials.
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Feature cards
    st.markdown("### ✨ Key Features")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("""
        <div class="feature-card fade-in-up">
            <div class="feature-icon">📚</div>
            <h3>Smart Document Processing</h3>
            <p>Advanced PDF text extraction with intelligent chunking and metadata preservation for optimal understanding.</p>
            <div style="margin-top: 1rem;">
                <span style="background: var(--primary-color); color: white; padding: 0.25rem 0.5rem; border-radius: 0.5rem; font-size: 0.8rem;">
                    PyMuPDF Powered
                </span>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class="feature-card fade-in-up">
            <div class="feature-icon">🔍</div>
            <h3>Intelligent Search</h3>
            <p>Advanced vector-based semantic search with FAISS and enhanced ranking for precise results.</p>
            <div style="margin-top: 1rem;">
                <span style="background: var(--secondary-color); color: white; padding: 0.25rem 0.5rem; border-radius: 0.5rem; font-size: 0.8rem;">
                    FAISS Enhanced
                </span>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown("""
        <div class="feature-card fade-in-up">
            <div class="feature-icon">💬</div>
            <h3>Interactive Q&A</h3>
            <p>Natural language question answering with IBM Granite models, source attribution, and confidence scoring.</p>
            <div style="margin-top: 1rem;">
                <span style="background: var(--accent-color); color: white; padding: 0.25rem 0.5rem; border-radius: 0.5rem; font-size: 0.8rem;">
                    IBM Granite AI
                </span>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # Statistics section
    try:
        stats = st.session_state.backend.get_system_stats()
        if stats['documents_processed'] > 0:
            st.markdown("### 📊 Your Progress")

            col1, col2, col3, col4 = st.columns(4)

            with col1:
                st.metric(
                    "Documents Processed",
                    stats['documents_processed'],
                    help="Total number of PDF documents you've uploaded"
                )

            with col2:
                st.metric(
                    "Text Chunks",
                    stats['total_chunks'],
                    help="Number of text segments created for search"
                )

            with col3:
                session_stats = stats.get('session_stats', {})
                st.metric(
                    "Questions Asked",
                    session_stats.get('questions_answered', 0),
                    help="Total questions you've asked this session"
                )

            with col4:
                st.metric(
                    "Session Time",
                    f"{session_stats.get('session_duration_minutes', 0):.1f}m",
                    help="Time spent in current session"
                )
    except Exception as e:
        st.error(f"Stats display error: {str(e)}")

    # Quick start section
    st.markdown("### 🚀 Quick Start")

    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("📁 Upload Documents", type="primary", use_container_width=True):
            st.session_state.current_page = "upload"
            st.rerun()

    with col2:
        if st.button("💬 Start Chatting", use_container_width=True):
            st.session_state.current_page = "chat"
            st.rerun()

    with col3:
        if st.button("📊 View Analytics", use_container_width=True):
            st.session_state.current_page = "analytics"
            st.rerun()

    # Tips section
    try:
        stats = st.session_state.backend.get_system_stats()
        if stats['documents_processed'] == 0:
            st.markdown("### 💡 Getting Started Tips")

            st.markdown("""
            <div class="custom-card">
                <h4>📋 How to Use StudyMate:</h4>
                <ol>
                    <li><strong>Upload PDFs:</strong> Click "Upload Documents" and select your study materials</li>
                    <li><strong>Wait for Processing:</strong> StudyMate will extract and index the text</li>
                    <li><strong>Ask Questions:</strong> Go to "Chat" and ask questions in natural language</li>
                    <li><strong>Review Sources:</strong> Check the source documents for each answer</li>
                    <li><strong>Explore Analytics:</strong> View detailed statistics about your documents</li>
                </ol>
            </div>
            """, unsafe_allow_html=True)
    except Exception as e:
        st.error(f"Tips display error: {str(e)}")

def main():
    """Main application function without authentication"""
    st.set_page_config(
        page_title="StudyMate - AI Academic Assistant",
        page_icon="📚",
        layout="wide"
    )
    
    # Apply custom CSS
    st.markdown(get_custom_css(), unsafe_allow_html=True)

    # Initialize session state
    initialize_session_state()

    # Render header
    render_header()

    # Render sidebar
    render_sidebar()

    # Render main content based on current page
    current_page = st.session_state.current_page

    try:
        if current_page == "home":
            render_home_page()
        elif current_page == "upload":
            st.info("📁 Upload functionality - integrate with your existing upload code")
        elif current_page == "chat":
            st.info("💬 Chat functionality - integrate with your existing chat code")
        elif current_page == "analytics":
            st.info("📊 Analytics functionality - integrate with your existing analytics code")
        elif current_page == "settings":
            st.info("⚙️ Settings functionality - integrate with your existing settings code")
        else:
            render_home_page()

    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
        st.markdown("### 🔧 Troubleshooting")
        st.markdown("""
        - Try refreshing the page
        - Clear your browser cache
        - Check the console for detailed error messages
        - Go back to the Home page and try again
        """)

        if st.button("🏠 Go to Home"):
            st.session_state.current_page = "home"
            st.rerun()

if __name__ == "__main__":
    main()
