# Setup Guide

Complete guide for setting up AzureSearch FileShare Indexer in your environment.

---

## Table of Contents

- [Prerequisites](#prerequisites)
- [Azure Resources Setup](#azure-resources-setup)
- [Local Environment Setup](#local-environment-setup)
- [Configuration](#configuration)
- [Verification](#verification)
- [Environment-Specific Setup](#environment-specific-setup)
- [Troubleshooting](#troubleshooting)

---

## Prerequisites

### Software Requirements

| Software | Minimum Version | Recommended | Purpose |
|----------|----------------|-------------|---------|
| Python | 3.9 | 3.11+ | Core runtime |
| pip | 21.0+ | Latest | Package management |
| Git | 2.0+ | Latest | Version control |
| Azure CLI | 2.40+ | Latest | Azure management (optional) |

### Azure Subscription Requirements

- Active Azure subscription
- Permissions to create resources:
  - Azure AI Search service
  - Azure OpenAI service (for vector search)
  - Resource Group (if creating new)

### Network Requirements

- Outbound HTTPS access to:
  - `*.search.windows.net` (Azure AI Search)
  - `*.openai.azure.com` (Azure OpenAI)
  - `pypi.org` (Python packages)
- Access to file share (SMB, NFS, or local filesystem)

---

## Azure Resources Setup

### Option 1: Azure Portal (GUI)

#### 1. Create Azure AI Search Service

1. Navigate to [Azure Portal](https://portal.azure.com)
2. Click **"Create a resource"** → Search for **"Azure AI Search"**
3. Fill in the details:
   - **Subscription**: Your subscription
   - **Resource Group**: Create new or select existing
   - **Service name**: `your-search-service` (must be globally unique)
   - **Location**: Choose nearest region
   - **Pricing tier**: **Basic** (required for vector search)
     - Free tier does NOT support vector search
     - Basic tier supports up to 15 indexes, 2GB storage
4. Click **"Review + Create"** → **"Create"**
5. Wait for deployment (2-3 minutes)
6. Once deployed:
   - Go to resource
   - Navigate to **"Keys"** (left menu)
   - Copy **URL** and **Admin Key**

#### 2. Create Azure OpenAI Service

1. In Azure Portal, click **"Create a resource"** → Search for **"Azure OpenAI"**
2. Fill in the details:
   - **Subscription**: Your subscription
   - **Resource Group**: Same as search service
   - **Region**: Choose from available regions (limited availability)
   - **Name**: `your-openai-service`
   - **Pricing tier**: Standard S0
3. Click **"Review + Create"** → **"Create"**
4. Wait for deployment
5. Once deployed:
   - Go to resource
   - Click **"Keys and Endpoint"**
   - Copy **Endpoint** and **Key 1**

#### 3. Deploy Embedding Model

1. In your Azure OpenAI resource, navigate to **"Model deployments"**
2. Click **"Create new deployment"**
3. Configure:
   - **Model**: `text-embedding-3-large` (recommended) or `text-embedding-ada-002`
   - **Deployment name**: `text-embedding-3-large` (use same as model name for simplicity)
   - **Model version**: Latest available
   - **Deployment type**: Standard
   - **Tokens per Minute Rate Limit**: 120K (adjust based on needs)
4. Click **"Create"**
5. Wait for deployment to complete

### Option 2: Azure CLI (Command Line)
```bash
# Login to Azure
az login

# Set variables
RESOURCE_GROUP="fileshare-indexer-rg"
LOCATION="eastus"
SEARCH_SERVICE="your-search-service"
OPENAI_SERVICE="your-openai-service"

# Create resource group
az group create \
  --name $RESOURCE_GROUP \
  --location $LOCATION

# Create Azure AI Search service
az search service create \
  --name $SEARCH_SERVICE \
  --resource-group $RESOURCE_GROUP \
  --sku basic \
  --location $LOCATION

# Get search service keys
az search admin-key show \
  --service-name $SEARCH_SERVICE \
  --resource-group $RESOURCE_GROUP

# Create Azure OpenAI service
az cognitiveservices account create \
  --name $OPENAI_SERVICE \
  --resource-group $RESOURCE_GROUP \
  --kind OpenAI \
  --sku S0 \
  --location eastus \
  --yes

# Get OpenAI keys
az cognitiveservices account keys list \
  --name $OPENAI_SERVICE \
  --resource-group $RESOURCE_GROUP

# Deploy embedding model
az cognitiveservices account deployment create \
  --name $OPENAI_SERVICE \
  --resource-group $RESOURCE_GROUP \
  --deployment-name text-embedding-3-large \
  --model-name text-embedding-3-large \
  --model-version "1" \
  --model-format OpenAI \
  --sku-capacity 120 \
  --sku-name "Standard"
```

### Option 3: Terraform (Infrastructure as Code)
```hcl
# main.tf
terraform {
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 3.0"
    }
  }
}

provider "azurerm" {
  features {}
}

resource "azurerm_resource_group" "main" {
  name     = "fileshare-indexer-rg"
  location = "East US"
}

resource "azurerm_search_service" "main" {
  name                = "your-search-service"
  resource_group_name = azurerm_resource_group.main.name
  location            = azurerm_resource_group.main.location
  sku                 = "basic"
}

resource "azurerm_cognitive_account" "openai" {
  name                = "your-openai-service"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  kind                = "OpenAI"
  sku_name            = "S0"
}

output "search_endpoint" {
  value = "https://${azurerm_search_service.main.name}.search.windows.net"
}

output "openai_endpoint" {
  value = azurerm_cognitive_account.openai.endpoint
}
```

---

## Local Environment Setup

### 1. Clone Repository
```bash
# Using HTTPS
git clone https://github.com/YOUR_USERNAME/AzureSearch-FileShare-Indexer.git
cd AzureSearch-FileShare-Indexer

# Using SSH
git clone git@github.com:YOUR_USERNAME/AzureSearch-FileShare-Indexer.git
cd AzureSearch-FileShare-Indexer
```

### 2. Create Virtual Environment

#### Windows
```powershell
# Create virtual environment
python -m venv .venv

# Activate
.venv\Scripts\Activate.ps1

# If you get execution policy error:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

#### Linux/macOS
```bash
# Create virtual environment
python3 -m venv .venv

# Activate
source .venv/bin/activate
```

### 3. Install Dependencies
```bash
# Upgrade pip
python -m pip install --upgrade pip

# Install required packages
pip install -r requirements.txt

# Verify installation
pip list
```

### 4. Install Optional Dependencies
```bash
# For enhanced PDF extraction
pip install pdfplumber

# For image processing
pip install Pillow

# For OCR capabilities
pip install pytesseract

# For development tools
pip install -e ".[dev]"
```

---

## Configuration

### 1. Create Environment File
```bash
# Copy example file
cp .env.example .env

# Edit with your favorite editor
# Windows
notepad .env

# Linux/macOS
nano .env
# or
vim .env
```

### 2. Configure Azure Services

Edit `.env` file with your Azure credentials:
```env
#==============================================================================
# Azure AI Search Configuration
#==============================================================================
AZURE_SEARCH_ENDPOINT=https://your-search-service.search.windows.net
AZURE_SEARCH_KEY=your-admin-key-here
AZURE_SEARCH_INDEX_NAME=fileshare-documents
AZURE_SEARCH_VECTOR_INDEX_NAME=fileshare-vector-documents

#==============================================================================
# Azure OpenAI Configuration
#==============================================================================
AZURE_OPENAI_ENDPOINT=https://your-openai.openai.azure.com
AZURE_OPENAI_KEY=your-openai-key-here
AZURE_OPENAI_EMBEDDING_DEPLOYMENT=text-embedding-3-large
EMBEDDING_DIMENSIONS=3072

#==============================================================================
# File Share Configuration
#==============================================================================
# Windows UNC path
FILE_SHARE_PATH=\\\\SERVER\\Share\\Documents

# Linux/macOS mounted path
# FILE_SHARE_PATH=/mnt/share/documents

# Local path
# FILE_SHARE_PATH=C:\\Users\\YourName\\Documents
```

### 3. Configure File Share Access

#### Windows Network Share
```powershell
# Test access
Test-Path "\\SERVER\Share\Documents"

# Map network drive (optional)
New-PSDrive -Name "Z" -PSProvider FileSystem -Root "\\SERVER\Share\Documents" -Persist

# Use mapped drive in config
FILE_SHARE_PATH=Z:\
```

#### Linux/macOS Network Share
```bash
# Create mount point
sudo mkdir -p /mnt/share

# Mount SMB share
sudo mount -t cifs //SERVER/Share /mnt/share -o username=USER,password=PASS

# Or add to /etc/fstab for persistent mount
echo "//SERVER/Share /mnt/share cifs username=USER,password=PASS 0 0" | sudo tee -a /etc/fstab

# Use in config
FILE_SHARE_PATH=/mnt/share/documents
```

#### Azure File Share
```bash
# Mount Azure File Share
# Get storage account key from Azure Portal

# Linux
sudo mount -t cifs //storageaccount.file.core.windows.net/sharename /mnt/azurefiles \
  -o vers=3.0,username=storageaccount,password=STORAGE_KEY,dir_mode=0777,file_mode=0777

# Windows
net use Z: \\storageaccount.file.core.windows.net\sharename /u:AZURE\storageaccount STORAGE_KEY
```

### 4. Configure Logging
```env
#==============================================================================
# Logging Configuration
#==============================================================================
LOG_LEVEL=INFO
LOG_FILE=logs/indexer.log
LOG_TO_CONSOLE=true
LOG_FORMAT=detailed
```

Create logs directory:
```bash
mkdir logs
```

### 5. Advanced Configuration
```env
#==============================================================================
# Indexing Configuration
#==============================================================================
CHUNK_SIZE=1000
CHUNK_OVERLAP=200
BATCH_SIZE=100
MAX_WORKERS=4
INCREMENTAL_INDEXING=true

#==============================================================================
# Performance Configuration
#==============================================================================
CACHE_EMBEDDINGS=true
CACHE_DIR=.cache
MAX_RETRIES=3
RETRY_DELAY=2

#==============================================================================
# File Processing
#==============================================================================
SUPPORTED_EXTENSIONS=.txt,.docx,.pdf,.xlsx,.pptx
EXCLUDE_DIRECTORIES=temp,cache,node_modules
MAX_FILE_SIZE_MB=50
```

---

## Verification

### 1. Verify Configuration
```bash
# Test configuration
python -c "from config import Config; Config.validate(); print('✅ Configuration valid')"

# Print configuration (secrets masked)
python -c "from config import Config; Config.print_config()"
```

Expected output:
```
================================================================================
CONFIGURATION
================================================================================

Environment: DEVELOPMENT

Azure Search:
  endpoint: https://your-search.search.windows.net
  key: abcd1234...xyz9
  index_name: fileshare-documents
  vector_index_name: fileshare-vector-documents
  api_version: 2023-11-01

Azure Openai:
  endpoint: https://your-openai.openai.azure.com
  key: efgh5678...abc0
  embedding_deployment: text-embedding-3-large
  ...
================================================================================
```

### 2. Test Azure Connectivity
```bash
# Test Azure AI Search
python -c "
from src.index_manager import IndexManager
manager = IndexManager()
indexes = manager.list_indexes()
print(f'✅ Connected to Azure AI Search')
print(f'Found {len(indexes)} indexes: {indexes}')
"

# Test Azure OpenAI
python -c "
from openai import AzureOpenAI
from config import Config
client = AzureOpenAI(
    azure_endpoint=Config.AZURE_OPENAI_ENDPOINT,
    api_key=Config.AZURE_OPENAI_KEY,
    api_version=Config.AZURE_OPENAI_API_VERSION
)
response = client.embeddings.create(
    input='test',
    model=Config.AZURE_OPENAI_EMBEDDING_DEPLOYMENT
)
print(f'✅ Connected to Azure OpenAI')
print(f'Embedding dimensions: {len(response.data[0].embedding)}')
"
```

### 3. Test File Share Access
```bash
# Test file share access
python -c "
import os
from config import Config
path = Config.FILE_SHARE_PATH
if os.path.exists(path):
    files = os.listdir(path)
    print(f'✅ File share accessible')
    print(f'Found {len(files)} items in {path}')
else:
    print(f'❌ Cannot access {path}')
"
```

### 4. Create Test Index
```bash
# Create vector index
python scripts/create_vector_index.py
```

Expected output:
```
================================================================================
CREATING VECTOR-ENABLED INDEX WITH SEMANTIC SEARCH
================================================================================

Creating vector-enabled index: 'fileshare-vector-documents'
Vector dimensions: 3072 (text-embedding-3-large)
Semantic search: Enabled

✅ Vector index created successfully!
   - Text search: Enabled
   - Vector search: Enabled (HNSW algorithm)
   - Semantic ranking: Enabled
   - Hybrid search: Supported

✨ Index ready for vector embeddings!
   Next: Run 'python scripts/index_files_vector.py'
```

### 5. Index Sample Files
```bash
# Create test directory with sample files
mkdir test_files
echo "This is a test document about employee benefits." > test_files/test1.txt
echo "Azure AI Search provides powerful search capabilities." > test_files/test2.txt

# Index test files
python scripts/index_files_vector.py --path test_files
```

### 6. Test Search
```bash
# Run test search
python scripts/search_demo.py "employee benefits" --type hybrid --top 3
```

---

## Environment-Specific Setup

### Development Environment
```env
ENVIRONMENT=development
LOG_LEVEL=DEBUG
LOG_TO_CONSOLE=true
INCREMENTAL_INDEXING=false
CACHE_EMBEDDINGS=true
```

### Staging Environment
```env
ENVIRONMENT=staging
LOG_LEVEL=INFO
LOG_TO_CONSOLE=true
INCREMENTAL_INDEXING=true
CACHE_EMBEDDINGS=true
BATCH_SIZE=50
```

### Production Environment
```env
ENVIRONMENT=production
LOG_LEVEL=WARNING
LOG_TO_CONSOLE=false
LOG_FILE=/var/log/indexer/production.log
INCREMENTAL_INDEXING=true
CACHE_EMBEDDINGS=true
BATCH_SIZE=100
MAX_WORKERS=8
ENABLE_TELEMETRY=true
```

---

## Troubleshooting

### Common Setup Issues

#### Issue: "ModuleNotFoundError: No module named 'azure'"

**Solution:**
```bash
# Verify virtual environment is activated
# Windows
.venv\Scripts\Activate.ps1

# Linux/macOS
source .venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt
```

#### Issue: "Configuration validation failed"

**Solution:**
```bash
# Check .env file exists
ls -la .env

# Verify .env format (no spaces around =)
cat .env | grep AZURE_SEARCH_ENDPOINT

# Test configuration
python -c "from config import Config; Config.print_config()"
```

#### Issue: "Failed to connect to Azure AI Search"

**Solution:**
```bash
# Verify endpoint format (must include https://)
# Correct: https://your-service.search.windows.net
# Wrong: your-service.search.windows.net

# Test connectivity
curl https://your-search-service.search.windows.net?api-version=2023-11-01 \
  -H "api-key: YOUR_KEY"

# Check firewall rules in Azure Portal
# Search Service → Networking → Allow access from "All networks" (for testing)
```

#### Issue: "Embedding model not found"

**Solution:**
```bash
# Verify deployment name matches exactly
# Check in Azure Portal: OpenAI → Model deployments

# Common mistake: Using model name instead of deployment name
# Correct: AZURE_OPENAI_EMBEDDING_DEPLOYMENT=text-embedding-3-large
# If you named deployment differently: AZURE_OPENAI_EMBEDDING_DEPLOYMENT=my-embedding-model
```

#### Issue: "Cannot access file share"

**Solution:**
```bash
# Windows: Test UNC path
Test-Path "\\SERVER\Share"

# Check permissions
icacls "\\SERVER\Share"

# Linux/macOS: Test mount
ls -la /mnt/share

# Check mount options
mount | grep share
```

#### Issue: "Rate limit exceeded"

**Solution:**
```env
# Reduce batch size
BATCH_SIZE=10

# Increase retry delay
RETRY_DELAY=5

# Enable caching
CACHE_EMBEDDINGS=true

# Request quota increase in Azure Portal
# OpenAI → Quotas → Request increase
```

### Getting Help

If you encounter issues not covered here:

1. Check [Troubleshooting Guide](TROUBLESHOOTING.md)
2. Review [GitHub Issues](https://github.com/49ochieng/AzureSearch-FileShare-Indexer/issues)
3. Enable debug logging: `LOG_LEVEL=DEBUG`
4. Create a new issue with:
   - Error message
   - Configuration (with secrets removed)
   - Steps to reproduce

---

## Next Steps

After successful setup:

1. ✅ Read [Usage Guide](USAGE.md) for detailed usage instructions
2. ✅ Explore [Examples](../examples/) for common patterns
3. ✅ Review [API Documentation](API.md) for programmatic access
4. ✅ Plan your [Deployment Strategy](DEPLOYMENT.md)

---

**Setup Complete!** 🎉

You're ready to start indexing and searching your documents.