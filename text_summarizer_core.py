"""
Enhanced Text Summarization Core Module (Model)
Contains multiple summarization algorithms with SRT timestamp support.
"""

import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize, sent_tokenize
from collections import Counter
import heapq
import re
import math
from typing import List, Tuple, Dict, Optional, Any
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Download required NLTK data - FIXED: Removed manual resource finding
try:
    nltk.download('punkt_tab', quiet=True)
except:
    pass

try:
    nltk.download('stopwords', quiet=True)
except:
    pass

STOP_WORDS = set(stopwords.words('english'))

class TextSummarizer:
    """Enhanced text summarization class with multiple advanced algorithms."""

    def __init__(self):
        self.algorithms = {
            'weighted': self._summarize_weighted,
            'tfidf': self._summarize_tfidf,
            'keywords': self._summarize_keywords,
            'basic': self._summarize_basic,
            'textrank': self._summarize_textrank,
            'lexrank': self._summarize_lexrank,
            'centroid': self._summarize_centroid,
            'semantic': self._summarize_semantic_clustering
        }

    def summarize(self, text: str, method: str = 'weighted', n_sentences: int = 3,
                 srt_entries: Optional[List[Dict]] = None) -> str:
        """
        Main summarization method with optional SRT timestamp support.

        Args:
            text: Input text to summarize
            method: Algorithm to use
            n_sentences: Number of sentences in summary
            srt_entries: Optional SRT entries with timestamps

        Returns:
            Summarized text (with timestamps if SRT provided)
        """
        if not text.strip():
            return ""

        if method not in self.algorithms:
            method = 'weighted'

        # Get summary sentences
        summary_sentences = self.algorithms[method](text, n_sentences)

        # Add timestamps if SRT entries provided
        if srt_entries and summary_sentences:
            return self._add_timestamps_to_summary(summary_sentences, srt_entries)

        return summary_sentences

    def _add_timestamps_to_summary(self, summary: str, srt_entries: List[Dict]) -> str:
        """Add timestamps to summary sentences based on SRT entries."""
        summary_sentences = sent_tokenize(summary)
        timestamped_sentences = []

        for sentence in summary_sentences:
            # Find matching SRT entry for this sentence
            best_match = self._find_best_matching_srt_entry(sentence, srt_entries)
            if best_match:
                timestamp = f"[{best_match['start']} → {best_match['end']}]"
                timestamped_sentences.append(f"{timestamp} {sentence}")
            else:
                timestamped_sentences.append(sentence)

        return ' '.join(timestamped_sentences)

    def _find_best_matching_srt_entry(self, sentence: str, srt_entries: List[Dict]) -> Optional[Dict]:
        """Find the SRT entry that best matches a summary sentence."""
        best_match = None
        best_score = 0

        # Clean sentence for comparison
        sentence_words = set(word.lower() for word in word_tokenize(sentence) 
                           if word.isalnum())

        for entry in srt_entries:
            entry_words = set(word.lower() for word in word_tokenize(entry['text']) 
                            if word.isalnum())

            # Calculate word overlap
            if sentence_words and entry_words:
                overlap = len(sentence_words & entry_words)
                similarity = overlap / len(sentence_words)

                if similarity > best_score:
                    best_score = similarity
                    best_match = entry

        return best_match if best_score > 0.3 else None  # Threshold for matching

    def _filter_short_sentences(self, sentences: List[str], min_words: int = 6) -> List[str]:
        """Filter out very short sentences that are likely not informative."""
        return [s for s in sentences if len(s.split()) >= min_words]

    # Existing algorithms (weighted, tfidf, keywords, basic) remain the same
    def _summarize_weighted(self, text: str, n_sent: int = 3) -> str:
        """Multi-factor weighted summarization (position + frequency + length)."""
        sentences = sent_tokenize(text)
        filtered_sentences = [(i, s) for i, s in enumerate(sentences) if len(s.split()) >= 6]

        if len(filtered_sentences) <= n_sent:
            return ' '.join([s for _, s in filtered_sentences])

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

            # Position score
            if idx < total_sentences * 0.3:
                position_score = 1.0
            elif idx > total_sentences * 0.7:
                position_score = 0.8
            else:
                position_score = 0.6

            # Length score
            word_count = len(words)
            if 8 <= word_count <= 25:
                length_score = 1.0
            elif 6 <= word_count < 8:
                length_score = 0.7
            elif 26 <= word_count <= 35:
                length_score = 0.8
            else:
                length_score = 0.4

            sentence_scores[sentence] = (freq_score * 0.5 + 
                                       position_score * 0.3 + 
                                       length_score * 0.2)

        sentences_only = [s for _, s in filtered_sentences]
        return self._select_top_sentences(sentences_only, sentence_scores, n_sent)

    def _summarize_tfidf(self, text: str, n_sent: int = 3) -> str:
        """TF-IDF based extractive summarizer."""
        sentences = sent_tokenize(text)
        filtered_sentences = self._filter_short_sentences(sentences)

        if len(filtered_sentences) <= n_sent:
            return ' '.join(filtered_sentences)

        try:
            # Use sklearn's TfidfVectorizer for more robust TF-IDF
            vectorizer = TfidfVectorizer(stop_words='english', max_features=100)
            tfidf_matrix = vectorizer.fit_transform(filtered_sentences)

            # Score sentences by sum of TF-IDF values
            sentence_scores = {}
            for i, sentence in enumerate(filtered_sentences):
                score = np.sum(tfidf_matrix[i].toarray())
                sentence_scores[sentence] = score

            return self._select_top_sentences(filtered_sentences, sentence_scores, n_sent)

        except Exception:
            # Fallback to basic TF-IDF implementation
            return self._summarize_basic(text, n_sent)

    def _summarize_keywords(self, text: str, n_sent: int = 3) -> str:
        """Enhanced keyword density based summarization."""
        sentences = sent_tokenize(text)
        filtered_sentences = self._filter_short_sentences(sentences)

        if len(filtered_sentences) <= n_sent:
            return ' '.join(filtered_sentences)

        # Extract keywords using TF-IDF
        words = [w.lower() for w in word_tokenize(text) 
                if w.isalnum() and w.lower() not in STOP_WORDS and len(w) > 2]
        word_freq = Counter(words)

        # Get top 20% of words as keywords
        num_keywords = max(5, len(word_freq) // 5)
        keywords = set(word for word, _ in word_freq.most_common(num_keywords))

        sentence_scores = {}
        for sentence in filtered_sentences:
            words_in_sent = [w.lower() for w in word_tokenize(sentence) 
                            if w.isalnum() and w.lower() not in STOP_WORDS]

            if not words_in_sent:
                sentence_scores[sentence] = 0
                continue

            # Enhanced scoring: keyword frequency + rarity bonus
            keyword_score = 0
            for word in words_in_sent:
                if word in keywords:
                    # Give bonus for less common keywords
                    rarity_bonus = 1 / (word_freq[word] ** 0.5)
                    keyword_score += rarity_bonus

            sentence_scores[sentence] = keyword_score / len(words_in_sent)

        return self._select_top_sentences(filtered_sentences, sentence_scores, n_sent)

    def _summarize_basic(self, text: str, n_sent: int = 3) -> str:
        """Improved basic frequency-based summarization."""
        sentences = sent_tokenize(text)
        filtered_sentences = self._filter_short_sentences(sentences, min_words=8)

        if len(filtered_sentences) <= n_sent:
            return ' '.join(filtered_sentences)

        words = [w for w in word_tokenize(text.lower()) 
                if w.isalnum() and w not in STOP_WORDS]
        freq = Counter(words)

        scores = {}
        for sent in filtered_sentences:
            sent_words = [w for w in word_tokenize(sent.lower()) if w in freq]
            if sent_words:
                scores[sent] = max(freq[w] for w in sent_words)  # Use max instead of average
            else:
                scores[sent] = 0

        return self._select_top_sentences(filtered_sentences, scores, n_sent)

    # NEW ADVANCED ALGORITHMS

    def _summarize_textrank(self, text: str, n_sent: int = 3) -> str:
        """TextRank algorithm for extractive summarization."""
        sentences = sent_tokenize(text)
        filtered_sentences = self._filter_short_sentences(sentences)

        if len(filtered_sentences) <= n_sent:
            return ' '.join(filtered_sentences)

        try:
            # Create similarity matrix
            vectorizer = TfidfVectorizer(stop_words='english')
            tfidf_matrix = vectorizer.fit_transform(filtered_sentences)
            similarity_matrix = cosine_similarity(tfidf_matrix)

            # Apply PageRank algorithm
            scores = self._pagerank(similarity_matrix)

            # Create sentence scores dictionary
            sentence_scores = {sent: score for sent, score in zip(filtered_sentences, scores)}

            return self._select_top_sentences(filtered_sentences, sentence_scores, n_sent)

        except Exception:
            # Fallback to weighted algorithm
            return self._summarize_weighted(text, n_sent)

    def _summarize_lexrank(self, text: str, n_sent: int = 3) -> str:
        """LexRank algorithm - graph-based summarization."""
        sentences = sent_tokenize(text)
        filtered_sentences = self._filter_short_sentences(sentences)

        if len(filtered_sentences) <= n_sent:
            return ' '.join(filtered_sentences)

        try:
            # Calculate centrality scores
            vectorizer = TfidfVectorizer(stop_words='english')
            tfidf_matrix = vectorizer.fit_transform(filtered_sentences)
            similarity_matrix = cosine_similarity(tfidf_matrix)

            # LexRank scoring
            threshold = 0.1  # Similarity threshold
            adjacency_matrix = (similarity_matrix > threshold).astype(float)

            # Calculate degree centrality
            degrees = np.sum(adjacency_matrix, axis=1)
            scores = degrees / len(filtered_sentences)

            sentence_scores = {sent: score for sent, score in zip(filtered_sentences, scores)}

            return self._select_top_sentences(filtered_sentences, sentence_scores, n_sent)

        except Exception:
            return self._summarize_weighted(text, n_sent)

    def _summarize_centroid(self, text: str, n_sent: int = 3) -> str:
        """Centroid-based summarization."""
        sentences = sent_tokenize(text)
        filtered_sentences = self._filter_short_sentences(sentences)

        if len(filtered_sentences) <= n_sent:
            return ' '.join(filtered_sentences)

        try:
            vectorizer = TfidfVectorizer(stop_words='english')
            tfidf_matrix = vectorizer.fit_transform(filtered_sentences)

            # Calculate centroid vector
            centroid = np.mean(tfidf_matrix.toarray(), axis=0)

            # Score sentences by similarity to centroid
            sentence_scores = {}
            for i, sentence in enumerate(filtered_sentences):
                sentence_vector = tfidf_matrix[i].toarray()[0]
                similarity = cosine_similarity([sentence_vector], [centroid])[0][0]
                sentence_scores[sentence] = similarity

            return self._select_top_sentences(filtered_sentences, sentence_scores, n_sent)

        except Exception:
            return self._summarize_weighted(text, n_sent)

    def _summarize_semantic_clustering(self, text: str, n_sent: int = 3) -> str:
        """Semantic clustering-based summarization."""
        sentences = sent_tokenize(text)
        filtered_sentences = self._filter_short_sentences(sentences)

        if len(filtered_sentences) <= n_sent:
            return ' '.join(filtered_sentences)

        try:
            # Simple clustering approach
            vectorizer = TfidfVectorizer(stop_words='english', max_features=50)
            tfidf_matrix = vectorizer.fit_transform(filtered_sentences)

            # Group similar sentences and pick best from each group
            similarity_matrix = cosine_similarity(tfidf_matrix)

            # Greedy selection to maximize diversity
            selected_indices = []
            remaining_indices = list(range(len(filtered_sentences)))

            while len(selected_indices) < n_sent and remaining_indices:
                if not selected_indices:
                    # Pick sentence with highest TF-IDF sum
                    scores = np.sum(tfidf_matrix.toarray(), axis=1)
                    best_idx = remaining_indices[np.argmax([scores[i] for i in remaining_indices])]
                else:
                    # Pick sentence with lowest similarity to already selected
                    best_idx = None
                    min_max_similarity = float('inf')

                    for idx in remaining_indices:
                        max_similarity = max(similarity_matrix[idx][sel_idx] 
                                           for sel_idx in selected_indices)
                        if max_similarity < min_max_similarity:
                            min_max_similarity = max_similarity
                            best_idx = idx

                selected_indices.append(best_idx)
                remaining_indices.remove(best_idx)

            # Maintain original order
            selected_indices.sort()
            selected_sentences = [filtered_sentences[i] for i in selected_indices]

            return ' '.join(selected_sentences)

        except Exception:
            return self._summarize_weighted(text, n_sent)

    def _pagerank(self, similarity_matrix: np.ndarray, damping: float = 0.85, 
                  max_iter: int = 100, tol: float = 1e-4) -> np.ndarray:
        """Simple PageRank implementation."""
        n = similarity_matrix.shape[0]

        # Normalize similarity matrix
        row_sums = similarity_matrix.sum(axis=1)
        normalized_matrix = similarity_matrix / (row_sums[:, np.newaxis] + 1e-8)

        # Initialize scores
        scores = np.ones(n) / n

        for _ in range(max_iter):
            new_scores = (1 - damping) / n + damping * normalized_matrix.T.dot(scores)

            if np.linalg.norm(new_scores - scores) < tol:
                break

            scores = new_scores

        return scores

    def _select_top_sentences(self, sentences: List[str], scores: Dict[str, float], n_sent: int) -> str:
        """Select top N sentences while maintaining original order."""
        if not scores:
            return ' '.join(sentences[:n_sent])

        top_sentences = heapq.nlargest(n_sent, scores, key=scores.get)

        result = []
        for sentence in sentences:
            if sentence in top_sentences:
                result.append(sentence)

        return ' '.join(result)

    def get_available_methods(self) -> List[str]:
        """Return list of available summarization methods."""
        return list(self.algorithms.keys())

    # FIXED: Added the missing method that was causing the error
    def get_method_description(self, method: str) -> str:
        """Get description of summarization method."""
        descriptions = {
            'weighted': 'Multi-factor algorithm (position + frequency + length) - Best for general use',
            'tfidf': 'Term Frequency-Inverse Document Frequency with sklearn',
            'keywords': 'Enhanced keyword density with rarity bonuses',
            'basic': 'Improved frequency-based with max scoring',
            'textrank': 'Graph-based PageRank algorithm for sentence ranking',
            'lexrank': 'Centrality-based graph algorithm with similarity thresholding',
            'centroid': 'Vector space model using document centroid similarity',
            'semantic': 'Semantic clustering with diversity maximization'
        }
        return descriptions.get(method, 'Unknown algorithm')


class SRTParser:
    """Enhanced utility class for parsing SRT subtitle files with timestamp preservation."""

    @staticmethod
    def parse_srt_with_timestamps(srt_content: str) -> List[Dict[str, str]]:
        """
        Parse SRT content and return entries with timestamps.

        Returns:
            List of dictionaries with 'start', 'end', 'text', 'sequence' keys
        """
        entries = []
        lines = srt_content.strip().split('\n')

        i = 0
        while i < len(lines):
            # Skip empty lines
            while i < len(lines) and not lines[i].strip():
                i += 1
            if i >= len(lines):
                break

            # Read sequence number
            if not lines[i].strip().isdigit():
                i += 1
                continue

            sequence = lines[i].strip()
            i += 1

            if i >= len(lines):
                break

            # Read timestamp line
            timestamp_line = lines[i].strip()
            if '-->' not in timestamp_line:
                i += 1
                continue

            # Parse timestamps
            try:
                start_time, end_time = timestamp_line.split(' --> ')
                start_time = start_time.strip()
                end_time = end_time.strip()
            except ValueError:
                i += 1
                continue

            i += 1

            # Read text content
            text_lines = []
            while i < len(lines) and lines[i].strip() and not lines[i].strip().isdigit():
                clean_line = re.sub(r'<[^>]+>', '', lines[i].strip())
                if clean_line:
                    text_lines.append(clean_line)
                i += 1

            if text_lines:
                entries.append({
                    'start': start_time,
                    'end': end_time,
                    'text': ' '.join(text_lines),
                    'sequence': sequence
                })

        return entries

    @staticmethod
    def parse_srt_content(srt_content: str) -> str:
        """Parse SRT content and extract text (legacy method)."""
        entries = SRTParser.parse_srt_with_timestamps(srt_content)
        return ' '.join(entry['text'] for entry in entries)

    @staticmethod
    def is_srt_file(filename: str) -> bool:
        """Check if filename has .srt extension."""
        return filename.lower().endswith('.srt')


if __name__ == "__main__":
    # Test the enhanced summarizer
    sample_text = """
    This is a comprehensive test of the enhanced summarization system.
    The system now includes multiple advanced algorithms for better results.
    TextRank uses graph-based ranking similar to PageRank for web pages.
    LexRank employs centrality measures to find important sentences.
    Centroid-based methods compare sentences to the document's main theme.
    Semantic clustering ensures diversity in the selected sentences.
    All methods can now handle SRT files with timestamp preservation.
    """

    summarizer = TextSummarizer()
    print("Enhanced Summarizer Methods:", summarizer.get_available_methods())

    for method in ['weighted', 'textrank', 'semantic']:
        summary = summarizer.summarize(sample_text, method, 2)
        print(f"\n{method.upper()}: {summary}")
