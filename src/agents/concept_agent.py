"""Concept Agent - generates a compact concept map from simplified text."""

import json
import re

from src.agents.base_agent import AzureAIProvider


class ConceptAgent:
    def __init__(self, agent):
        self._agent = agent

    async def run(self, text: str) -> dict:
        prompt = (
            "Analyze the text and return a concept map as JSON only.\n"
            "Use this exact shape:\n"
            '{"nodes":[{"id":"1","label":"Main topic"}],"edges":[{"source":"1","target":"2"}]}\n'
            "Rules:\n"
            "- 4 to 7 nodes maximum\n"
            "- labels must be short\n"
            "- first node should be the main topic\n\n"
            f"TEXT:\n{text[:1500]}"
        )
        result = await self._agent.run(prompt)
        raw = result.text if hasattr(result, "text") else str(result)
        match = re.search(r"\{.*\}", raw, re.DOTALL)
        if not match:
            return {"nodes": [], "edges": []}
        try:
            return json.loads(match.group())
        except json.JSONDecodeError:
            return {"nodes": [], "edges": []}


async def concept_agent() -> ConceptAgent:
    provider = AzureAIProvider()
    agent = await provider.build(
        name="ConceptAgent",
        instructions=(
            "You extract short concept maps from text. "
            "Always respond with valid JSON only."
        ),
    )
    return ConceptAgent(agent)
