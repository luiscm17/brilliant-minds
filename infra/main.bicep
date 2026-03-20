param namePrefix string = 'foundry'
param uniqueSuffix string = take(uniqueString(resourceGroup().id), 5)
param aiFoundryName string = 'fd-${namePrefix}-${uniqueSuffix}'
param aiProjectName string = 'pj-${namePrefix}-${uniqueSuffix}'
param location string = 'westus'

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
    modelDeploymentName: 'grok-3-dev'
    modelName: 'grok-3'
    modelFormat: 'xAI'
    modelVersion: '1'
  }
}

output foundryId string = aiFoundry.id
output foundryName string = aiFoundry.name
output foundryEndpoint string = aiFoundry.properties.endpoint
output foundryIdentityPrincipalId string = aiFoundry.identity.principalId
output projectId string = aiProjectModule.outputs.projectId
output modelDeploymentName string = generativeModelModule.outputs.modelDeploymentName
