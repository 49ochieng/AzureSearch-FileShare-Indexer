# Troubleshooting Guide

Common issues and solutions for AzureSearch FileShare Indexer.

---

## Table of Contents

- [Configuration Issues](#configuration-issues)
- [Connection Issues](#connection-issues)
- [Indexing Issues](#indexing-issues)
- [Search Issues](#search-issues)
- [Performance Issues](#performance-issues)
- [Azure-Specific Issues](#azure-specific-issues)
- [File Share Access Issues](#file-share-access-issues)
- [Debugging Tips](#debugging-tips)

---

## Configuration Issues

### Issue: "Configuration validation failed"

**Symptoms:**
```
❌ Configuration validation failed:
  - AZURE_SEARCH_ENDPOINT is required
```

**Causes:**
- Missing or incorrectly named environment variables
- `.env` file not found
- `.env` file not loaded properly

**Solutions:**

1. **Check .env file exists:**
```bash
   ls -la .env
```

2. **Verify .env format (no spaces around =):**
```env
   # ❌ Wrong
   AZURE_SEARCH_ENDPOINT = https://...
   
   # ✅ Correct
   AZURE_SEARCH_ENDPOINT=https://...
```

3. **Test configuration:**
```bash
   python -c "from config import Config; Config.print_config()"
```

4. **Verify all required variables are set:**
```bash
   python verify_setup.py
```

---

### Issue: "Module not found" errors

**Symptoms:**
```
ModuleNotFoundError: No module named 'azure'
```

**Causes:**
- Virtual environment not activated
- Dependencies not installed

**Solutions:**

1. **Activate virtual environment:**
```bash
   # Windows
   .venv\Scripts\activate
   
   # Linux/Mac
   source .venv/bin/activate
```

2. **Reinstall dependencies:**
```bash
   pip install -r requirements.txt
```

3. **Verify installation:**
```bash
   pip list | grep azure
```

---

## Connection Issues

### Issue: "Failed to connect to Azure AI Search"

**Symptoms:**
```
❌ HTTPSConnectionPool: Failed to establish connection
❌ Failed to resolve 'your-search-service.search.windows.net'
```

**Causes:**
- Incorrect endpoint URL
- Network connectivity issues
- Firewall blocking connections
- Invalid API key

**Solutions:**

1. **Verify endpoint format:**
```env
   # ✅ Correct (must include https://)
   AZURE_SEARCH_ENDPOINT=https://your-service.search.windows.net
   
   # ❌ Wrong
   AZURE_SEARCH_ENDPOINT=your-service.search.windows.net
```

2. **Test connectivity:**
```bash
   curl https://your-search-service.search.windows.net?api-version=2023-11-01 \
     -H "api-key: YOUR_KEY"
```

3. **Check firewall rules in Azure Portal:**
   - Navigate to: Search Service → Networking
   - Temporarily set to "All networks" for testing
   - Add your IP if using IP restrictions

4. **Verify API key:**
   - Azure Portal → Your Search Service → Keys
   - Copy a fresh Admin key
   - Update `.env` file

5. **Test DNS resolution:**
```bash
   nslookup your-search-service.search.windows.net
```

---

### Issue: "Azure OpenAI connection failed"

**Symptoms:**
```
❌ Error calling Azure OpenAI API
❌ 401 Unauthorized
```

**Causes:**
- Invalid API key
- Wrong endpoint
- Deployment not found
- Rate limiting

**Solutions:**

1. **Verify OpenAI configuration:**
```bash
   python -c "
   from config import Config
   print(f'Endpoint: {Config.AZURE_OPENAI_ENDPOINT}')
   print(f'Deployment: {Config.AZURE_OPENAI_EMBEDDING_DEPLOYMENT}')
   "
```

2. **Test OpenAI connection:**
```python
   from openai import AzureOpenAI
   from config import Config
   
   client = AzureOpenAI(
       azure_endpoint=Config.AZURE_OPENAI_ENDPOINT,
       api_key=Config.AZURE_OPENAI_KEY,
       api_version=Config.AZURE_OPENAI_API_VERSION
   )
   
   response = client.embeddings.create(
       input="test",
       model=Config.AZURE_OPENAI_EMBEDDING_DEPLOYMENT
   )
   print(f"Success! Dimensions: {len(response.data[0].embedding)}")
```

3. **Verify deployment name:**
   - Azure Portal → OpenAI Service → Model deployments
   - Copy exact deployment name (case-sensitive)

4. **Check quota:**
   - Azure Portal → OpenAI Service → Quotas
   - Request increase if at limit

---

## Indexing Issues

### Issue: "No content extracted from file"

**Symptoms:**
```
⚠️ No content extracted, skipping
⚠️ Could not extract text: Unsupported file type
```

**Causes:**
- Unsupported file format
- Corrupted file
- File is password-protected
- File is empty

**Solutions:**

1. **Check file extension:**
```python
   # Supported formats
   SUPPORTED_EXTENSIONS = ['.txt', '.docx', '.pdf', '.xlsx', '.pptx']
```

2. **Manually test extraction:**
```python
   from src.extractors import ContentExtractor
   
   extractor = ContentExtractor()
   try:
       content = extractor.extract_text("problematic_file.pdf")
       print(f"Extracted {len(content)} characters")
   except Exception as e:
       print(f"Error: {e}")
```

3. **Check file is not password-protected:**
   - Try opening file manually
   - Remove password protection if possible

4. **Verify file is not corrupted:**
```bash
   # For PDF
   pdfinfo file.pdf
   
   # For Office files
   # Try opening in Microsoft Office
```

---

### Issue: "Embedding generation failed"

**Symptoms:**
```
❌ Failed to generate embedding after 3 attempts
⚠️ Embedding error: Rate limit exceeded
```

**Causes:**
- Rate limit exceeded
- Text too long
- Network timeout
- OpenAI service outage

**Solutions:**

1. **Reduce batch size:**
```env
   BATCH_SIZE=10
   MAX_WORKERS=2
```

2. **Increase retry delay:**
```env
   MAX_RETRIES=5
   RETRY_DELAY=5
```

3. **Enable embedding cache:**
```env
   CACHE_EMBEDDINGS=true
```

4. **Check text length:**
```python
   # Max 8191 tokens for text-embedding models
   # The indexer automatically truncates, but verify:
   import tiktoken
   
   encoding = tiktoken.get_encoding("cl100k_base")
   tokens = encoding.encode(text)
   print(f"Token count: {len(tokens)}")
```

5. **Monitor OpenAI status:**
   - Visit: https://status.azure.com
   - Check for service outages

---

### Issue: "Upload to Azure AI Search failed"

**Symptoms:**
```
❌ Failed to upload batch: 413 Request Entity Too Large
❌ Failed to index: 400 Bad Request
```

**Causes:**
- Document too large
- Invalid field values
- Schema mismatch
- Index doesn't exist

**Solutions:**

1. **Reduce chunk size:**
```env
   CHUNK_SIZE=800  # Reduce from 1000
```

2. **Verify index exists:**
```python
   from src.index_manager import IndexManager
   
   manager = IndexManager()
   indexes = manager.list_indexes()
   print(f"Available indexes: {indexes}")
```

3. **Check field limits:**
   - Content field: max 50,000 characters
   - String fields: max 32KB

4. **Validate document structure:**
```python
   # Ensure all required fields are present
   required_fields = ['id', 'content', 'title', 'name', 'filePath']
```

---

### Issue: "Incremental indexing not working"

**Symptoms:**
```
All files being re-indexed even though unchanged
```

**Causes:**
- Cache not enabled
- Cache file corrupted
- File timestamps changed

**Solutions:**

1. **Enable incremental indexing:**
```env
   INCREMENTAL_INDEXING=true
```

2. **Check cache directory:**
```bash
   ls -la .cache/
```

3. **Clear cache to reset:**
```bash
   rm -rf .cache/*
```

4. **Verify file timestamps:**
```bash
   stat filename.txt
```

---

## Search Issues

### Issue: "No search results found"

**Symptoms:**
```
No results found for query: "employee benefits"
```

**Causes:**
- Index is empty
- Query too specific
- Wrong index being searched
- Documents not yet indexed

**Solutions:**

1. **Verify index has documents:**
```python
   from src.index_manager import IndexManager
   
   manager = IndexManager()
   stats = manager.get_index_statistics("fileshare-vector-documents")
   print(f"Document count: {stats['documentCount']}")
```

2. **Try wildcard search:**
```python
   results = search.search("*", top=10)
   print(f"Found {len(results)} total documents")
```

3. **Check index name:**
```python
   print(f"Searching index: {search.index_name}")
```

4. **Try different search types:**
```python
   # Try keyword search
   results = search.search("employee")
   
   # Try vector search
   results = search.vector_search("employee")
   
   # Try hybrid
   results = search.hybrid_search("employee")
```

---

### Issue: "Vector search not available"

**Symptoms:**
```
❌ Vector search not configured. Check OpenAI settings.
```

**Causes:**
- Azure OpenAI not configured
- Vector index not created
- Using standard index instead of vector index

**Solutions:**

1. **Verify OpenAI configuration:**
```bash
   python -c "from config import Config; Config.validate(require_openai=True)"
```

2. **Verify using vector index:**
```python
   # Ensure use_vector_index=True
   search = SearchClient(use_vector_index=True)
```

3. **Check index has vector field:**
```python
   from src.index_manager import IndexManager
   
   manager = IndexManager()
   # Verify index was created with vector support
```

---

### Issue: "Search results not relevant"

**Symptoms:**
- Results don't match query intent
- Low relevance scores
- Wrong documents returned

**Solutions:**

1. **Try semantic search:**
```python
   # Semantic search provides better relevance
   results = search.semantic_search(query, top=10)
```

2. **Use more specific queries:**
```python
   # ❌ Too broad
   "documents"
   
   # ✅ More specific
   "employee benefits enrollment process"
```

3. **Add filters:**
```python
   results = search.filtered_search(
       query="benefits",
       extension=".pdf",
       date_from="2024-01-01T00:00:00Z"
   )
```

4. **Check document content:**
```python
   # Verify documents actually contain relevant content
   for result in results:
       print(result['chunk'][:200])
```

---

## Performance Issues

### Issue: "Indexing is very slow"

**Symptoms:**
- Takes hours to index small number of files
- High CPU usage
- Memory exhaustion

**Solutions:**

1. **Check resource usage:**
```bash
   # Windows
   taskmgr
   
   # Linux
   top
   htop
```

2. **Optimize configuration:**
```env
   # Increase workers for parallel processing
   MAX_WORKERS=8
   
   # Increase batch size
   BATCH_SIZE=200
   
   # Enable caching
   CACHE_EMBEDDINGS=true
```

3. **Monitor API rate limits:**
```python
   # Check stats for API calls
   stats = indexer.get_statistics()
   print(f"API calls: {stats['embedding_api_calls']}")
   print(f"Duration: {stats['duration']} seconds")
```

4. **Profile slow operations:**
```python
   import cProfile
   
   cProfile.run('indexer.index_directory()', 'profile_stats')
   
   import pstats
   p = pstats.Stats('profile_stats')
   p.sort_stats('cumulative').print_stats(10)
```

---

### Issue: "High memory usage"

**Symptoms:**
```
MemoryError: Unable to allocate array
Out of memory error
```

**Solutions:**

1. **Reduce batch size:**
```env
   BATCH_SIZE=10
```

2. **Reduce chunk size:**
```env
   CHUNK_SIZE=500
```

3. **Process fewer files concurrently:**
```env
   MAX_WORKERS=2
```

4. **Monitor memory usage:**
```python
   import psutil
   
   process = psutil.Process()
   print(f"Memory usage: {process.memory_info().rss / 1024 / 1024:.2f} MB")
```

---

### Issue: "Search queries are slow"

**Symptoms:**
- Search takes several seconds
- Timeout errors
- High latency

**Solutions:**

1. **Use filters to reduce result set:**
```python
   # ✅ Better - filtered search
   results = search.hybrid_search(
       query="documents",
       filter_expr="extension eq '.pdf'"
   )
   
   # ❌ Slower - no filter
   results = search.hybrid_search("documents", top=1000)
```

2. **Limit fields returned:**
```python
   results = search.hybrid_search(
       query="documents",
       select=["name", "filePath", "@search.score"]
   )
```

3. **Reduce top K:**
```python
   # ✅ Faster
   results = search.hybrid_search(query, top=10)
   
   # ❌ Slower
   results = search.hybrid_search(query, top=1000)
```

4. **Check Azure AI Search tier:**
   - Basic tier may be slow for large indexes
   - Consider upgrading to Standard

---

## Azure-Specific Issues

### Issue: "Index not found"

**Symptoms:**
```
❌ The index 'fileshare-vector-documents' does not exist
```

**Solutions:**

1. **List available indexes:**
```python
   from src.index_manager import IndexManager
   
   manager = IndexManager()
   indexes = manager.list_indexes()
   print(f"Available: {indexes}")
```

2. **Create index:**
```bash
   python scripts/create_vector_index.py
```

3. **Verify index name in config:**
```bash
   grep AZURE_SEARCH_VECTOR_INDEX_NAME .env
```

---

### Issue: "Quota exceeded"

**Symptoms:**
```
❌ 429 Too Many Requests
❌ Rate limit exceeded
```

**Solutions:**

1. **Check quotas in Azure Portal:**
   - Azure AI Search → Overview → Quota usage
   - Azure OpenAI → Quotas

2. **Request quota increase:**
   - Azure Portal → Support → New support request
   - Issue type: Service and subscription limits (quotas)

3. **Reduce request rate:**
```env
   BATCH_SIZE=10
   MAX_WORKERS=2
   RETRY_DELAY=5
```

4. **Implement exponential backoff:**
   - Already implemented in indexer
   - Increase MAX_RETRIES and RETRY_DELAY

---

### Issue: "Authentication failed"

**Symptoms:**
```
❌ 401 Unauthorized
❌ 403 Forbidden
```

**Solutions:**

1. **Verify API keys:**
```bash
   # Get fresh keys from Azure Portal
   # Search Service → Keys
   # OpenAI Service → Keys and Endpoint
```

2. **Check key type:**
   - Use **Admin key** for indexing
   - **Query key** is read-only (won't work for indexing)

3. **Use managed identity (recommended):**
```python
   from azure.identity import DefaultAzureCredential
   
   credential = DefaultAzureCredential()
   search_client = SearchClient(
       endpoint=Config.AZURE_SEARCH_ENDPOINT,
       index_name=Config.AZURE_SEARCH_INDEX_NAME,
       credential=credential
   )
```

---

## File Share Access Issues

### Issue: "Cannot access file share"

**Symptoms:**
```
❌ [Errno 2] No such file or directory: '\\\\SERVER\\Share'
❌ Permission denied
```

**Solutions:**

1. **Test file share access:**
```bash
   # Windows
   dir \\SERVER\Share
   
   # Linux (if mounted)
   ls /mnt/share
```

2. **Check credentials:**
```powershell
   # Windows - test with net use
   net use \\SERVER\Share /user:DOMAIN\username password
```

3. **Verify path format:**
```env
   # Windows UNC path
   FILE_SHARE_PATH=\\\\SERVER\\Share\\Documents
   
   # Linux mounted path
   FILE_SHARE_PATH=/mnt/share/documents
```

4. **Check permissions:**
```bash
   # Ensure service account has read access
   icacls \\SERVER\Share  # Windows
   ls -la /mnt/share      # Linux
```

---

### Issue: "File locked or in use"

**Symptoms:**
```
❌ Permission denied: 'file.docx'
❌ [Errno 13] Permission denied
```

**Solutions:**

1. **Skip locked files:**
   - Already handled by extractor
   - File will be logged as failed

2. **Close files before indexing:**
   - Ensure files aren't open in other applications

3. **Use read-only mode:**
   - Indexer only needs read access
   - Verify file share is mounted read-only

---

## Debugging Tips

### Enable Debug Logging
```env
LOG_LEVEL=DEBUG
LOG_TO_CONSOLE=true
LOG_FILE=logs/debug.log
```

### Use Python Debugger
```python
# Add breakpoint in code
import pdb; pdb.set_trace()

# Or use built-in breakpoint()
breakpoint()
```

### Test Individual Components
```python
# Test extraction
from src.extractors import ContentExtractor
extractor = ContentExtractor()
content = extractor.extract_text("test.pdf")

# Test embedding
from src.vector_indexer import VectorIndexer
indexer = VectorIndexer()
embedding = indexer.generate_embedding("test text")

# Test search
from src.search import SearchClient
search = SearchClient()
results = search.search("test")
```

### Check Environment Variables
```python
import os
print("Environment variables:")
for key in os.environ:
    if 'AZURE' in key or 'OPENAI' in key:
        value = os.environ[key]
        # Mask sensitive data
        if 'KEY' in key:
            value = value[:8] + "..." + value[-4:]
        print(f"  {key}={value}")
```

### Network Debugging
```bash
# Test Azure connectivity
curl -v https://your-search.search.windows.net

# Check DNS
nslookup your-search.search.windows.net

# Trace route
traceroute your-search.search.windows.net  # Linux
tracert your-search.search.windows.net     # Windows
```

### Performance Profiling
```python
import time
import cProfile
import pstats

# Time operations
start = time.time()
indexer.index_file("large_file.pdf")
print(f"Duration: {time.time() - start:.2f}s")

# Profile code
cProfile.run('indexer.index_directory()', 'profile.stats')
p = pstats.Stats('profile.stats')
p.sort_stats('cumulative').print_stats(20)
```

---

## Getting Help

### Before Asking for Help

1. Check this troubleshooting guide
2. Search existing GitHub issues
3. Enable debug logging
4. Run `python verify_setup.py`

### When Asking for Help

Include:
- Error message (full stack trace)
- Configuration (with secrets removed)
- Python version: `python --version`
- OS and version
- Steps to reproduce
- What you've already tried

### Where to Get Help

- **GitHub Issues**: https://github.com/YOUR_USERNAME/AzureSearch-FileShare-Indexer/issues
- **GitHub Discussions**: https://github.com/YOUR_USERNAME/AzureSearch-FileShare-Indexer/discussions
- **Email**: your.email@example.com

---

## Quick Diagnostic Commands
```bash
# Full system check
python verify_setup.py

# Check configuration
python -c "from config import Config; Config.print_config()"

# Test Azure connectivity
python -c "
from src.index_manager import IndexManager
manager = IndexManager()
print(manager.list_indexes())
"

# Test file share access
python -c "
import os
from config import Config
print(os.listdir(Config.FILE_SHARE_PATH))
"

# Run health check
python scripts/health_check.py
```

---

**Still having issues?** Open an issue on GitHub with detailed information and we'll help you troubleshoot!