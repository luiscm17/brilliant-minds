from typing import Any
from agent_framework.azure import AzureAIAgentsProvider
from azure.identity.aio import AzureCliCredential
from src.agents.providers.base_agent import BaseAgent
from src.config.settings import AgentSettings


class AIAgentsProvider(BaseAgent):
    """Create dynamic agents via AzureAIAgentsProvider with a shared credential."""

    def __init__(self):
        self._credential = AzureCliCredential()
        self._provider = AzureAIAgentsProvider(
            credential=self._credential,
            project_endpoint=AgentSettings.get_project_endpoint(),
        )

    async def build(
        self,
        name: str,
        instructions: str,
        tools: list[Any] | None = None,
    ) -> Any:
        az_agent = await self._provider.create_agent(
            name=name,
            instructions=instructions,
            tools=tools or [],
        )
        return await self._provider.get_agent(az_agent.id)

    async def close(self) -> None:
        """Close provider and credential when lifecycle ends."""
        if self._provider:
            await self._provider.__aexit__(None, None, None)
        if self._credential:
            await self._credential.__aexit__(None, None, None)
