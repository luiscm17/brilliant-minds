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
