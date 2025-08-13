"""
Main backend manager for StudyMate with HuggingFace integration
"""

from pathlib import Path
from typing import List, Dict, Optional, Tuple
from .config import config, logger
from .pdf_processor import PDFProcessor
from .qa_engine_hf import qa_engine
from .vector_database import vector_db
from .model_manager import model_manager
import time

class StudyMateBackend:
    """Main backend manager with HuggingFace and FAISS integration"""

    def __init__(self):
        self.pdf_processor = PDFProcessor()
        self.processed_documents = []
        self.processing_history = []
        self.session_stats = {
            'documents_processed': 0,
            'questions_answered': 0,
            'total_chunks': 0,
            'session_start': time.time()
        }

        # Initialize models
        self._initialize_models()

    def _initialize_models(self):
        """Initialize HuggingFace models"""
        try:
            logger.info("Initializing models...")

            # Load embedding model first (required for vector database)
            if not model_manager.load_embedding_model():
                logger.warning("Failed to load embedding model")

            # Try to load saved vector database
            if not vector_db.load_index():
                logger.info("No saved vector database found")

            logger.info("Model initialization completed")

        except Exception as e:
            logger.error(f"Model initialization failed: {str(e)}")

    def set_generation_model(self, model_key: str) -> bool:
        """Set the text generation model"""
        return qa_engine.set_model(model_key)
    
    def process_uploaded_files(self, file_paths: List[Path]) -> Dict[str, any]:
        """Process uploaded PDF files and add to vector database"""
        try:
            logger.info(f"Starting processing of {len(file_paths)} files")
            start_time = time.time()

            # Validate file paths
            valid_paths = [p for p in file_paths if p.exists() and p.suffix.lower() == '.pdf']
            if not valid_paths:
                return {
                    'success': False,
                    'message': 'No valid PDF files found',
                    'stats': {},
                    'processing_time': 0
                }

            # Process PDFs with detailed results
            processed_pdfs, processing_summary = self.pdf_processor.process_multiple_pdfs(valid_paths)

            if not processed_pdfs:
                return {
                    'success': False,
                    'message': 'No files were successfully processed',
                    'stats': processing_summary,
                    'processing_time': time.time() - start_time
                }

            # Store processed documents
            self.processed_documents.extend(processed_pdfs)

            # Collect all chunks for vector database
            new_chunks = []
            for pdf_data in processed_pdfs:
                new_chunks.extend(pdf_data['chunks'])

            # Add chunks to vector database
            logger.info(f"Adding {len(new_chunks)} chunks to vector database")
            if not vector_db.add_documents(new_chunks):
                logger.error("Failed to add documents to vector database")
                return {
                    'success': False,
                    'message': 'Failed to add documents to vector database',
                    'stats': {},
                    'processing_time': time.time() - start_time
                }

            # Save vector database
            vector_db.save_index()

            # Update session stats
            self.session_stats['documents_processed'] += len(processed_pdfs)
            self.session_stats['total_chunks'] = len(vector_db.documents)

            # Calculate comprehensive statistics
            stats = self.calculate_processing_stats(processed_pdfs)
            stats.update(processing_summary)

            # Record processing history
            processing_record = {
                'timestamp': time.time(),
                'files_processed': len(processed_pdfs),
                'chunks_created': len(new_chunks),
                'processing_time': time.time() - start_time,
                'success': True
            }
            self.processing_history.append(processing_record)

            logger.info(f"Successfully processed {len(processed_pdfs)} files in {time.time() - start_time:.2f}s")

            return {
                'success': True,
                'message': f'Successfully processed {len(processed_pdfs)} files',
                'stats': stats,
                'num_chunks': len(new_chunks),
                'total_chunks': len(vector_db.documents),
                'processing_time': time.time() - start_time,
                'failed_files': processing_summary.get('failed_file_details', [])
            }

        except Exception as e:
            logger.error(f"Error processing files: {str(e)}")

            # Record failed processing
            processing_record = {
                'timestamp': time.time(),
                'files_processed': 0,
                'error': str(e),
                'success': False
            }
            self.processing_history.append(processing_record)

            return {
                'success': False,
                'message': f'Error processing files: {str(e)}',
                'stats': {},
                'processing_time': 0
            }
    
    def ask_question(self, question: str, **kwargs) -> Dict[str, any]:
        """Ask a question using HuggingFace models"""
        if len(vector_db.documents) == 0:
            return {
                'answer': 'No documents have been processed yet. Please upload and process some PDF files first.',
                'sources': [],
                'confidence': 0.0,
                'model_used': qa_engine.get_current_model(),
                'error': False,
                'suggestions': ['Upload PDF documents first', 'Try the document upload page']
            }

        logger.info(f"Processing question: {question[:50]}...")

        # Get answer from HuggingFace Q&A engine
        result = qa_engine.ask_question(question, **kwargs)

        # Update session stats
        self.session_stats['questions_answered'] += 1

        return result
    
    def calculate_processing_stats(self, processed_pdfs: List[Dict[str, any]]) -> Dict[str, any]:
        """Calculate processing statistics"""
        if not processed_pdfs:
            return {}
        
        total_pages = sum(pdf['metadata']['total_pages'] for pdf in processed_pdfs)
        total_words = sum(pdf['metadata']['total_words'] for pdf in processed_pdfs)
        total_chars = sum(pdf['metadata']['total_characters'] for pdf in processed_pdfs)
        
        return {
            'total_files': len(processed_pdfs),
            'total_pages': total_pages,
            'total_words': total_words,
            'total_characters': total_chars,
            'average_words_per_file': total_words / len(processed_pdfs),
            'average_pages_per_file': total_pages / len(processed_pdfs)
        }
    
    def get_document_list(self) -> List[Dict[str, any]]:
        """Get list of processed documents"""
        documents = []
        
        for pdf_data in self.processed_documents:
            metadata = pdf_data['metadata']
            documents.append({
                'filename': metadata['filename'],
                'pages': metadata['total_pages'],
                'words': metadata['total_words'],
                'chunks': len(pdf_data['chunks'])
            })
        
        return documents
    
    def clear_all_data(self):
        """Clear all processed data"""
        self.processed_documents = []
        vector_db.clear()
        qa_engine.clear_conversation_history()

        # Reset session stats
        self.session_stats = {
            'documents_processed': 0,
            'questions_answered': 0,
            'total_chunks': 0,
            'session_start': time.time()
        }

    def get_conversation_history(self) -> List[Dict]:
        """Get conversation history"""
        return qa_engine.get_conversation_history()
    
    def get_system_stats(self) -> Dict[str, any]:
        """Get comprehensive system statistics"""
        qa_stats = qa_engine.get_stats()
        vector_stats = vector_db.get_stats()
        session_duration = time.time() - self.session_stats['session_start']

        return {
            'documents_processed': len(self.processed_documents),
            'total_chunks': vector_stats['total_documents'],
            'qa_engine': qa_stats,
            'vector_database': vector_stats,
            'ready_for_questions': vector_stats['total_documents'] > 0,
            'session_stats': {
                **self.session_stats,
                'session_duration_minutes': round(session_duration / 60, 1)
            },
            'processing_history': len(self.processing_history),
            'unique_sources': len(set(doc['metadata']['filename'] for doc in self.processed_documents))
        }

    def get_available_models(self) -> Dict[str, Dict[str, any]]:
        """Get available HuggingFace models"""
        return qa_engine.get_available_models()

    def get_current_model(self) -> str:
        """Get current model"""
        return qa_engine.get_current_model()

    def get_model_info(self) -> Dict[str, any]:
        """Get current model information"""
        return model_manager.get_current_model_info()

    def get_memory_usage(self) -> Dict[str, any]:
        """Get memory usage information"""
        return model_manager.get_model_memory_usage()

    def get_document_list(self) -> List[Dict[str, any]]:
        """Get list of processed documents"""
        documents = []

        for pdf_data in self.processed_documents:
            metadata = pdf_data['metadata']
            documents.append({
                'filename': metadata['filename'],
                'pages': metadata['total_pages'],
                'words': metadata['total_words'],
                'chunks': len(pdf_data['chunks'])
            })

        return documents

    def get_detailed_analytics(self) -> Dict[str, any]:
        """Get detailed analytics for the analytics page"""
        if not self.processed_documents:
            return {'error': 'No documents processed'}

        # Document analytics
        total_pages = sum(doc['metadata']['total_pages'] for doc in self.processed_documents)
        total_words = sum(doc['metadata']['total_words'] for doc in self.processed_documents)
        total_chars = sum(doc['metadata']['total_characters'] for doc in self.processed_documents)

        # File size analytics
        total_size = sum(doc['metadata'].get('file_size', 0) for doc in self.processed_documents)

        # Processing analytics
        successful_processing = sum(1 for record in self.processing_history if record['success'])
        total_processing_time = sum(record.get('processing_time', 0) for record in self.processing_history)

        # Q&A analytics
        conversation_summary = self.qa_engine.get_conversation_summary()

        return {
            'document_analytics': {
                'total_documents': len(self.processed_documents),
                'total_pages': total_pages,
                'total_words': total_words,
                'total_characters': total_chars,
                'total_size_mb': round(total_size / (1024 * 1024), 2),
                'avg_pages_per_doc': round(total_pages / len(self.processed_documents), 1),
                'avg_words_per_doc': round(total_words / len(self.processed_documents), 1)
            },
            'processing_analytics': {
                'total_processing_sessions': len(self.processing_history),
                'successful_sessions': successful_processing,
                'total_processing_time': round(total_processing_time, 2),
                'avg_processing_time': round(total_processing_time / max(len(self.processing_history), 1), 2)
            },
            'qa_analytics': conversation_summary,
            'search_analytics': self.qa_engine.search_engine.get_stats()
        }

    def export_session_data(self) -> Dict[str, any]:
        """Export session data for backup or analysis"""
        return {
            'session_stats': self.session_stats,
            'processing_history': self.processing_history,
            'conversation_history': self.qa_engine.get_conversation_history(),
            'document_list': self.get_document_list(),
            'system_stats': self.get_system_stats(),
            'export_timestamp': time.time()
        }
