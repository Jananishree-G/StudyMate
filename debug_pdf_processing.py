#!/usr/bin/env python3
"""
Debug PDF Processing
Test and fix PDF processing issues
"""

import streamlit as st
import sys
from pathlib import Path
import tempfile
import traceback

# Add paths
sys.path.append(str(Path(__file__).parent / "backend"))

def main():
    st.set_page_config(
        page_title="Debug PDF Processing",
        page_icon="🔧",
        layout="wide"
    )
    
    st.title("🔧 Debug PDF Processing")
    
    # Test 1: Check PyMuPDF installation
    st.markdown("## 1. PyMuPDF Installation Test")
    try:
        import fitz
        st.success(f"✅ PyMuPDF (fitz) imported successfully - Version: {fitz.version}")
    except ImportError as e:
        st.error(f"❌ PyMuPDF import failed: {str(e)}")
        st.markdown("**Fix:** Install PyMuPDF with: `pip install PyMuPDF`")
        return
    except Exception as e:
        st.error(f"❌ PyMuPDF error: {str(e)}")
        return
    
    # Test 2: Test PDF processing components
    st.markdown("## 2. PDF Processor Import Test")
    try:
        from backend.pdf_processor import PDFProcessor
        st.success("✅ PDFProcessor imported successfully")
        
        # Initialize processor
        processor = PDFProcessor()
        st.success("✅ PDFProcessor initialized successfully")
        
    except Exception as e:
        st.error(f"❌ PDFProcessor error: {str(e)}")
        st.code(traceback.format_exc())
        return
    
    # Test 3: File upload and processing test
    st.markdown("## 3. File Upload and Processing Test")
    
    uploaded_file = st.file_uploader("Upload a PDF file for testing", type=['pdf'])
    
    if uploaded_file:
        st.info(f"📄 File: {uploaded_file.name} ({uploaded_file.size / (1024*1024):.1f} MB)")
        
        if st.button("🔧 Test PDF Processing", type="primary"):
            with st.spinner("Testing PDF processing..."):
                try:
                    # Save uploaded file temporarily
                    with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
                        tmp_file.write(uploaded_file.getbuffer())
                        temp_path = Path(tmp_file.name)
                    
                    st.info(f"📁 Temporary file saved: {temp_path}")
                    
                    # Test basic PDF opening
                    st.markdown("### Step 1: Basic PDF Opening")
                    try:
                        doc = fitz.open(temp_path)
                        st.success(f"✅ PDF opened successfully - {len(doc)} pages")
                        
                        # Test text extraction from first page
                        if len(doc) > 0:
                            page = doc.load_page(0)
                            page_text = page.get_text()
                            st.success(f"✅ First page text extracted - {len(page_text)} characters")
                            
                            if page_text.strip():
                                st.text_area("First page text preview:", page_text[:500] + "..." if len(page_text) > 500 else page_text, height=100)
                            else:
                                st.warning("⚠️ First page appears to be empty or image-only")
                        
                        doc.close()
                        
                    except Exception as e:
                        st.error(f"❌ Basic PDF opening failed: {str(e)}")
                        st.code(traceback.format_exc())
                        return
                    
                    # Test full PDF processing
                    st.markdown("### Step 2: Full PDF Processing")
                    try:
                        result = processor.extract_text_from_pdf(temp_path)
                        st.success("✅ Full PDF processing successful!")
                        
                        # Display results
                        col1, col2, col3 = st.columns(3)
                        
                        with col1:
                            st.metric("Total Pages", result['metadata']['total_pages'])
                        with col2:
                            st.metric("Pages with Text", result['metadata']['pages_with_text'])
                        with col3:
                            st.metric("Total Words", result['metadata']['total_words'])
                        
                        # Show text preview
                        if result['full_text']:
                            st.text_area("Extracted text preview:", result['full_text'][:1000] + "..." if len(result['full_text']) > 1000 else result['full_text'], height=150)
                        else:
                            st.warning("⚠️ No text extracted from PDF")
                        
                        # Test chunking
                        st.markdown("### Step 3: Text Chunking")
                        try:
                            chunks = processor.chunk_text(result['full_text'])
                            st.success(f"✅ Text chunking successful - {len(chunks)} chunks created")
                            
                            if chunks:
                                st.text_area("First chunk preview:", chunks[0]['text'][:300] + "..." if len(chunks[0]['text']) > 300 else chunks[0]['text'], height=100)
                            
                        except Exception as e:
                            st.error(f"❌ Text chunking failed: {str(e)}")
                            st.code(traceback.format_exc())
                        
                        # Test complete processing
                        st.markdown("### Step 4: Complete Processing")
                        try:
                            complete_result = processor.process_pdf(temp_path)
                            st.success("✅ Complete PDF processing successful!")
                            
                            col1, col2, col3 = st.columns(3)
                            
                            with col1:
                                st.metric("Chunks Created", complete_result['chunk_count'])
                            with col2:
                                st.metric("Total Words", complete_result['metadata']['total_words'])
                            with col3:
                                st.metric("File Size", f"{complete_result['metadata']['file_size'] / (1024*1024):.1f} MB")
                            
                            st.json(complete_result['metadata'])
                            
                        except Exception as e:
                            st.error(f"❌ Complete processing failed: {str(e)}")
                            st.code(traceback.format_exc())
                    
                    except Exception as e:
                        st.error(f"❌ Full PDF processing failed: {str(e)}")
                        st.code(traceback.format_exc())
                    
                    # Clean up
                    try:
                        temp_path.unlink()
                        st.info("🗑️ Temporary file cleaned up")
                    except:
                        pass
                        
                except Exception as e:
                    st.error(f"❌ Overall test failed: {str(e)}")
                    st.code(traceback.format_exc())
    
    # Test 4: Backend integration test
    st.markdown("## 4. Backend Integration Test")
    
    if st.button("🔧 Test Backend Integration"):
        try:
            from backend.manager import StudyMateBackend
            
            backend = StudyMateBackend()
            st.success("✅ Backend initialized successfully")
            
            # Test with a simple file path list
            test_paths = [Path("nonexistent.pdf")]  # This should fail gracefully
            result = backend.process_uploaded_files(test_paths)
            
            st.json(result)
            
            if not result['success']:
                st.info("✅ Backend correctly handled invalid file (expected behavior)")
            
        except Exception as e:
            st.error(f"❌ Backend integration failed: {str(e)}")
            st.code(traceback.format_exc())
    
    # Troubleshooting guide
    st.markdown("## 🔧 Troubleshooting Guide")
    
    st.markdown("""
    ### Common Issues and Solutions:
    
    **1. PyMuPDF Import Error:**
    ```bash
    pip install PyMuPDF
    ```
    
    **2. Empty Text Extraction:**
    - PDF might be image-based (scanned document)
    - Try OCR-enabled PDF processing
    - Check if PDF is password protected
    
    **3. Processing Timeout:**
    - Large PDF files may take time
    - Check file size limits
    - Ensure sufficient memory
    
    **4. Chunking Issues:**
    - Check text content quality
    - Verify chunk size settings
    - Review text cleaning process
    
    **5. Backend Integration Issues:**
    - Verify all dependencies installed
    - Check file path handling
    - Review error logs
    """)

if __name__ == "__main__":
    main()
