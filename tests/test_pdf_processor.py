"""
Tests for PDF processor module
"""

import pytest
import tempfile
from pathlib import Path
import sys

# Add src to path
sys.path.append(str(Path(__file__).parent.parent / "src"))

from pdf_processor import PDFProcessor
from config import config

class TestPDFProcessor:
    """Test cases for PDFProcessor class"""
    
    def setup_method(self):
        """Setup test fixtures"""
        self.processor = PDFProcessor()
    
    def test_pdf_processor_initialization(self):
        """Test PDF processor initialization"""
        assert self.processor is not None
        assert isinstance(self.processor.processed_files, dict)
    
    def test_extract_text_from_nonexistent_file(self):
        """Test extraction from non-existent file"""
        fake_path = Path("nonexistent.pdf")
        
        with pytest.raises(Exception):
            self.processor.extract_text_from_pdf(fake_path)
    
    def test_create_text_chunks_empty_data(self):
        """Test chunk creation with empty data"""
        empty_data = {
            'metadata': {
                'filename': 'test.pdf',
                'file_hash': 'test_hash'
            },
            'full_text': ''
        }
        
        chunks = self.processor.create_text_chunks(empty_data)
        assert len(chunks) == 0
    
    def test_create_text_chunks_with_data(self):
        """Test chunk creation with sample data"""
        sample_text = "This is a test document. " * 100  # Create longer text
        
        sample_data = {
            'metadata': {
                'filename': 'test.pdf',
                'file_path': '/path/to/test.pdf',
                'file_hash': 'test_hash'
            },
            'full_text': sample_text
        }
        
        chunks = self.processor.create_text_chunks(sample_data)
        assert len(chunks) > 0
        
        # Check chunk structure
        for chunk in chunks:
            assert 'chunk_id' in chunk
            assert 'text' in chunk
            assert 'source_file' in chunk
            assert 'chunk_index' in chunk
            assert chunk['source_file'] == 'test.pdf'
    
    def test_get_processing_stats_empty(self):
        """Test processing stats with empty data"""
        stats = self.processor.get_processing_stats([])
        assert stats == {}
    
    def test_get_processing_stats_with_data(self):
        """Test processing stats with sample data"""
        sample_pdfs = [
            {
                'metadata': {
                    'total_pages': 10,
                    'total_words': 1000,
                    'total_characters': 5000
                }
            },
            {
                'metadata': {
                    'total_pages': 20,
                    'total_words': 2000,
                    'total_characters': 10000
                }
            }
        ]
        
        stats = self.processor.get_processing_stats(sample_pdfs)
        
        assert stats['total_files'] == 2
        assert stats['total_pages'] == 30
        assert stats['total_words'] == 3000
        assert stats['total_characters'] == 15000
        assert stats['average_words_per_file'] == 1500
        assert stats['average_pages_per_file'] == 15

if __name__ == "__main__":
    pytest.main([__file__])
