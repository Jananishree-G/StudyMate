"""
Advanced search engine for StudyMate using TF-IDF with enhancements
"""

import re
import math
import string
from typing import List, Dict, Tuple, Set
from collections import Counter, defaultdict
from .config import config, logger

class AdvancedSearchEngine:
    """Enhanced TF-IDF based search engine with improved ranking"""

    def __init__(self):
        self.documents = []
        self.tf_idf_matrix = {}
        self.idf_scores = {}
        self.vocabulary = set()
        self.stop_words = self._get_stop_words()
        self.indexed = False
    
    def _get_stop_words(self) -> Set[str]:
        """Get common English stop words"""
        return {
            'a', 'an', 'and', 'are', 'as', 'at', 'be', 'by', 'for', 'from',
            'has', 'he', 'in', 'is', 'it', 'its', 'of', 'on', 'that', 'the',
            'to', 'was', 'will', 'with', 'the', 'this', 'but', 'they', 'have',
            'had', 'what', 'said', 'each', 'which', 'their', 'time', 'if',
            'up', 'out', 'many', 'then', 'them', 'these', 'so', 'some', 'her',
            'would', 'make', 'like', 'into', 'him', 'has', 'two', 'more',
            'very', 'after', 'words', 'long', 'than', 'first', 'been', 'call',
            'who', 'oil', 'sit', 'now', 'find', 'down', 'day', 'did', 'get',
            'come', 'made', 'may', 'part'
        }

    def preprocess_text(self, text: str) -> List[str]:
        """Enhanced text preprocessing with stop word removal"""
        if not text:
            return []

        # Convert to lowercase
        text = text.lower()

        # Remove punctuation and special characters
        text = re.sub(r'[^\w\s]', ' ', text)

        # Split into words
        words = text.split()

        # Filter words: remove stop words, short words, and numbers
        filtered_words = []
        for word in words:
            if (len(word) > 2 and
                word not in self.stop_words and
                not word.isdigit() and
                word.isalpha()):
                filtered_words.append(word)

        return filtered_words
    
    def calculate_tf(self, doc_tokens: List[str]) -> Dict[str, float]:
        """Calculate term frequency"""
        tf_scores = {}
        total_tokens = len(doc_tokens)
        
        if total_tokens == 0:
            return tf_scores
        
        token_counts = Counter(doc_tokens)
        
        for token, count in token_counts.items():
            tf_scores[token] = count / total_tokens
        
        return tf_scores
    
    def calculate_idf(self):
        """Calculate inverse document frequency"""
        total_docs = len(self.documents)
        
        if total_docs == 0:
            return
        
        # Count documents containing each term
        doc_freq = defaultdict(int)
        
        for doc in self.documents:
            unique_tokens = set(doc['tokens'])
            for token in unique_tokens:
                doc_freq[token] += 1
        
        # Calculate IDF scores
        for token, freq in doc_freq.items():
            self.idf_scores[token] = math.log(total_docs / freq)
    
    def build_index(self, chunks: List[Dict[str, any]]):
        """Build enhanced search index from document chunks"""
        logger.info(f"Building search index from {len(chunks)} chunks")

        self.documents = []
        self.tf_idf_matrix = {}
        self.vocabulary = set()

        if not chunks:
            logger.warning("No chunks provided for indexing")
            return

        # Process each chunk
        for i, chunk in enumerate(chunks):
            # Preprocess text
            tokens = self.preprocess_text(chunk['text'])

            if not tokens:  # Skip chunks with no valid tokens
                continue

            # Store document with enhanced metadata
            doc = {
                'id': i,
                'chunk_id': chunk['chunk_id'],
                'text': chunk['text'],
                'tokens': tokens,
                'source_file': chunk['source_file'],
                'chunk_index': chunk.get('chunk_index', i),
                'word_count': chunk.get('word_count', len(chunk['text'].split())),
                'char_count': chunk.get('char_count', len(chunk['text'])),
                'file_hash': chunk.get('file_hash', ''),
                'token_count': len(tokens)
            }

            self.documents.append(doc)
            self.vocabulary.update(tokens)

        if not self.documents:
            logger.error("No valid documents after preprocessing")
            return

        logger.info(f"Processed {len(self.documents)} documents with vocabulary of {len(self.vocabulary)} terms")

        # Calculate IDF scores
        self.calculate_idf()

        # Calculate TF-IDF for each document
        for doc in self.documents:
            tf_scores = self.calculate_tf(doc['tokens'])
            tfidf_scores = {}

            for token in self.vocabulary:
                tf = tf_scores.get(token, 0)
                idf = self.idf_scores.get(token, 0)
                tfidf_scores[token] = tf * idf

            self.tf_idf_matrix[doc['id']] = tfidf_scores

        self.indexed = True
        logger.info("Search index built successfully")
    
    def calculate_similarity(self, query_vector: Dict[str, float], doc_vector: Dict[str, float]) -> float:
        """Calculate cosine similarity between query and document"""
        # Calculate dot product
        dot_product = sum(query_vector.get(token, 0) * doc_vector.get(token, 0) 
                         for token in self.vocabulary)
        
        # Calculate magnitudes
        query_magnitude = math.sqrt(sum(score ** 2 for score in query_vector.values()))
        doc_magnitude = math.sqrt(sum(score ** 2 for score in doc_vector.values()))
        
        # Avoid division by zero
        if query_magnitude == 0 or doc_magnitude == 0:
            return 0
        
        return dot_product / (query_magnitude * doc_magnitude)
    
    def search(self, query: str, max_results: int = None) -> List[Dict[str, any]]:
        """Enhanced search with improved ranking and filtering"""
        if max_results is None:
            max_results = config.MAX_SEARCH_RESULTS

        if not self.indexed or not self.documents:
            logger.warning("Search index not built or empty")
            return []

        # Preprocess query
        query_tokens = self.preprocess_text(query)

        if not query_tokens:
            logger.warning("Query produced no valid tokens after preprocessing")
            return []

        logger.info(f"Searching for query: '{query}' with {len(query_tokens)} tokens")

        # Calculate query TF-IDF
        query_tf = self.calculate_tf(query_tokens)
        query_tfidf = {}

        for token in self.vocabulary:
            tf = query_tf.get(token, 0)
            idf = self.idf_scores.get(token, 0)
            query_tfidf[token] = tf * idf

        # Calculate similarities with enhanced scoring
        similarities = []

        for doc in self.documents:
            doc_tfidf = self.tf_idf_matrix[doc['id']]

            # Base cosine similarity
            base_similarity = self.calculate_similarity(query_tfidf, doc_tfidf)

            if base_similarity > config.MIN_SIMILARITY_SCORE:
                # Enhanced scoring with additional factors
                enhanced_score = self.calculate_enhanced_score(
                    query_tokens, doc, base_similarity
                )

                similarities.append({
                    'document': doc,
                    'similarity': base_similarity,
                    'enhanced_score': enhanced_score,
                    'matched_terms': self.count_matched_terms(query_tokens, doc['tokens'])
                })

        # Sort by enhanced score (descending)
        similarities.sort(key=lambda x: x['enhanced_score'], reverse=True)

        # Return top results with comprehensive metadata
        results = []
        for i, item in enumerate(similarities[:max_results]):
            doc = item['document']
            result = {
                'chunk_id': doc['chunk_id'],
                'text': doc['text'],
                'source_file': doc['source_file'],
                'chunk_index': doc['chunk_index'],
                'similarity_score': item['similarity'],
                'enhanced_score': item['enhanced_score'],
                'matched_terms': item['matched_terms'],
                'rank': i + 1,
                'word_count': doc['word_count'],
                'file_hash': doc.get('file_hash', ''),
                'relevance_explanation': self.explain_relevance(query_tokens, doc)
            }
            results.append(result)

        logger.info(f"Found {len(results)} relevant results for query")
        return results

    def calculate_enhanced_score(self, query_tokens: List[str], doc: Dict, base_score: float) -> float:
        """Calculate enhanced relevance score with multiple factors"""
        # Start with base TF-IDF similarity
        score = base_score

        # Boost for exact phrase matches
        query_text = ' '.join(query_tokens)
        if query_text.lower() in doc['text'].lower():
            score *= 1.5

        # Boost for term frequency in document
        doc_tokens = doc['tokens']
        matched_terms = sum(1 for token in query_tokens if token in doc_tokens)
        term_coverage = matched_terms / len(query_tokens) if query_tokens else 0
        score *= (1 + term_coverage)

        # Slight boost for shorter documents (more focused content)
        if doc['word_count'] < 200:
            score *= 1.1

        # Boost for documents with higher term density
        if doc['token_count'] > 0:
            term_density = matched_terms / doc['token_count']
            score *= (1 + term_density)

        return score

    def count_matched_terms(self, query_tokens: List[str], doc_tokens: List[str]) -> int:
        """Count how many query terms appear in the document"""
        doc_token_set = set(doc_tokens)
        return sum(1 for token in query_tokens if token in doc_token_set)

    def explain_relevance(self, query_tokens: List[str], doc: Dict) -> str:
        """Generate explanation for why this document is relevant"""
        doc_tokens = set(doc['tokens'])
        matched_terms = [token for token in query_tokens if token in doc_tokens]

        if not matched_terms:
            return "No direct term matches found"

        if len(matched_terms) == 1:
            return f"Contains term: {matched_terms[0]}"
        else:
            return f"Contains terms: {', '.join(matched_terms[:3])}" + \
                   (f" and {len(matched_terms)-3} more" if len(matched_terms) > 3 else "")
    
    def get_stats(self) -> Dict[str, any]:
        """Get comprehensive search engine statistics"""
        if not self.documents:
            return {
                'total_documents': 0,
                'vocabulary_size': 0,
                'indexed': False,
                'average_doc_length': 0,
                'total_tokens': 0
            }

        total_tokens = sum(doc['token_count'] for doc in self.documents)
        avg_doc_length = total_tokens / len(self.documents) if self.documents else 0

        return {
            'total_documents': len(self.documents),
            'vocabulary_size': len(self.vocabulary),
            'indexed': self.indexed,
            'average_doc_length': round(avg_doc_length, 2),
            'total_tokens': total_tokens,
            'unique_sources': len(set(doc['source_file'] for doc in self.documents)),
            'min_similarity_threshold': config.MIN_SIMILARITY_SCORE,
            'max_results_limit': config.MAX_SEARCH_RESULTS
        }

    def get_vocabulary_sample(self, limit: int = 20) -> List[str]:
        """Get a sample of the vocabulary for debugging"""
        return sorted(list(self.vocabulary))[:limit]

    def search_debug(self, query: str) -> Dict[str, any]:
        """Debug version of search with detailed information"""
        query_tokens = self.preprocess_text(query)

        debug_info = {
            'original_query': query,
            'processed_tokens': query_tokens,
            'tokens_in_vocabulary': [t for t in query_tokens if t in self.vocabulary],
            'tokens_not_found': [t for t in query_tokens if t not in self.vocabulary],
            'vocabulary_sample': self.get_vocabulary_sample()
        }

        return debug_info
