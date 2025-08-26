"""
Text Summarizer Model

Pure algorithm logic for text summarization with multiple advanced algorithms.
PHASE 4: Extracted from text_summarizer_core.py - Pure model with no dependencies.
"""

import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize, sent_tokenize
from collections import Counter
import heapq
import math
from typing import List, Dict, Optional
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Download required NLTK data
try:
    nltk.download('punkt_tab', quiet=True)
    nltk.download('stopwords', quiet=True)
except:
    pass

STOP_WORDS = set(stopwords.words('english'))

class TextSummarizer:
    """Pure text summarization model with multiple advanced algorithms."""

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

        return best_match if best_score > 0.3 else None

    def _filter_short_sentences(self, sentences: List[str], min_words: int = 6) -> List[str]:
        """Filter out very short sentences that are likely not informative."""
        return [s for s in sentences if len(s.split()) >= min_words]

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
            vectorizer = TfidfVectorizer(stop_words='english', max_features=100)
            tfidf_matrix = vectorizer.fit_transform(filtered_sentences)

            sentence_scores = {}
            for i, sentence in enumerate(filtered_sentences):
                score = np.sum(tfidf_matrix[i].toarray())
                sentence_scores[sentence] = score

            return self._select_top_sentences(filtered_sentences, sentence_scores, n_sent)

        except Exception:
            return self._summarize_basic(text, n_sent)

    def _summarize_keywords(self, text: str, n_sent: int = 3) -> str:
        """Enhanced keyword density based summarization."""
        sentences = sent_tokenize(text)
        filtered_sentences = self._filter_short_sentences(sentences)

        if len(filtered_sentences) <= n_sent:
            return ' '.join(filtered_sentences)

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

            keyword_score = 0
            for word in words_in_sent:
                if word in keywords:
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
                scores[sent] = max(freq[w] for w in sent_words)
            else:
                scores[sent] = 0

        return self._select_top_sentences(filtered_sentences, scores, n_sent)

    def _summarize_textrank(self, text: str, n_sent: int = 3) -> str:
        """TextRank algorithm for extractive summarization."""
        sentences = sent_tokenize(text)
        filtered_sentences = self._filter_short_sentences(sentences)

        if len(filtered_sentences) <= n_sent:
            return ' '.join(filtered_sentences)

        try:
            vectorizer = TfidfVectorizer(stop_words='english')
            tfidf_matrix = vectorizer.fit_transform(filtered_sentences)
            similarity_matrix = cosine_similarity(tfidf_matrix)

            scores = self._pagerank(similarity_matrix)
            sentence_scores = {sent: score for sent, score in zip(filtered_sentences, scores)}

            return self._select_top_sentences(filtered_sentences, sentence_scores, n_sent)

        except Exception:
            return self._summarize_weighted(text, n_sent)

    def _summarize_lexrank(self, text: str, n_sent: int = 3) -> str:
        """LexRank algorithm - graph-based summarization."""
        sentences = sent_tokenize(text)
        filtered_sentences = self._filter_short_sentences(sentences)

        if len(filtered_sentences) <= n_sent:
            return ' '.join(filtered_sentences)

        try:
            vectorizer = TfidfVectorizer(stop_words='english')
            tfidf_matrix = vectorizer.fit_transform(filtered_sentences)
            similarity_matrix = cosine_similarity(tfidf_matrix)

            threshold = 0.1
            adjacency_matrix = (similarity_matrix > threshold).astype(float)
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
            centroid = np.mean(tfidf_matrix.toarray(), axis=0)

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
            vectorizer = TfidfVectorizer(stop_words='english', max_features=50)
            tfidf_matrix = vectorizer.fit_transform(filtered_sentences)
            similarity_matrix = cosine_similarity(tfidf_matrix)

            # Greedy selection to maximize diversity
            selected_indices = []
            remaining_indices = list(range(len(filtered_sentences)))

            while len(selected_indices) < n_sent and remaining_indices:
                if not selected_indices:
                    scores = np.sum(tfidf_matrix.toarray(), axis=1)
                    best_idx = remaining_indices[np.argmax([scores[i] for i in remaining_indices])]
                else:
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