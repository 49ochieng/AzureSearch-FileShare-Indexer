"""
Logging configuration and utilities
Author: Edgar McOchieng
"""

import sys
import os
from pathlib import Path
from loguru import logger

# Flag to track if logger is initialized
_logger_initialized = False


def setup_logger(log_level="INFO", log_file="logs/indexer.log", log_to_console=True, log_format="detailed"):
    """
    Configure logging based on provided settings
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Path to log file
        log_to_console: Whether to log to console
        log_format: Format style (simple, detailed, json)
    
    Supports multiple log formats:
    - simple: Basic messages only
    - detailed: Includes timestamp, level, module
    - json: Structured JSON logs for monitoring systems
    """
    global _logger_initialized
    
    # Remove default logger
    logger.remove()
    
    # Define formats
    formats = {
        "simple": "<level>{message}</level>",
        "detailed": "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | <level>{message}</level>",
        "json": "{time:YYYY-MM-DD HH:mm:ss} | {level} | {name}:{function}:{line} | {message}"
    }
    
    log_format_str = formats.get(log_format, formats["detailed"])
    
    # Console logging
    if log_to_console:
        logger.add(
            sys.stdout,
            format=log_format_str,
            level=log_level,
            colorize=True
        )
    
    # File logging
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        logger.add(
            log_file,
            format=log_format_str,
            level=log_level,
            rotation="10 MB",
            retention="30 days",
            compression="zip"
        )
    
    _logger_initialized = True
    return logger


def get_logger(name: str = None):
    """
    Get a logger instance
    
    Args:
        name: Logger name (usually __name__)
        
    Returns:
        Logger instance
    """
    global _logger_initialized
    
    # Lazy initialization with Config if available
    if not _logger_initialized:
        try:
            from config.settings import Config
            setup_logger(
                log_level=Config.LOG_LEVEL,
                log_file=Config.LOG_FILE,
                log_to_console=Config.LOG_TO_CONSOLE,
                log_format=Config.LOG_FORMAT
            )
        except (ImportError, Exception):
            # Fallback to default settings if Config not available
            setup_logger()
    
    if name:
        return logger.bind(name=name)
    return logger