"""
Index management utilities for creating and managing Azure AI Search indexes

Author: Edgar McOchieng
"""

import requests
from typing import Dict, Optional, List, Any
from config import Config
from config.logger import get_logger

logger = get_logger(__name__)


class IndexManager:
    """
    Manage Azure AI Search indexes
    
    Features:
    - Create standard text indexes
    - Create vector-enabled indexes
    - Update index schemas
    - Delete indexes
    - List all indexes
    """
    
    def __init__(self):
        """Initialize index manager"""
        self.endpoint = Config.AZURE_SEARCH_ENDPOINT
        self.api_key = Config.AZURE_SEARCH_KEY
        self.api_version = Config.AZURE_SEARCH_API_VERSION
        
        self.headers = {
            "Content-Type": "application/json",
            "api-key": self.api_key
        }
    
    def create_standard_index(self, index_name: Optional[str] = None) -> bool:
        """
        Create a standard text search index
        
        Args:
            index_name: Name of the index (defaults to config)
            
        Returns:
            True if successful, False otherwise
        """
        index_name = index_name or Config.AZURE_SEARCH_INDEX_NAME
        
        logger.info(f"Creating standard index: {index_name}")
        
        index_definition = {
            "name": index_name,
            "fields": [
                {"name": "id", "type": "Edm.String", "key": True, "searchable": False},
                {"name": "content", "type": "Edm.String", "searchable": True, "analyzer": "en.microsoft"},
                {"name": "title", "type": "Edm.String", "searchable": True, "filterable": True, "sortable": True},
                {"name": "name", "type": "Edm.String", "searchable": True, "filterable": True},
                {"name": "filePath", "type": "Edm.String", "searchable": True, "filterable": True},
                {"name": "extension", "type": "Edm.String", "filterable": True, "facetable": True},
                {"name": "size", "type": "Edm.Int64", "filterable": True, "sortable": True},
                {"name": "createdDateTime", "type": "Edm.DateTimeOffset", "filterable": True, "sortable": True},
                {"name": "modifiedDateTime", "type": "Edm.DateTimeOffset", "filterable": True, "sortable": True},
                {"name": "createdBy", "type": "Edm.String", "filterable": True, "facetable": True},
                {"name": "lastModifiedBy", "type": "Edm.String", "filterable": True, "facetable": True},
                {"name": "fileType", "type": "Edm.String", "filterable": True, "facetable": True},
                {"name": "url", "type": "Edm.String", "searchable": False}
            ]
        }
        
        url = f"{self.endpoint}/indexes?api-version={self.api_version}"
        
        try:
            response = requests.post(url, headers=self.headers, json=index_definition)
            
            if response.status_code in [200, 201]:
                logger.info(f"✅ Standard index '{index_name}' created successfully")
                return True
            elif response.status_code == 204:
                logger.info(f"ℹ️  Index '{index_name}' already exists")
                return True
            else:
                logger.error(f"Failed to create index: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Error creating index: {e}")
            return False
    
    def create_vector_index(
        self,
        index_name: Optional[str] = None,
        embedding_dimensions: Optional[int] = None
    ) -> bool:
        """
        Create a vector-enabled index with semantic configuration
        
        Args:
            index_name: Name of the index (defaults to config)
            embedding_dimensions: Vector dimensions (defaults to config)
            
        Returns:
            True if successful, False otherwise
        """
        index_name = index_name or Config.AZURE_SEARCH_VECTOR_INDEX_NAME
        embedding_dimensions = embedding_dimensions or Config.EMBEDDING_DIMENSIONS
        
        logger.info(f"Creating vector index: {index_name}")
        logger.info(f"Vector dimensions: {embedding_dimensions}")
        
        index_definition = {
            "name": index_name,
            "fields": [
                # Key field
                {"name": "id", "type": "Edm.String", "key": True, "searchable": False},
                
                # Content fields
                {"name": "content", "type": "Edm.String", "searchable": True, "analyzer": "en.microsoft"},
                {"name": "chunk", "type": "Edm.String", "searchable": True, "analyzer": "en.microsoft"},
                
                # Vector field
                {
                    "name": "contentVector",
                    "type": "Collection(Edm.Single)",
                    "searchable": True,
                    "dimensions": embedding_dimensions,
                    "vectorSearchProfile": "vector-profile"
                },
                
                # Metadata fields
                {"name": "title", "type": "Edm.String", "searchable": True, "filterable": True, "sortable": True},
                {"name": "name", "type": "Edm.String", "searchable": True, "filterable": True},
                {"name": "filePath", "type": "Edm.String", "searchable": True, "filterable": True},
                {"name": "extension", "type": "Edm.String", "filterable": True, "facetable": True},
                {"name": "size", "type": "Edm.Int64", "filterable": True, "sortable": True},
                {"name": "createdDateTime", "type": "Edm.DateTimeOffset", "filterable": True, "sortable": True},
                {"name": "modifiedDateTime", "type": "Edm.DateTimeOffset", "filterable": True, "sortable": True},
                {"name": "createdBy", "type": "Edm.String", "filterable": True, "facetable": True},
                {"name": "lastModifiedBy", "type": "Edm.String", "filterable": True, "facetable": True},
                {"name": "fileType", "type": "Edm.String", "filterable": True, "facetable": True},
                {"name": "url", "type": "Edm.String", "searchable": False},
                
                # Chunk metadata
                {"name": "chunkNumber", "type": "Edm.Int32", "filterable": True, "sortable": True},
                {"name": "totalChunks", "type": "Edm.Int32", "filterable": True}
            ],
            
            # Vector search configuration
            "vectorSearch": {
                "algorithms": [
                    {
                        "name": "hnsw-algorithm",
                        "kind": "hnsw",
                        "hnswParameters": {
                            "metric": "cosine",
                            "m": 4,
                            "efConstruction": 400,
                            "efSearch": 500
                        }
                    }
                ],
                "profiles": [
                    {
                        "name": "vector-profile",
                        "algorithm": "hnsw-algorithm"
                    }
                ]
            },
            
            # Semantic search configuration
            "semantic": {
                "configurations": [
                    {
                        "name": "semantic-config",
                        "prioritizedFields": {
                            "titleField": {"fieldName": "title"},
                            "prioritizedContentFields": [
                                {"fieldName": "chunk"},
                                {"fieldName": "content"}
                            ],
                            "prioritizedKeywordsFields": [
                                {"fieldName": "name"},
                                {"fieldName": "extension"}
                            ]
                        }
                    }
                ]
            }
        }
        
        url = f"{self.endpoint}/indexes?api-version={self.api_version}"
        
        try:
            response = requests.post(url, headers=self.headers, json=index_definition)
            
            if response.status_code in [200, 201]:
                logger.info(f"✅ Vector index '{index_name}' created successfully")
                logger.info("   - Text search: Enabled")
                logger.info("   - Vector search: Enabled (HNSW algorithm)")
                logger.info("   - Semantic ranking: Enabled")
                return True
            elif response.status_code == 204:
                logger.info(f"ℹ️  Index '{index_name}' already exists")
                return True
            else:
                logger.error(f"Failed to create index: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Error creating index: {e}")
            return False
    
    def delete_index(self, index_name: str) -> bool:
        """
        Delete an index
        
        Args:
            index_name: Name of the index to delete
            
        Returns:
            True if successful, False otherwise
        """
        logger.warning(f"Deleting index: {index_name}")
        
        url = f"{self.endpoint}/indexes/{index_name}?api-version={self.api_version}"
        
        try:
            response = requests.delete(url, headers=self.headers)
            
            if response.status_code in [200, 204]:
                logger.info(f"✅ Index '{index_name}' deleted successfully")
                return True
            elif response.status_code == 404:
                logger.warning(f"Index '{index_name}' not found")
                return False
            else:
                logger.error(f"Failed to delete index: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Error deleting index: {e}")
            return False
    
    def list_indexes(self) -> List[str]:
        """
        List all indexes in the search service
        
        Returns:
            List of index names
        """
        logger.info("Listing all indexes")
        
        url = f"{self.endpoint}/indexes?api-version={self.api_version}"
        
        try:
            response = requests.get(url, headers=self.headers)
            
            if response.status_code == 200:
                data = response.json()
                indexes = [idx['name'] for idx in data.get('value', [])]
                logger.info(f"Found {len(indexes)} indexes")
                return indexes
            else:
                logger.error(f"Failed to list indexes: {response.status_code}")
                return []
                
        except Exception as e:
            logger.error(f"Error listing indexes: {e}")
            return []
    
    def get_index_statistics(self, index_name: str) -> Optional[Dict[str, Any]]:
        """
        Get statistics for an index
        
        Args:
            index_name: Name of the index
            
        Returns:
            Dictionary with statistics or None if failed
        """
        logger.info(f"Getting statistics for index: {index_name}")
        
        url = f"{self.endpoint}/indexes/{index_name}/stats?api-version={self.api_version}"
        
        try:
            response = requests.get(url, headers=self.headers)
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Failed to get statistics: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"Error getting statistics: {e}")
            return None