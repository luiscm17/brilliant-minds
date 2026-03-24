"""Service for creating and deploying Azure AI Search knowledge bases."""

from azure.search.documents.indexes.models import (
    AzureOpenAIVectorizerParameters,
    KnowledgeBase,
    KnowledgeBaseAzureOpenAIModel,
    KnowledgeRetrievalLowReasoningEffort,
    KnowledgeRetrievalOutputMode,
    KnowledgeSourceReference,
)

from src.config.settings import AgenticRagSettings, OpenAISettings
from src.services.search.search_index_service import SearchIndexService


class KnowledgeBaseService:
    """Builds and deploys knowledge bases for agentic retrieval."""

    def __init__(self) -> None:
        self._index_service = SearchIndexService()

    def _build_model(self) -> KnowledgeBaseAzureOpenAIModel:
        azure_params = AzureOpenAIVectorizerParameters(
            resource_url=OpenAISettings.ENDPOINT,
            deployment_name=OpenAISettings.CHAT_MODEL,
            model_name=OpenAISettings.MODEL_NAME,
            api_key=OpenAISettings.API_KEY,
        )
        return KnowledgeBaseAzureOpenAIModel(azure_open_ai_parameters=azure_params)

    def create_and_deploy(self, knowledge_source_name: str | None = None) -> None:
        knowledge_base = KnowledgeBase(
            name=AgenticRagSettings.KNOWLEDGE_BASE_NAME,
            description=AgenticRagSettings.KNOWLEDGE_BASE_DESCRIPTION,
            knowledge_sources=[
                KnowledgeSourceReference(
                    name=knowledge_source_name or AgenticRagSettings.KNOWLEDGE_SOURCE_NAME
                )
            ],
            models=[self._build_model()],
            output_mode=KnowledgeRetrievalOutputMode.ANSWER_SYNTHESIS,
            retrieval_reasoning_effort=KnowledgeRetrievalLowReasoningEffort(),
            answer_instructions=AgenticRagSettings.ANSWER_INSTRUCTIONS,
            retrieval_instructions=AgenticRagSettings.RETRIEVAL_INSTRUCTIONS,
        )
        client = self._index_service.get_client()
        client.create_or_update_knowledge_base(knowledge_base)
