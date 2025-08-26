"""
Controllers Package - PHASE 3 COMPLETE

All controller classes with clean imports and dependencies.
PHASE 3: Complete MVC controller layer with business logic separation.
"""

from .base_controller import BaseController
from .file_controller import FileController  
from .summarizer_controller import SummarizerController

__all__ = [
    'BaseController',
    'FileController', 
    'SummarizerController'
]

# Version information
__version__ = '3.0.0'
__phase__ = 'Phase 3 - Business Logic Extracted'