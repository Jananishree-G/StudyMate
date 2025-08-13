"""
FAISS Vector Database for StudyMate
Efficient vector storage and similarity search
"""

import faiss
import numpy as np
import pickle
import json
from pathlib import Path
from typing import List, Dict, Tuple, Optional, Any
from .config import config, logger
from .model_manager import model_manager

class VectorDatabase:
    """FAISS-based vector database for document embeddings"""
    
    def __init__(self):
        self.index = None
        self.documents = []
        self.dimension = config.EMBEDDING_DIMENSION
        self.index_type = config.FAISS_INDEX_TYPE
        self.is_trained = False
        
    def _create_index(self, dimension: int) -> faiss.Index:
        """Create a FAISS index based on configuration"""
        if self.index_type == "IndexFlatIP":
            # Inner Product (for cosine similarity with normalized vectors)
            index = faiss.IndexFlatIP(dimension)
        elif self.index_type == "IndexFlatL2":
            # L2 distance
            index = faiss.IndexFlatL2(dimension)
        elif self.index_type == "IndexIVFFlat":
            # IVF with flat quantizer (for larger datasets)
            quantizer = faiss.IndexFlatIP(dimension)
            index = faiss.IndexIVFFlat(quantizer, dimension, config.FAISS_NLIST)
        else:
            # Default to flat IP
            index = faiss.IndexFlatIP(dimension)
        
        logger.info(f"Created FAISS index: {type(index).__name__}")
        return index
    
    def add_documents(self, documents: List[Dict[str, Any]]) -> bool:
        """Add documents to the vector database"""
        try:
            if not documents:
                logger.warning("No documents to add")
                return False
            
            logger.info(f"Adding {len(documents)} documents to vector database")
            
            # Extract texts for embedding
            texts = [doc['text'] for doc in documents]
            
            # Create embeddings
            embeddings = model_manager.create_embeddings(texts)
            
            if embeddings is None:
                logger.error("Failed to create embeddings")
                return False
            
            # Convert to numpy array and normalize for cosine similarity
            embeddings_np = embeddings.cpu().numpy().astype('float32')
            
            # Normalize vectors for cosine similarity with inner product
            if self.index_type == "IndexFlatIP":
                faiss.normalize_L2(embeddings_np)
            
            # Create index if it doesn't exist
            if self.index is None:
                self.dimension = embeddings_np.shape[1]
                self.index = self._create_index(self.dimension)
            
            # Train index if necessary (for IVF indices)
            if not self.is_trained and hasattr(self.index, 'train'):
                logger.info("Training FAISS index...")
                self.index.train(embeddings_np)
                self.is_trained = True
            
            # Add vectors to index
            start_id = len(self.documents)
            self.index.add(embeddings_np)
            
            # Store document metadata with IDs
            for i, doc in enumerate(documents):
                doc_with_id = doc.copy()
                doc_with_id['vector_id'] = start_id + i
                self.documents.append(doc_with_id)
            
            logger.info(f"Successfully added {len(documents)} documents. Total: {len(self.documents)}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to add documents to vector database: {str(e)}")
            return False
    
    def search(self, query: str, k: int = None) -> List[Dict[str, Any]]:
        """Search for similar documents"""
        try:
            if k is None:
                k = config.MAX_SEARCH_RESULTS
            
            if self.index is None or len(self.documents) == 0:
                logger.warning("Vector database is empty")
                return []
            
            # Create query embedding
            query_embedding = model_manager.create_embeddings([query])
            
            if query_embedding is None:
                logger.error("Failed to create query embedding")
                return []
            
            # Convert to numpy and normalize
            query_np = query_embedding.cpu().numpy().astype('float32')
            
            if self.index_type == "IndexFlatIP":
                faiss.normalize_L2(query_np)
            
            # Set nprobe for IVF indices
            if hasattr(self.index, 'nprobe'):
                self.index.nprobe = config.FAISS_NPROBE
            
            # Search
            scores, indices = self.index.search(query_np, min(k, len(self.documents)))
            
            # Prepare results
            results = []
            for i, (score, idx) in enumerate(zip(scores[0], indices[0])):
                if idx == -1:  # FAISS returns -1 for invalid indices
                    continue
                
                if score < config.MIN_SIMILARITY_SCORE:
                    continue
                
                doc = self.documents[idx].copy()
                result = {
                    'rank': i + 1,
                    'score': float(score),
                    'document': doc,
                    'chunk_id': doc.get('chunk_id', f'chunk_{idx}'),
                    'text': doc.get('text', ''),
                    'source_file': doc.get('source_file', 'unknown'),
                    'chunk_index': doc.get('chunk_index', 0)
                }
                results.append(result)
            
            logger.info(f"Found {len(results)} similar documents for query")
            return results
            
        except Exception as e:
            logger.error(f"Vector search failed: {str(e)}")
            return []
    
    def save_index(self, filepath: Path = None) -> bool:
        """Save the FAISS index and metadata to disk"""
        try:
            if self.index is None:
                logger.warning("No index to save")
                return False
            
            if filepath is None:
                filepath = config.EMBEDDINGS_DIR / "faiss_index"
            
            # Save FAISS index
            index_file = filepath.with_suffix('.faiss')
            faiss.write_index(self.index, str(index_file))
            
            # Save metadata
            metadata = {
                'documents': self.documents,
                'dimension': self.dimension,
                'index_type': self.index_type,
                'is_trained': self.is_trained,
                'total_documents': len(self.documents)
            }
            
            metadata_file = filepath.with_suffix('.json')
            with open(metadata_file, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Saved FAISS index to {index_file}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to save index: {str(e)}")
            return False
    
    def load_index(self, filepath: Path = None) -> bool:
        """Load the FAISS index and metadata from disk"""
        try:
            if filepath is None:
                filepath = config.EMBEDDINGS_DIR / "faiss_index"
            
            index_file = filepath.with_suffix('.faiss')
            metadata_file = filepath.with_suffix('.json')
            
            if not index_file.exists() or not metadata_file.exists():
                logger.info("No saved index found")
                return False
            
            # Load FAISS index
            self.index = faiss.read_index(str(index_file))
            
            # Load metadata
            with open(metadata_file, 'r', encoding='utf-8') as f:
                metadata = json.load(f)
            
            self.documents = metadata['documents']
            self.dimension = metadata['dimension']
            self.index_type = metadata['index_type']
            self.is_trained = metadata['is_trained']
            
            logger.info(f"Loaded FAISS index with {len(self.documents)} documents")
            return True
            
        except Exception as e:
            logger.error(f"Failed to load index: {str(e)}")
            return False
    
    def get_stats(self) -> Dict[str, Any]:
        """Get vector database statistics"""
        stats = {
            'total_documents': len(self.documents),
            'dimension': self.dimension,
            'index_type': self.index_type,
            'is_trained': self.is_trained,
            'index_exists': self.index is not None
        }
        
        if self.index is not None:
            stats['index_size'] = self.index.ntotal
            
            # Add index-specific stats
            if hasattr(self.index, 'nlist'):
                stats['nlist'] = self.index.nlist
            if hasattr(self.index, 'nprobe'):
                stats['nprobe'] = self.index.nprobe
        
        return stats
    
    def clear(self):
        """Clear the vector database"""
        logger.info("Clearing vector database")
        
        self.index = None
        self.documents = []
        self.is_trained = False
        
        logger.info("Vector database cleared")
    
    def rebuild_index(self) -> bool:
        """Rebuild the index from existing documents"""
        try:
            if not self.documents:
                logger.warning("No documents to rebuild index from")
                return False
            
            logger.info("Rebuilding vector database index...")
            
            # Extract documents and clear current index
            documents = self.documents.copy()
            self.clear()
            
            # Re-add all documents
            return self.add_documents(documents)
            
        except Exception as e:
            logger.error(f"Failed to rebuild index: {str(e)}")
            return False
    
    def get_document_by_id(self, vector_id: int) -> Optional[Dict[str, Any]]:
        """Get a document by its vector ID"""
        try:
            if 0 <= vector_id < len(self.documents):
                return self.documents[vector_id]
            return None
        except Exception as e:
            logger.error(f"Failed to get document by ID {vector_id}: {str(e)}")
            return None
    
    def remove_documents_by_source(self, source_file: str) -> bool:
        """Remove all documents from a specific source file"""
        try:
            logger.info(f"Removing documents from source: {source_file}")
            
            # Find documents to remove
            documents_to_keep = [doc for doc in self.documents if doc.get('source_file') != source_file]
            
            if len(documents_to_keep) == len(self.documents):
                logger.info("No documents found for the specified source")
                return True
            
            # Rebuild index with remaining documents
            self.clear()
            if documents_to_keep:
                return self.add_documents(documents_to_keep)
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to remove documents from source {source_file}: {str(e)}")
            return False

# Global vector database instance
vector_db = VectorDatabase()
