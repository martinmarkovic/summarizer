"""
Application Entry Point - PHASE 4 FINAL

Clean entry point for the Enhanced AI Text & SRT Summarizer.
PHASE 4: Professional application launcher with error handling.
"""

import sys
import os
from pathlib import Path

# Add current directory to path for imports
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

def check_dependencies():
    """Check if all required dependencies are available."""
    missing_deps = []
    
    try:
        import tkinter
    except ImportError:
        missing_deps.append("tkinter")
    
    try:
        import nltk
    except ImportError:
        missing_deps.append("nltk")
    
    try:
        import numpy
    except ImportError:
        missing_deps.append("numpy")
    
    try:
        import sklearn
    except ImportError:
        missing_deps.append("scikit-learn")
    
    return missing_deps

def check_mvc_structure():
    """Check if MVC structure is properly set up."""
    required_dirs = ['controllers', 'models', 'views']
    missing_dirs = []
    
    for dir_name in required_dirs:
        if not os.path.exists(dir_name):
            missing_dirs.append(dir_name)
    
    required_files = [
        'controllers/__init__.py',
        'controllers/base_controller.py', 
        'controllers/file_controller.py',
        'controllers/summarizer_controller.py',
        'models/__init__.py',
        'models/text_summarizer.py',
        'models/srt_parser.py',
        'views/__init__.py',
        'views/summarizer_gui.py'
    ]
    
    missing_files = []
    for file_path in required_files:
        if not os.path.exists(file_path):
            missing_files.append(file_path)
    
    return missing_dirs, missing_files

def main():
    """Main application entry point with comprehensive error checking."""
    print("🤖 Enhanced AI Text & SRT Summarizer - Phase 4")
    print("=" * 60)
    
    # Check dependencies
    print("🔍 Checking dependencies...")
    missing_deps = check_dependencies()
    if missing_deps:
        print("❌ Missing required dependencies:")
        for dep in missing_deps:
            print(f"   • {dep}")
        print("\nInstall missing dependencies:")
        print("   pip install nltk numpy scikit-learn")
        return 1
    print("✅ All dependencies available")
    
    # Check MVC structure
    print("🔍 Checking MVC structure...")
    missing_dirs, missing_files = check_mvc_structure()
    
    if missing_dirs:
        print("❌ Missing required directories:")
        for dir_name in missing_dirs:
            print(f"   • {dir_name}/")
        return 1
    
    if missing_files:
        print("❌ Missing required files:")
        for file_path in missing_files:
            print(f"   • {file_path}")
        return 1
    
    print("✅ MVC structure complete")
    
    # Import and run application
    try:
        print("🚀 Starting application...")
        from text_summarizer_app import main as app_main
        app_main()
        return 0
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("\nPlease ensure all files are in the correct locations:")
        print("• text_summarizer_app.py in root directory")
        print("• All MVC components properly organized")
        return 1
        
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        print("\nTroubleshooting:")
        print("• Check Python version (3.7+ recommended)")
        print("• Verify all dependencies are installed")
        print("• Ensure NLTK data is downloaded")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)