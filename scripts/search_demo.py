"""
Demonstrate search capabilities

Author: Edgar McOchieng
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.search import SearchClient
from config import Config
import argparse

def main():
    """Run search demonstration"""
    parser = argparse.ArgumentParser(description="Search indexed documents")
    parser.add_argument("query", type=str, help="Search query")
    parser.add_argument("--type", type=str, default="hybrid", 
                       choices=["keyword", "vector", "hybrid", "semantic"],
                       help="Search type")
    parser.add_argument("--top", type=int, default=5, help="Number of results")
    parser.add_argument("--extension", type=str, help="Filter by file extension (e.g., .pdf)")
    parser.add_argument("--date-from", type=str, help="Filter by modified date from (ISO format)")
    
    args = parser.parse_args()
    
    print("=" * 80)
    print(f"SEARCH DEMO - {args.type.upper()} SEARCH")
    print("=" * 80)
    print(f"Query: {args.query}")
    print(f"Top: {args.top}")
    if args.extension:
        print(f"Extension filter: {args.extension}")
    if args.date_from:
        print(f"Date from: {args.date_from}")
    print("=" * 80)
    print()
    
    # Create search client
    search = SearchClient()
    
    # Execute search
    if args.extension or args.date_from:
        results = search.filtered_search(
            query=args.query,
            extension=args.extension,
            date_from=args.date_from,
            top=args.top,
            search_type=args.type
        )
    else:
        search_methods = {
            "keyword": search.search,
            "vector": search.vector_search,
            "hybrid": search.hybrid_search,
            "semantic": search.semantic_search
        }
        search_method = search_methods[args.type]
        results = search_method(args.query, top=args.top)
    
    # Display results
    output = search.format_results(results)
    print(output)
    
    return 0

if __name__ == "__main__":
    sys.exit(main())