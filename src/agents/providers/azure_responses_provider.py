import os
from typing import Optional

from azure.identity import DefaultAzureCredential

from agent_framework.azure import AzureOpenAIResponsesClient
from src.config.settings import AgentSettings
from .base_agent import BaseAgent


class AzureResponsesAgent(BaseAgent):
    """Bridge between BaseAgent and AzureOpenAIResponsesClient-backed agents."""

    def __init__(
        self,
        name: str,
        instructions: str,
        project_endpoint: Optional[str] = None,
        deployment_name: Optional[str] = None,
        tools: Optional[list] = None,
        **kwargs,
    ):
        super().__init__(name, instructions, tools)

        self.project_endpoint = AgentSettings.get_project_endpoint()
        self.deployment_name = deployment_name or os.getenv(
            "AZURE_OPENAI_RESPONSES_DEPLOYMENT_NAME"
        )

        if not self.project_endpoint or not self.deployment_name:
            raise ValueError(
                "Faltan variables: AZURE_AI_PROJECT_ENDPOINT y AZURE_OPENAI_RESPONSES_DEPLOYMENT_NAME"
            )

    async def _create_client(self) -> AzureOpenAIResponsesClient:
        """Create the AzureOpenAIResponsesClient with configured credentials."""
        credential = DefaultAzureCredential()

        return AzureOpenAIResponsesClient(
            project_endpoint=self.project_endpoint,
            deployment_name=self.deployment_name,
            credential=credential,
        )
