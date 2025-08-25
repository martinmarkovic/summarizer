"""
File Controller Module

Handles all file I/O operations for the Text Summarizer application.
STEP 3: First function migration - file reading logic moved here.
"""

import os
from typing import Dict, Any
from .base_controller import BaseController

class FileController(BaseController):
    """Controller for file operations."""

    def __init__(self):
        super().__init__()

    def read_file_content(self, file_path: str) -> Dict[str, Any]:
        """
        Read file content with encoding detection.
        
        STEP 3: Moved from handle_file_selection() in text_summarizer_app.py
        
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

    def get_file_info(self, file_path: str) -> Dict[str, Any]:
        """
        Get basic file information.
        
        Args:
            file_path: Path to file
            
        Returns:
            Dict with file information
        """
        try:
            if not os.path.exists(file_path):
                return {'exists': False, 'size': 0, 'name': ''}
                
            file_size = os.path.getsize(file_path)
            file_name = os.path.basename(file_path)
            
            return {
                'exists': True,
                'size': file_size,
                'name': file_name,
                'path': file_path
            }
        except Exception as e:
            return {
                'exists': False,
                'size': 0,
                'name': '',
                'error': str(e)
            }