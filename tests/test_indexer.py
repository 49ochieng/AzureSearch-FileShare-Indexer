"""
Unit tests for file indexer

Author: Edgar McOchieng
"""

import unittest
import os
import tempfile
from unittest.mock import Mock, patch, MagicMock
from src.indexer import FileIndexer


class TestFileIndexer(unittest.TestCase):
    """Test cases for FileIndexer class"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        """Clean up test fixtures"""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    @patch('src.indexer.SearchClient')
    @patch('src.indexer.Config')
    def test_indexer_initialization(self, mock_config, mock_search_client):
        """Test indexer initializes correctly"""
        mock_config.AZURE_SEARCH_ENDPOINT = "https://test.search.windows.net"
        mock_config.AZURE_SEARCH_KEY = "test-key"
        mock_config.AZURE_SEARCH_INDEX_NAME = "test-index"
        
        indexer = FileIndexer()
        
        self.assertIsNotNone(indexer.search_client)
        self.assertIsNotNone(indexer.extractor)
    
    @patch('src.indexer.SearchClient')
    @patch('src.indexer.Config')
    def test_should_index_file_size_check(self, mock_config, mock_search_client):
        """Test file size filtering"""
        mock_config.MAX_FILE_SIZE_MB = 1
        mock_config.INCREMENTAL_INDEXING = False
        
        indexer = FileIndexer()
        
        # Create large file (2 MB)
        large_file = os.path.join(self.temp_dir, "large.txt")
        with open(large_file, 'w') as f:
            f.write("x" * (2 * 1024 * 1024))
        
        # Should return False for file > 1MB
        result = indexer._should_index_file(large_file)
        self.assertFalse(result)
    
    @patch('src.indexer.SearchClient')
    @patch('src.indexer.Config')
    def test_generate_document_id(self, mock_config, mock_search_client):
        """Test document ID generation is consistent"""
        indexer = FileIndexer()
        
        file_path = "/path/to/test.txt"
        id1 = indexer._generate_document_id(file_path)
        id2 = indexer._generate_document_id(file_path)
        
        # Same file should produce same ID
        self.assertEqual(id1, id2)
        
        # Different file should produce different ID
        id3 = indexer._generate_document_id("/different/path.txt")
        self.assertNotEqual(id1, id3)
    
    @patch('src.indexer.SearchClient')
    @patch('src.indexer.Config')
    def test_prepare_document(self, mock_config, mock_search_client):
        """Test document preparation"""
        indexer = FileIndexer()
        
        # Create test file
        test_file = os.path.join(self.temp_dir, "test.txt")
        with open(test_file, 'w') as f:
            f.write("Test content for indexing.")
        
        # Prepare document
        doc = indexer._prepare_document(test_file)
        
        # Check required fields
        self.assertIsNotNone(doc)
        self.assertIn("id", doc)
        self.assertIn("content", doc)
        self.assertIn("title", doc)
        self.assertIn("name", doc)
        self.assertIn("filePath", doc)
        self.assertEqual(doc["name"], "test.txt")
    
    @patch('src.indexer.SearchClient')
    @patch('src.indexer.Config')
    def test_get_statistics(self, mock_config, mock_search_client):
        """Test statistics tracking"""
        indexer = FileIndexer()
        
        stats = indexer.get_statistics()
        
        # Check stats structure
        self.assertIn("total_files", stats)
        self.assertIn("successful", stats)
        self.assertIn("failed", stats)
        self.assertIn("skipped", stats)


class TestFileIndexerIntegration(unittest.TestCase):
    """Integration tests for file indexer"""
    
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        
        # Create test files
        self.test_files = []
        for i in range(3):
            file_path = os.path.join(self.temp_dir, f"test{i}.txt")
            with open(file_path, 'w') as f:
                f.write(f"Test content {i}")
            self.test_files.append(file_path)
    
    def tearDown(self):
        import shutil
        shutil.rmtree(self.temp_dir)
    
    @unittest.skip("Requires Azure credentials")
    def test_index_directory_integration(self):
        """Test indexing a directory (integration test)"""
        # This would require actual Azure credentials
        # Skip in unit tests, run separately in integration tests
        pass


if __name__ == '__main__':
    unittest.main()