"""Application settings loaded from environment variables."""

import os
from typing import Optional

from dotenv import load_dotenv

load_dotenv()

ENVIRONMENT = os.getenv("ENVIRONMENT", "development")


def _first_env(*names: str, default: Optional[str] = None) -> Optional[str]:
    """Return the first non-empty environment variable from a list of aliases."""
    for name in names:
        value = os.getenv(name)
        if value:
            return value
    return default


class AgentSettings:
    """Settings for Azure AI Project agents."""

    _AI_PROJECT_ENDPOINT: Optional[str] = _first_env("AI_PROJECT_ENDPOINT")
    _AI_MODEL_DEPLOYMENT_NAME: Optional[str] = _first_env(
        "AI_MODEL_DEPLOYMENT_NAME",
        "AOAI_DEPLOYMENT_NAME",
    )

    @classmethod
    def get_project_endpoint(cls) -> str:
        endpoint = cls._AI_PROJECT_ENDPOINT
        if not endpoint:
            raise ValueError("AI_PROJECT_ENDPOINT is not configured")
        return endpoint

    @classmethod
    def get_model_deployment_name(cls) -> str:
        model = cls._AI_MODEL_DEPLOYMENT_NAME
        if not model:
            raise ValueError("AI_MODEL_DEPLOYMENT_NAME is not configured")
        return model


class AuthSettings:
    """Settings for JWT authentication."""

    SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "change-me-in-production")
    ALGORITHM: str = os.getenv("JWT_ALGORITHM", "HS256")
    EXPIRE_MINUTES: int = int(os.getenv("JWT_EXPIRE_MINUTES", "60"))


class BlobStorageSettings:
    """Settings for Azure Blob Storage."""

    CONNECTION_STRING: Optional[str] = _first_env("AZURE_STORAGE_CONNECTION_STRING")
    CONTAINER: Optional[str] = _first_env(
        "AZURE_STORAGE_CONTAINER",
        default="documents",
    )

    @classmethod
    def validate(cls) -> None:
        if not cls.CONNECTION_STRING:
            raise ValueError("AZURE_STORAGE_CONNECTION_STRING is not configured")


class CosmosDBSettings:
    """Settings for Azure Cosmos DB."""

    ENDPOINT: Optional[str] = os.getenv("COSMOS_ENDPOINT")
    KEY: Optional[str] = os.getenv("COSMOS_KEY")
    DATABASE: str = os.getenv("COSMOS_DATABASE", "docsimplify")
    USERS_CONTAINER: str = os.getenv("COSMOS_USERS_CONTAINER", "users")
    DOCUMENTS_CONTAINER: str = os.getenv("COSMOS_DOCUMENTS_CONTAINER", "documents")
    CHATS_CONTAINER: str = os.getenv("COSMOS_CHATS_CONTAINER", "chats")
    SHARES_CONTAINER: str = os.getenv("COSMOS_SHARES_CONTAINER", "shares")

    @classmethod
    def validate(cls) -> None:
        if not cls.ENDPOINT:
            raise ValueError("COSMOS_ENDPOINT is not configured")
        if not cls.KEY:
            raise ValueError("COSMOS_KEY is not configured")


class AzureSearchSettings:
    """Settings for Azure AI Search (RAG)."""

    ENDPOINT: Optional[str] = _first_env("AZURE_SEARCH_ENDPOINT", "AI_SEARCH_ENDPOINT")
    KEY: Optional[str] = _first_env("AZURE_SEARCH_KEY", "AI_SEARCH_KEY")
    INDEX: str = _first_env(
        "AZURE_SEARCH_INDEX",
        "AI_SEARCH_INDEX_NAME",
        default="documents-index",
    ) or "documents-index"

    @classmethod
    def validate(cls) -> None:
        if not cls.ENDPOINT:
            raise ValueError("AZURE_SEARCH_ENDPOINT is not configured")
        if not cls.KEY:
            raise ValueError("AZURE_SEARCH_KEY is not configured")


