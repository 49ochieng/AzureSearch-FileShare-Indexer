"""
Logging configuration and utilities
Author: Edgar McOchieng
"""

import sys
import os
from pathlib import Path
from loguru import logger
from config.settings import Config


def setup_logger():
    """
    Configure logging based on Config settings
    
    Supports multiple log formats:
    - simple: Basic messages only
    - detailed: Includes timestamp, level, module
    - json: Structured JSON logs for monitoring systems
    """
    # Remove default logger
    logger.remove()
    
    # Define formats
    formats = {
        "simple": "<level>{message}</level>",
        "detailed": "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | <level>{message}</level>",
        "json": "{time:YYYY-MM-DD HH:mm:ss} | {level} | {name}:{function}:{line} | {message}"
    }
    
    log_format = formats.get(Config.LOG_FORMAT, formats["detailed"])
    
    # Console logging
    if Config.LOG_TO_CONSOLE:
        logger.add(
            sys.stdout,
            format=log_format,
            level=Config.LOG_LEVEL,
            colorize=True
        )
    
    # File logging
    if Config.LOG_FILE:
        log_path = Path(Config.LOG_FILE)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        logger.add(
            Config.LOG_FILE,
            format=log_format,
            level=Config.LOG_LEVEL,
            rotation="10 MB",
            retention="30 days",
            compression="zip"
        )
    
    return logger


def get_logger(name: str = None):
    """
    Get a logger instance
    
    Args:
        name: Logger name (usually __name__)
        
    Returns:
        Logger instance
    """
    if name:
        return logger.bind(name=name)
    return logger


# Initialize logger on import
setup_logger()