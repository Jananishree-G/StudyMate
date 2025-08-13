"""
Embeddings module for StudyMate
Handles text embeddings using SentenceTransformers and FAISS indexing
"""

import numpy as np
import faiss
import pickle
import logging
from pathlib import Path
from typing import List, Dict, Optional, Tuple
import streamlit as st
from sentence_transformers import SentenceTransformer

from config import config
from utils import get_timestamp

logger = logging.getLogger(__name__)

class EmbeddingManager:
    """Manages text embeddings and FAISS indexing"""
    
    def __init__(self, model_name: str = None):
        self.model_name = model_name or config.HUGGINGFACE_MODEL
        self.model = None
        self.index = None
        self.chunks_metadata = []
        self.embedding_dimension = config.EMBEDDING_DIMENSION
        
    def load_model(self):
        """Load the SentenceTransformer model"""
        try:
            if self.model is None:
                with st.spinner(f"Loading embedding model: {self.model_name}"):
                    self.model = SentenceTransformer(self.model_name)
                    self.embedding_dimension = self.model.get_sentence_embedding_dimension()
                    logger.info(f"Loaded embedding model: {self.model_name}")
                    logger.info(f"Embedding dimension: {self.embedding_dimension}")
            
            return True
            
        except Exception as e:
            logger.error(f"Error loading embedding model: {str(e)}")
            st.error(f"Failed to load embedding model: {str(e)}")
            return False
    
    def create_embeddings(self, texts: List[str]) -> np.ndarray:
        """
        Create embeddings for a list of texts
        
        Args:
            texts: List of text strings
            
        Returns:
            NumPy array of embeddings
        """
        if not self.load_model():
            raise Exception("Failed to load embedding model")
        
        try:
            with st.spinner(f"Creating embeddings for {len(texts)} text chunks..."):
                embeddings = self.model.encode(
                    texts,
                    show_progress_bar=True,
                    batch_size=32,
                    convert_to_numpy=True
                )
            
            logger.info(f"Created embeddings for {len(texts)} texts")
            return embeddings
            
        except Exception as e:
            logger.error(f"Error creating embeddings: {str(e)}")
            raise Exception(f"Failed to create embeddings: {str(e)}")
    
    def create_faiss_index(self, embeddings: np.ndarray) -> faiss.Index:
        """
        Create FAISS index from embeddings
        
        Args:
            embeddings: NumPy array of embeddings
            
        Returns:
            FAISS index
        """
        try:
            dimension = embeddings.shape[1]
            
            # Create appropriate index based on configuration
            if config.FAISS_INDEX_TYPE == "IndexFlatIP":
                index = faiss.IndexFlatIP(dimension)
            elif config.FAISS_INDEX_TYPE == "IndexFlatL2":
                index = faiss.IndexFlatL2(dimension)
            else:
                # Default to Inner Product
                index = faiss.IndexFlatIP(dimension)
            
            # Normalize embeddings for cosine similarity (if using IP)
            if config.FAISS_INDEX_TYPE == "IndexFlatIP":
                faiss.normalize_L2(embeddings)
            
            # Add embeddings to index
            index.add(embeddings.astype('float32'))
            
            logger.info(f"Created FAISS index with {index.ntotal} vectors")
            return index
            
        except Exception as e:
            logger.error(f"Error creating FAISS index: {str(e)}")
            raise Exception(f"Failed to create FAISS index: {str(e)}")
    
    def build_index_from_chunks(self, chunks: List[Dict[str, any]]) -> bool:
        """
        Build FAISS index from text chunks
        
        Args:
            chunks: List of text chunks with metadata
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if not chunks:
                logger.warning("No chunks provided for indexing")
                return False
            
            # Extract texts from chunks
            texts = [chunk['text'] for chunk in chunks]
            
            # Create embeddings
            embeddings = self.create_embeddings(texts)
            
            # Create FAISS index
            self.index = self.create_faiss_index(embeddings)
            
            # Store chunks metadata
            self.chunks_metadata = chunks
            
            logger.info(f"Successfully built index from {len(chunks)} chunks")
            return True
            
        except Exception as e:
            logger.error(f"Error building index: {str(e)}")
            st.error(f"Failed to build search index: {str(e)}")
            return False
    
    def search(self, query: str, k: int = 5) -> List[Dict[str, any]]:
        """
        Search for similar chunks using the query
        
        Args:
            query: Search query
            k: Number of results to return
            
        Returns:
            List of similar chunks with scores
        """
        if self.index is None or not self.chunks_metadata:
            logger.error("Index not built. Please build index first.")
            return []
        
        try:
            # Create query embedding
            query_embedding = self.create_embeddings([query])
            
            # Normalize for cosine similarity (if using IP)
            if config.FAISS_INDEX_TYPE == "IndexFlatIP":
                faiss.normalize_L2(query_embedding)
            
            # Search in index
            scores, indices = self.index.search(query_embedding.astype('float32'), k)
            
            # Prepare results
            results = []
            for i, (score, idx) in enumerate(zip(scores[0], indices[0])):
                if idx < len(self.chunks_metadata):
                    result = {
                        'rank': i + 1,
                        'score': float(score),
                        'chunk': self.chunks_metadata[idx].copy()
                    }
                    results.append(result)
            
            logger.info(f"Found {len(results)} similar chunks for query")
            return results
            
        except Exception as e:
            logger.error(f"Error during search: {str(e)}")
            return []
    
    def save_index(self, save_path: Path = None) -> bool:
        """
        Save FAISS index and metadata to disk
        
        Args:
            save_path: Path to save the index
            
        Returns:
            True if successful, False otherwise
        """
        if self.index is None:
            logger.error("No index to save")
            return False
        
        try:
            if save_path is None:
                timestamp = get_timestamp()
                save_path = config.EMBEDDINGS_DIR / f"index_{timestamp}"
            
            save_path.mkdir(parents=True, exist_ok=True)
            
            # Save FAISS index
            index_file = save_path / "faiss_index.bin"
            faiss.write_index(self.index, str(index_file))
            
            # Save metadata
            metadata_file = save_path / "chunks_metadata.pkl"
            with open(metadata_file, 'wb') as f:
                pickle.dump(self.chunks_metadata, f)
            
            # Save configuration
            config_file = save_path / "config.pkl"
            index_config = {
                'model_name': self.model_name,
                'embedding_dimension': self.embedding_dimension,
                'index_type': config.FAISS_INDEX_TYPE,
                'total_chunks': len(self.chunks_metadata)
            }
            with open(config_file, 'wb') as f:
                pickle.dump(index_config, f)
            
            logger.info(f"Saved index to {save_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving index: {str(e)}")
            return False
    
    def load_index(self, load_path: Path) -> bool:
        """
        Load FAISS index and metadata from disk
        
        Args:
            load_path: Path to load the index from
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if not load_path.exists():
                logger.error(f"Index path does not exist: {load_path}")
                return False
            
            # Load FAISS index
            index_file = load_path / "faiss_index.bin"
            if index_file.exists():
                self.index = faiss.read_index(str(index_file))
            else:
                logger.error("FAISS index file not found")
                return False
            
            # Load metadata
            metadata_file = load_path / "chunks_metadata.pkl"
            if metadata_file.exists():
                with open(metadata_file, 'rb') as f:
                    self.chunks_metadata = pickle.load(f)
            else:
                logger.error("Chunks metadata file not found")
                return False
            
            # Load configuration
            config_file = load_path / "config.pkl"
            if config_file.exists():
                with open(config_file, 'rb') as f:
                    index_config = pickle.load(f)
                    self.model_name = index_config.get('model_name', self.model_name)
                    self.embedding_dimension = index_config.get('embedding_dimension', self.embedding_dimension)
            
            logger.info(f"Loaded index from {load_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error loading index: {str(e)}")
            return False
    
    def get_index_stats(self) -> Dict[str, any]:
        """Get statistics about the current index"""
        if self.index is None:
            return {}
        
        stats = {
            'total_vectors': self.index.ntotal,
            'embedding_dimension': self.embedding_dimension,
            'model_name': self.model_name,
            'index_type': config.FAISS_INDEX_TYPE,
            'total_chunks': len(self.chunks_metadata)
        }
        
        return stats
