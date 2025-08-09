"""
Text Summarization Core Module (Model)
Contains all summarization algorithms and text processing logic.
"""

import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize, sent_tokenize
from collections import Counter
import heapq
import re
import math
from typing import List, Tuple, Dict, Optional


STOP_WORDS = set(stopwords.words('english'))

class TextSummarizer:
    """Core text summarization class with multiple algorithms."""

    def __init__(self):
        self.algorithms = {
            'tfidf': self._summarize_tfidf,
            'weighted': self._summarize_weighted,
            'keywords': self._summarize_keywords,
            'basic': self._summarize_basic
        }

    def summarize(self, text: str, method: str = 'weighted', n_sentences: int = 3) -> str:
        """
        Main summarization method.

        Args:
            text: Input text to summarize
            method: Algorithm to use ('tfidf', 'weighted', 'keywords', 'basic')
            n_sentences: Number of sentences in summary

        Returns:
            Summarized text
        """
        if not text.strip():
            return ""

        if method not in self.algorithms:
            method = 'weighted'

        return self.algorithms[method](text, n_sentences)

    def _filter_short_sentences(self, sentences: List[str], min_words: int = 6) -> List[str]:
        """Filter out very short sentences that are likely not informative."""
        return [s for s in sentences if len(s.split()) >= min_words]

    def _summarize_tfidf(self, text: str, n_sent: int = 3) -> str:
        """TF-IDF based extractive summarizer with length filtering."""
        sentences = sent_tokenize(text)
        filtered_sentences = self._filter_short_sentences(sentences)

        if len(filtered_sentences) <= n_sent:
            return ' '.join(filtered_sentences)

        # Calculate TF for each sentence
        sentence_word_counts = []

        for sentence in filtered_sentences:
            words = [w.lower() for w in word_tokenize(sentence) 
                    if w.isalnum() and w.lower() not in STOP_WORDS]
            sentence_word_counts.append(Counter(words))

        # Calculate IDF
        total_docs = len(filtered_sentences)
        word_doc_count = Counter()

        for word_count in sentence_word_counts:
            for word in word_count:
                word_doc_count[word] += 1

        # TF-IDF scores for sentences
        sentence_scores = {}
        for i, sentence in enumerate(filtered_sentences):
            score = 0
            word_count = sentence_word_counts[i]
            total_words = sum(word_count.values())

            if total_words == 0:
                sentence_scores[sentence] = 0
                continue

            for word, count in word_count.items():
                tf = count / total_words
                idf = math.log(total_docs / word_doc_count[word])
                score += tf * idf

            # Length normalization
            sentence_scores[sentence] = score / total_words

        return self._select_top_sentences(filtered_sentences, sentence_scores, n_sent)

    def _summarize_weighted(self, text: str, n_sent: int = 3) -> str:
        """Multi-factor weighted summarization (position + frequency + length)."""
        sentences = sent_tokenize(text)
        filtered_sentences = [(i, s) for i, s in enumerate(sentences) if len(s.split()) >= 6]

        if len(filtered_sentences) <= n_sent:
            return ' '.join([s for _, s in filtered_sentences])

        # Word frequency across entire text
        all_words = [w.lower() for w in word_tokenize(text) 
                    if w.isalnum() and w.lower() not in STOP_WORDS]
        word_freq = Counter(all_words)
        max_freq = max(word_freq.values()) if word_freq else 1

        sentence_scores = {}
        total_sentences = len(filtered_sentences)

        for idx, (original_idx, sentence) in enumerate(filtered_sentences):
            words = [w.lower() for w in word_tokenize(sentence) 
                    if w.isalnum() and w.lower() not in STOP_WORDS]

            if not words:
                sentence_scores[sentence] = 0
                continue

            # Frequency score (normalized)
            freq_score = sum(word_freq[word] for word in words) / (len(words) * max_freq)

            # Position score (higher for beginning and end)
            if idx < total_sentences * 0.3:  # First 30%
                position_score = 1.0
            elif idx > total_sentences * 0.7:  # Last 30%
                position_score = 0.8
            else:  # Middle
                position_score = 0.6

            # Length score (prefer moderate length sentences)
            word_count = len(words)
            if 8 <= word_count <= 25:  # Optimal range
                length_score = 1.0
            elif 6 <= word_count < 8:
                length_score = 0.7
            elif 26 <= word_count <= 35:
                length_score = 0.8
            else:
                length_score = 0.4

            # Combined weighted score
            sentence_scores[sentence] = (freq_score * 0.5 + 
                                       position_score * 0.3 + 
                                       length_score * 0.2)

        sentences_only = [s for _, s in filtered_sentences]
        return self._select_top_sentences(sentences_only, sentence_scores, n_sent)

    def _summarize_keywords(self, text: str, n_sent: int = 3) -> str:
        """Keyword density based summarization."""
        sentences = sent_tokenize(text)
        filtered_sentences = self._filter_short_sentences(sentences)

        if len(filtered_sentences) <= n_sent:
            return ' '.join(filtered_sentences)

        # Extract important keywords
        words = [w.lower() for w in word_tokenize(text) 
                if w.isalnum() and w.lower() not in STOP_WORDS]
        word_freq = Counter(words)

        # Get keywords that appear multiple times and are significant
        keywords = {word for word, freq in word_freq.items() if freq > 1}

        # Score sentences based on keyword density and frequency
        sentence_scores = {}
        for sentence in filtered_sentences:
            words_in_sent = [w.lower() for w in word_tokenize(sentence) 
                            if w.isalnum() and w.lower() not in STOP_WORDS]

            if not words_in_sent:
                sentence_scores[sentence] = 0
                continue

            # Keyword count weighted by frequency
            keyword_score = sum(word_freq[word] for word in words_in_sent if word in keywords)
            total_words = len(words_in_sent)

            # Normalized keyword density
            sentence_scores[sentence] = keyword_score / total_words

        return self._select_top_sentences(filtered_sentences, sentence_scores, n_sent)

    def _summarize_basic(self, text: str, n_sent: int = 3) -> str:
        """Improved version of basic frequency-based summarization."""
        sentences = sent_tokenize(text)
        filtered_sentences = self._filter_short_sentences(sentences, min_words=8)

        if len(filtered_sentences) <= n_sent:
            return ' '.join(filtered_sentences)

        # Word frequency
        words = [w for w in word_tokenize(text.lower()) 
                if w.isalnum() and w not in STOP_WORDS]
        freq = Counter(words)

        # Score sentences
        scores = {}
        for sent in filtered_sentences:
            sent_words = [w for w in word_tokenize(sent.lower()) if w in freq]
            if sent_words:
                # Use max frequency instead of average to avoid bias toward short sentences
                scores[sent] = max(freq[w] for w in sent_words)
            else:
                scores[sent] = 0

        return self._select_top_sentences(filtered_sentences, scores, n_sent)

    def _select_top_sentences(self, sentences: List[str], scores: Dict[str, float], n_sent: int) -> str:
        """Select top N sentences while maintaining original order."""
        if not scores:
            return ' '.join(sentences[:n_sent])

        top_sentences = heapq.nlargest(n_sent, scores, key=scores.get)

        # Maintain original order
        result = []
        for sentence in sentences:
            if sentence in top_sentences:
                result.append(sentence)

        return ' '.join(result)

    def get_available_methods(self) -> List[str]:
        """Return list of available summarization methods."""
        return list(self.algorithms.keys())


