from typing import Any

# from agent_framework.azure import AzureOpenAIResponsesClient
from agent_framework.openai import OpenAIChatClient
from src.agents.providers.base_agent import BaseAgent
from src.config.settings import AzureOpenAISettings
from azure.identity import AzureCliCredential


class OpenAIProvider(BaseAgent):
    """Create agents directly from Azure OpenAI chat client."""

    def __init__(self):
        self.client = OpenAIChatClient(
            model_id=AzureOpenAISettings.get_deployment_name(),
            api_key=AzureOpenAISettings.get_api_key(),
        )

    async def build(
        self,
        name: str,
        instructions: str,
        tools: list[Any] | None = None,
    ) -> Any:
        """Instantiate an agent through the synchronous OpenAI Chat client."""
        agent = self.client.as_agent(
            name=name,
            instructions=instructions,
            tools=tools or [],
        )
        return agent
