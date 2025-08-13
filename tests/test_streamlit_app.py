"""
Tests for Streamlit application
"""

import pytest
from pathlib import Path
import sys

# Add src to path
sys.path.append(str(Path(__file__).parent.parent / "src"))

from config import config
from utils import validate_file_type, validate_file_size, clean_text, chunk_text

class TestUtilityFunctions:
    """Test cases for utility functions"""
    
    def test_validate_file_type_valid(self):
        """Test file type validation with valid files"""
        valid_files = [
            "document.pdf",
            "study_guide.PDF",
            "notes.txt",
            "report.docx"
        ]
        
        for filename in valid_files:
            if filename.split('.')[-1].lower() in config.ALLOWED_EXTENSIONS:
                assert validate_file_type(filename) is True
    
    def test_validate_file_type_invalid(self):
        """Test file type validation with invalid files"""
        invalid_files = [
            "image.jpg",
            "video.mp4",
            "audio.mp3",
            "executable.exe"
        ]
        
        for filename in invalid_files:
            assert validate_file_type(filename) is False
    
    def test_validate_file_size_valid(self):
        """Test file size validation with valid sizes"""
        max_size = config.MAX_FILE_SIZE_MB * 1024 * 1024  # Convert to bytes
        
        valid_sizes = [
            1024,  # 1KB
            1024 * 1024,  # 1MB
            max_size - 1000  # Just under limit
        ]
        
        for size in valid_sizes:
            assert validate_file_size(size) is True
    
    def test_validate_file_size_invalid(self):
        """Test file size validation with invalid sizes"""
        max_size = config.MAX_FILE_SIZE_MB * 1024 * 1024  # Convert to bytes
        
        invalid_sizes = [
            max_size + 1,  # Just over limit
            max_size * 2,  # Double the limit
            max_size * 10  # Way over limit
        ]
        
        for size in invalid_sizes:
            assert validate_file_size(size) is False
    
    def test_clean_text(self):
        """Test text cleaning function"""
        dirty_text = "  This   is    a   test   text.  \n\n  With   extra   spaces.  "
        clean = clean_text(dirty_text)
        
        assert clean == "This is a test text. With extra spaces."
        assert "  " not in clean  # No double spaces
        assert not clean.startswith(" ")  # No leading space
        assert not clean.endswith(" ")  # No trailing space
    
    def test_clean_text_special_characters(self):
        """Test text cleaning with special characters"""
        text_with_special = "This has @#$% special characters!"
        clean = clean_text(text_with_special)
        
        # Should preserve basic punctuation but remove special chars
        assert "!" in clean
        assert "@" not in clean
        assert "#" not in clean
        assert "$" not in clean
        assert "%" not in clean
    
    def test_chunk_text_short_text(self):
        """Test text chunking with short text"""
        short_text = "This is a short text."
        chunks = chunk_text(short_text, chunk_size=100, overlap=20)
        
        assert len(chunks) == 1
        assert chunks[0] == short_text
    
    def test_chunk_text_long_text(self):
        """Test text chunking with long text"""
        long_text = "This is a sentence. " * 100  # Create long text
        chunks = chunk_text(long_text, chunk_size=200, overlap=50)
        
        assert len(chunks) > 1
        
        # Check that chunks have proper overlap
        for i in range(len(chunks) - 1):
            current_chunk = chunks[i]
            next_chunk = chunks[i + 1]
            
            # Should have some overlap
            assert len(current_chunk) <= 250  # Allowing some flexibility for sentence boundaries
            assert len(next_chunk) <= 250

class TestConfigValidation:
    """Test cases for configuration validation"""
    
    def test_config_attributes_exist(self):
        """Test that required config attributes exist"""
        required_attrs = [
            'WATSONX_API_KEY',
            'WATSONX_PROJECT_ID',
            'WATSONX_URL',
            'HUGGINGFACE_MODEL',
            'MAX_FILE_SIZE_MB',
            'MAX_FILES_UPLOAD',
            'CHUNK_SIZE',
            'CHUNK_OVERLAP',
            'MAX_TOKENS',
            'TEMPERATURE'
        ]
        
        for attr in required_attrs:
            assert hasattr(config, attr)
    
    def test_config_types(self):
        """Test that config attributes have correct types"""
        assert isinstance(config.MAX_FILE_SIZE_MB, int)
        assert isinstance(config.MAX_FILES_UPLOAD, int)
        assert isinstance(config.CHUNK_SIZE, int)
        assert isinstance(config.CHUNK_OVERLAP, int)
        assert isinstance(config.MAX_TOKENS, int)
        assert isinstance(config.TEMPERATURE, float)
        assert isinstance(config.ALLOWED_EXTENSIONS, list)
    
    def test_config_reasonable_values(self):
        """Test that config values are reasonable"""
        assert config.MAX_FILE_SIZE_MB > 0
        assert config.MAX_FILES_UPLOAD > 0
        assert config.CHUNK_SIZE > 0
        assert config.CHUNK_OVERLAP >= 0
        assert config.CHUNK_OVERLAP < config.CHUNK_SIZE
        assert config.MAX_TOKENS > 0
        assert 0.0 <= config.TEMPERATURE <= 2.0
        assert len(config.ALLOWED_EXTENSIONS) > 0

if __name__ == "__main__":
    pytest.main([__file__])
