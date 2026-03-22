"""Simplifier Agent — rewrites text to a target reading level using Plain Language rules."""

from typing import Optional
from src.agents.base_agent import AzureAIProvider

LEVEL_RULES = {
    "A1": "Use sentences under 8 words. Only the most basic everyday vocabulary. No jargon.",
    "A2": "Use sentences under 12 words. Simple and familiar vocabulary. Short paragraphs.",
    "B1": "Use sentences under 18 words. Avoid technical terms unless explained. Clear structure.",
    "B2": "Use sentences under 22 words. Moderate vocabulary is fine. Add context where needed.",
    "C1": "Use sentences under 28 words. Preserve technical nuance but simplify structure.",
}

PRESET_EXTRA = {
    "TDAH": "Format output as bullet points. Highlight deadlines and action items. Keep each point short.",
    "Dislexia": "Use very short sentences. Leave space between ideas. Avoid dense paragraphs.",
    "Combinado": "Use bullet points AND very short sentences. Maximum clarity and calm tone.",
    "Docente": "Preserve multiple reading levels. Generate a brief summary first, then the full simplified text.",
}


class SimplifierAgent:
    def __init__(self, agent):
        self._agent = agent

    async def run(
        self,
        text: str,
        reading_level: str,
        preset: str,
        avoid_words: list[str],
        target_language: Optional[str] = None,
    ) -> str:
        avoid = ", ".join(avoid_words) if avoid_words else "none"
        if target_language:
            lang_instruction = f"IMPORTANT: Output the simplified text in {target_language}."
        else:
            lang_instruction = "IMPORTANT: Detect the language of the source text and respond in the SAME language."
        prompt = (
            f"Simplify the following text.\n"
            f"Reading level: {reading_level}. Rules: {LEVEL_RULES.get(reading_level, '')}\n"
            f"Preset style: {PRESET_EXTRA.get(preset, '')}\n"
            f"Never use these words: {avoid}\n"
            f"{lang_instruction}\n\n"
            f"TEXT TO SIMPLIFY:\n{text}"
        )
        result = await self._agent.run(prompt)
        return result.text if hasattr(result, "text") else str(result)


async def simplifier_agent() -> SimplifierAgent:
    provider = AzureAIProvider()
    agent = await provider.build(
        name="SimplifierAgent",
        instructions=(
            "You are a Plain Language specialist. Your only job is to simplify text "
            "according to the reading level and preset provided by the user. "
            "Follow instructions exactly. Never add unsolicited information. "
            "Never use words the user has listed as forbidden. "
            "Output only the simplified text, nothing else."
        ),
    )
    return SimplifierAgent(agent)
