#!/usr/bin/env python3
"""
Test PDF Processing Fix
Verify the document closed issue is resolved
"""

import sys
from pathlib import Path
import tempfile
import traceback

# Add paths
sys.path.append(str(Path(__file__).parent / "backend"))

def test_pdf_processing():
    """Test PDF processing with the fix"""
    print("🧪 Testing PDF Processing Fix")
    print("=" * 50)
    
    try:
        # Import PyMuPDF
        import fitz
        print(f"✅ PyMuPDF imported successfully - Version: {fitz.version}")
        
        # Import PDF processor
        from backend.pdf_processor import PDFProcessor
        print("✅ PDFProcessor imported successfully")
        
        # Initialize processor
        processor = PDFProcessor()
        print("✅ PDFProcessor initialized successfully")
        
        # Create a test PDF
        print("\n📄 Creating test PDF...")
        
        # Create a simple test PDF with multiple pages
        doc = fitz.open()
        
        # Add first page
        page1 = doc.new_page()
        page1.insert_text((72, 72), "This is page 1 of the test document.\nIt contains some sample text for testing PDF processing.")
        
        # Add second page
        page2 = doc.new_page()
        page2.insert_text((72, 72), "This is page 2 of the test document.\nIt has different content to test multi-page processing.")
        
        # Add third page
        page3 = doc.new_page()
        page3.insert_text((72, 72), "This is page 3 of the test document.\nFinal page with more test content for verification.")
        
        # Save to temporary file
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp:
            doc.save(tmp.name)
            test_path = Path(tmp.name)
        
        doc.close()
        print(f"✅ Test PDF created: {test_path}")
        
        # Test the fixed PDF processing
        print("\n🔄 Testing PDF processing...")
        
        try:
            result = processor.extract_text_from_pdf(test_path)
            print("✅ PDF processing successful!")
            
            # Display results
            print(f"\n📊 Results:")
            print(f"  • Filename: {result['metadata']['filename']}")
            print(f"  • Total pages: {result['metadata']['total_pages']}")
            print(f"  • Pages with text: {result['metadata']['pages_with_text']}")
            print(f"  • Total words: {result['metadata']['total_words']}")
            print(f"  • Total characters: {result['metadata']['total_characters']}")
            
            # Show extracted text preview
            if result['full_text']:
                preview = result['full_text'][:200] + "..." if len(result['full_text']) > 200 else result['full_text']
                print(f"\n📝 Text preview:")
                print(f"  {preview}")
            
            # Test chunking
            print(f"\n🔄 Testing text chunking...")
            chunks = processor.chunk_text(result['full_text'])
            print(f"✅ Chunking successful: {len(chunks)} chunks created")
            
            if chunks:
                print(f"  • First chunk: {chunks[0]['text'][:100]}...")
                print(f"  • Chunk word count: {chunks[0]['word_count']}")
            
            # Test complete processing
            print(f"\n🔄 Testing complete PDF processing...")
            complete_result = processor.process_pdf(test_path)
            print(f"✅ Complete processing successful!")
            print(f"  • Chunks created: {complete_result['chunk_count']}")
            print(f"  • Processing successful: {complete_result['metadata']['extraction_success']}")
            
        except Exception as e:
            print(f"❌ PDF processing failed: {str(e)}")
            traceback.print_exc()
            return False
        
        # Clean up
        try:
            test_path.unlink()
            print(f"\n🗑️ Test file cleaned up")
        except:
            pass
        
        print(f"\n🎉 All tests passed! PDF processing fix is working correctly.")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        traceback.print_exc()
        return False

def test_backend_integration():
    """Test backend integration with the fix"""
    print("\n🔧 Testing Backend Integration")
    print("=" * 50)
    
    try:
        from backend.manager import StudyMateBackend
        
        # Initialize backend
        backend = StudyMateBackend()
        print("✅ Backend initialized successfully")
        
        # Create test PDF
        import fitz
        doc = fitz.open()
        page = doc.new_page()
        page.insert_text((72, 72), "Test document for backend integration.\nThis is a sample PDF for testing the complete pipeline.")
        
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp:
            doc.save(tmp.name)
            test_path = Path(tmp.name)
        
        doc.close()
        print(f"✅ Test PDF created for backend test")
        
        # Test backend processing
        result = backend.process_uploaded_files([test_path])
        
        if result['success']:
            print("✅ Backend processing successful!")
            print(f"  • Files processed: {result['stats'].get('files_processed', 0)}")
            print(f"  • Chunks created: {result.get('num_chunks', 0)}")
            print(f"  • Processing time: {result.get('processing_time', 0):.2f}s")
        else:
            print(f"❌ Backend processing failed: {result['message']}")
            if 'stats' in result:
                print(f"  • Error details: {result['stats']}")
            return False
        
        # Test question answering
        try:
            stats = backend.get_system_stats()
            if stats['ready_for_questions']:
                print("✅ System ready for questions")
                
                # Test a simple question
                response = backend.ask_question("What is this document about?")
                print("✅ Question answering successful!")
                print(f"  • Answer: {response['answer'][:100]}...")
            else:
                print("⚠️ System not ready for questions")
        except Exception as e:
            print(f"⚠️ Question answering test failed: {str(e)}")
        
        # Clean up
        try:
            test_path.unlink()
            print(f"🗑️ Backend test file cleaned up")
        except:
            pass
        
        print(f"🎉 Backend integration test completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Backend integration test failed: {str(e)}")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🚀 Starting PDF Processing Fix Tests")
    print("=" * 60)
    
    # Test 1: PDF Processing Fix
    test1_success = test_pdf_processing()
    
    # Test 2: Backend Integration
    test2_success = test_backend_integration()
    
    # Summary
    print("\n" + "=" * 60)
    print("📋 TEST SUMMARY")
    print("=" * 60)
    print(f"PDF Processing Fix: {'✅ PASSED' if test1_success else '❌ FAILED'}")
    print(f"Backend Integration: {'✅ PASSED' if test2_success else '❌ FAILED'}")
    
    if test1_success and test2_success:
        print("\n🎉 ALL TESTS PASSED! PDF processing is now working correctly.")
        print("✅ The 'document closed' issue has been resolved.")
        print("🚀 StudyMate should now process PDFs successfully!")
    else:
        print("\n❌ Some tests failed. Please check the error messages above.")
    
    print("=" * 60)
