"""Service for creating and ingesting Azure Blob Knowledge Sources."""

from azure.search.documents.indexes.models import (
    AzureBlobKnowledgeSource,
    AzureBlobKnowledgeSourceParameters,
    KnowledgeSourceIngestionParameters,
    KnowledgeSourceContentExtractionMode,
    KnowledgeBaseAzureOpenAIModel,
    AzureOpenAIVectorizerParameters,
    KnowledgeSourceAzureOpenAIVectorizer,
)

from src.config.settings import (
    AgentSettings,
    BlobStorageSettings,
    AISearchSettings,
    AzureOpenAISettings,
)
from src.services.search.search_index_service import SearchIndexService


class KnowledgeSourceService:
    """
    Service to build and ingest AzureBlobKnowledgeSource instances.
    """

    def __init__(self) -> None:
        """
        Validate settings and prepare the SearchIndexService.

        Raises:
            ValueError: If any required setting is missing or invalid.
        """
        BlobStorageSettings.validate()
        AISearchSettings.validate()
        self._index_service = SearchIndexService()

        # Azure OpenAI endpoint and key for embedding and chat models
        self._aoai_endpoint = AzureOpenAISettings.get_endpoint()
        self._aoai_key = AzureOpenAISettings.get_api_key()

    def create_knowledge_source(
        self, name: str, description: str
    ) -> AzureBlobKnowledgeSource:
        """
        Construct an AzureBlobKnowledgeSource with minimal extraction and default models.

        Args:
            name: Unique name for the knowledge source.
            description: Human-readable description.

        Returns:
            Configured AzureBlobKnowledgeSource instance.
        """
        # Build vectorizer parameters for embeddings
        embedding_params = AzureOpenAIVectorizerParameters(
            resource_url=self._aoai_endpoint,
            deployment_name=AgentSettings.get_model_deployment_name(),
            model_name=AgentSettings.get_model_deployment_name(),
            api_key=self._aoai_key,
        )

        # Build vectorizer parameters for chat completions
        chat_params = AzureOpenAIVectorizerParameters(
            resource_url=self._aoai_endpoint,
            deployment_name=AgentSettings.get_model_deployment_name(),
            model_name=AgentSettings.get_model_deployment_name(),
            api_key=self._aoai_key,
        )

        ingestion_params = KnowledgeSourceIngestionParameters(
            identity=None,
            disable_image_verbalization=False,
            content_extraction_mode=KnowledgeSourceContentExtractionMode.MINIMAL,
            embedding_model=KnowledgeSourceAzureOpenAIVectorizer(
                azure_open_ai_parameters=embedding_params
            ),
            chat_completion_model=KnowledgeBaseAzureOpenAIModel(
                azure_open_ai_parameters=chat_params
            ),
            ingestion_schedule=None,
            ingestion_permission_options=None,
        )

        blob_params = AzureBlobKnowledgeSourceParameters(
            connection_string=BlobStorageSettings.AZURE_STORAGE_CONNECTION_STRING,  # type: ignore
            container_name=BlobStorageSettings.AZURE_STORAGE_CONTAINER,  # type: ignore
            is_adls_gen2=False,
            ingestion_parameters=ingestion_params,
        )

        return AzureBlobKnowledgeSource(
            name=name,
            description=description,
            azure_blob_parameters=blob_params,
        )

    def ingest(self, ks: AzureBlobKnowledgeSource) -> None:
        """
        Ingest the given knowledge source into the Azure Search index.

        Args:
            ks: The AzureBlobKnowledgeSource to create or update.
        """
        client = self._index_service.get_client()
        client.create_or_update_knowledge_source(ks)
