class ExplainerAgent:
    def __init__(self, agent):
        self.agent = agent

    async def run(self, diff_context: str):
        result = await self.agent.run(diff_context)
        return result.text if hasattr(result, "text") else result

async def explainer_agent():
    provider = AzureAIProvider()
    agent = await provider.build(
        name="ExplainerAgent",
        instructions="""Eres un asistente de transparencia y trazabilidad.
        TU MISIÓN:
        Explicar al usuario por qué se realizaron cambios en el texto original.
        - Justifica las simplificaciones basándote en beneficios de lectura.
        - Ejemplo: 'Cambié esta frase larga por dos cortas para que sea más fácil de seguir'.
        - Usa un tono honesto y servicial.""",
        tools=[],
    )
    return ExplainerAgent(agent)