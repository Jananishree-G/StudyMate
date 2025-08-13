"""
StudyMate Frontend - API Integration
Streamlit frontend that connects to the FastAPI backend
"""

import streamlit as st
import requests
import json
import time
from pathlib import Path
from typing import Dict, List, Any, Optional
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
API_BASE_URL = "http://localhost:8000"
API_V1_URL = f"{API_BASE_URL}/api/v1"

class APIClient:
    """Client for StudyMate API"""
    
    def __init__(self, base_url: str = API_BASE_URL):
        self.base_url = base_url
        self.session = requests.Session()
    
    def get_health(self) -> Dict[str, Any]:
        """Get API health status"""
        try:
            response = self.session.get(f"{self.base_url}/health")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return {"status": "error", "error": str(e)}
    
    def list_models(self) -> Dict[str, Any]:
        """Get available models"""
        try:
            response = self.session.get(f"{API_V1_URL}/models/")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Failed to list models: {e}")
            return {"models": [], "error": str(e)}
    
    def get_current_model(self) -> Dict[str, Any]:
        """Get current model info"""
        try:
            response = self.session.get(f"{API_V1_URL}/models/current")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Failed to get current model: {e}")
            return {"error": str(e)}
    
    def switch_model(self, model_id: str) -> Dict[str, Any]:
        """Switch to a different model"""
        try:
            response = self.session.post(f"{API_V1_URL}/models/switch", params={"model_id": model_id})
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Failed to switch model: {e}")
            return {"success": False, "error": str(e)}
    
    def ask_question(self, question: str, model: str = None, temperature: float = 0.7, max_tokens: int = 512) -> Dict[str, Any]:
        """Ask a question"""
        try:
            data = {
                "question": question,
                "temperature": temperature,
                "max_tokens": max_tokens
            }
            if model:
                data["model"] = model
            
            response = self.session.post(f"{API_V1_URL}/ask", json=data)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Failed to ask question: {e}")
            return {"answer": f"Error: {str(e)}", "error": True}
    
    def upload_document(self, file_data: bytes, filename: str) -> Dict[str, Any]:
        """Upload a document"""
        try:
            files = {"file": (filename, file_data, "application/pdf")}
            response = self.session.post(f"{API_V1_URL}/documents/upload", files=files)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Failed to upload document: {e}")
            return {"success": False, "error": str(e)}
    
    def list_documents(self) -> Dict[str, Any]:
        """Get list of documents"""
        try:
            response = self.session.get(f"{API_V1_URL}/documents/")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Failed to list documents: {e}")
            return {"documents": [], "error": str(e)}
    
    def get_analytics(self) -> Dict[str, Any]:
        """Get analytics data"""
        try:
            response = self.session.get(f"{API_V1_URL}/analytics/")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Failed to get analytics: {e}")
            return {"error": str(e)}

# Initialize API client
@st.cache_resource
def get_api_client():
    return APIClient()

def initialize_session_state():
    """Initialize Streamlit session state"""
    if 'api_client' not in st.session_state:
        st.session_state.api_client = get_api_client()
    
    if 'current_page' not in st.session_state:
        st.session_state.current_page = "home"
    
    if 'messages' not in st.session_state:
        st.session_state.messages = []

def render_header():
    """Render the application header"""
    st.markdown("""
    <div style="text-align: center; padding: 2rem; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 1rem; margin-bottom: 2rem;">
        <h1 style="color: white; margin: 0; font-size: 2.5rem;">🚀 StudyMate API</h1>
        <p style="color: rgba(255,255,255,0.9); margin: 0.5rem 0 0 0; font-size: 1.2rem;">
            Advanced AI Academic Assistant with IBM Granite Integration
        </p>
    </div>
    """, unsafe_allow_html=True)

def render_sidebar():
    """Render the sidebar"""
    with st.sidebar:
        st.markdown("### 🧭 Navigation")
        
        pages = {
            "🏠 Home": "home",
            "🤖 Models": "models",
            "📁 Documents": "documents",
            "💬 Chat": "chat",
            "📊 Analytics": "analytics"
        }
        
        for page_name, page_key in pages.items():
            if st.button(page_name, key=f"nav_{page_key}", use_container_width=True):
                st.session_state.current_page = page_key
                st.rerun()
        
        st.markdown("---")
        
        # API Status
        st.markdown("### 🔌 API Status")
        health = st.session_state.api_client.get_health()
        
        if health.get("status") == "healthy":
            st.success("✅ API Connected")
            st.write(f"**Version:** {health.get('version', 'Unknown')}")
            st.write(f"**Models:** {len(health.get('models_available', []))}")
        else:
            st.error("❌ API Disconnected")
            if "error" in health:
                st.write(f"Error: {health['error']}")

