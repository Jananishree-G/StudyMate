"""
Tests for embeddings module
"""

import pytest
import numpy as np
from pathlib import Path
import sys

# Add src to path
sys.path.append(str(Path(__file__).parent.parent / "src"))

from embeddings import EmbeddingManager

class TestEmbeddingManager:
    """Test cases for EmbeddingManager class"""
    
    def setup_method(self):
        """Setup test fixtures"""
        self.embedding_manager = EmbeddingManager()
    
    def test_embedding_manager_initialization(self):
        """Test embedding manager initialization"""
        assert self.embedding_manager is not None
        assert self.embedding_manager.model is None
        assert self.embedding_manager.index is None
        assert isinstance(self.embedding_manager.chunks_metadata, list)
    
    def test_create_embeddings_without_model(self):
        """Test creating embeddings without loading model first"""
        texts = ["This is a test sentence."]
        
        # This should fail because model is not loaded
        with pytest.raises(Exception):
            self.embedding_manager.create_embeddings(texts)
    
    def test_create_faiss_index(self):
        """Test FAISS index creation"""
        # Create sample embeddings
        sample_embeddings = np.random.rand(10, 384).astype('float32')
        
        index = self.embedding_manager.create_faiss_index(sample_embeddings)
        
        assert index is not None
        assert index.ntotal == 10
    
    def test_build_index_from_empty_chunks(self):
        """Test building index from empty chunks"""
        result = self.embedding_manager.build_index_from_chunks([])
        assert result is False
    
    def test_search_without_index(self):
        """Test search without building index first"""
        results = self.embedding_manager.search("test query")
        assert len(results) == 0
    
    def test_get_index_stats_empty(self):
        """Test getting index stats when no index exists"""
        stats = self.embedding_manager.get_index_stats()
        assert stats == {}
    
    def test_save_index_without_index(self):
        """Test saving index when no index exists"""
        result = self.embedding_manager.save_index()
        assert result is False
    
    def test_load_index_nonexistent_path(self):
        """Test loading index from non-existent path"""
        fake_path = Path("nonexistent_index")
        result = self.embedding_manager.load_index(fake_path)
        assert result is False

class TestEmbeddingManagerWithMockData:
    """Test cases with mock data"""
    
    def setup_method(self):
        """Setup test fixtures with mock data"""
        self.embedding_manager = EmbeddingManager()
        
        # Create mock chunks
        self.mock_chunks = [
            {
                'chunk_id': 'test_1',
                'text': 'This is the first test chunk.',
                'source_file': 'test1.pdf',
                'file_path': '/path/to/test1.pdf',
                'file_hash': 'hash1',
                'chunk_index': 0,
                'char_count': 30,
                'word_count': 6,
                'metadata': {'filename': 'test1.pdf'}
            },
            {
                'chunk_id': 'test_2',
                'text': 'This is the second test chunk.',
                'source_file': 'test2.pdf',
                'file_path': '/path/to/test2.pdf',
                'file_hash': 'hash2',
                'chunk_index': 0,
                'char_count': 31,
                'word_count': 6,
                'metadata': {'filename': 'test2.pdf'}
            }
        ]
    
    def test_mock_index_creation(self):
        """Test index creation with mock data"""
        # Create mock embeddings
        mock_embeddings = np.random.rand(len(self.mock_chunks), 384).astype('float32')
        
        # Create index
        index = self.embedding_manager.create_faiss_index(mock_embeddings)
        
        assert index is not None
        assert index.ntotal == len(self.mock_chunks)
        
        # Set up the embedding manager
        self.embedding_manager.index = index
        self.embedding_manager.chunks_metadata = self.mock_chunks
        
        # Test stats
        stats = self.embedding_manager.get_index_stats()
        assert stats['total_vectors'] == len(self.mock_chunks)
        assert stats['total_chunks'] == len(self.mock_chunks)

if __name__ == "__main__":
    pytest.main([__file__])
