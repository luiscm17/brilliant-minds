"""Service for creating and ingesting Azure Blob knowledge sources."""

from azure.search.documents.indexes.models import (
    AzureBlobKnowledgeSource,
    AzureBlobKnowledgeSourceParameters,
    AzureOpenAIVectorizerParameters,
    KnowledgeBaseAzureOpenAIModel,
    KnowledgeSourceAzureOpenAIVectorizer,
    KnowledgeSourceContentExtractionMode,
    KnowledgeSourceIngestionParameters,
)

from src.config.settings import AgenticRagSettings, BlobStorageSettings, OpenAISettings
from src.services.search.search_index_service import SearchIndexService


class KnowledgeSourceService:
    """Creates and updates Azure AI Search knowledge sources backed by Blob Storage."""

    def __init__(self) -> None:
        BlobStorageSettings.validate()
        self._index_service = SearchIndexService()

    def create_knowledge_source(
        self,
        name: str | None = None,
        description: str | None = None,
    ) -> AzureBlobKnowledgeSource:
        embedding_params = AzureOpenAIVectorizerParameters(
            resource_url=OpenAISettings.ENDPOINT,
            deployment_name=OpenAISettings.EMBEDDING_DEPLOYMENT,
            model_name=OpenAISettings.EMBEDDING_MODEL,
            api_key=OpenAISettings.API_KEY,
        )
        chat_params = AzureOpenAIVectorizerParameters(
            resource_url=OpenAISettings.ENDPOINT,
            deployment_name=OpenAISettings.CHAT_MODEL,
            model_name=OpenAISettings.MODEL_NAME,
            api_key=OpenAISettings.API_KEY,
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
            connection_string=BlobStorageSettings.CONNECTION_STRING,
            container_name=BlobStorageSettings.CONTAINER,
            is_adls_gen2=False,
            ingestion_parameters=ingestion_params,
        )

        return AzureBlobKnowledgeSource(
            name=name or AgenticRagSettings.KNOWLEDGE_SOURCE_NAME,
            description=description or AgenticRagSettings.KNOWLEDGE_SOURCE_DESCRIPTION,
            azure_blob_parameters=blob_params,
        )

    def create_or_update(self, knowledge_source: AzureBlobKnowledgeSource) -> None:
        client = self._index_service.get_client()
        client.create_or_update_knowledge_source(knowledge_source)