class OpenAISettings:
    """Settings for Azure OpenAI (embeddings + completions)."""

    ENDPOINT: Optional[str] = _first_env("OPENAI_ENDPOINT", "AOAI_ENDPOINT")
    API_KEY: Optional[str] = _first_env("OPENAI_API_KEY", "AOAI_KEY")
    EMBEDDING_MODEL: str = _first_env(
        "OPENAI_EMBEDDING_MODEL",
        "EMBEDDING_MODEL_NAME",
        default="text-embedding-ada-002",
    ) or "text-embedding-ada-002"
    EMBEDDING_DEPLOYMENT: str = _first_env(
        "OPENAI_EMBEDDING_DEPLOYMENT",
        "EMBEDDING_MODEL_DEPLOYMENT_NAME",
        "OPENAI_EMBEDDING_MODEL",
        default="text-embedding-ada-002",
    ) or "text-embedding-ada-002"
    CHAT_MODEL: str = _first_env(
        "AI_MODEL_DEPLOYMENT_NAME",
        "AOAI_DEPLOYMENT_NAME",
        default="gpt-4o-mini",
    ) or "gpt-4o-mini"
    MODEL_NAME: str = _first_env(
        "OPENAI_MODEL_NAME",
        "AI_MODEL_NAME",
        default="gpt-4o-mini",
    ) or "gpt-4o-mini"


class AgenticRagSettings:
    """Settings for Azure AI Search knowledge sources and knowledge bases."""

    ENABLED: bool = (
        _first_env("AGENTIC_RAG_ENABLED", default="false") or "false"
    ).lower() == "true"
    KNOWLEDGE_SOURCE_NAME: str = _first_env(
        "KNOWLEDGE_SOURCE_NAME",
        default="docsimplify-knowledge-source",
    ) or "docsimplify-knowledge-source"
    KNOWLEDGE_SOURCE_DESCRIPTION: str = _first_env(
        "KNOWLEDGE_SOURCE_DESCRIPTION",
        default="Knowledge source built from uploaded DocSimplify documents",
    ) or "Knowledge source built from uploaded DocSimplify documents"
    KNOWLEDGE_BASE_NAME: str = _first_env(
        "KNOWLEDGE_BASE_NAME",
        default="docsimplify-knowledge-base",
    ) or "docsimplify-knowledge-base"
    KNOWLEDGE_BASE_DESCRIPTION: str = _first_env(
        "KNOWLEDGE_BASE_DESCRIPTION",
        default="Agentic retrieval knowledge base for DocSimplify",
    ) or "Agentic retrieval knowledge base for DocSimplify"
    ANSWER_INSTRUCTIONS: str = _first_env(
        "KNOWLEDGE_BASE_ANSWER_INSTRUCTIONS",
        default=(
            "Answer in Spanish when the user writes in Spanish, keep the tone calm, "
            "and cite document context when available."
        ),
    ) or (
        "Answer in Spanish when the user writes in Spanish, keep the tone calm, "
        "and cite document context when available."
    )
    RETRIEVAL_INSTRUCTIONS: str = _first_env(
        "KNOWLEDGE_BASE_RETRIEVAL_INSTRUCTIONS",
        default=(
            "Prefer uploaded user documents, decompose complex questions into smaller "
            "subqueries, and prioritize accessible explanations."
        ),
    ) or (
        "Prefer uploaded user documents, decompose complex questions into smaller "
        "subqueries, and prioritize accessible explanations."
    )


