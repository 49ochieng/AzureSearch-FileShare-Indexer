"""
Index files from file share with vector embeddings

Author: Edgar McOchieng
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.vector_indexer import VectorIndexer
from config import Config
import argparse

def main():
    """Run vector indexing"""
    parser = argparse.ArgumentParser(description="Index files with vector embeddings")
    parser.add_argument("--path", type=str, help="Path to file share (overrides config)")
    parser.add_argument("--recursive", action="store_true", default=True, help="Index subdirectories")
    parser.add_argument("--no-progress", action="store_true", help="Disable progress bar")
    
    args = parser.parse_args()
    
    print("=" * 80)
    print("VECTOR INDEXER WITH EMBEDDINGS")
    print("=" * 80)
    print()
    
    # Validate configuration
    try:
        Config.validate(require_openai=True)
    except Exception as e:
        print(f"❌ Configuration error: {e}")
        return 1
    
    # Print configuration
    Config.print_config()
    print()
    
    # Create indexer
    indexer = VectorIndexer()
    
    # Run indexing
    path = args.path or Config.FILE_SHARE_PATH
    stats = indexer.index_directory(    