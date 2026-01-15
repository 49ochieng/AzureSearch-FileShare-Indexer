# AzureSearch FileShare Indexer

<div align="center">

![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)
![Python](https://img.shields.io/badge/python-3.9%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Azure](https://img.shields.io/badge/Azure-AI%20Search-0078D4)
![OpenAI](https://img.shields.io/badge/Azure-OpenAI-412991)

**Enterprise-grade document indexing for Azure AI Search with vector embeddings and semantic search**

[Features](#features) • [Quick Start](#quick-start) • [Documentation](#documentation) • [Examples](#examples) • [Contributing](#contributing)

</div>

---

## 🌟 Features

### Core Capabilities
- ✅ **Multi-Format Support**: Index DOCX, PDF, XLSX, TXT, PPTX files
- 🔍 **Full-Text Search**: Traditional keyword-based search
- 🧠 **Vector Embeddings**: Semantic search powered by Azure OpenAI
- 🎯 **Hybrid Search**: Combines keyword and vector search for best results
- 📊 **Semantic Ranking**: Intelligent result reranking
- 🏷️ **Metadata Extraction**: Automatic extraction of file properties and document metadata
- 📦 **Smart Chunking**: Intelligent text splitting for large documents
- ⚡ **Batch Processing**: High-performance batch uploads
- 🔄 **Incremental Indexing**: Only process changed files
- 💾 **Embedding Cache**: Reduce API costs by caching embeddings

### Enterprise Features
- 🔐 **Secure Configuration**: Environment-based secrets management
- 📝 **Comprehensive Logging**: Detailed logs with rotation
- 🎨 **Flexible Deployment**: Supports development, staging, and production environments
- 🔧 **Highly Configurable**: 30+ configuration options
- 📈 **Progress Tracking**: Real-time indexing progress with statistics
- 🚀 **Production-Ready**: Battle-tested code with error handling and retry logic

---

## 📋 Table of Contents

- [Prerequisites](#prerequisites)
- [Quick Start](#quick-start)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
  - [Creating Indexes](#creating-indexes)
  - [Indexing Files](#indexing-files)
  - [Searching](#searching)
- [Architecture](#architecture)
- [Documentation](#documentation)
- [Examples](#examples)
- [Deployment](#deployment)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)
- [License](#license)
- [Credits](#credits)

---

## 🔧 Prerequisites

### Required
- **Python 3.9 or higher**
- **Azure AI Search service** (Basic tier or higher for vector search)
- **Azure OpenAI service** (for vector embeddings)
- **File share access** (local, network, or cloud-mounted)

### Azure Resources Setup

1. **Azure AI Search**
```bash
   # Create via Azure Portal or CLI
   az search service create \
     --name your-search-service \
     --resource-group your-rg \
     --sku basic \
     --location eastus
```

2. **Azure OpenAI**
```bash
   # Deploy embeddings model
   az cognitiveservices account deployment create \
     --name your-openai-service \
     --resource-group your-rg \
     --deployment-name text-embedding-3-large \
     --model-name text-embedding-3-large \
     --model-version "1" \
     --model-format OpenAI \
     --sku-capacity 1 \
     --sku-name "Standard"
```

---

## 🚀 Quick Start

### 1. Clone and Setup
```bash
# Clone the repository
git clone https://github.com/YOUR_USERNAME/AzureSearch-FileShare-Indexer.git
cd AzureSearch-FileShare-Indexer

# Create virtual environment
python -m venv .venv

# Activate virtual environment
# Windows
.venv\Scripts\activate
# Linux/Mac
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Environment
```bash
# Copy example environment file
cp .env.example .env

# Edit .env with your Azure credentials
# Required fields:
# - AZURE_SEARCH_ENDPOINT
# - AZURE_SEARCH_KEY
# - AZURE_OPENAI_ENDPOINT (for vector search)
# - AZURE_OPENAI_KEY (for vector search)
# - FILE_SHARE_PATH
```

Example `.env`:
```env
AZURE_SEARCH_ENDPOINT=https://your-search.search.windows.net
AZURE_SEARCH_KEY=your-search-key-here
AZURE_OPENAI_ENDPOINT=https://your-openai.openai.azure.com
AZURE_OPENAI_KEY=your-openai-key-here
FILE_SHARE_PATH=\\\\SERVER\\Share\\Documents
```

### 3. Create Index
```bash
# For vector search (recommended)
python scripts/create_vector_index.py

# For standard text search only
python scripts/create_standard_index.py
```

### 4. Index Your Files
```bash
# Vector indexing with embeddings
python scripts/index_files_vector.py

# Standard text indexing
python scripts/index_files.py
```

### 5. Search
```bash
# Hybrid search (best results)
python scripts/search_demo.py "employee benefits" --type hybrid

# Semantic search with reranking
python scripts/search_demo.py "quarterly financial reports" --type semantic

# Filter by file type
python scripts/search_demo.py "contracts" --extension .pdf --type hybrid
```

---

## 📦 Installation

### Standard Installation
```bash
pip install -r requirements.txt
```

### Development Installation
```bash
pip install -r requirements.txt
pip install -e ".[dev]"
```

### Optional Enhanced Features
```bash
# For better PDF extraction
pip install pdfplumber

# For image processing
pip install Pillow

# For OCR (scanned documents)
pip install pytesseract
```

---

## ⚙️ Configuration

All configuration is managed through environment variables in `.env` file.

### Essential Configuration

| Variable | Description | Required |
|----------|-------------|----------|
| `AZURE_SEARCH_ENDPOINT` | Azure AI Search service URL | ✅ |
| `AZURE_SEARCH_KEY` | Admin API key | ✅ |
| `AZURE_OPENAI_ENDPOINT` | Azure OpenAI service URL | For vector search |
| `AZURE_OPENAI_KEY` | Azure OpenAI API key | For vector search |
| `FILE_SHARE_PATH` | Path to files to index | ✅ |

### Advanced Configuration

| Variable | Description | Default |
|----------|-------------|---------|
| `CHUNK_SIZE` | Tokens per chunk | 1000 |
| `CHUNK_OVERLAP` | Chunk overlap tokens | 200 |
| `BATCH_SIZE` | Upload batch size | 100 |
| `MAX_FILE_SIZE_MB` | Max file size to process | 50 |
| `INCREMENTAL_INDEXING` | Only index changed files | true |
| `CACHE_EMBEDDINGS` | Cache embeddings | true |

See [`.env.example`](.env.example) for complete configuration options.

### Validate Configuration
```python
from config import Config

# Validate basic configuration
Config.validate()

# Validate with OpenAI requirements
Config.validate(require_openai=True)

# Print current configuration (secrets masked)
Config.print_config()
```

---

## 📘 Usage

### Creating Indexes

#### Vector Index (Recommended)
```python
from src.index_manager import IndexManager

manager = IndexManager()
manager.create_vector_index()
```

**CLI:**
```bash
python scripts/create_vector_index.py
```

#### Standard Text Index
```python
manager.create_standard_index()
```

**CLI:**
```bash
python scripts/create_standard_index.py
```

### Indexing Files

#### Vector Indexing
```python
from src.vector_indexer import VectorIndexer

indexer = VectorIndexer()
stats = indexer.index_directory("/path/to/files")

print(f"Indexed {stats['successful_files']} files")
print(f"Created {stats['total_chunks']} chunks")
print(f"Generated {stats['total_embeddings']} embeddings")
```

**CLI:**
```bash
# Index with default settings
python scripts/index_files_vector.py

# Custom path
python scripts/index_files_vector.py --path /custom/path

# Non-recursive
python scripts/index_files_vector.py --recursive false
```

#### Standard Text Indexing
```python
from src.indexer import FileIndexer

indexer = FileIndexer()
stats = indexer.index_directory("/path/to/files")
```

**CLI:**
```bash
python scripts/index_files.py
```

### Searching

#### Programmatic Search
```python
from src.search import SearchClient

# Initialize search client
search = SearchClient()

# Hybrid search (keyword + vector)
results = search.hybrid_search("employee benefits", top=5)

# Semantic search with reranking
results = search.semantic_search("quarterly reports", top=5)

# Pure vector search
results = search.vector_search("team collaboration", top=5)

# Keyword search only
results = search.search("project documentation", top=5)

# Filtered search
results = search.filtered_search(
    query="contracts",
    extension=".pdf",
    date_from="2024-01-01T00:00:00Z",
    search_type="hybrid"
)

# Display results
print(search.format_results(results))
```

#### CLI Search
```bash
# Hybrid search
python scripts/search_demo.py "employee benefits" --type hybrid --top 10

# Semantic search
python scripts/search_demo.py "financial reports" --type semantic

# Filter by extension
python scripts/search_demo.py "contracts" --extension .pdf

# Filter by date
python scripts/search_demo.py "policies" --date-from 2024-01-01T00:00:00Z
```

### Advanced Usage

#### Custom Chunking
```python
from src.vector_indexer import VectorIndexer

indexer = VectorIndexer()

# Custom chunk size and overlap
text = "Your long document text..."
chunks = indexer.chunk_text(text, chunk_size=500, overlap=100)
```

#### Batch Operations
```python
from src.indexer import FileIndexer

indexer = FileIndexer()

# Index specific files
files = [
    "/path/file1.pdf",
    "/path/file2.docx",
    "/path/file3.xlsx"
]

for file in files:
    indexer.index_file(file)
```

#### Index Management
```python
from src.index_manager import IndexManager

manager = IndexManager()

# List all indexes
indexes = manager.list_indexes()
print(f"Found indexes: {indexes}")

# Get statistics
stats = manager.get_index_statistics("fileshare-vector-documents")
print(f"Document count: {stats['documentCount']}")

# Delete index (caution!)
manager.delete_index("old-index-name")
```

---

## 🏗️ Architecture

### Project Structure
```
AzureSearch-FileShare-Indexer/
├── config/                      # Configuration management
│   ├── __init__.py
│   ├── settings.py             # Central configuration
│   └── logger.py               # Logging setup
│
├── src/                        # Core library
│   ├── __init__.py
│   ├── extractors.py          # Content extraction
│   ├── indexer.py             # Standard indexing
│   ├── vector_indexer.py      # Vector indexing
│   ├── search.py              # Search functionality
│   └── index_manager.py       # Index management
│
├── scripts/                    # Executable scripts
│   ├── create_standard_index.py
│   ├── create_vector_index.py
│   ├── index_files.py
│   ├── index_files_vector.py
│   └── search_demo.py
│
├── docs/                       # Documentation
│   ├── SETUP.md
│   ├── USAGE.md
│   ├── ARCHITECTURE.md
│   ├── API.md
│   └── DEPLOYMENT.md
│
├── examples/                   # Usage examples
│   ├── basic_indexing.py
│   ├── advanced_search.py
│   └── custom_pipeline.py
│
├── tests/                      # Unit tests
│   ├── __init__.py
│   ├── test_indexer.py
│   ├── test_search.py
│   └── test_extractors.py
│
├── .env.example               # Environment template
├── .gitignore
├── requirements.txt
├── setup.py
├── LICENSE
└── README.md
```

### Data Flow
```
┌─────────────────┐
│  File Share     │
│  (Documents)    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Content        │
│  Extractor      │
└────────┬────────┘
         │
         ├──────────────┬──────────────┐
         ▼              ▼              ▼
┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│  Metadata    │ │  Text        │ │  Chunks      │
│  Extraction  │ │  Extraction  │ │  (Optional)  │
└──────┬───────┘ └──────┬───────┘ └──────┬───────┘
       │                │                │
       └────────┬───────┴────────┬───────┘
                │                │
                ▼                ▼
         ┌─────────────┐  ┌─────────────┐
         │  Standard   │  │  Vector     │
         │  Indexing   │  │  Indexing   │
         │             │  │  (OpenAI)   │
         └──────┬──────┘  └──────┬──────┘
                │                │
                └────────┬───────┘
                         ▼
                ┌─────────────────┐
                │  Azure AI       │
                │  Search         │
                │  Index          │
                └────────┬────────┘
                         │
                         ▼
                ┌─────────────────┐
                │  Search API     │
                │  - Keyword      │
                │  - Vector       │
                │  - Hybrid       │
                │  - Semantic     │
                └─────────────────┘
```

### Component Responsibilities

| Component | Responsibility |
|-----------|----------------|
| **ContentExtractor** | Extract text and metadata from files |
| **FileIndexer** | Standard text indexing |
| **VectorIndexer** | Chunking, embedding generation, vector indexing |
| **SearchClient** | All search operations |
| **IndexManager** | Index lifecycle management |
| **Config** | Configuration validation and access |

---

## 📚 Documentation

### Comprehensive Guides

- **[Setup Guide](docs/SETUP.md)** - Detailed installation and Azure setup
- **[Usage Guide](docs/USAGE.md)** - Complete usage examples and patterns
- **[Architecture](docs/ARCHITECTURE.md)** - System design and components
- **[API Reference](docs/API.md)** - Complete API documentation
- **[Deployment Guide](docs/DEPLOYMENT.md)** - Production deployment strategies
- **[Troubleshooting](docs/TROUBLESHOOTING.md)** - Common issues and solutions

### Quick Links

- [Configuration Options](.env.example)
- [Change Log](CHANGELOG.md)
- [Contributing Guidelines](CONTRIBUTING.md)
- [Security Policy](SECURITY.md)

---

## 💡 Examples

### Example 1: Basic Indexing
```python
from src.vector_indexer import VectorIndexer
from config import Config

# Configure
Config.FILE_SHARE_PATH = "\\\\SERVER\\Docs"

# Index
indexer = VectorIndexer()
indexer.index_directory()
```

### Example 2: Custom Search Pipeline
```python
from src.search import SearchClient

# Initialize
search = SearchClient()

# Multi-stage search
queries = [
    "employee handbook",
    "IT policies",
    "expense reports"
]

all_results = []
for query in queries:
    results = search.hybrid_search(query, top=3)
    all_results.extend(results)

# Deduplicate by file path
unique_files = {}
for result in all_results:
    path = result['filePath']
    if path not in unique_files:
        unique_files[path] = result

print(f"Found {len(unique_files)} unique documents")
```

### Example 3: Scheduled Indexing
```python
import schedule
import time
from src.vector_indexer import VectorIndexer

def index_job():
    """Daily indexing job"""
    indexer = VectorIndexer()
    stats = indexer.index_directory()
    print(f"Indexed {stats['successful_files']} files")

# Schedule daily at 2 AM
schedule.every().day.at("02:00").do(index_job)

while True:
    schedule.run_pending()
    time.sleep(60)
```

More examples in [`examples/`](examples/) directory.

---

## 🚀 Deployment

### Local Development
```bash
# Activate environment
.venv\Scripts\activate

# Run indexing
python scripts/index_files_vector.py

# Run search
python scripts/search_demo.py "test query"
```

### Windows Task Scheduler
```powershell
# Create scheduled task for daily indexing
$action = New-ScheduledTaskAction -Execute "python" -Argument "scripts/index_files_vector.py" -WorkingDirectory "C:\Path\To\Project"
$trigger = New-ScheduledTaskTrigger -Daily -At 2am
$principal = New-ScheduledTaskPrincipal -UserId "DOMAIN\User" -LogonType S4U
Register-ScheduledTask -TaskName "FileShare Indexer" -Action $action -Trigger $trigger -Principal $principal
```

### Azure Functions

Deploy as serverless function for automatic updates:
```python
import azure.functions as func
from src.vector_indexer import VectorIndexer

def main(mytimer: func.TimerRequest) -> None:
    indexer = VectorIndexer()
    indexer.index_directory()
```

### Docker Container
```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY . /app

RUN pip install -r requirements.txt

CMD ["python", "scripts/index_files_vector.py"]
```

See [Deployment Guide](docs/DEPLOYMENT.md) for detailed instructions.

---

## 🔍 Troubleshooting

### Common Issues

#### "Configuration validation failed"
```bash
# Check your .env file
python -c "from config import Config; Config.print_config()"
```

#### "Vector search not available"
- Ensure Azure OpenAI credentials are set
- Verify embedding model deployment name matches config

#### "Failed to extract content"
- Check file permissions
- Verify file is not corrupted
- Ensure file extension is supported

#### "Embedding API rate limit"
- Reduce `BATCH_SIZE` in config
- Enable `CACHE_EMBEDDINGS=true`
- Increase `RETRY_DELAY`

### Enable Debug Logging
```env
LOG_LEVEL=DEBUG
LOG_FORMAT=detailed
```

### Get Support

- 📖 [Documentation](docs/)
- 🐛 [Report Issues](https://github.com/YOUR_USERNAME/AzureSearch-FileShare-Indexer/issues)
- 💬 [Discussions](https://github.com/YOUR_USERNAME/AzureSearch-FileShare-Indexer/discussions)

---

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guidelines](CONTRIBUTING.md).

### Development Setup
```bash
# Clone and setup
git clone https://github.com/YOUR_USERNAME/AzureSearch-FileShare-Indexer.git
cd AzureSearch-FileShare-Indexer
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
pip install -e ".[dev]"

# Run tests
pytest tests/

# Code formatting
black src/ scripts/
flake8 src/ scripts/
```

### Contribution Areas

- 🐛 Bug fixes
- ✨ New features
- 📝 Documentation improvements
- 🧪 Test coverage
- 🌍 Internationalization
- 🎨 UI/UX enhancements

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
```
MIT License

Copyright (c) 2025 Edgar McOchieng

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction...
```

---

## 👏 Credits

**Author:** Edgar McOchieng

### Built With

- [Azure AI Search](https://azure.microsoft.com/en-us/services/search/) - Enterprise search service
- [Azure OpenAI](https://azure.microsoft.com/en-us/products/ai-services/openai-service) - Embeddings generation
- [Python](https://www.python.org/) - Core programming language
- [azure-search-documents](https://pypi.org/project/azure-search-documents/) - Azure SDK
- [openai](https://pypi.org/project/openai/) - OpenAI Python client
- [python-docx](https://pypi.org/project/python-docx/) - DOCX processing
- [PyPDF2](https://pypi.org/project/PyPDF2/) - PDF processing
- [openpyxl](https://pypi.org/project/openpyxl/) - Excel processing

### Acknowledgments

- Azure AI team for excellent documentation
- Open source community for amazing libraries
- Contributors and users for feedback and improvements

---

## 📊 Project Stats

![GitHub stars](https://img.shields.io/github/stars/YOUR_USERNAME/AzureSearch-FileShare-Indexer?style=social)
![GitHub forks](https://img.shields.io/github/forks/YOUR_USERNAME/AzureSearch-FileShare-Indexer?style=social)
![GitHub issues](https://img.shields.io/github/issues/YOUR_USERNAME/AzureSearch-FileShare-Indexer)
![GitHub pull requests](https://img.shields.io/github/issues-pr/YOUR_USERNAME/AzureSearch-FileShare-Indexer)

---

## 🗺️ Roadmap

- [ ] Support for additional file formats (MSG, EML, HTML)
- [ ] Real-time indexing with file system watchers
- [ ] Multi-language support
- [ ] Custom metadata extractors
- [ ] Web UI for management
- [ ] API endpoint for programmatic access
- [ ] Integration with Microsoft 365 Copilot
- [ ] Advanced analytics and reporting

---

## 💬 Support

- **Documentation**: [docs/](docs/)
- **Issues**: [GitHub Issues](https://github.com/YOUR_USERNAME/AzureSearch-FileShare-Indexer/issues)
- **Discussions**: [GitHub Discussions](https://github.com/YOUR_USERNAME/AzureSearch-FileShare-Indexer/discussions)
- **Email**: your.email@example.com

---

<div align="center">

**Made with ❤️ by Edgar McOchieng**

⭐ Star this repo if you find it helpful!

[Report Bug](https://github.com/YOUR_USERNAME/AzureSearch-FileShare-Indexer/issues) · 
[Request Feature](https://github.com/YOUR_USERNAME/AzureSearch-FileShare-Indexer/issues) · 
[Documentation](docs/)

</div>