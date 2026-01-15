"""
Create a standard text search index in Azure AI Search

Author: Edgar McOchieng
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.index_manager import IndexManager
from config import Config

def main():
    """Create standard index"""
    print("=" * 80)
    print("CREATE STANDARD TEXT SEARCH INDEX")
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
    
    # Create index
    manager = IndexManager()
    success = manager.create_standard_index()
    
    if success:
        print("\n✨ Standard index created successfully!")
        print(f"   Index name: {Config.AZURE_SEARCH_INDEX_NAME}")
        print(f"   Ready for text indexing")
        print(f"\nNext steps:")
        print(f"   1. Run: python scripts/index_files.py")
        return 0
    else:
        print("\n❌ Failed to create index")
        return 1

if __name__ == "__main__":
    sys.exit(main())