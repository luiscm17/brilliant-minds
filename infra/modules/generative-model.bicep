@description('Bicep module for deploying a generative model within an existing AI Foundry account.')
param resourceName string

@description('Generative Model Deployment.')
param modelDeploymentName string

@description('Model Name')
param modelName string

@description('Model format to be deployed.')
param modelFormat string

@description('Model version to be deployed.')
param modelVersion string

@description('SKU capacity.')
param skuCapacity int

@description('SKU name for the deployment.')
param skuName string = 'GlobalStandard'

@description('The name of RAI policy.')
param raiPolicyName string


resource aiFoundryAccount 'Microsoft.CognitiveServices/accounts@2025-09-01' existing = {
  name: resourceName
}

resource modelDeployment 'Microsoft.CognitiveServices/accounts/deployments@2025-09-01' = {
  parent: aiFoundryAccount
  name: modelDeploymentName
  sku: {
    name: skuName
    capacity: skuCapacity
  }
  properties: {
    model: {
      name: modelName
      format: modelFormat
      version: modelVersion
    }
    raiPolicyName: raiPolicyName
    versionUpgradeOption: 'OnceNewDefaultVersionAvailable'
  }
}

output modelDeploymentId string = modelDeployment.id
output modelDeploymentName string = modelDeployment.name
