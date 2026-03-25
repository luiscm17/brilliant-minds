class ComprehensionAgent:
    def __init__(self, agent):
        self.agent = agent

    async def run(self, processed_text: str):
        result = await self.agent.run(processed_text)
        return result.text if hasattr(result, "text") else result

async def comprehension_agent():
    provider = AzureAIProvider()
    agent = await provider.build(
        name="ComprehensionAgent",
        instructions="""Eres un evaluador pedagógico especializado en accesibilidad cognitiva.
        TU MISIÓN:
        Crear 3 preguntas de opción múltiple basadas en el contenido procesado.
        - Las preguntas deben ser directas, evitando dobles negaciones.
        - Proporciona la respuesta correcta y una explicación breve del 'por qué'.
        - Usa un tono alentador y paciente.""",
        tools=[],
    )
    return ComprehensionAgent(agent)