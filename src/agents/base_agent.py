"""Azure AI Project provider for agent creation.

Provides integration with Azure AI Foundry's agent framework,
enabling creation and management of AI agents.
"""

import os
from typing import Any
from agent_framework.azure import AzureAIProjectAgentProvider
from azure.ai.projects.aio import AIProjectClient
from azure.ai.projects.models import PromptAgentDefinition
from azure.identity.aio import AzureCliCredential
from src.config.settings import AgentSettings


class AzureAIProvider:
    """Provider for creating agents using Azure AI Project client.

    Uses Azure's AI Foundry to instantiate and configure agents
    with custom names, instructions, and tools.

    Example:
        provider = AzureAIProvider()
        agent = await provider.build(
            name="MyAgent",
            instructions="You are a helpful assistant."
        )
    """

    async def build(
        self,
        name: str,
        instructions: str,
        tools: list[Any] | None = None,
    ) -> Any:
        """Build and return an Azure AI agent.

        Args:
            name: Unique identifier for the agent.
            instructions: System prompt defining agent behavior.
            tools: Optional list of tools the agent can use.

        Returns:
            Configured agent instance ready to handle requests.
        """
        async with (
            AzureCliCredential() as credential,
            AIProjectClient(
                endpoint=AgentSettings.get_project_endpoint(),
                credential=credential,
            ) as project_client,
        ):
            created_agent = await project_client.agents.create_version(
                agent_name=name,
                definition=PromptAgentDefinition(
                    model=AgentSettings.get_model_deployment_name(),
                    instructions=instructions,
                    tools=tools or [],
                ),
            )

            provider = AzureAIProjectAgentProvider(project_client=project_client)
            agent = provider.as_agent(created_agent)

            return agent
