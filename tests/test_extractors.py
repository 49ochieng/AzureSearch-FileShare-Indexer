"""
Unit tests for content extractors

Author: Edgar McOchieng
"""

import unittest
import os
from pathlib import Path
import tempfile
from src.extractors import ContentExtractor, ExtractionError


class TestContentExtractor(unittest.TestCase):
    """Test cases for ContentExtractor class"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.extractor = ContentExtractor()
        self.temp_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        """Clean up test fixtures"""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_extract_text_from_txt(self):
        """Test text extraction from .txt file"""
        # Create test file
        test_file = os.path.join(self.temp_dir, "test.txt")
        test_content = "This is a test document."
        
        with open(test_file, 'w', encoding='utf-8') as f:
            f.write(test_content)
        
        # Extract
        content = self.extractor.extract_text(test_file)
        
        # Assert
        self.assertEqual(content, test_content)
    
    def test_extract_text_unsupported_format(self):
        """Test extraction fails for unsupported format"""
        test_file = os.path.join(self.temp_dir, "test.xyz")
        
        with open(test_file, 'w') as f:
            f.write("test")
        
        # Should raise ExtractionError
        with self.assertRaises(ExtractionError):
            self.extractor.extract_text(test_file)
    
    def test_extract_metadata(self):
        """Test metadata extraction"""
        test_file = os.path.join(self.temp_dir, "test.txt")
        
        with open(test_file, 'w') as f:
            f.write("test content")
        
        metadata = self.extractor.extract_metadata(test_file)
        
        # Check required fields
        self.assertIn("file_name", metadata)
        self.assertIn("file_path", metadata)
        self.assertIn("file_extension", metadata)
        self.assertIn("file_size_bytes", metadata)
        self.assertEqual(metadata["file_name"], "test.txt")
        self.assertEqual(metadata["file_extension"], ".txt")
    
    def test_get_statistics(self):
        """Test statistics tracking"""
        test_file = os.path.join(self.temp_dir, "test.txt")
        
        with open(test_file, 'w') as f:
            f.write("test")
        
        # Reset stats
        self.extractor.reset_statistics()
        
        # Extract
        self.extractor.extract_text(test_file)
        
        # Check stats
        stats = self.extractor.get_statistics()
        self.assertEqual(stats["total_extracted"], 1)
        self.assertEqual(stats["failed"], 0)
        self.assertEqual(stats["by_type"][".txt"], 1)
    
    def test_extract_text_encoding_handling(self):
        """Test handling of different text encodings"""
        test_file = os.path.join(self.temp_dir, "test_utf16.txt")
        test_content = "Special chars: é, ñ, ü"
        
        # Write with UTF-16 encoding
        with open(test_file, 'w', encoding='utf-16') as f:
            f.write(test_content)
        
        # Should handle encoding automatically
        content = self.extractor.extract_text(test_file)
        self.assertIsNotNone(content)


class TestContentExtractorIntegration(unittest.TestCase):
    """Integration tests for content extraction"""
    
    def setUp(self):
        self.extractor = ContentExtractor()
    
    @unittest.skipUnless(os.path.exists("test_files"), "Test files directory not found")
    def test_extract_real_pdf(self):
        """Test extraction from real PDF file"""
        pdf_path = "test_files/sample.pdf"
        if os.path.exists(pdf_path):
            content = self.extractor.extract_text(pdf_path)
            self.assertIsNotNone(content)
            self.assertGreater(len(content), 0)
    
    @unittest.skipUnless(os.path.exists("test_files"), "Test files directory not found")
    def test_extract_real_docx(self):
        """Test extraction from real DOCX file"""
        docx_path = "test_files/sample.docx"
        if os.path.exists(docx_path):
            content = self.extractor.extract_text(docx_path)
            self.assertIsNotNone(content)
            self.assertGreater(len(content), 0)


if __name__ == '__main__':
    unittest.main()