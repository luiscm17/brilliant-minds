class CalmEvaluatorAgent:
    def __init__(self, agent):
        self.agent = agent

    async def run(self, text_to_calm: str):
        result = await self.agent.run(text_to_calm)
        return result.text if hasattr(result, "text") else result

async def calm_evaluator_agent():
    provider = AzureAIProvider()
    agent = await provider.build(
        name="CalmEvaluatorAgent",
        instructions="""Eres un experto en regulación emocional y comunicación empática.
        TU MISIÓN:
        Revisar el texto generado y eliminar cualquier disparador de ansiedad (palabras de urgencia, presión o términos alarmistas).
        - Transforma 'Debes hacer esto ahora' en 'Un buen primer paso sería este'.
        - Mantén un tono alentador y paciente.""",
        tools=[], 
    )
    return CalmEvaluatorAgent(agent)