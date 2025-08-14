#!/usr/bin/env python3
"""
StudyMate Frontend Application
Streamlit app with authentication, PDF management, and chatbot
"""

import streamlit as st
import requests
import json
from typing import Dict, List, Optional
from datetime import datetime
import time

# Configuration
API_BASE_URL = "http://localhost:8000"

# Page configuration
st.set_page_config(
    page_title="StudyMate - AI Academic Assistant",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
    }
    .login-container {
        max-width: 400px;
        margin: 0 auto;
        padding: 2rem;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        background: white;
    }
    .chat-message {
        padding: 1rem;
        margin: 0.5rem 0;
        border-radius: 10px;
        border-left: 4px solid #667eea;
        background: #f8f9fa;
    }
    .user-message {
        background: #e3f2fd;
        border-left-color: #2196f3;
    }
    .assistant-message {
        background: #f3e5f5;
        border-left-color: #9c27b0;
    }
    .document-card {
        border: 1px solid #ddd;
        border-radius: 8px;
        padding: 1rem;
        margin: 0.5rem 0;
        background: white;
    }
    .success-message {
        background: #d4edda;
        color: #155724;
        padding: 0.75rem;
        border-radius: 5px;
        border: 1px solid #c3e6cb;
    }
    .error-message {
        background: #f8d7da;
        color: #721c24;
        padding: 0.75rem;
        border-radius: 5px;
        border: 1px solid #f5c6cb;
    }
</style>
""", unsafe_allow_html=True)

# Session state initialization
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'user' not in st.session_state:
    st.session_state.user = None
if 'token' not in st.session_state:
    st.session_state.token = None
if 'login_time' not in st.session_state:
    st.session_state.login_time = None
if 'documents' not in st.session_state:
    st.session_state.documents = []
if 'selected_document' not in st.session_state:
    st.session_state.selected_document = None
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'current_page' not in st.session_state:
    st.session_state.current_page = "📄 Document Management"

# API helper functions
def make_api_request(endpoint: str, method: str = "GET", data: Dict = None, files: Dict = None, auth: bool = True):
    """Make API request with error handling"""
    url = f"{API_BASE_URL}{endpoint}"
    headers = {}
    
    if auth and st.session_state.token:
        headers["Authorization"] = f"Bearer {st.session_state.token}"
    
    try:
        if method == "GET":
            response = requests.get(url, headers=headers)
        elif method == "POST":
            if files:
                response = requests.post(url, headers=headers, files=files, data=data)
            else:
                headers["Content-Type"] = "application/json"
                response = requests.post(url, headers=headers, json=data)
        elif method == "PUT":
            headers["Content-Type"] = "application/json"
            response = requests.put(url, headers=headers, json=data)
        elif method == "DELETE":
            response = requests.delete(url, headers=headers)
        
        if response.status_code == 200 or response.status_code == 201:
            return {"success": True, "data": response.json()}
        else:
            return {"success": False, "error": response.json().get("detail", "Unknown error")}
    
    except requests.exceptions.ConnectionError:
        return {"success": False, "error": "Cannot connect to API server. Please ensure the backend is running."}
    except Exception as e:
        return {"success": False, "error": str(e)}

def login_user(username: str, password: str):
    """Login user"""
    result = make_api_request("/auth/login", "POST", {"username": username, "password": password}, auth=False)
    
    if result["success"]:
        st.session_state.authenticated = True
        st.session_state.user = result["data"]["user"]
        st.session_state.token = result["data"]["access_token"]
        st.session_state.login_time = datetime.now()
        return True, "Login successful!"
    else:
        return False, result["error"]

def register_user(username: str, email: str, password: str, full_name: str = ""):
    """Register new user"""
    result = make_api_request("/auth/register", "POST", {
        "username": username,
        "email": email,
        "password": password,
        "full_name": full_name
    }, auth=False)
    
    if result["success"]:
        st.session_state.authenticated = True
        st.session_state.user = result["data"]["user"]
        st.session_state.token = result["data"]["access_token"]
        st.session_state.login_time = datetime.now()
        return True, "Registration successful!"
    else:
        return False, result["error"]

def logout_user():
    """Logout user"""
    st.session_state.authenticated = False
    st.session_state.user = None
    st.session_state.token = None
    st.session_state.login_time = None
    st.session_state.documents = []
    st.session_state.selected_document = None
    st.session_state.chat_history = []
    st.session_state.current_page = "📄 Document Management"

def check_session_timeout():
    """Check if user session has timed out"""
    if st.session_state.authenticated and st.session_state.login_time:
        time_elapsed = datetime.now() - st.session_state.login_time
        # Session timeout after 2 hours
        if time_elapsed.total_seconds() > 7200:  # 2 hours
            st.warning("⏰ Your session has expired. Please login again.")
            logout_user()
            return True
    return False

def load_user_documents():
    """Load user's documents"""
    result = make_api_request("/documents")
    if result["success"]:
        st.session_state.documents = result["data"]
        return True
    return False

