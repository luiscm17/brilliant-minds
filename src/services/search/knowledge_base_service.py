"""Service for creating and deploying Azure AI Search knowledge bases."""

from azure.search.documents.indexes.models import (
    AzureOpenAIVectorizerParameters,
    KnowledgeBase,
    KnowledgeBaseAzureOpenAIModel,
    KnowledgeRetrievalLowReasoningEffort,
    KnowledgeRetrievalOutputMode,
    KnowledgeSourceReference,
)

from src.config.settings import KnowledgeBaseSettings, KnowledgeSourceSettings, OpenAISettings
from src.services.search.search_index_service import SearchIndexService


class KnowledgeBaseService:
    """Builds and deploys knowledge bases for agentic retrieval."""

    def __init__(self) -> None:
        self._index_service = SearchIndexService()

    def _build_model(self) -> KnowledgeBaseAzureOpenAIModel:
        """Build and configure the Azure OpenAI model for the knowledge base."""
        azure_params = AzureOpenAIVectorizerParameters(
            resource_url=OpenAISettings.ENDPOINT,
            deployment_name=OpenAISettings.CHAT_MODEL,
            model_name=OpenAISettings.MODEL_NAME,
            api_key=OpenAISettings.API_KEY,
        )
        return KnowledgeBaseAzureOpenAIModel(azure_open_ai_parameters=azure_params)

    def create_and_deploy(self, knowledge_source_name: str | None = None) -> None:
        """Create and deploy a knowledge base with the specified knowledge source."""
        knowledge_base = KnowledgeBase(
            name=KnowledgeBaseSettings.get_name(),
            description=KnowledgeBaseSettings.get_description(),
            knowledge_sources=[
                KnowledgeSourceReference(
                    name=knowledge_source_name or KnowledgeBaseSettings.get_name()
                )
            ],
            models=[self._build_model()],
            output_mode=KnowledgeRetrievalOutputMode.ANSWER_SYNTHESIS,
            retrieval_reasoning_effort=KnowledgeRetrievalLowReasoningEffort(),
            answer_instructions=KnowledgeBaseSettings.get_answer_instructions(),
            retrieval_instructions=KnowledgeBaseSettings.get_retrieval_instructions(),
        )
        client = self._index_service.get_client()
        client.create_or_update_knowledge_base(knowledge_base)
