#!/usr/bin/env python3
"""
StudyMate with Authentication
Main application that requires login first
"""

import streamlit as st
import json
import time
import sys
from pathlib import Path

# Add paths
sys.path.append(str(Path(__file__).parent / "backend"))
sys.path.append(str(Path(__file__).parent / "frontend"))

# Authentication configuration
LOGIN_URL = "http://localhost:8506"

def check_authentication():
    """Check if user is authenticated"""
    # Check if user has valid authentication data in session state
    if 'authenticated' in st.session_state and st.session_state.authenticated:
        return True, st.session_state.get('user_data', {})
    
    # Check URL parameters for authentication from login redirect
    try:
        if hasattr(st, 'query_params'):
            query_params = st.query_params
            if 'auth' in query_params and query_params['auth'] == 'success':
                if 'user' in query_params and 'token' in query_params:
                    try:
                        user_data = json.loads(query_params['user'])
                        token = query_params['token']
                        
                        # Store authentication in session state
                        st.session_state.authenticated = True
                        st.session_state.user_data = user_data
                        st.session_state.auth_token = token
                        
                        # Clear URL parameters
                        st.query_params.clear()
                        
                        return True, user_data
                    except:
                        pass
    except:
        pass
    
    return False, None

def show_login_required():
    """Show login required page"""
    st.set_page_config(
        page_title="StudyMate - Login Required",
        page_icon="🔐",
        layout="centered"
    )
    
    st.markdown("""
    <style>
        .login-container {
            text-align: center;
            padding: 50px 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border-radius: 15px;
            margin: 50px 0;
            box-shadow: 0 10px 30px rgba(0,0,0,0.3);
        }
        .login-btn {
            background: rgba(255,255,255,0.2);
            color: white;
            padding: 15px 30px;
            text-decoration: none;
            border-radius: 8px;
            border: 2px solid white;
            font-size: 1.1rem;
            font-weight: bold;
            display: inline-block;
            margin: 20px 10px;
            transition: all 0.3s ease;
        }
        .login-btn:hover {
            background: rgba(255,255,255,0.3);
            transform: translateY(-2px);
        }
    </style>
    """, unsafe_allow_html=True)
    
    # Main container with gradient background
    st.markdown("""
    <div class="login-container">
        <h1>🔐 Authentication Required</h1>
        <h2>Welcome to StudyMate!</h2>
        <p style="font-size: 1.2rem; margin: 20px 0;">
            Please login or register to access your AI-powered academic assistant
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Login button
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🔑 Login / Register", use_container_width=True, type="primary"):
            st.markdown(f'<meta http-equiv="refresh" content="0; url={LOGIN_URL}">', unsafe_allow_html=True)

    st.markdown("---")

    # Feature showcase
    st.markdown("### ✨ What You'll Get Access To:")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("""
        #### 📚 Smart PDF Processing
        Upload and analyze your study documents with advanced AI

        #### 🤖 AI Q&A
        Ask questions and get instant, contextual answers
        """)

    with col2:
        st.markdown("""
        #### 📊 Analytics
        Track your study progress and insights

        #### 🔐 Secure
        Your data is protected and private
        """)

    # Call to action
    st.markdown("---")
    st.markdown("### 🎓 Transform your study experience with AI-powered document analysis")

    # Auto-redirect message
    st.info("💡 Click the button above to login, or you'll be redirected automatically in a few seconds...")

    # JavaScript redirect as backup
    st.markdown(f"""
    <script>
        setTimeout(function() {{
            window.location.href = '{LOGIN_URL}';
        }}, 5000);
    </script>
    """, unsafe_allow_html=True)
    
    # Note: Removed auto-refresh to prevent infinite loops
    # Users will click the login button or be redirected by JavaScript

def show_authenticated_app(user_data):
    """Show the main StudyMate application for authenticated users"""
    st.set_page_config(
        page_title="StudyMate - AI Academic Assistant",
        page_icon="📚",
        layout="wide"
    )
    
    # Sidebar with user info
    with st.sidebar:
        st.success(f"👤 Welcome {user_data.get('username', 'User')}!")
        st.info(f"📧 {user_data.get('email', 'No email')}")
        
        if st.button("🚪 Logout", use_container_width=True):
            # Clear authentication
            st.session_state.authenticated = False
            if 'user_data' in st.session_state:
                del st.session_state.user_data
            if 'auth_token' in st.session_state:
                del st.session_state.auth_token
            st.rerun()
        
        st.markdown("---")
        st.markdown("### 🧭 Navigation")
        
        # Simple navigation
        page = st.selectbox(
            "Choose a page:",
            ["🏠 Home", "📁 Upload Documents", "💬 Chat", "📊 Analytics", "⚙️ Settings"]
        )
    
    # Main content area
    st.title("📚 StudyMate - AI Academic Assistant")
    st.success(f"Welcome back, {user_data.get('username', 'User')}! 🎉")
    
    if page == "🏠 Home":
        show_home_page(user_data)
    elif page == "📁 Upload Documents":
        show_upload_page()
    elif page == "💬 Chat":
        show_chat_page()
    elif page == "📊 Analytics":
        show_analytics_page()
    elif page == "⚙️ Settings":
        show_settings_page(user_data)

def show_home_page(user_data):
    """Show home page"""
    st.markdown("## 🎓 Welcome to StudyMate!")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        ### ✨ Your AI Academic Assistant
        
        StudyMate helps you:
        - 📄 **Process PDF documents** with advanced text extraction
        - 🔍 **Search intelligently** through your study materials  
        - 💬 **Ask questions** and get contextual answers
        - 📊 **Track progress** with detailed analytics
        """)
    
    with col2:
        st.markdown("### 👤 Your Account")
        st.info(f"**Username:** {user_data.get('username', 'N/A')}")
        st.info(f"**Email:** {user_data.get('email', 'N/A')}")
        st.info(f"**User ID:** {user_data.get('id', 'N/A')}")
        st.info(f"**Member Since:** {user_data.get('created_at', 'N/A')[:10]}")
    
    # Quick actions
    st.markdown("### 🚀 Quick Actions")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📁 Upload Documents", use_container_width=True):
            st.info("Upload feature coming soon!")
    
    with col2:
        if st.button("💬 Start Chatting", use_container_width=True):
            st.info("Chat feature coming soon!")
    
    with col3:
        if st.button("📊 View Analytics", use_container_width=True):
            st.info("Analytics feature coming soon!")

