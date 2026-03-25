"""The Calm Filter agent implementation.
Especializado en regulación emocional y eliminación de disparadores de ansiedad.
"""
from src.agents.base_agent import AzureAIProvider

class CalmFilterAgent:
    def __init__(self, agent):
        self.agent = agent

    async def run(self, text_to_refine: str):
        result = await self.agent.run(text_to_refine)
        return result.text if hasattr(result, "text") else result

async def calm_filter_agent():
    provider = AzureAIProvider()
    agent = await provider.build(
        name="The Calm Filter",
        instructions="""Eres un experto en comunicación empática y apoyo neurodiverso.
        
        TU MISIÓN:
        Reescribir el contenido generado por otros agentes para asegurar que sea calmado y no genere ansiedad.
        
        GUÍAS DE ESTILO:
        - Elimina palabras de urgencia o presión (ej. 'inmediato', 'crítico', 'urgente', 'ya').
        - Transforma órdenes en sugerencias amables (ej. 'Debes hacer' -> 'Podrías empezar con').
        - Mantén un tono paciente, alentador y profesional.
        - No elimines información clave, solo cambia la carga emocional del mensaje.
        """,
        tools=[], # Este agente suele ser puramente de transformación de texto
    )
    return CalmFilterAgent(agent)