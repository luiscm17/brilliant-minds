"""Glossary Agent - extracts difficult words and explains them simply."""

import json
import re

from src.agents.base_agent import AzureAIProvider


class GlossaryAgent:
    def __init__(self, agent):
        self._agent = agent

    async def run(self, text: str) -> list[dict]:
        prompt = (
            "Extract 3 to 5 difficult words or concepts from the text below.\n"
            "For each one, provide a short simple definition.\n"
            "Respond ONLY with valid JSON in this format:\n"
            '[{"word": "...", "definition": "..."}]\n\n'
            f"TEXT:\n{text[:1200]}"
        )
        result = await self._agent.run(prompt)
        raw = result.text if hasattr(result, "text") else str(result)
        match = re.search(r"\[.*\]", raw, re.DOTALL)
        if not match:
            return []
        try:
            return json.loads(match.group())
        except json.JSONDecodeError:
            return []


async def glossary_agent() -> GlossaryAgent:
    provider = AzureAIProvider()
    agent = await provider.build(
        name="GlossaryAgent",
        instructions=(
            "You explain difficult vocabulary with simple, calm definitions. "
            "Always respond with valid JSON only."
        ),
    )
    return GlossaryAgent(agent)
