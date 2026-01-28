# Docker Deployment Guide

This guide explains how to deploy AzureSearch FileShare Indexer using Docker containers.

## Prerequisites

- Docker Engine 20.10+
- Docker Compose 2.0+
- Azure Search service
- Azure OpenAI service
- File share accessible from Docker host

## Quick Start

### 1. Build the Docker Image

```bash
docker build -t azure-search-indexer:latest .
```

### 2. Configure Environment Variables

Copy the `.env.example` file and configure your values:

```bash
cp .env.example .env.docker
```

Edit `.env.docker` with your Azure credentials and configuration.

### 3. Run with Docker Compose

```bash
docker-compose --env-file .env.docker up -d
```

## Configuration

### Environment Variables

All configuration is done through environment variables. Key variables:

#### Required
- `AZURE_SEARCH_ENDPOINT` - Your Azure Search endpoint
- `AZURE_SEARCH_ADMIN_KEY` - Azure Search admin key
- `AZURE_OPENAI_ENDPOINT` - Azure OpenAI endpoint
- `AZURE_OPENAI_KEY` - Azure OpenAI API key
- `FILE_SHARE_PATH` - Path to files to index (mounted volume)

#### Optional
- `INDEX_NAME` - Search index name (default: documents-index)
- `BATCH_SIZE` - Batch processing size (default: 10)
- `LOG_LEVEL` - Logging level (default: INFO)

See `.env.example` for complete list.

### Volume Mounts

The Docker container requires several volume mounts:

```yaml
volumes:
  - /path/to/documents:/data:ro  # Read-only file share
  - ./logs:/app/logs              # Log output
  - ./cache:/app/cache            # Embedding cache
```

## Usage Examples

### One-Time Indexing

Index files once and exit:

```bash
docker run --rm \
  --env-file .env.docker \
  -v /path/to/documents:/data:ro \
  -v $(pwd)/logs:/app/logs \
  azure-search-indexer:latest \
  python scripts/index_files_vector.py /data
```

### Scheduled Indexing with Cron

Run indexing on a schedule (requires cron in container or host):

```bash
# Add to crontab (runs daily at 2 AM)
0 2 * * * docker run --rm --env-file /path/to/.env.docker -v /data:/data:ro azure-search-indexer:latest python scripts/index_files_vector.py /data
```

### Interactive Shell

Access the container shell for debugging:

```bash
docker-compose exec indexer bash
```

### View Logs

```bash
# Follow logs
docker-compose logs -f indexer

# View specific number of lines
docker-compose logs --tail=100 indexer
```

## Advanced Configuration

### Custom Dockerfile

Modify the `Dockerfile` for specific needs:

```dockerfile
# Add custom dependencies
RUN pip install your-custom-package

# Add custom scripts
COPY scripts/custom_script.py /app/scripts/
```

### Multi-Stage Builds

For smaller production images:

```dockerfile
FROM python:3.11-slim as builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --user -r requirements.txt

FROM python:3.11-slim
WORKDIR /app
COPY --from=builder /root/.local /root/.local
COPY . .
ENV PATH=/root/.local/bin:$PATH
```

### Health Checks

Add health check to docker-compose.yml:

```yaml
healthcheck:
  test: ["CMD", "python", "-c", "import sys; sys.exit(0)"]
  interval: 30s
  timeout: 10s
  retries: 3
  start_period: 40s
```

## Kubernetes Deployment

### Create ConfigMap

```bash
kubectl create configmap indexer-config \
  --from-env-file=.env.docker
```

### Deploy Pod

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: azure-search-indexer
spec:
  containers:
  - name: indexer
    image: azure-search-indexer:latest
    envFrom:
    - configMapRef:
        name: indexer-config
    volumeMounts:
    - name: data
      mountPath: /data
      readOnly: true
    - name: logs
      mountPath: /app/logs
  volumes:
  - name: data
    persistentVolumeClaim:
      claimName: file-share-pvc
  - name: logs
    emptyDir: {}
```

### CronJob for Scheduled Indexing

```yaml
apiVersion: batch/v1
kind: CronJob
metadata:
  name: indexer-cronjob
