class AgenticRAGAgent:
    def __init__(self, agent):
        self.agent = agent

    async def run(self, query: str):
        result = await self.agent.run(query)
        return result.text if hasattr(result, "text") else result

async def agentic_rag_agent():
    provider = AzureAIProvider()
    agent = await provider.build(
        name="AgenticRAGAgent",
        instructions="""Eres el cerebro del sistema de RAG Agéntico. 
        TU MISIÓN:
        1. Buscar información precisa en el índice semántico usando herramientas.
        2. Simplificar el contenido según el perfil de accesibilidad del usuario.
        3. Generar respuestas fundamentadas (grounded) evitando alucinaciones.
        
        REGLAS:
        - Si el usuario tiene TDAH: Usa estructuras atómicas.
        - Si el usuario tiene Autismo: Usa lenguaje literal y explica el contexto.
        - Siempre cita las fuentes del documento original.""",
        tools=[build_mcp_tool()], # Crucial para el acceso a AI Search/Foundry IQ
    )
    return AgenticRAGAgent(agent)