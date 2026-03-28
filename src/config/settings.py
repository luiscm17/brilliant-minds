"""Application settings loaded from environment variables."""

import os
from pathlib import Path
from typing import Optional, List

from dotenv import load_dotenv

load_dotenv()

ENVIRONMENT = os.getenv("ENVIRONMENT") or "development"

CORS_ORIGINS: List[str] = [
    origin.strip()
    for origin in os.getenv("CORS_ORIGINS", "").split(",")
    if origin.strip()
]


def _first_env(*names: str, default: Optional[str] = None) -> Optional[str]:
    """Return the first non-empty environment variable from a list of aliases."""
    for name in names:
        value = os.getenv(name)
        if value:
            return value
    return default


class AgentSettings:
    """Settings for Azure AI Project agents."""

    _AZURE_AI_PROJECT_ENDPOINT: Optional[str] = os.getenv("AZURE_AI_PROJECT_ENDPOINT")
    _AZURE_OPENAI_RESPONSES_DEPLOYMENT_NAME: Optional[str] = os.getenv(
        "AZURE_OPENAI_RESPONSES_DEPLOYMENT_NAME"
    )

    @classmethod
    def get_project_endpoint(cls) -> str:
        endpoint = cls._AZURE_AI_PROJECT_ENDPOINT
        if not endpoint:
            raise ValueError("AZURE_AI_PROJECT_ENDPOINT is not configured")
        assert isinstance(endpoint, str)
        return endpoint

    @classmethod
    def get_model_deployment_name(cls) -> str:
        model = cls._AZURE_OPENAI_RESPONSES_DEPLOYMENT_NAME
        if not model:
            raise ValueError("AZURE_AI_MODEL_DEPLOYMENT_NAME is not configured")
        assert isinstance(model, str)
        return model


class AuthSettings:
    """Settings for JWT authentication."""

    SECRET_KEY: str = os.getenv("JWT_SECRET_KEY") or "change-me-in-production"
    ALGORITHM: str = os.getenv("JWT_ALGORITHM") or "HS256"
    EXPIRE_MINUTES: int = int(os.getenv("JWT_EXPIRE_MINUTES", "60"))
    ALLOW_INSECURE_DEV_SECRET: bool = (
        _first_env(
            "ALLOW_INSECURE_DEV_SECRET",
            "ALLOW_INSECURE_DEV_JWT",
            default="false",
        ).lower()
        == "true"
    )

    @classmethod
    def get_secret_key(cls) -> str:
        if cls.SECRET_KEY:
            return cls.SECRET_KEY
        if cls.ALLOW_INSECURE_DEV_SECRET == "development":
            return "change-me-in-production"
        else:
            raise ValueError("JWT_SECRET_KEY is not configured for production use")


class AuthStorageSettings:
    """Settings for simple user storage used during authentication."""

    DB_PATH: str = os.getenv("AUTH_DB_PATH", "data/users.db")

    @classmethod
    def get_db_path(cls) -> Path:
        path = Path(cls.DB_PATH)
        return path if path.is_absolute() else Path.cwd() / path


class BlobStorageSettings:
    """Settings for Azure Blob Storage."""

    CONNECTION_STRING: str = os.getenv(
        "AZURE_STORAGE_CONNECTION_STRING", ""
    )  # validated in validate()
    AZURE_STORAGE_CONTAINER: str = os.getenv(
        "AZURE_STORAGE_CONTAINER",
        default="documents",
    )
    AZURE_BLOB_STORAGE_URL: str = os.getenv(
        "AZURE_STORAGE_ACCOUNT_URL", ""
    )  # validated in validate()

    @classmethod
    def validate(cls) -> None:
        if not cls.CONNECTION_STRING:
            raise ValueError("AZURE_STORAGE_CONNECTION_STRING is not configured")
        if not cls.AZURE_STORAGE_CONTAINER:
            raise ValueError("AZURE_STORAGE_CONTAINER is not configured")
        if not cls.AZURE_BLOB_STORAGE_URL:
            raise ValueError("AZURE_STORAGE_ACCOUNT_URL is not configured")


