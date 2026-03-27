"""Azure AI Project provider for agent creation.

Uses Azure AI Foundry's project-based agent creation with versioning.
Agents are created as versioned definitions (v1.0, v2.0, etc.).

Note: This provider freezes agent definition with each version.
Does NOT support runtime tool modifications (incompatible with GroupChatBuilder).
Recommended for: Compliance-heavy scenarios with formal versioning requirements.
"""

from typing import Any
from azure.ai.projects.aio import AIProjectClient
from azure.ai.projects.models import PromptAgentDefinition
from azure.identity.aio import AzureCliCredential
from src.agents.providers.base_agent import BaseAgent
from src.config.settings import AgentSettings


class AIProjectProvider(BaseAgent):
    """
    Provider for creating versioned agents using Azure AI Projects SDK.

    Agents are stored in Azure AI Foundry with explicit versioning.
    Each agent update creates a new version (v1.0, v2.0, etc.).

    Architecture:
        AIProjectClient → create_version() → PromptAgentDefinition
                              ↓
                         Immutable version
                         (audit trail)

    Example:
        provider = AzureAIProjectProvider()
        agent = await provider.build(
            name="ComplianceAgent",
            instructions="You enforce compliance rules."
        )
    """

    async def build(
        self,
        name: str,
        instructions: str,
        tools: list[Any] | None = None,
    ) -> Any:
        """Build a versioned agent using Azure AI Project client.

        Each build creates a new version in the project.
        Tools are frozen with the version definition.

        Args:
            name: Agent identifier (becomes project name).
            instructions: System prompt for the agent.
            tools: Optional list of tools (frozen in version).

        Returns:
            Configured agent instance.

        Raises:
            Exception: If agent creation fails in Azure AI service.
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

            # This uses AzureAIProjectAgentProvider which wraps the versioned agent
            from agent_framework.azure import AzureAIProjectAgentProvider

            provider = AzureAIProjectAgentProvider(project_client=project_client)
            agent = provider.as_agent(created_agent)

            return agent

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        return False
