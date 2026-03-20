"""Explainer Agent — generates a calm explanation of the simplification changes made."""

from src.agents.base_agent import AzureAIProvider


class ExplainerAgent:
    def __init__(self, agent):
        self._agent = agent

    async def run(self, original: str, simplified: str) -> str:
        prompt = (
            f"Original text (first 300 chars): {original[:300]}\n\n"
            f"Simplified text (first 300 chars): {simplified[:300]}\n\n"
            "Explain the main changes you made, in a calm and supportive tone. "
            "Max 150 words. Start with 'I simplified this text because...'"
        )
        result = await self._agent.run(prompt)
        return result.text if hasattr(result, "text") else str(result)


async def explainer_agent() -> ExplainerAgent:
    provider = AzureAIProvider()
    agent = await provider.build(
        name="ExplainerAgent",
        instructions=(
            "You are a supportive accessibility assistant. "
            "Your job is to explain, in calm and encouraging language, "
            "why and how a document was simplified. "
            "Never use words like: urgent, critical, must, failed, error, wrong. "
            "Always be positive, brief (max 150 words), and empathetic."
        ),
    )
    return ExplainerAgent(agent)
