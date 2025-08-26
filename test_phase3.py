"""
Phase 3 Validation Test Script

Quick test to validate all Phase 3 controllers work correctly.
Run this to verify the MVC architecture is functioning properly.
"""

import sys
import os

def test_controller_imports():
    """Test that all controllers import correctly."""
    print("🧪 Testing Controller Imports...")
    
    try:
        from controllers import BaseController, FileController, SummarizerController
        print("✅ All controllers imported successfully")
        return True
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

def test_controller_initialization():
    """Test that controllers initialize correctly."""
    print("🧪 Testing Controller Initialization...")
    
    try:
        from controllers import BaseController, FileController, SummarizerController
        from text_summarizer_core import TextSummarizer, SRTParser
        
        # Test BaseController
        base = BaseController()
        print("✅ BaseController initialized")
        
        # Test FileController  
        file_ctrl = FileController()
        print("✅ FileController initialized")
        
        # Test SummarizerController
        summarizer = TextSummarizer()
        srt_parser = SRTParser()
        summ_ctrl = SummarizerController(summarizer, srt_parser)
        print("✅ SummarizerController initialized")
        
        return True
    except Exception as e:
        print(f"❌ Initialization error: {e}")
        return False

def test_state_management():
    """Test BaseController state management."""
    print("🧪 Testing State Management...")
    
    try:
        from controllers import BaseController
        
        controller = BaseController()
        
        # Test initial state
        initial_state = controller.get_state()
        assert initial_state['current_file_path'] is None
        assert initial_state['original_text'] == ""
        print("✅ Initial state correct")
        
        # Test state update
        controller.update_file_state("test.txt", "test content", None, False)
        updated_state = controller.get_state()
        assert updated_state['current_file_path'] == "test.txt"
        assert updated_state['original_text'] == "test content"
        print("✅ State update working")
        
        # Test state validation
        validation = controller.validate_state()
        assert validation['has_file'] == True
        assert validation['has_content'] == True
        print("✅ State validation working")
        
        # Test state reset
        controller.reset_state()
        reset_state = controller.get_state()
        assert reset_state['current_file_path'] is None
        print("✅ State reset working")
        
        return True
    except Exception as e:
        print(f"❌ State management error: {e}")
        return False

def test_file_operations():
    """Test FileController operations."""
    print("🧪 Testing File Operations...")
    
    try:
        from controllers import FileController
        
        file_ctrl = FileController()
        
        # Test non-existent file
        result = file_ctrl.read_file_content("nonexistent_file.txt")
        assert result['success'] == False
        assert "not found" in result['error']
        print("✅ Non-existent file handling correct")
        
        # Test SRT validation with non-SRT file
        srt_result = file_ctrl.validate_srt_format("test.txt", "test content")
        assert srt_result['is_srt'] == False
        assert srt_result['text'] == "test content"
        print("✅ Non-SRT file validation correct")
        
        return True
    except Exception as e:
        print(f"❌ File operations error: {e}")
        return False

def test_summarization_logic():
    """Test SummarizerController logic."""
    print("🧪 Testing Summarization Logic...")
    
    try:
        from controllers import SummarizerController
        from text_summarizer_core import TextSummarizer, SRTParser
        
        summarizer = TextSummarizer()
        srt_parser = SRTParser()
        summ_ctrl = SummarizerController(summarizer, srt_parser)
        
        # Test input validation
        validation = summ_ctrl.validate_summarization_ready("")
        assert validation['ready'] == False
        print("✅ Empty text validation correct")
        
        validation = summ_ctrl.validate_summarization_ready("Short text.")
        assert validation['ready'] == False
        print("✅ Short text validation correct")
        
        # Test with adequate text
        long_text = "This is a comprehensive test of the enhanced summarization system. " * 10
        validation = summ_ctrl.validate_summarization_ready(long_text)
        assert validation['ready'] == True
        print("✅ Adequate text validation correct")
        
        # Test algorithm category
        category = summ_ctrl.get_algorithm_category('weighted')
        assert category == 'Multi-Factor'
        print("✅ Algorithm categorization correct")
        
        return True
    except Exception as e:
        print(f"❌ Summarization logic error: {e}")
        return False

def test_main_controller():
    """Test main controller initialization."""
    print("🧪 Testing Main Controller...")
    
    try:
        # Import without running the GUI
        sys.path.append('.')
        
        # Test app info structure
        from text_summarizer_app import EnhancedSummarizerController
        import tkinter as tk
        
        # This will create the GUI but we won't run mainloop
        app = EnhancedSummarizerController()
        
        info = app.get_app_info()
        assert info['phase'] == 'Phase 3 - Business Logic Extracted'
        assert 'controllers' in info
        assert len(info['controllers']) == 3
        print("✅ Main controller info correct")
        
        # Test system status
        status = app.get_system_status()
        assert 'controllers_initialized' in status
        print("✅ System status working")
        
        # Close the root window to clean up
        app.root.destroy()
        
        return True
    except Exception as e:
        print(f"❌ Main controller error: {e}")
        return False

def main():
    """Run all Phase 3 validation tests."""
    print("🚀 Phase 3 Validation Test Suite")
    print("=" * 50)
    
    tests = [
        test_controller_imports,
        test_controller_initialization,
        test_state_management,
        test_file_operations,
        test_summarization_logic,
        test_main_controller
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
            print()
        except Exception as e:
            print(f"❌ Test failed with exception: {e}")
            print()
    
    print("=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All Phase 3 tests passed! Architecture is working correctly!")
        print("✅ Ready for production use")
        print("🚀 Ready to proceed with Phase 4 when desired")
    else:
        print(f"⚠️ {total - passed} tests failed")
        print("🔍 Check the error messages above for details")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)