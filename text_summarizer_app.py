"""
Text Summarizer Application Controller
Main application entry point that coordinates between Model and View.
"""

import tkinter as tk
from tkinter import messagebox
import os
import sys
from typing import Optional

# Import our modules
try:
    from text_summarizer_core import TextSummarizer, SRTParser
    from text_summarizer_gui import SummarizerGUI, configure_styles
except ImportError as e:
    print(f"Error importing modules: {e}")
    print("Make sure text_summarizer_core.py and text_summarizer_gui.py are in the same directory.")
    sys.exit(1)


class SummarizerController:
    """Main controller class that coordinates between GUI and core logic."""

    def __init__(self):
        # Initialize core components
        self.summarizer = TextSummarizer()
        self.srt_parser = SRTParser()

        # Initialize GUI
        self.root = tk.Tk()
        configure_styles()
        self.gui = SummarizerGUI(self.root)

        # Connect GUI callbacks to controller methods
        self._connect_callbacks()

        # Application state
        self.current_file_path: Optional[str] = None
        self.original_text: str = ""

        # Show welcome message
        self.gui.set_status("Welcome! Load a .txt or .srt file to get started.")

    def _connect_callbacks(self):
        """Connect GUI callbacks to controller methods."""
        self.gui.on_file_browse = self.handle_file_selection
        self.gui.on_summarize = self.handle_summarization
        self.gui.on_clear = self.handle_clear
        self.gui.on_method_change = self.handle_method_change

    def handle_file_selection(self, file_path: str):
        """Handle file selection from GUI."""
        try:
            self.gui.set_status("Loading file...")

            # Validate file exists
            if not os.path.exists(file_path):
                self.gui.show_error("File Error", f"File not found: {file_path}")
                return

            # Read file content
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    raw_content = f.read()
            except UnicodeDecodeError:
                # Try with different encoding
                try:
                    with open(file_path, 'r', encoding='latin-1') as f:
                        raw_content = f.read()
                except Exception as e:
                    self.gui.show_error("Encoding Error", 
                                      f"Could not read file with UTF-8 or Latin-1 encoding:\n{str(e)}")
                    return

            # Parse content based on file type
            if self.srt_parser.is_srt_file(file_path):
                self.original_text = self.srt_parser.parse_srt_content(raw_content)
                file_type = "SRT subtitle"
            else:
                self.original_text = raw_content
                file_type = "text"

            # Validate content
            if not self.original_text.strip():
                self.gui.show_error("Empty File", "The selected file appears to be empty or contains no readable text.")
                return

            # Update GUI
            self.current_file_path = file_path
            self.gui.set_file_path(os.path.basename(file_path))
            self.gui.display_original_text(self.original_text)

            # Show file info
            word_count = len(self.original_text.split())
            char_count = len(self.original_text)
            self.gui.set_status(f"Loaded {file_type} file: {word_count:,} words, {char_count:,} characters")

        except Exception as e:
            self.gui.show_error("File Loading Error", f"An error occurred while loading the file:\n{str(e)}")
            self.gui.set_status("Error loading file")

    def handle_summarization(self, text: str, method: str, n_sentences: int) -> str:
        """Handle summarization request from GUI."""
        try:
            # Validate inputs
            if not text.strip():
                raise ValueError("No text provided for summarization")

            if method not in self.summarizer.get_available_methods():
                method = 'weighted'  # Fall back to default

            if n_sentences < 1 or n_sentences > 10:
                n_sentences = 3  # Default value

            # Perform summarization
            summary = self.summarizer.summarize(text, method, n_sentences)

            if not summary.strip():
                raise ValueError("Summarization produced no output. Text may be too short or lack meaningful content.")

            # Calculate statistics
            original_words = len(text.split())
            summary_words = len(summary.split())
            compression_ratio = (summary_words / original_words) * 100 if original_words > 0 else 0

            # Update status
            self.gui.set_status(f"Summary completed • Method: {method.upper()} • "
                              f"Compression: {original_words:,} → {summary_words:,} words ({compression_ratio:.1f}%)")

            return summary

        except Exception as e:
            error_msg = f"Summarization failed: {str(e)}"
            self.gui.set_status("Summarization error")
            raise Exception(error_msg)

    def handle_clear(self):
        """Handle clear request from GUI."""
        try:
            # Reset application state
            self.current_file_path = None
            self.original_text = ""

            # Clear GUI
            self.gui.clear_all_text()

            self.gui.set_status("Ready for new file")

        except Exception as e:
            self.gui.show_error("Clear Error", f"An error occurred while clearing: {str(e)}")

    def handle_method_change(self, method: str):
        """Handle summarization method change."""
        try:
            # Validate method
            if method not in self.summarizer.get_available_methods():
                self.gui.set_status("Invalid summarization method selected")
                return

            # Update status with method info
            method_descriptions = {
                'weighted': 'Multi-factor algorithm combining position, frequency, and length scores',
                'tfidf': 'Term Frequency-Inverse Document Frequency with length filtering',
                'keywords': 'Keyword density-based sentence ranking',
                'basic': 'Improved frequency-based algorithm with short sentence filtering'
            }

            description = method_descriptions.get(method, 'Unknown algorithm')
            self.gui.set_status(f"Algorithm changed to {method.upper()}: {description}")

        except Exception as e:
            self.gui.show_error("Method Change Error", f"Error changing method: {str(e)}")

    def run(self):
        """Start the application."""
        try:
            self.gui.set_status("Application ready")
            self.root.mainloop()
        except Exception as e:
            print(f"Fatal error: {e}")
            sys.exit(1)

    def get_app_info(self) -> dict:
        """Get application information."""
        return {
            'name': 'Advanced Text & SRT Summarizer',
            'version': '2.0.0',
            'author': 'AI Assistant',
            'description': 'Multi-algorithm text summarization tool with SRT support',
            'algorithms': self.summarizer.get_available_methods(),
            'supported_formats': ['.txt', '.srt']
        }


def main():
    """Main application entry point."""
    try:
        # Create and run the application
        app = SummarizerController()

        # Print application info
        info = app.get_app_info()
        print(f"Starting {info['name']} v{info['version']}")
        print(f"Available algorithms: {', '.join(info['algorithms'])}")
        print(f"Supported formats: {', '.join(info['supported_formats'])}")
        print("-" * 50)

        # Run the application
        app.run()

    except KeyboardInterrupt:
        print("\nApplication terminated by user")
    except Exception as e:
        print(f"Fatal application error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
