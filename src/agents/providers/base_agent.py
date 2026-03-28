from abc import ABC, abstractmethod
import os
from typing import Optional, List, Any

from agent_framework.azure import AzureOpenAIResponsesClient
from azure.identity import DefaultAzureCredential


class BaseAgent(ABC):
    """Abstract base that lazily builds agents from Azure OpenAI responses."""

    def __init__(
        self,
        name: str,
        instructions: str,
        tools: Optional[List] = None,
        temperature: float = 0.7,
        **kwargs: Any,
    ):
        self.name = name
        self.instructions = instructions
        self.tools = tools or []
        self._agent = None  # return as_agent)
        self._client = None
        self.extra_kwargs = kwargs

    @abstractmethod
    async def _create_client(self) -> AzureOpenAIResponsesClient:
        """Let subclasses provide the Azure OpenAI responses client implementation."""
        pass

    async def get_agent(self):
        """Lazily instantiate and cache the agent created from the client."""
        if self._agent is None:
            if self._client is None:
                self._client = await self._create_client()

            self._agent = self._client.as_agent(
                name=self.name,
                instructions=self.instructions,
                tools=self.tools,
                **self.extra_kwargs,
            )
        return self._agent

    async def run(self, message: str, session=None):
        """Send a single message through the cached agent and return the result."""
        agent = await self.get_agent()

        result = await agent.run(message, session=session)
        return result