class AISearchSettings:
    _AI_SEARCH_ENDPOINT: Optional[str] = os.getenv("AI_SEARCH_ENDPOINT")
    _AI_SEARCH_API_KEY: Optional[str] = os.getenv("AI_SEARCH_KEY")
    _AI_SEARCH_INDEX_NAME: Optional[str] = os.getenv("AI_SEARCH_INDEX_NAME")

    @classmethod
    def validate(cls) -> None:
        if not cls._AI_SEARCH_ENDPOINT:
            raise ValueError("AI_SEARCH_ENDPOINT is not configured")
        if not cls._AI_SEARCH_INDEX_NAME:
            raise ValueError("AI_SEARCH_INDEX_NAME is not configured")
        if not cls._AI_SEARCH_API_KEY:
            raise ValueError("AI_SEARCH_KEY is not configured")

    @classmethod
    def get_endpoint(cls) -> str:
        """Retrieve the Azure Search endpoint from environment."""
        ai_search_endpoint = cls._AI_SEARCH_ENDPOINT
        if not ai_search_endpoint:
            raise ValueError("AI_SEARCH_ENDPOINT is not configured")
        return ai_search_endpoint

    @classmethod
    def get_api_key(cls) -> str:
        """Retrieve the Azure Search API key from environment."""
        ai_search_key = cls._AI_SEARCH_API_KEY
        if not ai_search_key:
            raise ValueError("AI_SEARCH_KEY is not configured")
        return ai_search_key

    @classmethod
    def get_index_name(cls) -> str:
        """Retrieve the Azure Search index name from environment."""
        ai_search_name = cls._AI_SEARCH_INDEX_NAME
        if not ai_search_name:
            raise ValueError("AI_SEARCH_INDEX_NAME is not configured")
        return ai_search_name


class AzureOpenAISettings:
    """Settings for Azure OpenAI resource."""

    _AOAI_ENDPOINT: Optional[str] = os.getenv("AOAI_ENDPOINT")
    _AOAI_API_KEY: Optional[str] = os.getenv("AOAI_KEY")
    _AOAI_DEPLOYMENT_NAME: Optional[str] = os.getenv("AOAI_DEPLOYMENT_NAME")
    _AOAI_MODEL_NAME: Optional[str] = os.getenv("AI_MODEL_NAME")
    _EMBEDDING_MODEL_NAME: Optional[str] = os.getenv("EMBEDDING_MODEL_NAME")
    _EMBEDDING_MODEL_DEPLOYMENT_NAME: Optional[str] = os.getenv(
        "EMBEDDING_MODEL_DEPLOYMENT_NAME"
    )

    @classmethod
    def get_endpoint(cls) -> str:
        """Retrieve the Azure OpenAI endpoint from environment."""
        aoai_endpoint = cls._AOAI_ENDPOINT
        if not aoai_endpoint:
            raise ValueError("AOAI_ENDPOINT is not configured")
        return aoai_endpoint

    @classmethod
    def get_api_key(cls) -> str:
        """Retrieve the Azure OpenAI API key from environment."""
        aoai_api_key = cls._AOAI_API_KEY
        if not aoai_api_key:
            raise ValueError("AOAI_KEY is not configured")
        return aoai_api_key

    @classmethod
    def get_deployment_name(cls) -> str:
        aoai_deployment_name = cls._AOAI_DEPLOYMENT_NAME
        if not aoai_deployment_name:
            raise ValueError("AOAI_DEPLOYMENT_NAME is not configured")
        return aoai_deployment_name

    @classmethod
    def get_model_name(cls) -> str:
        aoai_model_name = cls._AOAI_MODEL_NAME
        if not aoai_model_name:
            raise ValueError("AI_MODEL_NAME is not configured")
        return aoai_model_name

    @classmethod
    def get_embedding_deployment_name(cls) -> str:
        embedding_deployment_name = cls._EMBEDDING_MODEL_DEPLOYMENT_NAME
        if not embedding_deployment_name:
            raise ValueError("AOAI_DEPLOYMENT_NAME is not configured")
        return embedding_deployment_name

    @classmethod
    def get_embedding_model_name(cls) -> str:
        embedding_model_name = cls._EMBEDDING_MODEL_NAME
        if not embedding_model_name:
            raise ValueError("AOAI_DEPLOYMENT_NAME is not configured")
        return embedding_model_name

    @classmethod
    def chat_completions_uri(cls, deployment_name: Optional[str] = None) -> str:
        if not cls._AOAI_ENDPOINT:
            raise ValueError("AOAI_ENDPOINT is not configured")
        deployment = deployment_name or cls.get_deployment_name()
        return (
            f"{cls._AOAI_ENDPOINT.rstrip('/')}/openai/deployments/{deployment}/chat/completions"
            "?api-version=2024-02-01"
        )


