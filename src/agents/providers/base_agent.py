from abc import ABC, abstractmethod
import os
from typing import Optional, List, Any

from agent_framework.azure import AzureOpenAIResponsesClient
from azure.identity import DefaultAzureCredential


class BaseAgent(ABC):
    """
    Clase base para todos los agentes.
    Maneja la creación lazy del cliente y del agente real.
    """

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
        self._agent = None          # Aquí guardaremos el agente real (lo que retorna as_agent)
        self._client = None
        self.extra_kwargs = kwargs

    @abstractmethod
    async def _create_client(self) -> AzureOpenAIResponsesClient:
        """Cada subclase define cómo crear su cliente."""
        pass

    async def get_agent(self):
        """Crea o retorna el agente (lazy)."""
        if self._agent is None:
            if self._client is None:
                self._client = await self._create_client()

            # Aquí es donde se llama as_agent() → sobre el CLIENTE
            self._agent = self._client.as_agent(
                name=self.name,
                instructions=self.instructions,
                tools=self.tools,
                **self.extra_kwargs,
            )
        return self._agent

    async def run(self, message: str, session=None):
        """Método simple y único que usaremos por ahora (sin stream)."""
        agent = await self.get_agent()
        # agent.run() devuelve normalmente el resultado completo (texto o respuesta estructurada)
        result = await agent.run(message, session=session)
        return result