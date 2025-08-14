#!/usr/bin/env python3
"""
Authentication Bridge
Connects Flask login with Streamlit main app
"""

import streamlit as st
import requests
import json
from datetime import datetime
import os

# Configuration
API_BASE_URL = "http://localhost:8000"
LOGIN_URL = "http://localhost:8506"

def check_authentication():
    """Check if user is authenticated via Flask session or direct login"""
    
    # Check if user has a valid session token
    if 'auth_token' in st.session_state and 'user_data' in st.session_state:
        return True, st.session_state.user_data
    
    # Check URL parameters for authentication data (from Flask redirect)
    query_params = st.experimental_get_query_params()
    if 'token' in query_params and 'user' in query_params:
        try:
            token = query_params['token'][0]
            user_data = json.loads(query_params['user'][0])
            
            # Verify token with backend
            if verify_token(token):
                st.session_state.auth_token = token
                st.session_state.user_data = user_data
                return True, user_data
        except:
            pass
    
    return False, None

def verify_token(token):
    """Verify authentication token with backend"""
    try:
        response = requests.get(f"{API_BASE_URL}/auth/me", 
                              headers={"Authorization": f"Bearer {token}"},
                              timeout=5)
        return response.status_code == 200
    except:
        return False

def show_login_required():
    """Show login required message with redirect to login page"""
    st.markdown("""
    <div style="text-align: center; padding: 50px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; border-radius: 10px; margin: 20px 0;">
        <h1>🔐 Authentication Required</h1>
        <p style="font-size: 1.2rem; margin: 20px 0;">
            Please login to access StudyMate features
        </p>
        <p style="margin: 30px 0;">
            <a href="http://localhost:8506" target="_blank" 
               style="background: rgba(255,255,255,0.2); color: white; padding: 12px 24px; 
                      text-decoration: none; border-radius: 5px; border: 2px solid white;">
                🔑 Go to Login Page
            </a>
        </p>
        <p style="font-size: 0.9rem; opacity: 0.8;">
            After logging in, you'll be redirected back to this application
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Auto-refresh every 5 seconds to check for authentication
    st.markdown("""
    <script>
        setTimeout(function() {
            window.location.reload();
        }, 5000);
    </script>
    """, unsafe_allow_html=True)

def show_user_info(user_data):
    """Show authenticated user information"""
    with st.sidebar:
        st.success(f"👤 Welcome {user_data['username']}!")
        st.info(f"📧 {user_data['email']}")
        
        if st.button("🚪 Logout"):
            # Clear session
            if 'auth_token' in st.session_state:
                del st.session_state.auth_token
            if 'user_data' in st.session_state:
                del st.session_state.user_data
            st.rerun()

def require_authentication(func):
    """Decorator to require authentication for Streamlit functions"""
    def wrapper(*args, **kwargs):
        is_authenticated, user_data = check_authentication()
        
        if not is_authenticated:
            show_login_required()
            return None
        
        # Show user info in sidebar
        show_user_info(user_data)
        
        # Call the original function
        return func(*args, **kwargs)
    
    return wrapper

# Example usage in main app
def integrate_with_main_app():
    """Integration example for main app.py"""
    
    st.set_page_config(
        page_title="StudyMate - AI Academic Assistant",
        page_icon="📚",
        layout="wide"
    )
    
    # Check authentication
    is_authenticated, user_data = check_authentication()
    
    if not is_authenticated:
        show_login_required()
        return
    
    # User is authenticated, show main app
    show_user_info(user_data)
    
    st.title("📚 StudyMate - AI Academic Assistant")
    st.success(f"Welcome back, {user_data['username']}! 🎉")
    
    # Your main app content goes here
    st.write("Your authenticated StudyMate application content...")
    
    # Example: Show user-specific data
    st.subheader("👤 Your Account")
    col1, col2 = st.columns(2)
    
    with col1:
        st.info(f"**Username:** {user_data['username']}")
        st.info(f"**Email:** {user_data['email']}")
    
    with col2:
        st.info(f"**User ID:** {user_data['id']}")
        st.info(f"**Account Created:** {user_data['created_at'][:10]}")

if __name__ == "__main__":
    integrate_with_main_app()
