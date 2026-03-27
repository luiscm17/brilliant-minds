"""Azure OpenAI provider for agent-like completions.

Replaces the AzureAIProjectAgentProvider with a direct AsyncAzureOpenAI
client backed by the AI Foundry endpoint. Each agent is a lightweight
wrapper that sends a system prompt + user message and returns a response
with a .text attribute, matching the original agent interface.
"""

from openai import AsyncAzureOpenAI
from src.config.settings import OpenAISettings


class _AgentResponse:
    """Wraps a chat completion so callers can do result.text."""

    def __init__(self, text: str):
        self.text = text

    def __str__(self) -> str:
        return self.text


class _SimpleAgent:
    """Sends system+user messages to Azure OpenAI and returns _AgentResponse."""

    def __init__(self, instructions: str):
        self._instructions = instructions
        self._client = AsyncAzureOpenAI(
            azure_endpoint=OpenAISettings.ENDPOINT or "",
            api_key=OpenAISettings.API_KEY or "",
            api_version="2024-08-01-preview",
        )
        self._model = OpenAISettings.CHAT_MODEL

    async def run(self, prompt: str) -> _AgentResponse:
        response = await self._client.chat.completions.create(
            model=self._model,
            messages=[
                {"role": "system", "content": self._instructions},
                {"role": "user", "content": prompt},
            ],
            temperature=0.3,
        )
        text = response.choices[0].message.content or ""
        return _AgentResponse(text)


class AzureAIProvider:
    """Builds lightweight OpenAI-backed agents compatible with the agent interface."""

    async def build(
        self,
        name: str,
        instructions: str,
        tools: list | None = None,
    ) -> _SimpleAgent:
        return _SimpleAgent(instructions=instructions)
