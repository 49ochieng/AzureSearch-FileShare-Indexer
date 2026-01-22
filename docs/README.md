# Documentation

Comprehensive documentation for AzureSearch FileShare Indexer.

---

## Quick Links

### Getting Started
- **[Setup Guide](SETUP.md)** - Installation and configuration
- **[Usage Guide](USAGE.md)** - How to use the indexer
- **[Quick Start](../README.md#quick-start)** - 5-minute setup

### Technical Documentation
- **[Architecture](ARCHITECTURE.md)** - System design and components
- **[API Reference](API.md)** - Complete API documentation
- **[Deployment Guide](DEPLOYMENT.md)** - Production deployment

### Support
- **[Troubleshooting](TROUBLESHOOTING.md)** - Common issues and solutions
- **[FAQ](#frequently-asked-questions)** - Frequently asked questions

---

## Documentation Structure
```
docs/
├── README.md                # This file - documentation index
├── SETUP.md                 # Installation and setup
├── USAGE.md                 # Usage guide and examples
├── ARCHITECTURE.md          # Technical architecture
├── API.md                   # API reference
├── DEPLOYMENT.md            # Deployment strategies
└── TROUBLESHOOTING.md       # Problem solving
```

---

## Frequently Asked Questions

### General Questions

**Q: What file formats are supported?**

A: Currently supported formats:
- Text: `.txt`, `.md`
- Documents: `.docx`, `.pdf`
- Spreadsheets: `.xlsx`
- Presentations: `.pptx`

**Q: How much does it cost to run?**

A: Typical monthly costs:
- Azure AI Search (Basic): $75
- Azure OpenAI (usage-based): $50-200
- Total: $125-275/month

See [Deployment Guide - Cost Optimization](DEPLOYMENT.md#cost-optimization)

**Q: Can I use this with my on-premises file share?**

A: Yes! The indexer works with:
- On-premises file shares (SMB/CIFS)
- Azure Files
- Local directories
- Network-attached storage (NAS)

---

### Technical Questions

**Q: What's the difference between keyword, vector, hybrid, and semantic search?**

A: 
- **Keyword**: Traditional text matching (fastest)
- **Vector**: Semantic similarity using AI embeddings (best for meaning)
- **Hybrid**: Combines keyword + vector (recommended for most use cases)
- **Semantic**: Hybrid + intelligent reranking (best quality)

See [Usage Guide - Search Types](USAGE.md#search-types)

**Q: How are large documents handled?**

A: Large documents are automatically:
1. Split into chunks (default: 1000 tokens)
2. Each chunk gets an embedding
3. Chunks are indexed separately
4. Search returns relevant chunks

**Q: Can I customize the chunking strategy?**

A: Yes! Adjust in `.env`:
```env
CHUNK_SIZE=1000      # Tokens per chunk
CHUNK_OVERLAP=200    # Overlap between chunks
```

**Q: How does incremental indexing work?**

A: When enabled:
1. File modification times are tracked
2. Only changed files are re-indexed
3. Cache is maintained in `.cache/` directory
4. Significantly reduces processing time

---

### Deployment Questions

**Q: What's the best deployment option for my scenario?**

A: Depends on your needs:

| Scenario | Best Option |
|----------|-------------|
| Small team, testing | Local workstation |
| On-premises files | Windows Server with Task Scheduler |
| Cloud-native
Jan 16
| Azure Functions |
| Enterprise scale | Kubernetes (AKS) |

See Deployment Guide

Q: How do I schedule regular indexing?

A: Multiple options:

Windows: Task Scheduler (guide)
Linux: Cron jobs
Azure: Azure Functions with timer trigger
Kubernetes: CronJob resource
Q: Can I run multiple indexers in parallel?

A: Yes! For large file shares:

Partition by directory
Run separate indexer instances
All write to same Azure AI Search index
Improves overall throughput
Performance Questions
Q: How long does indexing take?

A: Depends on:

Number of files
File sizes
Embedding API rate limits
Network speed
Typical: 10-50 files/minute with vector embeddings

Q: How can I speed up indexing?

A: Several strategies:

Increase BATCH_SIZE and MAX_WORKERS
Enable CACHE_EMBEDDINGS
Use INCREMENTAL_INDEXING
Upgrade Azure OpenAI quota
See Troubleshooting - Performance Issues

Q: My searches are slow. How can I improve performance?

A: Try:

Use filters to reduce result set
Limit fields returned
Reduce top parameter
Upgrade Azure AI Search tier
Security Questions
Q: How are credentials secured?

A: Multiple approaches:

Development: .env file (never committed)
Production: Azure Key Vault or Managed Identity
All secrets masked in logs
See Security Policy

Q: Can I use managed identity instead of API keys?

A: Yes! Recommended for production:

python
from azure.identity import DefaultAzureCredential

credential = DefaultAzureCredential()
# Use credential instead of API key
```

**Q: Is my data encrypted?**

A: Yes:
- **At rest**: Azure AI Search encrypts all data (AES-256)
- **In transit**: All API calls use TLS 1.2+
- **Local cache**: Use file system encryption (BitLocker/LUKS)

---

## Documentation Contributions

Found an issue or want to improve the documentation?

1. Check existing documentation
2. Submit an issue or pull request
3. See [Contributing Guide](../CONTRIBUTING.md)

---

## Additional Resources

### Official Azure Documentation
- [Azure AI Search](https://docs.microsoft.com/azure/search/)
- [Azure OpenAI](https://docs.microsoft.com/azure/ai-services/openai/)

### Related Projects
- [Azure SDK for Python](https://github.com/Azure/azure-sdk-for-python)
- [OpenAI Python Client](https://github.com/openai/openai-python)

### Community
- [GitHub Discussions](https://github.com/49ochieng/AzureSearch-FileShare-Indexer/discussions)
- [Stack Overflow](https://stackoverflow.com/questions/tagged/azure-search)

---

**Questions not answered here?** Check [Troubleshooting](TROUBLESHOOTING.md) or open an [issue](https://github.com/49ochieng/AzureSearch-FileShare-Indexer/issues).
```
