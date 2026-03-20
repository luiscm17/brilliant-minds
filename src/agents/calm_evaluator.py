"""Calm Evaluator Agent — tone linter that ensures text is anxiety-free."""

from dataclasses import dataclass
from src.agents.base_agent import AzureAIProvider

ANXIETY_WORDS = [
    "urgent", "urgente", "critical", "crítico", "must", "debe", "obligatorio",
    "mandatory", "immediately", "inmediatamente", "failure", "fallo", "error grave",
    "failed", "fallido", "warning", "alarm", "alerta", "danger", "peligro",
]


@dataclass
class CalmResult:
    approved: bool
    issues: list[str]
    corrected_text: str


class CalmEvaluatorAgent:
    def __init__(self, agent):
        self._agent = agent

    async def run(self, text: str) -> CalmResult:
        found = [w for w in ANXIETY_WORDS if w.lower() in text.lower()]

        if not found:
            return CalmResult(approved=True, issues=[], corrected_text=text)

        prompt = (
            f"The following text contains words that may cause anxiety: {', '.join(found)}.\n\n"
            f"TEXT:\n{text}\n\n"
            "Replace those words with calm, supportive alternatives. "
            "Return ONLY the corrected text, nothing else."
        )
        result = await self._agent.run(prompt)
        corrected = result.text if hasattr(result, "text") else str(result)

        return CalmResult(
            approved=False,
            issues=[f"Replaced anxiety-inducing word: '{w}'" for w in found],
            corrected_text=corrected,
        )


async def calm_evaluator_agent() -> CalmEvaluatorAgent:
    provider = AzureAIProvider()
    agent = await provider.build(
        name="CalmEvaluatorAgent",
        instructions=(
            "You are a tone and empathy specialist for neurodiverse users. "
            "When given text, replace any anxiety-inducing or pressuring words "
            "with calm, supportive, and encouraging alternatives. "
            "Output only the corrected text. Never add explanations."
        ),
    )
    return CalmEvaluatorAgent(agent)
