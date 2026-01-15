"""
Configuration module for AzureSearch FileShare Indexer
"""

from .settings import Config
from .logger import setup_logger, get_logger

__all__ = ["Config", "setup_logger", "get_logger"]