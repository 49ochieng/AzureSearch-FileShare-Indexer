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
