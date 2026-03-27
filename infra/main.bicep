@description('The prefix for the resource names.')
param namePrefix string = 'foundry'

@description('The unique suffix for the resource names.')
param uniqueSuffix string = take(uniqueString(resourceGroup().id), 5)

// Azure Foundry Service
@description('The name of the AI Foundry.')
param aiFoundryName string = 'fd-${namePrefix}-${uniqueSuffix}'

@description('The name of the AI Project.')
param aiProjectName string = 'pj-${namePrefix}-${uniqueSuffix}'

@description('The location of the resources.')
param location string = 'eastus'

// AI Search Service
@description('The SKU AI Search service.')
param skuSearch string = 'standard'

// Generative Model Service
@description('Model deployment name.')
param modelDeploymentName string = 'gpt-4.1m-dev'

@description('Model name.')
param modelName string = 'gpt-4.1-mini'

@description('Model format.')
param modelFormat string = 'OpenAI'

@description('Model version.')
param modelVersion string = '2025-04-14'

@description('The name of RAI policy.')
param raiPolicyName string = 'Microsoft.DefaultV2'

@description('SKU Generative Model capacity.')
param skuCapacity int = 100

// Embedding Model Service
@description('Embedding Model Deployment.')
param embeddingModelDeploymentName string = 'text-embedding-3-large'

@description('Model Name')
param embeddingModelName string = 'text-embedding-3-large'

@description('Model format to be deployed.')
param embeddingModelFormat string = 'OpenAI'

@description('Model version to be deployed.')
param embeddingModelVersion string = '1'

@description('SKU capacity.')
param skuCapacityEmbedding int = 120

@description('SKU name for the deployment.')
param skuNameEmbedding string = 'GlobalStandard'

var storageAccountName = 'st${namePrefix}${uniqueSuffix}'
var cosmosAccountName = 'cosmos-${namePrefix}-${uniqueSuffix}'
var searchServiceName = 'srch-${namePrefix}-${uniqueSuffix}'
var docIntelName = 'docintel-${namePrefix}-${uniqueSuffix}'

// ── AI Foundry (AIServices) ─────────────────────────────────────────────────
resource aiFoundry 'Microsoft.CognitiveServices/accounts@2025-09-01' = {
  name: aiFoundryName
  location: location
  identity: {
    type: 'SystemAssigned'
  }
  sku: {
    name: 'S0'
  }
  kind: 'AIServices'
  properties: {
    allowProjectManagement: true
    customSubDomainName: aiFoundryName
    disableLocalAuth: false
    publicNetworkAccess: 'Enabled'
  }
}

// ── AI Project ───────────────────────────────────────────────────────────────
module aiProjectModule 'modules/project.bicep' = {
  name: 'aiProjectDeployment'
  params: {
    aiProjectName: aiProjectName
    location: location
    resourceName: aiFoundry.name
  }
}

// ── Storage Account ──────────────────────────────────────────────────────────
module storageAccountModule 'modules/storage-account.bicep' = {
  name: 'storageDeployment'
  params: {
    storageAccountName: storageAccountName
    location: location
  }
}

// ── GPT-4o-mini deployment ───────────────────────────────────────────────────
module gptModel 'modules/generative-model.bicep' = {
  name: 'gptModelDeployment'
  params: {
    resourceName: aiFoundry.name
    modelDeploymentName: modelDeploymentName
    modelName: modelName
    modelFormat: modelFormat
    modelVersion: modelVersion
    skuCapacity: skuCapacity
    raiPolicyName: raiPolicyName
    
  }
  dependsOn: [
    aiProjectModule
  ]
}

module embeddingModelModule 'modules/embedding-model.bicep' = {
  name: 'embeddingModelDeployment'
  params: {
    resourceName: aiFoundry.name
    embeddingModelDeploymentName: embeddingModelDeploymentName
    embeddingModelName: embeddingModelName
    embeddingModelFormat: embeddingModelFormat
    embeddingModelVersion: embeddingModelVersion
    skuCapacityEmbedding: skuCapacityEmbedding
    skuNameEmbedding: skuNameEmbedding
  }
  dependsOn: [
    generativeModelModule
  ]
}

module aiSearchModule 'modules/ai-search.bicep' = {
  name: 'aiSearchDeployment'
  params: {
    searchServiceName: 'search-${namePrefix}-${uniqueSuffix}'
    location: location
    tags: {
      
    }
    sku: skuSearch
  }
}

// ── Embedding model (text-embedding-ada-002) ─────────────────────────────────
module embeddingModel 'modules/generative-model.bicep' = {
  name: 'embeddingModelDeployment'
  params: {
    resourceName: aiFoundry.name
    modelDeploymentName: 'text-embedding-ada-002'
    modelName: 'text-embedding-ada-002'
    modelFormat: 'OpenAI'
    modelVersion: '2'
    skuCapacity: 10
  }
  dependsOn: [gptModel]
}

// ── Cosmos DB (Serverless) ───────────────────────────────────────────────────
module cosmosModule 'modules/cosmos-db.bicep' = {
  name: 'cosmosDeployment'
  params: {
    accountName: cosmosAccountName
    location: location
    databaseName: 'docsimplify'
  }
}

// ── Azure AI Search (Free) ───────────────────────────────────────────────────
module searchModule 'modules/ai-search.bicep' = {
  name: 'searchDeployment'
  params: {
    serviceName: searchServiceName
    location: location
  }
}

// ── Document Intelligence (Free F0) ─────────────────────────────────────────
module docIntelModule 'modules/document-intelligence.bicep' = {
  name: 'docIntelDeployment'
  params: {
    accountName: docIntelName
    location: location
  }
}

// ── Outputs ──────────────────────────────────────────────────────────────────
output foundryName string = aiFoundry.name
output foundryEndpoint string = aiFoundry.properties.endpoint
output foundryIdentityPrincipalId string = aiFoundry.identity.principalId
output projectId string = aiProjectModule.outputs.projectId
output modelDeploymentName string = generativeModelModule.outputs.modelDeploymentName
output embeddingModelDeploymentName string = embeddingModelModule.outputs.embeddingModelName
output searchServiceId string = aiSearchModule.outputs.searchId
