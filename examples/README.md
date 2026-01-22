# Examples

This directory contains practical examples for using AzureSearch FileShare Indexer.

---

## Available Examples

### 1. Basic Indexing (`basic_indexing.py`)

**Purpose**: Simple document indexing to Azure AI Search

**What it demonstrates:**
- Initializing the vector indexer
- Indexing a directory of documents
- Viewing indexing statistics

**Usage:**
```bash
python examples/basic_indexing.py
```

**When to use:**
- First time setup
- Simple indexing scenarios
- Learning the basics

---

### 2. Advanced Search (`advanced_search.py`)

**Purpose**: Demonstrates different search capabilities

**What it demonstrates:**
- Hybrid search (keyword + vector)
- Semantic search with reranking
- Filtered search by file type
- Date-based filtering
- Pure vector search

**Usage:**
```bash
python examples/advanced_search.py
```

**When to use:**
- Understanding search types
- Comparing search quality
- Learning filter syntax

---

### 3. Custom Pipeline (`custom_pipeline.py`)

**Purpose**: Building a custom indexing workflow

**What it demonstrates:**
- Pre-processing before indexing
- Post-processing after indexing
- Custom validation logic
- Generating reports
- Verifying indexed content

**Usage:**
```bash
python examples/custom_pipeline.py
```

**When to use:**
- Complex business requirements
- Custom validation needs
- Audit and compliance
- Integration with existing systems

---

## Running Examples

### Prerequisites

1. Complete setup (see [Setup Guide](../docs/SETUP.md))
2. Configure `.env` file with your Azure credentials
3. Create an index:
```bash
   python scripts/create_vector_index.py
```

### Modify for Your Environment

Each example uses a default path. Update this line:
```python
# Change this to your file share path
FILE_SHARE_PATH = r"\\BIGMAC\Test Data"
```

---

## Example Workflows

### Workflow 1: Initial Setup and Test
```bash
# 1. Run basic indexing
python examples/basic_indexing.py

# 2. Test search
python examples/advanced_search.py

# 3. Verify results
python scripts/search_demo.py "test query"
```

### Workflow 2: Production Deployment
```bash
# 1. Use custom pipeline for production
python examples/custom_pipeline.py

# 2. Review generated report
cat indexing_report_*.json

# 3. Set up scheduled execution
# (See Deployment Guide)
```

### Workflow 3: Incremental Updates
```bash
# Enable incremental indexing in .env
INCREMENTAL_INDEXING=true

# Run indexing (only changed files processed)
python examples/basic_indexing.py
```

---

## Creating Your Own Examples

### Template Structure
```python
"""
Your custom example

Description of what it does.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.vector_indexer import VectorIndexer
from src.search import SearchClient
from config import Config

def main():
    """Main function"""
    # Your code here
    pass

if __name__ == "__main__":
    main()
```

### Best Practices

1. **Import from src/**: Use the library modules
2. **Use Config**: Get settings from configuration
3. **Add docstrings**: Document what your example does
4. **Handle errors**: Add try/except blocks
5. **Print results**: Show what's happening

---

## Common Patterns

### Pattern 1: Batch Processing
```python
from src.vector_indexer import VectorIndexer

indexer = VectorIndexer()

# Process specific directories
directories = [
    "/path/to/dir1",
    "/path/to/dir2",
    "/path/to/dir3"
]

for directory in directories:
    print(f"Processing {directory}...")
    stats = indexer.index_directory(directory)
    print(f"Indexed {stats['successful_files']} files")
```

### Pattern 2: Filtered Indexing
```python
import os
from src.vector_indexer import VectorIndexer

indexer = VectorIndexer()

# Only index PDF files
for root, dirs, files in os.walk("/path/to/docs"):
    for file in files:
        if file.endswith('.pdf'):
            file_path = os.path.join(root, file)
            chunks = indexer.index_file(file_path)
            print(f"Indexed {file}: {chunks} chunks")
```

### Pattern 3: Search with Post-Processing
```python
from src.search import SearchClient

search = SearchClient()

# Search and filter results
results = search.hybrid_search("employee benefits", top=20)

# Custom filtering
filtered = [
    r for r in results 
    if r['@search.score'] > 0.7 and r['extension'] == '.pdf'
]

# Sort by date
sorted_results = sorted(
    filtered, 
    key=lambda x: x['modifiedDateTime'], 
    reverse=True
)

for result in sorted_results[:5]:
    print(f"{result['name']}: {result['@search.score']:.4f}")
```

### Pattern 4: Monitoring and Alerts
```python
from src.vector_indexer import VectorIndexer
import smtplib
from email.mime.text import MIMEText

indexer = VectorIndexer()
stats = indexer.index_directory()

# Send alert if failures exceed threshold
if stats['failed_files'] > 10:
    msg = MIMEText(f"High failure rate: {stats['failed_files']} files failed")
    msg['Subject'] = 'Indexing Alert'
    msg['From'] = 'indexer@company.com'
    msg['To'] = 'admin@company.com'
    
    # Send email (configure SMTP)
    # smtp.send_message(msg)
    print("Alert sent!")
```

---

## Testing Examples

Before using in production:

1. **Test with small dataset:**
```bash
   # Create test directory
   mkdir test_files
   cp /path/to/few/files test_files/
   
   # Modify example to use test directory
   # Run example
```

2. **Verify results:**
```bash
   python scripts/search_demo.py "test query"
```

3. **Check logs:**
```bash
   tail -f logs/indexer.log
```

---

## Contributing Examples

Have a useful example? Contribute it!

1. Create a new example file
2. Add documentation here
3. Submit a pull request

See [Contributing Guide](../CONTRIBUTING.md)

---

## Need Help?

- Check [Documentation](../docs/)
- Open an [Issue](https://github.com/49ochieng/AzureSearch-FileShare-Indexer/issues)
- Ask in [Discussions](https://github.com/49ochieng/AzureSearch-FileShare-Indexer/discussions)