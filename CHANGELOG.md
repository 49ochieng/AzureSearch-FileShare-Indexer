# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2025-01-17

## [1.0.1] - 2026-02-09

### Changed
- Improved documentation in README.md and USAGE.md
- Added more usage tips and clarifications
- Updated documentation to better guide new users

### Added
- Initial release
- Multi-format document indexing (DOCX, PDF, XLSX, TXT, PPTX)
- Vector embeddings with Azure OpenAI
- Multiple search types (keyword, vector, hybrid, semantic)
- Intelligent text chunking
- Incremental indexing support
- Embedding caching
- Comprehensive configuration management
- CLI scripts for common operations
- Full test suite
- Comprehensive documentation

### Features
- **Content Extraction**: Support for multiple file formats
- **Vector Search**: Semantic search with embeddings
- **Hybrid Search**: Combined keyword and vector search
- **Semantic Ranking**: Intelligent result reranking
- **Metadata Extraction**: Automatic metadata parsing
- **Batch Processing**: High-performance batch uploads
- **Progress Tracking**: Real-time indexing progress
- **Logging**: Detailed logging with rotation

### Documentation
- Setup guide
- Usage guide
- Architecture documentation
- API reference
- Deployment guide
- Troubleshooting guide

## [Unreleased]

### Added
- Docker support with Dockerfile and docker-compose.yml for containerized deployment
- Comprehensive Docker deployment guide (docs/DOCKER.md)
- Performance optimization guide (docs/PERFORMANCE.md) with benchmarks and tuning strategies
- Security best practices documentation (docs/SECURITY.md)
- Additional badges in README for improved project visibility

### Documentation
- Detailed Docker deployment instructions for production environments
- Kubernetes deployment examples and CronJob configurations
- Performance tuning guidelines for different Azure tiers
- Security hardening recommendations and compliance checklists
- Benchmarking methodologies and expected performance metrics

### Planned
- Support for additional file formats (MSG, EML, HTML)
- Real-time indexing with file system watchers
- Multi-language support
- Web UI for management
- API endpoint for programmatic access
- Advanced analytics and reporting