"""
Centralized configuration management with validation and environment support
Author: Edgar McOchieng
"""

import os
from pathlib import Path
from typing import List, Optional, Dict, Any
from dotenv import load_dotenv
import json

# Load environment variables
load_dotenv()


class ConfigValidationError(Exception):
    """Raised when configuration validation fails"""
    pass


class Config:
    """
    Central configuration class with validation and environment support
    
    Supports multiple deployment scenarios:
    - Development: Local testing with .env file
    - Staging: Pre-production environment
    - Production: Enterprise deployment
    """
    
    # Environment
    ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
    
    #==========================================================================
    # Azure AI Search Configuration
    #==========================================================================
    AZURE_SEARCH_ENDPOINT: str = os.getenv("AZURE_SEARCH_ENDPOINT", "")
    AZURE_SEARCH_KEY: str = os.getenv("AZURE_SEARCH_KEY", "")
    AZURE_SEARCH_INDEX_NAME: str = os.getenv("AZURE_SEARCH_INDEX_NAME", "fileshare-documents")
    AZURE_SEARCH_VECTOR_INDEX_NAME: str = os.getenv("AZURE_SEARCH_VECTOR_INDEX_NAME", "fileshare-vector-documents")
    AZURE_SEARCH_API_VERSION: str = os.getenv("AZURE_SEARCH_API_VERSION", "2023-11-01")
    
    #==========================================================================
    # Azure OpenAI Configuration
    #==========================================================================
    AZURE_OPENAI_ENDPOINT: str = os.getenv("AZURE_OPENAI_ENDPOINT", "")
    AZURE_OPENAI_KEY: str = os.getenv("AZURE_OPENAI_KEY", "")
    AZURE_OPENAI_EMBEDDING_DEPLOYMENT: str = os.getenv("AZURE_OPENAI_EMBEDDING_DEPLOYMENT", "text-embedding-3-large")
    AZURE_OPENAI_CHAT_DEPLOYMENT: str = os.getenv("AZURE_OPENAI_CHAT_DEPLOYMENT", "gpt-4")
    AZURE_OPENAI_API_VERSION: str = os.getenv("AZURE_OPENAI_API_VERSION", "2024-05-01-preview")
    EMBEDDING_DIMENSIONS: int = int(os.getenv("EMBEDDING_DIMENSIONS", "3072"))
    
    #==========================================================================
    # File Share Configuration
    #==========================================================================
    FILE_SHARE_PATH: str = os.getenv("FILE_SHARE_PATH", "")
    SUPPORTED_EXTENSIONS: List[str] = [
        ext.strip() for ext in os.getenv("SUPPORTED_EXTENSIONS", ".txt,.docx,.pdf,.xlsx,.pptx").split(",")
    ]
    EXCLUDE_DIRECTORIES: List[str] = [
        d.strip() for d in os.getenv("EXCLUDE_DIRECTORIES", "").split(",") if d.strip()
    ]
    MAX_FILE_SIZE_MB: int = int(os.getenv("MAX_FILE_SIZE_MB", "50"))
    
    #==========================================================================
    # Indexing Configuration
    #==========================================================================
    CHUNK_SIZE: int = int(os.getenv("CHUNK_SIZE", "1000"))
    CHUNK_OVERLAP: int = int(os.getenv("CHUNK_OVERLAP", "200"))
    BATCH_SIZE: int = int(os.getenv("BATCH_SIZE", "100"))
    MAX_WORKERS: int = int(os.getenv("MAX_WORKERS", "4"))
    INCREMENTAL_INDEXING: bool = os.getenv("INCREMENTAL_INDEXING", "true").lower() == "true"
    
    #==========================================================================
    # Search Configuration
    #==========================================================================
    DEFAULT_TOP_K: int = int(os.getenv("DEFAULT_TOP_K", "5"))
    ENABLE_SEMANTIC_RERANKING: bool = os.getenv("ENABLE_SEMANTIC_RERANKING", "true").lower() == "true"
    MIN_RELEVANCE_SCORE: float = float(os.getenv("MIN_RELEVANCE_SCORE", "0.7"))
    
    #==========================================================================
    # Logging Configuration
    #==========================================================================
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE: str = os.getenv("LOG_FILE", "logs/indexer.log")
    LOG_TO_CONSOLE: bool = os.getenv("LOG_TO_CONSOLE", "true").lower() == "true"
    LOG_FORMAT: str = os.getenv("LOG_FORMAT", "detailed")
    
    #==========================================================================
    # Performance & Optimization
    #==========================================================================
    CACHE_EMBEDDINGS: bool = os.getenv("CACHE_EMBEDDINGS", "true").lower() == "true"
    CACHE_DIR: str = os.getenv("CACHE_DIR", ".cache")
    MAX_RETRIES: int = int(os.getenv("MAX_RETRIES", "3"))
    RETRY_DELAY: int = int(os.getenv("RETRY_DELAY", "2"))
    
    #==========================================================================
    # Advanced Configuration
    #==========================================================================
    ENABLE_TELEMETRY: bool = os.getenv("ENABLE_TELEMETRY", "false").lower() == "true"
    
    @classmethod
    def validate(cls, require_openai: bool = False) -> bool:
        """
        Validate configuration
        
        Args:
            require_openai: Whether to require OpenAI configuration
            
        Returns:
            True if valid
            
        Raises:
            ConfigValidationError: If validation fails
        """
        errors = []
        
        # Required fields
        if not cls.AZURE_SEARCH_ENDPOINT:
            errors.append("AZURE_SEARCH_ENDPOINT is required")
        elif not cls.AZURE_SEARCH_ENDPOINT.startswith("https://"):
            errors.append("AZURE_SEARCH_ENDPOINT must start with https://")
            
        if not cls.AZURE_SEARCH_KEY:
            errors.append("AZURE_SEARCH_KEY is required")
            
        if not cls.FILE_SHARE_PATH:
            errors.append("FILE_SHARE_PATH is required")
            
        # OpenAI validation (if required)
        if require_openai:
            if not cls.AZURE_OPENAI_ENDPOINT:
                errors.append("AZURE_OPENAI_ENDPOINT is required for vector search")
            if not cls.AZURE_OPENAI_KEY:
                errors.append("AZURE_OPENAI_KEY is required for vector search")
                
        # Value validation
        if cls.CHUNK_SIZE < 100 or cls.CHUNK_SIZE > 8000:
            errors.append("CHUNK_SIZE must be between 100 and 8000")
            
        if cls.CHUNK_OVERLAP >= cls.CHUNK_SIZE:
            errors.append("CHUNK_OVERLAP must be less than CHUNK_SIZE")
            
        if cls.BATCH_SIZE < 1 or cls.BATCH_SIZE > 1000:
            errors.append("BATCH_SIZE must be between 1 and 1000")
            
        if cls.EMBEDDING_DIMENSIONS not in [1536, 3072]:
            errors.append("EMBEDDING_DIMENSIONS must be 1536 or 3072")
            
        if errors:
            raise ConfigValidationError("Configuration validation failed:\n  - " + "\n  - ".join(errors))
        
        return True
    
    @classmethod
    def to_dict(cls, mask_secrets: bool = True) -> Dict[str, Any]:
        """
        Convert configuration to dictionary
        
        Args:
            mask_secrets: Whether to mask sensitive values
            
        Returns:
            Configuration dictionary
        """
        def mask(value: str) -> str:
            if not value or not mask_secrets:
                return value
            if len(value) <= 12:
                return "***"
            return f"{value[:8]}...{value[-4:]}"
        
        return {
            "environment": cls.ENVIRONMENT,
            "azure_search": {
                "endpoint": cls.AZURE_SEARCH_ENDPOINT,
                "key": mask(cls.AZURE_SEARCH_KEY),
                "index_name": cls.AZURE_SEARCH_INDEX_NAME,
                "vector_index_name": cls.AZURE_SEARCH_VECTOR_INDEX_NAME,
                "api_version": cls.AZURE_SEARCH_API_VERSION,
            },
            "azure_openai": {
                "endpoint": cls.AZURE_OPENAI_ENDPOINT,
                "key": mask(cls.AZURE_OPENAI_KEY),
                "embedding_deployment": cls.AZURE_OPENAI_EMBEDDING_DEPLOYMENT,
                "chat_deployment": cls.AZURE_OPENAI_CHAT_DEPLOYMENT,
                "api_version": cls.AZURE_OPENAI_API_VERSION,
                "embedding_dimensions": cls.EMBEDDING_DIMENSIONS,
            },
            "file_share": {
                "path": cls.FILE_SHARE_PATH,
                "supported_extensions": cls.SUPPORTED_EXTENSIONS,
                "exclude_directories": cls.EXCLUDE_DIRECTORIES,
                "max_file_size_mb": cls.MAX_FILE_SIZE_MB,
            },
            "indexing": {
                "chunk_size": cls.CHUNK_SIZE,
                "chunk_overlap": cls.CHUNK_OVERLAP,
                "batch_size": cls.BATCH_SIZE,
                "max_workers": cls.MAX_WORKERS,
                "incremental": cls.INCREMENTAL_INDEXING,
            },
            "search": {
                "default_top_k": cls.DEFAULT_TOP_K,
                "semantic_reranking": cls.ENABLE_SEMANTIC_RERANKING,
                "min_relevance_score": cls.MIN_RELEVANCE_SCORE,
            },
            "logging": {
                "level": cls.LOG_LEVEL,
                "file": cls.LOG_FILE,
                "console": cls.LOG_TO_CONSOLE,
                "format": cls.LOG_FORMAT,
            },
            "performance": {
                "cache_embeddings": cls.CACHE_EMBEDDINGS,
                "cache_dir": cls.CACHE_DIR,
                "max_retries": cls.MAX_RETRIES,
                "retry_delay": cls.RETRY_DELAY,
            }
        }
    
    @classmethod
    def print_config(cls, mask_secrets: bool = True):
        """Print configuration in formatted output"""
        config_dict = cls.to_dict(mask_secrets=mask_secrets)
        
        print("=" * 80)
        print("CONFIGURATION")
        print("=" * 80)
        print(f"\nEnvironment: {config_dict['environment'].upper()}\n")
        
        for section, values in config_dict.items():
            if section == "environment":
                continue
                
            print(f"\n{section.replace('_', ' ').title()}:")
            for key, value in values.items():
                if isinstance(value, list):
                    print(f"  {key}: {', '.join(str(v) for v in value)}")
                else:
                    print(f"  {key}: {value}")
        
        print("\n" + "=" * 80)
    
    @classmethod
    def save_config(cls, filepath: str = "config.json", mask_secrets: bool = True):
        """Save configuration to JSON file"""
        config_dict = cls.to_dict(mask_secrets=mask_secrets)
        with open(filepath, 'w') as f:
            json.dump(config_dict, f, indent=2)
        print(f"Configuration saved to {filepath}")


# Auto-validate on import (warning only)
try:
    Config.validate(require_openai=False)
except ConfigValidationError as e:
    print(f"⚠️  Configuration Warning: {e}")
    print("Please ensure your .env file is properly configured before running.")