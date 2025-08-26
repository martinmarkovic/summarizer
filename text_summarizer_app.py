"""
Enhanced Text Summarizer Application Controller - PHASE 4 FINAL

Advanced AI-powered summarization with complete professional MVC architecture.
PHASE 4: Final optimized version with models/views separation and clean dependencies.
"""

import tkinter as tk
import os
import sys
from typing import Optional

# PHASE 4: Import from properly organized packages
from controllers import BaseController, FileController, SummarizerController
from models import TextSummarizer, SRTParser  
from views import SummarizerGUI, configure_styles

class EnhancedSummarizerController(BaseController):
    """
    Enhanced controller with complete professional MVC architecture.
    
    PHASE 4 FINAL: Complete separation of concerns with optimized dependencies.
    - Models: Pure business logic (TextSummarizer, SRTParser)
    - Views: Pure GUI components (SummarizerGUI)
    - Controllers: Application flow and coordination
    """

    def __init__(self):
        # Initialize base controller with enhanced state management
        super().__init__()
        
        # Initialize all specialized controllers
        self.file_controller = FileController()
        self.summarizer_controller = SummarizerController()
        
        # Initialize enhanced GUI
        self.root = tk.Tk()
        configure_styles()
        self.gui = SummarizerGUI(self.root)

        # Set GUI references in all controllers
        self.set_gui(self.gui)
        self.file_controller.set_gui(self.gui)
        self.summarizer_controller.set_gui(self.gui)

        # Connect GUI callbacks
        self._connect_callbacks()

        # Show enhanced welcome message
        available_algorithms = len(self.summarizer_controller.get_available_methods())
        self.gui.set_status(f"🤖 AI Summarizer Ready • {available_algorithms} algorithms available • Load .txt or .srt files")

        print(f"🚀 Enhanced AI Summarizer Started - Phase 4 Complete")
        print(f"📊 Available Algorithms: {', '.join(self.summarizer_controller.get_available_methods())}")
        print(f"🏗️ MVC Architecture: Models, Views, Controllers fully separated")

    def _connect_callbacks(self):
        """Connect enhanced GUI callbacks."""
        self.gui.on_file_browse = self.handle_file_selection
        self.gui.on_summarize = self.handle_summarization
        self.gui.on_clear = self.handle_clear
        self.gui.on_method_change = self.handle_method_change

    def handle_file_selection(self, file_path: str):
        """
        Enhanced file selection - PHASE 4: Complete delegation to FileController.
        """
        try:
            self.gui.set_status("📂 Loading file with AI preprocessing...")

            # Use FileController's complete processing pipeline
            result = self.file_controller.process_file_completely(file_path)

            if not result['success']:
                self.handle_validation_error(Exception(result['error']), "file loading")
                return

            # Use BaseController's enhanced state management
            self.update_file_state(
                file_path=file_path,
                content=result['content'],
                srt_entries=result['srt_entries'],
                is_srt=result['is_srt']
            )

            # Validate content readiness
            if not self.original_text.strip():
                self.handle_validation_error(
                    Exception("The file appears to be empty or contains no readable text content."),
                    "content validation"
                )
                return

            # Update GUI
            self.gui.set_file_path(os.path.basename(file_path))
            self.gui.display_original_text(self.original_text)

            # Enhanced status with comprehensive file information
            content_info = self.get_content_info()
            encoding_info = f" ({result['encoding']} encoding)" if result['encoding'] else ""

            if self.is_srt_file:
                srt_stats = result.get('srt_statistics', {})
                subtitle_count = srt_stats.get('total_entries', len(self.srt_entries) if self.srt_entries else 0)
                duration = result.get('duration', '')
                
                self.gui.set_status(
                    f"✅ Loaded SRT subtitle: {subtitle_count} subtitles • "
                    f"{content_info['word_count']:,} words • {duration}{encoding_info}"
                )
            else:
                self.gui.set_status(
                    f"✅ Loaded text: {content_info['word_count']:,} words • "
                    f"{content_info['char_count']:,} characters • Ready for AI analysis{encoding_info}"
                )

        except Exception as e:
            self.handle_application_error(e, "file loading")

    def handle_summarization(self, text: str, method: str, n_sentences: int) -> str:
        """
        Enhanced summarization - PHASE 4: Complete delegation to SummarizerController.
        """
        try:
            # Validate readiness using SummarizerController
            readiness = self.summarizer_controller.validate_summarization_ready(text)
            if not readiness['ready']:
                raise ValueError(f"{readiness['reason']}: {readiness['recommendation']}")

            # Get user preferences
            _, _, show_timestamps = self.gui.get_summary_settings()
            
            # Use SummarizerController's complete coordination
            result = self.summarizer_controller.coordinate_summarization(
                text=text,
                method=method,
                n_sentences=n_sentences,
                srt_entries=self.srt_entries,
                show_timestamps=self.is_srt_file and show_timestamps
            )
            
            if not result['success']:
                raise Exception(result['error'])
            
            # Display enhanced statistics from SummarizerController
            stats = result['statistics']
            timestamp_info = " + Timestamps" if stats['has_timestamps'] else ""
            
            self.gui.set_status(
                f"🤖 {stats['algorithm']} Analysis Complete{timestamp_info} • "
                f"Compression: {stats['original_words']:,} → {stats['summary_words']:,} words "
                f"({stats['compression_ratio']:.1f}%) • {stats['efficiency_score']}"
            )
            
            return result['summary']
            
        except Exception as e:
            self.handle_processing_error(e, "AI summarization")
            raise Exception(str(e))

    def handle_clear(self):
        """
        Enhanced clear - PHASE 4: Uses BaseController's state management.
        """
        try:
            # Use BaseController's enhanced state reset
            self.reset_state()

            # Clear GUI
            self.gui.clear_all_text()

            available_algorithms = len(self.summarizer_controller.get_available_methods())
            self.gui.set_status(f"🗑️ Cleared • {available_algorithms} AI algorithms ready for new analysis")

        except Exception as e:
            self.handle_application_error(e, "clearing data")

    def handle_method_change(self, method: str):
        """
        Enhanced method change - PHASE 4: Uses SummarizerController for algorithm details.
        """
        try:
            # Validate using SummarizerController
            available_methods = self.summarizer_controller.get_available_methods()
            if method not in available_methods:
                self.gui.set_status("⚠️ Invalid algorithm selected")
                return

            # Get detailed info from SummarizerController
            description = self.summarizer_controller.get_method_description(method)
            algo_type = self.summarizer_controller.get_algorithm_category(method)
            
            self.gui.set_status(f"🔧 Algorithm: {method.upper()} ({algo_type}) • {description}")

        except Exception as e:
            self.handle_application_error(e, "changing algorithm")

    def run(self):
        """Start the enhanced application with Phase 4 architecture."""
        try:
            self.gui.set_status("🤖 Enhanced AI Summarizer Ready • Phase 4 Complete • Professional MVC Architecture")
            self.root.mainloop()
        except Exception as e:
            self.handle_application_error(e, "application runtime")
            sys.exit(1)

    def get_app_info(self) -> dict:
        """Get enhanced application information with Phase 4 details."""
        return {
            'name': 'Enhanced AI Text & SRT Summarizer',
            'version': '4.0.0',
            'phase': 'Phase 4 - Complete Professional MVC',
            'author': 'AI Assistant',
            'description': 'Advanced multi-algorithm summarization with professional MVC architecture',
            'architecture': 'Model-View-Controller (Complete Separation)',
            'algorithms': self.summarizer_controller.get_available_methods(),
            'supported_formats': ['.txt', '.srt'],
            'controllers': ['BaseController', 'FileController', 'SummarizerController'],
            'models': ['TextSummarizer', 'SRTParser'],
            'views': ['SummarizerGUI'],
            'features': [
                'Complete Professional MVC Architecture',
                'Optimized Dependencies & Performance',
                'Clean Model-View-Controller Separation', 
                'SRT Timestamp Preservation',
                'Multi-Algorithm AI Analysis',
                'Enhanced Error Handling',
                'Advanced State Management',
                'Comprehensive Statistics',
                'Export Functionality',
                'Professional Code Organization'
            ]
        }

    def get_system_status(self) -> dict:
        """Get current system status for debugging."""
        try:
            state_validation = self.validate_state()
            content_info = self.get_content_info()
            
            return {
                'phase': 'Phase 4 - Complete Professional MVC',
                'state_valid': all(state_validation.values()),
                'state_details': state_validation,
                'content_info': content_info,
                'mvc_components': {
                    'models': ['TextSummarizer', 'SRTParser'],
                    'views': ['SummarizerGUI'],
                    'controllers': ['BaseController', 'FileController', 'SummarizerController']
                },
                'controllers_initialized': {
                    'file_controller': self.file_controller is not None,
                    'summarizer_controller': self.summarizer_controller is not None,
                    'gui_connected': self.gui is not None
                },
                'algorithms_available': len(self.summarizer_controller.get_available_methods())
            }
        except Exception as e:
            return {
                'error': str(e),
                'state_valid': False,
                'phase': 'Phase 4 - Error in system status'
            }

