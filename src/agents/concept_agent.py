"""Concept Agent — generates a concept map (nodes + edges) from simplified text."""

import json
import re
from src.agents.base_agent import AzureAIProvider


class ConceptAgent:
    def __init__(self, agent):
        self._agent = agent

    async def run(self, text: str) -> dict:
        prompt = (
            "Analyze the text below and extract a concept map.\n"
            "Return ONLY valid JSON with this structure:\n"
            '{"nodes": [{"id": "1", "label": "Main concept"}, ...], '
            '"edges": [{"source": "1", "target": "2"}, ...]}\n'
            "Rules:\n"
            "- 5 to 8 nodes maximum\n"
            "- Node labels must be short (2-4 words)\n"
            "- The first node (id=1) is always the main topic\n"
            "- No markdown, no extra text, just JSON\n\n"
            f"TEXT:\n{text[:1500]}"
        )
        result = await self._agent.run(prompt)
        raw = result.text if hasattr(result, "text") else str(result)
        match = re.search(r"\{.*\}", raw, re.DOTALL)
        if match:
            try:
                return json.loads(match.group())
            except json.JSONDecodeError:
                pass
        return {"nodes": [], "edges": []}


async def concept_agent() -> ConceptAgent:
    provider = AzureAIProvider()
    agent = await provider.build(
        name="ConceptAgent",
        instructions=(
            "You are a knowledge graph specialist. "
            "You extract concepts and relationships from text as JSON concept maps. "
            "Always respond with valid JSON only."
        ),
    )
    return ConceptAgent(agent)
