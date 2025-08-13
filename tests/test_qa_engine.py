"""
Tests for QA engine module
"""

import pytest
from pathlib import Path
import sys

# Add src to path
sys.path.append(str(Path(__file__).parent.parent / "src"))

from qa_engine import QAEngine
from embeddings import EmbeddingManager

class TestQAEngine:
    """Test cases for QAEngine class"""
    
    def setup_method(self):
        """Setup test fixtures"""
        self.qa_engine = QAEngine()
    
    def test_qa_engine_initialization(self):
        """Test QA engine initialization"""
        assert self.qa_engine is not None
        assert self.qa_engine.client is None
        assert isinstance(self.qa_engine.embedding_manager, EmbeddingManager)
        assert isinstance(self.qa_engine.conversation_history, list)
    
    def test_build_context_empty_chunks(self):
        """Test building context with empty chunks"""
        context = self.qa_engine.build_context([])
        assert context == ""
    
    def test_build_context_with_chunks(self):
        """Test building context with sample chunks"""
        sample_chunks = [
            {
                'chunk': {
                    'text': 'This is the first chunk of text.',
                    'source_file': 'test1.pdf'
                }
            },
            {
                'chunk': {
                    'text': 'This is the second chunk of text.',
                    'source_file': 'test2.pdf'
                }
            }
        ]
        
        context = self.qa_engine.build_context(sample_chunks)
        
        assert len(context) > 0
        assert 'first chunk' in context
        assert 'second chunk' in context
        assert 'test1.pdf' in context
        assert 'test2.pdf' in context
    
    def test_create_prompt(self):
        """Test prompt creation"""
        question = "What is the main topic?"
        context = "This document discusses artificial intelligence and machine learning."
        
        prompt = self.qa_engine.create_prompt(question, context)
        
        assert len(prompt) > 0
        assert question in prompt
        assert context in prompt
        assert "StudyMate" in prompt
    
    def test_create_prompt_with_history(self):
        """Test prompt creation with conversation history"""
        question = "What is the main topic?"
        context = "This document discusses AI."
        history = [
            {
                'question': 'Previous question?',
                'answer': 'Previous answer.'
            }
        ]
        
        prompt = self.qa_engine.create_prompt(question, context, history)
        
        assert len(prompt) > 0
        assert question in prompt
        assert context in prompt
        assert 'Previous question' in prompt
        assert 'Previous answer' in prompt
    
    def test_ask_question_without_embedding_manager(self):
        """Test asking question without proper setup"""
        # Create QA engine with empty embedding manager
        qa_engine = QAEngine()
        qa_engine.embedding_manager.index = None
        
        result = qa_engine.ask_question("Test question")
        
        assert 'error' in result
        assert result['error'] is False  # Should be handled gracefully
        assert 'couldn\'t find' in result['answer'].lower()
    
    def test_clear_conversation_history(self):
        """Test clearing conversation history"""
        # Add some history
        self.qa_engine.conversation_history = [
            {'question': 'Q1', 'answer': 'A1'},
            {'question': 'Q2', 'answer': 'A2'}
        ]
        
        self.qa_engine.clear_conversation_history()
        
        assert len(self.qa_engine.conversation_history) == 0
    
    def test_get_conversation_history(self):
        """Test getting conversation history"""
        # Add some history
        history = [
            {'question': 'Q1', 'answer': 'A1'},
            {'question': 'Q2', 'answer': 'A2'}
        ]
        self.qa_engine.conversation_history = history
        
        retrieved_history = self.qa_engine.get_conversation_history()
        
        assert len(retrieved_history) == 2
        assert retrieved_history == history
        assert retrieved_history is not self.qa_engine.conversation_history  # Should be a copy
    
    def test_set_embedding_manager(self):
        """Test setting embedding manager"""
        new_embedding_manager = EmbeddingManager()
        
        self.qa_engine.set_embedding_manager(new_embedding_manager)
        
        assert self.qa_engine.embedding_manager is new_embedding_manager

class TestQAEngineWithMockData:
    """Test cases with mock data"""
    
    def setup_method(self):
        """Setup test fixtures with mock data"""
        self.qa_engine = QAEngine()
        
        # Mock similar chunks
        self.mock_similar_chunks = [
            {
                'rank': 1,
                'score': 0.95,
                'chunk': {
                    'text': 'Artificial intelligence is a branch of computer science.',
                    'source_file': 'ai_textbook.pdf',
                    'chunk_id': 'ai_1'
                }
            },
            {
                'rank': 2,
                'score': 0.87,
                'chunk': {
                    'text': 'Machine learning is a subset of artificial intelligence.',
                    'source_file': 'ml_guide.pdf',
                    'chunk_id': 'ml_1'
                }
            }
        ]
    
    def test_generate_answer_structure(self):
        """Test the structure of generated answer (without actual LLM call)"""
        # This test focuses on the structure and error handling
        # without making actual API calls
        
        question = "What is artificial intelligence?"
        
        # Test with empty chunks
        result = self.qa_engine.generate_answer(question, [])
        
        assert 'answer' in result
        assert 'sources' in result
        assert 'confidence' in result
        assert 'error' in result
        assert isinstance(result['sources'], list)
        assert isinstance(result['confidence'], float)
        assert isinstance(result['error'], bool)

if __name__ == "__main__":
    pytest.main([__file__])
