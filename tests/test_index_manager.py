"""
Unit tests for index manager

Author: Edgar McOchieng
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
from src.index_manager import IndexManager


class TestIndexManager(unittest.TestCase):
    """Test cases for IndexManager class"""
    
    @patch('src.index_manager.Config')
    def test_index_manager_initialization(self, mock_config):
        """Test index manager initializes correctly"""
        mock_config.AZURE_SEARCH_ENDPOINT = "https://test.search.windows.net"
        mock_config.AZURE_SEARCH_KEY = "test-key"
        mock_config.AZURE_SEARCH_API_VERSION = "2023-11-01"
        
        manager = IndexManager()
        
        self.assertEqual(manager.endpoint, "https://test.search.windows.net")
        self.assertEqual(manager.api_key, "test-key")
    
    @patch('src.index_manager.requests.post')
    @patch('src.index_manager.Config')
    def test_create_standard_index_success(self, mock_config, mock_post):
        """Test successful standard index creation"""
        mock_config.AZURE_SEARCH_ENDPOINT = "https://test.search.windows.net"
        mock_config.AZURE_SEARCH_KEY = "test-key"
        mock_config.AZURE_SEARCH_API_VERSION = "2023-11-01"
        mock_config.AZURE_SEARCH_INDEX_NAME = "test-index"
        
        # Mock successful response
        mock_response = MagicMock()
        mock_response.status_code = 201
        mock_post.return_value = mock_response
        
        manager = IndexManager()
        result = manager.create_standard_index()
        
        self.assertTrue(result)
        mock_post.assert_called_once()
    
    @patch('src.index_manager.requests.post')
    @patch('src.index_manager.Config')
    def test_create_vector_index_success(self, mock_config, mock_post):
        """Test successful vector index creation"""
        mock_config.AZURE_SEARCH_ENDPOINT = "https://test.search.windows.net"
        mock_config.AZURE_SEARCH_KEY = "test-key"
        mock_config.AZURE_SEARCH_API_VERSION = "2023-11-01"
        mock_config.AZURE_SEARCH_VECTOR_INDEX_NAME = "test-vector-index"
        mock_config.EMBEDDING_DIMENSIONS = 3072
        
        # Mock successful response
        mock_response = MagicMock()
        mock_response.status_code = 201
        mock_post.return_value = mock_response
        
        manager = IndexManager()
        result = manager.create_vector_index()
        
        self.assertTrue(result)
        mock_post.assert_called_once()
    
    @patch('src.index_manager.requests.get')
    @patch('src.index_manager.Config')
    def test_list_indexes(self, mock_config, mock_get):
        """Test listing indexes"""
        mock_config.AZURE_SEARCH_ENDPOINT = "https://test.search.windows.net"
        mock_config.AZURE_SEARCH_KEY = "test-key"
        mock_config.AZURE_SEARCH_API_VERSION = "2023-11-01"
        
        # Mock response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'value': [
                {'name': 'index1'},
                {'name': 'index2'}
            ]
        }
        mock_get.return_value = mock_response
        
        manager = IndexManager()
        indexes = manager.list_indexes()
        
        self.assertEqual(len(indexes), 2)
        self.assertIn('index1', indexes)
        self.assertIn('index2', indexes)
    
    @patch('src.index_manager.requests.delete')
    @patch('src.index_manager.Config')
    def test_delete_index(self, mock_config, mock_delete):
        """Test index deletion"""
        mock_config.AZURE_SEARCH_ENDPOINT = "https://test.search.windows.net"
        mock_config.AZURE_SEARCH_KEY = "test-key"
        mock_config.AZURE_SEARCH_API_VERSION = "2023-11-01"
        
        # Mock successful deletion
        mock_response = MagicMock()
        mock_response.status_code = 204
        mock_delete.return_value = mock_response
        
        manager = IndexManager()
        result = manager.delete_index("test-index")
        
        self.assertTrue(result)
        mock_delete.assert_called_once()


if __name__ == '__main__':
    unittest.main()