#!/usr/bin/env python3
"""
Minimal StudyMate Login Page
Simple, working login interface
"""

import streamlit as st
import requests

# Page config
st.set_page_config(page_title="StudyMate Login", page_icon="📚")

# Initialize session state
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'user' not in st.session_state:
    st.session_state.user = None

def test_backend():
    """Test if backend is running"""
    try:
        response = requests.get("http://localhost:8000/", timeout=5)
        return response.status_code == 200
    except:
        return False

def login_user(username, password):
    """Login user"""
    try:
        response = requests.post("http://localhost:8000/auth/login", 
                               json={"username": username, "password": password},
                               timeout=10)
        if response.status_code == 200:
            data = response.json()
            st.session_state.authenticated = True
            st.session_state.user = data["user"]
            return True, "Login successful!"
        else:
            error = response.json()
            return False, error.get("detail", "Login failed")
    except Exception as e:
        return False, f"Connection error: {str(e)}"

def register_user(username, email, password):
    """Register user"""
    try:
        response = requests.post("http://localhost:8000/auth/register",
                               json={"username": username, "email": email, "password": password},
                               timeout=10)
        if response.status_code == 200:
            data = response.json()
            st.session_state.authenticated = True
            st.session_state.user = data["user"]
            return True, "Registration successful!"
        else:
            error = response.json()
            return False, error.get("detail", "Registration failed")
    except Exception as e:
        return False, f"Connection error: {str(e)}"

def show_login():
    """Show login page"""
    st.title("📚 StudyMate Login")
    
    # Check backend
    if not test_backend():
        st.error("❌ Backend not running!")
        st.info("Start backend: python backend_api.py")
        return
    
    st.success("✅ Backend connected")
    
    # Login form
    with st.form("login_form"):
        st.subheader("🔑 Login")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        login_btn = st.form_submit_button("Login")
        
        if login_btn and username and password:
            success, message = login_user(username, password)
            if success:
                st.success(message)
                st.rerun()
            else:
                st.error(message)
    
    st.markdown("---")
    
    # Register form
    with st.form("register_form"):
        st.subheader("📝 Register")
        reg_username = st.text_input("New Username")
        reg_email = st.text_input("Email")
        reg_password = st.text_input("New Password", type="password")
        register_btn = st.form_submit_button("Register")
        
        if register_btn and reg_username and reg_email and reg_password:
            if len(reg_password) >= 6:
                success, message = register_user(reg_username, reg_email, reg_password)
                if success:
                    st.success(message)
                    st.rerun()
                else:
                    st.error(message)
            else:
                st.error("Password must be at least 6 characters")
    
    # Test credentials
    st.markdown("---")
    st.info("**Test Credentials:**\nUsername: demo_1755150234\nPassword: demo123456")

def show_dashboard():
    """Show user dashboard"""
    st.title(f"Welcome {st.session_state.user['username']}!")
    st.success("✅ You are logged in!")
    
    st.write("**Your Account:**")
    st.write(f"Username: {st.session_state.user['username']}")
    st.write(f"Email: {st.session_state.user['email']}")
    st.write(f"ID: {st.session_state.user['id']}")
    
    if st.button("Logout"):
        st.session_state.authenticated = False
        st.session_state.user = None
        st.rerun()

def main():
    """Main app"""
    if st.session_state.authenticated:
        show_dashboard()
    else:
        show_login()

if __name__ == "__main__":
    main()
