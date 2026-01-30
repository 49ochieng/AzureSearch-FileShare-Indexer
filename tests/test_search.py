"""
Unit tests for search client

Author: Edgar McOchieng
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
from src.search import SearchClient


class TestSearchClient(unittest.TestCase):

        def test_format_results_empty(self):
            """Test format_results returns 'No results found.' for empty input"""
            search = SearchClient(use_vector_index=False)
            result = search.format_results([])
            self.assertEqual(result, "No results found.")
    """Test cases for SearchClient class"""
    
    @patch('src.search.AzureSearchClient')
    @patch('src.search.Config')
    def test_search_client_initialization(self, mock_config, mock_search_client):
        """Test search client initializes correctly"""
        mock_config.AZURE_SEARCH_ENDPOINT = "https://test.search.windows.net"
        mock_config.AZURE_SEARCH_KEY = "test-key"
        mock_config.AZURE_SEARCH_VECTOR_INDEX_NAME = "test-index"
        
        search = SearchClient(use_vector_index=False)
        
        self.assertIsNotNone(search.search_client)
    
    @patch('src.search.AzureSearchClient')
    @patch('src.search.AzureOpenAI')
    @patch('src.search.Config')
    def test_generate_query_embedding(self, mock_config, mock_openai, mock_search_client):
        """Test query embedding generation"""
        # Setup mocks
        mock_client = MagicMock()
        mock_openai.return_value = mock_client
        
        mock_response = MagicMock()
        mock_response.data = [MagicMock(embedding=[0.1] * 3072)]
        mock_client.embeddings.create.return_value = mock_response
        
        mock_config.AZURE_OPENAI_ENDPOINT = "https://test.openai.azure.com"
        mock_config.AZURE_OPENAI_KEY = "test-key"
        mock_config.AZURE_OPENAI_API_VERSION = "2024-05-01-preview"
        mock_config.AZURE_OPENAI_EMBEDDING_DEPLOYMENT = "test-deployment"
        
        search = SearchClient()
        search.vector_enabled = True
        search.openai_client = mock_client
        
        # Generate embedding
        embedding = search.generate_query_embedding("test query")
        
        # Verify
        self.assertIsNotNone(embedding)
        self.assertEqual(len(embedding), 3072)
    
    @patch('src.search.AzureSearchClient')
    @patch('src.search.Config')
    def test_format_results(self, mock_config, mock_search_client):
        """Test result formatting"""
        search = SearchClient(use_vector_index=False)
        
        # Mock results
        results = [
            {
                'name': 'test.pdf',
                'filePath': '/path/to/test.pdf',
                'extension': '.pdf',
                '@search.score': 0.85,
                'chunk': 'This is test content...'
            }
        ]
        
        formatted = search.format_results(results, show_scores=True)
        
        # Check formatting
        self.assertIn('test.pdf', formatted)
        self.assertIn('0.85', formatted)
    
    @patch('src.search.AzureSearchClient')
    @patch('src.search.Config')
    def test_format_empty_results(self, mock_config, mock_search_client):
        """Test formatting of empty results"""
        search = SearchClient(use_vector_index=False)
        
        formatted = search.format_results([])
        
        self.assertEqual(formatted, "No results found.")


if __name__ == '__main__':
    unittest.main()