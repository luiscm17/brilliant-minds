@description('Storage Account type to be created.')
@allowed([
  'Standard_LRS'
  'Standard_GRS'
])
param storageAccountType string = 'Standard_LRS'

@description('The name of the Storage Account to be created.')
param storageAccountName string


@description('The Storage Account Location.')
param location string

resource storageAccount 'Microsoft.Storage/storageAccounts@2025-06-01' = {
  name: storageAccountName
  location: location
  sku: {
    name: storageAccountType
  }
  kind: 'StorageV2'
  properties: {}
}

output storageAccountId string = storageAccount.id
output storageAccountName string = storageAccount.name
