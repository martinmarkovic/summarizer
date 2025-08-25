"""

Enhanced Text Summarizer Application Controller

Advanced AI-powered summarization with SRT timestamp support.
REFACTORED - Step 3: Now uses FileController for file operations

"""

import tkinter as tk
from tkinter import messagebox
import os
import sys
from typing import Optional

# Import base controller - STEP 2 ADDITION
from controllers.base_controller import BaseController
# Import file controller - STEP 3 ADDITION
from controllers.file_controller import FileController

# Import our enhanced modules
try:
    from text_summarizer_core import TextSummarizer, SRTParser
    from text_summarizer_gui import SummarizerGUI, configure_styles
except ImportError as e:
    print(f"Error importing enhanced modules: {e}")
    print("Make sure text_summarizer_core.py and text_summarizer_gui.py are in the same directory.")
    sys.exit(1)

class EnhancedSummarizerController(BaseController):  # STEP 2 CHANGE: Inherit from BaseController
    """Enhanced controller with AI algorithms and SRT timestamp support."""

    def __init__(self):
        # STEP 2 ADDITION: Call parent constructor
        super().__init__()
        
        # STEP 3 ADDITION: Initialize file controller
        self.file_controller = FileController()
        
        # Initialize enhanced components
        self.summarizer = TextSummarizer()
        self.srt_parser = SRTParser()

        # Initialize enhanced GUI
        self.root = tk.Tk()
        configure_styles()
        self.gui = SummarizerGUI(self.root)

        # STEP 2 ADDITION: Set GUI reference in base controller
        self.set_gui(self.gui)

        # Connect GUI callbacks
        self._connect_callbacks()

        # STEP 2 REMOVAL: These state variables are now in BaseController
        # Removed: self.current_file_path: Optional[str] = None
        # Removed: self.original_text: str = ""
        # Removed: self.srt_entries: Optional[list] = None
        # Removed: self.is_srt_file: bool = False

        # Show enhanced welcome message
        available_algorithms = len(self.summarizer.get_available_methods())
        self.gui.set_status(f"🤖 AI Summarizer Ready • {available_algorithms} algorithms available • Load .txt or .srt files")

        print(f"🚀 Enhanced AI Summarizer Started")
        print(f"📊 Available Algorithms: {', '.join(self.summarizer.get_available_methods())}")

    def _connect_callbacks(self):
        """Connect enhanced GUI callbacks."""
        self.gui.on_file_browse = self.handle_file_selection
        self.gui.on_summarize = self.handle_summarization
        self.gui.on_clear = self.handle_clear
        self.gui.on_method_change = self.handle_method_change

    def handle_file_selection(self, file_path: str):
        """Enhanced file selection with SRT timestamp parsing - STEP 3 REFACTORED."""
        try:
            self.gui.set_status("📂 Loading file with AI preprocessing...")

            # STEP 3: Use FileController instead of inline file reading
            file_result = self.file_controller.read_file_content(file_path)

            if not file_result['success']:
                self.gui.show_error("File Error", file_result['error'])
                return

            raw_content = file_result['content']

            # Enhanced SRT processing with timestamp preservation
            self.is_srt_file = self.srt_parser.is_srt_file(file_path)

            if self.is_srt_file:
                # Parse SRT with timestamps
                self.srt_entries = self.srt_parser.parse_srt_with_timestamps(raw_content)
                self.original_text = ' '.join(entry['text'] for entry in self.srt_entries)
                file_type = "SRT subtitle"

                if not self.srt_entries:
                    self.gui.show_error("SRT Parse Error",
                        "Could not parse SRT file. Please check the format:\n\n" +
                        "Expected format:\n1\n00:00:00,000 --> 00:00:01,000\nText content")
                    return

                subtitle_count = len(self.srt_entries)
                total_duration = self._calculate_srt_duration()
            else:
                # Regular text file
                self.srt_entries = None
                self.original_text = raw_content
                file_type = "text"
                subtitle_count = 0
                total_duration = ""

            # Validate content
            if not self.original_text.strip():
                self.gui.show_error("Empty Content",
                    "The file appears to be empty or contains no readable text content.")
                return

            # Update GUI
            self.current_file_path = file_path
            self.gui.set_file_path(os.path.basename(file_path))
            self.gui.display_original_text(self.original_text)

            # Enhanced file info with encoding information from FileController
            word_count = len(self.original_text.split())
            char_count = len(self.original_text)
            encoding_info = f" ({file_result['encoding']} encoding)" if file_result['encoding'] else ""

            if self.is_srt_file:
                self.gui.set_status(f"✅ Loaded {file_type}: {subtitle_count} subtitles • {word_count:,} words • {total_duration}{encoding_info}")
            else:
                self.gui.set_status(f"✅ Loaded {file_type}: {word_count:,} words • {char_count:,} characters • Ready for AI analysis{encoding_info}")

        except Exception as e:
            # STEP 2 ENHANCEMENT: Use base controller error handling
            self.handle_application_error(e, "file loading")

    def handle_summarization(self, text: str, method: str, n_sentences: int) -> str:
        """Enhanced summarization with SRT timestamp support."""
        try:
            # Validate inputs
            if not text.strip():
                raise ValueError("No text provided for summarization")

            available_methods = self.summarizer.get_available_methods()
            if method not in available_methods:
                method = 'weighted'  # Fallback

            if not (1 <= n_sentences <= 15):
                n_sentences = 3

            # Get user preference for timestamps
            _, _, show_timestamps = self.gui.get_summary_settings()

            # Perform enhanced summarization
            if self.is_srt_file and self.srt_entries and show_timestamps:
                # Use SRT-aware summarization
                summary = self.summarizer.summarize(text, method, n_sentences, self.srt_entries)
            else:
                # Standard summarization
                summary = self.summarizer.summarize(text, method, n_sentences)

            if not summary.strip():
                raise ValueError("AI analysis produced no output. The text may be too short or lack sufficient content for meaningful summarization.")

            # Enhanced statistics
            original_words = len(text.split())
            summary_words = len(summary.split())
            compression_ratio = (summary_words / original_words) * 100 if original_words > 0 else 0

            # Get algorithm description
            algo_description = self.summarizer.get_method_description(method)

            # Update status with enhanced info
            timestamp_info = " + Timestamps" if (self.is_srt_file and show_timestamps) else ""
            self.gui.set_status(f"🤖 {method.upper()} Analysis Complete{timestamp_info} • " +
                f"Compression: {original_words:,} → {summary_words:,} words ({compression_ratio:.1f}%)")

            return summary

        except Exception as e:
            error_msg = f"AI Summarization failed with {method.upper()} algorithm:\n\n{str(e)}"
            self.gui.set_status("❌ AI processing error")
            raise Exception(error_msg)

    def handle_clear(self):
        """Enhanced clear with state reset."""
        try:
            # STEP 2 ENHANCEMENT: Use base controller reset method
            self.reset_state()

            # Clear GUI
            self.gui.clear_all_text()

            available_algorithms = len(self.summarizer.get_available_methods())
            self.gui.set_status(f"🗑️ Cleared • {available_algorithms} AI algorithms ready for new analysis")

        except Exception as e:
            # STEP 2 ENHANCEMENT: Use base controller error handling
            self.handle_application_error(e, "clearing data")

    def handle_method_change(self, method: str):
        """Enhanced method change with detailed feedback."""
        try:
            available_methods = self.summarizer.get_available_methods()
            if method not in available_methods:
                self.gui.set_status("⚠️ Invalid algorithm selected")
                return

            # Get detailed description
            description = self.summarizer.get_method_description(method)

            # Enhanced status with algorithm details
            algo_type = self._get_algorithm_type(method)
            self.gui.set_status(f"🔧 Algorithm: {method.upper()} ({algo_type}) • {description}")

        except Exception as e:
            # STEP 2 ENHANCEMENT: Use base controller error handling
            self.handle_application_error(e, "changing algorithm")

    def _get_algorithm_type(self, method: str) -> str:
        """Get algorithm category type."""
        algorithm_types = {
            'weighted': 'Multi-Factor',
            'textrank': 'Graph-Based',
            'semantic': 'Clustering',
            'tfidf': 'Statistical',
            'lexrank': 'Graph-Based',
            'centroid': 'Vector Space',
            'keywords': 'Frequency',
            'basic': 'Frequency'
        }
        return algorithm_types.get(method, 'Unknown')

    def _calculate_srt_duration(self) -> str:
        """Calculate total duration of SRT file."""
        if not self.srt_entries:
            return ""

        try:
            # Get last subtitle end time
            last_entry = self.srt_entries[-1]
            end_time = last_entry['end']

            # Convert to readable format
            return f"Duration: {end_time}"
        except:
            return "Duration: Unknown"

    def run(self):
        """Start the enhanced application."""
        try:
            self.gui.set_status("🤖 Enhanced AI Summarizer Ready • 8 algorithms • SRT support")
            self.root.mainloop()
        except Exception as e:
            print(f"Fatal application error: {e}")
            sys.exit(1)

    def get_app_info(self) -> dict:
        """Get enhanced application information."""
        return {
            'name': 'Enhanced AI Text & SRT Summarizer',
            'version': '2.5.0',
            'author': 'AI Assistant',
            'description': 'Advanced multi-algorithm summarization with SRT timestamp support',
            'algorithms': self.summarizer.get_available_methods(),
            'supported_formats': ['.txt', '.srt'],
            'features': [
                'SRT Timestamp Preservation',
                'Multi-Algorithm AI Analysis',
                'Export Functionality',
                'Real-time Statistics',
                'Enhanced Error Handling',
                'MVC Architecture'
            ]
        }

def main():
    """Enhanced main application entry point."""
    try:
        print("🤖 Starting Enhanced AI Text & SRT Summarizer...")
        print("=" * 60)

        # Create enhanced application
        app = EnhancedSummarizerController()

        # Display enhanced info
        info = app.get_app_info()
        print(f"📱 {info['name']} v{info['version']}")
        print(f"🧠 AI Algorithms: {', '.join(info['algorithms'])}")
        print(f"📁 Supported Formats: {', '.join(info['supported_formats'])}")
        print(f"✨ Key Features:")
        for feature in info['features']:
            print(f"   • {feature}")
        print("=" * 60)
        print("🚀 Application ready! Load a file to begin AI analysis.")
        print()

        # Run enhanced application
        app.run()

    except KeyboardInterrupt:
        print("\n👋 Application terminated by user")
    except Exception as e:
        print(f"💥 Fatal application error: {e}")
        print("\nPlease check:")
        print("• Python dependencies are installed")
        print("• NLTK data is downloaded")
        print("• All module files are present")
        sys.exit(1)

if __name__ == "__main__":
    main()