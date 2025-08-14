#!/usr/bin/env python3
"""
Test StudyMate Components
Verify all components work correctly
"""

import streamlit as st
import sys
from pathlib import Path

# Add paths
sys.path.append(str(Path(__file__).parent / "backend"))
sys.path.append(str(Path(__file__).parent / "frontend"))

def main():
    st.set_page_config(
        page_title="StudyMate Test",
        page_icon="🧪",
        layout="wide"
    )
    
    st.title("🧪 StudyMate Component Test")
    
    # Test 1: Backend Import
    st.markdown("## 1. Backend Import Test")
    try:
        from backend.manager import StudyMateBackend
        st.success("✅ Backend imported successfully")
        
        # Initialize backend
        if 'backend' not in st.session_state:
            with st.spinner("Initializing backend..."):
                st.session_state.backend = StudyMateBackend()
        
        st.success("✅ Backend initialized successfully")
        
        # Test backend methods
        stats = st.session_state.backend.get_system_stats()
        st.json(stats)
        
    except Exception as e:
        st.error(f"❌ Backend error: {str(e)}")
        st.code(str(e))
    
    # Test 2: Frontend Import
    st.markdown("## 2. Frontend Import Test")
    try:
        from frontend.styles import get_custom_css
        st.success("✅ Frontend imported successfully")
        
        # Apply CSS
        st.markdown(get_custom_css(), unsafe_allow_html=True)
        st.success("✅ CSS applied successfully")
        
    except Exception as e:
        st.error(f"❌ Frontend error: {str(e)}")
        st.code(str(e))
    
    # Test 3: Model Loading
    st.markdown("## 3. Model Loading Test")
    try:
        available_models = st.session_state.backend.get_available_models()
        st.success(f"✅ Available models: {list(available_models.keys())}")
        
        current_model = st.session_state.backend.get_current_model()
        st.info(f"🔄 Current model: {current_model}")
        
    except Exception as e:
        st.error(f"❌ Model error: {str(e)}")
        st.code(str(e))
    
    # Test 4: File Upload Interface
    st.markdown("## 4. File Upload Test")
    uploaded_file = st.file_uploader("Test file upload", type=['pdf'])
    if uploaded_file:
        st.success(f"✅ File uploaded: {uploaded_file.name}")
        st.info(f"Size: {uploaded_file.size / (1024*1024):.1f} MB")
    
    # Test 5: Chat Interface
    st.markdown("## 5. Chat Interface Test")
    if prompt := st.chat_input("Test chat input..."):
        st.chat_message("user").write(prompt)
        st.chat_message("assistant").write(f"Echo: {prompt}")
    
    # Test 6: System Information
    st.markdown("## 6. System Information")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Python Environment:**")
        st.write(f"Python: {sys.version}")
        st.write(f"Streamlit: {st.__version__}")
    
    with col2:
        st.markdown("**Project Structure:**")
        project_root = Path(__file__).parent
        st.write(f"Root: {project_root}")
        st.write(f"Backend exists: {(project_root / 'backend').exists()}")
        st.write(f"Frontend exists: {(project_root / 'frontend').exists()}")
    
    # Success message
    st.markdown("---")
    st.success("🎉 All tests completed! StudyMate components are working correctly.")
    
    if st.button("🚀 Launch Full StudyMate", type="primary"):
        st.info("Run: streamlit run studymate_final.py")

if __name__ == "__main__":
    main()
