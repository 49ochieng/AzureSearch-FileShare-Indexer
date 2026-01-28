# Performance Optimization Guide

This guide provides strategies and best practices for optimizing the performance of AzureSearch FileShare Indexer.

## Table of Contents

- [Quick Wins](#quick-wins)
- [Configuration Tuning](#configuration-tuning)
- [Azure Service Optimization](#azure-service-optimization)
- [Code-Level Optimizations](#code-level-optimizations)
- [Monitoring & Profiling](#monitoring--profiling)
- [Troubleshooting Performance Issues](#troubleshooting-performance-issues)

---

## Quick Wins

### 1. Enable Embedding Cache

Reduce API calls and costs by caching embeddings:

```env
ENABLE_EMBEDDING_CACHE=true
CACHE_DIR=./cache
```

**Impact**: 
- Reduces OpenAI API calls by 70-90%
- Saves $10-100 per run (depending on corpus size)
- 3-5x faster re-indexing

### 2. Increase Batch Size

Process more documents in parallel:

```env
BATCH_SIZE=50  # Default is 10
```

**Impact**:
- 2-3x faster indexing
- Better throughput for large document sets

**Considerations**:
- Higher memory usage
- May hit rate limits more quickly

### 3. Optimize Chunk Size

Balance context vs. processing speed:

```env
MAX_CHUNK_SIZE=800  # Default is 1000
CHUNK_OVERLAP=100   # Default is 200
```

**Impact**:
- Fewer chunks = faster processing
- Smaller overlap = less redundant embeddings

### 4. Use Incremental Indexing

Only process changed files:

```env
ENABLE_INCREMENTAL_INDEXING=true
```

**Impact**:
- 10-100x faster subsequent runs
- Only processes new/modified files

---

## Configuration Tuning

### Batch Processing

Tune based on your Azure tier and document size:

| Scenario | BATCH_SIZE | MAX_WORKERS |
|----------|-----------|-------------|
| Small docs (<100KB) | 50-100 | 4-8 |
| Medium docs (100KB-1MB) | 20-50 | 2-4 |
| Large docs (>1MB) | 10-20 | 1-2 |
| Azure Free Tier | 5-10 | 1 |
| Azure Standard | 50-100 | 4-8 |

### Chunking Strategy

Optimize for your use case:

**For Q&A / RAG:**
```env
MAX_CHUNK_SIZE=500
CHUNK_OVERLAP=50
```
- Smaller chunks for precise answers
- Less overlap to reduce duplication

**For Document Retrieval:**
```env
MAX_CHUNK_SIZE=1500
CHUNK_OVERLAP=300
```
- Larger chunks for more context
- More overlap to preserve continuity

**For Mixed Use:**
```env
MAX_CHUNK_SIZE=1000
CHUNK_OVERLAP=200
```
- Balanced approach (default)

### File Filtering

Skip unnecessary files:

```env
SUPPORTED_EXTENSIONS=.docx,.pdf  # Only process specific types
IGNORE_PATTERNS=temp,draft,test  # Skip files matching patterns
MAX_FILE_SIZE_MB=10              # Skip files larger than 10MB
```

### Concurrency Limits

Prevent overwhelming Azure services:

```env
MAX_CONCURRENT_REQUESTS=10  # Max parallel API calls
REQUEST_TIMEOUT=30          # Timeout per request (seconds)
RETRY_MAX_ATTEMPTS=3        # Max retry attempts
RETRY_BACKOFF_FACTOR=2      # Exponential backoff multiplier
```

---

## Azure Service Optimization

### 1. Azure Search Tier Selection

Choose appropriate tier:

| Tier | Use Case | Indexing Speed | Cost/Month |
|------|----------|----------------|------------|
| Free | Dev/Testing | 1-2 docs/sec | $0 |
| Basic | Small projects | 3-5 docs/sec | ~$75 |
| Standard S1 | Production | 10-15 docs/sec | ~$250 |
| Standard S2 | Large-scale | 25-40 docs/sec | ~$1,000 |
| Standard S3 | Enterprise | 50+ docs/sec | ~$4,000 |

**Recommendation**: Start with Basic, scale to S1 for production.

### 2. Replica & Partition Configuration

For Azure Search:

**Development:**
```
Replicas: 1
Partitions: 1
```

**Production (High Availability):**
```
Replicas: 3  # For 99.9% SLA
Partitions: 1-3  # Based on data size
```

**Production (High Throughput):**
```
Replicas: 2
Partitions: 2-6  # More partitions = better indexing speed
```

### 3. Azure OpenAI Optimization

**TPM (Tokens Per Minute) Limits:**

| Model | Tier | TPM Limit | Recommended BATCH_SIZE |
|-------|------|-----------|------------------------|
| ada-002 | Free | 60K | 5-10 |
| ada-002 | Standard | 240K | 30-50 |
| ada-002 | Enterprise | 1M+ | 100+ |

**Rate Limiting Strategy:**

```python
# Implement exponential backoff
from tenacity import retry, wait_exponential, stop_after_attempt

@retry(
    wait=wait_exponential(multiplier=1, min=4, max=60),
    stop=stop_after_attempt(5)
)
def call_openai_api():
    # Your API call
    pass
```

### 4. Network Optimization

**Use Azure Private Link:**
- Reduces latency by 20-50ms
- More secure
- Consistent performance

**Enable Accelerated Networking:**
- Available on Azure VMs
- Reduces CPU utilization
- Lower latency

---

## Code-Level Optimizations

### 1. Parallel Processing

Use asyncio for I/O-bound operations:

```python
import asyncio
from azure.search.documents.aio import SearchClient

async def index_documents_async(documents):
    async with SearchClient(...) as client:
        tasks = [client.upload_documents([doc]) for doc in batches]
        await asyncio.gather(*tasks)

# Run async
asyncio.run(index_documents_async(documents))
```

**Impact**: 2-4x faster for I/O operations

### 2. Efficient Text Extraction

Use optimized libraries:

```python
# Slow: PyPDF2
from PyPDF2 import PdfReader

# Fast: pdfplumber (3-5x faster)
import pdfplumber

with pdfplumber.open(file_path) as pdf:
    text = "\n".join([page.extract_text() for page in pdf.pages])
```

### 3. Memory Management

Process large files in chunks:

```python
def process_large_file(file_path, chunk_size=1024*1024):  # 1MB chunks
    with open(file_path, 'rb') as f:
        while chunk := f.read(chunk_size):
            process_chunk(chunk)
```

### 4. Vectorization Optimization

Batch embed multiple texts:

```python
# Inefficient: One at a time
for text in texts:
    embedding = openai.embeddings.create(input=text)

# Efficient: Batch
embeddings = openai.embeddings.create(
    input=texts[:100]  # Batch of 100
)
```

**Impact**: 5-10x faster embedding generation

### 5. Database-Style Caching

Use SQLite for embedding cache:

```python
import sqlite3
import hashlib

class EmbeddingCache:
    def __init__(self, db_path='embeddings.db'):
        self.conn = sqlite3.connect(db_path)
        self.conn.execute('''
            CREATE TABLE IF NOT EXISTS embeddings (
                text_hash TEXT PRIMARY KEY,
                embedding BLOB
            )
        ''')
    
    def get(self, text):
        hash_key = hashlib.md5(text.encode()).hexdigest()
        result = self.conn.execute(
            'SELECT embedding FROM embeddings WHERE text_hash=?',
            (hash_key,)
        ).fetchone()
        return pickle.loads(result[0]) if result else None
    
    def set(self, text, embedding):
        hash_key = hashlib.md5(text.encode()).hexdigest()
        self.conn.execute(
            'INSERT OR REPLACE INTO embeddings VALUES (?, ?)',
            (hash_key, pickle.dumps(embedding))
        )
        self.conn.commit()
```

---

## Monitoring & Profiling

### 1. Enable Performance Logging

```env
LOG_LEVEL=DEBUG
LOG_PERFORMANCE_METRICS=true
```

```python
import time
from functools import wraps

def timing_decorator(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = func(*args, **kwargs)
        elapsed = time.perf_counter() - start
        logger.info(f"{func.__name__} took {elapsed:.2f}s")
        return result
    return wrapper

@timing_decorator
def index_document(doc):
    # Your code
    pass
```

### 2. Profile Memory Usage

```python
from memory_profiler import profile

@profile
def index_large_corpus():
    # Your indexing code
    pass
```

Run with:
```bash
python -m memory_profiler script.py
```

### 3. Monitor Azure Metrics

Use Azure Monitor to track:

- **Search Service**:
  - Indexing latency
  - Document count
  - Storage used
  - Query latency

- **OpenAI Service**:
  - Token usage
  - Request rate
  - Error rate
  - Latency

```python
from azure.monitor.query import MetricsQueryClient

client = MetricsQueryClient(credential)
metrics = client.query_resource(
    resource_uri=search_resource_id,
    metric_names=["DocumentCount", "IndexingLatency"],
    timespan=timedelta(hours=1)
)
```

### 4. Application Insights

Integrate for detailed telemetry:

```python
from applicationinsights import TelemetryClient

tc = TelemetryClient('your-instrumentation-key')

tc.track_event('DocumentIndexed', {
    'file_type': 'pdf',
    'size_kb': file_size,
    'duration_ms': elapsed_ms
})

tc.flush()
```

---

## Troubleshooting Performance Issues

### Symptom: Slow Indexing

**Possible Causes:**

1. **Large documents**
   - Solution: Reduce `MAX_CHUNK_SIZE` or skip large files
   ```env
   MAX_FILE_SIZE_MB=5
   ```

2. **Rate limiting**
   - Check Azure portal for throttling
   - Solution: Reduce `BATCH_SIZE` or upgrade tier

3. **Network latency**
   - Solution: Use Azure VM in same region as services

4. **Inefficient chunking**
   - Solution: Optimize chunk size and overlap

### Symptom: High Memory Usage

**Possible Causes:**

1. **Large batch size**
   - Solution: Reduce `BATCH_SIZE`

2. **Loading entire files into memory**
   - Solution: Stream large files

3. **Embedding cache in memory**
   - Solution: Use disk-based cache

### Symptom: API Rate Limit Errors

**Solutions:**

1. **Implement exponential backoff**
   ```python
   @retry(wait=wait_exponential(multiplier=1, min=4, max=60))
   def api_call():
       pass
   ```

2. **Reduce concurrency**
   ```env
   MAX_CONCURRENT_REQUESTS=5
   ```

3. **Upgrade Azure tier**

### Symptom: Inconsistent Performance

**Possible Causes:**

1. **Azure service throttling**
   - Check Azure metrics

2. **Network issues**
   - Run from Azure VM

3. **Insufficient resources**
   - Increase RAM/CPU

---

## Benchmarking

### Test Setup

```python
import time
import statistics

def benchmark_indexing(num_runs=5):
    times = []
    for i in range(num_runs):
        start = time.perf_counter()
        index_documents(test_docs)
        elapsed = time.perf_counter() - start
        times.append(elapsed)
    
    return {
        'mean': statistics.mean(times),
        'median': statistics.median(times),
        'stdev': statistics.stdev(times) if len(times) > 1 else 0
    }
```

### Expected Performance

| Document Count | Size | Time (Basic) | Time (S1) | Cost |
|---------------|------|--------------|-----------|------|
| 100 | 10MB | 2-5 min | 1-2 min | ~$0.50 |
| 1,000 | 100MB | 20-45 min | 8-15 min | ~$5 |
| 10,000 | 1GB | 4-8 hours | 1-3 hours | ~$50 |
| 100,000 | 10GB | 2-4 days | 10-24 hours | ~$500 |

*Assumes text-embedding-ada-002 with average document complexity*

---

## Best Practices Summary

1. ✅ Enable embedding cache
2. ✅ Use incremental indexing
3. ✅ Optimize batch size for your tier
4. ✅ Choose appropriate chunk size
5. ✅ Monitor Azure metrics
6. ✅ Implement retry logic with backoff
7. ✅ Use async processing for I/O
8. ✅ Profile and benchmark regularly
9. ✅ Scale Azure services as needed
10. ✅ Use Private Link for production

---

## Additional Resources

- [Azure Search Performance](https://learn.microsoft.com/azure/search/search-performance-optimization)
- [Azure OpenAI Rate Limits](https://learn.microsoft.com/azure/ai-services/openai/quotas-limits)
- [Python Performance Tips](https://wiki.python.org/moin/PythonSpeed/PerformanceTips)
- [Async Programming in Python](https://docs.python.org/3/library/asyncio.html)