spec:
  schedule: "0 2 * * *"  # Daily at 2 AM
  jobTemplate:
    spec:
      template:
        spec:
          containers:
          - name: indexer
            image: azure-search-indexer:latest
            command: ["python", "scripts/index_files_vector.py", "/data"]
            envFrom:
            - configMapRef:
                name: indexer-config
            volumeMounts:
            - name: data
              mountPath: /data
              readOnly: true
          restartPolicy: OnFailure
          volumes:
          - name: data
            persistentVolumeClaim:
              claimName: file-share-pvc
```

## Security Best Practices

### 1. Non-Root User

The Dockerfile already creates a non-root user. Verify:

```bash
docker run --rm azure-search-indexer:latest whoami
# Should output: appuser
```

### 2. Read-Only File System

Mount file share as read-only:

```yaml
volumes:
  - /path/to/documents:/data:ro
```

### 3. Secrets Management

**Option 1: Docker Secrets** (Swarm mode)

```bash
echo "your-api-key" | docker secret create azure_search_key -
```

```yaml
services:
  indexer:
    secrets:
      - azure_search_key
    environment:
      - AZURE_SEARCH_ADMIN_KEY_FILE=/run/secrets/azure_search_key
```

**Option 2: Azure Key Vault**

Use managed identity and Azure Key Vault for secrets:

```python
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient

credential = DefaultAzureCredential()
client = SecretClient(vault_url="https://your-vault.vault.azure.net/", credential=credential)
secret = client.get_secret("azure-search-key")
```

### 4. Network Security

Isolate with custom networks:

```yaml
networks:
  indexer-network:
    driver: bridge
    internal: true  # No external access
```

## Troubleshooting

### Container Won't Start

```bash
# Check logs
docker-compose logs indexer

# Check container status
docker ps -a

# Inspect container
docker inspect azure-search-indexer
```

### Permission Issues

```bash
# Fix volume permissions
sudo chown -R 1000:1000 logs/ cache/

# Run with user namespace
docker run --userns=host ...
```

### Network Connectivity

```bash
# Test Azure connectivity
docker run --rm --env-file .env.docker azure-search-indexer:latest \
  python -c "import requests; print(requests.get('https://management.azure.com').status_code)"
```

### Memory Issues

Increase Docker memory limits:

```yaml
services:
  indexer:
    deploy:
      resources:
        limits:
          memory: 4G
        reservations:
          memory: 2G
```

## Performance Optimization

### 1. Multi-Stage Build

Reduces image size by ~50%:

```dockerfile
FROM python:3.11-slim as builder
...
FROM python:3.11-slim
COPY --from=builder ...
```

### 2. Layer Caching

Order Dockerfile commands from least to most frequently changed:

```dockerfile
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .  # Changed most frequently
```

### 3. Parallel Processing

Configure batch size and workers:

```yaml
environment:
  - BATCH_SIZE=50
  - MAX_WORKERS=4
```

## Monitoring

### Container Stats

```bash
docker stats azure-search-indexer
```

### Prometheus Metrics

Add prometheus exporter:

```dockerfile
RUN pip install prometheus-client
```

```python
from prometheus_client import Counter, start_http_server

indexed_files = Counter('indexed_files_total', 'Total files indexed')
start_http_server(8000)
```

### Log Aggregation

Use Docker logging drivers:

```yaml
services:
  indexer:
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
```

## Maintenance

### Update Container

```bash
# Pull latest code
git pull

# Rebuild image
docker-compose build

# Restart with new image
docker-compose up -d
```

### Backup Cache

```bash
# Backup embedding cache
docker run --rm \
  -v azure-search-indexer_cache:/data \
  -v $(pwd)/backup:/backup \
  alpine tar czf /backup/cache-$(date +%Y%m%d).tar.gz -C /data .
```

### Clean Up

```bash
# Remove stopped containers
docker-compose down

# Remove volumes
docker-compose down -v

# Clean system
docker system prune -a
```

## Additional Resources

- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose Reference](https://docs.docker.com/compose/compose-file/)
- [Azure Container Instances](https://azure.microsoft.com/services/container-instances/)
- [Azure Kubernetes Service](https://azure.microsoft.com/services/kubernetes-service/)
