class AdaptationAgent:
    def __init__(self, agent):
        self.agent = agent

    async def run(self, summary: str):
        result = await self.agent.run(summary)
        return result.text if hasattr(result, "text") else result

async def adaptation_agent():
    provider = AzureAIProvider()
    agent = await provider.build(
        name="AdaptationAgent",
        instructions="""Eres un experto en comunicación visual y cognitiva.
        TU MISIÓN:
        Crear un resumen ultra-compacto utilizando emojis y frases muy cortas.
        - Cada emoji debe representar una acción clave del texto.
        - Máximo 5 puntos clave.
        - El objetivo es proporcionar una idea general del documento en menos de 10 segundos de lectura.""",
        tools=[],
    )
    return AdaptationAgent(agent)