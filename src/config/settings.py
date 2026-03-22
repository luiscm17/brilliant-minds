"""Application settings loaded from environment variables."""

import os
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

ENVIRONMENT = os.getenv("ENVIRONMENT", "development")


class AgentSettings:
    """Settings for Azure AI Project agents."""

    _AI_PROJECT_ENDPOINT: Optional[str] = os.getenv("AI_PROJECT_ENDPOINT")
    _AI_MODEL_DEPLOYMENT_NAME: Optional[str] = os.getenv("AI_MODEL_DEPLOYMENT_NAME")

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

    CONNECTION_STRING: Optional[str] = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
    CONTAINER: Optional[str] = os.getenv("AZURE_STORAGE_CONTAINER", "documents")

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

    ENDPOINT: Optional[str] = os.getenv("AZURE_SEARCH_ENDPOINT")
    KEY: Optional[str] = os.getenv("AZURE_SEARCH_KEY")
    INDEX: str = os.getenv("AZURE_SEARCH_INDEX", "documents-index")

    @classmethod
    def validate(cls) -> None:
        if not cls.ENDPOINT:
            raise ValueError("AZURE_SEARCH_ENDPOINT is not configured")
        if not cls.KEY:
            raise ValueError("AZURE_SEARCH_KEY is not configured")


class OpenAISettings:
    """Settings for Azure OpenAI (embeddings + completions)."""

    ENDPOINT: Optional[str] = os.getenv("OPENAI_ENDPOINT")
    API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY")
    EMBEDDING_MODEL: str = os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-ada-002")
    CHAT_MODEL: str = os.getenv("AI_MODEL_DEPLOYMENT_NAME", "grok-3")


class DocumentIntelligenceSettings:
    """Settings for Azure Document Intelligence (Form Recognizer)."""

    ENDPOINT: Optional[str] = os.getenv("DOCUMENT_INTELLIGENCE_ENDPOINT")
    KEY: Optional[str] = os.getenv("DOCUMENT_INTELLIGENCE_KEY")