def render_home_page():
    """Render the home page"""
    st.markdown("## Welcome to StudyMate API! 🎓")
    
    # API Information
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        ### 🚀 API Features
        - **IBM Granite Models** from HuggingFace
        - **FastAPI Backend** with async support
        - **FAISS Vector Database** for search
        - **JWT Authentication** system
        - **Real-time Q&A** processing
        - **Document Management** with PDF support
        """)
    
    with col2:
        st.markdown("""
        ### 📊 Current Status
        """)
        
        # Get API status
        health = st.session_state.api_client.get_health()
        analytics = st.session_state.api_client.get_analytics()
        
        if health.get("status") == "healthy":
            st.metric("API Status", "🟢 Healthy")
            st.metric("Available Models", len(health.get('models_available', [])))
            
            if not analytics.get("error"):
                st.metric("Documents", analytics.get('documents', {}).get('total', 0))
        else:
            st.metric("API Status", "🔴 Error")
    
    # Quick Actions
    st.markdown("### 🎯 Quick Actions")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🤖 View Models", use_container_width=True):
            st.session_state.current_page = "models"
            st.rerun()
    
    with col2:
        if st.button("📁 Upload Document", use_container_width=True):
            st.session_state.current_page = "documents"
            st.rerun()
    
    with col3:
        if st.button("💬 Start Chat", use_container_width=True):
            st.session_state.current_page = "chat"
            st.rerun()

def render_models_page():
    """Render the models page"""
    st.markdown("## 🤖 IBM Granite Models")
    
    # Get models data
    models_data = st.session_state.api_client.list_models()
    current_model_data = st.session_state.api_client.get_current_model()
    
    if models_data.get("error"):
        st.error(f"Failed to load models: {models_data['error']}")
        return
    
    # Current model info
    st.markdown("### 📍 Current Model")
    
    if not current_model_data.get("error"):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Model", current_model_data.get("name", "Unknown"))
        with col2:
            st.metric("Status", "🟢 Loaded" if current_model_data.get("loaded") else "🔴 Not Loaded")
        with col3:
            st.metric("Model ID", current_model_data.get("model_id", "Unknown"))
        
        st.info(current_model_data.get("description", "No description available"))
    
    # Available models
    st.markdown("### 📋 Available Models")
    
    models = models_data.get("models", [])
    
    for model in models:
        with st.expander(f"🤖 {model['name']}"):
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.write(f"**Description:** {model['description']}")
                st.write(f"**Model ID:** {model['model_id']}")
                st.write(f"**Status:** {model['status']}")
            
            with col2:
                if st.button(f"Switch to {model['model_id']}", key=f"switch_{model['model_id']}"):
                    with st.spinner("Switching model..."):
                        result = st.session_state.api_client.switch_model(model['model_id'])
                        
                        if result.get("success"):
                            st.success(f"✅ {result['message']}")
                            st.rerun()
                        else:
                            st.error(f"❌ Failed to switch: {result.get('error', 'Unknown error')}")

def render_documents_page():
    """Render the documents page"""
    st.markdown("## 📁 Document Management")
    
    # Upload section
    st.markdown("### 📤 Upload Documents")
    
    uploaded_files = st.file_uploader(
        "Choose PDF files",
        type=['pdf'],
        accept_multiple_files=True,
        help="Upload PDF documents for processing"
    )
    
    if uploaded_files:
        if st.button("🚀 Upload Documents", type="primary"):
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            for i, file in enumerate(uploaded_files):
                status_text.text(f"Uploading {file.name}...")
                
                result = st.session_state.api_client.upload_document(
                    file.getvalue(), 
                    file.name
                )
                
                if result.get("success"):
                    st.success(f"✅ {file.name} uploaded successfully")
                else:
                    st.error(f"❌ Failed to upload {file.name}: {result.get('error', 'Unknown error')}")
                
                progress_bar.progress((i + 1) / len(uploaded_files))
            
            status_text.text("Upload complete!")
            st.rerun()
    
    # Documents list
    st.markdown("### 📋 Uploaded Documents")
    
    documents_data = st.session_state.api_client.list_documents()
    
    if documents_data.get("error"):
        st.error(f"Failed to load documents: {documents_data['error']}")
    else:
        documents = documents_data.get("documents", [])
        
        if not documents:
            st.info("No documents uploaded yet.")
        else:
            for doc in documents:
                with st.expander(f"📄 {doc['filename']}"):
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.metric("Size", f"{doc.get('size', 0)} bytes")
                    with col2:
                        st.metric("Pages", doc.get('pages', 'Unknown'))
                    with col3:
                        st.metric("Chunks", doc.get('chunks', 'Unknown'))
                    
                    st.write(f"**Status:** {doc.get('status', 'Unknown')}")
                    st.write(f"**Uploaded:** {doc.get('uploaded_at', 'Unknown')}")

def render_chat_page():
    """Render the chat page"""
    st.markdown("## 💬 Chat with IBM Granite")
    
    # Model selection
    models_data = st.session_state.api_client.list_models()
    current_model_data = st.session_state.api_client.get_current_model()
    
    if not models_data.get("error") and not current_model_data.get("error"):
        st.info(f"🤖 Current Model: **{current_model_data.get('name', 'Unknown')}**")
    
    # Chat interface
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            
            if message["role"] == "assistant" and "metadata" in message:
                metadata = message["metadata"]
                
                with st.expander("📊 Response Details"):
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.metric("Model", metadata.get("model_used", "Unknown"))
                    with col2:
                        st.metric("Processing Time", f"{metadata.get('processing_time', 0):.2f}s")
                    with col3:
                        st.metric("Confidence", f"{metadata.get('confidence', 0):.2f}")
    
    # Chat input
    if prompt := st.chat_input("Ask a question about your documents..."):
        # Add user message
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Generate response
        with st.chat_message("assistant"):
            with st.spinner("🤖 IBM Granite is thinking..."):
                response = st.session_state.api_client.ask_question(prompt)
            
            if response.get("error"):
                st.error(f"Error: {response.get('answer', 'Unknown error')}")
            else:
                st.markdown(response["answer"])
                
                # Add assistant message with metadata
                assistant_message = {
                    "role": "assistant",
                    "content": response["answer"],
                    "metadata": {
                        "model_used": response.get("model_used", "Unknown"),
                        "processing_time": response.get("processing_time", 0),
                        "confidence": response.get("confidence", 0)
                    }
                }
                st.session_state.messages.append(assistant_message)
    
    # Chat controls
    if st.session_state.messages:
        if st.button("🗑️ Clear Chat"):
            st.session_state.messages = []
            st.rerun()

def render_analytics_page():
    """Render the analytics page"""
    st.markdown("## 📊 Analytics Dashboard")
    
    analytics = st.session_state.api_client.get_analytics()
    
    if analytics.get("error"):
        st.error(f"Failed to load analytics: {analytics['error']}")
        return
    
    # Overview metrics
    st.markdown("### 📈 Overview")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Documents", analytics.get('documents', {}).get('total', 0))
    
    with col2:
        st.metric("Total Pages", analytics.get('documents', {}).get('total_pages', 0))
    
    with col3:
        st.metric("Text Chunks", analytics.get('documents', {}).get('total_chunks', 0))
    
    with col4:
        st.metric("Conversations", analytics.get('conversations', {}).get('total', 0))
    
    # Model information
    st.markdown("### 🤖 Model Information")
    
    models_info = analytics.get('models', {})
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Available Models", models_info.get('available', 0))
    
    with col2:
        st.metric("Current Model", models_info.get('current', 'Unknown'))
    
    with col3:
        st.metric("Models Loaded", "✅ Yes" if models_info.get('loaded') else "❌ No")

def main():
    """Main application function"""
    st.set_page_config(
        page_title="StudyMate API",
        page_icon="🚀",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Initialize session state
    initialize_session_state()
    
    # Render header
    render_header()
    
    # Render sidebar
    render_sidebar()
    
    # Render main content
    current_page = st.session_state.current_page
    
    if current_page == "home":
        render_home_page()
    elif current_page == "models":
        render_models_page()
    elif current_page == "documents":
        render_documents_page()
    elif current_page == "chat":
        render_chat_page()
    elif current_page == "analytics":
        render_analytics_page()
    else:
        render_home_page()

if __name__ == "__main__":
    main()
