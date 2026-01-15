"""
Advanced search functionality for indexed documents
Supports keyword, vector, hybrid, and semantic search

Author: Edgar McOchieng
"""

from typing import List, Dict, Optional, Any
from azure.search.documents import SearchClient as AzureSearchClient
from azure.search.documents.models import VectorizedQuery, QueryType
from azure.core.credentials import AzureKeyCredential
from openai import AzureOpenAI

from config import Config
from config.logger import get_logger

logger = get_logger(__name__)


class SearchClient:
    """
    Advanced search client for file share index
    
    Features:
    - Keyword search
    - Vector similarity search
    - Hybrid search (keyword + vector)
    - Semantic search with reranking
    - Filtered search
    """
    
    def __init__(self, index_name: Optional[str] = None, use_vector_index: bool = True):
        """
        Initialize search client
        
        Args:
            index_name: Index to search (defaults to vector index if use_vector_index=True)
            use_vector_index: Whether to use vector-enabled index
        """
        if use_vector_index:
            self.index_name = index_name or Config.AZURE_SEARCH_VECTOR_INDEX_NAME
        else:
            self.index_name = index_name or Config.AZURE_SEARCH_INDEX_NAME
        
        logger.info(f"Initializing SearchClient for index: {self.index_name}")
        
        # Initialize search client
        self.search_client = AzureSearchClient(
            endpoint=Config.AZURE_SEARCH_ENDPOINT,
            index_name=self.index_name,
            credential=AzureKeyCredential(Config.AZURE_SEARCH_KEY)
        )
        
        # Initialize OpenAI for vector queries
        self.vector_enabled = False
        if use_vector_index:
            try:
                Config.validate(require_openai=True)
                self.openai_client = AzureOpenAI(
                    azure_endpoint=Config.AZURE_OPENAI_ENDPOINT,
                    api_key=Config.AZURE_OPENAI_KEY,
                    api_version=Config.AZURE_OPENAI_API_VERSION
                )
                self.vector_enabled = True
                logger.info("Vector search enabled")
            except Exception as e:
                logger.warning(f"Vector search not available: {e}")
    
    def generate_query_embedding(self, query: str) -> List[float]:
        """
        Generate embedding for search query
        
        Args:
            query: Search query text
            
        Returns:
            Embedding vector
            
        Raises:
            ValueError: If vector search not configured
        """
        if not self.vector_enabled:
            raise ValueError("Vector search not configured. Check OpenAI settings.")
        
        response = self.openai_client.embeddings.create(
            input=query,
            model=Config.AZURE_OPENAI_EMBEDDING_DEPLOYMENT
        )
        
        return response.data[0].embedding
    
    def search(
        self,
        query: str,
        top: Optional[int] = None,
        filter_expr: Optional[str] = None,
        select: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """
        Basic keyword search
        
        Args:
            query: Search query
            top: Number of results (defaults to config)
            filter_expr: OData filter expression
            select: Fields to return
            
        Returns:
            List of search results
        """
        top = top or Config.DEFAULT_TOP_K
        select = select or ["title", "chunk", "name", "filePath", "extension", "modifiedDateTime"]
        
        logger.info(f"Keyword search: '{query}' (top={top})")
        
        results = self.search_client.search(
            search_text=query,
            filter=filter_expr,
            top=top,
            select=select,
            query_type=QueryType.SIMPLE
        )
        
        results_list = list(results)
        logger.info(f"Found {len(results_list)} results")
        
        return results_list
    
    def vector_search(
        self,
        query: str,
        top: Optional[int] = None,
        filter_expr: Optional[str] = None,
        select: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """
        Pure vector similarity search
        
        Args:
            query: Search query
            top: Number of results
            filter_expr: OData filter expression
            select: Fields to return
            
        Returns:
            List of search results
        """
        if not self.vector_enabled:
            raise ValueError("Vector search not available. Use keyword search instead.")
        
        top = top or Config.DEFAULT_TOP_K
        select = select or ["title", "chunk", "name", "filePath", "chunkNumber", "modifiedDateTime"]
        
        logger.info(f"Vector search: '{query}' (top={top})")
        
        # Generate query embedding
        query_vector = self.generate_query_embedding(query)
        
        # Create vector query
        vector_query = VectorizedQuery(
            vector=query_vector,
            k_nearest_neighbors=top,
            fields="contentVector"
        )
        
        # Execute search
        results = self.search_client.search(
            search_text=None,
            vector_queries=[vector_query],
            filter=filter_expr,
            select=select,
            top=top
        )
        
        results_list = list(results)
        logger.info(f"Found {len(results_list)} results")
        
        return results_list
    
    def hybrid_search(
        self,
        query: str,
        top: Optional[int] = None,
        filter_expr: Optional[str] = None,
        select: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """
        Hybrid search combining keyword and vector search
        
        Args:
            query: Search query
            top: Number of results
            filter_expr: OData filter expression
            select: Fields to return
            
        Returns:
            List of search results
        """
        if not self.vector_enabled:
            logger.warning("Vector search not available. Falling back to keyword search.")
            return self.search(query, top, filter_expr, select)
        
        top = top or Config.DEFAULT_TOP_K
        select = select or ["title", "chunk", "name", "filePath", "extension", "chunkNumber", "modifiedDateTime"]
        
        logger.info(f"Hybrid search: '{query}' (top={top})")
        
        # Generate query embedding
        query_vector = self.generate_query_embedding(query)
        
        # Create vector query
        vector_query = VectorizedQuery(
            vector=query_vector,
            k_nearest_neighbors=50,  # Get more candidates for better hybrid results
            fields="contentVector"
        )
        
        # Execute hybrid search
        results = self.search_client.search(
            search_text=query,
            vector_queries=[vector_query],
            filter=filter_expr,
            select=select,
            top=top,
            query_type=QueryType.SIMPLE
        )
        
        results_list = list(results)
        logger.info(f"Found {len(results_list)} results")
        
        return results_list
    
    def semantic_search(
        self,
        query: str,
        top: Optional[int] = None,
        filter_expr: Optional[str] = None,
        select: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """
        Semantic search with intelligent reranking
        
        Requires Azure AI Search Basic tier or higher
        
        Args:
            query: Search query
            top: Number of results
            filter_expr: OData filter expression
            select: Fields to return
            
        Returns:
            List of search results with semantic scores
        """
        if not self.vector_enabled:
            logger.warning("Vector search not available. Falling back to keyword search.")
            return self.search(query, top, filter_expr, select)
        
        if not Config.ENABLE_SEMANTIC_RERANKING:
            logger.warning("Semantic reranking disabled. Using hybrid search instead.")
            return self.hybrid_search(query, top, filter_expr, select)
        
        top = top or Config.DEFAULT_TOP_K
        select = select or ["title", "chunk", "name", "filePath", "extension", "chunkNumber", "modifiedDateTime"]
        
        logger.info(f"Semantic search: '{query}' (top={top})")
        
        # Generate query embedding
        query_vector = self.generate_query_embedding(query)
        
        # Create vector query
        vector_query = VectorizedQuery(
            vector=query_vector,
            k_nearest_neighbors=50,
            fields="contentVector"
        )
        
        # Execute semantic search
        results = self.search_client.search(
            search_text=query,
            vector_queries=[vector_query],
            filter=filter_expr,
            select=select,
            top=top,
            query_type=QueryType.SEMANTIC,
            semantic_configuration_name="semantic-config",
            query_caption="extractive",
            query_answer="extractive"
        )
        
        results_list = list(results)
        logger.info(f"Found {len(results_list)} results")
        
        return results_list
    
    def filtered_search(
        self,
        query: str,
        extension: Optional[str] = None,
        date_from: Optional[str] = None,
        date_to: Optional[str] = None,
        author: Optional[str] = None,
        top: Optional[int] = None,
        search_type: str = "hybrid"
    ) -> List[Dict[str, Any]]:
        """
        Search with metadata filters
        
        Args:
            query: Search query
            extension: File extension filter (e.g., ".pdf")
            date_from: Modified date from (ISO format)
            date_to: Modified date to (ISO format)
            author: Author filter
            top: Number of results
            search_type: Type of search ("keyword", "vector", "hybrid", "semantic")
            
        Returns:
            List of filtered search results
        """
        # Build filter expression
        filters = []
        
        if extension:
            filters.append(f"extension eq '{extension}'")
        
        if date_from:
            filters.append(f"modifiedDateTime ge {date_from}")
        
        if date_to:
            filters.append(f"modifiedDateTime le {date_to}")
        
        if author:
            filters.append(f"search.in(createdBy, '{author}', ',')")
        
        filter_expr = " and ".join(filters) if filters else None
        
        logger.info(f"Filtered search: query='{query}', filters='{filter_expr}'")
        
        # Execute appropriate search type
        search_methods = {
            "keyword": self.search,
            "vector": self.vector_search,
            "hybrid": self.hybrid_search,
            "semantic": self.semantic_search
        }
        
        search_method = search_methods.get(search_type, self.hybrid_search)
        return search_method(query, top, filter_expr)
    
    def format_results(self, results: List[Dict[str, Any]], show_scores: bool = True) -> str:
        """
        Format search results for display
        
        Args:
            results: List of search results
            show_scores: Whether to show relevance scores
            
        Returns:
            Formatted string
        """
        if not results:
            return "No results found."
        
        output = []
        output.append(f"\nFound {len(results)} results:\n")
        output.append("=" * 80)
        
        for i, result in enumerate(results, 1):
            output.append(f"\n{i}. {result.get('name', 'Unknown')}")
            
            if 'chunkNumber' in result:
                output.append(f"   Chunk: {result['chunkNumber'] + 1}/{result.get('totalChunks', '?')}")
            
            output.append(f"   Path: {result.get('filePath', 'Unknown')}")
            output.append(f"   Extension: {result.get('extension', 'Unknown')}")
            
            if 'modifiedDateTime' in result:
                output.append(f"   Modified: {result['modifiedDateTime']}")
            
            if show_scores and '@search.score' in result:
                output.append(f"   Score: {result['@search.score']:.4f}")
            
            if '@search.reranker_score' in result:
                output.append(f"   Reranker Score: {result['@search.reranker_score']:.4f}")
            
            # Show captions if available
            if '@search.captions' in result:
                for caption in result['@search.captions']:
                    output.append(f"   Caption: {caption.text}")
            
            # Show content preview
            content = result.get('chunk') or result.get('content', '')
            if content:
                preview = content[:200].replace('\n', ' ')
                output.append(f"   Preview: {preview}...")
            
            output.append("")
        
        output.append("=" * 80)
        return '\n'.join(output)