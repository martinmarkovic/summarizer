"""
Complete MVC Test Suite - PHASE 4 FINAL

Comprehensive testing for the complete MVC architecture.
"""

import unittest
import sys
import os
from pathlib import Path

# Add current directory to path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

class TestMVCArchitecture(unittest.TestCase):
    """Test complete MVC architecture implementation."""
    
    def setUp(self):
        """Set up test environment."""
        try:
            from controllers import BaseController, FileController, SummarizerController
            from models import TextSummarizer, SRTParser
            
            self.base_controller = BaseController()
            self.file_controller = FileController()
            self.text_summarizer = TextSummarizer()
            self.srt_parser = SRTParser()
            self.summarizer_controller = SummarizerController()
            
        except ImportError as e:
            self.fail(f"Failed to import MVC components: {e}")

    def test_models_separation(self):
        """Test that models are properly separated."""
        # Test TextSummarizer
        self.assertTrue(hasattr(self.text_summarizer, 'summarize'))
        self.assertTrue(hasattr(self.text_summarizer, 'get_available_methods'))
        
        # Test SRTParser
        self.assertTrue(hasattr(self.srt_parser, 'parse_srt_with_timestamps'))
        self.assertTrue(hasattr(self.srt_parser, 'is_srt_file'))
        
        print("✅ Models properly separated")

    def test_controllers_initialization(self):
        """Test that all controllers initialize correctly."""
        self.assertIsNotNone(self.base_controller)
        self.assertIsNotNone(self.file_controller)
        self.assertIsNotNone(self.summarizer_controller)
        
        print("✅ All controllers initialize correctly")

    def test_state_management(self):
        """Test enhanced state management."""
        # Test initial state
        initial_state = self.base_controller.get_state()
        self.assertIsNone(initial_state['current_file_path'])
        self.assertEqual(initial_state['original_text'], "")
        
        # Test state update
        self.base_controller.update_file_state("test.txt", "test content", None, False)
        updated_state = self.base_controller.get_state()
        self.assertEqual(updated_state['current_file_path'], "test.txt")
        self.assertEqual(updated_state['original_text'], "test content")
        
        # Test state validation
        validation = self.base_controller.validate_state()
        self.assertTrue(validation['has_file'])
        self.assertTrue(validation['has_content'])
        
        print("✅ State management working correctly")

    def test_summarization_coordination(self):
        """Test summarization coordination."""
        test_text = """
        This is a comprehensive test of the enhanced summarization system.
        The system now includes multiple advanced algorithms for better results.
        TextRank uses graph-based ranking similar to PageRank for web pages.
        LexRank employs centrality measures to find important sentences.
        Centroid-based methods compare sentences to the document's main theme.
        Semantic clustering ensures diversity in the selected sentences.
        """
        
        # Test input validation
        validation = self.summarizer_controller.validate_summarization_ready(test_text)
        self.assertTrue(validation['ready'])
        
        # Test coordination
        result = self.summarizer_controller.coordinate_summarization(
            test_text, 'weighted', 3
        )
        self.assertTrue(result['success'])
        self.assertIn('summary', result)
        self.assertIn('statistics', result)
        
        print("✅ Summarization coordination working")

    def test_file_operations(self):
        """Test file operations."""
        # Test non-existent file
        result = self.file_controller.read_file_content("nonexistent_file.txt")
        self.assertFalse(result['success'])
        self.assertIn("not found", result['error'])
        
        # Test SRT validation
        srt_result = self.file_controller.validate_srt_format("test.txt", "test content")
        self.assertFalse(srt_result['is_srt'])
        self.assertEqual(srt_result['text'], "test content")
        
        print("✅ File operations working correctly")

    def test_algorithm_availability(self):
        """Test that all algorithms are available."""
        methods = self.text_summarizer.get_available_methods()
        expected_methods = ['weighted', 'tfidf', 'keywords', 'basic', 
                          'textrank', 'lexrank', 'centroid', 'semantic']
        
        for method in expected_methods:
            self.assertIn(method, methods)
        
        print(f"✅ All {len(methods)} algorithms available")

    def test_mvc_separation(self):
        """Test proper MVC separation of concerns."""
        # Models should not have GUI dependencies
        text_summarizer_dir = dir(self.text_summarizer)
        srt_parser_dir = dir(self.srt_parser)
        
        gui_related = ['tkinter', 'gui', 'widget', 'window', 'button']
        for item in text_summarizer_dir + srt_parser_dir:
            for gui_term in gui_related:
                self.assertNotIn(gui_term.lower(), item.lower())
        
        print("✅ MVC separation maintained - no GUI in models")

class TestPerformance(unittest.TestCase):
    """Test performance of the MVC architecture."""
    
    def test_import_speed(self):
        """Test that imports are fast."""
        import time
        
        start_time = time.time()
        from controllers import BaseController, FileController, SummarizerController
        from models import TextSummarizer, SRTParser
        end_time = time.time()
        
        import_time = end_time - start_time
        self.assertLess(import_time, 2.0, "Imports should be fast")
        
        print(f"✅ Import time: {import_time:.3f}s (within acceptable range)")

    def test_initialization_speed(self):
        """Test that initialization is fast."""
        import time
        
        start_time = time.time()
        from controllers import SummarizerController
        controller = SummarizerController()
        end_time = time.time()
        
        init_time = end_time - start_time
        self.assertLess(init_time, 3.0, "Initialization should be fast")
        
        print(f"✅ Initialization time: {init_time:.3f}s (within acceptable range)")

def run_comprehensive_tests():
    """Run all tests with detailed output."""
    print("🧪 Phase 4 MVC Architecture Test Suite")
    print("=" * 60)
    
    # Test MVC Architecture
    print("\n📋 Testing MVC Architecture...")
    suite1 = unittest.TestLoader().loadTestsFromTestCase(TestMVCArchitecture)
    runner = unittest.TextTestRunner(verbosity=0, stream=open(os.devnull, 'w'))
    result1 = runner.run(suite1)
    
    # Test Performance
    print("\n⚡ Testing Performance...")
    suite2 = unittest.TestLoader().loadTestsFromTestCase(TestPerformance)
    result2 = runner.run(suite2)
    
    # Summary
    total_tests = result1.testsRun + result2.testsRun
    total_failures = len(result1.failures) + len(result2.failures)
    total_errors = len(result1.errors) + len(result2.errors)
    
    print("\n" + "=" * 60)
    print(f"📊 Test Results: {total_tests - total_failures - total_errors}/{total_tests} tests passed")
    
    if total_failures == 0 and total_errors == 0:
        print("🎉 All Phase 4 tests passed! MVC architecture is working perfectly!")
        print("✅ Ready for production use")
        print("🏆 Professional software architecture achieved!")
        return True
    else:
        if total_failures > 0:
            print(f"❌ {total_failures} test failures")
        if total_errors > 0:
            print(f"💥 {total_errors} test errors")
        return False

if __name__ == "__main__":
    success = run_comprehensive_tests()
    sys.exit(0 if success else 1)