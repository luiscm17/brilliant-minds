class ConceptAgent:
    def __init__(self, agent):
        self.agent = agent

    async def run(self, context: str):
        result = await self.agent.run(context)
        return result.text if hasattr(result, "text") else result

async def concept_agent():
    provider = AzureAIProvider()
    agent = await provider.build(
        name="ConceptAgent",
        instructions="""Eres un arquitecto de información visual.
        TU MISIÓN:
        Convertir la información del documento en un esquema de nodos y relaciones.
        - La salida DEBE ser un JSON compatible con ReactFlow (nodes, edges).
        - Simplifica las conexiones para evitar la sobrecarga visual.""",
        tools=[],
    )
    return ConceptAgent(agent)