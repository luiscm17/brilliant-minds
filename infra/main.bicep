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

module aiProjectModule 'modules/project.bicep' = {
  name: 'aiProjectDeployment'
  params: {
    aiProjectName: aiProjectName
    location: location
    resourceName: aiFoundry.name
  }
}

module storageAccountModule 'modules/storage-account.bicep' = {
  params: {
    storageAccountName: 'st${namePrefix}${uniqueSuffix}'
    location: location
  }
}

module generativeModelModule 'modules/generative-model.bicep' = {
  name: 'generativeModelDeployment'
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

output foundryId string = aiFoundry.id
output foundryName string = aiFoundry.name
output foundryEndpoint string = aiFoundry.properties.endpoint
output foundryIdentityPrincipalId string = aiFoundry.identity.principalId
output projectId string = aiProjectModule.outputs.projectId
output modelDeploymentName string = generativeModelModule.outputs.modelDeploymentName
output embeddingModelDeploymentName string = embeddingModelModule.outputs.embeddingModelName
output searchServiceId string = aiSearchModule.outputs.searchId
