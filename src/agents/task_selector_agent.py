from src.agents.providers.azure_responses_provider import AzureResponsesAgent


class TaskSelectorAgent(AzureResponsesAgent):
    """Determine the focus area and priority strategy for the user request."""

    def __init__(self, **kwargs):
        instructions = """
        You are the Task Selector for an educational reading-comprehension tool supporting ADHD learners.

        Analyze the user's query and respond **only** with a valid, concise JSON object:
        {
          "focus": "simplificar | descomponer | estrategias | combinado",
          "priority": "alta | media | baja",
          "reason": "a short sentence explaining your decision"
        }

        Do not add any text outside the JSON.
        """

        super().__init__(name="TaskSelector", instructions=instructions, **kwargs)
