"""Adaptation Agent (AAM) — main orchestrator for the DocSimplify pipeline.

Flow:
  1. AgenticRAGAgent decides when/what to search and produces simplified text
  2. CalmEvaluatorAgent (up to 2 iterations)
  3. ExplainerAgent
  4. ValidatorAgent
  5. EmojiSummary + GlossaryAgent (parallel)
  6. Returns SimplifiedResponse
"""

import asyncio
from typing import Optional

from src.agents.agentic_rag_agent import AgenticRAGAgent
from src.agents.explainer_agent import explainer_agent
from src.agents.calm_evaluator import calm_evaluator_agent
from src.agents.validator_agent import validate
from src.agents.glossary_agent import glossary_agent
from src.agents.base_agent import AzureAIProvider
from src.models.schemas import SimplifiedResponse, UserProfile

# Maps reading level + fatigue to an effective (lower) reading level
_FATIGUE_MAP: dict[str, list[str]] = {
    "A1": ["A1", "A1", "A1"],
    "A2": ["A2", "A1", "A1"],
    "B1": ["B1", "A2", "A1"],
    "B2": ["B2", "B1", "A2"],
    "C1": ["C1", "B2", "B1"],
}


async def _generate_emoji_summary(text: str) -> str:
    provider = AzureAIProvider()
    agent = await provider.build(
        name="EmojiAgent",
        instructions=(
            "You generate emoji summaries. "
            "Respond with ONLY 5 emojis that represent the key topics of the text. "
            "No words, no punctuation — just 5 emojis in a row."
        ),
    )
    result = await agent.run(f"Summarize in 5 emojis:\n{text[:600]}")
    return result.text.strip() if hasattr(result, "text") else str(result).strip()


async def _build_glossary(text: str) -> list[dict]:
    agent = await glossary_agent()
    return await agent.run(text)


async def run_adaptation_pipeline(
    message: str,
    profile: UserProfile,
    user_id: str,
    fatigue_level: int = 0,
    target_language: Optional[str] = None,
) -> SimplifiedResponse:
    """Execute the full multi-agent adaptation pipeline with Agentic RAG."""

    # Adjust reading level based on fatigue
    effective_level = _FATIGUE_MAP.get(profile.reading_level, ["A2", "A1", "A1"])[
        max(0, min(2, fatigue_level))
    ]

    # Step 1: Agentic RAG — agent decides when and what to search
    rag_agent = AgenticRAGAgent(user_id=user_id)
    simplified, queries_made = await rag_agent.run(
        message=message,
        reading_level=effective_level,
        preset=profile.preset,
        avoid_words=profile.avoid_words,
        target_language=target_language,
    )

    # Step 2: Calm evaluation (max 2 iterations)
    calm = await calm_evaluator_agent()
    for _ in range(2):
        calm_result = await calm.run(simplified)
        if calm_result.approved:
            break
        simplified = calm_result.corrected_text

    # Step 3: Generate explanation
    explainer = await explainer_agent()
    explanation = await explainer.run(original=message, simplified=simplified)

    # Step 4: Validate
    wcag_report = validate(
        text=simplified,
        reading_level=effective_level,
        avoid_words=profile.avoid_words,
    )

    # Step 5: Emoji summary + Glossary in parallel
    emoji_summary, glossary_entries = await asyncio.gather(
        _generate_emoji_summary(simplified),
        _build_glossary(simplified),
    )

    return SimplifiedResponse(
        original_message=message,
        simplified_text=simplified,
        explanation=explanation,
        wcag_report=wcag_report,
        preset_used=profile.preset,
        reading_level_used=effective_level,
        emoji_summary=emoji_summary,
        glossary=glossary_entries,
        searches_performed=queries_made,
    )
