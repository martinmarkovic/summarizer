"""
Models Package - PHASE 4 COMPLETE

Pure model classes with no external dependencies.
PHASE 4: Complete separation of business logic from controllers.
"""

from .text_summarizer import TextSummarizer
from .srt_parser import SRTParser

__all__ = [
    'TextSummarizer',
    'SRTParser'
]

# Version information
__version__ = '4.0.0'
__phase__ = 'Phase 4 - Models Extracted & Optimized'