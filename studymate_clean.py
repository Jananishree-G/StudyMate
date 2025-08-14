#!/usr/bin/env python3
"""
StudyMate with Clean Authentication
Simple, working authentication system
"""

import streamlit as st
import json
import sys
from pathlib import Path

# Add paths
sys.path.append(str(Path(__file__).parent / "backend"))
sys.path.append(str(Path(__file__).parent / "frontend"))

# Configuration
LOGIN_URL = "http://localhost:8506"

def check_authentication():
    """Check if user is authenticated"""
    # Check session state first
    if 'authenticated' in st.session_state and st.session_state.authenticated:
        return True, st.session_state.get('user_data', {})
    
    # Check URL parameters for auth data (with fallback for older Streamlit)
    try:
        # Try new query_params API
        if hasattr(st, 'query_params'):
            query_params = st.query_params
            if 'auth' in query_params and query_params['auth'] == 'success':
                if 'user' in query_params:
                    user_data = json.loads(query_params['user'])
                    st.session_state.authenticated = True
                    st.session_state.user_data = user_data
                    st.query_params.clear()
                    return True, user_data
        else:
            # Fallback for older Streamlit versions
            query_params = st.experimental_get_query_params()
            if 'auth' in query_params and query_params['auth'][0] == 'success':
                if 'user' in query_params:
                    user_data = json.loads(query_params['user'][0])
                    st.session_state.authenticated = True
                    st.session_state.user_data = user_data
                    st.experimental_set_query_params()
                    return True, user_data
    except:
        pass
    
    return False, None

def show_login_required():
    """Show clean login required page"""
    st.title("🔐 StudyMate - Login Required")
    
    st.markdown("""
    ### Welcome to StudyMate!
    
    Your AI-powered academic assistant for document analysis and Q&A.
    
    **Please login to continue:**
    """)
    
    # Simple login button
    if st.button("🔑 Go to Login Page", type="primary", use_container_width=True):
        st.markdown(f'<meta http-equiv="refresh" content="0; url={LOGIN_URL}">', unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Feature preview
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        **📚 Features you'll get:**
        - Smart PDF processing
        - AI-powered Q&A
        - Document analytics
        - Secure data storage
        """)
    
    with col2:
        st.markdown("""
        **🎯 Quick Start:**
        1. Click login button above
        2. Login or register
        3. Get redirected back here
        4. Start using StudyMate!
        """)
    
    st.info("💡 After logging in, you'll be automatically redirected back to this application.")

def show_main_app(user_data):
    """Show the main StudyMate application"""
    st.title("📚 StudyMate - AI Academic Assistant")
    
    # Sidebar with user info
    with st.sidebar:
        st.success(f"👤 Welcome {user_data.get('username', 'User')}!")
        st.write(f"📧 {user_data.get('email', 'No email')}")
        
        if st.button("🚪 Logout"):
            st.session_state.authenticated = False
            if 'user_data' in st.session_state:
                del st.session_state.user_data
            st.rerun()
        
        st.markdown("---")
        
        # Navigation
        page = st.selectbox(
            "Navigate:",
            ["🏠 Home", "📁 Upload", "💬 Chat", "📊 Analytics", "⚙️ Settings"]
        )
    
    # Main content
    st.success(f"🎉 Welcome back, {user_data.get('username', 'User')}!")
    
    if page == "🏠 Home":
        show_home(user_data)
    elif page == "📁 Upload":
        show_upload()
    elif page == "💬 Chat":
        show_chat()
    elif page == "📊 Analytics":
        show_analytics()
    elif page == "⚙️ Settings":
        show_settings(user_data)

def show_home(user_data):
    """Home page"""
    st.markdown("## 🏠 Home Dashboard")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Documents", "0", help="PDFs uploaded")
    with col2:
        st.metric("Questions", "0", help="AI questions asked")
    with col3:
        st.metric("Sessions", "1", help="Study sessions")
    
    st.markdown("### 👤 Your Account")
    st.json({
        "username": user_data.get('username', 'N/A'),
        "email": user_data.get('email', 'N/A'),
        "user_id": user_data.get('id', 'N/A'),
        "created": user_data.get('created_at', 'N/A')[:19] if user_data.get('created_at') else 'N/A'
    })
    
    st.markdown("### 🚀 Quick Actions")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📁 Upload PDF", use_container_width=True):
            st.info("Upload feature - integrate with your backend")
    
    with col2:
        if st.button("💬 Start Chat", use_container_width=True):
            st.info("Chat feature - integrate with your AI backend")
    
    with col3:
        if st.button("📊 View Stats", use_container_width=True):
            st.info("Analytics feature - integrate with your data")

def show_upload():
    """Upload page"""
    st.markdown("## 📁 Document Upload")
    
    uploaded_file = st.file_uploader("Choose a PDF file", type=['pdf'])
    
    if uploaded_file:
        st.success(f"✅ File ready: {uploaded_file.name}")
        st.info("💡 Integrate this with your PDF processing backend")
        
        if st.button("🚀 Process Document"):
            st.success("Document processing would happen here!")

def show_chat():
    """Chat page"""
    st.markdown("## 💬 AI Chat")
    
    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # Chat input
    if prompt := st.chat_input("Ask a question about your documents..."):
        # Add user message
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Add assistant response
        response = f"🤖 I would answer: '{prompt}' (integrate with your AI backend)"
        st.session_state.messages.append({"role": "assistant", "content": response})
        with st.chat_message("assistant"):
            st.markdown(response)

def show_analytics():
    """Analytics page"""
    st.markdown("## 📊 Analytics Dashboard")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Documents", "0")
    with col2:
        st.metric("Total Questions", "0")
    with col3:
        st.metric("Avg Confidence", "0%")
    with col4:
        st.metric("Study Time", "0h")
    
    st.markdown("### 📈 Usage Over Time")
    st.line_chart({"Usage": [1, 2, 3, 2, 4, 3, 5]})
    
    st.info("💡 Integrate with your analytics backend for real data")

def show_settings(user_data):
    """Settings page"""
    st.markdown("## ⚙️ Settings")
    
    st.markdown("### 👤 Account Information")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.text_input("Username", value=user_data.get('username', ''), disabled=True)
        st.text_input("Email", value=user_data.get('email', ''), disabled=True)
    
    with col2:
        st.text_input("Full Name", value=user_data.get('full_name', ''))
        st.text_input("User ID", value=user_data.get('id', ''), disabled=True)
    
    st.markdown("### 🔧 Preferences")
    st.checkbox("Enable notifications")
    st.selectbox("Theme", ["Light", "Dark", "Auto"])
    st.slider("Max documents", 1, 100, 10)

def main():
    """Main application"""
    st.set_page_config(
        page_title="StudyMate",
        page_icon="📚",
        layout="wide"
    )
    
    # Check authentication
    is_authenticated, user_data = check_authentication()
    
    if not is_authenticated:
        show_login_required()
    else:
        show_main_app(user_data)

if __name__ == "__main__":
    main()
