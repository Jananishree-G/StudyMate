"""
Question-Answering engine for StudyMate
Handles LLM-based answer generation using IBM Watsonx
"""

import logging
from typing import List, Dict, Optional, Tuple
import streamlit as st

# Try to import IBM Watson libraries, handle gracefully if not available
try:
    from ibm_watson_machine_learning import APIClient
    from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
    WATSON_AVAILABLE = True
except ImportError:
    WATSON_AVAILABLE = False
    APIClient = None
    IAMAuthenticator = None

from config import config
from embeddings import EmbeddingManager

logger = logging.getLogger(__name__)

class QAEngine:
    """Question-Answering engine using IBM Watsonx"""
    
    def __init__(self):
        self.client = None
        self.embedding_manager = EmbeddingManager()
        self.conversation_history = []
        
    def initialize_watsonx(self) -> bool:
        """Initialize IBM Watsonx client"""
        try:
            if not WATSON_AVAILABLE:
                st.warning("⚠️ IBM Watson libraries not installed. Install with: pip install ibm-watson-machine-learning")
                return False

            if not config.validate_config():
                st.error("Please configure IBM Watsonx credentials in your .env file")
                return False

            # Set up credentials
            wml_credentials = {
                "url": config.WATSONX_URL,
                "apikey": config.WATSONX_API_KEY
            }

            # Initialize client
            self.client = APIClient(wml_credentials)
            self.client.set.default_project(config.WATSONX_PROJECT_ID)

            logger.info("Successfully initialized IBM Watsonx client")
            return True

        except Exception as e:
            logger.error(f"Error initializing Watsonx: {str(e)}")
            st.error(f"Failed to initialize IBM Watsonx: {str(e)}")
            return False
    
    def build_context(self, similar_chunks: List[Dict[str, any]], max_context_length: int = 3000) -> str:
        """
        Build context from similar chunks for the LLM
        
        Args:
            similar_chunks: List of similar chunks from search
            max_context_length: Maximum length of context
            
        Returns:
            Formatted context string
        """
        context_parts = []
        current_length = 0
        
        for result in similar_chunks:
            chunk = result['chunk']
            chunk_text = chunk['text']
            source_info = f"[Source: {chunk['source_file']}, Page context]"
            
            chunk_with_source = f"{chunk_text}\n{source_info}\n"
            
            if current_length + len(chunk_with_source) > max_context_length:
                break
            
            context_parts.append(chunk_with_source)
            current_length += len(chunk_with_source)
        
        return "\n---\n".join(context_parts)
    
    def create_prompt(self, question: str, context: str, conversation_history: List[Dict] = None) -> str:
        """
        Create a prompt for the LLM
        
        Args:
            question: User's question
            context: Retrieved context
            conversation_history: Previous conversation
            
        Returns:
            Formatted prompt
        """
        # Base system prompt
        system_prompt = """You are StudyMate, an AI academic assistant that helps students understand their study materials. 
        
Your role is to:
1. Answer questions based ONLY on the provided context from the student's documents
2. Provide clear, accurate, and educational explanations
3. Reference specific sources when possible
4. If the context doesn't contain enough information, clearly state this
5. Encourage further learning and understanding

Guidelines:
- Be concise but thorough
- Use academic language appropriate for students
- Always ground your answers in the provided context
- If asked about something not in the context, politely explain that you can only answer based on the provided materials
- Provide page references when available"""
        
        # Add conversation history if available
        history_text = ""
        if conversation_history:
            history_text = "\n\nPrevious conversation:\n"
            for entry in conversation_history[-3:]:  # Last 3 exchanges
                history_text += f"Q: {entry['question']}\nA: {entry['answer']}\n\n"
        
        # Construct the full prompt
        prompt = f"""{system_prompt}

Context from study materials:
{context}
{history_text}
Current question: {question}

Please provide a comprehensive answer based on the context above:"""
        
        return prompt
    
    def generate_answer(self, question: str, similar_chunks: List[Dict[str, any]]) -> Dict[str, any]:
        """
        Generate answer using IBM Watsonx or fallback method

        Args:
            question: User's question
            similar_chunks: Similar chunks from search

        Returns:
            Dictionary containing answer and metadata
        """
        # Check if Watson is available and configured
        if not WATSON_AVAILABLE:
            return self._generate_fallback_answer(question, similar_chunks)

        if not self.client:
            if not self.initialize_watsonx():
                return self._generate_fallback_answer(question, similar_chunks)
        
        try:
            # Build context from similar chunks
            context = self.build_context(similar_chunks)
            
            if not context.strip():
                return {
                    'answer': "I couldn't find relevant information in your documents to answer this question. Please try rephrasing your question or upload more relevant materials.",
                    'sources': [],
                    'confidence': 0.0,
                    'error': False
                }
            
            # Create prompt
            prompt = self.create_prompt(question, context, self.conversation_history)
            
            # Set up generation parameters
            generation_params = {
                "decoding_method": "greedy",
                "max_new_tokens": config.MAX_TOKENS,
                "temperature": config.TEMPERATURE,
                "top_p": config.TOP_P,
                "repetition_penalty": 1.1
            }
            
            # Generate response
            with st.spinner("Generating answer..."):
                response = self.client.foundation_models.generate_text(
                    model_id=config.WATSONX_MODEL_ID,
                    prompt=prompt,
                    params=generation_params
                )
            
            # Extract answer
            answer = response.strip()
            
            # Extract sources
            sources = []
            for result in similar_chunks[:3]:  # Top 3 sources
                chunk = result['chunk']
                source = {
                    'filename': chunk['source_file'],
                    'score': result['score'],
                    'text_preview': chunk['text'][:200] + "..." if len(chunk['text']) > 200 else chunk['text']
                }
                sources.append(source)
            
            # Calculate confidence based on search scores
            confidence = 0.0
            if similar_chunks:
                avg_score = sum(result['score'] for result in similar_chunks[:3]) / min(3, len(similar_chunks))
                confidence = min(avg_score * 100, 100.0)  # Convert to percentage
            
            # Store in conversation history
            self.conversation_history.append({
                'question': question,
                'answer': answer,
                'sources': sources,
                'confidence': confidence
            })
            
            # Keep only last 10 exchanges
            if len(self.conversation_history) > 10:
                self.conversation_history = self.conversation_history[-10:]
            
            logger.info(f"Generated answer for question: {question[:50]}...")
            
            return {
                'answer': answer,
                'sources': sources,
                'confidence': confidence,
                'error': False
            }
            
        except Exception as e:
            logger.error(f"Error generating answer: {str(e)}")
            return {
                'answer': f"I encountered an error while generating the answer: {str(e)}",
                'sources': [],
                'confidence': 0.0,
                'error': True
            }
    
    def ask_question(self, question: str, k: int = 5) -> Dict[str, any]:
        """
        Complete Q&A pipeline: search + generate answer
        
        Args:
            question: User's question
            k: Number of similar chunks to retrieve
            
        Returns:
            Dictionary containing answer and metadata
        """
        try:
            # Search for similar chunks
            similar_chunks = self.embedding_manager.search(question, k=k)
            
            if not similar_chunks:
                return {
                    'answer': "I couldn't find any relevant information in your documents. Please make sure you have uploaded relevant study materials.",
                    'sources': [],
                    'confidence': 0.0,
                    'error': False
                }
            
            # Generate answer
            result = self.generate_answer(question, similar_chunks)
            
            return result
            
        except Exception as e:
            logger.error(f"Error in Q&A pipeline: {str(e)}")
            return {
                'answer': f"An error occurred while processing your question: {str(e)}",
                'sources': [],
                'confidence': 0.0,
                'error': True
            }
    
    def clear_conversation_history(self):
        """Clear conversation history"""
        self.conversation_history = []
        logger.info("Cleared conversation history")
    
    def get_conversation_history(self) -> List[Dict]:
        """Get conversation history"""
        return self.conversation_history.copy()
    
    def _generate_fallback_answer(self, question: str, similar_chunks: List[Dict[str, any]]) -> Dict[str, any]:
        """
        Generate a fallback answer when Watson is not available

        Args:
            question: User's question
            similar_chunks: Similar chunks from search

        Returns:
            Dictionary containing answer and metadata
        """
        try:
            # Build context from similar chunks
            context = self.build_context(similar_chunks)

            if not context.strip():
                return {
                    'answer': "I couldn't find relevant information in your documents to answer this question. Please try rephrasing your question or upload more relevant materials.",
                    'sources': [],
                    'confidence': 0.0,
                    'error': False
                }

            # Create a simple extractive answer from the most relevant chunks
            answer_parts = []
            answer_parts.append("Based on your uploaded documents, here's what I found:\n")

            # Use the top 2-3 most relevant chunks
            for i, result in enumerate(similar_chunks[:3], 1):
                chunk = result['chunk']
                score = result['score']

                # Add chunk content with source
                answer_parts.append(f"\n**From {chunk['source_file']}:**")
                answer_parts.append(f"{chunk['text'][:500]}{'...' if len(chunk['text']) > 500 else ''}")

                if i < len(similar_chunks[:3]):
                    answer_parts.append("\n---")

            answer_parts.append(f"\n\n*Note: This is a basic text extraction. For AI-generated answers, please install IBM Watson libraries and configure your API keys.*")

            answer = "\n".join(answer_parts)

            # Extract sources
            sources = []
            for result in similar_chunks[:3]:
                chunk = result['chunk']
                source = {
                    'filename': chunk['source_file'],
                    'score': result['score'],
                    'text_preview': chunk['text'][:200] + "..." if len(chunk['text']) > 200 else chunk['text']
                }
                sources.append(source)

            # Calculate confidence based on search scores
            confidence = 0.0
            if similar_chunks:
                avg_score = sum(result['score'] for result in similar_chunks[:3]) / min(3, len(similar_chunks))
                confidence = min(avg_score * 100, 100.0)

            return {
                'answer': answer,
                'sources': sources,
                'confidence': confidence,
                'error': False
            }

        except Exception as e:
            logger.error(f"Error generating fallback answer: {str(e)}")
            return {
                'answer': f"I encountered an error while processing your question: {str(e)}",
                'sources': [],
                'confidence': 0.0,
                'error': True
            }

    def set_embedding_manager(self, embedding_manager: EmbeddingManager):
        """Set the embedding manager"""
        self.embedding_manager = embedding_manager
