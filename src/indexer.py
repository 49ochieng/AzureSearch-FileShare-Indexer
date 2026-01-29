"""
Standard indexer for Azure AI Search (without vector embeddings)
For high-performance text indexing with metadata

Author: Edgar McOchieng
"""

import os
import hashlib
from datetime import datetime
from typing import Dict, List, Optional, Any
from pathlib import Path
from azure.search.documents import SearchClient
from azure.core.credentials import AzureKeyCredential
from tqdm import tqdm
import time

from config import Config
from config.logger import get_logger
from .extractors import ContentExtractor, ExtractionError

logger = get_logger(__name__)


class FileIndexer:
    """
    Index files to Azure AI Search with full-text search capabilities
    
    Features:
    - Multi-format document processing
    - Metadata extraction
    - Batch upload for performance
    - Incremental indexing support
    - Progress tracking
    """
    
    def __init__(self, index_name: Optional[str] = None):
        """
        Initialize the file indexer
        
        Args:
            index_name: Name of the index (defaults to config value)
        """
        self.index_name = index_name or Config.AZURE_SEARCH_INDEX_NAME
        
        logger.info(f"Initializing FileIndexer for index: {self.index_name}")
        
        # Initialize search client
        self.search_client = SearchClient(
            endpoint=Config.AZURE_SEARCH_ENDPOINT,
            index_name=self.index_name,
            credential=AzureKeyCredential(Config.AZURE_SEARCH_KEY)
        )
        
        # Initialize content extractor
        self.extractor = ContentExtractor()
        
        # Statistics
        self.stats = {
            "total_files": 0,
            "successful": 0,
            "failed": 0,
            "skipped": 0,
            "total_size_mb": 0,
            "start_time": None,
            "end_time": None,
        }
        
        # Incremental indexing cache
        self.indexed_files_cache = {}
        if Config.INCREMENTAL_INDEXING:
            self._load_indexed_files_cache()
    
    def _load_indexed_files_cache(self):
        """Load cache of previously indexed files"""
        cache_file = Path(Config.CACHE_DIR) / f"{self.index_name}_cache.txt"
        
        if cache_file.exists():
            try:
                with open(cache_file, 'r') as f:
                    for line in f:
                        path, mtime = line.strip().split('|')
                        self.indexed_files_cache[path] = float(mtime)
                logger.info(f"Loaded {len(self.indexed_files_cache)} cached entries")
            except Exception as e:
                logger.warning(f"Could not load cache: {e}")
    
    def _save_indexed_files_cache(self):
        """Save cache of indexed files"""
        cache_file = Path(Config.CACHE_DIR) / f"{self.index_name}_cache.txt"
        cache_file.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            with open(cache_file, 'w') as f:
                for path, mtime in self.indexed_files_cache.items():
                    f.write(f"{path}|{mtime}\n")
            logger.info("Saved indexing cache")
        except Exception as e:
            logger.warning(f"Could not save cache: {e}")
    
    def _should_index_file(self, file_path: str) -> bool:
        """Check if file should be indexed based on size and incremental settings
        
        Args:
            file_path: Path to the file to check
            
        Returns:
            True if file should be indexed, False otherwise
        """
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
    
    def _generate_document_id(self, file_path: str) -> str:
        """Generate unique document ID using MD5 hash of file path
        
        Args:
            file_path: Path to the file
            
        Returns:
            MD5 hash string as document identifier
        """
        return hashlib.md5(file_path.encode()).hexdigest()
    
    def _prepare_document(self, file_path: str) -> Optional[Dict[str, Any]]:
        """
        Prepare document for indexing
        
        Args:
            file_path: Path to the file
            
        Returns:
            Document dictionary or None if preparation fails
        """
        try:
            # Extract metadata
            metadata = self.extractor.extract_metadata(file_path)
            
            # Extract content
            content = self.extractor.extract_text(file_path)
            
            # Truncate content if too large
            max_content_length = 50000  # characters
            if len(content) > max_content_length:
                logger.warning(f"Truncating content for {file_path} ({len(content)} chars)")
                content = content[:max_content_length]
            
            # Prepare document
            document = {
                "id": self._generate_document_id(file_path),
                "content": content,
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
            if "document_keywords" in metadata:
                document["keywords"] = metadata["document_keywords"]
            
            return document
            
        except ExtractionError as e:
            logger.error(f"Failed to prepare document {file_path}: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error preparing {file_path}: {e}")
            return None
    
    def index_file(self, file_path: str) -> bool:
        """
        Index a single file
        
        Args:
            file_path: Path to the file
            
        Returns:
            True if successful, False otherwise
        """
        try:
            logger.info(f"Indexing: {os.path.basename(file_path)}")
            
            # Check if should index
            if not self._should_index_file(file_path):
                return False
            
            # Prepare document
            document = self._prepare_document(file_path)
            if not document:
                self.stats["failed"] += 1
                return False
            
            # Upload to Azure AI Search
            result = self.search_client.upload_documents(documents=[document])
            
            if result[0].succeeded:
                logger.info(f"✅ Successfully indexed: {os.path.basename(file_path)}")
                self.stats["successful"] += 1
                
                # Update cache
                if Config.INCREMENTAL_INDEXING:
                    self.indexed_files_cache[file_path] = os.path.getmtime(file_path)
                
                # Update size statistics
                self.stats["total_size_mb"] += os.path.getsize(file_path) / (1024 * 1024)
                
                return True
            else:
                logger.error(f"❌ Failed to index: {os.path.basename(file_path)}")
                self.stats["failed"] += 1
                return False
                
        except Exception as e:
            logger.error(f"Error indexing {file_path}: {e}")
            self.stats["failed"] += 1
            return False
    
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
        
        logger.info(f"Starting indexing from: {directory_path}")
        logger.info(f"Recursive: {recursive}, Incremental: {Config.INCREMENTAL_INDEXING}")
        
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
        
        # Save cache
        if Config.INCREMENTAL_INDEXING:
            self._save_indexed_files_cache()
        
        # Print summary
        self._print_summary()
        
        return self.stats.copy()
    
    def _print_summary(self):
        """Print indexing summary"""
        duration = (self.stats["end_time"] - self.stats["start_time"]).total_seconds()
        
        logger.info("=" * 80)
        logger.info("INDEXING SUMMARY")
        logger.info("=" * 80)
        logger.info(f"Total files found: {self.stats['total_files']}")
        logger.info(f"Successfully indexed: {self.stats['successful']}")
        logger.info(f"Failed: {self.stats['failed']}")
        logger.info(f"Skipped (unchanged): {self.stats['skipped']}")
        logger.info(f"Total size: {self.stats['total_size_mb']:.2f} MB")
        logger.info(f"Duration: {duration:.2f} seconds")
        
        if self.stats['successful'] > 0:
            rate = self.stats['successful'] / duration
            logger.info(f"Indexing rate: {rate:.2f} files/second")
        
        logger.info("=" * 80)
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get indexing statistics"""
        return self.stats.copy()