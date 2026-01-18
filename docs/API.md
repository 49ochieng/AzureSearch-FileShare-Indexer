# API Reference

Complete API documentation for all modules and classes.

---

## Table of Contents

- [Configuration Module](#configuration-module)
- [Content Extractors](#content-extractors)
- [File Indexer](#file-indexer)
- [Vector Indexer](#vector-indexer)
- [Search Client](#search-client)
- [Index Manager](#index-manager)
- [Error Classes](#error-classes)

---

## Configuration Module

### `config.Config`

Central configuration class with environment variable management.

#### Class Variables

| Variable | Type | Description | Required |
|----------|------|-------------|----------|
| `AZURE_SEARCH_ENDPOINT` | str | Azure AI Search service URL | ✅ |
| `AZURE_SEARCH_KEY` | str | Admin API key | ✅ |
| `AZURE_SEARCH_INDEX_NAME` | str | Standard index name | ✅ |
| `AZURE_SEARCH_VECTOR_INDEX_NAME` | str | Vector index name | ✅ |
| `AZURE_OPENAI_ENDPOINT` | str | Azure OpenAI endpoint | For vector search |
| `AZURE_OPENAI_KEY` | str | Azure OpenAI API key | For vector search |
| `AZURE_OPENAI_EMBEDDING_DEPLOYMENT` | str | Embedding model deployment name | For vector search |
| `FILE_SHARE_PATH` | str | Path to file share | ✅ |
| `SUPPORTED_EXTENSIONS` | List[str] | File extensions to index | Optional |
| `CHUNK_SIZE` | int | Tokens per chunk | Optional |
| `CHUNK_OVERLAP` | int | Overlap between chunks | Optional |
| `BATCH_SIZE` | int | Upload batch size | Optional |
| `MAX_WORKERS` | int | Concurrent workers | Optional |
| `INCREMENTAL_INDEXING` | bool | Enable incremental indexing | Optional |
| `CACHE_EMBEDDINGS` | bool | Cache embeddings | Optional |
| `LOG_LEVEL` | str | Logging level | Optional |

#### Methods

##### `validate(require_openai: bool = False) -> bool`

Validate configuration settings.

**Parameters:**
- `require_openai` (bool): Whether to require OpenAI configuration

**Returns:**
- `bool`: True if valid

**Raises:**
- `ConfigValidationError`: If validation fails

**Example:**
```python
from config import Config

# Basic validation
Config.validate()

# Validate with OpenAI requirements
Config.validate(require_openai=True)
```

##### `print_config(mask_secrets: bool = True) -> None`

Print current configuration.

**Parameters:**
- `mask_secrets` (bool): Whether to mask sensitive values

**Example:**
```python
Config.print_config()
```

##### `to_dict(mask_secrets: bool = True) -> Dict[str, Any]`

Convert configuration to dictionary.

**Parameters:**
- `mask_secrets` (bool): Whether to mask sensitive values

**Returns:**
- `Dict[str, Any]`: Configuration dictionary

**Example:**
```python
config_dict = Config.to_dict()
```

---

## Content Extractors

### `src.extractors.ContentExtractor`

Extract text and metadata from various file formats.

#### Methods

##### `extract_text(file_path: str) -> str`

Extract text content from a file.

**Parameters:**
- `file_path` (str): Path to the file

**Returns:**
- `str`: Extracted text content

**Raises:**
- `ExtractionError`: If extraction fails

**Supported Formats:**
- `.txt` - Plain text
- `.docx` - Microsoft Word
- `.pdf` - PDF documents
- `.xlsx` - Microsoft Excel
- `.md` - Markdown

**Example:**
```python
from src.extractors import ContentExtractor

extractor = ContentExtractor()
content = extractor.extract_text("/path/to/document.pdf")
print(f"Extracted {len(content)} characters")
```

##### `extract_metadata(file_path: str) -> Dict[str, Any]`

Extract metadata from a file.

**Parameters:**
- `file_path` (str): Path to the file

**Returns:**
- `Dict[str, Any]`: Metadata dictionary

**Metadata Fields:**
- `file_name` (str): File name
- `file_path` (str): Full file path
- `file_extension` (str): File extension
- `file_size_bytes` (int): File size in bytes
- `file_size_mb` (float): File size in MB
- `created_time` (str): Creation timestamp (ISO format)
- `modified_time` (str): Modification timestamp (ISO format)
- `accessed_time` (str): Access timestamp (ISO format)
- `owner` (str): File owner (Windows only)
- `document_title` (str): Document title (if available)
- `document_author` (str): Document author (if available)
- `document_keywords` (str): Document keywords (if available)

**Example:**
```python
metadata = extractor.extract_metadata("/path/to/document.docx")
print(f"Title: {metadata.get('document_title')}")
print(f"Author: {metadata.get('document_author')}")
print(f"Size: {metadata['file_size_mb']:.2f} MB")
```

##### `get_statistics() -> Dict[str, Any]`

Get extraction statistics.

**Returns:**
- `Dict[str, Any]`: Statistics dictionary

**Statistics Fields:**
- `total_extracted` (int): Total files extracted
- `failed` (int): Failed extractions
- `by_type` (Dict[str, int]): Count by file type

**Example:**
```python
stats = extractor.get_statistics()
print(f"Extracted: {stats['total_extracted']}")
print(f"Failed: {stats['failed']}")
```

##### `reset_statistics() -> None`

Reset extraction statistics.

**Example:**
```python
extractor.reset_statistics()
```

---

## File Indexer

### `src.indexer.FileIndexer`

Index files to Azure AI Search with standard text search.

#### Constructor

##### `__init__(index_name: Optional[str] = None)`

Initialize file indexer.

**Parameters:**
- `index_name` (str, optional): Name of the index (defaults to config value)

**Example:**
```python
from src.indexer import FileIndexer

# Use default index from config
indexer = FileIndexer()

# Use custom index
indexer = FileIndexer(index_name="custom-index")
```

#### Methods

##### `index_file(file_path: str) -> bool`

Index a single file.

**Parameters:**
- `file_path` (str): Path to the file

**Returns:**
- `bool`: True if successful, False otherwise

**Example:**
```python
success = indexer.index_file("/path/to/document.pdf")
if success:
    print("Document indexed successfully")
```

##### `index_directory(directory_path: Optional[str] = None, recursive: bool = True, show_progress: bool = True) -> Dict[str, Any]`

Index all supported files in a directory.

**Parameters:**
- `directory_path` (str, optional): Path to directory (defaults to config value)
- `recursive` (bool): Whether to index subdirectories
- `show_progress` (bool): Whether to show progress bar

**Returns:**
- `Dict[str, Any]`: Statistics dictionary with keys:
  - `total_files` (int): Total files processed
  - `successful` (int): Successfully indexed
  - `failed` (int): Failed to index
  - `skipped` (int): Skipped (unchanged)
  - `total_size_mb` (float): Total size processed
  - `start_time` (datetime): Start timestamp
  - `end_time` (datetime): End timestamp

**Example:**
```python
stats = indexer.index_directory(
    directory_path="/path/to/documents",
    recursive=True,
    show_progress=True
)

print(f"Indexed {stats['successful']} files")
print(f"Failed: {stats['failed']}")
print(f"Skipped: {stats['skipped']}")
```

##### `get_statistics() -> Dict[str, Any]`

Get indexing statistics.

**Returns:**
- `Dict[str, Any]`: Statistics dictionary

**Example:**
```python
stats = indexer.get_statistics()
print(f"Total files: {stats['total_files']}")
```

---

## Vector Indexer

### `src.vector_indexer.VectorIndexer`

Index files with vector embeddings for semantic search.

#### Constructor

##### `__init__(index_name: Optional[str] = None)`

Initialize vector indexer.

**Parameters:**
- `index_name` (str, optional): Name of the vector index

**Example:**
```python
from src.vector_indexer import VectorIndexer

indexer = VectorIndexer()
```

#### Methods

##### `chunk_text(text: str, chunk_size: Optional[int] = None, overlap: Optional[int] = None) -> List[str]`

Split text into overlapping chunks.

**Parameters:**
- `text` (str): Text to chunk
- `chunk_size` (int, optional): Size in tokens (defaults to config)
- `overlap` (int, optional): Overlap in tokens (defaults to config)

**Returns:**
- `List[str]`: List of text chunks

**Example:**
```python
text = "Long document text here..."
chunks = indexer.chunk_text(text, chunk_size=500, overlap=100)
print(f"Created {len(chunks)} chunks")
```

##### `generate_embedding(text: str, use_cache: bool = True) -> Optional[List[float]]`

Generate embedding for text using Azure OpenAI.

**Parameters:**
- `text` (str): Text to embed
- `use_cache` (bool): Whether to use cached embeddings

**Returns:**
- `Optional[List[float]]`: Embedding vector (3072 dimensions for text-embedding-3-large)

**Example:**
```python
embedding = indexer.generate_embedding("sample text")
if embedding:
    print(f"Generated embedding with {len(embedding)} dimensions")
```

##### `index_file(file_path: str) -> int`

Index a single file with embeddings.

**Parameters:**
- `file_path` (str): Path to the file

**Returns:**
- `int`: Number of chunks successfully indexed

**Example:**
```python
chunks = indexer.index_file("/path/to/document.pdf")
print(f"Indexed {chunks} chunks")
```

##### `index_directory(directory_path: Optional[str] = None, recursive: bool = True, show_progress: bool = True) -> Dict[str, Any]`

Index all supported files in a directory.

**Parameters:**
- `directory_path` (str, optional): Path to directory
- `recursive` (bool): Whether to index subdirectories
- `show_progress` (bool): Whether to show progress bar

**Returns:**
- `Dict[str, Any]`: Statistics dictionary with keys:
  - `total_files` (int): Total files found
  - `successful_files` (int): Successfully indexed
  - `failed_files` (int): Failed to index
  - `total_chunks` (int): Total chunks created
  - `total_embeddings` (int): Total embeddings generated
  - `embedding_api_calls` (int): OpenAI API calls made
  - `skipped` (int): Files skipped
  - `total_size_mb` (float): Total size processed

**Example:**
```python
stats = indexer.index_directory("/path/to/documents")
print(f"Files: {stats['successful_files']}")
print(f"Chunks: {stats['total_chunks']}")
print(f"API calls: {stats['embedding_api_calls']}")
```

---

## Search Client

### `src.search.SearchClient`

Advanced search client for indexed documents.

#### Constructor

##### `__init__(index_name: Optional[str] = None, use_vector_index: bool = True)`

Initialize search client.

**Parameters:**
- `index_name` (str, optional): Index name
- `use_vector_index` (bool): Whether to use vector-enabled index

**Example:**
```python
from src.search import SearchClient

# Vector search
search = SearchClient()

# Standard text search only
search = SearchClient(use_vector_index=False)
```

#### Methods

##### `search(query: str, top: Optional[int] = None, filter_expr: Optional[str] = None, select: Optional[List[str]] = None) -> List[Dict[str, Any]]`

Basic keyword search.

**Parameters:**
- `query` (str): Search query
- `top` (int, optional): Number of results (defaults to 5)
- `filter_expr` (str, optional): OData filter expression
- `select` (List[str], optional): Fields to return

**Returns:**
- `List[Dict[str, Any]]`: Search results

**Example:**
```python
results = search.search("employee benefits", top=10)
for result in results:
    print(f"{result['name']}: {result['@search.score']}")
```

##### `vector_search(query: str, top: Optional[int] = None, filter_expr: Optional[str] = None, select: Optional[List[str]] = None) -> List[Dict[str, Any]]`

Pure vector similarity search.

**Parameters:**
- `query` (str): Search query
- `top` (int, optional): Number of results
- `filter_expr` (str, optional): OData filter
- `select` (List[str], optional): Fields to return

**Returns:**
- `List[Dict[str, Any]]`: Search results

**Example:**
```python
results = search.vector_search("team collaboration tools")
```

##### `hybrid_search(query: str, top: Optional[int] = None, filter_expr: Optional[str] = None, select: Optional[List[str]] = None) -> List[Dict[str, Any]]`

Hybrid search (keyword + vector).

**Parameters:**
- `query` (str): Search query
- `top` (int, optional): Number of results
- `filter_expr` (str, optional): OData filter
- `select` (List[str], optional): Fields to return

**Returns:**
- `List[Dict[str, Any]]`: Search results

**Example:**
```python
results = search.hybrid_search("quarterly financial reports", top=10)
```

##### `semantic_search(query: str, top: Optional[int] = None, filter_expr: Optional[str] = None, select: Optional[List[str]] = None) -> List[Dict[str, Any]]`

Semantic search with intelligent reranking.

**Parameters:**
- `query` (str): Search query
- `top` (int, optional): Number of results
- `filter_expr` (str, optional): OData filter
- `select` (List[str], optional): Fields to return

**Returns:**
- `List[Dict[str, Any]]`: Search results with semantic scores

**Example:**
```python
results = search.semantic_search("company policies on remote work")
for result in results:
    print(f"Score: {result['@search.score']:.4f}")
    if '@search.reranker_score' in result:
        print(f"Reranker: {result['@search.reranker_score']:.4f}")
```

##### `filtered_search(query: str, extension: Optional[str] = None, date_from: Optional[str] = None, date_to: Optional[str] = None, author: Optional[str] = None, top: Optional[int] = None, search_type: str = "hybrid") -> List[Dict[str, Any]]`

Search with metadata filters.

**Parameters:**
- `query` (str): Search query
- `extension` (str, optional): File extension filter (e.g., ".pdf")
- `date_from` (str, optional): Modified date from (ISO format)
- `date_to` (str, optional): Modified date to (ISO format)
- `author` (str, optional): Author filter
- `top` (int, optional): Number of results
- `search_type` (str): Type of search ("keyword", "vector", "hybrid", "semantic")

**Returns:**
- `List[Dict[str, Any]]`: Filtered search results

**Example:**
```python
results = search.filtered_search(
    query="contracts",
    extension=".pdf",
    date_from="2024-01-01T00:00:00Z",
    search_type="hybrid"
)
```

##### `format_results(results: List[Dict[str, Any]], show_scores: bool = True) -> str`

Format search results for display.

**Parameters:**
- `results` (List[Dict[str, Any]]): Search results
- `show_scores` (bool): Whether to show relevance scores

**Returns:**
- `str`: Formatted string

**Example:**
```python
results = search.hybrid_search("employee benefits")
print(search.format_results(results))
```

---

## Index Manager

### `src.index_manager.IndexManager`

Manage Azure AI Search indexes.

#### Constructor

##### `__init__()`

Initialize index manager.

**Example:**
```python
from src.index_manager import IndexManager

manager = IndexManager()
```

#### Methods

##### `create_standard_index(index_name: Optional[str] = None) -> bool`

Create a standard text search index.

**Parameters:**
- `index_name` (str, optional): Name of the index

**Returns:**
- `bool`: True if successful

**Example:**
```python
success = manager.create_standard_index("my-text-index")
```

##### `create_vector_index(index_name: Optional[str] = None, embedding_dimensions: Optional[int] = None) -> bool`

Create a vector-enabled index with semantic configuration.

**Parameters:**
- `index_name` (str, optional): Name of the index
- `embedding_dimensions` (int, optional): Vector dimensions (3072 or 1536)

**Returns:**
- `bool`: True if successful

**Example:**
```python
success = manager.create_vector_index(
    index_name="my-vector-index",
    embedding_dimensions=3072
)
```

##### `delete_index(index_name: str) -> bool`

Delete an index.

**Parameters:**
- `index_name` (str): Name of the index to delete

**Returns:**
- `bool`: True if successful

**Example:**
```python
manager.delete_index("old-index")
```

##### `list_indexes() -> List[str]`

List all indexes in the search service.

**Returns:**
- `List[str]`: List of index names

**Example:**
```python
indexes = manager.list_indexes()
print(f"Found {len(indexes)} indexes:")
for index in indexes:
    print(f"  - {index}")
```

##### `get_index_statistics(index_name: str) -> Optional[Dict[str, Any]]`

Get statistics for an index.

**Parameters:**
- `index_name` (str): Name of the index

**Returns:**
- `Optional[Dict[str, Any]]`: Statistics dictionary or None

**Statistics Fields:**
- `documentCount` (int): Number of documents
- `storageSize` (int): Storage size in bytes

**Example:**
```python
stats = manager.get_index_statistics("fileshare-vector-documents")
if stats:
    print(f"Documents: {stats['documentCount']}")
    print(f"Storage: {stats['storageSize']} bytes")
```

---

## Error Classes

### `src.extractors.ExtractionError`

Raised when content extraction fails.

**Example:**
```python
from src.extractors import ExtractionError

try:
    content = extractor.extract_text("file.xyz")
except ExtractionError as e:
    print(f"Extraction failed: {e}")
```

### `config.settings.ConfigValidationError`

Raised when configuration validation fails.

**Example:**
```python
from config import Config, ConfigValidationError

try:
    Config.validate(require_openai=True)
except ConfigValidationError as e:
    print(f"Configuration error: {e}")
```

---

## OData Filter Syntax

Azure AI Search uses OData filter syntax for filtering.

### Common Operators

| Operator | Description | Example |
|----------|-------------|---------|
| `eq` | Equals | `extension eq '.pdf'` |
| `ne` | Not equals | `extension ne '.tmp'` |
| `gt` | Greater than | `size gt 1000000` |
| `lt` | Less than | `size lt 10000000` |
| `ge` | Greater or equal | `modifiedDateTime ge 2024-01-01T00:00:00Z` |
| `le` | Less or equal | `modifiedDateTime le 2024-12-31T23:59:59Z` |
| `and` | Logical AND | `extension eq '.pdf' and size gt 1000000` |
| `or` | Logical OR | `extension eq '.pdf' or extension eq '.docx'` |
| `not` | Logical NOT | `not (extension eq '.tmp')` |

### Functions

| Function | Description | Example |
|----------|-------------|---------|
| `search.in()` | Value in list | `search.in(author, 'John,Jane', ',')` |
| `search.ismatch()` | Full-text match | `search.ismatch('benefits', 'content')` |

### Examples
```python
# PDF files larger than 1MB
filter_expr = "extension eq '.pdf' and size gt 1000000"

# Modified in 2024
filter_expr = "modifiedDateTime ge 2024-01-01T00:00:00Z and modifiedDateTime lt 2025-01-01T00:00:00Z"

# Multiple authors
filter_expr = "search.in(createdBy, 'John Doe,Jane Smith', ',')"

# Complex filter
filter_expr = "(extension eq '.pdf' or extension eq '.docx') and size lt 10000000 and modifiedDateTime ge 2024-01-01T00:00:00Z"
```

---

## Response Fields

### Standard Search Result Fields

| Field | Type | Description |
|-------|------|-------------|
| `id` | str | Unique document ID |
| `name` | str | File name |
| `title` | str | Document title |
| `filePath` | str | Full file path |
| `extension` | str | File extension |
| `size` | int | File size in bytes |
| `createdDateTime` | str | Creation timestamp |
| `modifiedDateTime` | str | Modification timestamp |
| `createdBy` | str | File creator |
| `lastModifiedBy` | str | Last modifier |
| `content` | str | Full content (truncated) |
| `@search.score` | float | Relevance score |

### Vector Search Additional Fields

| Field | Type | Description |
|-------|------|-------------|
| `chunk` | str | Text chunk |
| `chunkNumber` | int | Chunk index |
| `totalChunks` | int | Total chunks for file |
| `contentVector` | List[float] | Embedding vector |

### Semantic Search Additional Fields

| Field | Type | Description |
|-------|------|-------------|
| `@search.reranker_score` | float | Semantic relevance score |
| `@search.captions` | List[Dict] | Extracted captions |
| `@search.answers` | List[Dict] | Direct answers |

---

## Code Examples

### Complete Indexing Example
```python
from src.vector_indexer import VectorIndexer
from config import Config

# Configure
Config.FILE_SHARE_PATH = "\\\\SERVER\\Documents"

# Initialize
indexer = VectorIndexer()

# Index
stats = indexer.index_directory(
    recursive=True,
    show_progress=True
)

# Results
print(f"Indexed {stats['successful_files']} files")
print(f"Created {stats['total_chunks']} chunks")
print(f"API calls: {stats['embedding_api_calls']}")
```

### Complete Search Example
```python
from src.search import SearchClient

# Initialize
search = SearchClient()

# Search
results = search.hybrid_search(
    query="employee benefits",
    top=10
)

# Display
for i, result in enumerate(results, 1):
    print(f"{i}. {result['name']}")
    print(f"   Score: {result['@search.score']:.4f}")
    print(f"   Path: {result['filePath']}")
    print()
```

### Complete Management Example
```python
from src.index_manager import IndexManager

# Initialize
manager = IndexManager()

# Create index
manager.create_vector_index(
    index_name="my-documents",
    embedding_dimensions=3072
)

# List indexes
indexes = manager.list_indexes()
print(f"Found {len(indexes)} indexes")

# Get statistics
stats = manager.get_index_statistics("my-documents")
print(f"Documents: {stats['documentCount']}")

# Delete (use with caution!)
# manager.delete_index("old-index")
```

---

For more examples, see the `examples/` directory.