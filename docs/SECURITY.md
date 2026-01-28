# Security Best Practices

This guide outlines security best practices for deploying and operating AzureSearch FileShare Indexer in production environments.

## Table of Contents

- [Secrets Management](#secrets-management)
- [Azure Service Security](#azure-service-security)
- [Network Security](#network-security)
- [Access Control](#access-control)
- [Data Protection](#data-protection)
- [Compliance & Auditing](#compliance--auditing)
- [Security Checklist](#security-checklist)

---

## Secrets Management

### ❌ Don't: Hard-Code Secrets

```python
# NEVER do this
AZURE_SEARCH_KEY = "abcd1234efgh5678"
OPENAI_KEY = "sk-xxxxxxxxx"
```

### ✅ Do: Use Environment Variables

```python
import os
from dotenv import load_dotenv

load_dotenv()
AZURE_SEARCH_KEY = os.getenv("AZURE_SEARCH_ADMIN_KEY")
```

### Azure Key Vault (Recommended for Production)

**1. Store secrets in Key Vault:**

```bash
az keyvault secret set \
  --vault-name "your-vault-name" \
  --name "azure-search-key" \
  --value "your-actual-key"
```

**2. Retrieve in code:**

```python
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient

# Use managed identity (no credentials in code!)
credential = DefaultAzureCredential()
client = SecretClient(
    vault_url="https://your-vault-name.vault.azure.net/",
    credential=credential
)

azure_search_key = client.get_secret("azure-search-key").value
```

**3. Configure in .env:**

```env
# Instead of actual keys
AZURE_KEYVAULT_URL=https://your-vault-name.vault.azure.net/
USE_MANAGED_IDENTITY=true
```

### Managed Identity Setup

**Enable on Azure VM/Container:**

```bash
az vm identity assign --name your-vm --resource-group your-rg
```

**Grant Key Vault access:**

```bash
az keyvault set-policy \
  --name your-vault-name \
  --object-id <managed-identity-id> \
  --secret-permissions get list
```

### Environment File Security

**Protect .env files:**

```bash
# Set restrictive permissions
chmod 600 .env

# Ensure .env is in .gitignore
echo ".env" >> .gitignore
```

**Validate .gitignore:**

```bash
# Verify .env is not tracked
git check-ignore .env
# Should output: .env
```

---

## Azure Service Security

### Azure Search Security

**1. Use Query Keys for Read-Only Access:**

```python
# Admin key (write operations only)
AZURE_SEARCH_ADMIN_KEY = os.getenv("AZURE_SEARCH_ADMIN_KEY")

# Query key for search operations (less privileged)
AZURE_SEARCH_QUERY_KEY = os.getenv("AZURE_SEARCH_QUERY_KEY")

# Use appropriate key
from azure.search.documents import SearchClient
from azure.core.credentials import AzureKeyCredential

# For searching (use query key)
search_client = SearchClient(
    endpoint=endpoint,
    index_name=index_name,
    credential=AzureKeyCredential(AZURE_SEARCH_QUERY_KEY)
)

# For indexing (use admin key)
from azure.search.documents import SearchIndexClient
index_client = SearchIndexClient(
    endpoint=endpoint,
    credential=AzureKeyCredential(AZURE_SEARCH_ADMIN_KEY)
)
```

**2. Enable Network Access Controls:**

```bash
# Restrict to specific IPs
az search service update \
  --name your-search-service \
  --resource-group your-rg \
  --ip-rules "203.0.113.0/24,198.51.100.42"
```

**3. Enable Private Endpoint:**

```bash
az network private-endpoint create \
  --name search-private-endpoint \
  --resource-group your-rg \
  --vnet-name your-vnet \
  --subnet your-subnet \
  --private-connection-resource-id "/subscriptions/.../Microsoft.Search/searchServices/your-service" \
  --group-id searchService \
  --connection-name search-connection
```

### Azure OpenAI Security

**1. Use Role-Based Access Control (RBAC):**

```bash
# Assign least privilege role
az role assignment create \
  --assignee <managed-identity-id> \
  --role "Cognitive Services OpenAI User" \
  --scope "/subscriptions/.../Microsoft.CognitiveServices/accounts/your-openai"
```

**2. Enable Content Filtering:**

```python
from openai import AzureOpenAI

client = AzureOpenAI(
    api_version="2024-02-15-preview",
    azure_endpoint=endpoint,
    azure_ad_token_provider=token_provider,
)

# Content filters are automatically applied
response = client.embeddings.create(
    input="text to embed",
    model="text-embedding-ada-002"
)
```

**3. Monitor Abuse:**

```bash
# Set up Azure Monitor alerts for unusual patterns
az monitor metrics alert create \
  --name "openai-high-usage" \
  --resource your-openai-resource-id \
  --condition "total TokenTransaction > 1000000" \
  --window-size 5m
```

---

## Network Security

### Virtual Network Integration

**1. Deploy in VNet:**

```bash
# Create VNet
az network vnet create \
  --name indexer-vnet \
  --resource-group your-rg \
  --address-prefix 10.0.0.0/16 \
  --subnet-name indexer-subnet \
  --subnet-prefix 10.0.1.0/24
```

**2. Use Service Endpoints:**

```bash
# Enable service endpoints
az network vnet subnet update \
  --name indexer-subnet \
  --resource-group your-rg \
  --vnet-name indexer-vnet \
  --service-endpoints Microsoft.CognitiveServices Microsoft.Search
```

### Network Security Groups (NSG)

**Restrict inbound traffic:**

```bash
az network nsg create \
  --name indexer-nsg \
  --resource-group your-rg

# Allow HTTPS only
az network nsg rule create \
  --name allow-https \
  --nsg-name indexer-nsg \
  --resource-group your-rg \
  --priority 100 \
  --destination-port-ranges 443 \
  --access Allow \
  --protocol Tcp

# Deny all other inbound
az network nsg rule create \
  --name deny-all-inbound \
  --nsg-name indexer-nsg \
  --resource-group your-rg \
  --priority 4096 \
  --access Deny \
  --protocol '*'
```

### TLS/SSL Configuration

**Enforce HTTPS:**

```python
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# Force TLS 1.2+
session = requests.Session()
session.mount('https://', HTTPAdapter(
    max_retries=Retry(total=3, backoff_factor=1)
))

# Verify SSL certificates
response = session.get(url, verify=True)
```

---

## Access Control

### Principle of Least Privilege

**Grant minimal permissions:**

```bash
# Read-only access to file share
az storage share-rm create \
  --storage-account your-storage \
  --name documents \
  --quota 100

# Grant read-only SAS token
az storage share generate-sas \
  --account-name your-storage \
  --name documents \
  --permissions rl \
  --expiry 2026-12-31
```

### Azure AD Authentication

**Use Azure AD instead of keys:**

```python
from azure.identity import DefaultAzureCredential

# Automatically uses:
# 1. Environment variables
# 2. Managed identity
# 3. Azure CLI credentials
# 4. Visual Studio Code credentials
credential = DefaultAzureCredential()

# Use with Azure services
from azure.search.documents import SearchClient

client = SearchClient(
    endpoint=endpoint,
    index_name=index_name,
    credential=credential
)
```

### Service Principal

**Create and use service principal:**

```bash
# Create service principal
az ad sp create-for-rbac \
  --name "azure-search-indexer-sp" \
  --role "Cognitive Services OpenAI User" \
  --scopes /subscriptions/<subscription-id>

# Output includes:
# appId (CLIENT_ID)
# password (CLIENT_SECRET)
# tenant (TENANT_ID)
```

**Use in code:**

```python
from azure.identity import ClientSecretCredential

credential = ClientSecretCredential(
    tenant_id=os.getenv("AZURE_TENANT_ID"),
    client_id=os.getenv("AZURE_CLIENT_ID"),
    client_secret=os.getenv("AZURE_CLIENT_SECRET")
)
```

---

## Data Protection

### Data in Transit

**1. Always use HTTPS:**

```python
# Ensure all endpoints use HTTPS
AZURE_SEARCH_ENDPOINT = "https://your-service.search.windows.net"
AZURE_OPENAI_ENDPOINT = "https://your-openai.openai.azure.com/"
```

**2. Verify certificates:**

```python
import certifi

response = requests.get(url, verify=certifi.where())
```

### Data at Rest

**1. Enable encryption:**

```bash
# Azure Search encrypts by default with Microsoft-managed keys

# Use customer-managed keys for additional control
az search service update \
  --name your-search \
  --resource-group your-rg \
  --identity-type SystemAssigned

az search service update \
  --name your-search \
  --resource-group your-rg \
  --encryption-key-vault-key-identifier "https://your-vault.vault.azure.net/keys/your-key"
```

**2. Secure local cache:**

```python
import os
from cryptography.fernet import Fernet

# Generate encryption key (store securely!)
key = Fernet.generate_key()
cipher = Fernet(key)

# Encrypt cached data
def cache_embedding(text, embedding):
    encrypted = cipher.encrypt(pickle.dumps(embedding))
    with open(cache_file, 'wb') as f:
        f.write(encrypted)

# Decrypt cached data
def load_cached_embedding(cache_file):
    with open(cache_file, 'rb') as f:
        encrypted = f.read()
    return pickle.loads(cipher.decrypt(encrypted))
```

### Data Sanitization

**Remove sensitive data:**

```python
import re

def sanitize_text(text):
    # Remove email addresses
    text = re.sub(r'\b[\w\.-]+@[\w\.-]+\.\w+\b', '[EMAIL]', text)
    
    # Remove phone numbers
    text = re.sub(r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b', '[PHONE]', text)
    
    # Remove SSNs
    text = re.sub(r'\b\d{3}-\d{2}-\d{4}\b', '[SSN]', text)
    
    # Remove credit card numbers
    text = re.sub(r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b', '[CARD]', text)
    
    return text
```

### PII Detection with Azure AI

```python
from azure.ai.textanalytics import TextAnalyticsClient

text_analytics_client = TextAnalyticsClient(
    endpoint=endpoint,
    credential=credential
)

def detect_pii(text):
    response = text_analytics_client.recognize_pii_entities([text])
    for doc in response:
        for entity in doc.entities:
            print(f"PII found: {entity.text} (Type: {entity.category})")
            # Redact or handle appropriately
```

---

## Compliance & Auditing

### Logging

**Enable comprehensive logging:**

```python
import logging
from logging.handlers import RotatingFileHandler
import json

# Structured logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

handler = RotatingFileHandler(
    'security.log',
    maxBytes=10*1024*1024,  # 10MB
    backupCount=5
)

formatter = logging.Formatter(
    '{"timestamp":"%(asctime)s","level":"%(levelname)s",'
    '"message":"%(message)s","user":"%(user)s"}'
)
handler.setFormatter(formatter)
logger.addHandler(handler)

# Log security events
logger.info("Document indexed", extra={
    'user': 'system',
    'action': 'index',
    'document': doc_id,
    'ip_address': '10.0.1.5'
})
```

### Azure Monitor Integration

```python
from opencensus.ext.azure.log_exporter import AzureLogHandler

logger.addHandler(AzureLogHandler(
    connection_string='InstrumentationKey=your-key'
))

# Logs automatically sent to Azure Monitor
logger.info("Security event", extra={
    'custom_dimensions': {
        'event_type': 'authentication',
        'result': 'success'
    }
})
```

### Audit Trail

**Track all operations:**

```python
from datetime import datetime
import json

class AuditLogger:
    def __init__(self, audit_file='audit.log'):
        self.audit_file = audit_file
    
    def log(self, action, user, resource, status, details=None):
        entry = {
            'timestamp': datetime.utcnow().isoformat(),
            'action': action,
            'user': user,
            'resource': resource,
            'status': status,
            'details': details or {}
        }
        
        with open(self.audit_file, 'a') as f:
            f.write(json.dumps(entry) + '\n')

audit = AuditLogger()

# Log operations
audit.log(
    action='INDEX_DOCUMENT',
    user='system',
    resource='document-123.pdf',
    status='success',
    details={'chunks': 5, 'tokens': 2500}
)
```

### Compliance Standards

**GDPR Compliance:**

```python
# Right to erasure
def delete_user_data(user_id):
    # Delete from search index
    search_client.delete_documents(
        documents=[{"id": doc_id} for doc_id in user_docs]
    )
    
    # Delete from cache
    cache.delete(user_id)
    
    # Log deletion
    audit.log(
        action='DELETE_USER_DATA',
        user=user_id,
        resource='all_documents',
        status='success'
    )
```

**HIPAA Compliance:**
- Use Business Associate Agreement (BAA) with Azure
- Enable encryption at rest and in transit
- Implement access controls and audit logging
- Regular security assessments

---

## Security Checklist

### Pre-Deployment

- [ ] All secrets stored in Key Vault
- [ ] Managed identity configured
- [ ] Network security groups configured
- [ ] Private endpoints enabled
- [ ] TLS 1.2+ enforced
- [ ] Role-based access control implemented
- [ ] Data sanitization in place
- [ ] Audit logging enabled

### Production

- [ ] Regular security updates applied
- [ ] Access keys rotated every 90 days
- [ ] Security logs monitored
- [ ] Alerts configured for anomalies
- [ ] Backup and recovery tested
- [ ] Incident response plan documented
- [ ] Compliance requirements met
- [ ] Third-party dependencies audited

### Monitoring

- [ ] Azure Monitor enabled
- [ ] Log Analytics configured
- [ ] Security Center enabled
- [ ] Threat detection active
- [ ] Regular security scans
- [ ] Penetration testing scheduled
- [ ] Vulnerability assessments quarterly

---

## Incident Response

### Security Incident Plan

**1. Detection:**
- Monitor Azure Security Center alerts
- Review audit logs daily
- Set up automated alerting

**2. Response:**
```bash
# Immediate: Rotate compromised keys
az keyvault secret set \
  --vault-name your-vault \
  --name azure-search-key \
  --value new-key

# Revoke access
az role assignment delete \
  --assignee compromised-identity \
  --role "Cognitive Services OpenAI User"
```

**3. Investigation:**
- Review audit logs
- Check access patterns
- Identify affected resources

**4. Recovery:**
- Restore from backup if needed
- Apply security patches
- Update access controls

**5. Post-Incident:**
- Document incident
- Update security procedures
- Conduct lessons learned review

---

## Additional Resources

- [Azure Security Best Practices](https://learn.microsoft.com/azure/security/)
- [Azure Search Security](https://learn.microsoft.com/azure/search/search-security-overview)
- [Azure Key Vault](https://learn.microsoft.com/azure/key-vault/)
- [Azure AD Authentication](https://learn.microsoft.com/azure/active-directory/)
- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [CIS Azure Foundations Benchmark](https://www.cisecurity.org/benchmark/azure)