class MCPConnectionSettings:
    """Settings for exposing the Azure AI Search knowledge base as an MCP tool."""

    PROJECT_RESOURCE_ID: Optional[str] = os.getenv("AI_PROJECT_RESOURCE_ID")
    PROJECT_CONNECTION_NAME: str = os.getenv(
        "AI_PROJECT_CONNECTION_NAME",
        "rag-mcp-connection",
    )

    @classmethod
    def configured(cls) -> bool:
        return bool(cls.PROJECT_RESOURCE_ID)

    @classmethod
    def get_project_resource_id(cls) -> str:
        if not cls.PROJECT_RESOURCE_ID:
            raise ValueError("AI_PROJECT_RESOURCE_ID is not configured")
        return cls.PROJECT_RESOURCE_ID

    @classmethod
    def get_project_connection_name(cls) -> str:
        if not cls.PROJECT_CONNECTION_NAME:
            raise ValueError("AI_PROJECT_CONNECTION_NAME is not configured")
        return cls.PROJECT_CONNECTION_NAME

    @classmethod
    def get_project_connection_id(cls) -> str:
        return (
            f"{cls.get_project_resource_id()}/connections/"
            f"{cls.get_project_connection_name()}"
        )

    @classmethod
    def get_mcp_endpoint(cls) -> str:
        if not AzureSearchSettings.ENDPOINT:
            raise ValueError("AZURE_SEARCH_ENDPOINT is not configured")
        return (
            f"{AzureSearchSettings.ENDPOINT}/knowledgebases/"
            f"{AgenticRagSettings.KNOWLEDGE_BASE_NAME}/mcp"
            "?api-version=2025-11-01-Preview"
        )


class LayoutRagSettings:
    """Settings for the versioned layout-based RAG ingestion pipeline."""

    ENABLED: bool = (os.getenv("LAYOUT_RAG_ENABLED", "false").lower() == "true")
    INDEX_NAME: str = os.getenv("LAYOUT_RAG_INDEX_NAME", "documents-layout-rag-v2")
    DATASOURCE_NAME: str = os.getenv(
        "LAYOUT_RAG_DATASOURCE_NAME",
        "documents-layout-rag-v2-datasource",
    )
    SKILLSET_NAME: str = os.getenv(
        "LAYOUT_RAG_SKILLSET_NAME",
        "documents-layout-rag-v2-skillset",
    )
    INDEXER_NAME: str = os.getenv(
        "LAYOUT_RAG_INDEXER_NAME",
        "documents-layout-rag-v2-indexer",
    )
    MAX_CHUNK_LENGTH: int = int(os.getenv("LAYOUT_RAG_MAX_CHUNK_LENGTH", "2000"))
    OVERLAP_LENGTH: int = int(os.getenv("LAYOUT_RAG_OVERLAP_LENGTH", "200"))
    ENABLE_IMAGE_REFERENCES: bool = (
        os.getenv("LAYOUT_RAG_ENABLE_IMAGE_REFERENCES", "true").lower() == "true"
    )
    CONTENT_FIELD: str = os.getenv("LAYOUT_RAG_CONTENT_FIELD", "content")
    VECTOR_FIELD: str = os.getenv("LAYOUT_RAG_VECTOR_FIELD", "content_vector")
    TITLE_FIELD: str = os.getenv("LAYOUT_RAG_TITLE_FIELD", "document_title")
    PATH_FIELD: str = os.getenv("LAYOUT_RAG_PATH_FIELD", "metadata_storage_path")
    PAGE_FIELD: str = os.getenv("LAYOUT_RAG_PAGE_FIELD", "page_number")

    @classmethod
    def embedding_dimensions(cls) -> int:
        model_name = (OpenAISettings.EMBEDDING_MODEL or "").lower()
        if "3-large" in model_name:
            return 3072
        if "3-small" in model_name:
            return 1536
        return 1536


class DocumentIntelligenceSettings:
    """Settings for Azure Document Intelligence (Form Recognizer)."""

    ENDPOINT: Optional[str] = os.getenv("DOCUMENT_INTELLIGENCE_ENDPOINT")
    KEY: Optional[str] = os.getenv("DOCUMENT_INTELLIGENCE_KEY")
