"""
Index files from file share using standard text search

Author: Edgar McOchieng
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.indexer import FileIndexer
from config import Config
import argparse

def main():
    """Run file indexing"""
    parser = argparse.ArgumentParser(description="Index files to Azure AI Search")
    parser.add_argument("--path", type=str, help="Path to file share (overrides config)")
    parser.add_argument("--recursive", action="store_true", default=True, help="Index subdirectories")
    parser.add_argument("--no-progress", action="store_true", help="Disable progress bar")
    
    args = parser.parse_args()
    
    print("=" * 80)
    print("FILE SHARE INDEXER - STANDARD TEXT SEARCH")
    print("=" * 80)
    print()
    
    # Validate configuration
    try:
        Config.validate(require_openai=False)
    except Exception as e:
        print(f"❌ Configuration error: {e}")
        return 1
    
    # Print configuration
    Config.print_config()
    print()
    
    # Create indexer
    indexer = FileIndexer()
    
    # Run indexing
    path = args.path or Config.FILE_SHARE_PATH
    stats = indexer.index_directory(
        directory_path=path,
        recursive=args.recursive,
        show_progress=not args.no_progress
    )
    
    print("\n✨ Indexing complete!")
    return 0

if __name__ == "__main__":
    sys.exit(main())