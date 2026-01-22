# Deployment Guide

Comprehensive guide for deploying AzureSearch FileShare Indexer in various environments.

---

## Table of Contents

- [Deployment Options](#deployment-options)
- [Local Deployment](#local-deployment)
- [Windows Server Deployment](#windows-server-deployment)
- [Azure Virtual Machine](#azure-virtual-machine)
- [Azure Functions (Serverless)](#azure-functions-serverless)
- [Docker Container](#docker-container)
- [Kubernetes (AKS)](#kubernetes-aks)
- [CI/CD Pipeline](#cicd-pipeline)
- [Monitoring and Maintenance](#monitoring-and-maintenance)
- [Scaling Strategies](#scaling-strategies)

---

## Deployment Options

### Comparison Matrix

| Option | Cost | Complexity | Scalability | Best For |
|--------|------|------------|-------------|----------|
| Local Workstation | Low | Low | Limited | Development, testing |
| Windows Server | Medium | Medium | Medium | On-premises, scheduled jobs |
| Azure VM | Medium | Medium | High | Hybrid scenarios |
| Azure Functions | Low | Low | Very High | Event-driven, serverless |
| Docker | Medium | Medium | High | Containerized environments |
| Kubernetes | High | High | Very High | Enterprise, multi-tenant |

---

## Local Deployment

### For Development and Testing

#### Setup
```bash
# Clone repository
git clone https://github.com/YOUR_USERNAME/AzureSearch-FileShare-Indexer.git
cd AzureSearch-FileShare-Indexer

# Create virtual environment
python -m venv .venv
.venv\Scripts\activate  # Windows
# source .venv/bin/activate  # Linux/Mac

# Install dependencies
pip install -r requirements.txt

# Configure
cp .env.example .env
# Edit .env with your settings
```

#### Run Manually
```bash
# Create index
python scripts/create_vector_index.py

# Index files
python scripts/index_files_vector.py

# Search
python scripts/search_demo.py "your query"
```

#### Advantages
- ✅ Quick setup
- ✅ Easy debugging
- ✅ No infrastructure costs

#### Limitations
- ❌ Not suitable for production
- ❌ Requires manual execution
- ❌ Single point of failure

---

## Windows Server Deployment

### Scheduled Indexing with Task Scheduler

#### 1. Install Application
```powershell
# Create application directory
New-Item -ItemType Directory -Path "C:\Apps\FileShareIndexer"

# Copy files
Copy-Item -Path "C:\Source\AzureSearch-FileShare-Indexer\*" -Destination "C:\Apps\FileShareIndexer" -Recurse

# Create virtual environment
cd C:\Apps\FileShareIndexer
python -m venv .venv

# Install dependencies
.venv\Scripts\pip.exe install -r requirements.txt
```

#### 2. Create Configuration
```powershell
# Create .env file
@"
AZURE_SEARCH_ENDPOINT=https://your-search.search.windows.net
AZURE_SEARCH_KEY=your-key-here
AZURE_OPENAI_ENDPOINT=https://your-openai.openai.azure.com
AZURE_OPENAI_KEY=your-key-here
FILE_SHARE_PATH=\\\\SERVER\\Share\\Documents
LOG_FILE=C:\Apps\FileShareIndexer\logs\indexer.log
"@ | Out-File -FilePath "C:\Apps\FileShareIndexer\.env" -Encoding UTF8
```

#### 3. Create Batch Script

Create `C:\Apps\FileShareIndexer\run_indexer.bat`:
```batch
@echo off
cd /d C:\Apps\FileShareIndexer
call .venv\Scripts\activate.bat
python scripts\index_files_vector.py
if errorlevel 1 (
    echo Indexing failed with error code %errorlevel%
    exit /b %errorlevel%
)
echo Indexing completed successfully
```

#### 4. Create Scheduled Task
```powershell
# Create scheduled task for daily indexing at 2 AM
$action = New-ScheduledTaskAction -Execute "C:\Apps\FileShareIndexer\run_indexer.bat" -WorkingDirectory "C:\Apps\FileShareIndexer"

$trigger = New-ScheduledTaskTrigger -Daily -At 2am

$principal = New-ScheduledTaskPrincipal -UserId "DOMAIN\ServiceAccount" -LogonType Password -RunLevel Highest

$settings = New-ScheduledTaskSettingsSet -StartWhenAvailable -RestartCount 3 -RestartInterval (New-TimeSpan -Minutes 5)

Register-ScheduledTask -TaskName "FileShare Indexer" -Action $action -Trigger $trigger -Principal $principal -Settings $settings -Description "Daily indexing of file share documents"
```

#### 5. Email Notifications

Create `C:\Apps\FileShareIndexer\scripts\notify_admin.ps1`:
```powershell
param(
    [string]$Subject,
    [string]$Body
)

$From = "indexer@company.com"
$To = "admin@company.com"
$SMTPServer = "smtp.company.com"

Send-MailMessage -From $From -To $To -Subject $Subject -Body $Body -SmtpServer $SMTPServer
```

Modify batch script:
```batch
@echo off
cd /d C:\Apps\FileShareIndexer
call .venv\Scripts\activate.bat

python scripts\index_files_vector.py > logs\last_run.log 2>&1

if errorlevel 1 (
    powershell -File scripts\notify_admin.ps1 -Subject "Indexing Failed" -Body "Check logs at C:\Apps\FileShareIndexer\logs\last_run.log"
    exit /b %errorlevel%
) else (
    powershell -File scripts\notify_admin.ps1 -Subject "Indexing Completed" -Body "Indexing completed successfully"
)
```

#### Advantages
- ✅ Reliable scheduled execution
- ✅ Windows integrated authentication
- ✅ Good for on-premises file shares

#### Limitations
- ❌ Requires Windows Server license
- ❌ Manual maintenance
- ❌ Limited scalability

---

## Azure Virtual Machine

### Cloud-Based Scheduled Execution

#### 1. Create Azure VM
```bash
# Create resource group
az group create --name fileshare-indexer-rg --location eastus

# Create VM
az vm create \
  --resource-group fileshare-indexer-rg \
  --name indexer-vm \
  --image Win2022Datacenter \
  --size Standard_D2s_v3 \
  --admin-username azureuser \
  --admin-password 'SecurePassword123!' \
  --public-ip-sku Standard
```

#### 2. Configure VM

Connect via RDP and follow Windows Server deployment steps above.

#### 3. Network Configuration
```bash
# Allow outbound HTTPS to Azure services
az vm open-port --resource-group fileshare-indexer-rg --name indexer-vm --port 443

# Configure private endpoint for file share (if using Azure Files)
az network private-endpoint create \
  --resource-group fileshare-indexer-rg \
  --name fileshare-endpoint \
  --vnet-name indexer-vnet \
  --subnet default \
  --private-connection-resource-id /subscriptions/.../storageAccounts/... \
  --group-id file \
  --connection-name fileshare-connection
```

#### 4. Managed Identity (Recommended)
```bash
# Enable system-assigned managed identity
az vm identity assign --resource-group fileshare-indexer-rg --name indexer-vm

# Get managed identity principal ID
$principalId = az vm identity show --resource-group fileshare-indexer-rg --name indexer-vm --query principalId -o tsv

# Grant access to Azure AI Search
az role assignment create \
  --role "Search Index Data Contributor" \
  --assignee $principalId \
  --scope /subscriptions/.../resourceGroups/.../providers/Microsoft.Search/searchServices/...
```

Update code to use managed identity:
```python
from azure.identity import DefaultAzureCredential
from azure.search.documents import SearchClient

credential = DefaultAzureCredential()
search_client = SearchClient(
    endpoint=Config.AZURE_SEARCH_ENDPOINT,
    index_name=Config.AZURE_SEARCH_INDEX_NAME,
    credential=credential
)
```

#### Advantages
- ✅ Cloud-based reliability
- ✅ Managed identity support
- ✅ Easy scaling
- ✅ Azure backup integration

#### Limitations
- ❌ Higher cost than on-premises
- ❌ Requires Azure subscription
- ❌ VM maintenance overhead

---

## Azure Functions (Serverless)

### Event-Driven, Serverless Deployment

#### 1. Create Function App Structure
```
FileShareIndexerFunction/
├── function_app.py
├── requirements.txt
├── host.json
├── local.settings.json
└── shared_code/
    ├── __init__.py
    └── indexer.py
```

#### 2. `function_app.py`
```python
import azure.functions as func
import logging
import os
import sys

# Add shared code to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'shared_code'))

from src.vector_indexer import VectorIndexer
from config import Config

app = func.FunctionApp()

@app.schedule(schedule="0 0 2 * * *", arg_name="timer", run_on_startup=False)
def scheduled_indexing(timer: func.TimerRequest) -> None:
    """
    Runs daily at 2 AM UTC
    Schedule format: {second} {minute} {hour} {day} {month} {day-of-week}
    """
    logging.info('Starting scheduled indexing...')
    
    try:
        indexer = VectorIndexer()
        stats = indexer.index_directory(
            directory_path=Config.FILE_SHARE_PATH,
            recursive=True,
            show_progress=False
        )
        
        logging.info(f"Indexing completed: {stats['successful_files']} files, {stats['total_chunks']} chunks")
        
    except Exception as e:
        logging.error(f"Indexing failed: {e}")
        raise

@app.blob_trigger(arg_name="blob", path="documents/{name}",
                  connection="AzureWebJobsStorage")
def blob_trigger_indexing(blob: func.InputStream):
    """
    Triggered when new blob is uploaded
    """
    logging.info(f'Blob trigger: {blob.name}')
    
    # Download blob content
    content = blob.read()
    
    # Save temporarily and index
    temp_path = f"/tmp/{blob.name}"
    with open(temp_path, 'wb') as f:
        f.write(content)
    
    # Index the file
    indexer = VectorIndexer()
    chunks = indexer.index_file(temp_path)
    
    logging.info(f'Indexed {chunks} chunks from {blob.name}')
```

#### 3. `requirements.txt`
```txt
azure-functions
azure-search-documents==11.6.0
azure-identity==1.25.1
openai==1.54.0
python-docx==1.2.0
PyPDF2==3.0.1
openpyxl==3.1.5
python-dotenv==1.0.1
tiktoken==0.7.0
loguru==0.7.2
```

#### 4. Deploy to Azure
```bash
# Create Function App
az functionapp create \
  --resource-group fileshare-indexer-rg \
  --consumption-plan-location eastus \
  --runtime python \
  --runtime-version 3.11 \
  --functions-version 4 \
  --name fileshare-indexer-func \
  --storage-account indexerstorage \
  --os-type Linux

# Configure app settings
az functionapp config appsettings set \
  --name fileshare-indexer-func \
  --resource-group fileshare-indexer-rg \
  --settings \
    AZURE_SEARCH_ENDPOINT="https://your-search.search.windows.net" \
    AZURE_SEARCH_KEY="your-key" \
    AZURE_OPENAI_ENDPOINT="https://your-openai.openai.azure.com" \
    AZURE_OPENAI_KEY="your-key" \
    FILE_SHARE_PATH="/mnt/fileshare"

# Deploy
func azure functionapp publish fileshare-indexer-func
```

#### 5. Mount Azure File Share
```bash
# Create storage account and file share
az storage account create \
  --name indexerfiles \
  --resource-group fileshare-indexer-rg \
  --location eastus

az storage share create \
  --name documents \
  --account-name indexerfiles

# Mount to function app
az webapp config storage-account add \
  --resource-group fileshare-indexer-rg \
  --name fileshare-indexer-func \
  --custom-id fileshare \
  --storage-type AzureFiles \
  --share-name documents \
  --account-name indexerfiles \
  --mount-path /mnt/fileshare \
  --access-key $(az storage account keys list --resource-group fileshare-indexer-rg --account-name indexerfiles --query '[0].value' -o tsv)
```

#### Advantages
- ✅ Serverless (no VM management)
- ✅ Pay-per-execution pricing
- ✅ Auto-scaling
- ✅ Event-driven triggers
- ✅ Built-in monitoring

#### Limitations
- ❌ 10-minute execution timeout (Consumption plan)
- ❌ Cold start delays
- ❌ Limited local storage
- ❌ Requires Azure Files for file share

---

## Docker Container

### Containerized Deployment

#### 1. Create `Dockerfile`
```dockerfile
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create logs directory
RUN mkdir -p logs

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Run indexer
CMD ["python", "scripts/index_files_vector.py"]
```

#### 2. Create `.dockerignore`
```
.venv
.git
.env
__pycache__
*.pyc
*.pyo
*.pyd
.pytest_cache
htmlcov
dist
build
*.egg-info
logs/
.cache/
test_files/
```

#### 3. Build and Run
```bash
# Build image
docker build -t fileshare-indexer:latest .

# Run container
docker run -d \
  --name indexer \
  -v /path/to/fileshare:/mnt/fileshare:ro \
  -v /path/to/logs:/app/logs \
  -e AZURE_SEARCH_ENDPOINT="https://your-search.search.windows.net" \
  -e AZURE_SEARCH_KEY="your-key" \
  -e AZURE_OPENAI_ENDPOINT="https://your-openai.openai.azure.com" \
  -e AZURE_OPENAI_KEY="your-key" \
  -e FILE_SHARE_PATH="/mnt/fileshare" \
  fileshare-indexer:latest
```

#### 4. Docker Compose

Create `docker-compose.yml`:
```yaml
version: '3.8'

services:
  indexer:
    build: .
    container_name: fileshare-indexer
    volumes:
      - /path/to/fileshare:/mnt/fileshare:ro
      - ./logs:/app/logs
    environment:
      - AZURE_SEARCH_ENDPOINT=${AZURE_SEARCH_ENDPOINT}
      - AZURE_SEARCH_KEY=${AZURE_SEARCH_KEY}
      - AZURE_OPENAI_ENDPOINT=${AZURE_OPENAI_ENDPOINT}
      - AZURE_OPENAI_KEY=${AZURE_OPENAI_KEY}
      - FILE_SHARE_PATH=/mnt/fileshare
      - LOG_LEVEL=INFO
    restart: unless-stopped
    networks:
      - indexer-network

networks:
  indexer-network:
    driver: bridge
```

Run with:
```bash
docker-compose up -d
```

#### 5. Scheduled Execution with Cron

Create `docker-compose-cron.yml`:
```yaml
version: '3.8'

services:
  indexer-cron:
    build: .
    container_name: fileshare-indexer-cron
    volumes:
      - /path/to/fileshare:/mnt/fileshare:ro
      - ./logs:/app/logs
      - ./crontab:/etc/cron.d/indexer-cron
    environment:
      - AZURE_SEARCH_ENDPOINT=${AZURE_SEARCH_ENDPOINT}
      - AZURE_SEARCH_KEY=${AZURE_SEARCH_KEY}
      - AZURE_OPENAI_ENDPOINT=${AZURE_OPENAI_ENDPOINT}
      - AZURE_OPENAI_KEY=${AZURE_OPENAI_KEY}
      - FILE_SHARE_PATH=/mnt/fileshare
    command: cron -f
    restart: unless-stopped
```

Create `crontab`:
```
# Run daily at 2 AM
0 2 * * * cd /app && python scripts/index_files_vector.py >> /app/logs/cron.log 2>&1
```

#### Advantages
- ✅ Consistent environment
- ✅ Easy deployment
- ✅ Version control for infrastructure
- ✅ Portable across platforms

#### Limitations
- ❌ Requires Docker knowledge
- ❌ Overhead of containerization
- ❌ Network configuration complexity

---

## Kubernetes (AKS)

### Enterprise-Grade Container Orchestration

#### 1. Create Kubernetes Resources

**`deployment.yaml`**:
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: fileshare-indexer
  namespace: indexing
spec:
  replicas: 1
  selector:
    matchLabels:
      app: fileshare-indexer
  template:
    metadata:
      labels:
        app: fileshare-indexer
    spec:
      containers:
      - name: indexer
        image: youracr.azurecr.io/fileshare-indexer:latest
        env:
        - name: AZURE_SEARCH_ENDPOINT
          valueFrom:
            secretKeyRef:
              name: indexer-secrets
              key: search-endpoint
        - name: AZURE_SEARCH_KEY
          valueFrom:
            secretKeyRef:
              name: indexer-secrets
              key: search-key
        - name: AZURE_OPENAI_ENDPOINT
          valueFrom:
            secretKeyRef:
              name: indexer-secrets
              key: openai-endpoint
        - name: AZURE_OPENAI_KEY
          valueFrom:
            secretKeyRef:
              name: indexer-secrets
              key: openai-key
        - name: FILE_SHARE_PATH
          value: "/mnt/fileshare"
        volumeMounts:
        - name: fileshare
          mountPath: /mnt/fileshare
          readOnly: true
        - name: logs
          mountPath: /app/logs
        resources:
          requests:
            memory: "2Gi"
            cpu: "1"
          limits:
            memory: "4Gi"
            cpu: "2"
      volumes:
      - name: fileshare
        azureFile:
          secretName: azure-file-secret
          shareName: documents
          readOnly: true
      - name: logs
        emptyDir: {}
```

**`cronjob.yaml`**:
```yaml
apiVersion: batch/v1
kind: CronJob
metadata:
  name: fileshare-indexer-cron
  namespace: indexing
spec:
  schedule: "0 2 * * *"  # Daily at 2 AM
  jobTemplate:
    spec:
      template:
        spec:
          containers:
          - name: indexer
            image: youracr.azurecr.io/fileshare-indexer:latest
            env:
            - name: AZURE_SEARCH_ENDPOINT
              valueFrom:
                secretKeyRef:
                  name: indexer-secrets
                  key: search-endpoint
            - name: AZURE_SEARCH_KEY
              valueFrom:
                secretKeyRef:
                  name: indexer-secrets
                  key: search-key
            volumeMounts:
            - name: fileshare
              mountPath: /mnt/fileshare
              readOnly: true
          restartPolicy: OnFailure
          volumes:
          - name: fileshare
            azureFile:
              secretName: azure-file-secret
              shareName: documents
              readOnly: true
```

**`secrets.yaml`**:
```yaml
apiVersion: v1
kind: Secret
metadata:
  name: indexer-secrets
  namespace: indexing
type: Opaque
stringData:
  search-endpoint: "https://your-search.search.windows.net"
  search-key: "your-search-key"
  openai-endpoint: "https://your-openai.openai.azure.com"
  openai-key: "your-openai-key"
---
apiVersion: v1
kind: Secret
metadata:
  name: azure-file-secret
  namespace: indexing
type: Opaque
stringData:
  azurestorageaccountname: "yourstorageaccount"
  azurestorageaccountkey: "your-storage-key"
```

#### 2. Deploy to AKS
```bash
# Create AKS cluster
az aks create \
  --resource-group fileshare-indexer-rg \
  --name indexer-aks \
  --node-count 2 \
  --node-vm-size Standard_D2s_v3 \
  --enable-managed-identity \
  --generate-ssh-keys

# Get credentials
az aks get-credentials --resource-group fileshare-indexer-rg --name indexer-aks

# Create namespace
kubectl create namespace indexing

# Apply configurations
kubectl apply -f secrets.yaml
kubectl apply -f cronjob.yaml

# Verify
kubectl get cronjobs -n indexing
kubectl get pods -n indexing
```

#### 3. Monitoring
```bash
# View logs
kubectl logs -n indexing -l app=fileshare-indexer --tail=100

# View cron job history
kubectl get jobs -n indexing

# Describe cron job
kubectl describe cronjob fileshare-indexer-cron -n indexing
```

#### Advantages
- ✅ Enterprise-grade orchestration
- ✅ Auto-scaling
- ✅ Self-healing
- ✅ Rolling updates
- ✅ Resource management

#### Limitations
- ❌ Complex setup
- ❌ Higher operational overhead
- ❌ Requires Kubernetes expertise
- ❌ Higher cost

---

## CI/CD Pipeline

### Automated Deployment with GitHub Actions

#### `.github/workflows/deploy.yml`
```yaml
name: Build and Deploy

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

env:
  AZURE_FUNCTIONAPP_NAME: fileshare-indexer-func
  PYTHON_VERSION: '3.11'

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: ${{ env.PYTHON_VERSION }}
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        pip install pytest pytest-cov
    
    - name: Run tests
      run: |
        pytest tests/ -v --cov=src --cov-report=xml
    
    - name: Upload coverage
      uses: codecov/codecov-action@v3
      with:
        files: ./coverage.xml

  build-and-deploy:
    needs: test
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: ${{ env.PYTHON_VERSION }}
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
    
    - name: Zip artifact for deployment
      run: zip -r release.zip . -x '*.git*' -x '*tests*' -x '*.venv*'
    
    - name: Deploy to Azure Function App
      uses: Azure/functions-action@v1
      with:
        app-name: ${{ env.AZURE_FUNCTIONAPP_NAME }}
        package: release.zip
        publish-profile: ${{ secrets.AZURE_FUNCTIONAPP_PUBLISH_PROFILE }}
    
    - name: Notify deployment
      if: success()
      run: |
        echo "Deployment successful to ${{ env.AZURE_FUNCTIONAPP_NAME }}"
```

---

## Monitoring and Maintenance

### Application Insights Integration
```python
from opencensus.ext.azure.log_exporter import AzureLogHandler
import logging

# Configure Application Insights
logger = logging.getLogger(__name__)
logger.addHandler(AzureLogHandler(
    connection_string='InstrumentationKey=your-key-here'
))

# Log custom metrics
logger.info('Indexing started', extra={'custom_dimensions': {'files_count': 100}})
```

### Health Checks

Create `scripts/health_check.py`:
```python
"""
Health check script for monitoring
"""

import sys
from src.index_manager import IndexManager
from src.search import SearchClient

def check_search_service():
    """Check if search service is accessible"""
    try:
        manager = IndexManager()
        indexes = manager.list_indexes()
        return True, f"Found {len(indexes)} indexes"
    except Exception as e:
        return False, str(e)

def check_index_health():
    """Check if index has recent documents"""
    try:
        search = SearchClient()
        results = search.search("*", top=1)
        return True, "Index is accessible"
    except Exception as e:
        return False, str(e)

def main():
    checks = [
        ("Search Service", check_search_service),
        ("Index Health", check_index_health)
    ]
    
    all_passed = True
    for name, check_func in checks:
        passed, message = check_func()
        status = "✅" if passed else "❌"
        print(f"{status} {name}: {message}")
        if not passed:
            all_passed = False
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())
```

### Backup Strategy
```bash
# Backup index schema
python -c "
from src.index_manager import IndexManager
import json

manager = IndexManager()
# Export index definitions
# Save to JSON file
"

# Backup configuration
cp .env .env.backup.$(date +%Y%m%d)

# Backup cache
tar -czf cache_backup_$(date +%Y%m%d).tar.gz .cache/
```

---

## Scaling Strategies

### Horizontal Scaling

**Partition by directory:**
```python
# Instance 1: /dept1
FILE_SHARE_PATH=\\\\SERVER\\Share\\dept1

# Instance 2: /dept2
FILE_SHARE_PATH=\\\\SERVER\\Share\\dept2

# Instance 3: /dept3
FILE_SHARE_PATH=\\\\SERVER\\Share\\dept3
```

### Vertical Scaling

**Increase resources:**
```env
# More workers for faster processing
MAX_WORKERS=16

# Larger batches
BATCH_SIZE=500

# Smaller chunks for less memory
CHUNK_SIZE=800
```

### Load Balancing

Use Azure Load Balancer or Application Gateway for distributing search queries across multiple search replicas.

---

## Security Checklist

- [ ] Use managed identities instead of keys
- [ ] Enable Azure Key Vault for secret management
- [ ] Configure network security groups
- [ ] Enable Azure AI Search firewall
- [ ] Use private endpoints for Azure services
- [ ] Implement least privilege access
- [ ] Enable audit logging
- [ ] Rotate keys regularly
- [ ] Encrypt data at rest
- [ ] Use TLS 1.2+ for all connections

---

## Cost Optimization

### Tips

1. **Use Consumption Plan for Azure Functions** if workload is intermittent
2. **Enable incremental indexing** to reduce API calls
3. **Cache embeddings** to avoid regeneration
4. **Use appropriate Azure AI Search tier** (Basic for < 100K docs)
5. **Schedule indexing during off-peak hours**
6. **Monitor and optimize batch sizes**
7. **Use spot VMs** for non-critical workloads

### Cost Estimation

| Component | Tier | Monthly Cost (USD) |
|-----------|------|-------------------|
| Azure AI Search | Basic | $75 |
| Azure OpenAI | Standard | $50-200 (usage-based) |
| Azure Functions | Consumption | $10-50 |
| Azure VM | B2s | $30 |
| Azure Files | Standard | $20 |
| **Total** | | **$185-375** |

---

For production deployment assistance, contact: edgar@mcochieng.com