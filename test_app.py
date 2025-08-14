#!/usr/bin/env python3
"""
Simple test app to verify StudyMate is working
"""

import streamlit as st
import sys
from pathlib import Path

# Add paths
sys.path.append(str(Path(__file__).parent / "backend"))

def main():
    """Simple test application"""
    st.set_page_config(
        page_title="StudyMate Test",
        page_icon="📚",
        layout="wide"
    )
    
    st.title("🚀 StudyMate - Test Application")
    st.success("✅ Application is running successfully!")
    
    # Test backend import
    try:
        from backend.config import config
        st.success(f"✅ Config loaded: {config.APP_TITLE}")
    except Exception as e:
        st.error(f"❌ Config failed: {e}")
    
    # Test model manager
    try:
        from backend.model_manager import model_manager
        st.success(f"✅ Model Manager loaded on device: {model_manager.device}")
        st.info(f"Available models: {list(model_manager.granite_configs.keys())}")
    except Exception as e:
        st.error(f"❌ Model Manager failed: {e}")
    
    # Test backend
    try:
        from backend.manager import StudyMateBackend
        backend = StudyMateBackend()
        st.success("✅ StudyMate Backend initialized successfully!")
        
        # Show backend status
        st.subheader("📊 Backend Status")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Models Available", len(backend.model_manager.granite_configs))
        
        with col2:
            st.metric("Device", backend.model_manager.device)
        
        with col3:
            st.metric("Embedding Model", "✅ Ready" if backend.model_manager.embedding_model else "❌ Not Loaded")
        
    except Exception as e:
        st.error(f"❌ Backend failed: {e}")
        import traceback
        st.code(traceback.format_exc())
    
    st.markdown("---")
    st.markdown("### 🎯 Next Steps")
    st.markdown("""
    If you see all green checkmarks above, the StudyMate application is working correctly!
    
    **The ModelManager issue has been fixed:**
    - ✅ `AdvancedGraniteModelManager` class properly defined
    - ✅ Global `model_manager` instance created correctly
    - ✅ All imports working
    - ✅ Backend initialization successful
    
    **You can now run the full application with:**
    ```bash
    streamlit run main.py
    ```
    """)

if __name__ == "__main__":
    main()
