"""
Enhanced PDF processing for StudyMate with FAISS integration
"""

import fitz  # PyMuPDF
import re
import hashlib
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from .config import config, logger

class PDFProcessor:
    """Enhanced PDF text extraction and processing for vector database"""

    def __init__(self):
        self.processed_files = {}
        self.processing_stats = {}
        self.supported_formats = ['.pdf']
    
    def get_file_hash(self, file_path: Path) -> str:
        """Generate MD5 hash of a file"""
        hash_md5 = hashlib.md5()
        try:
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_md5.update(chunk)
            return hash_md5.hexdigest()
        except Exception as e:
            logger.error(f"Error generating hash for {file_path}: {e}")
            return ""

    def extract_text_from_pdf(self, pdf_path: Path) -> Dict[str, any]:
        """Extract text from PDF file with robust error handling"""
        try:
            logger.info(f"Starting PDF extraction for: {pdf_path.name}")

            # Check if file exists
            if not pdf_path.exists():
                raise FileNotFoundError(f"PDF file not found: {pdf_path}")

            # Generate file hash for caching
            file_hash = self.get_file_hash(pdf_path)

            # Check cache
            if file_hash in self.processed_files:
                logger.info(f"Using cached version of {pdf_path.name}")
                return self.processed_files[file_hash]

            doc = fitz.open(pdf_path)

            # Extract text from all pages
            full_text = ""
            pages_text = []
            total_chars = 0

            for page_num in range(len(doc)):
                try:
                    page = doc.load_page(page_num)
                    page_text = page.get_text()

                    if page_text.strip():
                        cleaned_text = self.clean_text(page_text)
                        if cleaned_text:  # Only add non-empty pages
                            page_info = {
                                'page_number': page_num + 1,
                                'text': cleaned_text,
                                'word_count': len(cleaned_text.split()),
                                'char_count': len(cleaned_text)
                            }
                            pages_text.append(page_info)
                            full_text += cleaned_text + " "
                            total_chars += len(cleaned_text)

                except Exception as e:
                    logger.warning(f"Error processing page {page_num + 1} of {pdf_path.name}: {e}")
                    continue

            doc.close()

            # Create comprehensive metadata
            metadata = {
                'filename': pdf_path.name,
                'file_path': str(pdf_path),
                'file_hash': file_hash,
                'file_size': pdf_path.stat().st_size,
                'total_pages': len(doc),
                'pages_with_text': len(pages_text),
                'total_words': len(full_text.split()),
                'total_characters': total_chars,
                'extraction_success': True
            }

            result = {
                'metadata': metadata,
                'pages': pages_text,
                'full_text': full_text.strip()
            }

            # Cache the result
            self.processed_files[file_hash] = result

            logger.info(f"Successfully extracted text from {pdf_path.name}: "
                       f"{metadata['total_words']} words, {len(pages_text)} pages")

            return result

        except Exception as e:
            logger.error(f"Failed to extract text from PDF {pdf_path.name}: {str(e)}")
            raise Exception(f"Failed to extract text from PDF: {str(e)}")
    
    def clean_text(self, text: str) -> str:
        """Clean and normalize text with improved handling"""
        if not text:
            return ""

        # Remove extra whitespace and normalize
        text = ' '.join(text.split())

        # Remove special characters but preserve important punctuation
        text = re.sub(r'[^\w\s\.\,\!\?\;\:\-\(\)\[\]\"\'\/]', ' ', text)

        # Fix common PDF extraction issues
        text = re.sub(r'\s+', ' ', text)  # Multiple spaces to single
        text = re.sub(r'([a-z])([A-Z])', r'\1 \2', text)  # Add space between camelCase
        text = re.sub(r'(\w)([\.!?])(\w)', r'\1\2 \3', text)  # Space after punctuation

        # Remove very short words (likely extraction artifacts)
        words = text.split()
        words = [word for word in words if len(word) > 1 or word.lower() in ['a', 'i']]

        return ' '.join(words).strip()
    
    def chunk_text(self, text: str) -> List[Dict[str, any]]:
        """Split text into intelligent chunks with metadata"""
        if not text or len(text) < config.MIN_CHUNK_SIZE:
            return []

        if len(text) <= config.CHUNK_SIZE:
            return [{
                'text': text,
                'start_pos': 0,
                'end_pos': len(text),
                'word_count': len(text.split()),
                'char_count': len(text)
            }]

        chunks = []
        start = 0
        chunk_index = 0

        while start < len(text):
            end = start + config.CHUNK_SIZE

            # Try to break at natural boundaries
            if end < len(text):
                # Look for sentence endings first
                best_break = end
                for i in range(end, max(start + config.CHUNK_SIZE // 2, end - 200), -1):
                    if text[i] in '.!?\n':
                        best_break = i + 1
                        break
                    elif text[i] in ' \t' and i > start + config.CHUNK_SIZE // 2:
                        best_break = i

                end = best_break

            chunk_text = text[start:end].strip()

            if len(chunk_text) >= config.MIN_CHUNK_SIZE:
                chunk_info = {
                    'text': chunk_text,
                    'start_pos': start,
                    'end_pos': end,
                    'word_count': len(chunk_text.split()),
                    'char_count': len(chunk_text),
                    'chunk_index': chunk_index
                }
                chunks.append(chunk_info)
                chunk_index += 1

            # Move start position with overlap
            start = max(end - config.CHUNK_OVERLAP, start + config.MIN_CHUNK_SIZE)

            if start >= len(text):
                break

        logger.info(f"Created {len(chunks)} chunks from text of {len(text)} characters")
        return chunks
    
    def process_pdf(self, pdf_path: Path) -> Dict[str, any]:
        """Process a PDF file completely with full metadata"""
        try:
            logger.info(f"Processing PDF: {pdf_path.name}")

            # Extract text
            pdf_data = self.extract_text_from_pdf(pdf_path)

            # Create chunks
            chunk_data = self.chunk_text(pdf_data['full_text'])

            # Enhance chunks with additional metadata
            enhanced_chunks = []
            for i, chunk_info in enumerate(chunk_data):
                enhanced_chunk = {
                    'chunk_id': f"{pdf_data['metadata']['file_hash']}_{i}",
                    'text': chunk_info['text'],
                    'chunk_index': i,
                    'source_file': pdf_data['metadata']['filename'],
                    'file_hash': pdf_data['metadata']['file_hash'],
                    'word_count': chunk_info['word_count'],
                    'char_count': chunk_info['char_count'],
                    'start_pos': chunk_info['start_pos'],
                    'end_pos': chunk_info['end_pos'],
                    'file_path': str(pdf_path)
                }
                enhanced_chunks.append(enhanced_chunk)

            pdf_data['chunks'] = enhanced_chunks
            pdf_data['chunk_count'] = len(enhanced_chunks)

            # Update processing stats
            self.processing_stats[pdf_path.name] = {
                'success': True,
                'chunks_created': len(enhanced_chunks),
                'total_words': pdf_data['metadata']['total_words'],
                'total_pages': pdf_data['metadata']['total_pages']
            }

            logger.info(f"Successfully processed {pdf_path.name}: {len(enhanced_chunks)} chunks created")
            return pdf_data

        except Exception as e:
            logger.error(f"Error processing PDF {pdf_path.name}: {str(e)}")
            self.processing_stats[pdf_path.name] = {
                'success': False,
                'error': str(e)
            }
            raise

    def process_multiple_pdfs(self, pdf_paths: List[Path]) -> Tuple[List[Dict[str, any]], Dict[str, any]]:
        """Process multiple PDF files with comprehensive error handling"""
        processed_pdfs = []
        failed_files = []

        logger.info(f"Starting batch processing of {len(pdf_paths)} PDF files")

        for i, pdf_path in enumerate(pdf_paths):
            try:
                logger.info(f"Processing file {i+1}/{len(pdf_paths)}: {pdf_path.name}")
                pdf_data = self.process_pdf(pdf_path)
                processed_pdfs.append(pdf_data)

            except Exception as e:
                logger.error(f"Failed to process {pdf_path.name}: {str(e)}")
                failed_files.append({
                    'filename': pdf_path.name,
                    'error': str(e)
                })
                continue

        # Generate summary statistics
        summary = {
            'total_files': len(pdf_paths),
            'successful_files': len(processed_pdfs),
            'failed_files': len(failed_files),
            'failed_file_details': failed_files,
            'processing_stats': self.processing_stats.copy()
        }

        logger.info(f"Batch processing complete: {len(processed_pdfs)}/{len(pdf_paths)} files successful")

        return processed_pdfs, summary

    def get_processing_summary(self) -> Dict[str, any]:
        """Get summary of all processing operations"""
        return {
            'files_processed': len(self.processed_files),
            'cache_size': len(self.processed_files),
            'processing_stats': self.processing_stats.copy()
        }