def upload_document(uploaded_file):
    """Upload document"""
    files = {"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
    result = make_api_request("/documents/upload", "POST", files=files)
    
    if result["success"]:
        load_user_documents()  # Refresh documents list
        return True, "Document uploaded and processed successfully!"
    else:
        return False, result["error"]

def chat_with_document(message: str, document_id: str):
    """Chat with document"""
    result = make_api_request("/chat", "POST", {"message": message, "document_id": document_id})
    
    if result["success"]:
        return True, result["data"]
    else:
        return False, result["error"]

# Authentication page
def show_auth_page():
    """Show authentication page"""
    st.markdown('<div class="main-header"><h1>📚 StudyMate</h1><p>AI Academic Assistant with Document Intelligence</p></div>', unsafe_allow_html=True)
    
    # Check API connection
    api_status = make_api_request("/", auth=False)
    if not api_status["success"]:
        st.error("⚠️ Cannot connect to backend API. Please ensure the backend server is running on http://localhost:8000")
        st.info("To start the backend, run: `python backend_api.py`")
        st.code("python backend_api.py", language="bash")

        with st.expander("🔧 Troubleshooting"):
            st.markdown("""
            **Common issues:**
            1. **Backend not running**: Start the backend API server
            2. **Port conflict**: Check if port 8000 is available
            3. **Dependencies missing**: Install required packages
            4. **Database issues**: Ensure database is initialized

            **Quick fix:**
            ```bash
            # Start the complete system
            python start_studymate.py
            ```
            """)
        return
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown('<div class="login-container">', unsafe_allow_html=True)
        
        tab1, tab2 = st.tabs(["🔑 Login", "📝 Register"])
        
        with tab1:
            st.subheader("Login to StudyMate")
            
            with st.form("login_form"):
                username = st.text_input("Username", placeholder="Enter your username")
                password = st.text_input("Password", type="password", placeholder="Enter your password")
                login_button = st.form_submit_button("🔑 Login", use_container_width=True)
                
                if login_button:
                    if username and password:
                        with st.spinner("Logging in..."):
                            success, message = login_user(username, password)
                        
                        if success:
                            st.success(message)
                            time.sleep(1)
                            st.rerun()
                        else:
                            st.error(message)
                    else:
                        st.error("Please fill in all fields")
        
        with tab2:
            st.subheader("Create Account")
            
            with st.form("register_form"):
                reg_username = st.text_input("Username", placeholder="Choose a username")
                reg_email = st.text_input("Email", placeholder="Enter your email")
                reg_full_name = st.text_input("Full Name", placeholder="Enter your full name (optional)")
                reg_password = st.text_input("Password", type="password", placeholder="Choose a password")
                reg_confirm_password = st.text_input("Confirm Password", type="password", placeholder="Confirm your password")
                register_button = st.form_submit_button("📝 Register", use_container_width=True)
                
                if register_button:
                    if reg_username and reg_email and reg_password and reg_confirm_password:
                        if reg_password == reg_confirm_password:
                            if len(reg_password) >= 6:
                                with st.spinner("Creating account..."):
                                    success, message = register_user(reg_username, reg_email, reg_password, reg_full_name)
                                
                                if success:
                                    st.success(message)
                                    time.sleep(1)
                                    st.rerun()
                                else:
                                    st.error(message)
                            else:
                                st.error("Password must be at least 6 characters long")
                        else:
                            st.error("Passwords do not match")
                    else:
                        st.error("Please fill in all required fields")
        
        st.markdown('</div>', unsafe_allow_html=True)

# Main application
def show_main_app():
    """Show main application"""
    # Header
    col1, col2, col3 = st.columns([3, 1, 1])
    with col1:
        st.markdown(f'<div class="main-header"><h2>📚 Welcome, {st.session_state.user["username"]}!</h2></div>', unsafe_allow_html=True)
    with col3:
        if st.button("🚪 Logout", use_container_width=True):
            logout_user()
            st.rerun()
    
    # Sidebar
    with st.sidebar:
        st.header("📋 Navigation")
        
        page = st.selectbox("Choose a page:", [
            "📄 Document Management",
            "💬 Chat with Documents",
            "📊 Dashboard",
            "⚙️ Settings"
        ], index=["📄 Document Management", "💬 Chat with Documents", "📊 Dashboard", "⚙️ Settings"].index(st.session_state.current_page) if st.session_state.current_page in ["📄 Document Management", "💬 Chat with Documents", "📊 Dashboard", "⚙️ Settings"] else 0)

        # Update current page when selection changes
        if page != st.session_state.current_page:
            st.session_state.current_page = page
            st.rerun()
    
    # Load documents if not loaded
    if not st.session_state.documents:
        load_user_documents()
    
    # Page routing
    if st.session_state.current_page == "📄 Document Management":
        show_document_management()
    elif st.session_state.current_page == "💬 Chat with Documents":
        show_chat_interface()
    elif st.session_state.current_page == "📊 Dashboard":
        show_dashboard()
    elif st.session_state.current_page == "⚙️ Settings":
        show_settings()

def show_document_management():
    """Show document management page"""
    st.header("📄 Document Management")
    
    # Upload section
    st.subheader("📤 Upload New Document")
    
    uploaded_file = st.file_uploader(
        "Choose a PDF file",
        type=['pdf'],
        help="Upload PDF documents to chat with them using AI"
    )
    
    if uploaded_file is not None:
        col1, col2 = st.columns([3, 1])
        with col1:
            st.info(f"📄 Selected: {uploaded_file.name} ({uploaded_file.size / 1024:.1f} KB)")
        with col2:
            if st.button("🚀 Upload & Process", use_container_width=True):
                with st.spinner("Uploading and processing document..."):
                    success, message = upload_document(uploaded_file)
                
                if success:
                    st.success(message)
                    st.rerun()
                else:
                    st.error(message)
    
    # Documents list
    st.subheader("📚 Your Documents")
    
    if st.session_state.documents:
        for doc in st.session_state.documents:
            with st.container():
                st.markdown('<div class="document-card">', unsafe_allow_html=True)
                
                col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
                
                with col1:
                    st.write(f"**📄 {doc['filename']}**")
                    st.caption(f"Size: {doc['file_size'] / 1024:.1f} KB | Chunks: {doc['chunk_count']} | Status: {doc['status']}")
                
                with col2:
                    status_color = "🟢" if doc['status'] == 'processed' else "🟡" if doc['status'] == 'processing' else "🔴"
                    st.write(f"{status_color} {doc['status'].title()}")
                
                with col3:
                    st.caption(f"📅 {doc['created_at'][:10]}")
                
                with col4:
                    if st.button("💬 Chat", key=f"chat_{doc['id']}", use_container_width=True):
                        st.session_state.selected_document = doc
                        st.session_state.current_page = "💬 Chat with Documents"
                        st.rerun()
                
                st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.info("📭 No documents uploaded yet. Upload your first PDF to get started!")

def show_chat_interface():
    """Show chat interface"""
    st.header("💬 Chat with Documents")

    if not st.session_state.documents:
        st.warning("📭 No documents available. Please upload a document first.")
        return

    # Document selection
    st.subheader("📄 Select Document")

    doc_options = {doc['filename']: doc for doc in st.session_state.documents if doc['status'] == 'processed'}

    if not doc_options:
        st.warning("⚠️ No processed documents available. Please wait for your documents to be processed.")
        return

    selected_doc_name = st.selectbox(
        "Choose a document to chat with:",
        options=list(doc_options.keys()),
        index=0 if not st.session_state.selected_document else
              list(doc_options.keys()).index(st.session_state.selected_document['filename'])
              if st.session_state.selected_document['filename'] in doc_options else 0
    )

    selected_doc = doc_options[selected_doc_name]
    st.session_state.selected_document = selected_doc

    st.info(f"💬 Chatting with: **{selected_doc['filename']}** ({selected_doc['chunk_count']} chunks)")

    # Chat interface
    st.subheader("🤖 AI Assistant")

    # Chat history
    chat_container = st.container()

    with chat_container:
        if st.session_state.chat_history:
            for i, message in enumerate(st.session_state.chat_history):
                if message['role'] == 'user':
                    st.markdown(f'<div class="chat-message user-message"><strong>👤 You:</strong><br>{message["content"]}</div>', unsafe_allow_html=True)
                else:
                    st.markdown(f'<div class="chat-message assistant-message"><strong>🤖 AI:</strong><br>{message["content"]}</div>', unsafe_allow_html=True)

                    # Show sources if available
                    if message.get('sources'):
                        with st.expander("📚 Sources"):
                            for source in message['sources']:
                                st.write(f"**Page {source['page']}:** {source['text']}")
        else:
            st.info("💭 Start a conversation by asking a question about your document!")

    # Chat input
    with st.form("chat_form", clear_on_submit=True):
        user_question = st.text_area(
            "Ask a question about your document:",
            placeholder="What is this document about? Can you summarize the main points?",
            height=100
        )

        col1, col2 = st.columns([4, 1])
        with col2:
            send_button = st.form_submit_button("🚀 Send", use_container_width=True)

        if send_button and user_question.strip():
            # Add user message to history
            st.session_state.chat_history.append({
                'role': 'user',
                'content': user_question,
                'timestamp': datetime.now().isoformat()
            })

            # Get AI response
            with st.spinner("🤖 AI is thinking..."):
                success, response = chat_with_document(user_question, selected_doc['id'])

            if success:
                # Add AI response to history
                st.session_state.chat_history.append({
                    'role': 'assistant',
                    'content': response['response'],
                    'sources': response.get('sources', []),
                    'confidence': response.get('confidence', 0.0),
                    'timestamp': datetime.now().isoformat()
                })

                st.rerun()
            else:
                st.error(f"❌ Error: {response}")

def show_dashboard():
    """Show dashboard"""
    st.header("📊 Dashboard")

    # Statistics
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("📄 Total Documents", len(st.session_state.documents))

    with col2:
        processed_docs = len([doc for doc in st.session_state.documents if doc['status'] == 'processed'])
        st.metric("✅ Processed", processed_docs)

    with col3:
        total_chunks = sum(doc['chunk_count'] for doc in st.session_state.documents)
        st.metric("📝 Total Chunks", total_chunks)

    with col4:
        total_size = sum(doc['file_size'] for doc in st.session_state.documents) / (1024 * 1024)
        st.metric("💾 Total Size", f"{total_size:.1f} MB")

    # Recent activity
    st.subheader("📈 Recent Activity")

    if st.session_state.documents:
        # Sort documents by creation date
        recent_docs = sorted(st.session_state.documents, key=lambda x: x['created_at'], reverse=True)[:5]

        for doc in recent_docs:
            with st.container():
                col1, col2, col3 = st.columns([3, 1, 1])
                with col1:
                    st.write(f"📄 **{doc['filename']}**")
                with col2:
                    status_emoji = "✅" if doc['status'] == 'processed' else "⏳" if doc['status'] == 'processing' else "❌"
                    st.write(f"{status_emoji} {doc['status'].title()}")
                with col3:
                    st.write(f"📅 {doc['created_at'][:10]}")
    else:
        st.info("📭 No activity yet. Upload your first document to get started!")

    # Chat statistics
    if st.session_state.chat_history:
        st.subheader("💬 Chat Statistics")

        total_messages = len(st.session_state.chat_history)
        user_messages = len([msg for msg in st.session_state.chat_history if msg['role'] == 'user'])

        col1, col2 = st.columns(2)
        with col1:
            st.metric("💬 Total Messages", total_messages)
        with col2:
            st.metric("❓ Questions Asked", user_messages)

def show_settings():
    """Show settings page"""
    st.header("⚙️ Settings")

    # User information
    st.subheader("👤 User Information")

    col1, col2 = st.columns(2)
    with col1:
        st.info(f"**Username:** {st.session_state.user['username']}")
        st.info(f"**Email:** {st.session_state.user['email']}")
    with col2:
        st.info(f"**Full Name:** {st.session_state.user.get('full_name', 'Not provided')}")
        st.info(f"**Account Created:** {st.session_state.user['created_at'][:10]}")

    # Application settings
    st.subheader("🔧 Application Settings")

    # Clear chat history
    if st.button("🗑️ Clear Chat History", type="secondary"):
        st.session_state.chat_history = []
        st.success("Chat history cleared!")
        st.rerun()

    # Refresh documents
    if st.button("🔄 Refresh Documents", type="secondary"):
        load_user_documents()
        st.success("Documents refreshed!")
        st.rerun()

    # API status
    st.subheader("🔌 API Status")
    api_status = make_api_request("/", auth=False)
    if api_status["success"]:
        st.success("✅ API connection is healthy")
        st.json(api_status["data"])
    else:
        st.error("❌ API connection failed")
        st.error(api_status["error"])

# Main app logic
def main():
    """Main application logic"""
    # Check session timeout first
    if check_session_timeout():
        st.rerun()

    if not st.session_state.authenticated:
        show_auth_page()
    else:
        show_main_app()

if __name__ == "__main__":
    main()
