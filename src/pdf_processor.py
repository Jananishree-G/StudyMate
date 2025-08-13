"""
PDF processing module for StudyMate
Handles PDF text extraction and preprocessing using PyMuPDF
"""

import fitz  # PyMuPDF
import logging
from pathlib import Path
from typing import List, Dict, Optional, Tuple
import streamlit as st

from config import config
from utils import clean_text, chunk_text, get_file_hash

logger = logging.getLogger(__name__)

class PDFProcessor:
    """PDF processing class for text extraction and chunking"""
    
    def __init__(self):
        self.processed_files = {}
    
    def extract_text_from_pdf(self, pdf_path: Path) -> Dict[str, any]:
        """
        Extract text from PDF file
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            Dictionary containing extracted text and metadata
        """
        try:
            doc = fitz.open(pdf_path)
            
            text_content = []
            metadata = {
                'filename': pdf_path.name,
                'file_path': str(pdf_path),
                'file_hash': get_file_hash(pdf_path),
                'total_pages': len(doc),
                'title': doc.metadata.get('title', ''),
                'author': doc.metadata.get('author', ''),
                'subject': doc.metadata.get('subject', ''),
                'creator': doc.metadata.get('creator', ''),
                'producer': doc.metadata.get('producer', ''),
                'creation_date': doc.metadata.get('creationDate', ''),
                'modification_date': doc.metadata.get('modDate', '')
            }
            
            # Extract text from each page
            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                page_text = page.get_text()
                
                if page_text.strip():  # Only add non-empty pages
                    page_info = {
                        'page_number': page_num + 1,
                        'text': clean_text(page_text),
                        'char_count': len(page_text),
                        'word_count': len(page_text.split())
                    }
                    text_content.append(page_info)
            
            doc.close()
            
            # Calculate total statistics
            total_chars = sum(page['char_count'] for page in text_content)
            total_words = sum(page['word_count'] for page in text_content)
            
            metadata.update({
                'total_characters': total_chars,
                'total_words': total_words,
                'pages_with_text': len(text_content)
            })
            
            result = {
                'metadata': metadata,
                'pages': text_content,
                'full_text': ' '.join([page['text'] for page in text_content])
            }
            
            logger.info(f"Successfully extracted text from {pdf_path.name}: "
                       f"{total_words} words, {len(text_content)} pages")
            
            return result
            
        except Exception as e:
            logger.error(f"Error extracting text from {pdf_path}: {str(e)}")
            raise Exception(f"Failed to extract text from PDF: {str(e)}")
    
    def process_multiple_pdfs(self, pdf_paths: List[Path]) -> List[Dict[str, any]]:
        """
        Process multiple PDF files
        
        Args:
            pdf_paths: List of PDF file paths
            
        Returns:
            List of processed PDF data
        """
        processed_pdfs = []
        
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        for i, pdf_path in enumerate(pdf_paths):
            try:
                status_text.text(f"Processing {pdf_path.name}...")
                
                # Check if already processed
                file_hash = get_file_hash(pdf_path)
                if file_hash in self.processed_files:
                    logger.info(f"Using cached version of {pdf_path.name}")
                    processed_pdfs.append(self.processed_files[file_hash])
                else:
                    # Extract text from PDF
                    pdf_data = self.extract_text_from_pdf(pdf_path)
                    
                    # Cache the result
                    self.processed_files[file_hash] = pdf_data
                    processed_pdfs.append(pdf_data)
                
                # Update progress
                progress = (i + 1) / len(pdf_paths)
                progress_bar.progress(progress)
                
            except Exception as e:
                logger.error(f"Error processing {pdf_path.name}: {str(e)}")
                st.error(f"Error processing {pdf_path.name}: {str(e)}")
                continue
        
        status_text.text("Processing complete!")
        progress_bar.empty()
        status_text.empty()
        
        return processed_pdfs
    
    def create_text_chunks(self, pdf_data: Dict[str, any]) -> List[Dict[str, any]]:
        """
        Create text chunks from processed PDF data
        
        Args:
            pdf_data: Processed PDF data
            
        Returns:
            List of text chunks with metadata
        """
        chunks = []
        full_text = pdf_data['full_text']
        metadata = pdf_data['metadata']
        
        # Create chunks from full text
        text_chunks = chunk_text(full_text, config.CHUNK_SIZE, config.CHUNK_OVERLAP)
        
        for i, chunk_text in enumerate(text_chunks):
            chunk = {
                'chunk_id': f"{metadata['file_hash']}_{i}",
                'text': chunk_text,
                'source_file': metadata['filename'],
                'file_path': metadata['file_path'],
                'file_hash': metadata['file_hash'],
                'chunk_index': i,
                'char_count': len(chunk_text),
                'word_count': len(chunk_text.split()),
                'metadata': metadata
            }
            chunks.append(chunk)
        
        logger.info(f"Created {len(chunks)} chunks from {metadata['filename']}")
        return chunks
    
    def create_chunks_from_multiple_pdfs(self, processed_pdfs: List[Dict[str, any]]) -> List[Dict[str, any]]:
        """
        Create text chunks from multiple processed PDFs
        
        Args:
            processed_pdfs: List of processed PDF data
            
        Returns:
            List of all text chunks
        """
        all_chunks = []
        
        for pdf_data in processed_pdfs:
            chunks = self.create_text_chunks(pdf_data)
            all_chunks.extend(chunks)
        
        logger.info(f"Created total of {len(all_chunks)} chunks from {len(processed_pdfs)} PDFs")
        return all_chunks
    
    def get_processing_stats(self, processed_pdfs: List[Dict[str, any]]) -> Dict[str, any]:
        """
        Get processing statistics
        
        Args:
            processed_pdfs: List of processed PDF data
            
        Returns:
            Dictionary with processing statistics
        """
        if not processed_pdfs:
            return {}
        
        total_pages = sum(pdf['metadata']['total_pages'] for pdf in processed_pdfs)
        total_words = sum(pdf['metadata']['total_words'] for pdf in processed_pdfs)
        total_chars = sum(pdf['metadata']['total_characters'] for pdf in processed_pdfs)
        
        stats = {
            'total_files': len(processed_pdfs),
            'total_pages': total_pages,
            'total_words': total_words,
            'total_characters': total_chars,
            'average_words_per_file': total_words / len(processed_pdfs),
            'average_pages_per_file': total_pages / len(processed_pdfs)
        }
        
        return stats
