class FatigueAgent:
    def __init__(self, agent):
        self.agent = agent

    async def run(self, text: str):
        result = await self.agent.run(text)
        return result.text if hasattr(result, "text") else result

async def fatigue_agent():
    provider = AzureAIProvider()
    agent = await provider.build(
        name="FatigueAgent",
        instructions="""Eres el agente de reducción de fatiga cognitiva.
        TU MISIÓN:
        Cuando el usuario está agotado, resume todo a lo más esencial.
        - Usa frases de máximo 5 palabras.
        - Elimina cualquier detalle que no sea vital para la acción inmediata.
        - Usa un formato ultra-espaciado.""",
        tools=[],
    )
    return FatigueAgent(agent)