class KnowledgeSourceSettings:
    """Centralized settings for the default knowledge source."""

    _KS_DEFAULT_NAME = "ks-name-default"
    _KS_DEFAULT_DESCRIPTION = "Knowledge Source description default"
    _KS_NAME: Optional[str] = os.getenv("KNOWLEDGE_SOURCE_NAME")
    _KS_DESCRIPTION: Optional[str] = os.getenv("KNOWLEDGE_SOURCE_DESCRIPTION")

    @classmethod
    def _value_or_default(cls, value: Optional[str], default: str) -> str:
        resolved = value or default
        if not resolved.strip():
            raise ValueError("Knowledge source values must not be empty")
        return resolved

    @classmethod
    def get_name(cls) -> str:
        """Return the configured knowledge source name."""
        return cls._value_or_default(cls._KS_NAME, cls._KS_DEFAULT_NAME)

    @classmethod
    def get_description(cls) -> str:
        """Return the configured knowledge source description."""
        return cls._value_or_default(cls._KS_DESCRIPTION, cls._KS_DEFAULT_DESCRIPTION)

    @classmethod
    def validate(cls) -> None:
        """Ensure both name and description are resolvable."""
        cls.get_name()
        cls.get_description()


class KnowledgeBaseSettings:
    """Centralized settings for the default knowledge base."""

    _KB_DEFAULT_NAME = "kb-name-deafult"
    _KB_DEFAULT_DESCRIPTION = "Agentic RAG sobre mi PDF"
    _KB_DEFAULT_ANSWER_INSTRUCTIONS = (
        "Responde en español, cita siempre la página del PDF."
    )
    _KB_DEFAULT_RETRIEVAL_INSTRUCTIONS = (
        "Responde en español, cita siempre la página del PDF."
    )
    _KB_NAME: Optional[str] = os.getenv("KNOWLEDGE_BASE_NAME")
    _KB_DESCRIPTION: Optional[str] = os.getenv("KNOWLEDGE_BASE_DESCRIPTION")
    _KB_ANSWER_INSTRUCTIONS: Optional[str] = os.getenv(
        "KNOWLEDGE_BASE_ANSWER_INSTRUCTIONS"
    )
    _KB_RETRIEVAL_INSTRUCTIONS: Optional[str] = os.getenv(
        "KNOWLEDGE_BASE_RETRIEVAL_INSTRUCTIONS"
    )

    @classmethod
    def _value_or_default(cls, value: Optional[str], default: str) -> str:
        resolved = value or default
        if not resolved.strip():
            raise ValueError("Knowledge base values must not be empty")
        return resolved

    @classmethod
    def get_name(cls) -> str:
        return cls._value_or_default(cls._KB_NAME, cls._KB_DEFAULT_NAME)

    @classmethod
    def get_description(cls) -> str:
        return cls._value_or_default(cls._KB_DESCRIPTION, cls._KB_DEFAULT_DESCRIPTION)

    @classmethod
    def get_answer_instructions(cls) -> str:
        return cls._value_or_default(
            cls._KB_ANSWER_INSTRUCTIONS, cls._KB_DEFAULT_ANSWER_INSTRUCTIONS
        )

    @classmethod
    def get_retrieval_instructions(cls) -> str:
        return cls._value_or_default(
            cls._KB_RETRIEVAL_INSTRUCTIONS, cls._KB_DEFAULT_RETRIEVAL_INSTRUCTIONS
        )

    @classmethod
    def validate(cls) -> None:
        cls.get_name()
        cls.get_description()
        cls.get_answer_instructions()
        cls.get_retrieval_instructions()


