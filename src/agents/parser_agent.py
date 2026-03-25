from src.agents.base_agent import AzureAIProvider

class ParserAgent:
    def __init__(self, agent):
        self.agent = agent

    async def run(self, text_to_refine: str):
        result = await self.agent.run(text_to_refine)
        return result.text if hasattr(result, "text") else result

async def parser_agent():
    provider = AzureAIProvider()
    agent = await provider.build(
        name="ParserAgent",
        instructions="""Eres un experto en extracción de datos y Document Intelligence. 
        TU MISIÓN:
        Analizar archivos (PDF, imágenes, correos) y extraer el texto con su jerarquía estructural completa.
        - Identifica títulos, subtítulos y párrafos.
        - Limpia el ruido del documento (pie de página, números de página).
        - Entrega un JSON estructurado listo para ser procesado por 'The Brain'.""",
        tools=[build_mcp_tool()], # Conexión a Blob Storage/Document Intelligence
    )
    return agent