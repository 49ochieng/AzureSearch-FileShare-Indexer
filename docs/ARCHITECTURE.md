# Architecture Documentation

Comprehensive technical architecture of AzureSearch FileShare Indexer.

---

## Table of Contents

- [System Overview](#system-overview)
- [Component Architecture](#component-architecture)
- [Data Flow](#data-flow)
- [Module Design](#module-design)
- [Search Architecture](#search-architecture)
- [Performance Considerations](#performance-considerations)
- [Security Architecture](#security-architecture)
- [Scalability](#scalability)
- [Extension Points](#extension-points)

---

## System Overview

### High-Level Architecture
```
┌─────────────────────────────────────────────────────────────────┐
│                      File Share Indexer                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐      │
│  │   Config     │───▶│   Indexer    │───▶│    Search    │      │
│  │   Manager    │    │   Pipeline   │    │   Client     │      │
│  └──────────────┘    └──────────────┘    └──────────────┘      │
│         │                    │                    │              │
│         │                    │                    │              │
│  ┌──────▼──────┐    ┌───────▼────────┐  ┌───────▼────────┐    │
│  │   Logger    │    │   Extractors   │  │  Index Mgr     │    │
│  └─────────────┘    └────────────────┘  └────────────────┘    │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
        ┌─────────────────────────────────────────┐
        │         Azure Services                   │
        ├─────────────────────────────────────────┤
        │  ┌──────────────┐  ┌──────────────┐    │
        │  │ Azure AI     │  │ Azure OpenAI │    │
        │  │ Search       │  │ (Embeddings) │    │
        │  └──────────────┘  └──────────────┘    │
        └─────────────────────────────────────────┘
```

### Deployment Topology
```
┌────────────────────────────────────────────────────────────────┐
│                    Deployment Options                           │
└────────────────────────────────────────────────────────────────┘

Option 1: Local Workstation
┌─────────────────┐
│  Windows/Linux  │
│   Workstation   │──┐
│                 │  │
│  File Share ◄───┤  │
│  Access         │  │
└─────────────────┘  │
                     │
                     ▼
            ┌──────────────┐
            │    Azure     │
            │   Services   │
            └──────────────┘

Option 2: Azure VM
┌─────────────────┐
│   Azure VM      │
│  (Windows/Linux)│──┐
│                 │  │
│  VNet Access    │  │
│  to File Share  │  │
└─────────────────┘  │
                     │
                     ▼
            ┌──────────────┐
            │    Azure     │
            │   Services   │
            └──────────────┘

Option 3: Azure Function (Serverless)
┌─────────────────┐
│ Azure Function  │
│  Timer Trigger  │──┐
│                 │  │
│  File Share     │  │
│  Integration    │  │
└─────────────────┘  │
                     │
                     ▼
            ┌──────────────┐
            │    Azure     │
            │   Services   │
            └──────────────┘

Option 4: Kubernetes
┌─────────────────┐
│   AKS Cluster   │
│                 │──┐
│  CronJob for    │  │
│  Indexing       │  │
│                 │  │
└─────────────────┘  │
                     │
                     ▼
            ┌──────────────┐
            │    Azure     │
            │   Services   │
            └──────────────┘
```

---

## Component Architecture

### Core Components

#### 1. Configuration Manager (`config/`)
```python
config/
├── __init__.py
├── settings.py      # Environment-based configuration
└── logger.py        # Centralized logging

Responsibilities:
- Load and validate environment variables
- Provide type-safe configuration access
- Manage environment-specific settings
- Handle secret masking for logging

Key Classes:
- Config: Static configuration class with validation
- setup_logger(): Initialize logging system
```

**Design Pattern**: Singleton pattern for configuration access
```python
# Configuration is loaded once at import
from config import Config

# Accessed statically throughout application
endpoint = Config.AZURE_SEARCH_ENDPOINT
```

#### 2. Content Extractors (`src/extractors.py`)
```python
ContentExtractor
├── extract_text()           # Main extraction method
├── extract_metadata()       # Metadata extraction
├── _extract_txt()          # Plain text
├── _extract_docx()         # Word documents
├── _extract_pdf()          # PDF documents
├── _extract_xlsx()         # Excel spreadsheets
└── get_statistics()        # Extraction stats

Responsibilities:
- Multi-format content extraction
- Metadata parsing
- Error handling for corrupted files
- Statistics tracking

Design Pattern: Strategy pattern for format-specific extraction
```

**Extension Architecture**:
```python
# Easy to add new formats
class ContentExtractor:
    EXTRACTORS = {
        '.txt': '_extract_txt',
        '.docx': '_extract_docx',
        '.pdf': '_extract_pdf',
        '.xlsx': '_extract_xlsx',
        # Add new formats here
        '.html': '_extract_html',
        '.md': '_extract_markdown',
    }
```

#### 3. File Indexer (`src/indexer.py`)
```python
FileIndexer
├── index_directory()        # Index entire directory
├── index_file()            # Index single file
├── _prepare_document()     # Prepare for upload
├── _should_index_file()    # Incremental check
└── get_statistics()        # Indexing stats

Responsibilities:
- Standard text indexing
- Batch processing
- Progress tracking
- Incremental indexing logic
- Statistics collection

Design Pattern: Template method for indexing pipeline
```

**Indexing Pipeline**:
```
File Input
    ↓
Should Index? (Incremental Check)
    ↓
Extract Metadata (ContentExtractor)
    ↓
Extract Content (ContentExtractor)
    ↓
Prepare Document (Transform)
    ↓
Batch Upload (Azure AI Search)
    ↓
Update Cache (Incremental)
    ↓
Statistics Update
```

#### 4. Vector Indexer (`src/vector_indexer.py`)
```python
VectorIndexer
├── index_directory()        # Index with embeddings
├── index_file()            # Index single file
├── chunk_text()            # Split into chunks
├── generate_embedding()    # Create embeddings
├── _prepare_documents()    # Prepare chunks
└── get_statistics()        # Indexing stats

Responsibilities:
- Text chunking with overlap
- Embedding generation
- Caching embeddings
- Batch processing chunks
- Retry logic for API calls

Design Pattern: Pipeline pattern with caching
```

**Vector Indexing Pipeline**:
```
File Input
    ↓
Should Index? (Incremental Check)
    ↓
Extract Content (ContentExtractor)
    ↓
Chunk Text (Tokenization)
    ↓
For Each Chunk:
    ↓
    Check Embedding Cache
    ↓
    Generate Embedding (Azure OpenAI)
    ↓
    Cache Embedding
    ↓
    Prepare Document
    ↓
Batch Upload All Chunks (Azure AI Search)
    ↓
Update Caches
    ↓
Statistics Update
```

#### 5. Search Client (`src/search.py`)
```python
SearchClient
├── search()                 # Keyword search
├── vector_search()         # Vector similarity
├── hybrid_search()         # Keyword + Vector
├── semantic_search()       # With reranking
├── filtered_search()       # With filters
├── generate_query_embedding() # Query embeddings
└── format_results()        # Display formatting

Responsibilities:
- Multiple search strategies
- Query embedding generation
- Result formatting
- Filter construction

Design Pattern: Strategy pattern for search types
```

**Search Type Comparison**:

| Search Type | Speed | Quality | Use Case |
|------------|-------|---------|----------|
| Keyword | Fastest | Good | Exact matches |
| Vector | Fast | Excellent | Semantic |
| Hybrid | Medium | Excellent | General purpose |
| Semantic | Slower | Best | Critical queries |

#### 6. Index Manager (`src/index_manager.py`)
```python
IndexManager
├── create_standard_index()  # Text index
├── create_vector_index()   # Vector index
├── delete_index()          # Remove index
├── list_indexes()          # List all indexes
└── get_index_statistics()  # Index stats

Responsibilities:
- Index lifecycle management
- Schema definition
- Index monitoring
- API interactions

Design Pattern: Factory pattern for index creation
```

---

## Data Flow

### Indexing Data Flow
```
┌──────────────────────────────────────────────────────────────┐
│                    Indexing Data Flow                         │
└──────────────────────────────────────────────────────────────┘

1. File Discovery
   ┌─────────────┐
   │ File Share  │
   │  Directory  │
   └──────┬──────┘
          │
          ▼
   ┌─────────────┐
   │   Walk      │
   │  Directory  │
   │   Tree      │
   └──────┬──────┘
          │
          ▼
   ┌─────────────┐
   │   Filter    │
   │ Extensions  │
   └──────┬──────┘
          │
          ▼

2. Content Processing
   ┌─────────────┐
   │  For Each   │
   │    File     │
   └──────┬──────┘
          │
          ├──────────────────────┬─────────────────────┐
          ▼                      ▼                     ▼
   ┌─────────────┐       ┌─────────────┐      ┌─────────────┐
   │  Extract    │       │  Extract    │      │  Get File   │
   │   Text      │       │  Metadata   │      │   Stats     │
   └──────┬──────┘       └──────┬──────┘      └──────┬──────┘
          │                      │                     │
          └──────────────────────┴─────────────────────┘
                                 │
                                 ▼

3. Vector Processing (Optional)
   ┌─────────────┐
   │   Chunk     │
   │    Text     │
   └──────┬──────┘
          │
          ▼
   ┌─────────────┐
   │  Generate   │
   │ Embeddings  │
   │ (OpenAI)    │
   └──────┬──────┘
          │
          ▼

4. Upload to Azure
   ┌─────────────┐
   │   Create    │
   │  Documents  │
   └──────┬──────┘
          │
          ▼
   ┌─────────────┐
   │   Batch     │
   │   Upload    │
   └──────┬──────┘
          │
          ▼
   ┌─────────────┐
   │  Azure AI   │
   │   Search    │
   └─────────────┘
```

### Search Data Flow
```
┌──────────────────────────────────────────────────────────────┐
│                     Search Data Flow                          │
└──────────────────────────────────────────────────────────────┘

1. Query Input
   ┌─────────────┐
   │    User     │
   │   Query     │
   └──────┬──────┘
          │
          ▼
   ┌─────────────┐
   │  Search     │
   │   Client    │
   └──────┬──────┘
          │
          ▼

2. Query Processing
   ┌─────────────┐
   │  Generate   │
   │  Embedding  │
   │  (OpenAI)   │
   └──────┬──────┘
          │
          ▼
   ┌─────────────┐
   │  Construct  │
   │   Query     │
   └──────┬──────┘
          │
          ▼

3. Search Execution
   ┌─────────────┐
   │  Azure AI   │
   │   Search    │
   │             │
   │  • Keyword  │
   │  • Vector   │
   │  • Hybrid   │
   │  • Semantic │
   └──────┬──────┘
          │
          ▼

4. Result Processing
   ┌─────────────┐
   │   Score     │
   │  Results    │
   └──────┬──────┘
          │
          ▼
   ┌─────────────┐
   │   Format    │
   │   Output    │
   └──────┬──────┘
          │
          ▼
   ┌─────────────┐
   │   Return    │
   │  to User    │
   └─────────────┘
```

---

## Module Design

### Package Structure
```
AzureSearch-FileShare-Indexer/
│
├── config/                          # Configuration Layer
│   ├── __init__.py
│   ├── settings.py                 # Configuration management
│   └── logger.py                   # Logging setup
│
├── src/                            # Core Business Logic
│   ├── __init__.py
│   ├── extractors.py              # Content extraction
│   │   └── ContentExtractor
│   │
│   ├── indexer.py                 # Standard indexing
│   │   └── FileIndexer
│   │
│   ├── vector_indexer.py          # Vector indexing
│   │   └── VectorIndexer
│   │
│   ├── search.py                  # Search operations
│   │   └── SearchClient
│   │
│   └── index_manager.py           # Index management
│       └── IndexManager
│
├── scripts/                        # CLI Scripts
│   ├── create_standard_index.py
│   ├── create_vector_index.py
│   ├── index_files.py
│   ├── index_files_vector.py
│   └── search_demo.py
│
└── tests/                          # Unit Tests
    ├── test_extractors.py
    ├── test_indexer.py
    ├── test_vector_indexer.py
    ├── test_search.py
    └── test_index_manager.py
```

### Dependency Graph
```
┌─────────────────────────────────────────────────────────────┐
│                     Dependency Graph                         │
└─────────────────────────────────────────────────────────────┘

scripts/
    ↓
src/ (Core Modules)
    ├── indexer ──────────┐
    ├── vector_indexer ───┤
    ├── search ───────────┼────→ Azure SDK
    ├── index_manager ────┤
    └── extractors ───────┘
         ↓
config/
    ├── settings
    └── logger
         ↓
    Environment Variables (.env)
```

### Design Principles

#### 1. Separation of Concerns

Each module has a single, well-defined responsibility:
```python
# Content extraction is separate from indexing
from src.extractors import ContentExtractor
from src.indexer import FileIndexer

extractor = ContentExtractor()
content = extractor.extract_text("file.pdf")

indexer = FileIndexer()
indexer.index_file("file.pdf")  # Uses extractor internally
```

#### 2. Dependency Injection
```python
# Indexer can use different extractors
class FileIndexer:
    def __init__(self, extractor=None):
        self.extractor = extractor or ContentExtractor()

# Custom extractor
class CustomExtractor(ContentExtractor):
    def extract_text(self, file_path):
        # Custom logic
        pass

indexer = FileIndexer(extractor=CustomExtractor())
```

#### 3. Configuration Management
```python
# Centralized configuration
from config import Config

# All modules use same config
class FileIndexer:
    def __init__(self):
        self.endpoint = Config.AZURE_SEARCH_ENDPOINT
        self.key = Config.AZURE_SEARCH_KEY
```

#### 4. Error Handling
```python
# Consistent error handling across modules
try:
    indexer.index_file(file_path)
except ExtractionError as e:
    logger.error(f"Extraction failed: {e}")
except Exception as e:
    logger.error(f"Unexpected error: {e}")
```

---

## Search Architecture

### Vector Search Implementation
```
┌─────────────────────────────────────────────────────────────┐
│              Vector Search Architecture                      │
└─────────────────────────────────────────────────────────────┘

Query: "employee benefits"
    ↓
┌─────────────────────┐
│  Query Embedding    │
│  Generation         │
│  (Azure OpenAI)     │
└──────────┬──────────┘
           │
           ▼
    [0.234, -0.567, 0.891, ...]  (3072 dimensions)
           │
           ▼
┌─────────────────────┐
│  Azure AI Search    │
│  Vector Search      │
│  (HNSW Algorithm)   │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  Find K-Nearest     │
│  Neighbors          │
│  (Cosine Similarity)│
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  Ranked Results     │
│  by Similarity      │
└─────────────────────┘
```

### HNSW Algorithm

Azure AI Search uses Hierarchical Navigable Small World (HNSW) for efficient vector search:
```
Layer 2: ●─────●         (Coarse navigation)
         │     │
Layer 1: ●─●─●─●─●       (Medium resolution)
         │ │ │ │ │
Layer 0: ●─●─●─●─●─●─●   (Fine-grained search)

Benefits:
- O(log N) search complexity
- High recall (>95%)
- Efficient for large datasets
- Trade-off: Index size vs. speed
```

### Hybrid Search Algorithm
```
Query: "employee benefits"
         │
         ├──────────────────────┬─────────────────────┐
         ▼                      ▼                     ▼
┌─────────────────┐    ┌─────────────────┐   ┌─────────────────┐
│  Keyword Search │    │  Vector Search  │   │  BM25 Scoring   │
│  (BM25)         │    │  (Cosine Sim)   │   │                 │
└────────┬────────┘    └────────┬────────┘   └────────┬────────┘
         │                      │                      │
         ├──────────────────────┴──────────────────────┘
         │
         ▼
┌─────────────────┐
│  Score Fusion   │
│  (RRF)          │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Ranked Results │
└─────────────────┘

Reciprocal Rank Fusion (RRF):
score = Σ (1 / (k + rank_i))
where k = 60 (constant)
```

### Semantic Ranking
```
Hybrid Search Results (Top 50)
         ↓
┌─────────────────────┐
│  Extract Captions   │
│  from Content       │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  Deep Learning      │
│  Reranker Model     │
│  (Azure Cognitive)  │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  Reranked Results   │
│  (Top K)            │
│  + Captions         │
└─────────────────────┘
```

---

## Performance Considerations

### Indexing Performance

#### Bottlenecks

1. **File I/O**
   - Reading files from network share
   - Mitigation: Local caching, parallel reading

2. **Content Extraction**
   - PDF parsing can be slow
   - Mitigation: Async processing, extraction timeouts

3. **Embedding Generation**
   - API rate limits (120K tokens/min typical)
   - Mitigation: Batching, caching, retries

4. **Network Upload**
   - Batch upload to Azure
   - Mitigation: Larger batches, compression

#### Optimization Strategies
```python
# 1. Batch Processing
documents = []
for file in files[:100]:  # Process in batches
    doc = prepare_document(file)
    documents.append(doc)

search_client.upload_documents(documents)  # Single API call

# 2. Parallel Processing
from concurrent.futures import ThreadPoolExecutor

with ThreadPoolExecutor(max_workers=4) as executor:
    futures = [executor.submit(index_file, f) for f in files]
    results = [f.result() for f in futures]

# 3. Caching
cache = {}
def get_embedding_cached(text):
    key = hash(text)
    if key not in cache:
        cache[key] = generate_embedding(text)
    return cache[key]
```

### Search Performance

#### Query Optimization
```python
# Fast: Specific field search
results = search_client.search(
    search_text="benefits",
    search_fields=["title", "chunk"],  # Limit fields
    select=["name", "filePath"],       # Return fewer fields
    top=5                              # Limit results
)

# Slow: Search all fields, return all data
results = search_client.search(
    search_text="benefits",
    top=1000
)
```

#### Index Optimization
```
Index Size vs. Speed Trade-offs:

Small Index (<1K docs):
- Fast indexing
- Fast search
- Low cost

Medium Index (1K-100K docs):
- Moderate indexing time
- Fast search with proper config
- Moderate cost

Large Index (>100K docs):
- Slower indexing
- Requires optimization
- Higher cost
- Consider partitioning
```

---

## Security Architecture

### Secret Management
```
┌─────────────────────────────────────────────────────────────┐
│                   Secret Management Flow                     │
└─────────────────────────────────────────────────────────────┘

Development:
.env file → Config class → Application

Production Option 1 (Azure Key Vault):
Azure Key Vault → Environment Variables → Config → Application

Production Option 2 (Managed Identity):
Azure Managed Identity → Azure Services (no keys needed)

Production Option 3 (Azure App Configuration):
Azure App Configuration → Config → Application
```

### Access Control
```python
# Role-Based Access Control (RBAC)

Indexer Service:
- Needs: Azure AI Search Admin Key
- Permissions: Read/Write to index

Search Service:
- Needs: Azure AI Search Query Key (read-only)
- Permissions: Read from index

Principle of Least Privilege:
- Use Query Keys for search-only applications
- Use Admin Keys only for indexing
- Rotate keys regularly
```

### Data Protection
```
Data At Rest:
├── Azure AI Search: Encrypted by default (AES-256)
├── Azure OpenAI: Encrypted by default
└── Local Cache: File system encryption (BitLocker/LUKS)

Data In Transit:
├── HTTPS/TLS 1.2+ for all API calls
├── Encrypted network connections
└── Certificate validation
```

---

## Scalability

### Horizontal Scaling
```
┌─────────────────────────────────────────────────────────────┐
│                   Horizontal Scaling                         │
└─────────────────────────────────────────────────────────────┘

Single Instance:
┌──────────────┐
│   Indexer    │──→ File Share
└──────────────┘

Multiple Instances (Partitioned):
┌──────────────┐
│  Indexer 1   │──→ File Share /dept1/
└──────────────┘

┌──────────────┐
│  Indexer 2   │──→ File Share /dept2/
└──────────────┘

┌──────────────┐
│  Indexer 3   │──→ File Share /dept3/
└──────────────┘

All instances write to same Azure AI Search index
```

### Vertical Scaling
```
Azure AI Search Tiers:

Free:
- 50 MB storage
- No vector search
- Development only

Basic:
- 2 GB storage
- 15 indexes
- Vector search supported
- $75/month

Standard S1:
- 25 GB storage
- 50 indexes
- Better performance
- $250/month

Standard S2/S3:
- More replicas
- More partitions
- Enterprise scale
```

### Performance Scaling
```python
# Configuration for different scales

Small Scale (<10K docs):
BATCH_SIZE=100
MAX_WORKERS=4
CHUNK_SIZE=1000

Medium Scale (10K-100K docs):
BATCH_SIZE=200
MAX_WORKERS=8
CHUNK_SIZE=1000
CACHE_EMBEDDINGS=true

Large Scale (>100K docs):
BATCH_SIZE=500
MAX_WORKERS=16
CHUNK_SIZE=800
CACHE_EMBEDDINGS=true
# Consider index partitioning
```

---

## Extension Points

### Adding New File Formats
```python
# 1. Add to ContentExtractor

class ContentExtractor:
    EXTRACTORS = {
        '.txt': '_extract_txt',
        '.html': '_extract_html',  # New format
    }
    
    def _extract_html(self, file_path: str) -> str:
        """Extract text from HTML file"""
        from bs4 import BeautifulSoup
        
        with open(file_path, 'r') as f:
            soup = BeautifulSoup(f, 'html.parser')
            return soup.get_text()

# 2. Update configuration
SUPPORTED_EXTENSIONS=.txt,.docx,.pdf,.html
```

### Custom Metadata Extractors
```python
# Create custom extractor
class EnhancedExtractor(ContentExtractor):
    def extract_metadata(self, file_path):
        metadata = super().extract_metadata(file_path)
        
        # Add custom metadata
        metadata['custom_field'] = self._extract_custom(file_path)
        
        return metadata
    
    def _extract_custom(self, file_path):
        # Custom logic
        return "custom_value"

# Use in indexer
indexer = FileIndexer()
indexer.extractor = EnhancedExtractor()
```

### Custom Search Strategies
```python
# Implement custom search logic
class CustomSearchClient(SearchClient):
    def intelligent_search(self, query: str):
        # Step 1: Try vector search
        results = self.vector_search(query, top=5)
        
        # Step 2: If low scores, fall back to keyword
        if all(r['@search.score'] < 0.7 for r in results):
            results = self.search(query, top=5)
        
        # Step 3: Custom post-processing
        results = self._boost_recent_docs(results)
        
        return results
    
    def _boost_recent_docs(self, results):
        # Boost documents from last 30 days
        from datetime import datetime, timedelta
        cutoff = datetime.now() - timedelta(days=30)
        
        for result in results:
            mod_date = datetime.fromisoformat(result['modifiedDateTime'].replace('Z', '+00:00'))
            if mod_date > cutoff:
                result['@search.score'] *= 1.2
        
        return sorted(results, key=lambda r: r['@search.score'], reverse=True)
```

### Plugin Architecture
```python
# Define plugin interface
class IndexerPlugin:
    def before_index(self, file_path: str) -> bool:
        """Return False to skip indexing"""
        return True
    
    def after_index(self, file_path: str, success: bool):
        """Post-processing after indexing"""
        pass

# Implement plugin
class AuditPlugin(IndexerPlugin):
    def after_index(self, file_path, success):
        with open('audit.log', 'a') as f:
            f.write(f"{file_path},{success},{datetime.now()}\n")

# Use plugins
class PluggableIndexer(FileIndexer):
    def __init__(self, plugins=None):
        super().__init__()
        self.plugins = plugins or []
    
    def index_file(self, file_path):
        # Before hooks
        for plugin in self.plugins:
            if not plugin.before_index(file_path):
                return False
        
        # Index
        success = super().index_file(file_path)
        
        # After hooks
        for plugin in self.plugins:
            plugin.after_index(file_path, success)
        
        return success

# Usage
indexer = PluggableIndexer(plugins=[AuditPlugin()])
```

---

## Monitoring and Observability

### Logging Architecture
```
┌─────────────────────────────────────────────────────────────┐
│                    Logging Architecture                      │
└─────────────────────────────────────────────────────────────┘

Application Logs
       ↓
┌──────────────┐
│   Loguru     │
│   Logger     │
└──────┬───────┘
       │
       ├──────────────┬──────────────┐
       ▼              ▼              ▼
┌──────────┐   ┌──────────┐   ┌──────────────┐
│ Console  │   │   File   │   │ Application  │
│  Output  │   │  (Rotate)│   │   Insights   │
└──────────┘   └──────────┘   └──────────────┘
```

### Metrics Collection
```python
# Track important metrics
class MetricsCollector:
    def __init__(self):
        self.metrics = {
            'files_processed': 0,
            'chunks_created': 0,
            'api_calls': 0,
            'errors': 0,
            'total_size_mb': 0,
        }
    
    def increment(self, metric: str, value: int