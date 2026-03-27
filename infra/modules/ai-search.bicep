@description('Azure region used for the deployment of all resources.')
param location string = resourceGroup().location

@description('Set of tags to apply to all resources.')
param tags object = {}

@description('Replica count for the Azure Search service.')
param replicas int = 1

@description('Partition count for the Azure Search service.')
param partitions int = 1

@description('The name of the Azure Search service.')
param searchServiceName string

@description('The SKU for AI Search service')
@allowed([
  'free'
  'basic'
  'standard'
])
param sku string = 'basic'

resource searchService 'Microsoft.Search/searchServices@2025-05-01' = {
  name: searchServiceName
  location: location
  properties: {
    authOptions: {
      apiKeyOnly: {}
    }
    disableLocalAuth: false
    encryptionWithCmk: {
      enforcement: 'Disabled'
    }
    hostingMode: 'Default'
    networkRuleSet: {
      ipRules: [
        
      ]
    }
    partitionCount: partitions
    publicNetworkAccess: 'Enabled'
    replicaCount: replicas
  }
  sku: {
    name: sku
  }
  tags: tags
}

output searchName string = searchService.name
output searchId string = searchService.id
output searchEndpoint string = searchService.properties.hostingMode
