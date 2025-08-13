"""
Advanced Q&A engine for StudyMate
"""

from typing import List, Dict, Optional
from .search_engine import AdvancedSearchEngine
from .config import config, logger
import re

class AdvancedQAEngine:
    """Advanced question-answering engine with enhanced response generation"""

    def __init__(self):
        self.search_engine = AdvancedSearchEngine()
        self.conversation_history = []
        self.response_templates = self._load_response_templates()
    
    def _load_response_templates(self) -> Dict[str, str]:
        """Load response templates for different types of questions"""
        return {
            'no_results': "I couldn't find relevant information in your documents to answer this question. Try rephrasing your question or uploading more relevant materials.",
            'single_result': "Based on your document **{source}**, here's what I found:\n\n{content}",
            'multiple_results': "I found relevant information from {num_sources} sources in your documents:\n\n{content}",
            'low_confidence': "I found some potentially relevant information, but the match isn't very strong:\n\n{content}\n\n*Consider rephrasing your question for better results.*",
            'summary_intro': "Based on your uploaded documents, here's what I found:",
            'source_separator': "\n" + "─" * 60 + "\n"
        }

    def build_index(self, chunks: List[Dict[str, any]]):
        """Build search index from document chunks"""
        logger.info(f"Building Q&A index from {len(chunks)} chunks")
        self.search_engine.build_index(chunks)

    def _extract_key_sentences(self, text: str, query_terms: List[str], max_sentences: int = 3) -> str:
        """Extract the most relevant sentences from text based on query terms"""
        sentences = re.split(r'[.!?]+', text)
        scored_sentences = []

        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence) < 20:  # Skip very short sentences
                continue

            # Score sentence based on query term presence
            score = 0
            sentence_lower = sentence.lower()
            for term in query_terms:
                if term.lower() in sentence_lower:
                    score += 1

            if score > 0:
                scored_sentences.append((sentence, score))

        # Sort by score and return top sentences
        scored_sentences.sort(key=lambda x: x[1], reverse=True)
        top_sentences = [sent[0] for sent in scored_sentences[:max_sentences]]

        return '. '.join(top_sentences) + '.' if top_sentences else text[:300] + "..."

    def generate_answer(self, question: str, search_results: List[Dict[str, any]]) -> str:
        """Generate enhanced answer from search results"""
        if not search_results:
            return self.response_templates['no_results']

        # Analyze question type and results
        avg_confidence = sum(r['enhanced_score'] for r in search_results) / len(search_results)
        unique_sources = list(set(r['source_file'] for r in search_results))
        query_terms = self.search_engine.preprocess_text(question)

        # Generate appropriate response based on results
        if len(search_results) == 1:
            return self._generate_single_result_answer(search_results[0], query_terms)
        elif avg_confidence < 0.3:
            return self._generate_low_confidence_answer(search_results, query_terms)
        else:
            return self._generate_multi_result_answer(search_results, unique_sources, query_terms)

    def _generate_single_result_answer(self, result: Dict[str, any], query_terms: List[str]) -> str:
        """Generate answer for single result"""
        content = self._extract_key_sentences(result['text'], query_terms)

        return self.response_templates['single_result'].format(
            source=result['source_file'],
            content=content
        ) + f"\n\n*Relevance Score: {result['enhanced_score']:.2f}*"

    def _generate_low_confidence_answer(self, results: List[Dict[str, any]], query_terms: List[str]) -> str:
        """Generate answer for low confidence results"""
        content_parts = []

        for i, result in enumerate(results[:2], 1):
            content = self._extract_key_sentences(result['text'], query_terms, max_sentences=2)
            content_parts.append(f"**{i}. From {result['source_file']}:**\n{content}")

        content = self.response_templates['source_separator'].join(content_parts)

        return self.response_templates['low_confidence'].format(content=content)

    def _generate_multi_result_answer(self, results: List[Dict[str, any]], unique_sources: List[str], query_terms: List[str]) -> str:
        """Generate answer for multiple results"""
        content_parts = []

        # Group results by source for better organization
        source_results = {}
        for result in results[:5]:  # Limit to top 5 results
            source = result['source_file']
            if source not in source_results:
                source_results[source] = []
            source_results[source].append(result)

        # Generate content for each source
        for i, (source, source_results_list) in enumerate(source_results.items(), 1):
            best_result = max(source_results_list, key=lambda x: x['enhanced_score'])
            content = self._extract_key_sentences(best_result['text'], query_terms)

            content_parts.append(
                f"**{i}. From {source}** (Score: {best_result['enhanced_score']:.2f})\n{content}"
            )

        content = self.response_templates['source_separator'].join(content_parts)

        return self.response_templates['multiple_results'].format(
            num_sources=len(unique_sources),
            content=content
        ) + f"\n\n*Found {len(results)} relevant sections across {len(unique_sources)} documents.*"
    
    def ask_question(self, question: str) -> Dict[str, any]:
        """Process a question and return comprehensive answer with metadata"""
        try:
            logger.info(f"Processing question: {question[:100]}...")

            # Validate question
            if not question or len(question.strip()) < 3:
                return {
                    'answer': "Please provide a more specific question.",
                    'sources': [],
                    'confidence': 0.0,
                    'num_results': 0,
                    'error': False
                }

            # Search for relevant chunks
            search_results = self.search_engine.search(question)

            # Generate answer
            answer = self.generate_answer(question, search_results)

            # Calculate enhanced confidence
            confidence = self._calculate_confidence(search_results, question)

            # Prepare enhanced sources
            sources = self._prepare_sources(search_results)

            # Generate question insights
            insights = self._generate_insights(question, search_results)

            # Store in conversation history
            qa_pair = {
                'question': question,
                'answer': answer,
                'sources': sources,
                'confidence': confidence,
                'num_results': len(search_results),
                'insights': insights,
                'timestamp': self._get_timestamp()
            }

            self.conversation_history.append(qa_pair)

            # Keep only last 15 exchanges
            if len(self.conversation_history) > 15:
                self.conversation_history = self.conversation_history[-15:]

            logger.info(f"Generated answer with {len(search_results)} results, confidence: {confidence:.1f}%")

            return {
                'answer': answer,
                'sources': sources,
                'confidence': confidence,
                'num_results': len(search_results),
                'insights': insights,
                'error': False
            }

        except Exception as e:
            logger.error(f"Error processing question: {str(e)}")
            return {
                'answer': f"I encountered an error while processing your question: {str(e)}",
                'sources': [],
                'confidence': 0.0,
                'num_results': 0,
                'error': True
            }

    def _calculate_confidence(self, results: List[Dict[str, any]], question: str) -> float:
        """Calculate confidence score based on multiple factors"""
        if not results:
            return 0.0

        # Base confidence from search scores
        avg_enhanced_score = sum(r['enhanced_score'] for r in results) / len(results)
        base_confidence = min(avg_enhanced_score * 50, 100.0)  # Scale to 0-100

        # Boost for multiple results from different sources
        unique_sources = len(set(r['source_file'] for r in results))
        if unique_sources > 1:
            base_confidence *= 1.2

        # Boost for high number of matched terms
        if results:
            avg_matched_terms = sum(r.get('matched_terms', 0) for r in results) / len(results)
            query_terms = len(self.search_engine.preprocess_text(question))
            if query_terms > 0:
                term_coverage = avg_matched_terms / query_terms
                base_confidence *= (1 + term_coverage * 0.3)

        return min(base_confidence, 100.0)

    def _prepare_sources(self, results: List[Dict[str, any]]) -> List[Dict[str, any]]:
        """Prepare enhanced source information"""
        sources = []

        for result in results[:5]:  # Top 5 sources
            source = {
                'filename': result['source_file'],
                'similarity_score': result['similarity_score'],
                'enhanced_score': result['enhanced_score'],
                'matched_terms': result.get('matched_terms', 0),
                'relevance_explanation': result.get('relevance_explanation', ''),
                'text_preview': result['text'][:250] + "..." if len(result['text']) > 250 else result['text'],
                'word_count': result.get('word_count', 0),
                'chunk_index': result.get('chunk_index', 0)
            }
            sources.append(source)

        return sources

    def _generate_insights(self, question: str, results: List[Dict[str, any]]) -> Dict[str, any]:
        """Generate insights about the question and results"""
        if not results:
            return {'message': 'No relevant information found'}

        unique_sources = list(set(r['source_file'] for r in results))
        total_words = sum(r.get('word_count', 0) for r in results)

        insights = {
            'sources_searched': len(unique_sources),
            'total_content_words': total_words,
            'best_match_score': max(r['enhanced_score'] for r in results),
            'coverage_analysis': f"Found information across {len(unique_sources)} document(s)",
            'suggestion': self._generate_suggestion(question, results)
        }

        return insights

    def _generate_suggestion(self, question: str, results: List[Dict[str, any]]) -> str:
        """Generate helpful suggestions for the user"""
        if not results:
            return "Try using different keywords or upload more relevant documents."

        avg_score = sum(r['enhanced_score'] for r in results) / len(results)

        if avg_score < 0.3:
            return "Try rephrasing your question with more specific terms."
        elif len(results) == 1:
            return "Your question was very specific. Try broader terms to find more information."
        else:
            return "Great question! I found relevant information from multiple sources."

    def _get_timestamp(self) -> str:
        """Get current timestamp"""
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    def clear_conversation_history(self):
        """Clear conversation history"""
        logger.info("Clearing conversation history")
        self.conversation_history = []

    def get_conversation_history(self) -> List[Dict]:
        """Get conversation history"""
        return self.conversation_history.copy()

    def get_conversation_summary(self) -> Dict[str, any]:
        """Get summary of conversation history"""
        if not self.conversation_history:
            return {'total_questions': 0, 'avg_confidence': 0, 'topics': []}

        total_questions = len(self.conversation_history)
        avg_confidence = sum(qa['confidence'] for qa in self.conversation_history) / total_questions

        # Extract common topics (simplified)
        all_questions = ' '.join(qa['question'] for qa in self.conversation_history)
        common_words = self.search_engine.preprocess_text(all_questions)
        word_freq = {}
        for word in common_words:
            word_freq[word] = word_freq.get(word, 0) + 1

        topics = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:5]

        return {
            'total_questions': total_questions,
            'avg_confidence': round(avg_confidence, 1),
            'topics': [topic[0] for topic in topics],
            'recent_questions': [qa['question'] for qa in self.conversation_history[-3:]]
        }

    def get_stats(self) -> Dict[str, any]:
        """Get comprehensive Q&A engine statistics"""
        search_stats = self.search_engine.get_stats()
        conversation_summary = self.get_conversation_summary()

        return {
            'search_engine': search_stats,
            'conversation': conversation_summary,
            'ready': search_stats['indexed'],
            'total_questions_answered': len(self.conversation_history)
        }

    def suggest_questions(self, limit: int = 5) -> List[str]:
        """Suggest potential questions based on document content"""
        if not self.search_engine.indexed:
            return []

        # Get vocabulary sample for suggestions
        vocab_sample = self.search_engine.get_vocabulary_sample(50)

        # Generate question templates
        question_templates = [
            "What is {term}?",
            "How does {term} work?",
            "What are the benefits of {term}?",
            "Explain {term} in detail",
            "What is the purpose of {term}?"
        ]

        suggestions = []
        for term in vocab_sample[:limit]:
            if len(term) > 4:  # Only suggest longer, more meaningful terms
                template = question_templates[len(suggestions) % len(question_templates)]
                suggestions.append(template.format(term=term))

        return suggestions[:limit]