class SRTParser:
    """Utility class for parsing SRT subtitle files."""

    @staticmethod
    def parse_srt_content(srt_content: str) -> str:
        """
        Parse SRT content and extract text.

        Args:
            srt_content: Raw SRT file content

        Returns:
            Extracted text content
        """
        TIME_RE = re.compile(r'\d+:\d+:\d+,\d+\s+-->\s+\d+:\d+:\d+,\d+')

        lines = []
        for line in srt_content.splitlines():
            line = line.strip()
            # Skip sequence numbers, time codes, and empty lines
            if line.isdigit() or TIME_RE.match(line) or not line:
                continue
            # Remove HTML tags and add to content
            clean_line = re.sub(r'<[^>]+>', '', line)
            if clean_line.strip():
                lines.append(clean_line.strip())

        return ' '.join(lines)

    @staticmethod
    def is_srt_file(filename: str) -> bool:
        """Check if filename has .srt extension."""
        return filename.lower().endswith('.srt')


if __name__ == "__main__":
    # Test the summarizer
    sample_text = """
    This is a sample text for testing the summarization algorithms.
    The text contains multiple sentences with varying lengths.
    Some sentences are short. Others are much longer and contain more information.
    The summarizer should be able to identify the most important sentences.
    This final sentence wraps up the sample text for our testing purposes.
    """

    summarizer = TextSummarizer()
    print("Available methods:", summarizer.get_available_methods())
    print("\nWeighted summary:", summarizer.summarize(sample_text, 'weighted', 2))
