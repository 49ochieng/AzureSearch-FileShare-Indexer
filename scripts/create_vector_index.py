"""
Create a vector-enabled index with semantic search in Azure AI Search

Author: Edgar McOchieng
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.index_manager import IndexManager
from config import Config

def main():
    """Create vector index"""
    print("=" * 80)
    print("CREATE VECTOR-ENABLED INDEX WITH SEMANTIC SEARCH")
    print("=" * 80)
    print()
    
    # Validate configuration
    try:
        Config.validate(require_openai=True)
    except Exception as e:
        print(f"❌ Configuration error: {e}")
        print("\nPlease ensure Azure OpenAI configuration is set in .env file")
        return 1
    
    # Print configuration
    Config.print_config()
    print()
    
    # Create index
    manager = IndexManager()
    success = manager.create_vector_index()
    
    if success:
        print("\n✨ Vector index created successfully!")
        print(f"   Index name: {Config.AZURE_SEARCH_VECTOR_INDEX_NAME}")
        print(f"   Vector dimensions: {Config.EMBEDDING_DIMENSIONS}")
        print(f"   Embedding model: {Config.AZURE_OPENAI_EMBEDDING_DEPLOYMENT}")
        print(f"\n   Capabilities:")
        print(f"   ✅ Text search")
        print(f"   ✅ Vector similarity search")
        print(f"   ✅ Hybrid search")
        print(f"   ✅ Semantic ranking")
        print(f"\nNext steps:")
        print(f"   1. Run: python scripts/index_files_vector.py")
        return 0
    else:
        print("\n❌ Failed to create index")
        return 1

if __name__ == "__main__":
    sys.exit(main())