def main():
    """Enhanced main application entry point with Phase 4 architecture."""
    try:
        print("🤖 Starting Enhanced AI Text & SRT Summarizer - Phase 4 Complete...")
        print("=" * 80)

        # Create enhanced application
        app = EnhancedSummarizerController()

        # Display enhanced info
        info = app.get_app_info()
        print(f"📱 {info['name']} v{info['version']}")
        print(f"🏗️ Architecture: {info['architecture']}")
        print(f"📊 Phase: {info['phase']}")
        print(f"🧠 AI Algorithms: {', '.join(info['algorithms'])}")
        print(f"📁 Supported Formats: {', '.join(info['supported_formats'])}")
        print(f"🎛️ Controllers: {', '.join(info['controllers'])}")
        print(f"🏢 Models: {', '.join(info['models'])}")
        print(f"🖥️ Views: {', '.join(info['views'])}")
        print(f"✨ Key Features:")
        for feature in info['features']:
            print(f"   • {feature}")
        print("=" * 80)
        print("🎉 Phase 4 Complete! Professional MVC architecture achieved!")
        print("🚀 Load a file to begin AI analysis with the cleanest codebase possible.")
        print()

        # Run enhanced application
        app.run()

    except KeyboardInterrupt:
        print("\n👋 Application terminated by user")
    except Exception as e:
        print(f"💥 Fatal application error: {e}")
        print("\nPhase 4 Architecture Status:")
        print("• Check that all MVC components are present:")
        print("  - models/ directory with TextSummarizer and SRTParser")
        print("  - views/ directory with SummarizerGUI")
        print("  - controllers/ directory with all controllers")
        print("• Verify Python dependencies are installed")
        print("• Ensure NLTK data is downloaded")
        sys.exit(1)

if __name__ == "__main__":
    main()