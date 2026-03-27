# Azure AI Foundry - Complete Infrastructure Deployment

Complete infrastructure to deploy Azure AI Foundry with multiple AI models, search services, and storage.

## 🏗️ Architecture

```yaml
AI Foundry Account
├── AI Project
│   ├── Generative Model Deployment (<your-generative-model>)
│   └── Embedding Model Deployment (<your-embedding-model>)
├── AI Search Service
└── Storage Account
```

## 📦 Resources Created

- **Azure AI Foundry Account** - Main cognitive services account with system-assigned identity
- **AI Project** - Logical container for development work and model deployments
- **Generative Model Deployment** - Primary AI model with RAI policy and auto-upgrade
- **Embedding Model Deployment** - Text embedding model for vector operations
- **AI Search Service** - Cognitive search service with configurable SKU
- **Storage Account** - Standard storage for project data and assets

## 🚀 Quick Deploy

### Prerequisites

- Azure CLI installed
- Logged in to Azure (`az login`)
- Appropriate permissions for Cognitive Services and Storage resources

### Deployment Steps

1. **Create Resource Group**

   ```bash
   az group create --name <resource-group-name> --location eastus
   ```

2. **Preview Changes (Optional)**

   ```bash
   az deployment group what-if \
     --resource-group <resource-group-name> \
     --template-file main.bicep \
     --parameters main.parameters.json
   ```

3. **Deploy Resources**

   ```bash
   az deployment group create \
     --resource-group <resource-group-name> \
     --template-file main.bicep \
     --parameters main.parameters.json
   ```

## 📁 Template Structure

```yaml
infra/
├── main.bicep                 # Main orchestration template
├── main.parameters.json       # Deployment parameters
├── main.parameters.bicepparam # Bicep parameters file
└── modules/
    ├── project.bicep         # AI Project module
    ├── storage-account.bicep # Storage Account module
    ├── generative-model.bicep # Generative model deployment module
    ├── embedding-model.bicep # Embedding model deployment module
    └── ai-search.bicep       # AI Search service module
```

## ⚙️ Configuration

### Main Parameters

- `namePrefix`: Prefix for resource names (default: `foundry`)
- `location`: Azure region (default: `eastus`)

### Generative Model Configuration

- **Model Name**: `<your-generative-model>` (e.g., `gpt-4.1-mini`)
- **Format**: `<your-model-format>` (e.g., `OpenAI`, `xAI`)
- **Version**: `<your-model-version>` (e.g., `2025-04-14`)
- **SKU**: GlobalStandard (capacity: `<your-sku-capacity>`)

### Embedding Model Configuration

- **Model Name**: `<your-embedding-model>` (e.g., `text-embedding-3-large`)
- **Format**: `<your-embedding-format>` (e.g., `OpenAI`)
- **Version**: `<your-embedding-version>` (e.g., `1`)
- **SKU**: GlobalStandard (capacity: `<your-embedding-capacity>`)

### AI Search Configuration

- **SKU**: `<your-search-sku>` (e.g., `standard`, `basic`, `free`)
- **Replicas**: `<your-replica-count>` (default: 1)
- **Partitions**: `<your-partition-count>` (default: 1)

## 🔧 Customization

### Add New Model Deployments

1. Create new module in `modules/` directory
2. Add module call in `main.bicep` with proper dependencies
3. Update parameters as needed

### Modify Model Settings

Edit the parameters in `main.bicep` or `main.parameters.json`:

```bicep
param modelName string = '<your-model-name>'
param modelFormat string = '<your-model-format>'
param modelVersion string = '<your-model-version>'
param skuCapacity int = <your-capacity>
```

## 📖 Learn More

- [Azure AI Foundry Documentation](https://learn.microsoft.com/azure/ai-foundry/)
- [Bicep Documentation](https://learn.microsoft.com/azure/azure-resource-manager/bicep/)
- [Azure Cognitive Services](https://learn.microsoft.com/azure/cognitive-services/)

## 🔐 Security Notes

- API keys are not stored in the template
- Use Azure Key Vault for production credential management
- Consider using Managed Identity for applications
- Never commit API keys to version control

## 📋 Useful Commands

### List Available Models

```bash
# List available models for your Cognitive Services account
az cognitiveservices account list-models \
  --name <YOUR_AI_FOUNDRY_NAME> \
  --resource-group <YOUR_RESOURCE_GROUP> | \
  jq '.[] | { name: .name, format: .format, version: .version, sku: .skus[0].name, capacity: .skus[0].capacity.default }'
```

### Get Deployment Endpoints

```bash
# Get the endpoint URL for your AI Foundry account
az cognitiveservices account show \
  --name <YOUR_AI_FOUNDRY_NAME> \
  --resource-group <YOUR_RESOURCE_GROUP> \
  --query properties.endpoint -o tsv
```

### Check Deployment Status

```bash
# Check status of a specific model deployment
az cognitiveservices account deployment show \
  --deployment-name <YOUR_DEPLOYMENT_NAME> \
  --name <YOUR_AI_FOUNDRY_NAME> \
  --resource-group <YOUR_RESOURCE_GROUP> | \
  jq '.properties.provisioningState'
```

### List All Deployments

```bash
# List all model deployments
az cognitiveservices account deployment list \
  --name <YOUR_AI_FOUNDRY_NAME> \
  --resource-group <YOUR_RESOURCE_GROUP> | \
  jq '.[] | { name: .name, model: .properties.model, sku: .sku }'
```

## 🐛 Troubleshooting

### Common Issues

- **RequestConflict**: Ensure proper dependencies are set between model deployments
- **Quota exceeded**: Check your region's quota limits for Cognitive Services
- **Model not available**: Verify model availability in your selected region

### Get Deployment Logs

```bash
# Get detailed deployment operation logs
az deployment group operation list \
  --name <DEPLOYMENT_NAME> \
  --resource-group <YOUR_RESOURCE_GROUP>
```