def show_upload_page():
    """Show upload page"""
    st.markdown("## 📁 Upload Documents")
    st.info("📄 Document upload functionality will be integrated here")
    
    uploaded_file = st.file_uploader("Choose a PDF file", type=['pdf'])
    if uploaded_file:
        st.success(f"File uploaded: {uploaded_file.name}")

def show_chat_page():
    """Show chat page"""
    st.markdown("## 💬 Chat with Your Documents")
    st.info("🤖 AI chat functionality will be integrated here")
    
    if prompt := st.chat_input("Ask a question about your documents..."):
        st.write(f"You asked: {prompt}")
        st.write("🤖 AI response will appear here once integrated with your backend.")

def show_analytics_page():
    """Show analytics page"""
    st.markdown("## 📊 Analytics & Insights")
    st.info("📈 Analytics dashboard will be integrated here")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Documents", "0")
    with col2:
        st.metric("Questions Asked", "0")
    with col3:
        st.metric("Study Sessions", "1")

def show_settings_page(user_data):
    """Show settings page"""
    st.markdown("## ⚙️ Settings")
    
    st.markdown("### 👤 Account Information")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.text_input("Username", value=user_data.get('username', ''), disabled=True)
        st.text_input("Email", value=user_data.get('email', ''), disabled=True)
    
    with col2:
        st.text_input("Full Name", value=user_data.get('full_name', ''))
        st.text_input("User ID", value=user_data.get('id', ''), disabled=True)
    
    st.markdown("### 🔧 Application Settings")
    st.checkbox("Enable notifications")
    st.selectbox("Theme", ["Light", "Dark", "Auto"])

def main():
    """Main application function"""
    # Check authentication first
    is_authenticated, user_data = check_authentication()
    
    if not is_authenticated:
        show_login_required()
        return
    
    # User is authenticated, show main app
    show_authenticated_app(user_data)

if __name__ == "__main__":
    main()
