@description('Bicep module for deploying a embedding model within an existing AI Project.')
param resourceName string


@description('Embedding Model Deployment.')
param embeddingModelDeploymentName string

@description('Model Name')
param embeddingModelName string

@description('Model format to be deployed.')
param embeddingModelFormat string

@description('Model version to be deployed.')
param embeddingModelVersion string

@description('SKU capacity.')
param skuCapacityEmbedding int

@description('SKU name for the deployment.')
param skuNameEmbedding string = 'GlobalStandard'


resource aiFoundryAccount 'Microsoft.CognitiveServices/accounts@2025-09-01' existing = {
  name: resourceName
}

resource embeddingModel 'Microsoft.CognitiveServices/accounts/deployments@2025-09-01' = {
  parent: aiFoundryAccount
  name: embeddingModelDeploymentName
  sku: {
    name: skuNameEmbedding
    capacity: skuCapacityEmbedding
  }
  properties: {
    model: {
      name: embeddingModelName
      format: embeddingModelFormat
      version: embeddingModelVersion
    }
  }
}

output embeddingModelId string = embeddingModel.id
output embeddingModelName string = embeddingModel.name