class MCPConnectionSettings:
    """Configuration for exposing the knowledge base as an MCP tool."""

    _PROJECT_RESOURCE_ID: Optional[str] = os.getenv("AI_PROJECT_RESOURCE_ID")
    _PROJECT_CONNECTION_NAME: Optional[str] = os.getenv(
        "AI_PROJECT_CONNECTION_NAME", "rag-mcp-connection"
    )

    @classmethod
    def get_project_resource_id(cls) -> str:
        resource_id = cls._PROJECT_RESOURCE_ID
        if not resource_id:
            raise ValueError("AI_PROJECT_RESOURCE_ID is not configured")
        return resource_id

    @classmethod
    def get_project_connection_name(cls) -> str:
        connection_name = cls._PROJECT_CONNECTION_NAME
        if not connection_name:
            raise ValueError("PROJECT_CONNECTION_NAME is not configured")
        return connection_name

    @classmethod
    def get_project_connection_id(cls) -> str:
        resource_id = cls.get_project_resource_id()
        connection_name = cls.get_project_connection_name()
        return f"{resource_id}/connections/{connection_name}"

    @classmethod
    def get_mcp_endpoint(cls) -> str:
        search_endpoint = AISearchSettings.get_endpoint()
        kb_name = KnowledgeBaseSettings.get_name()
        return f"{search_endpoint}/knowledgebases/{kb_name}/mcp?api-version=2025-11-01-Preview"


class RedisSettings:
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379")
    REDIS_KEY_PREFIX: str = os.getenv("REDIS_KEY_PREFIX", "chat_messages")
    REDIS_PORT: int = 6379

    @classmethod
    def get_redis_url(cls) -> str:
        return cls.REDIS_URL


class LayoutRagSettings:
    """Settings for the versioned layout-based RAG ingestion pipeline."""

    ENABLED: bool = os.getenv("LAYOUT_RAG_ENABLED", "false").lower() == "true"
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


class OpenAISettings:
    """Settings for Azure OpenAI (embeddings + completions)."""

    ENDPOINT: Optional[str] = _first_env("OPENAI_ENDPOINT", "AOAI_ENDPOINT")
    API_KEY: Optional[str] = _first_env("OPENAI_API_KEY", "AOAI_KEY")
    EMBEDDING_MODEL: str = (
        _first_env(
            "OPENAI_EMBEDDING_MODEL",
            "EMBEDDING_MODEL_NAME",
            default="text-embedding-ada-002",
        )
        or "text-embedding-ada-002"
    )
    EMBEDDING_DEPLOYMENT: str = (
        _first_env(
            "OPENAI_EMBEDDING_DEPLOYMENT",
            "EMBEDDING_MODEL_DEPLOYMENT_NAME",
            "OPENAI_EMBEDDING_MODEL",
            default="text-embedding-ada-002",
        )
        or "text-embedding-ada-002"
    )
    CHAT_MODEL: str = (
        _first_env(
            "AI_MODEL_DEPLOYMENT_NAME",
            "AOAI_DEPLOYMENT_NAME",
            default="gpt-4o-mini",
        )
        or "gpt-4o-mini"
    )
    MODEL_NAME: str = (
        _first_env(
            "OPENAI_MODEL_NAME",
            "AI_MODEL_NAME",
            default="gpt-4o-mini",
        )
        or "gpt-4o-mini"
    )

    VISION_DEPLOYMENT: str = (
        _first_env(
            "OPENAI_VISION_DEPLOYMENT",
            "RAG_V3_VISION_DEPLOYMENT",
            "AI_MODEL_DEPLOYMENT_NAME",
            "AOAI_DEPLOYMENT_NAME",
            default="gpt-4o-mini",
        )
        or "gpt-4o-mini"
    )


class DocumentIntelligenceSettings:
    """Settings for Azure Document Intelligence (Form Recognizer)."""

    DOCUMENT_INTELLIGENCE_ENDPOINT: Optional[str] = os.getenv(
        "DOCUMENT_INTELLIGENCE_ENDPOINT"
    )
    DOCUMENT_INTELLIGENCE_KEY: Optional[str] = os.getenv("DOCUMENT_INTELLIGENCE_KEY")

    @classmethod
    def validate(cls) -> None:
        """Ensure both endpoint and key are provided."""
        if not cls.DOCUMENT_INTELLIGENCE_ENDPOINT or not cls.DOCUMENT_INTELLIGENCE_KEY:
            raise ValueError(
                "DOCUMENT_INTELLIGENCE_ENDPOINT and DOCUMENT_INTELLIGENCE_KEY must be set"
            )

