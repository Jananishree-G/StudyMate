#!/usr/bin/env python3
"""
Simple StudyMate Login App
Simplified version to test login functionality
"""

import streamlit as st
import requests
import json
from datetime import datetime

# Configuration
API_BASE_URL = "http://localhost:8000"

# Page configuration
st.set_page_config(
    page_title="StudyMate - Login",
    page_icon="📚",
    layout="centered"
)

# Initialize session state
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'user' not in st.session_state:
    st.session_state.user = None
if 'token' not in st.session_state:
    st.session_state.token = None

def test_api_connection():
    """Test API connection"""
    try:
        response = requests.get(f"{API_BASE_URL}/")
        return response.status_code == 200
    except:
        return False

def login_user(username, password):
    """Login user"""
    try:
        response = requests.post(f"{API_BASE_URL}/auth/login", json={
            "username": username,
            "password": password
        })
        
        if response.status_code == 200:
            result = response.json()
            st.session_state.authenticated = True
            st.session_state.user = result["user"]
            st.session_state.token = result["access_token"]
            return True, "Login successful!"
        else:
            error = response.json()
            return False, error.get("detail", "Login failed")
    except Exception as e:
        return False, f"Connection error: {str(e)}"

def register_user(username, email, password, full_name=""):
    """Register user"""
    try:
        response = requests.post(f"{API_BASE_URL}/auth/register", json={
            "username": username,
            "email": email,
            "password": password,
            "full_name": full_name
        })
        
        if response.status_code == 200:
            result = response.json()
            st.session_state.authenticated = True
            st.session_state.user = result["user"]
            st.session_state.token = result["access_token"]
            return True, "Registration successful!"
        else:
            error = response.json()
            return False, error.get("detail", "Registration failed")
    except Exception as e:
        return False, f"Connection error: {str(e)}"

def logout_user():
    """Logout user"""
    st.session_state.authenticated = False
    st.session_state.user = None
    st.session_state.token = None

def show_login_page():
    """Show login page"""
    st.title("📚 StudyMate - AI Academic Assistant")
    st.markdown("---")
    
    # Check API connection
    if not test_api_connection():
        st.error("⚠️ Cannot connect to backend API!")
        st.info("Please ensure the backend server is running:")
        st.code("python backend_api.py", language="bash")
        return
    
    st.success("✅ Backend API is connected")
    
    # Login/Register tabs
    tab1, tab2 = st.tabs(["🔑 Login", "📝 Register"])
    
    with tab1:
        st.subheader("Login to StudyMate")
        
        with st.form("login_form"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            login_btn = st.form_submit_button("🔑 Login")
            
            if login_btn:
                if username and password:
                    with st.spinner("Logging in..."):
                        success, message = login_user(username, password)
                    
                    if success:
                        st.success(message)
                        st.rerun()
                    else:
                        st.error(message)
                else:
                    st.error("Please enter both username and password")
    
    with tab2:
        st.subheader("Create New Account")
        
        with st.form("register_form"):
            reg_username = st.text_input("Username*")
            reg_email = st.text_input("Email*")
            reg_full_name = st.text_input("Full Name (optional)")
            reg_password = st.text_input("Password*", type="password")
            reg_confirm = st.text_input("Confirm Password*", type="password")
            register_btn = st.form_submit_button("📝 Register")
            
            if register_btn:
                if reg_username and reg_email and reg_password and reg_confirm:
                    if reg_password == reg_confirm:
                        if len(reg_password) >= 6:
                            with st.spinner("Creating account..."):
                                success, message = register_user(reg_username, reg_email, reg_password, reg_full_name)
                            
                            if success:
                                st.success(message)
                                st.rerun()
                            else:
                                st.error(message)
                        else:
                            st.error("Password must be at least 6 characters")
                    else:
                        st.error("Passwords do not match")
                else:
                    st.error("Please fill in all required fields")

def show_dashboard():
    """Show user dashboard"""
    st.title(f"Welcome, {st.session_state.user['username']}! 👋")
    st.markdown("---")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.subheader("📊 Your Dashboard")
        st.info("🎉 You are successfully logged in!")
        
        st.markdown("### 📋 Available Features:")
        st.markdown("""
        - ✅ **Secure Authentication** - Your account is protected
        - ✅ **PDF Upload** - Upload and process documents
        - ✅ **AI Chat** - Ask questions about your documents
        - ✅ **Document Management** - Organize your files
        - ✅ **Conversation History** - Track your interactions
        """)
        
        st.markdown("### 👤 Your Account:")
        st.write(f"**Username:** {st.session_state.user['username']}")
        st.write(f"**Email:** {st.session_state.user['email']}")
        st.write(f"**Account ID:** {st.session_state.user['id']}")
        st.write(f"**Created:** {st.session_state.user['created_at'][:10]}")
    
    with col2:
        if st.button("🚪 Logout", type="primary"):
            logout_user()
            st.success("Logged out successfully!")
            st.rerun()

def main():
    """Main application"""
    if not st.session_state.authenticated:
        show_login_page()
    else:
        show_dashboard()

if __name__ == "__main__":
    main()
