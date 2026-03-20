# Azure AI Foundry - Grok-3 Deployment

Basic infrastructure to deploy Azure AI Foundry with Grok-3 model from xAI.

## 🏗️ Architecture

```yaml
AI Foundry Account
├── AI Project
├── Storage Account
└── Model Deployment (Grok-3)
```

## 📦 Resources Created

- **Azure AI Foundry Account** - Main cognitive services account
- **AI Project** - Logical container for development work
- **Storage Account** - Storage for project data
- **Model Deployment** - Grok-3 model deployment with xAI format

## 🚀 Quick Deploy

### Prerequisites

- Azure CLI installed
- Logged in to Azure (`az login`)

### Deployment Steps

1. **Create Resource Group**

   ```bash
   az group create --name <resource-group-name> --location westus
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
├── main.bicep                 # Main template
├── main.parameters.json       # Deployment parameters
├── modules/
│   ├── project.bicep         # AI Project module
│   ├── storage-account.bicep # Storage Account module
│   └── generative-model.bicep # Model deployment module
└── README.md                  
```

## ⚙️ Configuration

### Parameters

- `namePrefix`: Prefix for resource names (default: `docagent`)
- `location`: Azure region (default: `westus`)

### Model Configuration

- **Model**: grok-3
- **Format**: xAI
- **Version**: 1
- **SKU**: GlobalStandard (capacity: 10)

## 🔧 Customization

### Add New Services

The modular architecture makes it easy to add new services:

1. Create new module in `modules/` directory
2. Add module call in `main.bicep`
3. Update parameters as needed

## 📖 Learn More

- [Azure AI Foundry Documentation](https://learn.microsoft.com/azure/ai-foundry/)
- [Bicep Documentation](https://learn.microsoft.com/azure/azure-resource-manager/bicep/)
- [xAI Grok Models](https://x.ai/)

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
