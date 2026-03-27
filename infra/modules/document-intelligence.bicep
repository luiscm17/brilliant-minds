@description('Name of the Document Intelligence account.')
param accountName string

@description('Location for the resource.')
param location string

resource docIntel 'Microsoft.CognitiveServices/accounts@2024-04-01-preview' = {
  name: accountName
  location: location
  kind: 'FormRecognizer'
  sku: {
    name: 'F0'
  }
  properties: {
    customSubDomainName: accountName
    publicNetworkAccess: 'Enabled'
  }
}

output endpoint string = docIntel.properties.endpoint
output accountName string = docIntel.name
