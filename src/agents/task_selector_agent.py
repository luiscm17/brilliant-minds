from src.agents.providers.azure_responses_provider import AzureResponsesAgent

class TaskSelectorAgent(AzureResponsesAgent):
    """Analiza la consulta y decide qué estrategias se necesitan."""

    def __init__(self, **kwargs):
        instructions = """
        Eres Task Selector para una herramienta educativa de comprensión lectora para personas con TDH.

        Analiza la consulta del usuario y responde **únicamente** con un JSON válido y corto:
        {
          "focus": "simplificar | descomponer | estrategias | combinado",
          "priority": "alta | media | baja",
          "reason": "una frase corta explicando tu decisión"
        }

        No agregues texto fuera del JSON.
        """

        super().__init__(
            name="TaskSelector",
            instructions=instructions,
            **kwargs
        )