"""
Vector indexer with embeddings and intelligent chunking
Provides semantic search capabilities through Azure OpenAI embeddings

Author: Edgar McOchieng
"""

import os
import hashlib
from datetime import datetime
from typing import Dict, List, Optional, Any
from pathlib import Path
from azure.search.documents import SearchClient
from azure.core.credentials import AzureKeyCredential
from openai import AzureOpenAI
import tiktoken
from tqdm import tqdm
import time

from config import Config
from config.logger import get_logger
from .extractors import ContentExtractor, ExtractionError

logger = get_logger(__name__)


class VectorIndexer:
    """
    Index files with vector embeddings for semantic search
    
    Features:
    - Intelligent text chunking
    - Vector embeddings generation
    - Batch processing
    - Progress tracking
    - Embedding caching
    """
    
    def __init__(self, index_name: Optional[str] = None):
        """
        Initialize vector indexer
        
        Args:
            index_name: Name of the vector index (defaults to config value)
        """
        self.index_name = index_name or Config.AZURE_SEARCH_VECTOR_INDEX_NAME
        
        logger.info(f"Initializing VectorIndexer for index: {self.index_name}")
        
        # Validate OpenAI configuration
        Config.validate(require_openai=True)
        
        # Initialize search client
        self.search_client = SearchClient(
            endpoint=Config.AZURE_SEARCH_ENDPOINT,
            index_name=self.index_name,
            credential=AzureKeyCredential(Config.AZURE_SEARCH_KEY)
        )
        
        # Initialize OpenAI client
        self.openai_client = AzureOpenAI(
            azure_endpoint=Config.AZURE_OPENAI_ENDPOINT,
            api_key=Config.AZURE_OPENAI_KEY,
            api_version=Config.AZURE_OPENAI_API_VERSION
        )
        
        # Initialize content extractor
        self.extractor = ContentExtractor()
        
        # Initialize tokenizer
        self.encoding = tiktoken.get_encoding("cl100k_base")
        
        # Statistics
        self.stats = {
            "total_files": 0,
            "successful_files": 0,
            "failed_files": 0,
            "total_chunks": 0,
            "total_embeddings": 0,
            "skipped": 0,
            "total_size_mb": 0,
            "embedding_api_calls": 0,
            "start_time": None,
            "end_time": None,
        }
        
        # Embedding cache
        self.embedding_cache = {}
        if Config.CACHE_EMBEDDINGS:
            self._load_embedding_cache()
        
        # Incremental indexing cache
        self.indexed_files_cache = {}
        if Config.INCREMENTAL_INDEXING:
            self._load_indexed_files_cache()
    
    def _load_embedding_cache(self):
        """Load cached embeddings"""
        cache_file = Path(Config.CACHE_DIR) / f"{self.index_name}_embeddings.cache"
        if cache_file.exists():
            try:
                import pickle
                with open(cache_file, 'rb') as f:
                    self.embedding_cache = pickle.load(f)
                logger.info(f"Loaded {len(self.embedding_cache)} cached embeddings")
            except Exception as e:
                logger.warning(f"Could not load embedding cache: {e}")
    
    def _save_embedding_cache(self):
        """Save embedding cache"""
        if not Config.CACHE_EMBEDDINGS:
            return
        
        cache_file = Path(Config.CACHE_DIR) / f"{self.index_name}_embeddings.cache"
        cache_file.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            import pickle
            with open(cache_file, 'wb') as f:
                pickle.dump(self.embedding_cache, f)
            logger.info(f"Saved {len(self.embedding_cache)} embeddings to cache")
        except Exception as e:
            logger.warning(f"Could not save embedding cache: {e}")
    
    def _load_indexed_files_cache(self):
        """Load cache of previously indexed files"""
        cache_file = Path(Config.CACHE_DIR) / f"{self.index_name}_files.cache"
        if cache_file.exists():
            try:
                with open(cache_file, 'r') as f:
                    for line in f:
                        path, mtime = line.strip().split('|')
                        self.indexed_files_cache[path] = float(mtime)
                logger.info(f"Loaded {len(self.indexed_files_cache)} cached file entries")
            except Exception as e:
                logger.warning(f"Could not load file cache: {e}")
    
    def _save_indexed_files_cache(self):
        """Save cache of indexed files"""
        cache_file = Path(Config.CACHE_DIR) / f"{self.index_name}_files.cache"
        cache_file.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            with open(cache_file, 'w') as f:
                for path, mtime in self.indexed_files_cache.items():
                    f.write(f"{path}|{mtime}\n")
            logger.info("Saved file indexing cache")
        except Exception as e:
            logger.warning(f"Could not save file cache: {e}")
    
    def _should_index_file(self, file_path: str) -> bool:
        """Check if file should be indexed"""
        # Check file size
        file_size_mb = os.path.getsize(file_path) / (1024 * 1024)
        if file_size_mb > Config.MAX_FILE_SIZE_MB:
            logger.warning(f"Skipping {file_path}: exceeds max size ({file_size_mb:.2f} MB)")
            return False
        
        # Check if file was already indexed (incremental)
        if Config.INCREMENTAL_INDEXING:
            mtime = os.path.getmtime(file_path)
            cached_mtime = self.indexed_files_cache.get(file_path)
            
            if cached_mtime and mtime <= cached_mtime:
                logger.debug(f"Skipping {file_path}: already indexed")
                self.stats["skipped"] += 1
                return False
        
        return True
    
    def chunk_text(self, text: str, chunk_size: Optional[int] = None, overlap: Optional[int] = None) -> List[str]:
        """
        Split text into overlapping chunks based on token count
        
        Args:
            text: Text to chunk
            chunk_size: Size of each chunk in tokens (defaults to config)
            overlap: Overlap between chunks in tokens (defaults to config)
            
        Returns:
            List of text chunks
        """
        chunk_size = chunk_size or Config.CHUNK_SIZE
        overlap = overlap or Config.CHUNK_OVERLAP
        
        # Tokenize text
        tokens = self.encoding.encode(text)
        
        if len(tokens) <= chunk_size:
            return [text]
        
        chunks = []
        start = 0
        
        while start < len(tokens):
            end = start + chunk_size
            chunk_tokens = tokens[start:end]
            chunk_text = self.encoding.decode(chunk_tokens)
            chunks.append(chunk_text)
            
            # Move start position with overlap
            start += chunk_size - overlap
        
        logger.debug(f"Split text into {len(chunks)} chunks ({len(tokens)} tokens total)")
        return chunks
    
    def generate_embedding(self, text: str, use_cache: bool = True) -> Optional[List[float]]:
        """
        Generate embedding for text using Azure OpenAI
        
        Args:
            text: Text to embed
            use_cache: Whether to use cached embeddings
            
        Returns:
            Embedding vector or None if generation fails
        """
        # Check cache
        if use_cache and Config.CACHE_EMBEDDINGS:
            cache_key = hashlib.md5(text.encode()).hexdigest()
            if cache_key in self.embedding_cache:
                logger.debug("Using cached embedding")
                return self.embedding_cache[cache_key]
        
        # Truncate if too long (max 8191 tokens for text-embedding models)
        tokens = self.encoding.encode(text)
        if len(tokens) > 8000:
            logger.debug(f"Truncating text from {len(tokens)} to 8000 tokens")
            tokens = tokens[:8000]
            text = self.encoding.decode(tokens)
        
        # Generate embedding with retry logic
        for attempt in range(Config.MAX_RETRIES):
            try:
                response = self.openai_client.embeddings.create(
                    input=text,
                    model=Config.AZURE_OPENAI_EMBEDDING_DEPLOYMENT
                )
                
                embedding = response.data[0].embedding
                self.stats["embedding_api_calls"] += 1
                
                # Cache the embedding
                if Config.CACHE_EMBEDDINGS:
                    cache_key = hashlib.md5(text.encode()).hexdigest()
                    self.embedding_cache[cache_key] = embedding
                
                return embedding
                
            except Exception as e:
                if attempt < Config.MAX_RETRIES - 1:
                    logger.warning(f"Embedding generation failed (attempt {attempt + 1}): {e}")
                    time.sleep(Config.RETRY_DELAY * (attempt + 1))
                else:
                    logger.error(f"Failed to generate embedding after {Config.MAX_RETRIES} attempts: {e}")
                    return None
    
    def _prepare_documents(self, file_path: str) -> Optional[List[Dict[str, Any]]]:
        """
        Prepare documents with chunks and embeddings
        
        Args:
            file_path: Path to the file
            
        Returns:
            List of document dictionaries or None if preparation fails
        """
        try:
            # Extract metadata
            metadata = self.extractor.extract_metadata(file_path)
            
            # Extract content
            content = self.extractor.extract_text(file_path)
            
            if not content or len(content.strip()) < 10:
                logger.warning(f"No meaningful content extracted from {file_path}")
                return None
            
            # Chunk the content
            chunks = self.chunk_text(content)
            logger.info(f"Created {len(chunks)} chunks from {os.path.basename(file_path)}")
            
            # Prepare documents for each chunk
            documents = []
            for i, chunk in enumerate(chunks):
                # Generate embedding
                embedding = self.generate_embedding(chunk)
                
                if not embedding:
                    logger.warning(f"Skipping chunk {i + 1} due to embedding failure")
                    continue
                
                # Generate unique ID for this chunk
                chunk_id = hashlib.md5(f"{file_path}_chunk_{i}".encode()).hexdigest()
                
                # Prepare document
                document = {
                    "id": chunk_id,
                    "content": content[:50000],  # Store full content in first chunk
                    "chunk": chunk,
                    "contentVector": embedding,
                    "chunkNumber": i,
                    "totalChunks": len(chunks),
                    "title": metadata.get("document_title") or os.path.splitext(metadata["file_name"])[0],
                    "name": metadata["file_name"],
                    "filePath": file_path,
                    "extension": metadata["file_extension"],
                    "size": metadata["file_size_bytes"],
                    "createdDateTime": metadata["created_time"],
                    "modifiedDateTime": metadata["modified_time"],
                    "createdBy": metadata.get("owner", "Unknown"),
                    "lastModifiedBy": metadata.get("owner", "Unknown"),
                    "fileType": "File",
                    "url": file_path,
                }
                
                # Add document-specific metadata if available
                if "document_author" in metadata:
                    document["author"] = metadata["document_author"]
                
                documents.append(document)
                self.stats["total_embeddings"] += 1
            
            self.stats["total_chunks"] += len(documents)
            return documents
            
        except ExtractionError as e:
            logger.error(f"Failed to prepare documents for {file_path}: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error preparing {file_path}: {e}")
            return None
    
    def index_file(self, file_path: str) -> int:
        """
        Index a single file with chunking and embeddings
        
        Args:
            file_path: Path to the file
            
        Returns:
            Number of chunks successfully indexed
        """
        try:
            logger.info(f"Processing: {os.path.basename(file_path)}")
            
            # Check if should index
            if not self._should_index_file(file_path):
                return 0
            
            # Prepare documents
            documents = self._prepare_documents(file_path)
            if not documents:
                self.stats["failed_files"] += 1
                return 0
            
            # Upload in batches
            batch_size = Config.BATCH_SIZE
            successful_chunks = 0
            
            for i in range(0, len(documents), batch_size):
                batch = documents[i:i + batch_size]
                
                try:
                    result = self.search_client.upload_documents(documents=batch)
                    successful_chunks += sum(1 for r in result if r.succeeded)
                except Exception as e:
                    logger.error(f"Failed to upload batch: {e}")
            
            if successful_chunks > 0:
                logger.info(f"✅ Indexed {successful_chunks}/{len(documents)} chunks from {os.path.basename(file_path)}")
                self.stats["successful_files"] += 1
                
                # Update cache
                if Config.INCREMENTAL_INDEXING:
                    self.indexed_files_cache[file_path] = os.path.getmtime(file_path)
                
                # Update size statistics
                self.stats["total_size_mb"] += os.path.getsize(file_path) / (1024 * 1024)
            else:
                logger.error(f"❌ Failed to index any chunks from {os.path.basename(file_path)}")
                self.stats["failed_files"] += 1
            
            return successful_chunks
            
        except Exception as e:
            logger.error(f"Error indexing {file_path}: {e}")
            self.stats["failed_files"] += 1
            return 0
    
    def index_directory(
        self,
        directory_path: Optional[str] = None,
        recursive: bool = True,
        show_progress: bool = True
    ) -> Dict[str, Any]:
        """
        Index all supported files in a directory
        
        Args:
            directory_path: Path to directory (defaults to config value)
            recursive: Whether to index subdirectories
            show_progress: Whether to show progress bar
            
        Returns:
            Statistics dictionary
        """
        directory_path = directory_path or Config.FILE_SHARE_PATH
        
        logger.info("=" * 80)
        logger.info("VECTOR INDEXING WITH EMBEDDINGS")
        logger.info("=" * 80)
        logger.info(f"Directory: {directory_path}")
        logger.info(f"Recursive: {recursive}")
        logger.info(f"Incremental: {Config.INCREMENTAL_INDEXING}")
        logger.info(f"Embedding Model: {Config.AZURE_OPENAI_EMBEDDING_DEPLOYMENT}")
        logger.info(f"Chunk Size: {Config.CHUNK_SIZE} tokens")
        logger.info(f"Chunk Overlap: {Config.CHUNK_OVERLAP} tokens")
        logger.info("=" * 80)
        
        self.stats["start_time"] = datetime.now()
        
        # Collect all files to index
        files_to_index = []
        
        if recursive:
            for root, dirs, files in os.walk(directory_path):
                # Skip excluded directories
                dirs[:] = [d for d in dirs if d not in Config.EXCLUDE_DIRECTORIES]
                
                for file in files:
                    ext = os.path.splitext(file)[1].lower()
                    if ext in Config.SUPPORTED_EXTENSIONS:
                        files_to_index.append(os.path.join(root, file))
        else:
            for file in os.listdir(directory_path):
                file_path = os.path.join(directory_path, file)
                if os.path.isfile(file_path):
                    ext = os.path.splitext(file)[1].lower()
                    if ext in Config.SUPPORTED_EXTENSIONS:
                        files_to_index.append(file_path)
        
        self.stats["total_files"] = len(files_to_index)
        logger.info(f"Found {len(files_to_index)} files to process")
        
        # Index files with progress bar
        if show_progress:
            iterator = tqdm(files_to_index, desc="Indexing files", unit="file")
        else:
            iterator = files_to_index
        
        for file_path in iterator:
            self.index_file(file_path)
        
        self.stats["end_time"] = datetime.now()
        
        # Save caches
        if Config.CACHE_EMBEDDINGS:
            self._save_embedding_cache()
        if Config.INCREMENTAL_INDEXING:
            self._save_indexed_files_cache()
        
        # Print summary
        self._print_summary()
        
        return self.stats.copy()
    
    def _print_summary(self):
        """Print indexing summary"""
        duration = (self.stats["end_time"] - self.stats["start_time"]).total_seconds()
        
        logger.info("=" * 80)
        logger.info("VECTOR INDEXING SUMMARY")
        logger.info("=" * 80)
        logger.info(f"Total files found: {self.stats['total_files']}")
        logger.info(f"Successfully indexed: {self.stats['successful_files']}")
        logger.info(f"Failed: {self.stats['failed_files']}")
        logger.info(f"Skipped (unchanged): {self.stats['skipped']}")
        logger.info(f"Total chunks created: {self.stats['total_chunks']}")
        logger.info(f"Total embeddings generated: {self.stats['total_embeddings']}")
        logger.info(f"OpenAI API calls: {self.stats['embedding_api_calls']}")
        logger.info(f"Total size: {self.stats['total_size_mb']:.2f} MB")
        logger.info(f"Duration: {duration:.2f} seconds")
        
        if self.stats['successful_files'] > 0:
            rate = self.stats['successful_files'] / duration
            logger.info(f"Indexing rate: {rate:.2f} files/second")
        
        logger.info("=" * 80)
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get indexing statistics"""
        return self.stats.copy()