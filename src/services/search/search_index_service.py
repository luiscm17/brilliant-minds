"""Service to configure Azure AI Search management clients."""

from azure.core.credentials import AzureKeyCredential
from azure.search.documents.indexes import SearchIndexClient, SearchIndexerClient

from src.config.settings import AzureSearchSettings


class SearchIndexService:
    """Wrapper for the Azure AI Search index management client."""

    def __init__(self) -> None:
        AzureSearchSettings.validate()
        credential = AzureKeyCredential(AzureSearchSettings.KEY)
        self._client = SearchIndexClient(
            endpoint=AzureSearchSettings.ENDPOINT,
            credential=credential,
        )
        self._indexer_client = SearchIndexerClient(
            endpoint=AzureSearchSettings.ENDPOINT,
            credential=credential,
        )

    def get_client(self) -> SearchIndexClient:
        return self._client

    def get_indexer_client(self) -> SearchIndexerClient:
        return self._indexer_client

    def get_index_name(self) -> str:
        return AzureSearchSettings.INDEX
