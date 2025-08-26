"""
Views Package - PHASE 4 COMPLETE

Pure GUI components with no business logic.
PHASE 4: Views properly separated in MVC architecture.
"""

from .summarizer_gui import SummarizerGUI, configure_styles

__all__ = [
    'SummarizerGUI',
    'configure_styles'
]

# Version information
__version__ = '4.0.0'
__phase__ = 'Phase 4 - Views Properly Separated'