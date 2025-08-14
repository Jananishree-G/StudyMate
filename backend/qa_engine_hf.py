"""
HuggingFace-powered Q&A Engine for StudyMate
Uses IBM Granite and Mistral models for answer generation
"""

from typing import List, Dict, Optional, Any
from .config import config, logger
from .model_manager import model_manager
from .vector_database import vector_db
import time

class HuggingFaceQAEngine:
    """Q&A Engine powered by HuggingFace models"""
    
    def __init__(self):
        self.conversation_history = []
        self.current_model = config.DEFAULT_MODEL
        self.system_prompts = self._load_system_prompts()

        # Load default model during initialization
        logger.info(f"Initializing QA engine with default model: {self.current_model}")
        try:
            if not model_manager.load_generation_model(self.current_model):
                logger.warning(f"Failed to load default model {self.current_model}, trying fallback models...")
                # Try fallback models
                for fallback_model in ['mistral', 'ibm-granite']:
                    if fallback_model != self.current_model and fallback_model in config.AVAILABLE_MODELS:
                        logger.info(f"Trying fallback model: {fallback_model}")
                        if model_manager.load_generation_model(fallback_model):
                            self.current_model = fallback_model
                            logger.info(f"Successfully loaded fallback model: {fallback_model}")
                            break
                else:
                    logger.error("Failed to load any generation model - Q&A will not work properly")
            else:
                logger.info(f"Successfully loaded default model: {self.current_model}")
        except Exception as e:
            logger.error(f"Error during model initialization: {str(e)}")
            logger.warning("Q&A engine initialized without generation model - use set_model() to load one")
        
    def _load_system_prompts(self) -> Dict[str, str]:
        """Load system prompts for different models"""
        return {
            # Optimized prompts for FLAN-T5 (instruction-following models)
            "flan-t5": """Please answer the following question using only the information provided in the context. Be accurate and concise.

Context from documents:
{context}

Question: {question}

Answer:""",

            "flan-t5-base": """Please answer the following question using only the information provided in the context. Be accurate and concise.

Context from documents:
{context}

Question: {question}

Answer:""",

            # Fallback prompts for GPT-2 based models (less accurate)
            "distilgpt2": """Based on the following information from computer science documents, answer the question accurately.

Information: {context}

Question: {question}

Answer: According to the documents,""",

            # Legacy prompts for backward compatibility
            "ibm-granite": """You are StudyMate, an AI academic assistant. You help students understand their study materials by providing clear, accurate answers based on the provided context.

Instructions:
- Answer questions based ONLY on the provided context from the documents
- Be concise but comprehensive in your explanations
- If the context doesn't contain enough information, say so clearly
- Use examples from the context when helpful
- Structure your answers clearly with bullet points or numbered lists when appropriate
- Always cite which document(s) your answer comes from

Context: {context}

Question: {question}

Answer:""",

            "mistral": """<s>[INST] You are StudyMate, an intelligent academic assistant. Your role is to help students understand their study materials by providing accurate, helpful answers based on the provided document context.

Guidelines:
- Base your answers strictly on the provided context
- Be clear, concise, and educational
- If information is insufficient, acknowledge this limitation
- Use specific examples from the documents when relevant
- Organize complex answers with clear structure
- Always reference the source documents

Context from documents:
{context}

Student question: {question} [/INST]

Based on the provided documents, here's my answer:

""",
            
            "granite-code": """# StudyMate Academic Assistant

## Task
Answer the student's question using only the information provided in the document context below.

## Context
{context}

## Question
{question}

## Instructions
- Provide accurate answers based solely on the given context
- Be educational and clear in your explanations
- Reference specific documents when possible
- If context is insufficient, state this clearly
- Use structured formatting for complex answers

## Answer
"""
        }
    
    def set_model(self, model_key: str) -> bool:
        """Set the current model for Q&A"""
        try:
            if model_key not in config.AVAILABLE_MODELS:
                logger.error(f"Unknown model: {model_key}")
                return False
            
            if model_key != self.current_model:
                logger.info(f"Switching model from {self.current_model} to {model_key}")
                
                # Load the new model
                if model_manager.load_generation_model(model_key):
                    self.current_model = model_key
                    logger.info(f"Successfully switched to model: {model_key}")
                    return True
                else:
                    logger.error(f"Failed to load model: {model_key}")
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error setting model {model_key}: {str(e)}")
            return False
    
    def build_context(self, search_results: List[Dict[str, Any]], max_context_length: int = 3000) -> str:
        """Build context string from search results"""
        if not search_results:
            return ""
        
        context_parts = []
        current_length = 0
        
        for i, result in enumerate(search_results, 1):
            doc = result.get('document', result)
            text = doc.get('text', '')
            source = doc.get('source_file', 'Unknown')
            score = result.get('score', 0)
            
            # Create context entry
            context_entry = f"Document {i} ({source}, relevance: {score:.3f}):\n{text}\n"
            
            # Check if adding this entry would exceed the limit
            if current_length + len(context_entry) > max_context_length and context_parts:
                break
            
            context_parts.append(context_entry)
            current_length += len(context_entry)
        
        return "\n---\n".join(context_parts)
    
    def is_model_loaded(self) -> bool:
        """Check if a generation model is currently loaded"""
        return model_manager.generation_pipeline is not None

    def generate_answer(self, question: str, context: str, **kwargs) -> str:
        """Generate answer using the current HuggingFace model"""
        try:
            # Check if model is loaded
            if not self.is_model_loaded():
                logger.warning("No generation model loaded, attempting to load default model...")
                if not self.set_model(self.current_model):
                    return "I apologize, but no AI model is currently loaded. Please try selecting a model from the sidebar or contact support."

            # Get the appropriate system prompt
            system_prompt = self.system_prompts.get(
                self.current_model,
                self.system_prompts["flan-t5"]  # Use flan-t5 as fallback
            )

            # Format the prompt
            formatted_prompt = system_prompt.format(
                context=context,
                question=question
            )

            # Generate response
            logger.info(f"Generating answer using model: {self.current_model}")

            response = model_manager.generate_text(
                formatted_prompt,
                **kwargs
            )

            # Validate and improve the response
            validated_response = self._validate_answer(response, question, context)
            return validated_response

        except Exception as e:
            logger.error(f"Answer generation failed: {str(e)}")
            error_msg = str(e)
            if "No generation model loaded" in error_msg:
                return "I apologize, but no AI model is currently loaded. Please try selecting a model from the sidebar and try again."
            else:
                return f"I apologize, but I encountered an error while generating the answer: {error_msg}"

    def _validate_answer(self, answer: str, question: str, context: str) -> str:
        """Validate and improve the generated answer"""
        if not answer or len(answer.strip()) < 10:
            return self._create_fallback_answer(question, context)

        # Check if the answer seems relevant to the question
        question_words = set(question.lower().split())
        answer_words = set(answer.lower().split())

        # Remove common words
        common_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might', 'can', 'what', 'how', 'when', 'where', 'why', 'who'}
        question_words -= common_words
        answer_words -= common_words

        # Check for relevance - be more lenient for T5 models
        if question_words and answer_words:
            overlap = len(question_words & answer_words) / len(question_words)
            # More lenient threshold for instruction-tuned models
            min_overlap = 0.05 if model_manager.current_model_key == "flan-t5" else 0.1
            if overlap < min_overlap:
                logger.warning(f"Generated answer seems irrelevant (overlap: {overlap:.2f})")
                # For T5 models, try to use the answer anyway if it's not completely nonsensical
                if model_manager.current_model_key == "flan-t5" and len(answer.strip()) > 20:
                    logger.info("Using T5 answer despite low overlap - instruction-tuned model may be accurate")
                    return answer
                return self._create_fallback_answer(question, context)

        # Check for repetitive or nonsensical content
        words = answer.split()
        if len(words) > 10:
            unique_words = set(words)
            if len(unique_words) / len(words) < 0.3:  # Less than 30% unique words
                logger.warning("Generated answer is too repetitive")
                return self._create_fallback_answer(question, context)

        return answer

    def _create_fallback_answer(self, question: str, context: str) -> str:
        """Create a fallback answer when AI generation fails"""
        # Extract key information from context
        context_sentences = context.split('.')[:3]  # First 3 sentences
        relevant_info = '. '.join(sentence.strip() for sentence in context_sentences if sentence.strip())

        if relevant_info:
            return f"Based on the available information: {relevant_info}. Please refer to the source documents for more detailed information."
        else:
            return "I found some relevant information in your documents, but I'm having difficulty generating a clear answer. Please try rephrasing your question or refer to the source documents directly."
    
    def ask_question(self, question: str, **kwargs) -> Dict[str, Any]:
        """Complete Q&A pipeline: search + generate answer"""
        try:
            start_time = time.time()
            
            logger.info(f"Processing question: {question[:100]}...")
            
            # Validate question
            if not question or len(question.strip()) < 3:
                return {
                    'answer': "Please provide a more specific question.",
                    'sources': [],
                    'confidence': 0.0,
                    'model_used': self.current_model,
                    'processing_time': 0.0,
                    'error': False
                }
            
            # Search for relevant documents
            search_results = vector_db.search(question, k=kwargs.get('k', config.MAX_SEARCH_RESULTS))
            
            if not search_results:
                return {
                    'answer': "I couldn't find relevant information in your documents to answer this question. Please try rephrasing your question or upload more relevant materials.",
                    'sources': [],
                    'confidence': 0.0,
                    'model_used': self.current_model,
                    'processing_time': time.time() - start_time,
                    'error': False
                }
            
            # Build context
            context = self.build_context(search_results)
            
            # Generate answer
            answer = self.generate_answer(question, context, **kwargs)
            
            # Calculate confidence based on search scores
            confidence = self._calculate_confidence(search_results)
            
            # Prepare sources
            sources = self._prepare_sources(search_results)
            
            # Store in conversation history
            qa_entry = {
                'question': question,
                'answer': answer,
                'sources': sources,
                'confidence': confidence,
                'model_used': self.current_model,
                'timestamp': time.time(),
                'processing_time': time.time() - start_time
            }
            
            self.conversation_history.append(qa_entry)
            
            # Keep only last 20 exchanges
            if len(self.conversation_history) > 20:
                self.conversation_history = self.conversation_history[-20:]
            
            logger.info(f"Generated answer in {time.time() - start_time:.2f}s with confidence {confidence:.1f}%")
            
            return {
                'answer': answer,
                'sources': sources,
                'confidence': confidence,
                'model_used': self.current_model,
                'processing_time': time.time() - start_time,
                'num_sources': len(search_results),
                'error': False
            }
            
        except Exception as e:
            logger.error(f"Q&A pipeline failed: {str(e)}")
            return {
                'answer': f"I encountered an error while processing your question: {str(e)}",
                'sources': [],
                'confidence': 0.0,
                'model_used': self.current_model,
                'processing_time': time.time() - start_time if 'start_time' in locals() else 0.0,
                'error': True
            }
    
    def _calculate_confidence(self, search_results: List[Dict[str, Any]]) -> float:
        """Calculate confidence score based on search results"""
        if not search_results:
            return 0.0
        
        # Base confidence from average search scores
        avg_score = sum(result['score'] for result in search_results) / len(search_results)
        base_confidence = min(avg_score * 100, 100.0)
        
        # Boost for multiple relevant sources
        if len(search_results) > 3:
            base_confidence *= 1.1
        
        # Boost for high-scoring top result
        if search_results[0]['score'] > 0.8:
            base_confidence *= 1.2
        
        return min(base_confidence, 100.0)
    
    def _prepare_sources(self, search_results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Prepare source information for response"""
        sources = []
        
        for result in search_results[:5]:  # Top 5 sources
            doc = result.get('document', result)
            
            source = {
                'filename': doc.get('source_file', 'Unknown'),
                'score': result.get('score', 0.0),
                'rank': result.get('rank', 0),
                'text_preview': doc.get('text', '')[:300] + "..." if len(doc.get('text', '')) > 300 else doc.get('text', ''),
                'chunk_index': doc.get('chunk_index', 0)
            }
            sources.append(source)
        
        return sources
    
    def get_available_models(self) -> Dict[str, Dict[str, Any]]:
        """Get available models"""
        return config.AVAILABLE_MODELS
    
    def get_current_model(self) -> str:
        """Get current model key"""
        return self.current_model
    
    def get_conversation_history(self) -> List[Dict[str, Any]]:
        """Get conversation history"""
        return self.conversation_history.copy()
    
    def clear_conversation_history(self):
        """Clear conversation history"""
        logger.info("Clearing conversation history")
        self.conversation_history = []
    
    def get_stats(self) -> Dict[str, Any]:
        """Get Q&A engine statistics"""
        return {
            'current_model': self.current_model,
            'conversation_length': len(self.conversation_history),
            'total_questions': len(self.conversation_history),
            'avg_confidence': sum(qa.get('confidence', 0) for qa in self.conversation_history) / max(len(self.conversation_history), 1),
            'avg_processing_time': sum(qa.get('processing_time', 0) for qa in self.conversation_history) / max(len(self.conversation_history), 1),
            'model_info': model_manager.get_current_model_info(),
            'memory_usage': model_manager.get_model_memory_usage()
        }

# Global Q&A engine instance
qa_engine = HuggingFaceQAEngine()
