
"""
Index management script

List, create, delete, and manage Azure AI Search indexes.

Author: Edgar McOchieng
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import argparse
from src.index_manager import IndexManager
from config import Config

def list_indexes(manager):
    """List all indexes"""
    print("\n📋 Listing all indexes...")
    indexes = manager.list_indexes()
    
    if not indexes:
        print("No indexes found")
        return
    
    print(f"\nFound {len(indexes)} indexes:\n")
    for i, index_name in enumerate(indexes, 1):
        print(f"{i}. {index_name}")
        
        # Get statistics
        try:
            stats = manager.get_index_statistics(index_name)
            if stats:
                doc_count = stats.get('documentCount', 'N/A')
                storage = stats.get('storageSize', 0)
                storage_mb = storage / (1024 * 1024) if storage else 0
                print(f"   Documents: {doc_count}")
                print(f"   Storage: {storage_mb:.2f} MB")
        except:
            pass
        print()

def create_index(manager, args):
    """Create a new index"""
    if args.vector:
        print(f"\n🔨 Creating vector index: {args.name}")
        success = manager.create_vector_index(
            index_name=args.name,
            embedding_dimensions=args.dimensions
        )
    else:
        print(f"\n🔨 Creating standard index: {args.name}")
        success = manager.create_standard_index(index_name=args.name)
    
    if success:
        print("✅ Index created successfully!")
    else:
        print("❌ Failed to create index")
        return 1
    return 0

def delete_index(manager, args):
    """Delete an index"""
    if not args.confirm:
        response = input(f"⚠️  Are you sure you want to delete '{args.name}'? (yes/no): ")
        if response.lower() != 'yes':
            print("Cancelled")
            return 0
    
    print(f"\n🗑️  Deleting index: {args.name}")
    success = manager.delete_index(args.name)
    
    if success:
        print("✅ Index deleted successfully!")
    else:
        print("❌ Failed to delete index")
        return 1
    return 0

def show_stats(manager, args):
    """Show index statistics"""
    print(f"\n📊 Statistics for: {args.name}")
    
    stats = manager.get_index_statistics(args.name)
    
    if not stats:
        print("❌ Could not retrieve statistics")
        return 1
    
    print("\nIndex Statistics:")
    print(f"  Document Count: {stats.get('documentCount', 'N/A')}")
    
    storage = stats.get('storageSize', 0)
    if storage:
        storage_mb = storage / (1024 * 1024)
        storage_gb = storage_mb / 1024
        print(f"  Storage Size: {storage_mb:.2f} MB ({storage_gb:.4f} GB)")
    
    return 0

def main():
    """Main function"""
    parser = argparse.ArgumentParser(
        description="Manage Azure AI Search indexes",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # List all indexes
  python scripts/manage_indexes.py list
  
  # Create standard index
  python scripts/manage_indexes.py create my-index
  
  # Create vector index
  python scripts/manage_indexes.py create my-vector-index --vector
  
  # Show statistics
  python scripts/manage_indexes.py stats my-index
  
  # Delete index (with confirmation)
  python scripts/manage_indexes.py delete old-index
  
  # Delete index (skip confirmation)
  python scripts/manage_indexes.py delete old-index --confirm
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Command to execute')
    
    # List command
    subparsers.add_parser('list', help='List all indexes')
    
    # Create command
    create_parser = subparsers.add_parser('create', help='Create a new index')
    create_parser.add_argument('name', help='Index name')
    create_parser.add_argument('--vector', action='store_true', help='Create vector-enabled index')
    create_parser.add_argument('--dimensions', type=int, default=3072, help='Vector dimensions (default: 3072)')
    
    # Delete command
    delete_parser = subparsers.add_parser('delete', help='Delete an index')
    delete_parser.add_argument('name', help='Index name')
    delete_parser.add_argument('--confirm', action='store_true', help='Skip confirmation prompt')
    
    # Stats command
    stats_parser = subparsers.add_parser('stats', help='Show index statistics')
    stats_parser.add_argument('name', help='Index name')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    # Initialize manager
    try:
        Config.validate(require_openai=False)
    except Exception as e:
        print(f"❌ Configuration error: {e}")
        return 1
    
    manager = IndexManager()
    
    # Execute command
    try:
        if args.command == 'list':
            list_indexes(manager)
            return 0
        elif args.command == 'create':
            return create_index(manager, args)
        elif args.command == 'delete':
            return delete_index(manager, args)
        elif args.command == 'stats':
            return show_stats(manager, args)
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())