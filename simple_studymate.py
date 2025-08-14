#!/usr/bin/env python3
"""
Simple StudyMate with Authentication
Minimal working version
"""

import streamlit as st
import json

def main():
    st.set_page_config(
        page_title="StudyMate",
        page_icon="📚",
        layout="wide"
    )
    
    # Check if user is authenticated
    authenticated = st.session_state.get('authenticated', False)
    user_data = st.session_state.get('user_data', {})
    
    # Check URL parameters for authentication
    try:
        query_params = st.experimental_get_query_params()
        if 'auth' in query_params and query_params['auth'][0] == 'success':
            if 'user' in query_params:
                user_data = json.loads(query_params['user'][0])
                st.session_state.authenticated = True
                st.session_state.user_data = user_data
                authenticated = True
                st.experimental_set_query_params()
    except:
        pass
    
    if not authenticated:
        # Show login required page
        st.title("🔐 StudyMate - Login Required")
        
        st.markdown("""
        ### Welcome to StudyMate!
        Your AI-powered academic assistant for document analysis and Q&A.
        
        **Please login to continue:**
        """)
        
        if st.button("🔑 Go to Login Page", type="primary", use_container_width=True):
            st.markdown('<meta http-equiv="refresh" content="0; url=http://localhost:8506">', unsafe_allow_html=True)
        
        st.markdown("---")
        
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
        
    else:
        # Show main app
        st.title("📚 StudyMate - AI Academic Assistant")
        
        # Sidebar with user info
        with st.sidebar:
            st.success(f"👤 Welcome {user_data.get('username', 'User')}!")
            st.write(f"📧 {user_data.get('email', 'No email')}")
            
            if st.button("🚪 Logout"):
                st.session_state.authenticated = False
                if 'user_data' in st.session_state:
                    del st.session_state.user_data
                st.experimental_rerun()
        
        # Main content
        st.success(f"🎉 Welcome back, {user_data.get('username', 'User')}!")
        
        # Tabs for different sections
        tab1, tab2, tab3, tab4 = st.tabs(["🏠 Home", "📁 Upload", "💬 Chat", "📊 Analytics"])
        
        with tab1:
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
        
        with tab2:
            st.markdown("## 📁 Document Upload")
            
            uploaded_file = st.file_uploader("Choose a PDF file", type=['pdf'])
            
            if uploaded_file:
                st.success(f"✅ File ready: {uploaded_file.name}")
                st.info("💡 Integrate this with your PDF processing backend")
                
                if st.button("🚀 Process Document"):
                    st.success("Document processing would happen here!")
        
        with tab3:
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
        
        with tab4:
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

if __name__ == "__main__":
    main()
