"""Service to configure and provide Azure SearchIndexClient and index name."""

from azure.identity import DefaultAzureCredential
from azure.search.documents.indexes import SearchIndexClient

from src.config.settings import AISearchSettings


class SearchIndexService:
    """
    Wrapper for Azure SearchIndexClient setup and retrieval along with index name.
    """

    def __init__(self) -> None:
        """
        Initialize the SearchIndexService using settings from AISearchSettings.

        Raises:
            ValueError: If settings are not properly configured.
        """
        AISearchSettings.validate()
        ai_search_endpoint = AISearchSettings.get_endpoint()
        ai_search_api_key = AISearchSettings.get_api_key()
        index_name = AISearchSettings.get_index_name()

        self._client_index = SearchIndexClient(
            endpoint=ai_search_endpoint,
            credential=DefaultAzureCredential(),
        )
        self._index_name = index_name

    def get_client(self) -> SearchIndexClient:
        """
        Retrieve the configured SearchIndexClient instance.

        Returns:
            SearchIndexClient: The Azure Search Index client.
        """
        return self._client_index

    def get_index_name(self) -> str:
        """
        Retrieve the configured search index name.

        Returns:
            str: The name of the search index.
        """
        return self._index_name
