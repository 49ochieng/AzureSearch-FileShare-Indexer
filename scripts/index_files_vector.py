"""
Index files from file share with vector embeddings

Author: Edgar McOchieng
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import argparse
from config import Config
from src.vector_indexer import VectorIndexer
import logging

logging.basicConfig(
    level=getattr(logging, Config.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(Config.LOG_FILE),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)


def main():
    parser = argparse.ArgumentParser(description="Index files with vectors into Azure AI Search")
    parser.add_argument("--path", default=Config.FILE_SHARE_PATH, help="Path to file share or directory")
    parser.add_argument("--batch-size", type=int, default=Config.BATCH_SIZE, help="Batch size for indexing")
    args = parser.parse_args()
    
    if not args.path:
        logger.error("FILE_SHARE_PATH not configured. Set it in .env file.")
        sys.exit(1)
    
    try:
        indexer = VectorIndexer()
        success = indexer.index_directory_with_vectors(args.path)
        
        if success:
            logger.info("Vector indexing completed successfully")
            sys.exit(0)
        else:
            logger.error("Vector indexing failed")
            sys.exit(1)
    
    except Exception as e:
        logger.error(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
