"""
Controllers Package - PHASE 4 COMPLETE

All controller classes with optimized imports and dependencies.
PHASE 4: Final MVC controller layer with clean architecture.
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
__version__ = '4.0.0'
__phase__ = 'Phase 4 - Complete MVC Architecture'
__features__ = [
    'Optimized Dependencies',
    'Clean Model Separation', 
    'Enhanced Performance',
    'Professional Architecture'
]