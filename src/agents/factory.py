from agent_framework import Agent
from src.agents.common.memory import AccessibilityContextProvider

async def build_custom_agent(client, name, instructions, shared_context):
    """Generador universal de agentes con contexto inyectado."""
    return Agent(
        client=client,
        name=name,
        instructions=instructions,
        context_providers=[shared_context] # Aquí inyectamos el componente reutilizable
    )