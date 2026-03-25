class GlossaryAgent:
    def __init__(self, agent):
        self.agent = agent

    async def run(self, text: str):
        result = await self.agent.run(text)
        return result.text if hasattr(result, "text") else result

async def glossary_agent():
    provider = AzureAIProvider()
    agent = await provider.build(
        name="GlossaryAgent",
        instructions="""Eres un experto lingüista.
        TU MISIÓN:
        Extraer términos técnicos o legales complejos del texto.
        - Proporciona una definición simple de máximo 15 palabras para cada uno.
        - Formato: Lista de objetos {termino, definicion}.""",
        tools=[],
    )
    return GlossaryAgent(agent)