"""
AzureSearch FileShare Indexer
=============================

Enterprise-grade document indexing for Azure AI Search with vector embeddings 
and semantic search capabilities.

Author: Edgar McOchieng
License: MIT
Version: 1.0.0

Main Components:
- FileIndexer: Standard text indexing
- VectorIndexer: Vector embeddings with chunking
- SearchClient: Advanced search capabilities
- ContentExtractor: Multi-format document processing

Quick Start:
    >>> from src import VectorIndexer
    >>> indexer = VectorIndexer()
    >>> indexer.index_directory("/path/to/documents")

For detailed documentation, see: docs/USAGE.md
"""

__version__ = "1.0.0"
__author__ = "Edgar McOchieng"
__license__ = "MIT"
__all__ = [
    "FileIndexer",
    "VectorIndexer",
    "SearchClient",
    "ContentExtractor",
    "IndexManager",
]

from .indexer import FileIndexer
from .vector_indexer import VectorIndexer
from .search import SearchClient
from .extractors import ContentExtractor
from .index_manager import IndexManager