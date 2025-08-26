"""
Summarizer Controller Module

Handles summarization coordination and statistics calculation.
PHASE 3 - STEP 8: Business logic coordination moved from main controller.
"""

from typing import Dict, Any, Optional
from .base_controller import BaseController

class SummarizerController(BaseController):
    """Controller for summarization operations and statistics."""

    def __init__(self, summarizer, srt_parser):
        super().__init__()
        self.summarizer = summarizer
        self.srt_parser = srt_parser

    def coordinate_summarization(self, text: str, method: str, n_sentences: int, 
                                srt_entries: list = None, show_timestamps: bool = False) -> Dict[str, Any]:
        """
        Coordinate the complete summarization process.
        
        PHASE 3 - STEP 8: Moved from handle_summarization() in text_summarizer_app.py
        
        Args:
            text: Input text to summarize
            method: Algorithm to use
            n_sentences: Number of sentences in summary
            srt_entries: Optional SRT entries with timestamps
            show_timestamps: Whether to include timestamps in output
            
        Returns:
            Dict with 'success', 'summary', 'statistics', 'error' keys
        """
        try:
            # Validate inputs
            validation_result = self._validate_summarization_inputs(text, method, n_sentences)
            if not validation_result['valid']:
                return {
                    'success': False,
                    'summary': '',
                    'statistics': {},
                    'error': validation_result['error']
                }

            # Use validated parameters
            method = validation_result['method']
            n_sentences = validation_result['n_sentences']

            # Perform summarization
            if srt_entries and show_timestamps:
                summary = self.summarizer.summarize(text, method, n_sentences, srt_entries)
            else:
                summary = self.summarizer.summarize(text, method, n_sentences)

            if not summary.strip():
                return {
                    'success': False,
                    'summary': '',
                    'statistics': {},
                    'error': 'AI analysis produced no output. Text may be too short for summarization.'
                }

            # Calculate comprehensive statistics
            statistics = self.calculate_statistics(text, summary, method, show_timestamps, srt_entries)

            return {
                'success': True,
                'summary': summary,
                'statistics': statistics,
                'error': None
            }

        except Exception as e:
            return {
                'success': False,
                'summary': '',
                'statistics': {},
                'error': f'AI Summarization failed with {method.upper()} algorithm: {str(e)}'
            }

    def _validate_summarization_inputs(self, text: str, method: str, n_sentences: int) -> Dict[str, Any]:
        """
        Validate and sanitize summarization inputs.
        
        Returns:
            Dict with validation results and corrected values
        """
        # Validate text
        if not text or not text.strip():
            return {
                'valid': False,
                'error': 'No text provided for summarization'
            }

        # Validate method
        available_methods = self.summarizer.get_available_methods()
        if method not in available_methods:
            method = 'weighted'  # Fallback to default

        # Validate n_sentences
        if not isinstance(n_sentences, int) or not (1 <= n_sentences <= 15):
            n_sentences = 3  # Default value

        return {
            'valid': True,
            'method': method,
            'n_sentences': n_sentences,
            'text_length': len(text),
            'word_count': len(text.split())
        }

    def calculate_statistics(self, original_text: str, summary: str, 
                           method: str, has_timestamps: bool = False,
                           srt_entries: list = None) -> Dict[str, Any]:
        """
        Calculate comprehensive summarization statistics.
        
        PHASE 3 - STEP 11: Enhanced statistics calculation
        
        Args:
            original_text: Original input text
            summary: Generated summary
            method: Algorithm used
            has_timestamps: Whether timestamps were included
            srt_entries: Optional SRT entries for additional metrics
            
        Returns:
            Dict with comprehensive statistics
        """
        try:
            # Basic statistics
            original_words = len(original_text.split())
            summary_words = len(summary.split())
            original_chars = len(original_text)
            summary_chars = len(summary)
            
            # Calculate ratios
            compression_ratio = (summary_words / original_words) * 100 if original_words > 0 else 0
            char_compression_ratio = (summary_chars / original_chars) * 100 if original_chars > 0 else 0
            
            # Sentence counting
            original_sentences = len([s for s in original_text.split('.') if s.strip()])
            summary_sentences = len([s for s in summary.split('.') if s.strip()])
            
            # Base statistics dictionary
            stats = {
                'original_words': original_words,
                'summary_words': summary_words,
                'original_chars': original_chars,
                'summary_chars': summary_chars,
                'original_sentences': original_sentences,
                'summary_sentences': summary_sentences,
                'compression_ratio': round(compression_ratio, 1),
                'char_compression_ratio': round(char_compression_ratio, 1),
                'algorithm': method.upper(),
                'algorithm_category': self.get_algorithm_category(method),
                'has_timestamps': has_timestamps,
                'algorithm_description': self.summarizer.get_method_description(method)
            }
            
            # Add SRT-specific statistics
            if srt_entries:
                stats.update({
                    'subtitle_count': len(srt_entries),
                    'avg_subtitle_length': round(sum(len(entry['text'].split()) for entry in srt_entries) / len(srt_entries), 1),
                    'timestamp_coverage': self._calculate_timestamp_coverage(summary, srt_entries) if has_timestamps else 0
                })
            
            # Add efficiency metrics
            stats.update({
                'efficiency_score': self._calculate_efficiency_score(compression_ratio, original_words),
                'readability_estimate': self._estimate_readability(summary)
            })
            
            return stats
            
        except Exception as e:
            # Return minimal stats on error
            return {
                'original_words': len(original_text.split()) if original_text else 0,
                'summary_words': len(summary.split()) if summary else 0,
                'compression_ratio': 0,
                'algorithm': method.upper() if method else 'UNKNOWN',
                'error': f'Statistics calculation error: {str(e)}'
            }

    def _calculate_timestamp_coverage(self, summary: str, srt_entries: list) -> float:
        """Calculate what percentage of timeline is covered by summary."""
        try:
            if not summary or not srt_entries:
                return 0.0
            
            # Simple approximation - count how many SRT entries are represented
            summary_words = set(word.lower() for word in summary.split())
            matched_entries = 0
            
            for entry in srt_entries:
                entry_words = set(word.lower() for word in entry['text'].split())
                if len(summary_words & entry_words) > 0:
                    matched_entries += 1
            
            return round((matched_entries / len(srt_entries)) * 100, 1)
        except:
            return 0.0

    def _calculate_efficiency_score(self, compression_ratio: float, original_words: int) -> str:
        """Calculate efficiency score based on compression and content length."""
        try:
            if original_words < 100:
                return "Short Text"
            elif compression_ratio < 10:
                return "Highly Efficient"
            elif compression_ratio < 25:
                return "Efficient"
            elif compression_ratio < 40:
                return "Moderate"
            else:
                return "Low Compression"
        except:
            return "Unknown"

    def _estimate_readability(self, text: str) -> str:
        """Estimate readability level of summary."""
        try:
            if not text:
                return "Unknown"
            
            words = text.split()
            sentences = len([s for s in text.split('.') if s.strip()])
            avg_words_per_sentence = len(words) / sentences if sentences > 0 else 0
            
            if avg_words_per_sentence < 15:
                return "Easy"
            elif avg_words_per_sentence < 25:
                return "Moderate"
            else:
                return "Complex"
        except:
            return "Unknown"

    def get_algorithm_category(self, method: str) -> str:
        """
        Get algorithm category type.
        
        PHASE 3 - STEP 8: Moved from _get_algorithm_type() in main controller
        """
        algorithm_types = {
            'weighted': 'Multi-Factor',
            'textrank': 'Graph-Based',
            'semantic': 'Clustering',
            'tfidf': 'Statistical',
            'lexrank': 'Graph-Based',
            'centroid': 'Vector Space',
            'keywords': 'Frequency',
            'basic': 'Frequency'
        }
        return algorithm_types.get(method, 'Unknown')

    def get_available_methods(self) -> list:
        """Get list of available summarization methods."""
        return self.summarizer.get_available_methods()

    def get_method_description(self, method: str) -> str:
        """Get description of summarization method."""
        return self.summarizer.get_method_description(method)

    def validate_summarization_ready(self, text: str) -> Dict[str, Any]:
        """
        Validate if text is ready for summarization.
        
        Returns:
            Dict with validation status and recommendations
        """
        if not text or not text.strip():
            return {
                'ready': False,
                'reason': 'No text provided',
                'recommendation': 'Load a file or enter text manually'
            }

        word_count = len(text.split())
        sentence_count = len([s for s in text.split('.') if s.strip()])

        if word_count < 50:
            return {
                'ready': False,
                'reason': 'Text too short',
                'recommendation': f'Text has only {word_count} words. Summarization works best with 50+ words.'
            }

        if sentence_count < 3:
            return {
                'ready': False,
                'reason': 'Too few sentences',
                'recommendation': f'Text has only {sentence_count} sentences. Need at least 3 sentences for effective summarization.'
            }

        return {
            'ready': True,
            'word_count': word_count,
            'sentence_count': sentence_count,
            'recommendation': 'Text is ready for summarization'
        }