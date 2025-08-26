"""
File Controller Module

Handles all file I/O operations for the Text Summarizer application.
PHASE 3: Complete file operations controller with SRT support.
"""

import os
from typing import Dict, Any
from .base_controller import BaseController

class FileController(BaseController):
    """Controller for comprehensive file operations."""

    def __init__(self):
        super().__init__()

    def read_file_content(self, file_path: str) -> Dict[str, Any]:
        """
        Read file content with encoding detection.
        
        Args:
            file_path: Path to file to read
            
        Returns:
            Dict with 'success', 'content', 'encoding', 'error' keys
        """
        try:
            # Validate file exists
            if not os.path.exists(file_path):
                return {
                    'success': False,
                    'content': '',
                    'encoding': '',
                    'error': f'File not found: {file_path}'
                }

            # Try UTF-8 encoding first
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                return {
                    'success': True,
                    'content': content,
                    'encoding': 'utf-8',
                    'error': None
                }
            except UnicodeDecodeError:
                # Fallback to latin-1 encoding
                try:
                    with open(file_path, 'r', encoding='latin-1') as f:
                        content = f.read()
                    return {
                        'success': True,
                        'content': content,
                        'encoding': 'latin-1',
                        'error': None
                    }
                except Exception as e:
                    return {
                        'success': False,
                        'content': '',
                        'encoding': '',
                        'error': f'Could not read file. Try converting to UTF-8 encoding.\n\nError: {str(e)}'
                    }

        except Exception as e:
            return {
                'success': False,
                'content': '',
                'encoding': '',
                'error': f'Unexpected error reading file: {str(e)}'
            }

    def validate_srt_format(self, file_path: str, content: str) -> Dict[str, Any]:
        """
        Validate if file is SRT and parse if valid.
        
        Args:
            file_path: Path to file
            content: File content to validate/parse
            
        Returns:
            Dict with 'is_srt', 'entries', 'text', 'error' keys
        """
        try:
            # Check file extension
            is_srt_file = file_path.lower().endswith('.srt')

            if not is_srt_file:
                return {
                    'is_srt': False,
                    'entries': None,
                    'text': content,  # Return original content for .txt files
                    'error': None
                }

            # Parse SRT content (will move SRTParser to models in Phase 4)
            from text_summarizer_core import SRTParser
            parser = SRTParser()

            srt_entries = parser.parse_srt_with_timestamps(content)

            if not srt_entries:
                return {
                    'is_srt': True,
                    'entries': [],
                    'text': '',
                    'error': 'Could not parse SRT file. Please check the format:\n\n' +
                           'Expected format:\n1\n00:00:00,000 --> 00:00:01,000\nText content'
                }

            # Extract text from SRT entries
            extracted_text = ' '.join(entry['text'] for entry in srt_entries)

            return {
                'is_srt': True,
                'entries': srt_entries,
                'text': extracted_text,
                'error': None
            }

        except Exception as e:
            return {
                'is_srt': True,  # We know it's SRT by extension
                'entries': [],
                'text': '',
                'error': f'Error parsing SRT file: {str(e)}'
            }

    def calculate_srt_duration(self, srt_entries: list) -> str:
        """
        Calculate total duration of SRT file.
        
        Args:
            srt_entries: List of SRT entries with timestamps
            
        Returns:
            Duration string or empty if no entries
        """
        if not srt_entries:
            return ""

        try:
            # Get last subtitle end time
            last_entry = srt_entries[-1]
            end_time = last_entry['end']

            # Convert to readable format
            return f"Duration: {end_time}"
        except:
            return "Duration: Unknown"

    def get_file_info(self, file_path: str) -> Dict[str, Any]:
        """
        Get comprehensive file information.
        
        Args:
            file_path: Path to file
            
        Returns:
            Dict with file information
        """
        try:
            if not os.path.exists(file_path):
                return {'exists': False, 'size': 0, 'name': '', 'error': 'File not found'}
                
            file_size = os.path.getsize(file_path)
            file_name = os.path.basename(file_path)
            file_extension = os.path.splitext(file_path)[1].lower()
            
            return {
                'exists': True,
                'size': file_size,
                'name': file_name,
                'path': file_path,
                'extension': file_extension,
                'is_srt': file_extension == '.srt',
                'is_text': file_extension in ['.txt', '.md'],
                'size_mb': round(file_size / (1024 * 1024), 2) if file_size > 0 else 0
            }
        except Exception as e:
            return {
                'exists': False,
                'size': 0,
                'name': '',
                'error': str(e)
            }

    def process_file_completely(self, file_path: str) -> Dict[str, Any]:
        """
        Complete file processing pipeline.
        
        Args:
            file_path: Path to file to process
            
        Returns:
            Dict with complete file processing results
        """
        try:
            # Step 1: Get file info
            file_info = self.get_file_info(file_path)
            if not file_info['exists']:
                return {
                    'success': False,
                    'error': file_info.get('error', 'File does not exist'),
                    'file_info': file_info
                }

            # Step 2: Read file content
            file_result = self.read_file_content(file_path)
            if not file_result['success']:
                return {
                    'success': False,
                    'error': file_result['error'],
                    'file_info': file_info
                }

            # Step 3: Validate/parse SRT if applicable
            srt_result = self.validate_srt_format(file_path, file_result['content'])
            if srt_result['error']:
                return {
                    'success': False,
                    'error': srt_result['error'],
                    'file_info': file_info
                }

            # Step 4: Calculate additional metrics
            duration = ""
            if srt_result['is_srt'] and srt_result['entries']:
                duration = self.calculate_srt_duration(srt_result['entries'])

            return {
                'success': True,
                'file_info': file_info,
                'content': srt_result['text'],
                'encoding': file_result['encoding'],
                'is_srt': srt_result['is_srt'],
                'srt_entries': srt_result['entries'],
                'duration': duration,
                'error': None
            }

        except Exception as e:
            return {
                'success': False,
                'error': f'Complete file processing failed: {str(e)}',
                'file_info': {}
            }