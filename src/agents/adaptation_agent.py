"""Main orchestrator for the document simplification pipeline."""

import asyncio

from src.agents.calm_evaluator import calm_evaluator_agent
from src.agents.glossary_agent import glossary_agent
from src.agents.explainer_agent import explainer_agent
from src.agents.simplifier_agent import simplifier_agent
from src.agents.validator_agent import validate
from src.agents.base_agent import AzureAIProvider
from src.models.schemas import ChatResponse, UserProfile

_FATIGUE_MAP: dict[str, list[str]] = {
    "A1": ["A1", "A1", "A1"],
    "A2": ["A2", "A1", "A1"],
    "B1": ["B1", "A2", "A1"],
    "C1": ["C1", "B1", "A2"],
}


def _fallback_simplification(text: str, max_sentence_length: int) -> str:
    words = text.split()
    if not words:
        return ""

    chunks = []
    step = max(6, max_sentence_length)
    for start in range(0, len(words), step):
        chunk = " ".join(words[start : start + step]).strip()
        if chunk:
            chunks.append(f"- {chunk}")
    return "\n".join(chunks)


def _wcag_summary(score: int, passed: bool, issues: list[str]) -> str:
    if passed:
        return f"WCAG score {score}/100. Sin alertas principales."
    if issues:
        return f"WCAG score {score}/100. Principal ajuste pendiente: {issues[0]}"
    return f"WCAG score {score}/100."


async def _generate_emoji_summary(text: str) -> str:
    provider = AzureAIProvider()
    agent = await provider.build(
        name="EmojiAgent",
        instructions=(
            "You create emoji summaries. "
            "Return only 4 or 5 emojis that represent the text. No extra words."
        ),
    )
    result = await agent.run(f"Summarize this text in emojis only:\n{text[:600]}")
    return (result.text if hasattr(result, "text") else str(result)).strip()


async def _build_glossary(text: str) -> list[dict]:
    agent = await glossary_agent()
    return await agent.run(text)


async def run_adaptation_pipeline(
    message: str,
    profile: UserProfile,
    rag_chunks: list[str],
    fatigue_level: int = 0,
    target_language: str | None = None,
) -> ChatResponse:
    source_text = "\n\n".join(rag_chunks) if rag_chunks else message
    effective_level = _FATIGUE_MAP.get(profile.reading_level, ["A2", "A1", "A1"])[
        max(0, min(2, fatigue_level))
    ]
    searches_performed = [message] if rag_chunks else []

    try:
        simplifier = await simplifier_agent()
        simplified = await simplifier.run(
            text=source_text,
            reading_level=effective_level,
            preset=profile.preset,
            avoid_words=[],
            target_language=target_language,
        )
    except Exception:
        simplified = _fallback_simplification(source_text, profile.max_sentence_length)

    try:
        calm = await calm_evaluator_agent()
        for _ in range(2):
            calm_result = await calm.run(simplified)
            if calm_result.approved:
                break
            simplified = calm_result.corrected_text
    except Exception:
        pass

    try:
        explainer = await explainer_agent()
        explanation = await explainer.run(original=source_text, simplified=simplified)
    except Exception:
        explanation = (
            "Se reorganizo el contenido en una version mas clara, con menos carga "
            "cognitiva y una estructura mas facil de seguir."
        )

    wcag_report = validate(
        text=simplified,
        reading_level=effective_level,
        avoid_words=[],
    )

    try:
        emoji_summary, glossary = await asyncio.gather(
            _generate_emoji_summary(simplified),
            _build_glossary(simplified),
        )
    except Exception:
        emoji_summary = None
        glossary = []

    tone = "calmado" if profile.tone == "calm_supportive" else "neutral"
    return ChatResponse(
        originalMessage=message,
        simplifiedText=simplified,
        explanation=explanation,
        tone=tone,
        audioUrl=None,
        beeLineOverlay=profile.has_dyslexia or profile.preset in {"dyslexia", "combined"},
        wcagReport=_wcag_summary(
            wcag_report.score,
            wcag_report.passed,
            wcag_report.issues,
        ),
        presetUsed=profile.preset,
        readingLevelUsed=effective_level,
        emojiSummary=emoji_summary,
        glossary=glossary,
        searchesPerformed=searches_performed,
    )
