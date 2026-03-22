"""Service to configure and provide Azure SearchIndexClient and index name."""

from azure.core.credentials import AzureKeyCredential
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
        endpoint = AISearchSettings.get_endpoint()
        api_key = AISearchSettings.get_api_key()
        index_name = AISearchSettings.get_index_name()

        self._client = SearchIndexClient(
            endpoint=endpoint,
            credential=AzureKeyCredential(api_key),
        )
        self._index_name = index_name

    def get_client(self) -> SearchIndexClient:
        """
        Retrieve the configured SearchIndexClient instance.

        Returns:
            SearchIndexClient: The Azure Search Index client.
        """
        return self._client

    def get_index_name(self) -> str:
        """
        Retrieve the configured search index name.

        Returns:
            str: The name of the search index.
        """
        return self._index_name
