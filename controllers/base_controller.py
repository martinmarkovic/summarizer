"""
Base Controller Module

Common functionality for all controllers in the Text Summarizer application.
"""

from typing import Optional, Dict, Any
import tkinter as tk

class BaseController:
    """Base controller class with common functionality."""

    def __init__(self):
        """Initialize base controller."""
        # Application state - moved from EnhancedSummarizerController
        self.current_file_path: Optional[str] = None
        self.original_text: str = ""
        self.srt_entries: Optional[list] = None
        self.is_srt_file: bool = False

        # GUI reference (will be set by main controller)
        self.gui = None

    def set_gui(self, gui):
        """Set GUI reference for controller."""
        self.gui = gui

    def reset_state(self):
        """Reset application state."""
        self.current_file_path = None
        self.original_text = ""
        self.srt_entries = None
        self.is_srt_file = False

    def get_state(self) -> Dict[str, Any]:
        """Get current application state."""
        return {
            'current_file_path': self.current_file_path,
            'original_text': self.original_text,
            'srt_entries': self.srt_entries,
            'is_srt_file': self.is_srt_file
        }

    def handle_application_error(self, error: Exception, context: str = ""):
        """Handle application-level errors."""
        error_msg = f"Application error in {context}: {str(error)}"
        print(f"❌ {error_msg}")

        if self.gui:
            self.gui.show_error("Application Error", error_msg)
            self.gui.set_status(f"❌ Error in {context}")