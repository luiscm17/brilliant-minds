"""Application settings loaded from environment variables.

Uses dotenv to load configuration from .env files for local development
and environment variables in production deployments.
"""

import os
from typing import Optional

from dotenv import load_dotenv

load_dotenv()

ENVIRONMENT = os.getenv("ENVIRONMENT", "development")


class AgentSettings:
    """Settings for Azure AI Project agents.

    Manages configuration for Azure AI Foundry endpoints and model
    deployments. Values are loaded from environment variables.

    Environment variables:
        AI_PROJECT_ENDPOINT: Azure AI Project endpoint URL.
        AI_MODEL_DEPLOYMENT_NAME: Name of the deployed model.
    """

    _AI_PROJECT_ENDPOINT: Optional[str] = os.getenv("AI_PROJECT_ENDPOINT")
    _AI_MODEL_DEPLOYMENT_NAME: Optional[str] = os.getenv("AI_MODEL_DEPLOYMENT_NAME")

    @classmethod
    def get_project_endpoint(cls) -> str:
        endpoint = cls._AI_PROJECT_ENDPOINT
        if not endpoint:
            raise ValueError("AI_PROJECT_ENDPOINT is not configured")
        assert isinstance(endpoint, str)
        return endpoint

    @classmethod
    def get_model_deployment_name(cls) -> str:
        model = cls._AI_MODEL_DEPLOYMENT_NAME
        if not model:
            raise ValueError("AI_MODEL_DEPLOYMENT_NAME is not configured")
        assert isinstance(model, str)
        return model


class BlobStorageSettings:
    """Settings for Azure Blob Storage.

    Manages connection strings and container names for document
    storage operations.

    Environment variables:
        AZURE_STORAGE_CONNECTION_STRING: Storage account connection string.
        AZURE_STORAGE_CONTAINER: Name of the blob container.
    """

    AZURE_STORAGE_CONNECTION_STRING: Optional[str] = os.getenv(
        "AZURE_STORAGE_CONNECTION_STRING"
    )
    AZURE_STORAGE_CONTAINER: Optional[str] = os.getenv("AZURE_STORAGE_CONTAINER")

    @classmethod
    def validate(cls) -> None:
        if not cls.AZURE_STORAGE_CONNECTION_STRING:
            raise ValueError("AZURE_STORAGE_CONNECTION_STRING is not configured")
        if not cls.AZURE_STORAGE_CONTAINER:
            raise ValueError("AZURE_STORAGE_CONTAINER is not configured")


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


class KnowledgeSourceSettings:
    """Centralized settings for the default knowledge source."""

    _KS_DEFAULT_NAME = "ks-name-default"
    _KS_DEFAULT_DESCRIPTION = "Knowledge Source automática desde Blob con mi PDF"
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
