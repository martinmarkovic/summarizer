"""
Base Controller Module

Enhanced base controller with comprehensive error handling and state management.
PHASE 3: Enhanced with advanced error handling and state management methods.
"""

from typing import Optional, Dict, Any
import os

class BaseController:
    """Enhanced base controller class with comprehensive functionality."""

    def __init__(self):
        """Initialize base controller with enhanced state management."""
        # Application state
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

    # PHASE 3 - STEP 9: Enhanced Error Handling Methods
    def handle_application_error(self, error: Exception, context: str = ""):
        """Handle general application-level errors."""
        error_msg = f"Application error in {context}: {str(error)}"
        print(f"❌ {error_msg}")

        if self.gui:
            self.gui.show_error("Application Error", error_msg)
            self.gui.set_status(f"❌ Error in {context}")

    def handle_validation_error(self, error: Exception, context: str = "") -> None:
        """Handle input validation errors."""
        error_msg = f"Validation error in {context}: {str(error)}"
        print(f"⚠️ {error_msg}")
        
        if self.gui:
            self.gui.show_error("Validation Error", error_msg)
            self.gui.set_status(f"⚠️ Validation error in {context}")

    def handle_processing_error(self, error: Exception, operation: str = "") -> None:
        """Handle processing/algorithm errors."""
        error_msg = f"Processing failed in {operation}: {str(error)}"
        print(f"🔥 {error_msg}")
        
        if self.gui:
            self.gui.show_error("Processing Error", error_msg)
            self.gui.set_status(f"❌ Processing failed: {operation}")

    def log_application_state(self) -> None:
        """Log current application state for debugging."""
        state = self.get_state()
        print("📊 Application State:")
        for key, value in state.items():
            if isinstance(value, str) and len(value) > 100:
                print(f"   {key}: {value[:100]}... ({len(value)} chars)")
            else:
                print(f"   {key}: {value}")

    # PHASE 3 - STEP 10: Enhanced State Management Methods
    def update_file_state(self, file_path: str, content: str, 
                         srt_entries: list = None, is_srt: bool = False) -> None:
        """Update file-related state in one operation."""
        self.current_file_path = file_path
        self.original_text = content
        self.srt_entries = srt_entries
        self.is_srt_file = is_srt

    def validate_state(self) -> Dict[str, bool]:
        """Validate current application state."""
        return {
            'has_file': bool(self.current_file_path),
            'has_content': bool(self.original_text and self.original_text.strip()),
            'is_srt': self.is_srt_file,
            'has_srt_entries': bool(self.srt_entries),
            'ready_for_summarization': bool(self.original_text and self.original_text.strip())
        }

    def get_content_info(self) -> Dict[str, Any]:
        """Get information about loaded content."""
        if not self.original_text:
            return {'loaded': False}
        
        word_count = len(self.original_text.split())
        char_count = len(self.original_text)
        
        info = {
            'loaded': True,
            'word_count': word_count,
            'char_count': char_count,
            'file_type': 'SRT' if self.is_srt_file else 'Text',
            'file_name': os.path.basename(self.current_file_path) if self.current_file_path else ''
        }
        
        if self.is_srt_file and self.srt_entries:
            info['subtitle_count'] = len(self.srt_entries)
        
        return info

    def is_ready_for_operation(self, operation: str) -> bool:
        """Check if application state is ready for specific operation."""
        state = self.validate_state()
        
        if operation == 'summarization':
            return state['ready_for_summarization']
        elif operation == 'export':
            return state['has_content']
        elif operation == 'clear':
            return state['has_file'] or state['has_content']
        else:
            return True