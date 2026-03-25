"""The Brain agent implementation.
Especializado en simplificación cognitiva y estructuración de pasos atómicos.
"""
from src.agents.base_agent import AzureAIProvider
from src.agents.tools.mcp_tool import build_mcp_tool

class BrainAgent:
    def __init__(self, agent):
        self.agent = agent

    async def run(self, context_and_profile: str):
        result = await self.agent.run(context_and_profile)
        return result.text if hasattr(result, "text") else result

async def brain_agent():
    provider = AzureAIProvider()
    agent = await provider.build(
        name="The Brain",
        instructions="""Eres un experto en ingeniería de tareas y simplificación cognitiva. 
        
        TU MISIÓN:
        Recibir documentos densos y convertirlos en formatos digeribles según el perfil del usuario.
        
        REGLAS DE FORMATO:
        - Si el perfil indica TDAH: Entrega máximo 3 subtareas atómicas con tiempos estimados.
        - Si el perfil indica AUTISMO: Usa lenguaje 100% literal, elimina metáforas y explica el 'por qué' de cada paso.
        - Si el perfil indica DISLEXIA: Estructura la información con viñetas claras y resúmenes cortos.
        - Prioriza la estructura lógica sobre el tono decorativo.
        """,
        tools=[build_mcp_tool()], # Permite conexión con Foundry IQ
    )
    return BrainAgent(agent)