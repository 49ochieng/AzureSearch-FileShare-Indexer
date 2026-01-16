# Usage Guide

Comprehensive guide for using AzureSearch FileShare Indexer.

---

## Table of Contents

- [Quick Start](#quick-start)
- [Creating Indexes](#creating-indexes)
- [Indexing Files](#indexing-files)
- [Searching Documents](#searching-documents)
- [Advanced Features](#advanced-features)
- [Best Practices](#best-practices)
- [Performance Tuning](#performance-tuning)
- [Integration Patterns](#integration-patterns)

---

## Quick Start

### 30-Second Start
```bash
# 1. Create index
python scripts/create_vector_index.py

# 2. Index files
python scripts/index_files_vector.py

# 3. Search
python scripts/search_demo.py "your query"
```

### 5-Minute Start
```python
from src import VectorIndexer, SearchClient

# Index documents
indexer = VectorIndexer()
indexer.index_directory("/path/to/documents")

# Search
search = SearchClient()
results = search.hybrid_search("employee benefits")

# Display results
print(search.format_results(results))
```

---

## Creating Indexes

### Standard Text Index

For keyword-based search without vector embeddings:

#### CLI
```bash
python scripts/create_standard_index.py
```

#### Programmatic
```python
from src.index_manager import IndexManager

manager = IndexManager()
success = manager.create_standard_index(
    index_name="my-text-index"
)

if success:
    print("Index created!")
```

### Vector Index (Recommended)

For semantic search with AI-powered embeddings:

#### CLI
```bash
python scripts/create_vector_index.py
```

#### Programmatic
```python
from src.index_manager import IndexManager

manager = IndexManager()
success = manager.create_vector_index(
    index_name="my-vector-index",
    embedding_dimensions=3072  # for text-embedding-3-large
)
```

### Index Configuration Options
```python
# Custom embedding dimensions
# text-embedding-3-large: 3072
# text-embedding-ada-002: 1536

manager.create_vector_index(
    index_name="custom-index",
    embedding_dimensions=1536
)
```

### Managing Indexes
```python
from src.index_manager import IndexManager

manager = IndexManager()

# List all indexes
indexes = manager.list_indexes()
print(f"Found indexes: {indexes}")

# Get statistics
stats = manager.get_index_statistics("fileshare-vector-documents")
print(f"Documents: {stats['documentCount']}")
print(f"Storage: {stats['storageSize']}")

# Delete index (use with caution!)
manager.delete_index("old-index")
```

---

## Indexing Files

### Basic Indexing

#### Standard Text Indexing
```bash
# CLI
python scripts/index_files.py

# With custom path
python scripts/index_files.py --path /custom/path

# Non-recursive
python scripts/index_files.py --recursive false
```
```python
# Programmatic
from src.indexer import FileIndexer

indexer = FileIndexer()
stats = indexer.index_directory(
    directory_path="/path/to/documents",
    recursive=True,
    show_progress=True
)

print(f"Indexed {stats['successful']} files")
print(f"Failed: {stats['failed']}")
```

#### Vector Indexing with Embeddings
```bash
# CLI
python scripts/index_files_vector.py

# With custom path
python scripts/index_files_vector.py --path /custom/path
```
```python
# Programmatic
from src.vector_indexer import VectorIndexer

indexer = VectorIndexer()
stats = indexer.index_directory(
    directory_path="/path/to/documents",
    recursive=True,
    show_progress=True
)

print(f"Files indexed: {stats['successful_files']}")
print(f"Chunks created: {stats['total_chunks']}")
print(f"Embeddings generated: {stats['total_embeddings']}")
print(f"API calls: {stats['embedding_api_calls']}")
```

### Advanced Indexing

#### Index Specific Files
```python
from src.vector_indexer import VectorIndexer

indexer = VectorIndexer()

files = [
    "/path/to/file1.pdf",
    "/path/to/file2.docx",
    "/path/to/file3.xlsx"
]

for file_path in files:
    chunks = indexer.index_file(file_path)
    print(f"Indexed {chunks} chunks from {file_path}")
```

#### Custom Chunking
```python
from src.vector_indexer import VectorIndexer

indexer = VectorIndexer()

# Custom chunk size and overlap
text = "Your long document text here..."
chunks = indexer.chunk_text(
    text,
    chunk_size=500,    # 500 tokens per chunk
    overlap=100        # 100 token overlap
)

print(f"Created {len(chunks)} chunks")
```

#### Batch Indexing with Progress Tracking
```python
from src.vector_indexer import VectorIndexer
from tqdm import tqdm
import os

indexer = VectorIndexer()

# Collect files
files_to_index = []
for root, dirs, files in os.walk("/path/to/docs"):
    for file in files:
        if file.endswith(('.pdf', '.docx')):
            files_to_index.append(os.path.join(root, file))

# Index with progress bar
for file_path in tqdm(files_to_index, desc="Indexing"):
    indexer.index_file(file_path)

# Get statistics
stats = indexer.get_statistics()
print(f"Total chunks: {stats['total_chunks']}")
```

#### Incremental Indexing
```python
# Enable in .env
INCREMENTAL_INDEXING=true

# Or programmatically
from config import Config
Config.INCREMENTAL_INDEXING = True

from src.vector_indexer import VectorIndexer

indexer = VectorIndexer()

# Only modified files will be indexed
stats = indexer.index_directory("/path/to/docs")
print(f"Skipped {stats['skipped']} unchanged files")
```

---

## Searching Documents

### Search Types

#### 1. Keyword Search

Traditional text-based search:
```bash
# CLI
python scripts/search_demo.py "employee benefits" --type keyword --top 5
```
```python
# Programmatic
from src.search import SearchClient

search = SearchClient()
results = search.search(
    query="employee benefits",
    top=5
)

for result in results:
    print(f"{result['name']}: {result['@search.score']}")
```

#### 2. Vector Search

Pure semantic similarity:
```bash
# CLI
python scripts/search_demo.py "team collaboration tools" --type vector
```
```python
# Programmatic
results = search.vector_search(
    query="team collaboration tools",
    top=5
)
```

#### 3. Hybrid Search (Recommended)

Combines keyword and vector search:
```bash
# CLI
python scripts/search_demo.py "quarterly financial reports" --type hybrid
```
```python
# Programmatic
results = search.hybrid_search(
    query="quarterly financial reports",
    top=10
)
```

#### 4. Semantic Search

Hybrid search with intelligent reranking:
```bash
# CLI
python scripts/search_demo.py "company policies" --type semantic
```
```python
# Programmatic
results = search.semantic_search(
    query="company policies",
    top=5
)

# Check reranker scores
for result in results:
    print(f"Score: {result['@search.score']:.4f}")
    if '@search.reranker_score' in result:
        print(f"Reranker: {result['@search.reranker_score']:.4f}")
```

### Filtered Search

#### Filter by File Extension
```bash
# CLI
python scripts/search_demo.py "contracts" --extension .pdf
```
```python
# Programmatic
results = search.filtered_search(
    query="contracts",
    extension=".pdf",
    search_type="hybrid"
)
```

#### Filter by Date Range
```bash
# CLI
python scripts/search_demo.py "reports" \
  --date-from 2024-01-01T00:00:00Z \
  --type hybrid
```
```python
# Programmatic
results = search.filtered_search(
    query="reports",
    date_from="2024-01-01T00:00:00Z",
    date_to="2024-12-31T23:59:59Z",
    search_type="hybrid"
)
```

#### Complex Filters
```python
# Multiple filters
results = search.filtered_search(
    query="employee handbook",
    extension=".pdf",
    date_from="2024-01-01T00:00:00Z",
    author="HR Department",
    top=10,
    search_type="semantic"
)
```

#### Custom OData Filters
```python
# Direct OData filter expression
filter_expr = "extension eq '.pdf' and size gt 1000000"

results = search.hybrid_search(
    query="large documents",
    filter_expr=filter_expr
)
```

### Displaying Results

#### Basic Display
```python
from src.search import SearchClient

search = SearchClient()
results = search.hybrid_search("employee benefits")

# Format and print
output = search.format_results(results, show_scores=True)
print(output)
```

#### Custom Display
```python
results = search.hybrid_search("policies")

for i, result in enumerate(results, 1):
    print(f"\n{i}. {result['name']}")
    print(f"   Path: {result['filePath']}")
    print(f"   Score: {result['@search.score']:.4f}")
    print(f"   Modified: {result['modifiedDateTime']}")
    
    if 'chunk' in result:
        preview = result['chunk'][:150]
        print(f"   Preview: {preview}...")
```

---

## Advanced Features

### 1. Multi-Query Search
```python
from src.search import SearchClient

search = SearchClient()

# Multiple related queries
queries = [
    "employee benefits",
    "health insurance",
    "retirement plans"
]

all_results = []
for query in queries:
    results = search.hybrid_search(query, top=3)
    all_results.extend(results)

# Deduplicate by file path
unique_files = {}
for result in all_results:
    path = result['filePath']
    if path not in unique_files or result['@search.score'] > unique_files[path]['@search.score']:
        unique_files[path] = result

print(f"Found {len(unique_files)} unique documents")
```

### 2. Search with Aggregations
```python
# Get facets/aggregations
results = search.search_client.search(
    search_text="documents",
    facets=["extension", "createdBy"],
    top=0  # Just get facets
)

facets = results.get_facets()
print("File types:")
for facet in facets['extension']:
    print(f"  {facet['value']}: {facet['count']}")
```

### 3. Search Result Export
```python
import json
import csv

# Export to JSON
results = search.hybrid_search("reports", top=50)

with open('search_results.json', 'w') as f:
    json.dump([dict(r) for r in results], f, indent=2, default=str)

# Export to CSV
with open('search_results.csv', 'w', newline='') as f:
    if results:
        writer = csv.DictWriter(f, fieldnames=['name', 'filePath', 'extension', '@search.score'])
        writer.writeheader()
        for result in results:
            writer.writerow({
                'name': result['name'],
                'filePath': result['filePath'],
                'extension': result['extension'],
                '@search.score': result['@search.score']
            })
```

### 4. Programmatic Index Management
```python
from src.index_manager import IndexManager

manager = IndexManager()

# Create multiple indexes for different document sets
indexes = {
    "hr-documents": {"extensions": [".pdf", ".docx"]},
    "financial-reports": {"extensions": [".xlsx"]},
    "technical-docs": {"extensions": [".pdf", ".md"]}
}

for index_name, config in indexes.items():
    manager.create_vector_index(index_name=index_name)
    print(f"Created index: {index_name}")
```

---

## Best Practices

### Indexing Best Practices

#### 1. Use Incremental Indexing
```env
# In .env
INCREMENTAL_INDEXING=true
```

Benefits:
- Faster re-indexing
- Reduced API costs
- Lower resource usage

#### 2. Optimize Chunk Size
```env
# For general documents
CHUNK_SIZE=1000
CHUNK_OVERLAP=200
CHUNK_SIZE=1500
CHUNK_OVERLAP=300
For short documents (less chunking)
CHUNK_SIZE=500
CHUNK_OVERLAP=100