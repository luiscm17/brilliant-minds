@description('Name of the AI Project.')
param aiProjectName string

@description('Location for the project.')
param location string = resourceGroup().location

@description('Parent AI Foundry account name.')
param resourceName string

@description('Tags for the project.')
param tags object = {}

resource aiFoundryAccount 'Microsoft.CognitiveServices/accounts@2025-09-01' existing = {
  name: resourceName
}

resource aiProject 'Microsoft.CognitiveServices/accounts/projects@2025-09-01' = {
  name: aiProjectName
  parent: aiFoundryAccount
  location: location
  identity: {
    type: 'SystemAssigned'
  }
  properties: {}
  tags: tags
}

output projectId string = aiProject.id
output projectName string = aiProject.name
output projectIdentityPrincipalId string = aiProject.identity.principalId
