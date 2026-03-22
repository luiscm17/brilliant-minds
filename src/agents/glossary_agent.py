"""Glossary Agent — extracts technical terms and generates simple definitions."""

import json
import re
from src.agents.base_agent import AzureAIProvider


class GlossaryAgent:
    def __init__(self, agent):
        self._agent = agent

    async def run(self, text: str) -> list[dict]:
        prompt = (
            "Extract 3 to 5 technical or difficult words from the text below.\n"
            "For each word, provide a simple definition a child could understand.\n"
            "Respond ONLY with a JSON array, no markdown, no extra text.\n"
            "Format: [{\"word\": \"...\", \"definition\": \"...\"}, ...]\n\n"
            f"TEXT:\n{text[:1200]}"
        )
        result = await self._agent.run(prompt)
        raw = result.text if hasattr(result, "text") else str(result)
        # Extract JSON array from response
        match = re.search(r"\[.*\]", raw, re.DOTALL)
        if match:
            try:
                return json.loads(match.group())
            except json.JSONDecodeError:
                pass
        return []


async def glossary_agent() -> GlossaryAgent:
    provider = AzureAIProvider()
    agent = await provider.build(
        name="GlossaryAgent",
        instructions=(
            "You are a vocabulary specialist for accessibility. "
            "You identify difficult words and explain them in the simplest possible way. "
            "Always respond with valid JSON only."
        ),
    )
    return GlossaryAgent(agent)
