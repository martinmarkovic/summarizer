"""
SRT Parser Model

Pure parsing logic for SRT subtitle files with timestamp preservation.
PHASE 4: Extracted from text_summarizer_core.py - Pure model with no dependencies.
"""

import re
from typing import List, Dict

class SRTParser:
    """Pure utility class for parsing SRT subtitle files with timestamp preservation."""

    @staticmethod
    def parse_srt_with_timestamps(srt_content: str) -> List[Dict[str, str]]:
        """
        Parse SRT content and return entries with timestamps.
        
        Args:
            srt_content: Raw SRT file content
            
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

    @staticmethod
    def validate_srt_format(content: str) -> bool:
        """
        Validate if content follows SRT format.
        
        Args:
            content: Content to validate
            
        Returns:
            True if valid SRT format, False otherwise
        """
        try:
            entries = SRTParser.parse_srt_with_timestamps(content)
            return len(entries) > 0
        except:
            return False

    @staticmethod
    def get_srt_duration(entries: List[Dict[str, str]]) -> str:
        """
        Calculate total duration from SRT entries.
        
        Args:
            entries: List of SRT entries
            
        Returns:
            Duration string or empty if no entries
        """
        if not entries:
            return ""

        try:
            last_entry = entries[-1]
            end_time = last_entry['end']
            return f"Duration: {end_time}"
        except:
            return "Duration: Unknown"

    @staticmethod
    def get_srt_statistics(entries: List[Dict[str, str]]) -> Dict[str, any]:
        """
        Get comprehensive statistics from SRT entries.
        
        Args:
            entries: List of SRT entries
            
        Returns:
            Dictionary with statistics
        """
        if not entries:
            return {
                'total_entries': 0,
                'total_words': 0,
                'average_words_per_entry': 0,
                'duration': ''
            }

        total_words = sum(len(entry['text'].split()) for entry in entries)
        
        return {
            'total_entries': len(entries),
            'total_words': total_words,
            'average_words_per_entry': round(total_words / len(entries), 1),
            'duration': SRTParser.get_srt_duration(entries),
            'first_timestamp': entries[0]['start'] if entries else '',
            'last_timestamp': entries[-1]['end'] if entries else ''
        }