class ProcessingTriggerSettings:
    """Settings for decoupled document processing triggers."""

    MODE: str = (_first_env("PROCESSING_TRIGGER_MODE", default="inline") or "inline").strip().lower()
    FUNCTION_URL: Optional[str] = _first_env(
        "PROCESSING_FUNCTION_URL",
        "AZURE_FUNCTION_PROCESSING_URL",
    )
    SHARED_SECRET: Optional[str] = _first_env(
        "PROCESSING_FUNCTION_SECRET",
        "AZURE_FUNCTION_PROCESSING_SECRET",
    )
    TIMEOUT_SECONDS: int = int(
        _first_env("PROCESSING_TRIGGER_TIMEOUT_SECONDS", default="15") or "15"
    )

    @classmethod
    def use_azure_function(cls) -> bool:
        return cls.MODE == "azure_function"

    @classmethod
    def validate_function_mode(cls) -> None:
        if not cls.FUNCTION_URL:
            raise ValueError("PROCESSING_FUNCTION_URL is not configured")

class RagV3Settings:
    """Settings for the multimodal-ready rag-v3 extension."""

    ENABLED: bool = os.getenv("RAG_V3_ENABLED", "false").lower() == "true"
    INDEX_NAME: str = os.getenv("RAG_V3_INDEX_NAME", "documents-layout-rag-v3")
    IMAGE_INDEX_NAME: str = os.getenv(
        "RAG_V3_IMAGE_INDEX_NAME",
        "documents-layout-rag-v3-images",
    )
    DATASOURCE_NAME: str = os.getenv(
        "RAG_V3_DATASOURCE_NAME",
        "documents-layout-rag-v3-datasource",
    )
    SKILLSET_NAME: str = os.getenv(
        "RAG_V3_SKILLSET_NAME",
        "documents-layout-rag-v3-skillset",
    )
    INDEXER_NAME: str = os.getenv(
        "RAG_V3_INDEXER_NAME",
        "documents-layout-rag-v3-indexer",
    )
    CONTENT_FIELD: str = os.getenv("RAG_V3_CONTENT_FIELD", "content")
    VECTOR_FIELD: str = os.getenv("RAG_V3_VECTOR_FIELD", "content_vector")
    IMAGE_VECTOR_FIELD: str = os.getenv("RAG_V3_IMAGE_VECTOR_FIELD", "image_vector")
    TITLE_FIELD: str = os.getenv("RAG_V3_TITLE_FIELD", "document_title")
    PATH_FIELD: str = os.getenv("RAG_V3_PATH_FIELD", "metadata_storage_path")
    PAGE_FIELD: str = os.getenv("RAG_V3_PAGE_FIELD", "page_number")
    IMAGE_PATH_FIELD: str = os.getenv("RAG_V3_IMAGE_PATH_FIELD", "image_path")
    IMAGE_CAPTION_FIELD: str = os.getenv("RAG_V3_IMAGE_CAPTION_FIELD", "image_caption")
    SOURCE_KIND_FIELD: str = os.getenv("RAG_V3_SOURCE_KIND_FIELD", "source_kind")
    SECTION_KIND_FIELD: str = os.getenv("RAG_V3_SECTION_KIND_FIELD", "section_kind")

    @classmethod
    def embedding_dimensions(cls) -> int:
        return LayoutRagSettings.embedding_dimensions()


class AgenticRagSettings:
    """Settings for Azure AI Search knowledge sources and knowledge bases."""

    ENABLED: bool = (
        _first_env("AGENTIC_RAG_ENABLED", default="false") or "false"
    ).lower() == "true"


# def share_ttl() -> timedelta:
#     """Return how long public shares remain valid."""
#     return timedelta(hours=CosmosDBSettings.SHARE_TTL_HOURS)
